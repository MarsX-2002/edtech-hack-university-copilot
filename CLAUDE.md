## hired.uz (Verified Talent Marketplace)

hired.uz is a verified Talent Marketplace connecting employer companies with verified student talent while strictly respecting student data privacy and consent.

### Commands & Setup:
- **Telegram Bot**:
  - Run bot: `python3 bot.py` (ensure virtual env activated: `source .venv/bin/activate`)
  - Command `/start` initiates registration, resume upload, and profile building.
  - Command `/consent` toggles talent pool visibility/opt-in status.
- **Backend API Server**:
  - Run server: `python3 -m uvicorn src.api:app --reload --port 8000`
- **React Dashboard**:
  - Run locally: `npm run dev` (under `dashboard/`)
  - Build/Typecheck: `npm run build` (under `dashboard/`)

### Project Architecture & Rules:
- **Stack**: Python 3.12, python-telegram-bot, FastAPI, React/TypeScript (Vite), SQLite (`data/career_assistant.db`), ChromaDB for semantic talent search.
- **Roles**: `super_admin`, `career_staff`, `employer`.
- **Data Privacy**: Employers see anonymized student cards. Personal contact info is hidden until an introduction request is approved by both Career Staff and the Student.
- **Translations**: Bot translations in `src/i18n.py`. React dashboard has translation keys inside `App.tsx`.

