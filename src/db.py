"""
SQLite database and tables management for the Career AI Assistant stateful harness.
"""
import sqlite3
from datetime import datetime
from src.config import DATA_DIR

DB_FILE = DATA_DIR / "career_assistant.db"

def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database schemas for stateful agent logging and tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Conversations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT NOT NULL,
        type TEXT NOT NULL, -- 'interview', 'resume_builder', 'quiz', 'advice', 'skills'
        status TEXT NOT NULL, -- 'active', 'completed', 'cancelled'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        sender TEXT NOT NULL, -- 'user', 'agent'
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        latency_ms INTEGER,
        input_tokens INTEGER,
        output_tokens INTEGER,
        validation_attempts INTEGER DEFAULT 0,
        guardrail_status TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    );
    """)

    # Check if we need to add columns to messages (migration safety)
    try:
        cursor.execute("PRAGMA table_info(messages);")
        columns = [row["name"] for row in cursor.fetchall()]
        
        new_cols = {
            "latency_ms": "INTEGER",
            "input_tokens": "INTEGER",
            "output_tokens": "INTEGER",
            "validation_attempts": "INTEGER DEFAULT 0",
            "guardrail_status": "TEXT"
        }
        
        for col_name, col_type in new_cols.items():
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type};")
    except Exception as e:
        # If any issue occurs with table_info/alter table, ignore and proceed
        pass

    # 3. Tool Calls Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tool_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER NOT NULL,
        tool_name TEXT NOT NULL,
        arguments TEXT NOT NULL, -- JSON string
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
    );
    """)

    # 4. Tool Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tool_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_call_id INTEGER NOT NULL,
        result_content TEXT NOT NULL, -- JSON string / raw output
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tool_call_id) REFERENCES tool_calls(id) ON DELETE CASCADE
    );
    """)

    # 5. Risk Events Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT NOT NULL,
        category TEXT NOT NULL, -- 'hallucination', 'fallback_triggered', 'api_failure', 'anomaly', 'unauthorized'
        description TEXT NOT NULL,
        severity TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Quiz Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        details TEXT NOT NULL, -- JSON string of quiz questions & answers
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Homework Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS homework_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT NOT NULL,
        task_title TEXT NOT NULL,
        score INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ──────────────── AUTH TABLES ────────────────

    # 8. Students Table (replaces students.json)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_user_id TEXT UNIQUE NOT NULL,
        telegram_username TEXT,
        telegram_full_name TEXT,
        student_id TEXT UNIQUE,
        phone_number TEXT UNIQUE,
        name TEXT NOT NULL,
        university TEXT DEFAULT 'PDP University',
        faculty TEXT,
        year TEXT,
        target_role TEXT,
        skills TEXT DEFAULT '',
        readiness_score REAL,
        language TEXT DEFAULT 'uz',
        lms_verification_status TEXT DEFAULT 'pending',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. Staff Users (allowlist-based, no public signup)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT NOT NULL,
        google_sub TEXT UNIQUE,
        phone_number TEXT UNIQUE,
        telegram_user_id TEXT UNIQUE,
        avatar_url TEXT,
        role TEXT NOT NULL DEFAULT 'viewer',
        department TEXT NOT NULL DEFAULT 'career',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        password_hash TEXT,
        must_change_password INTEGER DEFAULT 1
    );
    """)

    # 10. Refresh Tokens (for JWT rotation + revocation)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_user_id INTEGER NOT NULL,
        token_hash TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        revoked INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (staff_user_id) REFERENCES staff_users(id) ON DELETE CASCADE
    );
    """)

    # 11. Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_type TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        action TEXT NOT NULL,
        target_type TEXT,
        target_id TEXT,
        details TEXT,
        ip_address TEXT,
        user_agent TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_phone ON students(phone_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_email ON staff_users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_staff_google_sub ON staff_users(google_sub);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_token_hash ON refresh_tokens(token_hash);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_logs(actor_type, actor_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);")

    # Migration: Add password_hash and must_change_password columns if they don't exist
    try:
        cursor.execute("ALTER TABLE staff_users ADD COLUMN password_hash TEXT;")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE staff_users ADD COLUMN must_change_password INTEGER DEFAULT 1;")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()

    # ── Bootstrap initial admin from env ──
    _bootstrap_initial_admin(conn)

    conn.close()

    # ── Auto-migrate legacy students JSON to SQLite ──
    from src.migrate_students import auto_migrate
    auto_migrate()


def _bootstrap_initial_admin(conn):
    """Seeds the first super_admin from INITIAL_ADMIN_EMAIL env if no super_admin exists."""
    from src.config import INITIAL_ADMIN_EMAIL, ADMIN_PASSWORD
    if not INITIAL_ADMIN_EMAIL:
        return

    cursor = conn.cursor()
    from src.auth import hash_password
    pwd_hash = hash_password(ADMIN_PASSWORD)

    # Check if this email already exists
    cursor.execute("SELECT id, password_hash FROM staff_users WHERE email = ?;", (INITIAL_ADMIN_EMAIL,))
    row = cursor.fetchone()
    
    if row:
        # If exists but password_hash is not set, update it
        if not row["password_hash"]:
            cursor.execute(
                "UPDATE staff_users SET password_hash = ?, must_change_password = 0 WHERE id = ?;",
                (pwd_hash, row["id"])
            )
            conn.commit()
            cursor.execute(
                """INSERT INTO audit_logs (actor_type, actor_id, action, details)
                   VALUES ('system', 'bootstrap', 'admin_password_updated', ?);""",
                (f"Updated initial super_admin password hash: {INITIAL_ADMIN_EMAIL}",)
            )
            conn.commit()
        return

    # Check if any super_admin exists at all
    cursor.execute("SELECT COUNT(*) as cnt FROM staff_users WHERE role = 'super_admin';")
    if cursor.fetchone()["cnt"] > 0:
        return  # Already have a super_admin, never overwrite

    cursor.execute(
        """INSERT INTO staff_users (email, name, role, department, is_active, password_hash, must_change_password)
           VALUES (?, ?, 'super_admin', 'career', 1, ?, 0);""",
        (INITIAL_ADMIN_EMAIL, "Initial Admin", pwd_hash)
    )
    conn.commit()

    # Log the bootstrap event
    cursor.execute(
        """INSERT INTO audit_logs (actor_type, actor_id, action, details)
           VALUES ('system', 'bootstrap', 'admin_seeded', ?);""",
        (f"Seeded initial super_admin: {INITIAL_ADMIN_EMAIL}",)
    )
    conn.commit()
    import logging
    logging.getLogger(__name__).info(f"Bootstrapped initial super_admin: {INITIAL_ADMIN_EMAIL}")

# --- DB Access Helpers ---

def create_conversation(telegram_id: int, conv_type: str) -> int:
    """Creates a new active conversation and returns the ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (telegram_id, type, status) VALUES (?, ?, ?);",
        (str(telegram_id), conv_type, "active")
    )
    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conv_id

