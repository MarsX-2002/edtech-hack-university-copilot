import os
import sqlite3
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import DATA_DIR, DASHBOARD_URL, ADMIN_PASSWORD
from src.storage import load_students, load_vacancies, get_student_assessments, get_student_interviews
from src.career_modes import match_vacancies
from src.db import DB_FILE, get_db_connection
from src.auth import (
    get_current_staff, require_role, require_department,
    create_access_token, create_refresh_token, rotate_refresh_token,
    revoke_all_tokens, set_auth_cookies, clear_auth_cookies,
    exchange_google_code, validate_staff_login, audit_log, audit_from_request,
    ACCESS_COOKIE, REFRESH_COOKIE, hash_password, verify_password
)

app = FastAPI(title="PDP University Career Center - Admin Analytics API")

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS restricted to DASHBOARD_URL
origins = [DASHBOARD_URL]
if "localhost" in DASHBOARD_URL:
    origins.append(DASHBOARD_URL.replace("localhost", "127.0.0.1"))
elif "127.0.0.1" in DASHBOARD_URL:
    origins.append(DASHBOARD_URL.replace("127.0.0.1", "localhost"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PYDANTIC MODELS ───
class LoginRequest(BaseModel):
    email: str
    password: str

class ChangePasswordRequest(BaseModel):
    email: str
    old_password: str
    new_password: str

class StaffCreateRequest(BaseModel):
    email: str
    name: str
    role: str
    department: str
    company_name: Optional[str] = None
    contact_phone: Optional[str] = None


class EmployerRegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    company_name: str
    contact_phone: Optional[str] = None
    reason_for_joining: Optional[str] = None


class StaffUpdateRequest(BaseModel):
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[int] = None

class StudentVerifyRequest(BaseModel):
    status: str

class ScheduleInterviewRequest(BaseModel):
    role: Optional[str] = None

# ─── ENDPOINTS ───

# ─── AUTH ENDPOINTS ───

@app.post("/auth/register-employer")
@limiter.limit("5/minute")
async def register_employer(request: Request, body: EmployerRegisterRequest):
    """Public self-registration endpoint for employers. Creates a pending employer account."""
    email = body.email.strip().lower()
    name = body.name.strip()
    company_name = body.company_name.strip()
    contact_phone = body.contact_phone.strip() if body.contact_phone else ""
    reason_for_joining = body.reason_for_joining.strip() if body.reason_for_joining else ""
    password = body.password
    
    if not email or not password or not name or not company_name:
        raise HTTPException(status_code=400, detail="All fields except phone number and reason are required")
        
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM staff_users WHERE LOWER(email) = ?;", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email address is already registered.")
        
    # Create staff_users record (initially inactive)
    pwd_hash = hash_password(password)
    cursor.execute(
        """INSERT INTO staff_users (email, name, role, department, is_active, password_hash, must_change_password)
           VALUES (?, ?, 'employer', 'career', 0, ?, 0);""",
        (email, name, pwd_hash)
    )
    new_id = cursor.lastrowid
    
    # Create employers record
    cursor.execute(
        """INSERT INTO employers (staff_user_id, company_name, contact_name, contact_email, contact_phone, status, reason_for_joining)
           VALUES (?, ?, ?, ?, ?, 'pending', ?);""",
        (new_id, company_name, name, email, contact_phone, reason_for_joining)
    )
    
    conn.commit()
    conn.close()
    
    audit_log("system", email, "employer_registered", details=f"Employer company={company_name} registered, status=pending")
    return {"status": "ok", "message": "Employer account registered successfully. Pending staff approval."}


@app.post("/auth/login")
@limiter.limit("10/minute")
async def auth_login(request: Request, body: LoginRequest, response: Response):
    """Log in allowlisted staff using email and password."""
    email = body.email.strip().lower()
    password = body.password
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if email matches
    cursor.execute("SELECT * FROM staff_users WHERE LOWER(email) = ?;", (email,))
    staff = cursor.fetchone()
    
    if not staff:
        conn.close()
        audit_log("system", email, "failed_login", details="Email not in allowlist")
        raise HTTPException(
            status_code=403,
            detail="Kirish taqiqlandi. Sizning emailingiz ro'yxatdan o'tmagan. / Access denied. Your email is not allowlisted."
        )
        
    if not staff["is_active"]:
        # Check if employer is pending or rejected for a better message
        if staff["role"] == "employer":
            cursor.execute("SELECT status FROM employers WHERE staff_user_id = ?;", (staff["id"],))
            employer = cursor.fetchone()
            if employer:
                if employer["status"] == "pending":
                    conn.close()
                    raise HTTPException(
                        status_code=403,
                        detail="Sizning hisobingiz hali tasdiqlanmagan. Karyera markazi tasdiqlashini kuting. / Your employer account is pending approval by the Career Center."
                    )
                elif employer["status"] == "rejected":
                    conn.close()
                    raise HTTPException(
                        status_code=403,
                        detail="Sizning hisobingiz rad etilgan. / Your employer account has been rejected."
                    )
        conn.close()
        audit_log("system", email, "failed_login", details="Account deactivated")
        raise HTTPException(status_code=403, detail="Hisob faolsizlantirilgan. / Account deactivated.")

    # Check password hash in SQLite
    if not verify_password(password, staff["password_hash"]):
        conn.close()
        audit_log("system", email, "failed_login", details="Incorrect password")
        raise HTTPException(
            status_code=401,
            detail="Noto'g'ri parol. / Incorrect password."
        )
        
    # Check if they need to change password
    if staff["must_change_password"]:
        conn.close()
        return {
            "must_change_password": True,
            "email": staff["email"]
        }
        
    # Update last_login
    from datetime import datetime, timezone
    cursor.execute(
        "UPDATE staff_users SET last_login = ? WHERE id = ?;",
        (datetime.now(timezone.utc).isoformat(), staff["id"])
    )
    conn.commit()
    conn.close()
    
    # Issue tokens
    access_token = create_access_token(
        staff_id=staff["id"],
        email=staff["email"],
        role=staff["role"],
        department=staff["department"]
    )
    refresh_token, _ = create_refresh_token(staff["id"])
    
    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Audit log
    audit_log(
        actor_type="staff",
        actor_id=str(staff["id"]),
        action="login",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:200]
    )
    
    staff_dict = dict(staff)
    return {
        "id": staff_dict["id"],
        "email": staff_dict["email"],
        "name": staff_dict["name"],
        "role": staff_dict["role"],
        "department": staff_dict["department"],
        "avatar_url": staff_dict.get("avatar_url"),
        "must_change_password": False
    }


