"""
Stateful custom agent runner harness for the Career AI Assistant.
Manages multi-turn conversations, executes native tool-calling with SQLite persistence,
integrates guardrails, post-execution validation, self-correction retries, and records telemetry.
"""
import json
import logging
import traceback
import time
from datetime import datetime

import src.config
from src.config import (
    GEMINI_API_KEY, OPENAI_API_KEY, DEFAULT_PROVIDER,
    GEMINI_MODEL, OPENAI_MODEL, API_FAILED
)
from src.db import (
    add_message, add_tool_call, add_tool_result,
    get_conversation_history, log_risk, update_message_telemetry
)
from src.tools import (
    search_knowledge_base,
    search_vacancies,
    check_resume_ats,
    get_student_profile,
    update_student_profile,
    log_risk_event
)
from src.schemas import (
    MockInterviewOutput,
    ResumeOptimizationOutput,
    VacancyMatchmakingOutput,
    QuizOutput,
    CareerAdviceOutput
)
from src.guardrails import check_input_safety, check_output_safety
from src.validator import (
    validate_response_language,
    validate_vacancy_response,
    validate_resume_response,
    validate_interview_response,
    validate_quiz_response
)
from src.storage import get_student_lang

logger = logging.getLogger(__name__)

# Expose tools list and mapping
TOOLS_LIST = [
    search_knowledge_base,
    search_vacancies,
    check_resume_ats,
    get_student_profile,
    update_student_profile,
    log_risk_event
]

# Simple mapping for tools execution
TOOLS_MAP = {t.__name__: t for t in TOOLS_LIST}

SCHEMA_MAP = {
    "interview": MockInterviewOutput,
    "resume_builder": ResumeOptimizationOutput,
    "vacancies": VacancyMatchmakingOutput,
    "quiz": QuizOutput,
    "advice": CareerAdviceOutput,
    "skills": CareerAdviceOutput
}

VALIDATOR_MAP = {
    "interview": validate_interview_response,
    "resume_builder": validate_resume_response,
    "vacancies": validate_vacancy_response,
    "quiz": validate_quiz_response
}

