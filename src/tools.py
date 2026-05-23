"""
Tools specification for Career AI Assistant.
These functions are exposed natively to the Generative AI model as executable tools.
"""
import re
from src.rag import retrieve_context
from src.storage import load_vacancies, get_student, save_student
from src.db import log_risk

def search_knowledge_base(query: str) -> list[dict]:
    """Queries the university career center knowledge base (text and pdf guidelines) 
    using the search query and returns the most relevant retrieved text chunks.
    
    Args:
        query: The search term or topic to look up in the career database.
    """
    try:
        chunks = retrieve_context(query)
        # Simplify return to ensure it serializes well
        return [{"filename": c.get("filename", "unknown"), "text": c.get("text", "")} for c in chunks]
    except Exception as e:
        return [{"error": f"Failed to retrieve from knowledge base: {e}"}]

def search_vacancies(query: str) -> list[dict]:
    """Searches the available database of corporate partner vacancies, stajirovkas, and internships.
    Returns matching vacancies including their requirements, description, salary, and apply link.
    
    Args:
        query: Keywords to search for in vacancy title, company, or required skills (e.g. 'Python', 'React', 'Uzum').
    """
    try:
        vacancies = load_vacancies()
        query_words = set(query.lower().split())
        if not query_words:
            return vacancies[:5]

        scored = []
        for v in vacancies:
            score = 0
            title = v.get("title", "").lower()
            company = v.get("company", "").lower()
            skills = [s.lower() for s in v.get("skills_required", [])]
            desc = v.get("description", "").lower()

            # Scoring match
            for word in query_words:
                if word in title:
                    score += 15
                if word in company:
                    score += 10
                if any(word in sk for sk in skills):
                    score += 20
                if word in desc:
                    score += 5

            if score > 0:
                scored.append((score, v))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:5]]
    except Exception as e:
        return [{"error": f"Failed to search vacancies: {e}"}]

def check_resume_ats(resume_markdown: str, target_position: str) -> dict:
    """Performs a local ATS (Applicant Tracking System) check on a candidate's resume markdown draft.
    Calculates a compatibility score, validates structure, identifies critical keyword gaps, and returns
    actionable recommendations.
    
    Args:
        resume_markdown: The markdown content of the candidate's resume.
        target_position: The job title or role the candidate is applying for (e.g., 'Backend Developer', 'UX/UI Designer').
    """
    resume_lower = resume_markdown.lower()
    score = 100
    missing_sections = []
    missing_keywords = []
    recommendations = []

    # 1. Structure Verification
    sections = {
        "summary": ["summary", "profile", "objective", "kirish", "haqida", "о себе", "резюме"],
        "experience": ["experience", "employment", "work", "tajriba", "ish joyi", "опыт работы"],
        "education": ["education", "academic", "tahsil", "o'qish", "ma'lumot", "образование"],
        "projects": ["projects", "portfolio", "loyihalar", "работы", "проекты"],
        "skills": ["skills", "competencies", "ko'nikmalar", "texnologiyalar", "навыки", "стек"]
    }

    for sect_name, synonyms in sections.items():
        found = False
        for syn in synonyms:
            # Look for headers in markdown: #, ##, ### or bold indicators
            if re.search(r'(?i)(?:^|[\n#*_])' + re.escape(syn) + r'(?:$|[\n#*_:])', resume_markdown):
                found = True
                break
        if not found:
            missing_sections.append(sect_name)
            score -= 10
            recommendations.append(f"Qidirilayotgan bo'lim topilmadi: {sect_name.upper()}. Uni rezyumega aniq sarlavha bilan qo'shing.")

    # 2. Targeted Role Keywords Check
    role_keywords = {
        "frontend developer": ["javascript", "react", "typescript", "html", "css", "git", "api", "sass", "next.js", "tailwind"],
        "backend developer": ["python", "django", "postgresql", "docker", "rest api", "git", "fastapi", "sql", "redis", "linux"],
        "full-stack developer": ["javascript", "react", "python", "django", "postgresql", "docker", "rest api", "git", "html", "css"],
        "mobile developer": ["flutter", "dart", "kotlin", "swift", "ios", "android", "api", "git", "firebase"],
        "data analyst": ["python", "sql", "pandas", "excel", "power bi", "tableau", "statistics", "numpy", "analyst"],
        "ai/ml engineer": ["python", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "ml", "nlp", "cv", "deep learning"],
        "devops engineer": ["linux", "docker", "kubernetes", "ci/cd", "aws", "bash", "git", "jenkins", "ansible", "nginx"],
        "ux/ui designer": ["figma", "wireframe", "prototype", "ux", "ui", "design", "user research", "adobe", "mockup"],
        "project manager": ["scrum", "agile", "jira", "roadmap", "milestone", "communication", "budget", "planning", "delivery"]
    }

    target_clean = target_position.lower().strip()
    matched_role = None
    for role, kw_list in role_keywords.items():
        if role in target_clean or target_clean in role:
            matched_role = role
            break

    if matched_role:
        for kw in role_keywords[matched_role]:
            if kw not in resume_lower:
                missing_keywords.append(kw.upper())
                score -= 4
                recommendations.append(f"Karyera yo'nalishingiz uchun muhim kalit so'z (keyword) topilmadi: {kw.upper()}. Buni rezyume loyihalari yoki ko'nikmalari orasida ishlatishni tavsiya qilamiz.")
    else:
        # Fallback general keywords if position is customized
        general_kws = ["git", "rest api", "sql", "docker"]
        for kw in general_kws:
            if kw not in resume_lower:
                missing_keywords.append(kw.upper())
                score -= 5

    # Clamp score
    score = max(30, min(100, score))

    return {
        "target_position": target_position,
        "score": score,
        "missing_sections": missing_sections,
        "missing_keywords": missing_keywords,
        "recommendations": recommendations[:6],  # limit recommendations
        "is_ats_compliant": score >= 75
    }

def get_student_profile(telegram_id: int) -> dict:
    """Retrieves the registration profile (name, university, year, target role) of the student.
    
    Args:
        telegram_id: The Telegram User ID of the student.
    """
    try:
        profile = get_student(telegram_id)
        if not profile:
            return {"error": "Student profile not found."}
        return profile
    except Exception as e:
        return {"error": f"Failed to load student profile: {e}"}

def update_student_profile(telegram_id: int, profile_data: dict) -> dict:
    """Updates the registration profile fields of the student in the persistent database.
    
    Args:
        telegram_id: The Telegram User ID of the student.
        profile_data: Key-value dictionary containing the updated fields (e.g. {'target_role': 'AI/ML Engineer', 'skills': 'Python, PyTorch'}).
    """
    try:
        current = get_student(telegram_id) or {}
        for k, v in profile_data.items():
            current[k] = v
        save_student(telegram_id, current)
        return {"status": "success", "profile": current}
    except Exception as e:
        return {"error": f"Failed to update profile: {e}"}

def log_risk_event(telegram_id: int, category: str, description: str, severity: str = "medium") -> dict:
    """Logs security concerns, API errors, or unexpected outputs to the risk monitoring dashboard.
    
    Args:
        telegram_id: The Telegram User ID of the student.
        category: The class of issue ('hallucination', 'api_failure', 'anomaly', 'unauthorized').
        description: A short explanation of what went wrong or what anomaly was detected.
        severity: High, Medium, or Low.
    """
    try:
        log_risk(telegram_id, category, description, severity)
        return {"status": "success", "logged": True}
    except Exception as e:
        return {"error": f"Failed to log risk event: {e}"}
