"""
Migration script: students.json → SQLite students table.
Run once on first startup if students table is empty and JSON exists.
Can also be run manually: python -m src.migrate_students
"""
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.config import DATA_DIR
from src.db import get_db_connection, init_db

logger = logging.getLogger(__name__)

STUDENTS_FILE = DATA_DIR / "students.json"


def migrate_students_json_to_db():
    """
    Migrate existing students.json to SQLite students table.
    - Backs up JSON first
    - Maps existing fields to new schema
    - Sets student_id=NULL, phone_number=NULL, lms_verification_status='pending'
    - Skips already-migrated telegram_ids
    """
    if not STUDENTS_FILE.exists():
        logger.info("No students.json found, skipping migration.")
        return 0

    # Check if we already have students in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM students;")
    existing_count = cursor.fetchone()["cnt"]

    if existing_count > 0:
        logger.info(f"Students table already has {existing_count} rows, skipping JSON migration.")
        conn.close()
        return 0

    # Load JSON
    try:
        with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
            students_json = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read students.json: {e}")
        conn.close()
        return 0

    if not students_json:
        logger.info("students.json is empty, skipping migration.")
        conn.close()
        return 0

    # Backup JSON
    backup_path = DATA_DIR / f"students_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy2(STUDENTS_FILE, backup_path)
    logger.info(f"Backed up students.json to {backup_path}")

    # Migrate each student
    migrated = 0
    skipped = 0

    for telegram_id_str, profile in students_json.items():
        # Check if already in DB
        cursor.execute(
            "SELECT id FROM students WHERE telegram_user_id = ?;",
            (telegram_id_str,)
        )
        if cursor.fetchone():
            skipped += 1
            continue

        try:
            cursor.execute(
                """INSERT INTO students
                   (telegram_user_id, telegram_username, telegram_full_name, name,
                    student_id, phone_number, university, faculty, year, target_role,
                    skills, readiness_score, language, lms_verification_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                (
                    telegram_id_str,
                    None,  # telegram_username not in old schema
                    None,  # telegram_full_name not in old schema
                    profile.get("name", "Unknown"),
                    None,  # student_id not in old schema — will prompt on next /start
                    None,  # phone_number not in old schema
                    profile.get("university", "PDP University"),
                    profile.get("faculty"),
                    profile.get("year"),
                    profile.get("target_role"),
                    profile.get("skills", ""),
                    profile.get("readiness_score"),
                    profile.get("language", "uz"),
                    "pending",  # lms_verification_status
                )
            )
            migrated += 1
        except Exception as e:
            logger.error(f"Failed to migrate student {telegram_id_str}: {e}")
            skipped += 1

    conn.commit()

    # Log migration event
    cursor.execute(
        """INSERT INTO audit_logs (actor_type, actor_id, action, details)
           VALUES ('system', 'migration', 'students_migrated', ?);""",
        (f"Migrated {migrated} students from JSON, skipped {skipped}",)
    )
    conn.commit()
    conn.close()

    logger.info(f"Migration complete: {migrated} migrated, {skipped} skipped")
    return migrated


def auto_migrate():
    """Run migration automatically if needed (call from app startup)."""
    try:
        migrate_students_json_to_db()
    except Exception as e:
        logger.error(f"Auto-migration failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    count = migrate_students_json_to_db()
    print(f"Migrated {count} students from JSON to SQLite.")