def get_openai_tool_specs() -> list[dict]:
    """Generates JSON schema tool specs for OpenAI function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "Queries the university career center knowledge base guidelines and returns matching text chunks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search term or topic to look up in the career database."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_vacancies",
                "description": "Searches the available database of partner vacancies, stajirovkas, and internships.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keywords to search for in vacancy title, company, or required skills."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_resume_ats",
                "description": "Performs an ATS compatibility check on a markdown resume draft.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resume_markdown": {"type": "string", "description": "The markdown content of the resume draft."},
                        "target_position": {"type": "string", "description": "The job title or role being targeted."}
                    },
                    "required": ["resume_markdown", "target_position"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_student_profile",
                "description": "Retrieves the registration profile details of the student.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "telegram_id": {"type": "integer", "description": "The Telegram ID of the student."}
                    },
                    "required": ["telegram_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_student_profile",
                "description": "Updates student profile registration fields in database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "telegram_id": {"type": "integer", "description": "The Telegram ID of the student."},
                        "profile_data": {
                            "type": "object",
                            "description": "Key-value dictionary containing the updated fields."
                        }
                    },
                    "required": ["telegram_id", "profile_data"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "log_risk_event",
                "description": "Logs security concerns, API errors, or unexpected outputs to the monitoring dashboard.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "telegram_id": {"type": "integer", "description": "The Telegram ID of the student."},
                        "category": {"type": "string", "description": "The class of issue ('hallucination', 'api_failure')."},
                        "description": {"type": "string", "description": "A short explanation of what went wrong."},
                        "severity": {"type": "string", "description": "High, Medium, or Low."}
                    },
                    "required": ["telegram_id", "category", "description"]
                }
            }
        }
    ]

def execute_tool(telegram_id: int, message_id: int, tool_name: str, arguments_dict: dict) -> str:
    """Invokes a Python tool function, logs execution metadata in SQLite, and returns string output."""
    tc_id = None
    try:
        args_str = json.dumps(arguments_dict)
        tc_id = add_tool_call(message_id, tool_name, args_str)
        logger.info(f"Agent executing tool '{tool_name}' with args {args_str}")

        if tool_name not in TOOLS_MAP:
            result = {"error": f"Tool '{tool_name}' is not defined."}
        else:
            func = TOOLS_MAP[tool_name]
            result = func(**arguments_dict)

        result_str = json.dumps(result, ensure_ascii=False)
        if tc_id:
            add_tool_result(tc_id, result_str)
        return result_str
    except Exception as e:
        err_msg = f"Tool execution failed: {e}"
        logger.error(err_msg)
        if tc_id:
            add_tool_result(tc_id, json.dumps({"error": err_msg}))
        log_risk(telegram_id, "api_failure", f"Tool execution failed for '{tool_name}': {e}", "medium")
        return json.dumps({"error": err_msg})

def run_agent_turn(telegram_id: int, conversation_id: int, user_message: str, 
                   system_instruction: str, provider: str = None) -> str:
    """
    Executes a single conversational agent turn.
    Applies input guardrails, runs self-correcting validation loops with Pydantic JSON enforcement,
    captures latency and token usage, runs output guardrails, and updates SQLite telemetry.
    """
    if provider is None:
        provider = DEFAULT_PROVIDER

    language = get_student_lang(telegram_id)

    # 1. Fetch conversation type from database to determine Pydantic schema
    from src.db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type FROM conversations WHERE id = ?;", (conversation_id,))
    row = cursor.fetchone()
    conv_type = row["type"] if row else "advice"
    conn.close()

    response_schema = SCHEMA_MAP.get(conv_type, CareerAdviceOutput)

    # 2. Input Guardrails
    is_safe, warning_msg = check_input_safety(user_message, language, provider)
    if not is_safe:
        user_msg_id = add_message(conversation_id, "user", user_message)
        agent_msg_id = add_message(conversation_id, "agent", warning_msg)
        update_message_telemetry(
            message_id=agent_msg_id,
            content=warning_msg,
            latency_ms=0,
            input_tokens=0,
            output_tokens=0,
            validation_attempts=0,
            guardrail_status="failed_input"
        )
        log_risk(telegram_id, "unauthorized", f"Input guardrail blocked query: '{user_message}'", "high")
        return warning_msg

    # 3. Log user message & retrieve conversation history
    user_msg_id = add_message(conversation_id, "user", user_message)
    history = get_conversation_history(conversation_id)

    # If the API key is broken, trigger mock fallback directly
    if src.config.API_FAILED:
        provider = "mock"

    start_time = time.time()
    validation_attempts = 0
    max_validation_attempts = 3
    validation_error_feedback = ""
    guardrail_status = "passed"
    final_text = ""
    prompt_tokens = 0
    completion_tokens = 0

    # Main self-correcting validation loop
    while validation_attempts < max_validation_attempts:
        raw_text = ""
        # --- GEMINI PROVIDER ---
        if provider == "gemini" and GEMINI_API_KEY:
            try:
                import google.genai as genai
                from google.genai import types
                client = genai.Client()

                # Compile past conversation into genai SDK Content format
                contents = []
                for h in history[:-1]:
                    role = "user" if h["role"] == "user" else "model"
                    contents.append(
                        genai.types.Content(
                            role=role,
                            parts=[genai.types.Part.from_text(text=h["content"])]
                        )
                    )
                # Add latest user message
                contents.append(
                    genai.types.Content(
                        role="user",
                        parts=[genai.types.Part.from_text(text=user_message)]
                    )
                )

                # Append previous validation feedback if we are in retry turn
                if validation_attempts > 0 and validation_error_feedback:
                    contents.append(
                        genai.types.Content(
                            role="user",
                            parts=[genai.types.Part.from_text(text=validation_error_feedback)]
                        )
                    )

                # Configure structured output + tools
                has_tools = conv_type in ["resume_builder", "vacancies"]
                gemini_tools = TOOLS_LIST if has_tools else None
                mime_type = None if has_tools else "application/json"
                schema = None if has_tools else response_schema

                config = genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    tools=gemini_tools,
                    response_mime_type=mime_type,
                    response_schema=schema
                )

                agent_msg_id = None
                # Manual tool calling loop (max 5 turns)
                for turn in range(5):
                    response = client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=contents,
                        config=config
                    )

                    # Extract usage metadata
                    if response.usage_metadata:
                        prompt_tokens = response.usage_metadata.prompt_token_count
                        completion_tokens = response.usage_metadata.candidates_token_count

                    # Check for tool calls
                    if response.function_calls:
                        if not agent_msg_id:
                            agent_msg_id = add_message(conversation_id, "agent", "[Executing Tools...]")

                        model_parts = []
                        tool_responses = []

                        for call in response.function_calls:
                            model_parts.append(genai.types.Part.from_function_call(
                                name=call.name,
                                args=call.args
                            ))
                            # Execute tool
                            tool_out = execute_tool(telegram_id, agent_msg_id, call.name, call.args)
                            tool_responses.append(genai.types.Part.from_function_response(
                                name=call.name,
                                response={"result": tool_out}
                            ))

                        contents.append(genai.types.Content(role="model", parts=model_parts))
                        contents.append(genai.types.Content(role="tool", parts=tool_responses))
                    else:
                        raw_text = response.text.strip() if response.text else "{}"
                        break
                
            except Exception as gemini_err:
                logger.error(f"Agent Gemini execution failed: {gemini_err}. Falling back to OpenAI if available.")
                traceback.print_exc()
                if OPENAI_API_KEY:
                    provider = "openai"
                else:
                    src.config.API_FAILED = True
                    provider = "mock"

        # --- OPENAI PROVIDER ---
        if provider == "openai" and OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)

                messages = [{"role": "system", "content": system_instruction}]
                for h in history:
                    role = "assistant" if h["role"] == "agent" else h["role"]
                    messages.append({"role": role, "content": h["content"]})

                if validation_attempts > 0 and validation_error_feedback:
                    messages.append({"role": "user", "content": validation_error_feedback})

                has_tools = conv_type in ["resume_builder", "vacancies"]
                openai_tools = get_openai_tool_specs() if has_tools else None

                agent_msg_id = None
                # Tool loop (max 5 turns)
                for turn in range(5):
                    if has_tools:
                        response = client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=messages,
                            tools=openai_tools,
                            tool_choice="auto",
                            temperature=0.3,
                            response_format={"type": "json_object"}
                        )
                    else:
                        response = client.beta.chat.completions.parse(
                            model=OPENAI_MODEL,
                            messages=messages,
                            temperature=0.3,
                            response_format=response_schema
                        )

                    # Extract usage metadata
                    if response.usage:
                        prompt_tokens = response.usage.prompt_tokens
                        completion_tokens = response.usage.completion_tokens

                    resp_message = response.choices[0].message
                    if resp_message.tool_calls:
                        if not agent_msg_id:
                            agent_msg_id = add_message(conversation_id, "agent", "[Executing Tools...]")

                        messages.append(resp_message)

                        for tool_call in resp_message.tool_calls:
                            t_name = tool_call.function.name
                            t_args = json.loads(tool_call.function.arguments)

                            tool_out = execute_tool(telegram_id, agent_msg_id, t_name, t_args)

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": t_name,
                                "content": tool_out
                            })
                    else:
                        raw_text = resp_message.content.strip() if resp_message.content else "{}"
                        break

            except Exception as openai_err:
                logger.error(f"Agent OpenAI execution failed: {openai_err}")
                traceback.print_exc()
                src.config.API_FAILED = True
                provider = "mock"

        # --- MOCK / FALLBACK PROVIDER ---
        if provider == "mock":
            logger.warning("Agent fallback to mock logic")
            log_risk(telegram_id, "fallback_triggered", "LLM APIs are unavailable. Triggered rule-based fallback.", "low")
            
            mock_data = {}
            if conv_type == "interview":
                user_msgs = [h for h in history if h["role"] == "user"]
                q_num = len(user_msgs)
                
                questions = {
                    1: "💻 REST API nima va u qanday ishlaydi? POST va PUT metodlari o'rtasidagi farqni tushuntiring.\n\n_Eslatma: Google Gemini/OpenAI API ulanishi muvaffaqiyatsiz tugadi._",
                    2: "🤝 Jamoada ziddiyatli vaziyatga duch kelganmisiz va uni qanday hal qilgansiz? (STAR metodi bilan javob bering).\n\n_Eslatma: Google Gemini/OpenAI API ulanishi muvaffaqiyatsiz tugadi._",
                    3: "💻 SQL-da indexlar qanday ishlaydi va ular qachon ishlatilishi kerak?\n\n_Eslatma: Google Gemini/OpenAI API ulanishi muvaffaqiyatsiz tugadi._",
                }
                
                if q_num <= 3:
                    mock_data = {
                        "question_number": q_num,
                        "question_text": questions.get(q_num, questions[1]),
                        "feedback_on_previous": "Javobingiz uchun rahmat. Keling, keyingi savolga o'tamiz." if q_num > 1 else "Keling, bilimingizni tekshirishni boshlaymiz.",
                        "is_completed": False,
                        "final_report": None
                    }
                else:
                    mock_data = {
                        "question_number": q_num,
                        "question_text": "Muvaffaqiyatli yakunlandi.",
                        "feedback_on_previous": "Ajoyib! Intervyu yakunlandi.",
                        "is_completed": True,
                        "final_report": {
                            "score": 8.0,
                            "strengths": ["Yaxshi nazariy bilim", "Tushunarli tushuntirish"],
                            "improvements": ["Amaliy tajriba kamligi"],
                            "star_analysis": "Situation: Yaxshi yoritilgan.\nTask: Aniq belgilangan.\nAction: Ko'rsatilgan.\nResult: Keltirilgan."
                        }
                    }
            elif conv_type == "resume_builder":
                from src.storage import get_student
                student = get_student(telegram_id) or {}
                name = student.get("name", "MIRJALOL SHAVKATOV").upper()
                phone = student.get("phone_number", "+998 XX XXX XX XX")
                telegram_username = student.get("telegram_username", "")
                telegram = f"@{telegram_username}" if telegram_username else "@student"
                skills = student.get("skills", "Python, Git, REST API, SQLite")
                mock_data = {
                    "ats_score": 75,
                    "missing_sections": ["SUMMARY", "EXPERIENCE"],
                    "missing_keywords": ["PYTHON", "DOCKER"],
                    "optimized_resume_markdown": f"*{name}*\n📧 email@example.com | 📱 {phone} | 💬 {telegram}\n\n*Professional Summary*\nJunior Developer seeking position. Experienced in {skills}.\n\n*Skills*\n{skills}\n\nFields to fill: [Email], [Address], [LinkedIn]\n_⚠️ Eslatma: Google Gemini/OpenAI API ulanishi muvaffaqiyatsiz tugadi. Bu statik mock javobdir._",
                    "critical_recommendations": [
                        "Rezyume sarlavhasiga professional SUMMARY qo'shing.",
                        "Ish tajribangizni batafsilroq yozing."
                    ]
                }
            elif conv_type == "vacancies":
                mock_data = {
                    "matches": [
                        {
                            "vacancy_title": "Junior Python Backend Developer",
                            "company": "Uzum Tech",
                            "match_score": 85,
                            "skill_gaps": ["Docker", "Django"],
                            "why_matches": "Python va SQL ko'nikmalaringiz Uzum Tech backend guruhiga mos keladi.",
                            "cover_letter": "Hurmatli Uzum Tech jamoasi,\n\nMen junior backend developer pozitsiyasiga ariza topshirmoqchiman...",
                            "networking_message": "Salom, Uzum Tech'dagi Junior Python vakansiyasi bo'yicha bog'lanayotgan edim."
                        }
                    ]
                }
            elif conv_type == "quiz":
                user_msgs = [h for h in history if h["role"] == "user"]
                q_num = len(user_msgs)
                
                questions = {
                    1: "Python-da list va tuple o'rtasidagi asosiy farq nima?",
                    2: "REST API-da GET va POST metodlari o'rtasidagi farq nima?",
                    3: "Relatsion ma'lumotlar bazasida indexlar nima uchun ishlatiladi?",
                }
                
                if q_num <= 3:
                    mock_data = {
                        "question_number": q_num,
                        "question_text": questions.get(q_num, questions[1]),
                        "is_completed": False,
                        "feedback_on_previous": "Javobingiz uchun rahmat. Keling, keyingi savolga o'tamiz." if q_num > 1 else "Keling, bilimingizni tekshirish uchun quizni boshlaymiz.",
                        "final_report": None
                    }
                else:
                    mock_data = {
                        "question_number": q_num,
                        "question_text": "Quiz yakunlandi.",
                        "is_completed": True,
                        "feedback_on_previous": "Quiz muvaffaqiyatli tugallandi!",
                        "final_report": {
                            "score": 3.0,
                            "quiz_topic": "Python & Database basics",
                            "errors_analysis": "Barcha savollarga to'g'ri javob berildi. Xatolar yo'q.",
                            "future_recommendations": "Bilimingiz juda yaxshi. Amaliy loyihalar yaratishda davom eting."
                        }
                    }
            else:
                mock_data = {
                    "response_text": "Sizga karyera bo'yicha tavsiyalar: IT sohasida muvaffaqiyat qozonish uchun amaliy loyihalar va portfolio yaratish shart. Shuningdek, rezyumeingizni ATS talablariga moslang.\n\n_Eslatma: Google Gemini/OpenAI API ulanishi muvaffaqiyatsiz tugadi._",
                    "suggested_next_steps": [
                        "Skill Passport bo'limida bilimingizni baholang",
                        "Rezyume optimallashtirish bo'limiga kiring"
                    ]
                }
            raw_text = json.dumps(mock_data, ensure_ascii=False)

        # 4. JSON Schema Validation check
        try:
            parsed_data = json.loads(raw_text)
            response_schema.model_validate(parsed_data)
        except Exception as e:
            validation_attempts += 1
            validation_error_feedback = f"Error: The response is not a valid JSON conforming to the requested schema. Please output a valid JSON. Details: {e}"
            logger.warning(f"Self-correction loop triggered (attempt {validation_attempts}) due to JSON parsing/schema error: {e}")
            continue

        # 5. Business logic validation
        validator_fn = VALIDATOR_MAP.get(conv_type)
        valid = True
        val_msg = ""
        if validator_fn:
            valid, val_msg = validator_fn(parsed_data)

        if valid:
            # Check language on key textual fields in parsed_data
            lang_fields = ["question_text", "optimized_resume_markdown", "why_matches", "cover_letter", "networking_message", "response_text"]
            for field in lang_fields:
                if field in parsed_data and parsed_data[field]:
                    lang_valid, lang_msg = validate_response_language(parsed_data[field], language)
                    if not lang_valid:
                        valid = False
                        val_msg = lang_msg
                        break

        if not valid:
            validation_attempts += 1
            validation_error_feedback = f"Validation Error: {val_msg} Please correct this and regenerate the response."
            logger.warning(f"Self-correction loop triggered (attempt {validation_attempts}) due to validation failure: {val_msg}")
            # Loop back to let the agent regenerate
            continue

        # All validations passed
        final_text = raw_text
        break

    # If max validation attempts reached and still invalid, fall back to mock
    if not final_text:
        logger.error(f"Failed to obtain valid structured output after {max_validation_attempts} attempts. Falling back.")
        log_risk(telegram_id, "hallucination", "Failed to generate valid structured response after self-correction retries.", "medium")
        # Generate clean mock output
        provider = "mock"
        # Run turn again in mock mode to populate final_text
        return run_agent_turn(telegram_id, conversation_id, user_message, system_instruction, provider="mock")

    # 6. Output Guardrails
    is_output_safe, safe_or_filtered_text = check_output_safety(final_text, language)
    if not is_output_safe:
        guardrail_status = "failed_output"
        final_text = json.dumps({
            "response_text": safe_or_filtered_text,
            "suggested_next_steps": []
        } if conv_type in ["advice", "skills"] else {
            "question_text": safe_or_filtered_text,
            "is_completed": True
        }, ensure_ascii=False)
        log_risk(telegram_id, "hallucination", "Output guardrails blocked unsafe system instruction leakage.", "high")

    # 7. Record telemetries and save final response to database
    latency_ms = int((time.time() - start_time) * 1000)

    # Insert/Update the agent's message in database with telemetry
    if 'agent_msg_id' in locals() and agent_msg_id:
        update_message_telemetry(
            message_id=agent_msg_id,
            content=final_text,
            latency_ms=latency_ms,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            validation_attempts=validation_attempts,
            guardrail_status=guardrail_status
        )
    else:
        new_msg_id = add_message(conversation_id, "agent", final_text)
        update_message_telemetry(
            message_id=new_msg_id,
            content=final_text,
            latency_ms=latency_ms,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            validation_attempts=validation_attempts,
            guardrail_status=guardrail_status
        )

    return final_text
