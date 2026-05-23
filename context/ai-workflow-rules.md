# AI Workflow Rules

## Approach

Build Attention AI incrementally using a spec-driven workflow. Context files define product scope, architecture, UI, and coding rules. Implement one verifiable unit at a time. Do not invent features. Do not broaden scope. Prioritize a working hackathon demo.

## Scoping Rules

- Work on one feature unit at a time.
- Keep each change small and demo-verifiable.
- Do not combine unrelated concerns unless required for a working slice.
- Prefer local storage and simple UI over production infrastructure.
- Do not add full authentication, payments, career advising, LMS integrations, or multi-tenant admin.
- Do not replace the teacher; position the product as teacher support.

## When to Split Work

Split implementation if it combines:

- UI shell and AI/RAG logic.
- File ingestion and dashboard analytics.
- Multiple unrelated modes.
- Storage model changes and visual redesign.
- New dependency installation and feature implementation that can be separated.
- Behavior not clearly defined in the context files.

If a change cannot be verified quickly in the app, split it.

## Handling Missing Requirements

- Do not invent product behavior not defined in context files.
- If ambiguous, choose the simplest demo-safe interpretation and record it in `progress-tracker.md`.
- If the decision affects architecture or scope, update the relevant context file first.
- If blocked by API keys, add a mock/demo fallback instead of stopping.

## Protected Files

Do not modify unless explicitly instructed:

- `.env` or any secret files.
- `chroma_db/` generated vector database files.
- `data/uploads/` user-uploaded files.
- Third-party package internals.
- Official hackathon slide template files.

## Documentation Sync

Update docs when changes affect:

- Product scope.
- AI behavior or guardrails.
- Storage model.
- File/folder structure.
- Setup or run instructions.
- Demo flow.

Always update `context/progress-tracker.md` after meaningful implementation.

## Verification Before Next Unit

1. App runs locally.
2. Current unit works through the UI.
3. No architecture invariant was violated.
4. AI output has citations or safe escalation.
5. Empty/error states are handled.
6. `context/progress-tracker.md` is updated.
7. README stays accurate if setup changed.