def get_active_conversation(telegram_id: int, conv_type: str) -> int | None:
    """Returns active conversation ID for a user and type, if exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM conversations WHERE telegram_id = ? AND type = ? AND status = 'active' ORDER BY id DESC LIMIT 1;",
        (str(telegram_id), conv_type)
    )
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else None

def complete_conversation(conversation_id: int):
    """Marks a conversation as completed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET status = 'completed' WHERE id = ?;",
        (conversation_id,)
    )
    conn.commit()
    conn.close()

def add_message(conversation_id: int, sender: str, content: str) -> int:
    """Inserts a new message and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?);",
        (conversation_id, sender, content)
    )
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def add_tool_call(message_id: int, tool_name: str, arguments: str) -> int:
    """Inserts a new tool call and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tool_calls (message_id, tool_name, arguments) VALUES (?, ?, ?);",
        (message_id, tool_name, arguments)
    )
    tc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tc_id

def add_tool_result(tool_call_id: int, result_content: str) -> int:
    """Inserts a tool execution outcome."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tool_results (tool_call_id, result_content) VALUES (?, ?);",
        (tool_call_id, result_content)
    )
    tr_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tr_id

def log_risk(telegram_id: int, category: str, description: str, severity: str = "medium"):
    """Logs security, hallucination, or error events."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO risk_events (telegram_id, category, description, severity) VALUES (?, ?, ?, ?);",
        (str(telegram_id), category, description, severity)
    )
    conn.commit()
    conn.close()

def log_quiz_attempt(telegram_id: int, topic: str, score: int, total_questions: int, details: str):
    """Saves a student quiz attempt with detailed QA history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quiz_attempts (telegram_id, topic, score, total_questions, details) VALUES (?, ?, ?, ?, ?);",
        (str(telegram_id), topic, score, total_questions, details)
    )
    conn.commit()
    conn.close()

def log_homework_feedback(telegram_id: int, task_title: str, score: int, feedback_text: str):
    """Saves student homework or assignment grading."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO homework_feedback (telegram_id, task_title, score, feedback_text) VALUES (?, ?, ?, ?);",
        (str(telegram_id), task_title, score, feedback_text)
    )
    conn.commit()
    conn.close()

def get_conversation_history(conversation_id: int) -> list[dict]:
    """Retrieves full conversation messages in chronological order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sender, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id ASC;",
        (conversation_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["sender"], "content": r["content"], "timestamp": r["timestamp"]} for r in rows]

def update_message_telemetry(message_id: int, content: str = None, latency_ms: int = None, 
                             input_tokens: int = None, output_tokens: int = None, 
                             validation_attempts: int = None, guardrail_status: str = None):
    """Updates message content and telemetry fields."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if latency_ms is not None:
        updates.append("latency_ms = ?")
        params.append(latency_ms)
    if input_tokens is not None:
        updates.append("input_tokens = ?")
        params.append(input_tokens)
    if output_tokens is not None:
        updates.append("output_tokens = ?")
        params.append(output_tokens)
    if validation_attempts is not None:
        updates.append("validation_attempts = ?")
        params.append(validation_attempts)
    if guardrail_status is not None:
        updates.append("guardrail_status = ?")
        params.append(guardrail_status)
        
    if updates:
        params.append(message_id)
        query = f"UPDATE messages SET {', '.join(updates)} WHERE id = ?;"
        cursor.execute(query, tuple(params))
        conn.commit()
    conn.close()

