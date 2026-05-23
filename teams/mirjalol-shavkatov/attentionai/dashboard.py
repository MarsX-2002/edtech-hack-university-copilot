import os
import sqlite3
import streamlit as st
from datetime import datetime
import json
from pathlib import Path

# Set Streamlit Page configuration for premium design
st.set_page_config(
    page_title="PDP University Career Center - Telemetry Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "career_assistant.db"
STUDENTS_FILE = BASE_DIR / "data" / "students.json"

# Load config to get ADMIN_PASSWORD
import sys
sys.path.append(str(BASE_DIR))
from src.config import ADMIN_PASSWORD, GEMINI_API_KEY, OPENAI_API_KEY, DEFAULT_PROVIDER

# Custom Premium CSS Styling for wow factor
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38BDF8;
        margin-bottom: 5px;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        text-align: left;
    }
    .subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 30px;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == ADMIN_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.markdown("<h2 style='text-align: center;'>🔒 Admin Authentication</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "Enter Admin Password", type="password", on_change=password_entered, key="password"
            )
        return False
    elif not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "Enter Admin Password", type="password", on_change=password_entered, key="password"
            )
            st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

def get_db_connection():
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def load_students_json():
    if not STUDENTS_FILE.exists():
        return {}
    try:
        with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

if check_password():
    # Load data from SQLite and JSON
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    
    if "conversations" not in tables or "messages" not in tables:
        st.warning("⚠️ Telemetry Database is not initialized yet. Run some interactions in the bot first!")
        st.stop()
        
    students = load_students_json()
    
    # ─── SIDEBAR ───
    with st.sidebar:
        st.markdown("### ⚙️ System Status")
        st.info(f"**Default Provider:** {DEFAULT_PROVIDER.upper()}")
        st.success(f"**Gemini API Key:** {'Configured ✅' if GEMINI_API_KEY else 'Missing ❌'}")
        st.success(f"**OpenAI API Key:** {'Configured ✅' if OPENAI_API_KEY else 'Missing ❌'}")
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state["password_correct"] = False
            st.experimental_rerun()
            
    # ─── HEADER ───
    st.markdown("<h1 class='main-title'>📊 Stateful Agent Harness Telemetry</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Real-time dashboard tracking agent latency, token consumption, self-corrections, and guardrail hits.</p>", unsafe_allow_html=True)
    
    # ─── QUERY METRICS ───
    # 1. Total Sessions
    cursor.execute("SELECT COUNT(*) as total FROM conversations;")
    total_sessions = cursor.fetchone()["total"]
    
    # 2. Total messages & turns
    cursor.execute("SELECT COUNT(*) as total FROM messages;")
    total_messages = cursor.fetchone()["total"]
    
    cursor.execute("""
        SELECT 
            AVG(latency_ms) as avg_latency,
            SUM(input_tokens) as total_in,
            SUM(output_tokens) as total_out,
            SUM(validation_attempts) as total_val_attempts
        FROM messages 
        WHERE sender = 'agent' AND latency_ms IS NOT NULL;
    """)
    telemetry = cursor.fetchone()
    avg_latency = (telemetry["avg_latency"] or 0.0) / 1000.0  # in seconds
    total_in_tokens = telemetry["total_in"] or 0
    total_out_tokens = telemetry["total_out"] or 0
    total_val_attempts = telemetry["total_val_attempts"] or 0
    
    # ─── KPI CARDS ───
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(students)}</div>
            <div class="metric-title">Registered Students</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_sessions}</div>
            <div class="metric-title">Total Agent Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_latency:.2f}s</div>
            <div class="metric-title">Average Latency</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_in_tokens + total_out_tokens:,}</div>
            <div class="metric-title">Total Tokens Exchanged</div>
        </div>
        """, unsafe_allow_html=True)
        
    # ─── TELEMETRY VISUALIZATIONS ───
    st.markdown("### 📈 Performance & Consumption")
    
    # Query data for latency over time
    cursor.execute("""
        SELECT id, latency_ms/1000.0 as latency_sec, timestamp 
        FROM messages 
        WHERE sender = 'agent' AND latency_ms IS NOT NULL 
        ORDER BY id ASC 
        LIMIT 100;
    """)
    latency_data = cursor.fetchall()
    
    if latency_data:
        latencies = [row["latency_sec"] for row in latency_data]
        ids = [row["id"] for row in latency_data]
        
        col_plot1, col_plot2 = st.columns(2)
        with col_plot1:
            st.markdown("**Agent Turn Kechikishi (Latency Trend in Seconds)**")
            st.line_chart(latencies)
            
        # Query tokens data
        cursor.execute("""
            SELECT id, input_tokens, output_tokens 
            FROM messages 
            WHERE sender = 'agent' AND input_tokens IS NOT NULL 
            ORDER BY id ASC 
            LIMIT 100;
        """)
        token_data = cursor.fetchall()
        if token_data:
            tokens_in = [row["input_tokens"] for row in token_data]
            tokens_out = [row["output_tokens"] for row in token_data]
            with col_plot2:
                st.markdown("**Token Consumption (Prompt vs Completion)**")
                st.area_chart(dict(
                    Prompt=tokens_in,
                    Completion=tokens_out
                ))
    else:
        st.info("💡 Not enough telemetry logs to display charts. Generate some activity in the bot!")
        
    # ─── HARNESS & GUARDRAIL AUDITS ───
    st.markdown("### 🛡️ Safety Guardrails & Self-Correction Analytics")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("**Guardrail Status Outcomes**")
        cursor.execute("""
            SELECT guardrail_status, COUNT(*) as cnt 
            FROM messages 
            WHERE guardrail_status IS NOT NULL 
            GROUP BY guardrail_status;
        """)
        guardrail_stats = cursor.fetchall()
        if guardrail_stats:
            g_labels = [row["guardrail_status"] for row in guardrail_stats]
            g_counts = [row["cnt"] for row in guardrail_stats]
            st.bar_chart(dict(zip(g_labels, g_counts)))
        else:
            st.info("No guardrail events recorded.")
            
    with col_g2:
        st.markdown("**Self-Correction Retry Distribution**")
        cursor.execute("""
            SELECT validation_attempts, COUNT(*) as cnt 
            FROM messages 
            WHERE sender = 'agent' AND validation_attempts IS NOT NULL 
            GROUP BY validation_attempts;
        """)
        validation_stats = cursor.fetchall()
        if validation_stats:
            v_labels = [f"Retries: {row['validation_attempts']}" for row in validation_stats]
            v_counts = [row["cnt"] for row in validation_stats]
            st.bar_chart(dict(zip(v_labels, v_counts)))
        else:
            st.info("No validation events recorded.")

    # ─── RISK EVENTS LOGS ───
    st.markdown("### 🚨 Recent Model & Security Risk Events")
    cursor.execute("""
        SELECT id, category, description, severity, timestamp 
        FROM risk_events 
        ORDER BY id DESC 
        LIMIT 10;
    """)
    risks = cursor.fetchall()
    if risks:
        risk_list = []
        for r in risks:
            risk_list.append({
                "ID": r["id"],
                "Category": r["category"].upper(),
                "Description": r["description"],
                "Severity": r["severity"].upper(),
                "Timestamp": r["timestamp"]
            })
        st.table(risk_list)
    else:
        st.success("🎉 No security anomalies or model hallucinations detected!")

    # ─── REGISTERED STUDENTS PROGRESSION ───
    st.markdown("### 👤 Student Profiles & Target Role Readiness")
    if students:
        student_list = []
        for sid, s in students.items():
            raw_skills = s.get("skills", "")
            verified_skills = [skill.replace(" (Verified)", "").strip() for skill in raw_skills.split(",") if "(Verified)" in skill]
            readiness = s.get("readiness_score")
            readiness_str = f"{readiness}/10" if readiness is not None else "N/A"
            
            student_list.append({
                "Telegram ID": sid,
                "Name": s.get("name"),
                "University": s.get("university"),
                "Faculty": s.get("faculty"),
                "Year": s.get("year"),
                "Target Role": s.get("target_role"),
                "Verified Skills": ", ".join(verified_skills) if verified_skills else "None",
                "Readiness Score": readiness_str
            })
        st.dataframe(student_list)
    else:
        st.info("No students registered yet.")

    conn.close()
