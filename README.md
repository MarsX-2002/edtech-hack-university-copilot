# hired.uz — Verified Student Talent Marketplace 🎓💼

> **Tagline**: from campus to hired.
> **Student Telegram Bot**: [@university_ai_agent_bot](https://t.me/university_ai_agent_bot) (username: `@university_ai_agent_bot`)

hired.uz is a unified career services and talent marketplace platform. It automates career center operations for universities while serving as a secure pipeline of verified student talent for partner employer companies. It features a modern, premium visitor landing page that introduces the platform, outlines value propositions, and lets visitors sample talent via an interactive preview widget.

---

## 💡 Business Model & Privacy

hired.uz operates on a two-sided value proposition:
1. **For Universities**: Automation of resume reviews, skill gap analysis, stateful interview simulators, and vacancy matching.
2. **For Employers**: Direct access to a pool of verified, pre-screened student talent sorted by algorithmic readiness scores.
3. **For Students**: A 24/7 AI career copilot, resume optimization, and warm introductions to hiring partners.

### 🔒 Student Consent and Data Privacy
We enforce a strict privacy-first model:
* **Consent Check**: Students must explicitly opt-in to the talent pool (via `/consent` or the bot menu).
* **Data Anonymization**: Employers see profile cards containing skills, target roles, education, projects, and work history. All personal contact info (Telegram handles, phone numbers, emails, student ID codes) is **completely hidden**.
* **Introduction Request Loop**:
  1. **Employer Request**: Employer finds a profile they like and clicks **Request Intro** in the dashboard, submitting a short message.
  2. **Staff Verification**: Career Center staff reviews the request. If approved, the system triggers an interactive push notification to the student's Telegram.
  3. **Student Decision**: The student receives an inline message with options to `[ Accept Intro ✅ ]` or `[ Decline Intro ❌ ]`.
  4. **Contact Release**: Only if the student accepts, contact information is released to the employer and both parties are connected.

---

## 🌟 Key Features

### 1. Interactive Landing Page
* 🌐 **Stakeholder Benefits Matrix**: Clearly explains the problems solved and solutions provided for Universities, Employers, and Students.
* 🎮 **Interactive Talent Preview Widget**: Clickable skill tags (Python, React, DevOps, QA) showcasing sample verified student profile card previews in real-time.
* 🚀 **Clear CTAs**: One-click redirection for employers to the secure sign-in portal and students to the Telegram bot.

### 2. Student Telegram Bot Onboarding & AI Tools
* 📋 **AI Resume Parser**: Students upload a PDF/DOCX resume or copy-paste raw work history. Gemini AI extracts education, experience, projects, and skills into a structured schema.
* 💯 **Readiness Scoring**: The system automatically scores profiles from 0 to 100 based on completeness, target role alignment, and verified skills.
* 📊 **Self-Service Controls**: Students can edit their profile drafts, toggle search visibility (`/consent`), and link introductory videos or portfolios.
* 🗣️ **Interview Simulator**: Stateful technical and behavioral practice using STAR evaluation.
* 💼 **Curriculum Deficit & Vacancy Match**: Real-time alignment against active partner listings.

### 3. Employer Talent Search UI
* 🔍 **Smart Hybrid Search**: Natural language search (e.g. *"React developer with Python knowledge and 2 years experience"*) powered by **ChromaDB semantic search** + SQLite filters.
* 📊 **Algorithmic Ranking**: Results sorted by profile readiness scores (0-100) and match relevance.
* 💡 **Explainable Matches**: AI-generated reasoning explaining *why* the student fits the query (e.g. *"Has 2 years Django experience and verified Python skill"*).
* 📁 **Intro Request Management**: Status board tracking approvals (`Pending Review`, `Pending Student Response`, `Connected`, `Declined`).

### 4. Career Center Admin Panel
* 🏫 **Introduction Approvals**: Review queue for employer-to-student connection requests.
* 🗺️ **Student Talent Map**: Unified directory of all student profiles, readiness scores, and verified skill badges.
* 📈 **Overview Analytics**: Aggregated dashboard showing registered users, average readiness, target roles, and AI safety monitoring.
* 📢 **Announcement Broadcast**: Admin utility to send messages directly to all registered students.

---

## 🛠 Technology Stack

* **Frontend**: React (Vite + TypeScript), styling with vanilla CSS.
* **Backend**: FastAPI (Python 3.12).
* **Bot Engine**: `python-telegram-bot` (v22.7+).
* **Database**: SQLite (`data/career_assistant.db`) for relational tables.
* **Vector Store**: ChromaDB (`chroma_db/`) for semantic embedding search.
* **AI Orchestration**: Direct Gemini API integration.

---

## 🚀 Setup & Running Instructions

### 1. Prerequisites
* Python 3.11+
* Node.js v18+
* Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))
* Gemini API Key (configured in environment variables)

