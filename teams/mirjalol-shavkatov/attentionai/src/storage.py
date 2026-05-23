"""
Storage layer for Career AI Assistant.
Manages student profiles, skill assessments, interview sessions,
resumes, vacancies, and analytics using local JSON files.
"""
import json
from pathlib import Path
from datetime import datetime
from src.config import DATA_DIR

# File paths
STUDENTS_FILE = DATA_DIR / "students.json"
SKILL_ASSESSMENTS_FILE = DATA_DIR / "skill_assessments.json"
INTERVIEW_SESSIONS_FILE = DATA_DIR / "interview_sessions.json"
RESUMES_FILE = DATA_DIR / "resumes.json"
VACANCIES_FILE = DATA_DIR / "vacancies.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"


def _load_json(file_path: Path, default_val):
    if not file_path.exists():
        return default_val
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val


def _save_json(file_path: Path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ──────────────── Student Profiles (SQLite-backed) ────────────────

def load_students() -> dict:
    """Load all student profiles. Returns dict keyed by telegram_user_id for backwards compat."""
    from src.auth import load_all_students_db
    students_list = load_all_students_db()
    result = {}
    for s in students_list:
        tid = s.get("telegram_user_id", "")
        # Convert to legacy dict format for API compatibility
        result[tid] = {
            "id": s.get("id"),
            "name": s.get("name"),
            "university": s.get("university"),
            "faculty": s.get("faculty"),
            "year": s.get("year"),
            "target_role": s.get("target_role"),
            "skills": s.get("skills", ""),
            "readiness_score": s.get("readiness_score"),
            "language": s.get("language", "uz"),
            "student_id": s.get("student_id"),
            "phone_number": s.get("phone_number"),
            "lms_verification_status": s.get("lms_verification_status", "pending"),
            "telegram_username": s.get("telegram_username"),
        }
    return result


def save_students(students: dict):
    """Bulk save — only used by legacy code. Saves each to SQLite."""
    from src.auth import save_student_db
    for tid, profile in students.items():
        save_student_db(int(tid), profile)


def get_student(telegram_id: int) -> dict | None:
    """Get student profile by telegram ID. Returns legacy-format dict or None."""
    from src.auth import get_student_by_telegram_id
    s = get_student_by_telegram_id(telegram_id)
    if not s:
        return None
    return {
        "id": s.get("id"),
        "name": s.get("name"),
        "university": s.get("university"),
        "faculty": s.get("faculty"),
        "year": s.get("year"),
        "target_role": s.get("target_role"),
        "skills": s.get("skills", ""),
        "readiness_score": s.get("readiness_score"),
        "language": s.get("language", "uz"),
        "student_id": s.get("student_id"),
        "phone_number": s.get("phone_number"),
        "lms_verification_status": s.get("lms_verification_status", "pending"),
        "telegram_username": s.get("telegram_username"),
    }


def save_student(telegram_id: int, profile: dict):
    """Save or update a student profile."""
    from src.auth import save_student_db
    save_student_db(telegram_id, profile)


def get_student_lang(telegram_id: int) -> str:
    student = get_student(telegram_id)
    if student:
        return student.get("language", "uz")
    return "uz"


# ──────────────── Skill Assessments ────────────────

def load_skill_assessments() -> list:
    return _load_json(SKILL_ASSESSMENTS_FILE, [])


def save_skill_assessments(assessments: list):
    _save_json(SKILL_ASSESSMENTS_FILE, assessments)


def add_skill_assessment(telegram_id: int, assessment: dict):
    assessments = load_skill_assessments()
    assessment["telegram_id"] = str(telegram_id)
    assessment["timestamp"] = datetime.now().isoformat()
    assessments.append(assessment)
    save_skill_assessments(assessments)


def get_student_assessments(telegram_id: int) -> list:
    assessments = load_skill_assessments()
    return [a for a in assessments if a.get("telegram_id") == str(telegram_id)]


# ──────────────── Interview Sessions ────────────────

def load_interview_sessions() -> list:
    return _load_json(INTERVIEW_SESSIONS_FILE, [])


def save_interview_sessions(sessions: list):
    _save_json(INTERVIEW_SESSIONS_FILE, sessions)


def add_interview_session(telegram_id: int, session: dict):
    sessions = load_interview_sessions()
    session["telegram_id"] = str(telegram_id)
    session["timestamp"] = datetime.now().isoformat()
    sessions.append(session)
    save_interview_sessions(sessions)


def get_student_interviews(telegram_id: int) -> list:
    sessions = load_interview_sessions()
    return [s for s in sessions if s.get("telegram_id") == str(telegram_id)]


# ──────────────── Resumes ────────────────

def load_resumes() -> list:
    return _load_json(RESUMES_FILE, [])


def save_resumes(resumes: list):
    _save_json(RESUMES_FILE, resumes)


def add_resume(telegram_id: int, resume: dict):
    resumes = load_resumes()
    resume["telegram_id"] = str(telegram_id)
    resume["timestamp"] = datetime.now().isoformat()
    resumes.append(resume)
    save_resumes(resumes)


# ──────────────── Vacancies ────────────────

def load_vacancies() -> list:
    return _load_json(VACANCIES_FILE, [])


def save_vacancies(vacancies: list):
    _save_json(VACANCIES_FILE, vacancies)


def prepopulate_vacancies():
    """Seed sample vacancies for demo purposes."""
    vacancies = [
        {
            "id": "v1",
            "title": "Junior Python Backend Developer",
            "company": "Uzum Tech",
            "location": "Tashkent",
            "type": "Full-time",
            "skills_required": ["Python", "Django", "PostgreSQL", "Docker", "REST API"],
            "description": "Backend jamoaga junior dasturchi qidirilmoqda. Django va PostgreSQL bilan ishlash tajribasi talab qilinadi.",
            "salary_range": "$600-900/oy",
            "apply_link": "https://uzum.uz/careers",
        },
        {
            "id": "v2",
            "title": "Frontend Developer Intern",
            "company": "Epam Systems",
            "location": "Remote",
            "type": "Internship",
            "skills_required": ["JavaScript", "React", "TypeScript", "CSS", "Git"],
            "description": "3 oylik stajirovka. React va TypeScript bilimi talab qilinadi. Mentor yordam beradi.",
            "salary_range": "$400-600/oy",
            "apply_link": "https://epam.com/careers",
        },
        {
            "id": "v3",
            "title": "Data Analyst",
            "company": "Payme",
            "location": "Tashkent",
            "type": "Full-time",
            "skills_required": ["Python", "SQL", "Pandas", "Power BI", "Statistics"],
            "description": "Ma'lumotlar tahlili bo'limiga analyst qidirilmoqda. SQL va Python bilan ishlash tajribasi kerak.",
            "salary_range": "$700-1100/oy",
            "apply_link": "https://payme.uz/careers",
        },
        {
            "id": "v4",
            "title": "Junior Mobile Developer (Flutter)",
            "company": "Click",
            "location": "Tashkent",
            "type": "Full-time",
            "skills_required": ["Flutter", "Dart", "REST API", "Firebase", "Git"],
            "description": "Mobile jamoa uchun Flutter developer. Kamida 1 ta published app bo'lishi kerak.",
            "salary_range": "$500-800/oy",
            "apply_link": "https://click.uz/careers",
        },
        {
            "id": "v5",
            "title": "Junior DevOps Engineer",
            "company": "HUMANS",
            "location": "Tashkent / Remote",
            "type": "Full-time",
            "skills_required": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS"],
            "description": "Infratuzilma jamoasiga DevOps engineer. Linux va Docker tajribasi shart.",
            "salary_range": "$800-1200/oy",
            "apply_link": "https://humans.uz/careers",
        },
        {
            "id": "v6",
            "title": "AI/ML Intern",
            "company": "IT Park Uzbekistan",
            "location": "Tashkent",
            "type": "Internship",
            "skills_required": ["Python", "TensorFlow", "PyTorch", "Pandas", "NumPy"],
            "description": "AI loyihalarida ishtirok etish uchun stajirovka. ML va deep learning asoslarini bilish kerak.",
            "salary_range": "$300-500/oy",
            "apply_link": "https://itpark.uz/careers",
        },
    ]
    save_vacancies(vacancies)


# ──────────────── Analytics ────────────────

def load_analytics() -> dict:
    return _load_json(ANALYTICS_FILE, {
        "total_users": 0,
        "feature_usage": {
            "skill_passport": 0,
            "resume_builder": 0,
            "interview_practice": 0,
            "vacancies": 0,
            "career_advice": 0,
        },
        "events": [],
    })


def save_analytics(analytics: dict):
    _save_json(ANALYTICS_FILE, analytics)


def track_event(telegram_id: int, event_type: str, details: str = ""):
    """Track a user event for admin analytics."""
    analytics = load_analytics()
    analytics["events"].append({
        "telegram_id": str(telegram_id),
        "event": event_type,
        "details": details,
        "timestamp": datetime.now().isoformat(),
    })
    # Update feature usage counters
    if event_type in analytics["feature_usage"]:
        analytics["feature_usage"][event_type] += 1
    save_analytics(analytics)


def increment_user_count():
    analytics = load_analytics()
    analytics["total_users"] += 1
    save_analytics(analytics)


# ──────────────── Init ────────────────

def init_storage():
    """Initialize storage files if they do not exist."""
    for fpath, default in [
        (STUDENTS_FILE, {}),
        (SKILL_ASSESSMENTS_FILE, []),
        (INTERVIEW_SESSIONS_FILE, []),
        (RESUMES_FILE, []),
        (VACANCIES_FILE, []),
    ]:
        if not fpath.exists():
            _save_json(fpath, default)

    # Seed vacancies if empty
    if not load_vacancies():
        prepopulate_vacancies()

    # Init analytics
    if not ANALYTICS_FILE.exists():
        save_analytics(load_analytics())
