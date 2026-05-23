# Walkthrough — PDP University Career Center

**PDP University Career Center** is a production-grade white-labelable Career Center AI platform currently branded for **PDP University**. It provides a dual-sided experience:
1. **Student Side (Telegram Bot)**: Powered by a multi-lingual state machine for skill audits, ATS resume validation, STAR interview practice, and vacancy matchmaking.
2. **Admin Side (Vite + React Dashboard)**: High-contrast, projector-ready analytical panel with student skill directories, curriculum deficit analyzers, and detailed student dossiers.

---

## 🚀 Key Admin Dashboard Enhancements

We implemented the following features on the Admin Web interface:

### 1. Renaming & Branding
* Rebranded all occurrences and labels back to **PDP University Career Center** (PDP).
* Reconfigured UI colors to use PDP's brand colors: White and Green (light mode) / Dark and Green (dark mode).
* Refactored the backend API title, Streamlit `dashboard.py` metrics, and React sidebar layouts to use **PDP University Career Center** branding.

### 2. Premium Theme Toggle & UI Polish
* Added a custom **Segmented Switch Control** (segmented Sun / Moon pill buttons) to the sidebar footer.
* Resolved light theme background gradient issues in the main panel, ensuring the canvas is styled consistently with a soft light-gray (`#F9FAFB`) when switching.
* Refined card depth shadows (`--shadow-md`, `--shadow-lg`) and separated the table headers visually in light mode to ensure a high-contrast, professional, and readable layout.
* Toggling themes faints color variables smoothly using CSS-only transitions.
* Configurations are persisted in `localStorage`.

### 3. Safety Event Realignment
* Updated KPI Metric Cards and Telemetry logs, changing the labels from "Security Risks" to **Safety Flags** and "Risk Logs" to **Guardrail Events** to fit the educational/career context.

### 4. Readiness Score formatting
* Replaced embarrassing `0%` readiness scores with a friendly **"Profile Incomplete"** status in both the "Recent Active Talent" dashboard list and the main student directory grid.

### 5. Detailed Student Dossier Overhaul
When clicking **Explore Profile** or **Open Dossier**, the modal now displays a fully loaded view:
* **Interactive Action Buttons Panel**:
  * **💬 Message Student**: Direct deep link to Telegram chat.
  * **📥 Export Shortlist**: Instantly downloads a clean `.txt` dossier detailing student skills, target roles, quiz attempts, and interviews.
  * **📅 Schedule Mock Interview**: Dispatches simulation requests directly to the student.
  * **🎯 Generate Learning Plan**: Dynamically evaluates student gaps against required vacancies, presenting a structured learning roadmap.
* **Curriculum Deficit Gaps**: Compares student capabilities against active vacancies and highlights missing skills with Lucide `AlertTriangle` warning badges.
* **STAR Mock Interview attempts**: Displays mock interview logs showing scores, timestamps, and responses structured using the **Situation, Task, Action, and Result** methodology.
* **Recommended Vacancies**: Full-width, ranked match listing illustrating matched (verified/declared) and missing skills for active job opportunities.

---

## 🛠️ Verification & Verification Commands

### 1. Build Compilation
We verified that the React dashboard builds cleanly with Vite and has no TypeScript or syntax compiler issues:
```bash
cd dashboard && npm run build
```
**Output:**
```
vite v8.0.14 building client environment for production...
✓ 1738 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-CGyAvDNU.css   10.82 kB │ gzip:  2.70 kB
dist/assets/index-DCZg0U6I.js   252.70 kB │ gzip: 74.51 kB
✓ built in 233ms
```

### 2. Python Backend & Logic Checks
We ran our import and matchmaking check scripts to verify backend routes resolve interviews and compute matches correctly:
```bash
python test_imports.py
```
**Output:**
```
Starting import verification...
...
✅ Vacancy match test: Found 6 matches.
   Top Match: Junior Python Backend Developer at Uzum Tech (64% match)
✅ Skill assessment test (mock mode) passed!
🎉 All checks passed! The codebase is ready.
```

