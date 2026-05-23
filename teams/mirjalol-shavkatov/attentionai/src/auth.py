"""
Authentication & Authorization module for PDP Career Center.
Handles JWT creation/validation, Google OAuth, RBAC, and audit logging.
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from functools import wraps

import jwt
from fastapi import Request, HTTPException, Depends, Response
from fastapi.security import HTTPBearer

from src.config import (
    JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    DASHBOARD_URL
)
from src.db import get_db_connection

logger = logging.getLogger(__name__)

# ── Constants ──
VALID_ROLES = {"super_admin", "career_staff", "academic_staff", "teacher", "viewer"}
VALID_DEPARTMENTS = {"career", "academic", "teaching"}
JWT_ALGORITHM = "HS256"

# Cookie names
ACCESS_COOKIE = "pdp_access_token"
REFRESH_COOKIE = "pdp_refresh_token"

# Optional bearer token extraction (fallback)
security = HTTPBearer(auto_error=False)


# ──────────────── JWT Token Management ────────────────

def create_access_token(staff_id: int, email: str, role: str, department: str) -> str:
    """Create a short-lived JWT access token (15 min default)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(staff_id),
        "email": email,
        "role": role,
        "department": department,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(staff_id: int) -> tuple[str, str]:
    """
    Create a refresh token. Returns (raw_token, token_hash).
    Raw token goes to cookie, hash goes to DB.
    """
    raw_token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO refresh_tokens (staff_user_id, token_hash, expires_at)
           VALUES (?, ?, ?);""",
        (staff_id, token_hash, expires_at.isoformat())
    )
    conn.commit()
    conn.close()

    return raw_token, token_hash


def verify_access_token(token: str) -> dict:
    """Decode and validate a JWT access token. Returns payload dict or raises."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def rotate_refresh_token(raw_old_token: str) -> tuple[dict, str, str]:
    """
    Validate old refresh token, revoke it, issue new one.
    Returns (staff_user_dict, new_raw_token, new_token_hash).
    """
    old_hash = hashlib.sha256(raw_old_token.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Find the token
    cursor.execute(
        """SELECT rt.id, rt.staff_user_id, rt.expires_at, rt.revoked,
                  su.id as su_id, su.email, su.name, su.role, su.department,
                  su.is_active, su.avatar_url
           FROM refresh_tokens rt
           JOIN staff_users su ON rt.staff_user_id = su.id
           WHERE rt.token_hash = ?;""",
        (old_hash,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if row["revoked"]:
        # Possible token reuse attack — revoke ALL tokens for this user
        cursor.execute(
            "UPDATE refresh_tokens SET revoked = 1 WHERE staff_user_id = ?;",
            (row["staff_user_id"],)
        )
        conn.commit()
        conn.close()
        logger.warning(f"Refresh token reuse detected for staff_user_id={row['staff_user_id']}")
        audit_log("system", str(row["staff_user_id"]), "token_reuse_detected",
                  details="All tokens revoked due to potential token theft")
        raise HTTPException(status_code=401, detail="Token reuse detected. All sessions revoked.")

    # Check expiry
    expires_at = datetime.fromisoformat(row["expires_at"]).replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        conn.close()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Check staff is still active
    if not row["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Account deactivated")

    # Revoke old token
    cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE id = ?;", (row["id"],))
    conn.commit()
    conn.close()

    # Issue new refresh token
    new_raw, new_hash = create_refresh_token(row["staff_user_id"])

    staff_user = {
        "id": row["su_id"],
        "email": row["email"],
        "name": row["name"],
        "role": row["role"],
        "department": row["department"],
        "is_active": row["is_active"],
        "avatar_url": row["avatar_url"],
    }

    return staff_user, new_raw, new_hash


def revoke_all_tokens(staff_id: int):
    """Revoke all refresh tokens for a staff user (logout/deactivation)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE refresh_tokens SET revoked = 1 WHERE staff_user_id = ? AND revoked = 0;",
        (staff_id,)
    )
    conn.commit()
    conn.close()


# ──────────────── Cookie Helpers ────────────────

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set httpOnly secure cookies for both tokens."""
    is_prod = not DASHBOARD_URL.startswith("http://localhost")

    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/auth/",  # Only sent to auth endpoints
    )


def clear_auth_cookies(response: Response):
    """Remove auth cookies on logout."""
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/auth/")


# ──────────────── FastAPI Dependencies ────────────────

async def get_current_staff(request: Request) -> dict:
    """
    FastAPI dependency: extract and validate staff user from JWT cookie.
    Returns staff user dict with id, email, role, department.
    Raises 401 if not authenticated.
    """
    token = request.cookies.get(ACCESS_COOKIE)

    if not token:
        # Fallback: check Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_access_token(token)

    # Verify staff still exists and is active
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, name, role, department, is_active, avatar_url FROM staff_users WHERE id = ?;",
        (int(payload["sub"]),)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Staff user not found")
    if not row["is_active"]:
        raise HTTPException(status_code=403, detail="Account deactivated")

    return dict(row)


def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory: checks that current staff has one of the allowed roles.
    Usage: staff = Depends(require_role("super_admin", "career_staff"))
    """
    async def _check(staff: dict = Depends(get_current_staff)) -> dict:
        if staff["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {', '.join(allowed_roles)}"
            )
        return staff
    return _check


def require_department(*allowed_departments: str):
    """
    FastAPI dependency factory: checks department access.
    super_admin bypasses department check.
    """
    async def _check(staff: dict = Depends(get_current_staff)) -> dict:
        if staff["role"] == "super_admin":
            return staff  # super_admin bypasses
        if staff["department"] not in allowed_departments:
            raise HTTPException(
                status_code=403,
                detail=f"No access to this department. Required: {', '.join(allowed_departments)}"
            )
        return staff
    return _check


# ──────────────── Google OAuth ────────────────

async def exchange_google_code(code: str, redirect_uri: str) -> dict:
    """
    Exchange Google auth code for user info.
    Returns dict with email, name, sub (Google ID), picture.
    """
    import httpx

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )

    if token_resp.status_code != 200:
        logger.error(f"Google token exchange failed: {token_resp.text}")
        raise HTTPException(status_code=400, detail="Google authentication failed")

    token_data = token_resp.json()
    id_token_str = token_data.get("id_token")

    if not id_token_str:
        raise HTTPException(status_code=400, detail="No ID token from Google")

    # Decode ID token (we trust Google's signature since we just got it)
    # For production, verify with Google's public keys
    try:
        # Decode without verification since we just received from Google's token endpoint
        payload = jwt.decode(id_token_str, options={"verify_signature": False})
    except Exception as e:
        logger.error(f"Failed to decode Google ID token: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google ID token")

    return {
        "email": payload.get("email"),
        "name": payload.get("name", payload.get("email", "").split("@")[0]),
        "sub": payload.get("sub"),
        "picture": payload.get("picture"),
        "email_verified": payload.get("email_verified", False),
    }


def validate_staff_login(google_user: dict) -> dict:
    """
    Validate that the Google user is in the staff allowlist.
    Returns the staff_users row dict.
    Raises 403 if not allowed.
    """
    email = google_user.get("email", "").lower().strip()

    if not email:
        raise HTTPException(status_code=400, detail="No email from Google")

    if not google_user.get("email_verified"):
        raise HTTPException(status_code=400, detail="Google email not verified")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Look up by email in allowlist
    cursor.execute("SELECT * FROM staff_users WHERE email = ?;", (email,))
    staff = cursor.fetchone()

    if not staff:
        conn.close()
        audit_log("system", email, "failed_login", details="Email not in staff allowlist")
        raise HTTPException(
            status_code=403,
            detail="Access denied. Your email is not in the staff allowlist. Contact your administrator."
        )

    if not staff["is_active"]:
        conn.close()
        audit_log("system", email, "failed_login", details="Account deactivated")
        raise HTTPException(status_code=403, detail="Account deactivated. Contact your administrator.")

    # Update Google sub and last_login
    cursor.execute(
        """UPDATE staff_users
           SET google_sub = ?, avatar_url = ?, name = ?, last_login = ?
           WHERE id = ?;""",
        (
            google_user.get("sub"),
            google_user.get("picture"),
            google_user.get("name", staff["name"]),
            datetime.now(timezone.utc).isoformat(),
            staff["id"],
        )
    )
    conn.commit()
    conn.close()

    return dict(staff)


# ──────────────── Audit Logging ────────────────

def audit_log(
    actor_type: str,
    actor_id: str,
    action: str,
    target_type: str = None,
    target_id: str = None,
    details: str = None,
    ip_address: str = None,
    user_agent: str = None,
):
    """Write an entry to the audit_logs table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO audit_logs
               (actor_type, actor_id, action, target_type, target_id, details, ip_address, user_agent)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
            (actor_type, str(actor_id), action, target_type, target_id, details, ip_address, user_agent)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


def audit_from_request(request: Request, staff: dict, action: str, **kwargs):
    """Convenience: audit_log with IP and user-agent extracted from request."""
    audit_log(
        actor_type="staff",
        actor_id=str(staff["id"]),
        action=action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:200],
        **kwargs,
    )


# ──────────────── Student DB Helpers ────────────────

def get_student_by_telegram_id(telegram_id: int) -> Optional[dict]:
    """Get student from SQLite by telegram_user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE telegram_user_id = ?;", (str(telegram_id),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_by_student_id(student_id: str) -> Optional[dict]:
    """Check if a student_id is already registered."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?;", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_by_phone(phone: str) -> Optional[dict]:
    """Check if a phone number is already registered."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE phone_number = ?;", (phone,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_student_db(telegram_id: int, profile: dict) -> int:
    """Insert or update student in SQLite. Returns student row ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exists
    cursor.execute("SELECT id FROM students WHERE telegram_user_id = ?;", (str(telegram_id),))
    existing = cursor.fetchone()

    if existing:
        # Update existing
        fields = []
        values = []
        for key in ["name", "university", "faculty", "year", "target_role",
                     "skills", "readiness_score", "language", "student_id",
                     "phone_number", "telegram_username", "telegram_full_name",
                     "lms_verification_status"]:
            if key in profile:
                fields.append(f"{key} = ?")
                values.append(profile[key])

        if fields:
            fields.append("updated_at = ?")
            values.append(datetime.now(timezone.utc).isoformat())
            values.append(existing["id"])
            cursor.execute(
                f"UPDATE students SET {', '.join(fields)} WHERE id = ?;",
                tuple(values)
            )

        row_id = existing["id"]
    else:
        # Insert new
        cursor.execute(
            """INSERT INTO students
               (telegram_user_id, telegram_username, telegram_full_name, name,
                student_id, phone_number, university, faculty, year, target_role,
                skills, language, lms_verification_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                str(telegram_id),
                profile.get("telegram_username"),
                profile.get("telegram_full_name"),
                profile.get("name", "Unknown"),
                profile.get("student_id"),
                profile.get("phone_number"),
                profile.get("university", "PDP University"),
                profile.get("faculty"),
                profile.get("year"),
                profile.get("target_role"),
                profile.get("skills", ""),
                profile.get("language", "uz"),
                profile.get("lms_verification_status", "pending"),
            )
        )
        row_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return row_id


def load_all_students_db() -> list[dict]:
    """Load all students from SQLite. Returns list of dicts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE is_active = 1 ORDER BY id;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
