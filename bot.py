"""
Main entry point for the Career AI Assistant Telegram Bot.
"""
import sys
import logging
import os
import psutil
from src.config import TELEGRAM_BOT_TOKEN, DEFAULT_PROVIDER, BASE_DIR
from telegram.error import TimedOut, NetworkError, Conflict
from src.ingestion import ingest_knowledge_base
from src.db import init_db
from src.bot_handlers import (
    start_command, admin_command, broadcast_command, consent_command,
    handle_callback_query, handle_message, handle_contact, handle_document
)
# Guard against multiple bot instances
LOCK_FILE = BASE_DIR / "bot.lock"
# ... [rest remains the same but imports are updated] ...

def another_instance_running() -> bool:
    """Check for existing bot instance via lock file and running process.
    If a stale lock or active process is found, attempt to terminate it and clean up.
    Returns False to indicate safe to start new instance.
    """
    # Handle lock file
    if LOCK_FILE.exists():
        try:
            existing_pid = int(LOCK_FILE.read_text().strip())
        except Exception:
            LOCK_FILE.unlink(missing_ok=True)
            existing_pid = None
        if existing_pid:
            if psutil.pid_exists(existing_pid):
                try:
                    proc = psutil.Process(existing_pid)
                    proc.kill()
                    logging.getLogger(__name__).info("Killed existing bot process with PID %s", existing_pid)
                except Exception as e:
                    logging.getLogger(__name__).warning("Failed to kill existing bot process %s: %s", existing_pid, e)
                # Remove lock after attempting termination
                LOCK_FILE.unlink(missing_ok=True)
            else:
                # Stale lock, remove it
                LOCK_FILE.unlink(missing_ok=True)
    # Also check for any other bot.py processes (excluding current)
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and proc.info['cmdline'] and 'bot.py' in ' '.join(proc.info['cmdline']):
                try:
                    proc.kill()
                    logging.getLogger(__name__).info("Killed stray bot process with PID %s", proc.info['pid'])
                except Exception as e:
                    logging.getLogger(__name__).warning("Failed to kill stray bot process %s: %s", proc.info['pid'], e)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # After cleanup, indicate safe to start
    return False

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import asyncio
from telegram import Update


# Global error handler for Telegram API timeouts and network issues
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and optionally notify user. Auto-retries on TimedOut."""
    logger.error(f"Update {update} caused error {context.error}")
    if isinstance(context.error, TimedOut):
        logger.warning("Telegram request timed out. Retrying after short delay.")
        # Simple retry: wait a moment then re-process the same update
        await asyncio.sleep(2)
        try:
            await context.application.process_update(update)
        except Exception as e:
            logger.error(f"Retry failed: {e}")
    elif isinstance(context.error, NetworkError):
        logger.warning("Network error occurred. Check connectivity.")


# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    # Prevent multiple bot instances (extra safety)
    # Check for existing bot instance (now handled by lock file and cleanup)
    if another_instance_running():
        logger.info("Detected another bot instance, proceeding with cleanup and lock handling.")
    # Write lock file with current PID
    try:
        LOCK_FILE.write_text(str(os.getpid()))
    except Exception as e:
        logger.error(f"Failed to write lock file: {e}")
        # Continue without lock if cannot write

    # Ensure no other bot processes are left running
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] != os.getpid() and proc.info['cmdline'] and 'bot.py' in ' '.join(proc.info['cmdline']):
                logger.info("Terminating stray bot process %s", proc.info['pid'])
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment or .env file.")
        print("\n❌ Error: TELEGRAM_BOT_TOKEN is not set in environment or .env file.")
        print("Please check your .env file and try again.\n")
        sys.exit(1)
    print(f"🤖 Starting Career AI Assistant Bot (Active Provider: {DEFAULT_PROVIDER})...")
    
    # Initialize SQLite Database
    try:
        init_db()
        logger.info("SQLite database initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize SQLite database: {e}")
        sys.exit(1)
        
    # Ingest knowledge base on startup to ensure RAG works
    print("📚 Ingesting knowledge base files into Chroma/cache...")
    try:
        ingest_knowledge_base()
    except Exception as e:
        logger.error(f"Failed to ingest knowledge base: {e}")

    # Build the Application with increased timeouts
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .connect_timeout(15.0)   # increase connect timeout
        .read_timeout(20.0)      # increase read timeout
        .build()
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", admin_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("consent", consent_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register global error handler
    app.add_error_handler(error_handler)

    # Run the bot (Webhook or Polling mode based on configuration)
    webhook_url = os.getenv("WEBHOOK_URL")
    port = int(os.getenv("PORT", "8443"))
    
    try:
        if webhook_url:
            logger.info(f"🌐 Starting bot in Webhook mode: {webhook_url} on port {port}")
            app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TELEGRAM_BOT_TOKEN,
                webhook_url=f"{webhook_url}/{TELEGRAM_BOT_TOKEN}",
                drop_pending_updates=True
            )
        else:
            logger.info("🤖 Starting bot in Polling mode...")
            app.run_polling(drop_pending_updates=True)
    except Conflict as ce:
        logger.error(f"Telegram Conflict error (likely another bot instance): {ce}")
        logger.info("Exiting due to Conflict.")
        sys.exit(1)
    except TimedOut as te:
        logger.error(f"Timed out: {te}")
        logger.info("Bot exiting due to timeout.")
        sys.exit(1)
    except NetworkError as ne:
        logger.error(f"Network error: {ne}")
        logger.info("Bot exiting due to network issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
