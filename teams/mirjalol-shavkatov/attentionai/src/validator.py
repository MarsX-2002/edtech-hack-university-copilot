"""
Unified post-execution validator for PDP Career Center.
Validates LLM output structures, values, and business rules before outputting to user.
"""
import logging
from src.storage import load_vacancies

logger = logging.getLogger(__name__)

# Simple language keyword sets for heuristic validation
LANG_KEYWORDS = {
    "uz": {"va", "bilan", "yoki", "uchun", "bo'lsa", "kerak", "bo'lim", "ish", "talab", "tajriba", "o'rganish"},
    "ru": {"и", "в", "на", "для", "быть", "нужно", "опыт", "резюме", "работа", "требования", "проект"},
    "en": {"the", "and", "with", "for", "resume", "experience", "required", "skills", "project", "education"}
}

def validate_response_language(text: str, expected_lang: str) -> tuple[bool, str]:
    """
    Checks if the generated text is in the expected language using token overlap.
    Only checks if text is long enough (e.g., > 30 chars).
    """
    if not text or len(text) < 30:
        return True, ""

    expected_lang = expected_lang.lower().strip()
    if expected_lang not in LANG_KEYWORDS:
        return True, ""

    # Clean text to words
    words = set(re.findall(r"\b[a-zA-Z'o`O`а-яА-ЯёЁ]+\b", text.lower()))
    if not words:
        return True, ""

    # Count overlaps for all languages
    scores = {}
    for lang, kw_set in LANG_KEYWORDS.items():
        overlap = words.intersection(kw_set)
        scores[lang] = len(overlap)

    # If the expected language has 0 score, but other languages have score > 2, flag it
    max_other_score = max([scores[l] for l in scores if l != expected_lang], default=0)
    if scores[expected_lang] == 0 and max_other_score > 2:
        logger.warning(f"Language validation failed. Expected: {expected_lang}. Scores: {scores}")
        return False, f"Output language is not {expected_lang.upper()}. Please translate the response."

    return True, ""

import re

def validate_vacancy_response(data: dict) -> tuple[bool, str]:
    """
    Validates if the vacancies proposed in VacancyMatchmakingOutput actually exist in local database.
    """
    matches = data.get("matches", [])
    if not matches:
        return True, ""

    active_vacancies = load_vacancies()
    active_companies = {v.get("company", "").lower().strip() for v in active_vacancies}
    active_titles = {v.get("title", "").lower().strip() for v in active_vacancies}

    for idx, match in enumerate(matches):
        company = match.get("company", "").lower().strip()
        title = match.get("vacancy_title", "").lower().strip()

        # Check if company or title does not match any active vacancy
        # We allow substring matches to be user-friendly, but must match at least one active company/title
        company_exists = any(company in ac or ac in company for ac in active_companies)
        title_exists = any(title in at or at in title for at in active_titles)

        if not (company_exists and title_exists):
            logger.warning(f"Vacancy validation failed. Suggested: '{title}' at '{company}' not found in DB.")
            return False, f"The vacancy '{match.get('vacancy_title')}' at '{match.get('company')}' does not exist in our partner database. Please only recommend vacancies from the search results."

    return True, ""

def validate_resume_response(data: dict) -> tuple[bool, str]:
    """
    Validates ResumeOptimizationOutput business rules.
    """
    score = data.get("ats_score", 0)
    if not isinstance(score, int) or score < 0 or score > 100:
        return False, "ATS score must be an integer between 0 and 100."

    # Validate that markdown resume is not empty
    markdown = data.get("optimized_resume_markdown", "").strip()
    if not markdown or len(markdown) < 100:
        return False, "Optimized resume markdown is too short or empty."

    return True, ""

def validate_interview_response(data: dict) -> tuple[bool, str]:
    """
    Validates MockInterviewOutput business rules.
    """
    # question_number must be valid
    qn = data.get("question_number", 1)
    if not isinstance(qn, int) or qn not in [1, 2, 3]:
        return False, "Question number must be 1, 2, or 3."

    # Must contain question text
    qtext = data.get("question_text", "").strip()
    if not qtext:
        return False, "Question text cannot be empty."

    return True, ""

def validate_quiz_response(data: dict) -> tuple[bool, str]:
    """
    Validates QuizOutput business rules.
    """
    qn = data.get("question_number", 1)
    if not isinstance(qn, int) or qn not in [1, 2, 3]:
        return False, "Question number must be 1, 2, or 3."

    qtext = data.get("question_text", "").strip()
    if not qtext:
        return False, "Quiz question text cannot be empty."

    return True, ""