### 3. Student Registration & Resume Optimization Updates (May 2026)
We implemented and verified the following core registration and resume generation enhancements:

* **Student Registration Bypass Optimization**:
  * Updated the `/start` registration state machine (`src/bot_handlers.py`) in the `reg_student_id` handler.
  * For migrated students whose profiles already contain academic details (university, faculty, year, target role), submitting their unique 6-digit student ID now automatically bypasses the academic setup steps and takes them straight to the secure Telegram contact-sharing phone verification (`reg_phone`).
  * New students will continue to flow through the full multi-step university, faculty, year, and target role setup.

* **Contact & Skill Details Pre-filling in Resume Builder**:
  * Updated the ATS Resume Optimizer prompts and fallback structures (`src/career_modes.py` and `src/agent.py`) so that the student's name, verified skills, phone number, and Telegram username are directly injected into system instructions and final markdown resume outputs.
  * Suppressed the placement of generic placeholders for these details in the final output, ensuring that only outstanding contact fields (like Email, Address, and LinkedIn) are appended in the "Fields to fill" recommendation checklist.

* **E2E Integration & Verification Runs**:
  * **Profile Progression Tests (`test_profile_progression.py`)**: Validated student profile lifecycle modifications (including skill verification, interview completions, and string formatting helpers) and verified they execute cleanly.
  * **Agentic Harness Turn Loop Tests (`test_agent_harness.py`)**: Ran full mock interview multi-turn loops and SQLite DB persistence validations, confirming all systems operate nominally in fallback mode.
  * **Knowledge Base Ingestion (`verify_ingestion.py`)**: Successfully ingested and embedded 20 knowledge base document chunks into Chroma DB.

**Output from Profile Progression test:**
```
📋 Starting Student Profile Progression Tests...
  ✅ Setup test student profile for Telegram ID: 123456789
  ✅ Quiz Completion Progression: Verified skill badge appended successfully
  ✅ Interview Completion Progression: Readiness score updated successfully
  ✅ Profile Display Formatting: Verified badges and readiness scores rendered correctly
  ✅ Cleaned up test student profile
🎉 All Profile Progression Verification Tests Passed!
```

### 4. Developer Bypass Authentication (May 2026)
To enable testing the actual FastAPI backend sessions, JWT cookie issuance, rate limiting, and SQLite role-based routing without requiring live Google OAuth project registration or setting up credentials, we added a **Developer Bypass** feature:

* **Backend Support (`src/api.py`)**: The `/auth/google` endpoint now checks if the authorization code starts with the `mock_code_` prefix. If present, it bypasses Google's servers, extracts the target email, and directly executes user validation and token/session cookie issuance using the actual database allowlist.
* **Frontend UI Box (`dashboard/src/App.tsx`)**: Added a dashed bypass input form on the login screen. Developers can type any allowlisted email address (such as `mirjalol0331@gmail.com`) and click **Log In with Bypass Email** to authenticate and load their session.
* **SQLite Seeding behavior**: Changing `INITIAL_ADMIN_EMAIL` in `.env` only seeds a super-admin user if no other super-admin exists. Pre-existing database installations can add new admins like `mirjalol0331@gmail.com` using the CLI command:
  ```bash
  python manage.py add-staff --email mirjalol0331@gmail.com --name "Mirjalol" --role super_admin --department career
  ```

### 5. Multilingual Switcher & Labor Market Trends Widget (May 2026)
* **Uzbek/English Toggle Switch**: Added a dynamic language switcher component to both the React sidebar footer and login screen. Toggling language updates all admin navigation, card titles, table headers, descriptions, and dashboard buttons dynamically.
* **Labor Market Trends**: Integrated a visual bar chart widget in the Overview tab showing the top 5 trending tech skills requested in partner vacancies (e.g. Python, React, Docker, Linux, SQL), satisfying the "Mehnat Bozori Trendlari" requirement from [CAREER_ASSISTANT.md](file:///home/mikey/Desktop/buildathon-2026/teams/mirjalol-shavkatov/attentionai/CAREER_ASSISTANT.md).

