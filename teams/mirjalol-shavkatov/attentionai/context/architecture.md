# Architecture Context

## Stack

| Layer | Technology | Role |
|---|---|---|
| Platform UI | Telegram Bot | Interactive user interface for students and admins |
| Language | Python 3.11+ | Main implementation language |
| AI Orchestration | Direct provider SDK calls | High performance, lightweight integration |
| LLM | OpenAI or Gemini via env var | Generate skill analysis, resumes, STAR interview mock, career advice |
| Embeddings | Provider embedding model | Embed knowledge base chunks for retrieval |
| Vector DB | Chroma | Local vector search for career documents |
| Storage | Local JSON + Chroma persistence | Store profiles, assessments, interview logs, vacancies, admin analytics |

## System Boundaries

- `bot.py` — Telegram bot polling and handler registrations.
- `src/config.py` — environment variables, constants, paths.
- `src/storage.py` — student profiles, skill passports, interview logs, vacancies, JSON persistence.
- `src/i18n.py` — multilingual dictionary.
- `src/ingestion.py` — text parsing, chunking, embedding, Chroma writes for knowledge base.
- `src/rag.py` — retrieval and grounded career advice generation.
- `src/career_modes.py` — skill assessment, resume building, interview practice, vacancy matchmaking.
- `src/analytics.py` — admin analytics compiling.
- `data/` — local persisted JSON files.
- `chroma_db/` — local Chroma vector database.
- `knowledge_base/` — core career guides and templates.

## Storage Model

- **JSON files**: students, skill assessments, interview sessions, resumes, vacancies, analytics events.
- **Chroma**: embedded career guide chunks and metadata.
- **Environment variables**: API keys and admin Telegram IDs.

## Invariants

1. All prompts ground the AI as a professional career mentor.
2. The UI is completely localized in UZ (primary), RU, and EN.
3. The bot automatically handles markdown formatting safely for Telegram.
4. Fallback/Mock mode executes local heuristic analysis if APIs fail or keys are absent.
