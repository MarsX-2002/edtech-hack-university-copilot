# hired.uz — Verified Student Talent Marketplace

> **Tagline**: from campus to hired.
> **Student Telegram Bot**: [@university_ai_agent_bot](https://t.me/university_ai_agent_bot)

hired.uz is a unified career services and talent marketplace platform. It automates career center operations for universities while serving as a secure pipeline of verified student talent for partner employers. The platform includes a React dashboard for employers and staff, a Telegram bot for students, and a FastAPI backend with an AI agent harness.

---

## Business Model & Privacy

hired.uz operates on a three-sided value proposition:
1. **For Universities**: Automation of resume reviews, skill gap analysis, stateful interview simulators, and vacancy matching.
2. **For Employers**: Direct access to a pool of verified, pre-screened student talent sorted by algorithmic readiness scores.
3. **For Students**: A 24/7 AI career copilot, resume optimization, and warm introductions to hiring partners.

### Student Consent and Data Privacy
We enforce a strict privacy-first model:
* **Consent Check**: Students must explicitly opt-in to the talent pool (via `/consent` or the bot menu).
* **Data Anonymization**: Employers see profile cards containing skills, target roles, education, projects, and work history. All personal contact info (Telegram handles, phone numbers, emails, student ID codes) is **completely hidden**.
* **Introduction Request Loop**:
  1. **Employer Request**: Employer finds a profile they like and clicks **Request Intro** in the dashboard, submitting a short message.
  2. **Staff Verification**: Career Center staff reviews the request. If approved, the system triggers an interactive push notification to the student's Telegram.
  3. **Student Decision**: The student receives an inline message with options to `[ Accept Intro ]` or `[ Decline Intro ]`.
  4. **Contact Release**: Only if the student accepts, contact information is released to the employer and both parties are connected.

---

## Key Features

### 1. React Dashboard (Landing Page + Admin Panel)
* **Public Landing Page**: Stakeholder benefits matrix, interactive talent preview widget with clickable skill tags, CTA buttons for employer sign-in and student bot.
* **Employer Self-Registration**: Companies sign up via the dashboard; staff approve or reject registrations.
* **Hybrid Talent Search**: Natural language search (e.g. *"React developer with Python knowledge"*) powered by ChromaDB semantic search + SQLite filters.
* **Algorithmic Ranking**: Results sorted by readiness score (0-100), semantic similarity, profile completeness, and skill keyword match.
* **Explainable Matches**: AI-generated reasoning explaining *why* each student fits the query.
* **Intro Request Management**: Status board tracking approvals (`pending_staff_approval`, `approved_by_staff`, `completed`, `declined_by_student`, `rejected_by_staff`).
* **Vacancy Matching**: AI-powered matching of students to job vacancies with skill overlap scoring.
* **Weak Areas Analytics**: Top skill gaps across the student population vs. active vacancies.
* **Telemetry & Safety Dashboard**: Latency trends, token usage, guardrail statistics, retry distribution, and risk event logs.
* **Staff Management**: CRUD for staff users (super_admin only).
* **Audit Logs**: Filterable admin action log with pagination.
* **Dark/Light Theme** and **Uzbek/English** language toggle.

### 2. Student Telegram Bot
* **AI Resume Parser**: Students upload a PDF or TXT resume, or paste raw work history. Gemini AI extracts education, experience, projects, and skills into a structured profile.
* **Readiness Scoring**: AI-computed profile score (0-100) based on target role alignment, skills, experiences, and projects.
* **Interview Simulator**: Stateful 3-question technical/behavioral practice with STAR evaluation and final X/10 score.
* **Resume/ATS Optimizer**: ATS compatibility check with missing sections and keyword suggestions.
* **Vacancy Matchmaker**: Search job listings, get skill gap analysis, and generate cover letters.
* **AI Quiz**: 3-question technical quiz with verified skill badges awarded for scores >= 2/3.
* **Career Advice**: Open-ended Q&A fallback via the AI agent.
* **Self-Service Controls**: Edit profile, toggle visibility (`/consent`), change language (uz/ru/en).

### 3. AI Agent Harness
* **Multi-Provider**: Gemini (`gemini-2.5-flash`) primary, OpenAI (`gpt-4o-mini`) fallback, mock fallback for development.
* **Tool Calling**: 5 agent tools — search knowledge base, search vacancies, check resume ATS, get/update student profile, log risk events.
* **Guardrails**: Input injection/offensive/off-topic detection; output system-prompt-leakage detection.
* **Self-Correction**: Retry loop (up to 3 attempts) with Pydantic schema-enforced structured output.
* **RAG**: ChromaDB-powered retrieval over the `knowledge_base/` documents (career guide, interview questions, resume templates, skill requirements).

---

## Technology Stack

* **Frontend**: React 19 (Vite + TypeScript 6), vanilla CSS with CSS variables for theming.
* **Backend**: FastAPI (Python 3.12), rate limiting via slowapi.
* **Bot Engine**: `python-telegram-bot` (v22.7+).
* **Database**: SQLite (`data/career_assistant.db`) for relational data.
* **Vector Store**: ChromaDB for semantic embedding search and RAG.
* **AI**: Gemini API (primary), OpenAI API (fallback).
* **Auth**: JWT access/refresh tokens with forced first-login password change.

---

## Setup & Running Instructions

### 1. Prerequisites
* Python 3.12+
* Node.js v18+
* Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
* Gemini API Key

### 2. Project Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd dashboard
npm install
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key        # optional fallback
ADMIN_IDS=your_telegram_chat_id
JWT_SECRET_KEY=random_64_char_string
INITIAL_ADMIN_EMAIL=admin@example.com
DASHBOARD_URL=http://localhost:5173
```

Full list of supported variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | required |
| `GEMINI_API_KEY` | Gemini API key | required |
| `OPENAI_API_KEY` | OpenAI fallback key | optional |
| `ADMIN_IDS` | Comma-separated Telegram admin IDs | — |
| `JWT_SECRET_KEY` | JWT signing key | `CHANGE-ME...` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `INITIAL_ADMIN_EMAIL` | Bootstraps first super_admin | — |
| `DASHBOARD_URL` | CORS origin | `http://localhost:5173` |
| `ALLOWED_EMAIL_DOMAINS` | Email domain allowlist | optional |
| `WEBHOOK_URL` | Webhook URL (default: polling) | optional |
| `PORT` | Webhook port | `8443` |

### 4. Running the Platform

**Step A: Backend & Init Database**
```bash
python3 -c "from src.db import init_db; init_db()"
python3 -m uvicorn src.api:app --reload --port 8000
```

**Step B: React Dashboard**
```bash
cd dashboard
npm run dev
```
Open `http://localhost:5173` in your browser.

**Step C: Telegram Bot**
```bash
python3 bot.py
```

### 5. CLI Tools

**Staff user management** via `manage.py`:
```bash
python3 manage.py create-staff --email admin@example.com --name "Admin" --role super_admin
python3 manage.py list-staff
python3 manage.py reset-password --email admin@example.com
```

---

## Project Structure

```
.
├── bot.py                    # Bot bootstrap, polling, callback routers
├── manage.py                 # CLI for staff user management
├── deploy.sh                 # Local deploy (build + rsync + restart)
├── requirements.txt          # Python dependencies
├── .env                      # Environment config (git-ignored)
├── dashboard/                # React Frontend (Vite + TypeScript)
│   └── src/
│       ├── App.tsx           # Single-page dashboard with tab-based navigation
│       ├── App.css           # Component styles
│       └── index.css         # Global styles and CSS variables
├── src/
│   ├── api.py                # FastAPI app and all REST endpoints
│   ├── agent.py              # Stateful AI agent harness with tool calling
│   ├── analytics.py          # Admin metrics and reporting
│   ├── auth.py               # JWT auth, role checks, token management
│   ├── bot_handlers.py       # Telegram message/callback handlers
│   ├── career_modes.py       # AI resume parser, scoring, interview/vacancy modes
│   ├── config.py             # Env loading and global settings
│   ├── db.py                 # SQLite schema, indices, CRUD helpers
│   ├── guardrails.py         # Input/output safety guardrails
│   ├── i18n.py               # Uzbek, Russian, English translations
│   ├── ingestion.py          # Document parsing, chunking, embedding
│   ├── migrate_students.py   # JSON-to-SQLite migration script
│   ├── rag.py                # Retrieval-Augmented Generation module
│   ├── schemas.py            # Pydantic models for structured agent output
│   ├── storage.py            # JSON persistence + SQLite bridge
│   ├── talent_search.py      # Hybrid search (SQL + ChromaDB + ranking)
│   ├── tools.py              # Tool definitions for the AI agent
│   └── validator.py          # Post-execution output validation
├── knowledge_base/           # RAG source documents
├── context/                  # Project context and architecture docs
├── data/
│   └── career_assistant.db   # SQLite database
├── chroma_db/                # ChromaDB vector storage
├── docs/                     # Static assets (university logos)
└── .github/workflows/        # GitHub Actions deploy workflow
```

---

## API Overview

### Auth (`/auth/`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register-employer` | Employer self-registration |
| POST | `/auth/login` | Email/password login |
| POST | `/auth/change-password` | Force password change on first login |
| POST | `/auth/refresh` | Rotate refresh token |
| POST | `/auth/logout` | Logout and revoke tokens |
| GET | `/auth/me` | Current user info |

### Data (`/api/`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats` | Dashboard aggregate metrics |
| GET | `/api/students` | All students with skills |
| GET | `/api/students/{id}` | Single student detail |
| GET | `/api/vacancies` | All vacancies |
| GET | `/api/vacancies/{id}/matching-students` | Ranked student matches |
| GET | `/api/analytics/weak-areas` | Top skill gaps |
| GET | `/api/telemetry` | Latency, token, guardrail stats |

### Admin (`/api/admin/`)
Staff CRUD, employer approvals, student verification, interview scheduling, intro request review, audit logs.

### Employer (`/api/employer/`)
Talent search with contact visibility controls, intro request creation and status tracking.

---

## Walkthrough Demo

1. **Student Registration**: In the bot, run `/start`. Complete registration and upload a resume (PDF/TXT) or paste resume text. Confirm the parsed profile details.
2. **Opt-in Visibility**: Use the `/consent` command or bot menu to opt into the talent pool.
3. **Employer Sign-Up**: On the dashboard landing page, fill in the employer registration form. A staff admin approves the registration.
4. **Talent Search**: Login as employer. Search for a skill or role (e.g. *"Python backend developer"*). Results show verified skills, readiness score, and match reasons — contact details are anonymized.
5. **Request Connection**: Click **Request Intro** on a student card. Submit a short message.
6. **Staff Approval**: Login as `career_staff`. Go to **Intro Approvals**, review the request, and click **Approve**.
7. **Student Accept**: The student receives an interactive notification in Telegram with Accept/Decline buttons.
8. **Contact Revealed**: On acceptance, the employer's tracker updates to **Connected** and reveals the student's Telegram handle and phone number.