@app.post("/auth/change-password")
@limiter.limit("10/minute")
async def auth_change_password(request: Request, body: ChangePasswordRequest, response: Response):
    """Change temporary password upon first login, then log in the staff user."""
    email = body.email.strip().lower()
    old_password = body.old_password
    new_password = body.new_password.strip()
    
    if not email or not old_password or not new_password:
        raise HTTPException(status_code=400, detail="All fields are required")
        
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Yangi parol kamida 6 ta belgidan iborat bo'lishi kerak. / New password must be at least 6 characters.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM staff_users WHERE LOWER(email) = ?;", (email,))
    staff = cursor.fetchone()
    
    if not staff:
        conn.close()
        raise HTTPException(status_code=403, detail="Email address not found")
        
    if not staff["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Account deactivated")
        
    # Verify old password
    if not verify_password(old_password, staff["password_hash"]):
        conn.close()
        raise HTTPException(status_code=401, detail="Eski parol noto'g'ri. / Old password is incorrect.")
        
    # Hash new password and update
    new_hash = hash_password(new_password)
    from datetime import datetime, timezone
    now_str = datetime.now(timezone.utc).isoformat()
    
    cursor.execute(
        """UPDATE staff_users 
           SET password_hash = ?, must_change_password = 0, last_login = ?
           WHERE id = ?;""",
        (new_hash, now_str, staff["id"])
    )
    conn.commit()
    conn.close()
    
    # Issue tokens
    access_token = create_access_token(
        staff_id=staff["id"],
        email=staff["email"],
        role=staff["role"],
        department=staff["department"]
    )
    refresh_token, _ = create_refresh_token(staff["id"])
    
    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)
    
    # Audit log
    audit_log(
        actor_type="staff",
        actor_id=str(staff["id"]),
        action="change_password",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:200]
    )
    
    staff_dict = dict(staff)
    return {
        "id": staff_dict["id"],
        "email": staff_dict["email"],
        "name": staff_dict["name"],
        "role": staff_dict["role"],
        "department": staff_dict["department"],
        "avatar_url": staff_dict.get("avatar_url"),
        "must_change_password": False
    }


