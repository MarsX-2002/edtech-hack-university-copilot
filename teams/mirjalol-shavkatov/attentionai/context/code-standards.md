# Code Standards

## General

- Keep modules small and single-purpose.
- Prefer boring, reliable code over clever abstractions.
- Optimize for hackathon demo reliability.
- Do not introduce unnecessary frameworks.
- Fix root causes; do not layer hacks unless marked as demo fallback.
- Use clear names: `course_id`, `student_id`, `document_id`, `risk_level`.

## Python

- Use Python 3.11+.
- Use type hints for public functions.
- Keep functions short and testable.
- Validate external inputs before using them.
- Handle missing files, empty uploads, empty retrieval, and API failures gracefully.
- Avoid global mutable state except Streamlit session state.

## Streamlit

- Keep UI composition in `app.py`.
- Put business logic in `src/` modules.
- Use Streamlit forms for upload/create actions.
- Use session state only for UI state, not source-of-truth storage.
- Show clear success/error messages for demo reliability.

## AI/RAG

- Always retrieve before answering course questions.
- Include citations in answers.
- Log user question, mode, retrieved sources, and risk signals.
- Use deterministic-ish settings for demo: low temperature unless creativity is needed.
- Add fallback behavior when LLM or embedding API fails.

## Data and Storage

- Store metadata in JSON under `data/`.
- Store vector embeddings in `chroma_db/`.
- Store uploaded documents under `data/uploads/`.
- Do not commit real private uploads.
- Include only safe sample data.

## File Organization

- `app.py` — app shell and page routing.
- `src/config.py` — config and path constants.
- `src/storage.py` — JSON persistence.
- `src/ingestion.py` — parsing/chunking/indexing.
- `src/rag.py` — retrieval and answer generation.
- `src/modes.py` — mode-specific prompts and handlers.
- `src/risk.py` — risk scoring.
- `src/dashboard.py` — analytics aggregation.
- `sample_data/` — demo course materials.
- `context/` — planning docs for coding agent.

## README Requirements

README must include:

- Project description.
- Setup steps.
- Required env vars.
- Run command.
- Demo flow.
- AI models/tools used.
- Responsible AI limitations.
