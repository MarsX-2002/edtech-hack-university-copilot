## Career AI Assistant (Telegram Bot Pivot)

You are building the **Career AI Assistant** (formerly Attention AI), a multilingual Telegram bot MVP for university career centers.

### Bot Commands & Setup:
- Run the bot: `python bot.py`
- Command `/start` initiates registration / main menu in UZ, RU, or EN.
- Command `/admin` or `/stats` displays user analytics.
- Command `/broadcast <message>` sends an announcement to all registered users.

### Project Rules & Architecture:
- Stack: Python, python-telegram-bot, Chroma DB, RAG (via Gemini/OpenAI).
- User interface is entirely inside Telegram.
- All translations are stored in `src/i18n.py`.
- Persistent storage is managed via local JSON files in `data/` using `src/storage.py`.
- Career guidance knowledge base is parsed and indexed from `knowledge_base/` on startup.
