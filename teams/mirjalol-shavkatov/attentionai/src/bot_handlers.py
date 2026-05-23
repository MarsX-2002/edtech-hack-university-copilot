"""
Telegram Bot Handlers for Career AI Assistant.
Manages conversations, inline buttons, state tracking, and business logic.
"""
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from src.config import ADMIN_IDS
from src.i18n import t, ROLE_MAP
from src.storage import (
    get_student, save_student, get_student_lang, init_storage,
    add_skill_assessment, add_interview_session, add_resume,
    track_event, increment_user_count, load_students
)
from src.career_modes import (
    assess_skills, generate_resume, generate_interview_question,
    evaluate_interview_answer, match_vacancies, get_career_advice,
    run_interview_agent_turn, run_resume_agent_turn,
    run_vacancy_agent_turn, run_quiz_agent_turn
)
from src.db import (
    create_conversation, get_active_conversation, complete_conversation,
    log_quiz_attempt, log_homework_feedback
)
from src.analytics import get_analytics_report
from src.auth import get_student_by_student_id, get_student_by_phone

# Initialize JSON-based storage
init_storage()

# Student ID validation: exactly 6 digits
STUDENT_ID_REGEX = re.compile(r'^\d{6}$')

# Back buttons set for checking across all languages
BACK_BUTTONS = {
    "⬅️ Orqaga", "⬅️ Назад", "⬅️ Back",
    "🏠 Asosiy menyu", "🏠 Главное меню", "🏠 Main Menu",
    "🏁 Yakunlash", "🏁 Завершить", "🏁 End Interview"
}