### 2. Project Installation
Clone the repository and set up the Python virtual environment:
```bash
# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set up Vite React dashboard dependencies:
```bash
cd dashboard
npm install
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
ADMIN_IDS=your_telegram_chat_id
ADMIN_PASSWORD=secure_admin_password
JWT_SECRET=super_secret_signing_key
```

### 4. Running the Platform

#### Step A: Run the Backend & Init Database
Initialize database tables and launch the FastAPI server:
```bash
# Initialize DB tables
python3 -c "from src.db import init_db; init_db()"

# Start FastAPI server
python3 -m uvicorn src.api:app --reload --port 8000
```

#### Step B: Start the React Dashboard
```bash
cd dashboard
npm run dev
```
Open `http://localhost:5173` in your browser.

#### Step C: Start the Telegram Bot
```bash
python3 bot.py
```

---

## 📂 Project Structure

```
.
├── bot.py                  # Bot bootstrap, runs polling and triggers callback routers
├── dashboard/              # React Frontend Application
│   ├── src/
│   │   ├── App.tsx         # Main UI Router, search interface, and approval boards
│   │   └── index.css       # Premium unified stylesheet
│   └── package.json        # Frontend scripts and dependencies
├── src/
│   ├── api.py              # FastAPI endpoints (employer search, approvals, auth)
│   ├── auth.py             # JWT & role authorization checks (super_admin, staff, employer)
│   ├── db.py               # SQLite tables config, indices, and CRUD utilities
│   ├── bot_handlers.py     # Telegram message receivers and button callback processors
│   ├── career_modes.py     # AI parser logic, score evaluator, and vector updater
│   ├── talent_search.py    # Hybrid search algorithm (SQL + ChromaDB similarity matching)
│   └── config.py           # Global settings, paths, and environment configurations
├── data/
│   └── career_assistant.db # Core SQLite Database
└── chroma_db/              # Vector database storage
```

---

## 🎮 Walkthrough Demo

1. **Student Registration**: In the bot, run `/start`. Complete registration and upload a resume document or paste resume text. Confirm the parsed profile details.
2. **Opt-in Visibility**: Use the `/consent` command or dashboard settings in the bot to opt-in to the talent pool.
3. **Employer Login**: Access the dashboard. Login as an `employer` user (e.g. credentials registered by admin).
4. **Talent Search**: Search for a skill or role (e.g. *"Python backend developer"*). You will see student profile cards showing verified skills, readiness score badge, and matching reasons, but contact details will be anonymized.
5. **Request Connection**: Click **Request Intro** on a student card. Submit a reason/role description.
6. **Staff Approval**: Login as a `career_staff` user. Go to the **Intro Approvals** tab. Review the request and click **Approve**.
7. **Student Accept**: The student receives an interactive button notification in the Telegram bot. The student clicks **✅ Ha, ulashish** (Accept).
8. **Contact Revealed**: The employer's tracker updates to **Connected** status and reveals the student's Telegram handle and phone number.
