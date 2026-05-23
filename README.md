# Attention AI — Career AI Assistant 🧠

Attention AI is a multilingual, production-grade **University Career Center AI Assistant** delivered as a **Telegram Bot**. It is grounded in university career guides, resume guidelines, and interview questions using Retrieval-Augmented Generation (RAG). 

It empowers students to assess their skills, build ATS-optimized resumes, practice mock interviews with real-time STAR feedback, and match with partner job vacancies. Simultaneously, it provides career administrators with analytics and broadcast capabilities.

---

## 🌟 Key Features

### 1. Student-Facing Features (Multilingual: UZ 🇺🇿 / RU 🇷🇺 / EN 🇬🇧)
*   📋 **Skill Passport & Gap Analysis**: Interactive skill assessment analyzing target roles, projects, technologies, and English levels. Generates a detailed report with a 3-6 month action plan, skill gap identification, and readiness rating.
*   📝 **ATS-Optimized Resume Builder**: Generates markdown-formatted, ATS-friendly professional resumes tailored to target positions, highlighting key metrics, keywords, and qualifications.
*   🎤 **Interactive Interview Simulator**: Simulates technical (hard skills) and behavioral interviews. Evaluates user answers on-the-fly using the international **STAR** methodology (Situation, Task, Action, Result) with scores out of 10.
*   💼 **Partner Vacancy Matching**: Automatically scores and matches students with relevant job vacancies and internships from partner companies based on their skills and preferences.
*   📚 **RAG-based Career Advice**: Continuous Q&A grounded in the university's career guide, networking scripts, and cover letter guidelines.

### 2. Admin & Dashboard Features
*   📊 **Student Activity & Analytics**: Admin-only commands (`/admin` or `/stats`) showing registered user counts, feature usage statistics, average interview simulator scores, and distribution of target roles.
*   📢 **Global Announcement Broadcast**: Allows administrators to broadcast news or job opportunities to all registered users simultaneously using `/broadcast <message>`.

---

## 🛠 Technology Stack

*   **Platform**: Telegram Bot API (via `python-telegram-bot` 22.7+)
*   **Vector Database**: Chroma DB (semantic index of the career knowledge base)
*   **Backend & Logic**: Python 3.11+
*   **LLM Integration**: Gemini API (`gemini-2.5-flash`) or OpenAI API (`gpt-4o-mini`)
*   **Fallback Mode**: Intelligent local mock/offline mode utilizing keyword matching and heuristics when API keys are absent or network requests fail.
*   **Storage**: Local JSON files (`data/students.json`, `data/analytics.json`, `data/vacancies.json`, etc.) acting as a persistent lightweight relational DB.

---

## 🚀 Setup & Installation

### 1. Prerequisites
*   Python 3.11+
*   Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))

### 2. Installation
Clone the repository and install dependencies in a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```env
# Telegram Bot Token (Required to run the bot)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# LLM Providers (Provide at least one. Default falls back to local Mock/Offline mode)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Admin Telegram IDs (Comma-separated integers)
ADMIN_IDS=123456789,987654321
```

### 4. Running the Bot
To start the bot, simply run:

```bash
python bot.py
```

*Note: On startup, the bot automatically parses, chunks, and indexes all text/PDF materials located in the `knowledge_base/` directory into Chroma DB.*

---

## 📂 Project Structure

```
.
├── bot.py                  # Bot bootstrap, configures handlers & starts polling
├── knowledge_base/         # Grounding materials for RAG
│   ├── career_guide.txt    # Networking, LinkedIn & job hunt advice
│   ├── interview_questions.txt # STAR questions & guidelines
│   ├── resume_templates.txt    # ATS resume templates
│   └── skill_requirements.txt  # Role-specific tech/soft skill lists
├── src/
│   ├── analytics.py        # Admin analytics report builder
│   ├── bot_handlers.py     # Main state machine & bot callbacks
│   ├── career_modes.py     # AI core logic (resume gen, mock interviews, passport)
│   ├── config.py           # Config variables & active LLM detection
│   ├── i18n.py             # Multilingual dictionaries (uz, ru, en)
│   ├── ingestion.py        # PDF/text parser & Chroma batch indexer
│   ├── rag.py              # LLM wrapper & RAG context retrieval
│   └── storage.py          # Persistent JSON storage managers
├── data/                   # JSON data store (generated on runtime)
└── requirements.txt        # Package requirements
```

---

## 🎮 Demo Walkthrough

1.  **Start and Language Choice**: Send `/start` to the bot. Click `🇺🇿 O'zbekcha` to run in the primary language.
2.  **Profile Setup**: Follow the registration prompts (Name, University, Faculty, Year, and Target Role).
3.  **Skill Passport**: Click `📋 Skill Passport` from the reply menu. Provide your tech stack, projects, and work experience. The bot returns a professional gap analysis and study roadmap.
4.  **ATS Resume Builder**: Click `📝 Rezyume yaratish`. Enter your target job position and job description/experience. The bot replies with a copy-pasteable ATS-compatible markdown resume.
5.  **Interview Simulator**: Click `🎤 Intervyu mashqi`. Choose `💻 Texnik savollar`. Answer the generated question. The bot evaluates your response using the STAR method, gives suggestions, and rates it out of 10. Click `➡️ Keyingi savol` to continue, or `🏁 Yakunlash` to finish.
6.  **Vacancy Matchmaking**: Click `💼 Vakansiyalar`. The bot compares your profile skills against partner listings and lists matches with match percentages and application links.
7.  **Admin Portal**: (If your Telegram ID is in `ADMIN_IDS`): Send `/admin` or `/stats` to receive the live dashboard report. Use `/broadcast Hello students!` to send announcements to everyone.
