import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed; environment variables should be set elsewhere
    pass

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Admin Telegram user IDs (comma-separated in env, or empty)
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

# ── Auth Configuration ──
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-use-a-random-64-char-string")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
INITIAL_ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5173")
ALLOWED_EMAIL_DOMAINS = os.getenv("ALLOWED_EMAIL_DOMAINS", "")  # optional comma-separated

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMBED_MODEL = "models/gemini-embedding-001"
OPENAI_MODEL = "gpt-4o-mini"

# Choose default active provider
if GEMINI_API_KEY:
    DEFAULT_PROVIDER = "gemini"
elif OPENAI_API_KEY:
    DEFAULT_PROVIDER = "openai"
else:
    DEFAULT_PROVIDER = "mock"

# Global state to track if the active API provider is failing
API_FAILED = False

# Knowledge base collection name for Chroma
KB_COLLECTION = "career-knowledge-base"
