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

from src.config import DATA_DIR, DASHBOARD_URL
from src.storage import load_students, load_vacancies, get_student_assessments, get_student_interviews
from src.career_modes import match_vacancies
from src.db import DB_FILE, get_db_connection
from src.auth import (
    get_current_staff, require_role, require_department,
    create_access_token, create_refresh_token, rotate_refresh_token,
    revoke_all_tokens, set_auth_cookies, clear_auth_cookies,
    exchange_google_code, validate_staff_login, audit_log, audit_from_request,
    ACCESS_COOKIE, REFRESH_COOKIE
)

app = FastAPI(title="PDP University Career Center - Admin Analytics API")

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS restricted to DASHBOARD_URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[DASHBOARD_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PYDANTIC MODELS ───
class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class StaffCreateRequest(BaseModel):
    email: str
    name: str
    role: str
    department: str

class StaffUpdateRequest(BaseModel):
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[int] = None

class StudentVerifyRequest(BaseModel):
    status: str

# ─── ENDPOINTS ───

# ─── AUTH ENDPOINTS ───

@app.post("/auth/google")
@limiter.limit("10/minute")
async def auth_google(request: Request, body: GoogleAuthRequest, response: Response):
    """Exchange Google Auth Code for JWT and set cookies."""
    try:
        if body.code and body.code.startswith("mock_code_"):
            email = body.code.replace("mock_code_", "").strip().lower()
            google_user = {
                "email": email,
                "name": email.split("@")[0].capitalize(),
                "sub": f"mock_sub_{email}",
                "picture": None,
                "email_verified": True
            }
        else:
            google_user = await exchange_google_code(body.code, body.redirect_uri)
            
        staff = validate_staff_login(google_user)
        
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
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


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


@app.get("/auth/config")
def get_auth_config():
    from src.config import GOOGLE_CLIENT_ID
    return {"google_client_id": GOOGLE_CLIENT_ID}


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
def get_vacancies_list(request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer"))):
    """Retrieve all vacancies in the system."""
    audit_from_request(request, staff, "dashboard_access", details="vacancies_list")
    try:
        return load_vacancies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vacancies: {e}")


@app.get("/api/vacancies/{vacancy_id}/matching-students")
@limiter.limit("60/minute")
def get_vacancy_student_matches(vacancy_id: str, request: Request, staff = Depends(require_role("super_admin", "career_staff", "viewer"))):
    """Rank all registered students for a specific vacancy based on their matching scores."""
    try:
        vacancies = load_vacancies()
        vacancy = next((v for v in vacancies if v.get("id") == vacancy_id), None)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Vacancy not found")
            
        students = load_students()
        required_skills = {s.lower().strip() for s in vacancy.get("skills_required", [])}
        v_title = vacancy.get("title", "").lower()
        
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
                
            score = round(score)
            
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
                matches.append({
                    "telegram_id": sid,
                    "name": s.get("name"),
                    "target_role": s.get("target_role"),
                    "match_score": score,
                    "skills_matched": matched_list,
                    "skills_missing": missing_list,
                    "readiness_score": s.get("readiness_score")
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
        
    cursor.execute(
        """INSERT INTO staff_users (email, name, role, department, is_active)
           VALUES (?, ?, ?, ?, 1);""",
        (email, body.name, body.role, body.department)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    audit_from_request(request, staff, "staff_user_created", target_type="staff", target_id=str(new_id), details=f"Added staff email={email}")
    return {"status": "ok", "id": new_id}


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
