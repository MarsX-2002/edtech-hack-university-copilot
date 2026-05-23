# UI Context

## Theme

Attention AI should feel like a clean university operations dashboard: calm, trustworthy, fast to understand. Use light mode by default. Avoid flashy visuals. The demo must be readable from a projector.

## Colors

| Role | CSS Variable | Value |
|---|---|---|
| Page background | `--bg-base` | `#F8FAFC` |
| Surface | `--bg-surface` | `#FFFFFF` |
| Primary text | `--text-primary` | `#0F172A` |
| Muted text | `--text-muted` | `#64748B` |
| Primary accent | `--accent-primary` | `#2563EB` |
| Secondary accent | `--accent-secondary` | `#7C3AED` |
| Border | `--border-default` | `#E2E8F0` |
| Warning | `--state-warning` | `#F59E0B` |
| Error | `--state-error` | `#DC2626` |
| Success | `--state-success` | `#16A34A` |

## Typography

| Role | Font | Variable |
|---|---|---|
| UI text | System sans-serif | `--font-sans` |
| Code/mono | System monospace | `--font-mono` |

## Layout Patterns

- Sidebar: role selector, course selector, demo course button.
- Teacher page: course setup on top, dashboard below.
- Student page: mode selector on top, chat/response area center.
- Dashboard: metrics row, confused topics table, risk table, recent questions.
- Use cards/panels with clear headings.
- Avoid deep nesting and hidden interactions.

## Streamlit Component Rules

- Use `st.sidebar` for navigation and role/course controls.
- Use `st.tabs` for Teacher Setup, Student Assistant, Dashboard if useful.
- Use `st.file_uploader` for documents.
- Use `st.chat_input` or text areas for student questions.
- Use `st.dataframe` or `st.table` for dashboard data.
- Use `st.warning`, `st.error`, `st.success`, and `st.info` for clear states.

## UX Rules

- Every AI answer should show sources or an escalation message.
- Every long-running action should show a spinner.
- Demo course must be loadable with one click.
- Empty states must explain what to do next.
- Never make the user guess whether ingestion or AI response worked.
