"""
Admin analytics and reporting for Career AI Assistant.
Generates premium reports on bot usage, active students, agent tool executions, and model risk events.
"""
from datetime import datetime
import re
from src.storage import load_students
from src.db import get_db_connection


def get_analytics_report(language: str = "uz") -> str:
    """Generates a comprehensive SQLite database-driven analytics report for admin users.
    Tracks user registration, stateful agent loops, tool usage, quiz scores, and system risk events.
    """
    students = load_students()
    total_users = len(students)

    # 1. Group students by target role
    roles = {}
    for std in students.values():
        role = std.get("target_role", "Not specified")
        roles[role] = roles.get(role, 0) + 1
    roles_str = "\n".join([f"• {role}: {count}" for role, count in roles.items()])

    # 2. SQLite relational statistics
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total stateful sessions
    cursor.execute("SELECT COUNT(*) as total FROM conversations;")
    total_sessions = cursor.fetchone()["total"]

    # Active vs Completed conversations
    cursor.execute("SELECT status, COUNT(*) as cnt FROM conversations GROUP BY status;")
    status_counts = {row["status"]: row["cnt"] for row in cursor.fetchall()}
    active_convs = status_counts.get("active", 0)
    completed_convs = status_counts.get("completed", 0)

    # Session counts by type
    cursor.execute("SELECT type, COUNT(*) as cnt FROM conversations GROUP BY type;")
    type_counts = {row["type"]: row["cnt"] for row in cursor.fetchall()}
    sp_count = type_counts.get("skills", 0)
    rb_count = type_counts.get("resume_builder", 0)
    ip_count = type_counts.get("interview", 0)
    vc_count = type_counts.get("vacancies", 0)
    ca_count = type_counts.get("advice", 0)
    qz_count = type_counts.get("quiz", 0)

    # Total messages exchanged
    cursor.execute("SELECT COUNT(*) as total FROM messages;")
    total_messages = cursor.fetchone()["total"]

    # Total native tool execution calls
    cursor.execute("SELECT COUNT(*) as total FROM tool_calls;")
    total_tool_calls = cursor.fetchone()["total"]

    # Breakdown of tool usage
    cursor.execute("SELECT tool_name, COUNT(*) as cnt FROM tool_calls GROUP BY tool_name;")
    tool_counts = {row["tool_name"]: row["cnt"] for row in cursor.fetchall()}
    tool_breakdown = "\n".join([f"  ▫️ {tname}: {cnt} calls" for tname, cnt in tool_counts.items()])

    # Average score in quiz attempts
    cursor.execute("SELECT COUNT(*) as cnt, AVG(score) as avg_s FROM quiz_attempts;")
    quiz_row = cursor.fetchone()
    quiz_attempts_cnt = quiz_row["cnt"]
    avg_quiz_score = quiz_row["avg_s"] if quiz_row["avg_s"] is not None else 0.0

    # Risk and security events profile
    cursor.execute("SELECT severity, COUNT(*) as cnt FROM risk_events GROUP BY severity;")
    risk_severities = {row["severity"]: row["cnt"] for row in cursor.fetchall()}
    low_risks = risk_severities.get("low", 0)
    medium_risks = risk_severities.get("medium", 0)
    high_risks = risk_severities.get("high", 0)
    critical_risks = risk_severities.get("critical", 0)
    total_risks = sum(risk_severities.values())

    # Get sample critical risk descriptions
    cursor.execute("SELECT category, description FROM risk_events ORDER BY id DESC LIMIT 3;")
    latest_risks = cursor.fetchall()
    latest_risks_str = "\n".join([f"  🚨 [{row['category'].upper()}] {row['description'][:60]}..." for row in latest_risks])

    # Fetch average mock interview score from completed interview conversations
    # (By checking the last message in completed interview conversations that mentions X/10 score)
    cursor.execute("""
        SELECT m.content 
        FROM messages m 
        JOIN conversations c ON m.conversation_id = c.id 
        WHERE c.type = 'interview' AND m.sender = 'agent' AND m.content LIKE '%/10%';
    """)
    interview_scores = []
    for row in cursor.fetchall():
        for line in row["content"].split("\n"):
            if "ball" in line.lower() or "score" in line.lower() or "оценка" in line.lower():
                match = re.search(r'(\d+)\s*/\s*10', line.lower())
                if match:
                    interview_scores.append(int(match.group(1)))
                    break
    avg_interview_score = sum(interview_scores) / len(interview_scores) if interview_scores else 0.0

    # 3. Model Telemetry & Performance
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN sender = 'agent' AND latency_ms IS NOT NULL THEN 1 END) as agent_turns,
            AVG(latency_ms) as avg_latency,
            SUM(input_tokens) as total_input_tokens,
            SUM(output_tokens) as total_output_tokens,
            SUM(validation_attempts) as total_validation_attempts
        FROM messages;
    """)
    telemetry_row = cursor.fetchone()
    agent_turns = telemetry_row["agent_turns"] or 0
    avg_latency = (telemetry_row["avg_latency"] or 0.0) / 1000.0  # in seconds
    total_in_tokens = telemetry_row["total_input_tokens"] or 0
    total_out_tokens = telemetry_row["total_output_tokens"] or 0
    total_val_attempts = telemetry_row["total_validation_attempts"] or 0

    cursor.execute("""
        SELECT guardrail_status, COUNT(*) as cnt 
        FROM messages 
        WHERE guardrail_status IS NOT NULL AND guardrail_status != 'passed'
        GROUP BY guardrail_status;
    """)
    guardrail_counts = {row["guardrail_status"]: row["cnt"] for row in cursor.fetchall()}
    failed_inputs = guardrail_counts.get("failed_input", 0)
    failed_outputs = guardrail_counts.get("failed_output", 0)

    conn.close()

    if language == "ru":
        report = (
            f"📊 *ОТЧЕТ ПО АНАЛИТИКЕ HARNESS*\n"
            f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"👥 *Пользователи:*\n"
            f"• Всего зарегистрировано студентов: {total_users}\n\n"
            f"⚙️ *Статистика Агента (SQLite Harness):*\n"
            f"• Всего сессий: {total_sessions} ({completed_convs} завершено, {active_convs} активно)\n"
            f"• Всего отправлено сообщений: {total_messages}\n"
            f"• Вызовов инструментов (Tool Calls): {total_tool_calls}\n"
            f"{tool_breakdown if tool_breakdown else '  ▫️ Инструменты не вызывались'}\n\n"
            f"📈 *Активность по модулям:*\n"
            f"• Оценка навыков (Skill Passport): {sp_count}\n"
            f"• Оптимизатор резюме (Resume Builder): {rb_count}\n"
            f"• Практика интервью (Interview Practice): {ip_count}\n"
            f"• Поиск вакансий (Vacancies): {vc_count}\n"
            f"• Карьерный совет (Career Advice): {ca_count}\n"
            f"• Викторина и ДЗ (Quiz & Homework): {qz_count}\n\n"
            f"🎤 *Качество симуляций интервью:*\n"
            f"• Проанализировано сессий: {len(interview_scores)}\n"
            f"• Средний балл STAR: {avg_interview_score:.1f}/10\n"
            f"• Попыток пройти квиз: {quiz_attempts_cnt} (Средняя оценка: {avg_quiz_score:.1f}/3)\n\n"
            f"🛡 *Профиль безопасности и рисков (LLM Guard):*\n"
            f"• Всего зафиксировано инцидентов: {total_risks} (Крит: {critical_risks}, Выс: {high_risks}, Ср: {medium_risks})\n"
            f"{latest_risks_str if latest_risks_str else '  🚨 Нет зафиксированных рисков'}\n\n"
            f"⚡ *Телеметрия и Производительность Модели (Model Telemetry & Performance):*\n"
            f"• Кол-во ответов агента (Agent turns): {agent_turns}\n"
            f"• Средняя задержка (Avg Latency): {avg_latency:.2f} сек.\n"
            f"• Всего входящих токенов (Total Input Tokens): {total_in_tokens}\n"
            f"• Всего исходящих токенов (Total Output Tokens): {total_out_tokens}\n"
            f"• Попыток самокоррекции (Total Self-Correction Attempts): {total_val_attempts}\n"
            f"• Заблокировано вредных запросов (Blocked Input Guardrails): {failed_inputs}\n"
            f"• Заблокировано опасных ответов (Blocked Output Guardrails): {failed_outputs}\n\n"
            f"🎯 *Целевые роли студентов:*\n"
            f"{roles_str if roles_str else '• Нет данных'}"
        )
    elif language == "en":
        report = (
            f"📊 *HARNESS OPERATIONAL REPORT*\n"
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"👥 *Users:*\n"
            f"• Total registered students: {total_users}\n\n"
            f"⚙️ *Stateful Agent Metrics (SQLite Harness):*\n"
            f"• Total agent sessions: {total_sessions} ({completed_convs} completed, {active_convs} active)\n"
            f"• Total messages logged: {total_messages}\n"
            f"• Model Tool Executions: {total_tool_calls}\n"
            f"{tool_breakdown if tool_breakdown else '  ▫️ No tool calls executed'}\n\n"
            f"📈 *Module Activity:*\n"
            f"• Skill Passport (Assessment): {sp_count}\n"
            f"• Resume Builder & ATS Checker: {rb_count}\n"
            f"• Interview Simulator: {ip_count}\n"
            f"• Vacancy Matchmaker: {vc_count}\n"
            f"• Career Advice Chat: {ca_count}\n"
            f"• Quiz & Homework Assessor: {qz_count}\n\n"
            f"🎤 *Assessment Performance:*\n"
            f"• Simulated interviews graded: {len(interview_scores)}\n"
            f"• Average STAR Score: {avg_interview_score:.1f}/10\n"
            f"• Quiz attempts: {quiz_attempts_cnt} (Average Score: {avg_quiz_score:.1f}/3)\n\n"
            f"🛡 *Security & Risk Profile (Model Guard):*\n"
            f"• Total logged risk events: {total_risks} (Critical: {critical_risks}, High: {high_risks}, Medium: {medium_risks})\n"
            f"{latest_risks_str if latest_risks_str else '  🚨 No risks detected'}\n\n"
            f"⚡ *Model Telemetry & Performance:*\n"
            f"• Agent responses (Agent turns): {agent_turns}\n"
            f"• Average Latency (Avg Latency): {avg_latency:.2f} seconds\n"
            f"• Total Input Tokens: {total_in_tokens}\n"
            f"• Total Output Tokens: {total_out_tokens}\n"
            f"• Total Self-Correction Attempts: {total_val_attempts}\n"
            f"• Blocked Input Guardrail Hits: {failed_inputs}\n"
            f"• Blocked Output Guardrail Hits: {failed_outputs}\n\n"
            f"🎯 *Target Roles:* \n"
            f"{roles_str if roles_str else '• No data'}"
        )
    else:  # Uzbek
        report = (
            f"📊 *HARNESS FOYDALANISH VA OPERATSION HISOBOT*\n"
            f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"👥 *Foydalanuvchilar:*\n"
            f"• Ro'yxatdan o'tgan talabalar: {total_users}\n\n"
            f"⚙️ *Stateful Agent Ko'rsatkichlari (SQLite Harness):*\n"
            f"• Umumiy sessiyalar: {total_sessions} ta ({completed_convs} yakunlangan, {active_convs} faol)\n"
            f"• Saqlangan xabarlar: {total_messages} ta\n"
            f"• Model instrumentlarining chaqiruvi (Tool Calls): {total_tool_calls} ta\n"
            f"{tool_breakdown if tool_breakdown else '  ▫️ Instrumentlar ishlatilmadi'}\n\n"
            f"📈 *Xizmatlar faolligi:*\n"
            f"• Skill Passport (Baholash): {sp_count}\n"
            f"• Rezyume yaratish (Resume Optimizer): {rb_count}\n"
            f"• Intervyu mashqi (Interview Simulator): {ip_count}\n"
            f"• Vakansiyalar Matchmaker: {vc_count}\n"
            f"• Karyera maslahatlari: {ca_count}\n"
            f"• Quiz & Homework Assessor: {qz_count}\n\n"
            f"🎤 *Baholash Natijalari:* \n"
            f"• Baholangan mock intervyular: {len(interview_scores)} ta\n"
            f"• O'rtacha STAR bahosi (Ball): {avg_interview_score:.1f}/10\n"
            f"• Quiz topshirishlar soni: {quiz_attempts_cnt} ta (O'rtacha ball: {avg_quiz_score:.1f}/3)\n\n"
            f"🛡 *Xavfsizlik va Model Anomaliyalari (Model Guard):*\n"
            f"• Aniqlangan xavflar soni: {total_risks} ta (Kritik: {critical_risks}, Yuqori: {high_risks}, O'rta: {medium_risks})\n"
            f"{latest_risks_str if latest_risks_str else '  🚨 Xavflar aniqlanmadi'}\n\n"
            f"⚡ *Model Telemetriyasi va Ishlash Tezligi (Model Telemetry & Performance):*\n"
            f"• Agent javoblari soni (Agent turns): {agent_turns} ta\n"
            f"• O'rtacha kechikish (Avg Latency): {avg_latency:.2f} soniya\n"
            f"• Jami kiruvchi tokenlar (Total Input Tokens): {total_in_tokens} ta\n"
            f"• Jami chiquvchi tokenlar (Total Output Tokens): {total_out_tokens} ta\n"
            f"• Jami o'z-o'zini tuzatish urinishlari (Total Self-Correction Attempts): {total_val_attempts} ta\n"
            f"• Bloklangan zararli so'rovlar (Blocked Input Guardrails): {failed_inputs} ta\n"
            f"• Bloklangan xavfli javoblar (Blocked Output Guardrails): {failed_outputs} ta\n\n"
            f"🎯 *Talabalar tanlagan yo'nalishlar:*\n"
            f"{roles_str if roles_str else '• Ma`lumot yo`q'}"
        )

    return report