@app.post("/auth/refresh")
@limiter.limit("10/minute")
async def auth_refresh(request: Request, response: Response):
    """Rotate refresh token and issue new access token."""
    old_refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not old_refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    try:
        staff, new_refresh, _ = rotate_refresh_token(old_refresh_token)
        
        access_token = create_access_token(
            staff_id=staff["id"],
            email=staff["email"],
            role=staff["role"],
            department=staff["department"]
        )
        
        set_auth_cookies(response, access_token, new_refresh)
        
        return {
            "id": staff["id"],
            "email": staff["email"],
            "name": staff["name"],
            "role": staff["role"],
            "department": staff["department"],
            "avatar_url": staff.get("avatar_url")
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Refresh failed: {str(e)}")


@app.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    """Logout current user and clear cookies."""
    old_refresh_token = request.cookies.get(REFRESH_COOKIE)
    if old_refresh_token:
        try:
            import hashlib
            old_hash = hashlib.sha256(old_refresh_token.encode()).hexdigest()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT staff_user_id FROM refresh_tokens WHERE token_hash = ?;", (old_hash,))
            row = cursor.fetchone()
            if row:
                revoke_all_tokens(row["staff_user_id"])
                audit_log(
                    actor_type="staff",
                    actor_id=str(row["staff_user_id"]),
                    action="logout",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent", "")[:200]
                )
            conn.close()
        except Exception:
            pass
            
    clear_auth_cookies(response)
    return {"status": "ok"}


@app.get("/auth/me")
async def auth_me(staff: dict = Depends(get_current_staff)):
    """Return info about current logged in user."""
    return {
        "id": staff["id"],
        "email": staff["email"],
        "name": staff["name"],
        "role": staff["role"],
        "department": staff["department"],
        "avatar_url": staff.get("avatar_url")
    }


# Google Auth Config endpoint removed as Google Auth is deactivated.


# ─── API ENDPOINTS ───

@app.get("/api/stats")
@limiter.limit("60/minute")
def get_stats(request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer"))):
    """Get aggregate stats for dashboard metrics cards."""
    audit_from_request(request, staff, "dashboard_access", details="stats")
    try:
        students = load_students()
        total_students = len(students)
        
        # Seeker status: students registered in target roles
        active_seekers = sum(1 for s in students.values() if s.get("target_role"))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Telemetry metrics
        cursor.execute("""
            SELECT 
                AVG(latency_ms) as avg_latency,
                SUM(input_tokens + output_tokens) as total_tokens,
                COUNT(*) as total_msgs
            FROM messages 
            WHERE sender = 'agent' AND latency_ms IS NOT NULL;
        """)
        row = cursor.fetchone()
        avg_latency = (row["avg_latency"] or 0.0) / 1000.0 if row else 0.0
        total_tokens = row["total_tokens"] or 0 if row else 0
        total_msgs = row["total_msgs"] or 0 if row else 0
        
        # Count active conversations
        cursor.execute("SELECT COUNT(*) as active_convs FROM conversations WHERE status = 'active';")
        active_convs = cursor.fetchone()["active_convs"]
        
        # Count guardrail hits (failures)
        cursor.execute("SELECT COUNT(*) as guardrail_hits FROM messages WHERE guardrail_status IS NOT NULL AND guardrail_status != 'passed';")
        guardrail_hits = cursor.fetchone()["guardrail_hits"]
        
        # Count critical risks
        cursor.execute("SELECT COUNT(*) as critical_risks FROM risk_events WHERE severity IN ('high', 'critical');")
        critical_risks = cursor.fetchone()["critical_risks"]
        
        conn.close()
        
        return {
            "total_students": total_students,
            "active_seekers": active_seekers,
            "avg_latency_sec": round(avg_latency, 2),
            "total_tokens_exchanged": total_tokens,
            "total_agent_turns": total_msgs,
            "active_sessions": active_convs,
            "guardrail_hits": guardrail_hits,
            "critical_risks": critical_risks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {e}")


@app.get("/api/students")
@limiter.limit("60/minute")
def get_students_list(request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer"))):
    """Returns a list of all registered students with categorized skills (verified/unverified)."""
    audit_from_request(request, staff, "dashboard_access", details="students_list")
    try:
        students = load_students()
        results = []
        
        for sid, s in students.items():
            raw_skills = s.get("skills", "")
            verified_skills = []
            unverified_skills = []
            
            if raw_skills:
                for skill in raw_skills.split(","):
                    skill = skill.strip()
                    if not skill:
                        continue
                    if "(Verified)" in skill:
                        verified_skills.append(skill.replace(" (Verified)", "").strip())
                    else:
                        unverified_skills.append(skill)
                        
            results.append({
                "id": s.get("id"),
                "telegram_id": sid,
                "name": s.get("name"),
                "university": s.get("university"),
                "faculty": s.get("faculty"),
                "year": s.get("year"),
                "target_role": s.get("target_role"),
                "verified_skills": verified_skills,
                "unverified_skills": unverified_skills,
                "readiness_score": s.get("readiness_score"),
                "lms_verification_status": s.get("lms_verification_status", "pending"),
                "student_id": s.get("student_id"),
                "phone_number": s.get("phone_number")
            })
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch students: {e}")


@app.get("/api/students/{telegram_id}")
@limiter.limit("60/minute")
def get_student_detail(telegram_id: str, request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer"))):
    """Retrieve detailed info, assessments, and resumes for a specific student."""
    audit_from_request(request, staff, "profile_opened", target_type="student", target_id=telegram_id)
    students = load_students()
    if telegram_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
        
    s = students[telegram_id]
    
    # Load assessments
    assessments = get_student_assessments(int(telegram_id))
    
    # Load resumes from resumes.json
    resumes_file = DATA_DIR / "resumes.json"
    resumes = []
    if resumes_file.exists():
        try:
            with open(resumes_file, "r", encoding="utf-8") as f:
                all_resumes = json.load(f)
                resumes = [r for r in all_resumes if str(r.get("telegram_id")) == telegram_id]
        except Exception:
            pass

    # Load quiz history from SQLite (quiz_attempts table)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic, score, total_questions, timestamp 
        FROM quiz_attempts 
        WHERE telegram_id = ? 
        ORDER BY id DESC;
    """, (telegram_id,))
    quizzes = [dict(row) for row in cursor.fetchall()]
    conn.close()

    raw_skills = s.get("skills", "")
    verified_skills = []
    unverified_skills = []
    if raw_skills:
        for skill in raw_skills.split(","):
            skill = skill.strip()
            if not skill:
                continue
            if "(Verified)" in skill:
                verified_skills.append(skill.replace(" (Verified)", "").strip())
            else:
                unverified_skills.append(skill)

    # Load interviews
    interviews = get_student_interviews(int(telegram_id))
    
    # Calculate recommended vacancies
    recommended_vacancies = match_vacancies(s)

    return {
        "profile": {
            "id": s.get("id"),
            "telegram_id": telegram_id,
            "name": s.get("name"),
            "university": s.get("university"),
            "faculty": s.get("faculty"),
            "year": s.get("year"),
            "target_role": s.get("target_role"),
            "verified_skills": verified_skills,
            "unverified_skills": unverified_skills,
            "readiness_score": s.get("readiness_score"),
            "lms_verification_status": s.get("lms_verification_status", "pending"),
            "student_id": s.get("student_id"),
            "phone_number": s.get("phone_number")
        },
        "assessments": assessments,
        "resumes": resumes,
        "quizzes": quizzes,
        "interviews": interviews,
        "recommended_vacancies": recommended_vacancies
    }


@app.get("/api/vacancies")
@limiter.limit("60/minute")
def get_vacancies_list(request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer", "employer"))):
    """Retrieve all vacancies in the system."""
    audit_from_request(request, staff, "dashboard_access", details="vacancies_list")
    try:
        return load_vacancies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vacancies: {e}")


@app.get("/api/vacancies/{vacancy_id}/matching-students")
@limiter.limit("60/minute")
def get_vacancy_student_matches(vacancy_id: str, request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer", "employer"))):
    """Rank all registered students for a specific vacancy based on their matching scores."""
    try:
        vacancies = load_vacancies()
        vacancy = next((v for v in vacancies if v.get("id") == vacancy_id), None)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Vacancy not found")
            
        students = load_students()
        required_skills = {s.lower().strip() for s in vacancy.get("skills_required", [])}
        v_title = vacancy.get("title", "").lower()
        
        employer_id = int(staff["id"])
        role = staff["role"]
        
        matches = []
        for sid, s in students.items():
            # Extract student skills
            skills_str = s.get("skills", "")
            student_skills = set()
            student_skills_raw = []
            if skills_str:
                student_skills_raw = [sk.strip() for sk in skills_str.split(",") if sk.strip()]
                student_skills = {sk.replace(" (Verified)", "").strip().lower() for sk in student_skills_raw}
                
            # Score logic matching career_modes.py match_vacancies
            score = 0
            overlap = student_skills & required_skills
            if required_skills:
                score += len(overlap) / len(required_skills) * 60
                
            s_target_role = s.get("target_role", "").lower()
            if s_target_role and any(word in v_title for word in s_target_role.split()):
                score += 30
            if "intern" in v_title or "junior" in v_title:
                score += 10
                
            if score > 0:
                score = 40 + (score * 0.45)
            else:
                score = 40
                
            score = min(88, round(score))
            
            # Map matched vs missing skills
            matched_list = []
            missing_list = []
            for req in vacancy.get("skills_required", []):
                if req.lower().strip() in student_skills:
                    # check if verified
                    is_verified = any(f"{req} (Verified)".lower() == sk.lower() for sk in student_skills_raw)
                    matched_list.append({"name": req, "verified": is_verified})
                else:
                    missing_list.append(req)
                    
            if score > 0 or len(overlap) > 0:
                intro_status = None
                intro_req_id = None
                if role == "employer":
                    conn_intro = get_db_connection()
                    cursor_intro = conn_intro.cursor()
                    cursor_intro.execute(
                        "SELECT id, status FROM intro_requests WHERE employer_id = ? AND student_id = ? ORDER BY id DESC LIMIT 1;",
                        (employer_id, s.get("id"))
                    )
                    intro_row = cursor_intro.fetchone()
                    conn_intro.close()
                    if intro_row:
                        intro_status = intro_row["status"]
                        intro_req_id = intro_row["id"]
                        
                matches.append({
                    "id": s.get("id"),
                    "telegram_id": sid,
                    "name": s.get("name"),
                    "target_role": s.get("target_role"),
                    "match_score": score,
                    "skills_matched": matched_list,
                    "skills_missing": missing_list,
                    "readiness_score": s.get("readiness_score"),
                    "intro_status": intro_status,
                    "intro_request_id": intro_req_id
                })
                
        # Sort by match score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return {
            "vacancy": vacancy,
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match students: {e}")


@app.get("/api/analytics/weak-areas")
@limiter.limit("60/minute")
def get_weak_areas_report(request: Request, staff = Depends(require_role("super_admin", "career_staff"))):
    """Aggregate common skill gaps and missing keywords across all students' target roles."""
    try:
        students = load_students()
        vacancies = load_vacancies()
        
        # Map vacancies by general keyword matching for role category
        skill_gap_counts = {}
        
        for sid, s in students.items():
            s_role = s.get("target_role", "")
            if not s_role:
                continue
                
            # Find vacancies matching student target role
            matching_vacs = [v for v in vacancies if s_role.lower() in v.get("title", "").lower() or v.get("title", "").lower() in s_role.lower()]
            if not matching_vacs:
                # fall back to all vacancies
                matching_vacs = vacancies
                
            # Extract student skills
            raw_skills = s.get("skills", "")
            student_skills = set()
            if raw_skills:
                student_skills = {sk.replace(" (Verified)", "").strip().lower() for sk in raw_skills.split(",")}
                
            # Accumulate required skills not possessed
            for v in matching_vacs:
                for req in v.get("skills_required", []):
                    req_clean = req.strip()
                    if req_clean.lower() not in student_skills:
                        skill_gap_counts[req_clean] = skill_gap_counts.get(req_clean, 0) + 1
                        
        # Sort and take top 10
        sorted_gaps = sorted(skill_gap_counts.items(), key=lambda x: x[1], reverse=True)
        results = [{"skill": k, "missing_count": v} for k, v in sorted_gaps[:10]]
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compile weak areas: {e}")


@app.get("/api/telemetry")
@limiter.limit("60/minute")
def get_telemetry_metrics(request: Request, staff = Depends(require_role("super_admin"))):
    """Fetch structured system telemetry charts data and safety risk logs."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Latency distribution (last 50 agent messages)
        cursor.execute("""
            SELECT id, latency_ms/1000.0 as latency_sec, timestamp 
            FROM messages 
            WHERE sender = 'agent' AND latency_ms IS NOT NULL 
            ORDER BY id DESC 
            LIMIT 50;
        """)
        latency_trend = [dict(row) for row in cursor.fetchall()]
        latency_trend.reverse()  # chronological order
        
        # 2. Token trends (last 50 agent messages)
        cursor.execute("""
            SELECT id, input_tokens, output_tokens, timestamp 
            FROM messages 
            WHERE sender = 'agent' AND input_tokens IS NOT NULL 
            ORDER BY id DESC 
            LIMIT 50;
        """)
        token_trend = [dict(row) for row in cursor.fetchall()]
        token_trend.reverse()
        
        # 3. Guardrail status count
        cursor.execute("""
            SELECT guardrail_status, COUNT(*) as cnt 
            FROM messages 
            WHERE guardrail_status IS NOT NULL 
            GROUP BY guardrail_status;
        """)
        guardrail_stats = {row["guardrail_status"]: row["cnt"] for row in cursor.fetchall()}
        
        # 4. Self-correction retry distribution
        cursor.execute("""
            SELECT validation_attempts, COUNT(*) as cnt 
            FROM messages 
            WHERE sender = 'agent' AND validation_attempts IS NOT NULL 
            GROUP BY validation_attempts;
        """)
        retry_stats = {f"Retries: {row['validation_attempts']}": row["cnt"] for row in cursor.fetchall()}
        
        # 5. Recent Risk Events logs
        cursor.execute("""
            SELECT id, telegram_id, category, description, severity, timestamp 
            FROM risk_events 
            ORDER BY id DESC 
            LIMIT 20;
        """)
        risk_logs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "latency_trend": latency_trend,
            "token_trend": token_trend,
            "guardrail_stats": guardrail_stats,
            "retry_stats": retry_stats,
            "risk_logs": risk_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compile telemetry: {e}")


# ─── ADMIN ENDPOINTS ───

@app.get("/api/admin/staff")
def list_staff(staff = Depends(require_role("super_admin"))):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, role, department, is_active, created_at, last_login FROM staff_users ORDER BY id;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/admin/staff")
def add_staff(request: Request, body: StaffCreateRequest, staff = Depends(require_role("super_admin"))):
    email = body.email.lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM staff_users WHERE email = ?;", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Staff user with this email already exists")
        
    import secrets
    temp_password = secrets.token_hex(4)
    pwd_hash = hash_password(temp_password)
    
    cursor.execute(
        """INSERT INTO staff_users (email, name, role, department, is_active, password_hash, must_change_password)
           VALUES (?, ?, ?, ?, 1, ?, 1);""",
        (email, body.name, body.role, body.department, pwd_hash)
    )
    new_id = cursor.lastrowid
    
    if body.role == "employer":
        company = body.company_name or "Unknown Company"
        phone = body.contact_phone or ""
        cursor.execute(
            """INSERT INTO employers (staff_user_id, company_name, contact_name, contact_email, contact_phone, status)
               VALUES (?, ?, ?, ?, ?, 'pending');""",
            (new_id, company, body.name, email, phone)
        )
        
    conn.commit()
    conn.close()
    
    audit_from_request(request, staff, "staff_user_created", target_type="staff", target_id=str(new_id), details=f"Added staff email={email}")
    return {"status": "ok", "id": new_id, "temp_password": temp_password}


@app.patch("/api/admin/staff/{id}")
def update_staff(id: int, request: Request, body: StaffUpdateRequest, staff = Depends(require_role("super_admin"))):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff_users WHERE id = ?;", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Staff user not found")
        
    updates = []
    params = []
    if body.role is not None:
        updates.append("role = ?")
        params.append(body.role)
    if body.department is not None:
        updates.append("department = ?")
        params.append(body.department)
    if body.is_active is not None:
        updates.append("is_active = ?")
        params.append(body.is_active)
        
    if updates:
        params.append(id)
        cursor.execute(f"UPDATE staff_users SET {', '.join(updates)} WHERE id = ?;", tuple(params))
        conn.commit()
        
    conn.close()
    audit_from_request(request, staff, "staff_user_updated", target_type="staff", target_id=str(id), details=f"Updated properties: {body.dict(exclude_none=True)}")
    return {"status": "ok"}


@app.delete("/api/admin/staff/{id}")
def deactivate_staff(id: int, request: Request, staff = Depends(require_role("super_admin"))):
    if id == int(staff["id"]):
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff_users WHERE id = ?;", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Staff user not found")
        
    cursor.execute("UPDATE staff_users SET is_active = 0 WHERE id = ?;", (id,))
    conn.commit()
    conn.close()
    
    revoke_all_tokens(id)
    audit_from_request(request, staff, "staff_user_deactivated", target_type="staff", target_id=str(id))
    return {"status": "ok"}


@app.get("/api/admin/employers")
def get_employers(staff = Depends(require_role("super_admin", "career_staff"))):
    """Fetch all employers and their verification status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT e.id, e.staff_user_id, e.company_name, e.contact_name, e.contact_email, e.contact_phone, e.status, e.reason_for_joining, e.created_at, su.is_active
           FROM employers e
           JOIN staff_users su ON e.staff_user_id = su.id
           ORDER BY e.id DESC;"""
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/admin/employers/{id}/approve")
def approve_employer(id: int, request: Request, staff = Depends(require_role("super_admin", "career_staff"))):
    """Approve employer account, allowing them to search and request introductions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employers WHERE id = ?;", (id,))
    emp = cursor.fetchone()
    if not emp:
        conn.close()
        raise HTTPException(status_code=404, detail="Employer not found")
        
    cursor.execute("UPDATE employers SET status = 'approved' WHERE id = ?;", (id,))
    cursor.execute("UPDATE staff_users SET is_active = 1 WHERE id = ?;", (emp["staff_user_id"],))
    conn.commit()
    conn.close()
    
    audit_from_request(request, staff, "employer_approved", target_type="employer", target_id=str(id))
    return {"status": "ok"}


@app.post("/api/admin/employers/{id}/reject")
def reject_employer(id: int, request: Request, staff = Depends(require_role("super_admin", "career_staff"))):
    """Reject/Deactivate employer account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employers WHERE id = ?;", (id,))
    emp = cursor.fetchone()
    if not emp:
        conn.close()
        raise HTTPException(status_code=404, detail="Employer not found")
        
    cursor.execute("UPDATE employers SET status = 'rejected' WHERE id = ?;", (id,))
    cursor.execute("UPDATE staff_users SET is_active = 0 WHERE id = ?;", (emp["staff_user_id"],))
    conn.commit()
    conn.close()
    
    revoke_all_tokens(emp["staff_user_id"])
    audit_from_request(request, staff, "employer_rejected", target_type="employer", target_id=str(id))
    return {"status": "ok"}


@app.get("/api/admin/audit-logs")
def get_audit_logs(
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    staff = Depends(require_role("super_admin"))
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    if actor_id:
        query += " AND actor_id = ?"
        params.append(actor_id)
    if action:
        query += " AND action = ?"
        params.append(action)
    if target_type:
        query += " AND target_type = ?"
        params.append(target_type)
        
    query += " ORDER BY id DESC LIMIT ? OFFSET ?;"
    params.extend([limit, offset])
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    
    # Get total count for pagination
    count_query = "SELECT COUNT(*) as total FROM audit_logs WHERE 1=1"
    count_params = []
    if actor_id:
        count_query += " AND actor_id = ?"
        count_params.append(actor_id)
    if action:
        count_query += " AND action = ?"
        count_params.append(action)
    if target_type:
        count_query += " AND target_type = ?"
        count_params.append(target_type)
        
    cursor.execute(count_query, tuple(count_params))
    total = cursor.fetchone()["total"]
    
    conn.close()
    return {
        "total": total,
        "logs": [dict(r) for r in rows]
    }


@app.get("/api/admin/students")
def get_admin_students(staff = Depends(require_role("super_admin", "career_staff", "viewer"))):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, telegram_user_id, telegram_username, telegram_full_name, name, 
               student_id, phone_number, university, faculty, year, target_role,
               skills, readiness_score, language, lms_verification_status, created_at
        FROM students ORDER BY id DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.patch("/api/admin/students/{id}/verify")
def verify_student(id: int, request: Request, body: StudentVerifyRequest, staff = Depends(require_role("super_admin", "career_staff"))):
    from datetime import datetime, timezone
    if body.status not in ["verified", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid verification status")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?;", (id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
        
    cursor.execute(
        "UPDATE students SET lms_verification_status = ?, updated_at = ? WHERE id = ?;",
        (body.status, datetime.now(timezone.utc).isoformat(), id)
    )
    conn.commit()
    conn.close()
    
    audit_from_request(
        request, 
        staff, 
        "student_verification_updated", 
        target_type="student", 
        target_id=student["telegram_user_id"], 
        details=f"Verification status set to: {body.status}"
    )
    return {"status": "ok"}


@app.post("/api/admin/students/{telegram_id}/schedule-interview")
async def schedule_mock_interview(telegram_id: str, request: Request, body: ScheduleInterviewRequest, staff = Depends(require_role("super_admin", "career_staff"))):
    """Sends a Telegram invite to the student to start a mock interview."""
    import httpx
    from src.config import TELEGRAM_BOT_TOKEN
    
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Telegram bot is not configured (missing token)")
        
    students = load_students()
    if telegram_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
        
    student = students[telegram_id]
    name = student.get("name", "Student")
    role = body.role or student.get("target_role") or "Software Developer"
    lang = student.get("language", "uz")
    
    # Message content in appropriate language
    if lang == "ru":
        text = (
            f"💼 *Уведомление Карьерного Центра*:\n"
            f"Уважаемый(а) {name}, университетский карьерный центр запланировал для вас "
            f"симуляцию собеседования на роль *{role}*.\n\n"
            f"Нажмите кнопку ниже, чтобы начать."
        )
        btn_text = "🚀 Начать интервью"
    elif lang == "en":
        text = (
            f"💼 *Career Center Notification*:\n"
            f"Dear {name}, the university career center has scheduled a "
            f"mock interview simulation for you for the role of *{role}*.\n\n"
            f"Click the button below to start."
        )
        btn_text = "🚀 Start Interview"
    else: # uz
        text = (
            f"💼 *Karyera Markazi Xabarnomasi*:\n"
            f"Hurmatli {name}, universitet karyera markazi siz uchun "
            f"*{role}* lavozimiga mo'ljallangan suhbat simulyatsiyasini rejalashtirdi.\n\n"
            f"Boshlash uchun quyidagi tugmani bosing."
        )
        btn_text = "🚀 Suhbatni boshlash"

    # Inline button markup
    keyboard = {
        "inline_keyboard": [
            [{"text": btn_text, "callback_data": f"start_scheduled_interview:{role}"}]
        ]
    }
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": int(telegram_id),
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload, timeout=10.0)
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Telegram API error: {res.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Telegram message: {str(e)}")
        
    audit_from_request(
        request,
        staff,
        "student_interview_scheduled",
        target_type="student",
        target_id=telegram_id,
        details=f"Scheduled mock interview for role: {role}"
    )
    return {"status": "ok"}


# ──────────────── EMPLOYER & INTRO REQUESTS ENDPOINTS ────────────────

class IntroRequestCreate(BaseModel):
    student_id: int
    message: str

class IntroRequestAction(BaseModel):
    notes: Optional[str] = None

@app.get("/api/employer/search")
def search_talent(
    query: Optional[str] = None,
    target_role: Optional[str] = None,
    min_readiness: Optional[float] = None,
    skills: Optional[str] = None,
    staff = Depends(require_role("super_admin", "career_staff", "employer"))
):
    """Hybrid AI search for student profiles, accessible by employers and staff."""
    from src.talent_search import search_students_hybrid
    
    employer_id = int(staff["id"])
    role = staff["role"]
    
    # Check approved status for employer
    if role == "employer":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM employers WHERE staff_user_id = ?;", (employer_id,))
        emp_row = cursor.fetchone()
        conn.close()
        if not emp_row or emp_row["status"] != "approved":
            raise HTTPException(status_code=403, detail="Employer account is pending approval by Career Center staff.")
            
    skills_list = None
    if skills:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]
        
    results = search_students_hybrid(
        query=query,
        target_role=target_role,
        min_readiness=min_readiness,
        skills_filter=skills_list
    )
    
    # Check approved intro requests to decide if we reveal contacts
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all completed intro requests for this employer
    cursor.execute(
        "SELECT student_id FROM intro_requests WHERE employer_id = ? AND status = 'completed';",
        (employer_id,)
    )
    approved_student_ids = {r["student_id"] for r in cursor.fetchall()}
    conn.close()
    
    # Process visibility
    for r in results:
        s_id = r["student_id"]
        # Retrieve telegram details from DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_username, phone_number, student_id FROM students WHERE id = ?;", (s_id,))
        details = cursor.fetchone()
        conn.close()
        
        has_access = (role in ["super_admin", "career_staff"]) or (s_id in approved_student_ids)
        
        if has_access and details:
            r["telegram_username"] = details["telegram_username"]
            r["phone_number"] = details["phone_number"]
            r["student_id_code"] = details["student_id"]
            r["contact_revealed"] = True
        else:
            if "name" in r and r["name"]:
                parts = r["name"].split()
                r["name"] = parts[0] if parts else "Candidate"
            r["telegram_username"] = None
            r["phone_number"] = None
            r["student_id_code"] = None
            r["contact_revealed"] = False
            
        # Get intro request status for this student and employer
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, status FROM intro_requests WHERE employer_id = ? AND student_id = ? ORDER BY id DESC LIMIT 1;",
            (employer_id, s_id)
        )
        intro_row = cursor.fetchone()
        conn.close()
        r["intro_status"] = intro_row["status"] if intro_row else None
        r["intro_request_id"] = intro_row["id"] if intro_row else None
        
    return results

@app.post("/api/employer/intro-request")
def create_intro_req(
    body: IntroRequestCreate,
    request: Request,
    staff = Depends(require_role("employer"))
):
    """Employer requests an introduction to a student."""
    employer_id = int(staff["id"])
    student_id = body.student_id
    
    # Check approved status for employer
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM employers WHERE staff_user_id = ?;", (employer_id,))
    emp_row = cursor.fetchone()
    conn.close()
    if not emp_row or emp_row["status"] != "approved":
        raise HTTPException(status_code=403, detail="Employer account is pending approval by Career Center staff.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if student exists
    cursor.execute("SELECT id, name FROM students WHERE id = ?;", (student_id,))
    student_row = cursor.fetchone()
    if not student_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Check if request already exists
    cursor.execute(
        "SELECT id, status FROM intro_requests WHERE employer_id = ? AND student_id = ? ORDER BY id DESC LIMIT 1;",
        (employer_id, student_id)
    )
    existing = cursor.fetchone()
    if existing and existing["status"] in ["pending_staff_approval", "approved_by_staff", "completed"]:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Intro request already exists with status: {existing['status']}")
        
    cursor.execute(
        """INSERT INTO intro_requests (employer_id, student_id, message_from_employer) 
           VALUES (?, ?, ?);""",
        (employer_id, student_id, body.message)
    )
    req_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    audit_from_request(
        request,
        staff,
        "intro_request_created",
        target_type="student",
        target_id=str(student_id),
        details=f"Created intro request #{req_id} for student {student_row['name']}"
    )
    return {"status": "ok", "request_id": req_id}

@app.get("/api/employer/intro-requests")
def get_employer_intros(staff = Depends(require_role("employer"))):
    """Fetch all intro requests created by the active employer."""
    employer_id = int(staff["id"])
    
    # Check approved status for employer
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM employers WHERE staff_user_id = ?;", (employer_id,))
    emp_row = cursor.fetchone()
    conn.close()
    if not emp_row or emp_row["status"] != "approved":
        raise HTTPException(status_code=403, detail="Employer account is pending approval by Career Center staff.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT ir.id, ir.student_id, ir.status, ir.message_from_employer, 
                  ir.staff_decision_notes, ir.created_at, ir.updated_at,
                  s.name as student_name, s.target_role as student_role, s.readiness_score as student_score
           FROM intro_requests ir
           JOIN students s ON ir.student_id = s.id
           WHERE ir.employer_id = ?
           ORDER BY ir.id DESC;""",
        (employer_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        d = dict(r)
        # If status is completed, load contact info too
        if d["status"] == "completed":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_username, phone_number FROM students WHERE id = ?;", (d["student_id"],))
            s_det = cursor.fetchone()
            conn.close()
            if s_det:
                d["telegram_username"] = s_det["telegram_username"]
                d["phone_number"] = s_det["phone_number"]
        else:
            d["telegram_username"] = None
            d["phone_number"] = None
        results.append(d)
    return results

@app.get("/api/admin/intro-requests")
def get_admin_intros(staff = Depends(require_role("super_admin", "career_staff"))):
    """Fetch all intro requests for Career Staff to review."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT ir.id, ir.employer_id, ir.student_id, ir.status, ir.message_from_employer, 
                  ir.staff_decision_notes, ir.created_at, ir.updated_at,
                  s.name as student_name, s.target_role as student_role, s.telegram_user_id as student_telegram_id,
                  su.name as employer_name, su.email as employer_email
           FROM intro_requests ir
           JOIN students s ON ir.student_id = s.id
           JOIN staff_users su ON ir.employer_id = su.id
           ORDER BY ir.id DESC;"""
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/admin/intro-requests/{id}/approve")
async def approve_intro_staff(id: int, request: Request, body: IntroRequestAction, staff = Depends(require_role("super_admin", "career_staff"))):
    """Staff approves employer request. Triggers a Telegram interactive push to student."""
    from src.config import TELEGRAM_BOT_TOKEN
    from datetime import datetime
    import httpx
    import json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT ir.*, s.name as student_name, s.telegram_user_id, s.language, su.name as employer_name
           FROM intro_requests ir
           JOIN students s ON ir.student_id = s.id
           JOIN staff_users su ON ir.employer_id = su.id
           WHERE ir.id = ?;""",
        (id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Intro request not found")
        
    if row["status"] != "pending_staff_approval":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Request is in status: {row['status']}")
        
    cursor.execute(
        "UPDATE intro_requests SET status = 'approved_by_staff', staff_decision_by = ?, staff_decision_notes = ?, updated_at = ? WHERE id = ?;",
        (staff["id"], body.notes, datetime.now().isoformat(), id)
    )
    conn.commit()
    conn.close()
    
    # Trigger Telegram Notification to student
    if TELEGRAM_BOT_TOKEN:
        lang = row["language"] or "uz"
        emp_name = row["employer_name"]
        
        if lang == "ru":
            msg_text = (
                f"💼 *Запрос на знакомство от работодателя*:\n"
                f"Представитель *{emp_name}* хочет связаться с вами для обсуждения карьерных возможностей.\n\n"
                f"Вы согласны поделиться своими контактами (телефон и Telegram)?"
            )
            btn_yes = "✅ Да, поделиться"
            btn_no = "❌ Нет, отклонить"
        elif lang == "en":
            msg_text = (
                f"💼 *Intro Request from Employer*:\n"
                f"Employer *{emp_name}* wants to connect with you regarding job opportunities.\n\n"
                f"Do you consent to share your contact details (phone and Telegram)?"
            )
            btn_yes = "✅ Yes, share"
            btn_no = "❌ No, decline"
        else: # uz
            msg_text = (
                f"💼 *Ish beruvchidan aloqa so'rovi*:\n"
                f"*{emp_name}* kompaniyasi siz bilan vakansiyalar bo'yicha bog'lanishni so'ramoqda.\n\n"
                f"Kontaktlaringizni (telefon va Telegram) baham ko'rishga rozimisiz?"
            )
            btn_yes = "✅ Ha, ulashish"
            btn_no = "❌ Yo'q, rad etish"
            
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": btn_yes, "callback_data": f"intro_accept:{id}"},
                    {"text": btn_no, "callback_data": f"intro_decline:{id}"}
                ]
            ]
        }
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": int(row["telegram_user_id"]),
            "text": msg_text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(keyboard)
        }
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=10.0)
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
            
    audit_from_request(
        request,
        staff,
        "intro_request_approved_by_staff",
        target_type="student",
        target_id=str(row["student_id"]),
        details=f"Staff approved request #{id}. Student push notification sent."
    )
    return {"status": "ok"}

@app.post("/api/admin/intro-requests/{id}/reject")
def reject_intro_staff(id: int, request: Request, body: IntroRequestAction, staff = Depends(require_role("super_admin", "career_staff"))):
    """Staff rejects employer request."""
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM intro_requests WHERE id = ?;", (id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Intro request not found")
        
    if row["status"] != "pending_staff_approval":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Request is in status: {row['status']}")
        
    cursor.execute(
        "UPDATE intro_requests SET status = 'rejected_by_staff', staff_decision_by = ?, staff_decision_notes = ?, updated_at = ? WHERE id = ?;",
        (staff["id"], body.notes, datetime.now().isoformat(), id)
    )
    conn.commit()
    conn.close()
    
    audit_from_request(
        request,
        staff,
        "intro_request_rejected_by_staff",
        target_type="student",
        target_id=str(row["student_id"]),
        details=f"Staff rejected request #{id}. Notes: {body.notes}"
    )
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