def get_lang_keyboard():
    """Inline keyboard for language selection."""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard(lang: str):
    """Main menu keyboard based on user's preferred language."""
    keyboard = [
        [t("btn_skill_passport", lang), t("btn_resume", lang)],
        [t("btn_vacancies", lang), t("btn_my_profile", lang)],
        [t("btn_language", lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_roles_keyboard(lang: str):
    """Keyboard for selecting common target roles."""
    keyboard = [
        ["1️⃣ Frontend Developer", "2️⃣ Backend Developer", "3️⃣ Full-stack Developer"],
        ["4️⃣ Mobile Developer", "5️⃣ Data Analyst", "6️⃣ AI/ML Engineer"],
        ["7️⃣ DevOps Engineer", "8️⃣ UX/UI Designer", "9️⃣ Project Manager"],
        [t("btn_back", lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_english_keyboard():
    """Keyboard for selecting English language level."""
    keyboard = [
        ["1️⃣ Beginner (A1-A2)", "2️⃣ Intermediate (B1-B2)", "3️⃣ Advanced (C1-C2)"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_interview_type_keyboard(lang: str):
    """Keyboard for selecting interview question type."""
    keyboard = [
        [t("btn_technical", lang), t("btn_behavioral", lang)],
        [t("btn_mixed", lang)],
        [t("btn_back", lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_interview_action_keyboard(lang: str):
    """Keyboard during/after an interview question."""
    keyboard = [
        [t("btn_next_question", lang)],
        [t("btn_end_interview", lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard(lang: str):
    """Keyboard with just a back button."""
    return ReplyKeyboardMarkup([[t("btn_back", lang)]], resize_keyboard=True)


async def send_split_message(message, text, reply_markup=None):
    """Sends long messages safely by splitting them to fit within Telegram's 4096-char limit."""
    # Escape simple characters if needed or use markdown.
    # To keep it simple and robust, we use parse_mode="Markdown" with basic replacement fallback
    clean_text = text.replace("_", "\\_").replace("[", "\\[").replace("]", "\\]")
    # Fix nested bolding/italic formatting that might be broken by escape, so let's do a soft markdown escape
    # For Telegram, we just need to ensure no unclosed *, _ or `
    
    if len(text) <= 4096:
        try:
            await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception:
            # Fallback if markdown parsing fails
            await message.reply_text(text, reply_markup=reply_markup)
        return

    parts = []
    while len(text) > 4096:
        split_idx = text.rfind("\n", 0, 4096)
        if split_idx == -1:
            split_idx = 4096
        parts.append(text[:split_idx])
        text = text[split_idx:]
    parts.append(text)

    for i, part in enumerate(parts):
        is_last = (i == len(parts) - 1)
        markup = reply_markup if is_last else None
        try:
            await message.reply_text(part, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            await message.reply_text(part, reply_markup=markup)


def parse_target_role(text: str) -> str:
    """Extracts standard target role name from button click or text."""
    clean_num = re.sub(r'\D', '', text)
    if clean_num in ROLE_MAP:
        return ROLE_MAP[clean_num]
    
    # Text fallback
    text_lower = text.lower()
    if "frontend" in text_lower:
        return "Frontend Developer"
    if "backend" in text_lower:
        return "Backend Developer"
    if "full-stack" in text_lower or "fullstack" in text_lower:
        return "Full-stack Developer"
    if "mobile" in text_lower:
        return "Mobile Developer"
    if "data analyst" in text_lower or "analyst" in text_lower:
        return "Data Analyst"
    if "ai" in text_lower or "ml" in text_lower or "machine learning" in text_lower:
        return "AI/ML Engineer"
    if "devops" in text_lower:
        return "DevOps Engineer"
    if "ux" in text_lower or "ui" in text_lower or "designer" in text_lower:
        return "UX/UI Designer"
    if "project" in text_lower or "manager" in text_lower:
        return "Project Manager"
    return text.strip()


# ──────────────── Core Commands ────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command."""
    user = update.effective_user
    student = get_student(user.id)

    if student:
        lang = student.get("language", "uz")

        # Check if profile is incomplete (missing student_id or phone)
        if not student.get("student_id"):
            await update.message.reply_text(
                t("profile_incomplete", lang) + "\n\n" + t("ask_student_id", lang),
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown"
            )
            context.user_data["state"] = "reg_student_id"
            context.user_data["temp_profile"] = {
                "language": lang,
                **{k: v for k, v in student.items() if v is not None}
            }
            return

        await update.message.reply_text(
            t("main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="Markdown"
        )
        context.user_data["state"] = None
    else:
        # Prompt language choice to kickstart registration
        await update.message.reply_text(
            t("welcome", "uz"),
            reply_markup=get_lang_keyboard(),
            parse_mode="Markdown"
        )
        context.user_data["state"] = "lang_selection"


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /admin or /stats commands."""
    user = update.effective_user
    lang = get_student_lang(user.id)

    if user.id not in ADMIN_IDS:
        await update.message.reply_text(t("not_admin", lang))
        return

    report = get_analytics_report(lang)
    await update.message.reply_text(report, parse_mode="Markdown")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /broadcast <message> (Admin only)."""
    user = update.effective_user
    lang = get_student_lang(user.id)

    if user.id not in ADMIN_IDS:
        await update.message.reply_text(t("not_admin", lang))
        return

    # Extract message
    msg_content = " ".join(context.args)
    if not msg_content:
        await update.message.reply_text("Usage: /broadcast <your message here>")
        return

    students = load_students()
    success = 0
    fail = 0

    for sid in students.keys():
        try:
            await context.bot.send_message(
                chat_id=int(sid),
                text=f"📢 *E'LON / ОБЪЯВЛЕНИЕ / ANNOUNCEMENT*\n\n{msg_content}",
                parse_mode="Markdown"
            )
            success += 1
        except Exception:
            fail += 1

    await update.message.reply_text(
        f"✅ Broadcast finished.\nSent successfully: {success}\nFailed: {fail}"
    )


# ──────────────── Callback Queries (Language selection) ────────────────

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button clicks (language buttons)."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        student = get_student(user.id)

        if student:
            student["language"] = lang
            save_student(user.id, student)
            await query.message.reply_text(
                t("language_changed", lang),
                reply_markup=get_main_menu_keyboard(lang)
            )
            context.user_data["state"] = None
        else:
            # First time user: kick off profile setup
            context.user_data["temp_profile"] = {"language": lang}
            context.user_data["state"] = "reg_name"
            # Remove inline keyboard from previous message
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(
                t("ask_name", lang),
                reply_markup=ReplyKeyboardRemove()
            )


# ──────────────── Message Handlers (State Machine) ────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message distributor state machine."""
    user = update.effective_user
    text = update.message.text.strip()
    state = context.user_data.get("state")
    student = get_student(user.id)
    lang = student.get("language", "uz") if student else "uz"

    # 1. Global back button handling
    if text in BACK_BUTTONS:
        # Complete any active stateful SQLite conversations
        for conv_type in ["interview", "resume_builder", "vacancies", "quiz", "advice"]:
            conv_id = get_active_conversation(user.id, conv_type)
            if conv_id:
                complete_conversation(conv_id)
            
        context.user_data["state"] = None
        context.user_data.pop("active_conv_id", None)
        await update.message.reply_text(
            t("main_menu", lang),
            reply_markup=get_main_menu_keyboard(lang),
            parse_mode="Markdown"
        )
        return

    # 2. Registration Flow (Unregistered or changing details)
    if state and state.startswith("reg_"):
        await handle_registration(update, context, state)
        return

    # 3. Features flows
    # (sp_tech, sp_projects, sp_exp, sp_lang removed in favor of direct stateful Quiz Assessor)

    if state == "rb_target":
        context.user_data["temp_rb"] = {"target_position": text}
        await update.message.reply_text(t("resume_ask_experience", lang), reply_markup=get_back_keyboard(lang))
        context.user_data["state"] = "rb_exp"
        return

    if state == "rb_exp":
        context.user_data["temp_rb"]["experience"] = text
        await update.message.reply_text(t("resume_generating", lang), reply_markup=ReplyKeyboardRemove())

        # Call stateful Resume Agent (Harness)
        student = get_student(user.id)
        conv_id = create_conversation(user.id, "resume_builder")
        prompt = f"Optimize my resume for target position '{context.user_data['temp_rb']['target_position']}' and experience '{text}'."
        resume_text = run_resume_agent_turn(user.id, conv_id, prompt, student, lang)
        
        complete_conversation(conv_id)
        add_resume(user.id, {
            "target_position": context.user_data["temp_rb"]["target_position"],
            "experience": text,
            "result": resume_text
        })
        track_event(user.id, "resume_builder")

        await send_split_message(update.message, resume_text, reply_markup=get_main_menu_keyboard(lang))
        context.user_data["state"] = None
        return

    if state == "int_type":
        # Determine question type
        qtype_raw = text.lower()
        if "texnik" in qtype_raw or "техническ" in qtype_raw or "technical" in qtype_raw:
            qtype = "technical"
        elif "xulq" in qtype_raw or "поведенческ" in qtype_raw or "behavioral" in qtype_raw:
            qtype = "behavioral"
        else:
            qtype = "mixed"

        conv_id = create_conversation(user.id, "interview")
        context.user_data["active_conv_id"] = conv_id
        
        await update.message.reply_text(t("processing", lang), reply_markup=ReplyKeyboardRemove())

        # Call stateful Mock Interview Agent to start (Harness)
        initial_prompt = f"Start mock interview for a '{student.get('target_role', 'Developer')}' position, question type: {qtype}."
        question, _ = run_interview_agent_turn(user.id, conv_id, initial_prompt, student, lang)
        
        await update.message.reply_text(question, reply_markup=get_back_keyboard(lang))
        context.user_data["state"] = "int_qa"
        return

    if state == "int_qa":
        conv_id = context.user_data.get("active_conv_id")
        if not conv_id:
            conv_id = get_active_conversation(user.id, "interview") or create_conversation(user.id, "interview")
            context.user_data["active_conv_id"] = conv_id

        await update.message.reply_text(t("interview_evaluating", lang), reply_markup=ReplyKeyboardRemove())
        
        # Call stateful Mock Interview Agent turn (Harness)
        agent_response, data = run_interview_agent_turn(user.id, conv_id, text, student, lang)
        
        # Check if interview is completed (agent generated final STAR assessment report with X/10 score)
        score = None
        is_completed = False
        if data:
            is_completed = data.get("is_completed", False)
            report = data.get("final_report")
            if report:
                is_completed = True
                score = report.get("score")
        
        if is_completed:
            complete_conversation(conv_id)
            add_interview_session(user.id, {
                "type": "agent",
                "history": [{"question": "Agent Mock Interview", "answer": "Stateful Chat Completion", "evaluation": agent_response, "score": score}]
            })
            track_event(user.id, "interview_practice", "Completed stateful session")
            if score is not None:
                student["readiness_score"] = score
                save_student(user.id, student)
            await send_split_message(update.message, agent_response, reply_markup=get_main_menu_keyboard(lang))
            context.user_data["state"] = None
        else:
            await send_split_message(update.message, agent_response, reply_markup=get_back_keyboard(lang))
        return

    if state == "vacancies_chat":
        conv_id = context.user_data.get("active_conv_id")
        if not conv_id:
            conv_id = get_active_conversation(user.id, "vacancies") or create_conversation(user.id, "vacancies")
            context.user_data["active_conv_id"] = conv_id

        await update.message.reply_text(t("processing", lang), reply_markup=ReplyKeyboardRemove())
        
        # Call stateful Vacancy Matchmaker Agent (Harness)
        agent_response = run_vacancy_agent_turn(user.id, conv_id, text, student, lang)
        track_event(user.id, "vacancies", text[:100])
        
        await send_split_message(update.message, agent_response, reply_markup=get_back_keyboard(lang))
        return

    if state == "quiz_chat":
        conv_id = context.user_data.get("active_conv_id")
        if not conv_id:
            conv_id = get_active_conversation(user.id, "quiz") or create_conversation(user.id, "quiz")
            context.user_data["active_conv_id"] = conv_id

        await update.message.reply_text(t("processing", lang), reply_markup=ReplyKeyboardRemove())
        
        # Call stateful Quiz Assessor Agent (Harness)
        agent_response, data = run_quiz_agent_turn(user.id, conv_id, text, student, lang)
        
        # Check if quiz is finished and grade attempt
        score = None
        total = 3
        is_completed = False
        quiz_topic = None
        if data:
            is_completed = data.get("is_completed", False)
            report = data.get("final_report")
            if report:
                is_completed = True
                score = report.get("score")
                quiz_topic = report.get("quiz_topic")
        
        if is_completed:
            log_quiz_attempt(user.id, quiz_topic if quiz_topic else student.get("target_role", "Developer"), score if score is not None else 0, total, agent_response)
            complete_conversation(conv_id)
            track_event(user.id, "quiz_assessment", f"Score: {score}/{total}")
            
            # Update student profile with verified skills if score >= 2
            if score is not None and score >= 2:
                topic_to_verify = quiz_topic if quiz_topic else student.get("target_role", "Developer")
                topic_to_verify = topic_to_verify.strip()
                current_skills = student.get("skills", "")
                skills_list = [s.strip() for s in current_skills.split(",") if s.strip()]
                
                # Check if we should append/replace target_role (Verified)
                verified_badge = f"{topic_to_verify} (Verified)"
                clean_skills = []
                found = False
                for s in skills_list:
                    s_clean = s.replace(" (Verified)", "").replace(" (verified)", "").strip()
                    if s_clean.lower() == topic_to_verify.lower():
                        clean_skills.append(verified_badge)
                        found = True
                    else:
                        clean_skills.append(s)
                if not found:
                    clean_skills.append(verified_badge)
                
                student["skills"] = ", ".join(clean_skills)
                save_student(user.id, student)

            await send_split_message(update.message, agent_response, reply_markup=get_main_menu_keyboard(lang))
            context.user_data["state"] = None
        else:
            await send_split_message(update.message, agent_response, reply_markup=get_back_keyboard(lang))
        return

    if state == "advice_query":
        await update.message.reply_text(t("processing", lang))
        conv_id = context.user_data.get("active_conv_id")
        if not conv_id:
            conv_id = get_active_conversation(user.id, "advice") or create_conversation(user.id, "advice")
            context.user_data["active_conv_id"] = conv_id
        reply = get_career_advice(user.id, conv_id, text, student, lang)
        track_event(user.id, "career_advice", text[:100])
        await send_split_message(update.message, reply, reply_markup=get_back_keyboard(lang))
        return

    # 4. Standard Menu Options Check (when state is None)
    if student:
        # Match button texts in any language
        if text in (t("btn_skill_passport", "uz"), t("btn_skill_passport", "ru"), t("btn_skill_passport", "en")):
            # Send intro with start button
            await update.message.reply_text(
                t("skill_passport_intro", lang),
                reply_markup=ReplyKeyboardMarkup([[t("btn_start", lang)], [t("btn_back", lang)]], resize_keyboard=True),
                parse_mode="Markdown"
            )
            context.user_data["state"] = "sp_wait_start"
            return

        # Wait for start button press
        if state == "sp_wait_start":
            if text == t("btn_start", lang):
                conv_id = create_conversation(user.id, "quiz")
                context.user_data["active_conv_id"] = conv_id
                context.user_data["state"] = "quiz_chat"
                
                await update.message.reply_text(t("processing", lang), reply_markup=ReplyKeyboardRemove())
                initial_prompt = f"Start quiz assessment for '{student.get('target_role', 'Developer')}' with skills '{student.get('skills', 'None')}'."
                agent_response, _ = run_quiz_agent_turn(user.id, conv_id, initial_prompt, student, lang)
                
                await send_split_message(update.message, agent_response, reply_markup=get_back_keyboard(lang))
                return
            else:
                await update.message.reply_text(t("error_generic", lang))
                return

        if text in (t("btn_resume", "uz"), t("btn_resume", "ru"), t("btn_resume", "en")):
            intro_msg = f"{t('resume_intro', lang)}\n\n{t('resume_ask_target', lang)}"
            await update.message.reply_text(intro_msg, reply_markup=get_back_keyboard(lang), parse_mode="Markdown")
            context.user_data["state"] = "rb_target"
            context.user_data["temp_rb"] = {}
            return

        if text in (t("btn_vacancies", "uz"), t("btn_vacancies", "ru"), t("btn_vacancies", "en")):
            conv_id = create_conversation(user.id, "vacancies")
            context.user_data["active_conv_id"] = conv_id
            context.user_data["state"] = "vacancies_chat"
            
            if lang == "ru":
                msg = "💼 Я ваш умный агент по поиску вакансий. Какую технологию, компанию или направление вы ищете? (Например: Python, React, удаленно)"
            elif lang == "en":
                msg = "💼 I am your smart vacancy matchmaking agent. What technology, company, or role are you looking for? (e.g. Python, React, remote)"
            else: # uz
                msg = "💼 Men sizning aqlli vakansiya qidirish agentingizman. Qaysi texnologiya, kompaniya yoki yo'nalish bo'yicha ish qidiryapsiz? (Masalan: Python, React, masofaviy)"
            
            await update.message.reply_text(msg, reply_markup=get_back_keyboard(lang))
            return

        if text in (t("btn_my_profile", "uz"), t("btn_my_profile", "ru"), t("btn_my_profile", "en")):
            readiness_val = student.get("readiness_score")
            readiness_str = f"{int(readiness_val) if readiness_val is not None and readiness_val == int(readiness_val) else readiness_val}/10" if readiness_val is not None else "N/A"
            
            # Format skills with badge emojis for verified skills
            raw_skills = student.get('skills', '')
            formatted_skills = []
            if raw_skills:
                for s in raw_skills.split(","):
                    s = s.strip()
                    if not s:
                        continue
                    if "(Verified)" in s:
                        formatted_skills.append(f"✅ {s}")
                    else:
                        formatted_skills.append(s)
                skills_str = ", ".join(formatted_skills) if formatted_skills else "None"
            else:
                skills_str = "None"

            profile_info = (
                f"👤 *PROFILE INFO*\n\n"
                f"🏷 *Name:* {student.get('name')}\n"
                f"🏫 *University:* {student.get('university')}\n"
                f"📚 *Faculty/Major:* {student.get('faculty')}\n"
                f"🎓 *Year:* {student.get('year')}\n"
                f"🎯 *Target Role:* {student.get('target_role')}\n"
                f"🛠 *Current Skills:* {skills_str}\n"
                f"📈 *Target Role Readiness:* {readiness_str}\n"
                f"🌐 *Bot Language:* {lang.upper()}\n\n"
                f"To re-register, type `/start` at any time."
            )
            await update.message.reply_text(profile_info, reply_markup=get_main_menu_keyboard(lang), parse_mode="Markdown")
            return

        if text in (t("btn_language", "uz"), t("btn_language", "ru"), t("btn_language", "en")):
            await update.message.reply_text(
                "Tilni tanlang / Выберите язык / Choose language:",
                reply_markup=get_lang_keyboard()
            )
            context.user_data["state"] = "change_lang"
            return

    # 5. Default Fallback
    if not student:
        await update.message.reply_text(
            t("welcome", "uz"),
            reply_markup=get_lang_keyboard(),
            parse_mode="Markdown"
        )
        context.user_data["state"] = "lang_selection"
    else:
        # Fallback to direct Career Advice Chat if no matching button
        await update.message.reply_text(t("processing", lang))
        conv_id = get_active_conversation(user.id, "advice") or create_conversation(user.id, "advice")
        reply = get_career_advice(user.id, conv_id, text, student, lang)
        track_event(user.id, "career_advice", text[:100])
        await send_split_message(update.message, reply, reply_markup=get_main_menu_keyboard(lang))


# ──────────────── Registration Helper Flow ────────────────

def get_phone_keyboard(lang: str):
    """Keyboard with 'Share Contact' button and 'Skip' option."""
    keyboard = [
        [KeyboardButton(t("btn_share_phone", lang), request_contact=True)],
        [t("btn_skip_phone", lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    """Processes multi-step profile registration flow."""
    user = update.effective_user
    text = update.message.text.strip() if update.message.text else ""
    temp = context.user_data.get("temp_profile", {})
    lang = temp.get("language", "uz")

    if state == "reg_name":
        temp["name"] = text
        # Store telegram metadata
        temp["telegram_username"] = user.username
        temp["telegram_full_name"] = user.full_name
        await update.message.reply_text(t("ask_student_id", lang), reply_markup=ReplyKeyboardRemove())
        context.user_data["state"] = "reg_student_id"
        return

    if state == "reg_student_id":
        # Validate 6-digit format
        if not STUDENT_ID_REGEX.match(text):
            await update.message.reply_text(t("invalid_student_id", lang))
            return  # Stay in same state

        # Check uniqueness
        existing = get_student_by_student_id(text)
        if existing and existing.get("telegram_user_id") != str(user.id):
            await update.message.reply_text(t("student_id_taken", lang))
            return  # Stay in same state

        temp["student_id"] = text
        
        # Optimize: For migrated users with existing profiles, bypass university/major setup
        # and navigate directly to phone verification.
        if temp.get("university") and temp.get("faculty") and temp.get("year") and temp.get("target_role"):
            await update.message.reply_text(
                t("ask_phone", lang),
                reply_markup=get_phone_keyboard(lang)
            )
            context.user_data["state"] = "reg_phone"
        else:
            await update.message.reply_text(t("ask_university", lang), reply_markup=ReplyKeyboardRemove())
            context.user_data["state"] = "reg_university"
        return

    if state == "reg_university":
        temp["university"] = text
        await update.message.reply_text(t("ask_faculty", lang))
        context.user_data["state"] = "reg_faculty"
        return

    if state == "reg_faculty":
        temp["faculty"] = text
        await update.message.reply_text(t("ask_year", lang))
        context.user_data["state"] = "reg_year"
        return

    if state == "reg_year":
        temp["year"] = text
        await update.message.reply_text(t("ask_target_role", lang), reply_markup=get_roles_keyboard(lang))
        context.user_data["state"] = "reg_role"
        return

    if state == "reg_role":
        role = parse_target_role(text)
        temp["target_role"] = role
        temp["skills"] = ""  # initial skills empty, will be updated by Skill Passport

        # Ask for phone number via contact share
        await update.message.reply_text(
            t("ask_phone", lang),
            reply_markup=get_phone_keyboard(lang)
        )
        context.user_data["state"] = "reg_phone"
        return

    if state == "reg_phone":
        # User typed "skip" button text
        skip_texts = {t("btn_skip_phone", "uz"), t("btn_skip_phone", "ru"), t("btn_skip_phone", "en")}
        if text in skip_texts:
            # Save without phone
            save_student(user.id, temp)
            increment_user_count()
            track_event(user.id, "registration", f"Target role: {temp.get('target_role', 'N/A')}")

            await update.message.reply_text(
                t("profile_saved", lang),
                reply_markup=get_main_menu_keyboard(lang)
            )
            context.user_data["state"] = None
            context.user_data.pop("temp_profile", None)
            return

        # If they typed something else (not contact share), tell them to use button
        await update.message.reply_text(
            t("phone_spoofed", lang),
            reply_markup=get_phone_keyboard(lang)
        )
        return


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for contact shares (phone number via Telegram button).
    Verifies contact.user_id == sender, stores in E.164 format.
    """
    user = update.effective_user
    contact = update.message.contact
    state = context.user_data.get("state")
    temp = context.user_data.get("temp_profile", {})
    lang = temp.get("language", get_student_lang(user.id))

    if state != "reg_phone":
        # Contact shared outside registration — ignore
        return

    # Security: verify contact belongs to the sender
    if contact.user_id != user.id:
        await update.message.reply_text(
            t("phone_spoofed", lang),
            reply_markup=get_phone_keyboard(lang)
        )
        return

    # Normalize phone to E.164
    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    # Check uniqueness
    existing = get_student_by_phone(phone)
    if existing and existing.get("telegram_user_id") != str(user.id):
        await update.message.reply_text(
            t("phone_taken", lang),
            reply_markup=get_phone_keyboard(lang)
        )
        return

    # Save with phone
    temp["phone_number"] = phone
    save_student(user.id, temp)
    increment_user_count()
    track_event(user.id, "registration", f"Target role: {temp.get('target_role', 'N/A')}")

    await update.message.reply_text(
        t("phone_verified", lang) + "\n\n" + t("profile_saved", lang),
        reply_markup=get_main_menu_keyboard(lang)
    )
    context.user_data["state"] = None
    context.user_data.pop("temp_profile", None)

