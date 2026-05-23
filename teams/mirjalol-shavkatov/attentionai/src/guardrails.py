"""
Safety guardrails middleware for PDP Career Center.
Filters input prompt injections, off-topic queries, and output anomalies/hallucinations.
"""
import re
import logging
from src.rag import call_llm
from src.config import DEFAULT_PROVIDER

logger = logging.getLogger(__name__)

# List of offensive keywords (UZ, RU, EN) and typical prompt injection keywords
INJECTION_KEYWORDS = [
    "ignore previous instructions", "ignore all instructions", "system prompt",
    "you are now a", "bypass filter", "tizim ko'rsatmasi", "yo'riqnomani unuting",
    "игнорируй инструкции", "системный промпт", "jailbreak", "prompt injection",
    "dan keyingi ko'rsatmalarni", "delete prompt", "bypass limit"
]

OFFENSIVE_KEYWORDS = [
    "suka", "blyad", "gandon", "tsex", "jalab", "qo'taq", "sikay", "sikey", "amming",
    "yob", "fuck", "bitch", "asshole", "pidor", "chmo"
]

LOCALIZED_OFF_TOPIC = {
    "uz": "Kechirasiz, men faqat IT karyerasi, rezyumelar, vakansiyalar va intervyular haqidagi savollarga javob bera olaman. Iltimos, mavzuga oid savol yuboring.",
    "ru": "Извините, я могу отвечать только на вопросы, связанные с IT-карьерой, резюме, вакансиями и собеседованиями. Пожалуйста, пришлите вопрос по теме.",
    "en": "Sorry, I can only assist with IT career advice, resumes, job openings, and interview preparation. Please submit a relevant question."
}

LOCALIZED_INJECTION = {
    "uz": "⚠️ Xavfsizlik qoidasi buzildi: kiritilgan so'rov taqiqlangan buyruqlarni o'z ichiga oladi.",
    "ru": "⚠️ Нарушение безопасности: запрос содержит запрещенные команды.",
    "en": "⚠️ Security violation: the input prompt contains restricted instructions."
}

def check_input_safety(user_message: str, language: str = "uz", provider: str = None) -> tuple[bool, str]:
    """
    Checks user input for prompt injections, offensive words, and off-topic queries.
    Returns:
        (is_safe, error_or_warning_message)
    """
    if provider is None:
        provider = DEFAULT_PROVIDER

    msg_lower = user_message.lower()

    # 1. Deterministic Injection Check
    for word in INJECTION_KEYWORDS:
        if word in msg_lower:
            logger.warning(f"Guardrails: Prompt injection detected with keyword '{word}'")
            return False, LOCALIZED_INJECTION.get(language, LOCALIZED_INJECTION["uz"])

    # 2. Deterministic Offensive Word Check
    for word in OFFENSIVE_KEYWORDS:
        # Use regex to match word boundaries
        if re.search(r'\b' + re.escape(word) + r'\b', msg_lower):
            logger.warning(f"Guardrails: Offensive word detected with keyword '{word}'")
            return False, LOCALIZED_OFF_TOPIC.get(language, LOCALIZED_OFF_TOPIC["uz"])

    # 3. LLM-based Off-topic Classifier
    # Skip if mock provider is active
    import src.config
    if provider != "mock" and not src.config.API_FAILED:
        try:
            classification_prompt = f"""You are a security filter for an IT Career AI Assistant.
Analyze if the following user query is related to IT careers, programming, jobs, internships, resumes, coding interviews, learning plans, or tech education.
If the query is related, reply with exactly "SAFE".
If the query is completely off-topic (e.g. cooking, general news, gaming, spam, math puzzles, general programming tasks unrelated to careers, roleplay), reply with exactly "OFF_TOPIC".

User query: "{user_message}"

Classification:"""
            result = call_llm(classification_prompt, provider=provider, temperature=0.0)
            if "OFF_TOPIC" in result.upper():
                logger.warning(f"Guardrails: LLM classified query as OFF_TOPIC: '{user_message}'")
                return False, LOCALIZED_OFF_TOPIC.get(language, LOCALIZED_OFF_TOPIC["uz"])
        except Exception as e:
            logger.warning(f"Guardrails: LLM classification failed: {e}. Falling back to deterministic pass.")

    return True, ""

def check_output_safety(agent_response: str, language: str = "uz") -> tuple[bool, str]:
    """
    Inspects agent response for leakage of internal prompts or massive placeholder errors.
    Returns:
        (is_safe, filtered_or_fallback_response)
    """
    # Look for system prompts leaking
    lower_resp = agent_response.lower()
    leakage_patterns = [
        "system_instruction", "sen professional va talabchan",
        "sen professional rezyume", "sen professional it recruiter",
        "sen professional it mentor"
    ]
    for pattern in leakage_patterns:
        if pattern in lower_resp:
            logger.critical(f"Guardrails: LLM leaked system instructions: '{pattern}' found.")
            fallback = {
                "uz": "Tizimda xatolik yuz berdi. Iltimos, so'rovingizni qayta yuboring.",
                "ru": "Произошла системная ошибка. Пожалуйста, отправьте запрос заново.",
                "en": "A system error occurred. Please resubmit your query."
            }
            return False, fallback.get(language, fallback["uz"])

    return True, agent_response
