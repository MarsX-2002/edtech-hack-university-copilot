"""
Career-specific AI modes for the Career AI Assistant.
Implements stateful custom agent loops for mock interview, self-correcting resume optimizer,
vacancy matchmaking, career advice, and technical quizzes.
"""
import json
from src.rag import call_llm, retrieve_context, career_query
from src.config import DEFAULT_PROVIDER
from src.storage import load_vacancies
from src.agent import run_agent_turn

# ──────────────── Stateful Agentic Upgrades ────────────────

def run_interview_agent_turn(telegram_id: int, conversation_id: int, user_message: str,
                             student_profile: dict, language: str) -> str:
    """Runs a turn in the stateful Mock Interview Simulator."""
    target_role = student_profile.get("target_role", "Developer")
    
    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    system_instruction = f"""Sen professional va talabchan IT intervyuerisan. Talaba bilan "{target_role}" pozitsiyasi uchun mock intervyu o'tkaz.
Javoblarni faqat {lang_instruction} yoz.

Qoidalar:
1. Talabaga intervyu savoli ber (aralash texnik/hard-skills va behavioral/soft-skills).
2. Talabaning javobini diqqat bilan eshitib, keyingi savolni uning javobidan kelib chiqib dynamic ravishda moslashtir (xuddi real suhbatdek).
3. STAR (Situation, Task, Action, Result) metodiga asoslanib qisqa micro-feedback ber, lekin intervyuni davom ettir.
4. Jami 3 ta savol so'ra. Savollar Junior darajasiga mos bo'lsin.
5. Talaba 3-savolga javob bergandan so'ng, suhbatni chiroyli yakunla va to'liq hisobot tuzib ber:
   - 📊 Kuchli tomonlar
   - ⚠️ Yaxshilash kerak bo'lgan jihatlar
   - STAR tahlili (qaysi qismlarni yaxshi yoki yomon ochib berdi)
   - 🎯 Yakuniy ball (X/10 formatida)
"""
    json_str = run_agent_turn(
        telegram_id=telegram_id,
        conversation_id=conversation_id,
        user_message=user_message,
        system_instruction=system_instruction
    )
    try:
        data = json.loads(json_str)
        parts = []
        if data.get("feedback_on_previous"):
            parts.append(f"💡 *Feedback:* {data['feedback_on_previous']}\n")
        
        parts.append(data.get("question_text", ""))
        
        if data.get("is_completed") or data.get("final_report"):
            report = data.get("final_report")
            if report:
                parts.append("\n📊 *MOCK INTERVIEW HISOBOTI (REPORT)*")
                
                strengths = report.get("strengths", [])
                if strengths:
                    parts.append("\n✅ *Kuchli tomonlar (Strengths):*")
                    for s in strengths:
                        parts.append(f"• {s}")
                        
                improvements = report.get("improvements", [])
                if improvements:
                    parts.append("\n⚠️ *Yaxshilash kerak bo'lgan jihatlar (Areas for Improvement):*")
                    for imp in improvements:
                        parts.append(f"• {imp}")
                
                if report.get("star_analysis"):
                    parts.append(f"\n🎯 *STAR Tahlili (STAR Analysis):*\n{report['star_analysis']}")
                
                parts.append(f"\n🎯 *Yakuniy ball (Final Score):* {report.get('score', 0)}/10")
        
        return "\n".join(parts), data
    except Exception:
        return json_str, {}

def run_resume_agent_turn(telegram_id: int, conversation_id: int, user_message: str,
                          student_profile: dict, language: str) -> str:
    """Runs a turn in the stateful Self-Correcting Resume & ATS Optimizer."""
    target_role = student_profile.get("target_role", "Developer")
    skills = student_profile.get("skills", "N/A")
    uni = student_profile.get("university", "N/A")
    faculty = student_profile.get("faculty", "N/A")
    year = student_profile.get("year", "N/A")
    name = student_profile.get("name", "N/A")
    phone = student_profile.get("phone_number", "N/A")
    telegram_username = student_profile.get("telegram_username", "")

    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    system_instruction = f"""Sen professional rezyume maslahatchisi va ATS (Applicant Tracking System) optimizatorisan.
Talabaga uning profiliga ko'ra (Ism: {name}, Tel: {phone}, Telegram: @{telegram_username if telegram_username else 'N/A'}, Universitet: {uni}, Fakultet: {faculty}, Kurs: {year}, Ko'nikmalar: {skills}) va maqsadi ({target_role}) uchun mukammal rezyume loyihasini tayyorlashga yordam ber.
Javoblarni faqat {lang_instruction} yoz.

Qoidalar:
1. Talabaning kiritgan ish tajribasi va loyihalarini olgach, `check_resume_ats` tool'ini chaqirib ATS score'ni tekshir.
2. Agar ATS score 75 dan past bo'lsa yoki target role uchun zarur bo'lgan kalit so'zlar (keywords) etishmayotgan bo'lsa, rezyume loyihasini avtomatik ravishda to'ldir va optimallashtir (self-correcting agent loop).
3. Rezyumeni chiroyli Telegram markdown formatida ber (*bold* sarlavhalar, • bullet nuqtalar).
4. Rezyume loyihasi ostida `check_resume_ats` natijalarini (ATS Score: X/100) va critical recommendations ko'rsatib ber.
5. Rezyume oxirida "Fields to fill: [Email], [Address], [LinkedIn]" qismini to'ldirilishi kerak bo'lgan boshqa maydonlar ro'yxati sifatida qo'sh. Talabaning ismi, telefoni, telegram useri, universiteti va ko'nikmalarini rezyume loyihasi ichiga avtomatik ravishda to'g'ri joylashtirganing sababli ularni "Fields to fill" qatorida qayta so'rama.
"""
    json_str = run_agent_turn(
        telegram_id=telegram_id,
        conversation_id=conversation_id,
        user_message=user_message,
        system_instruction=system_instruction
    )
    try:
        data = json.loads(json_str)
        parts = []
        parts.append(data.get("optimized_resume_markdown", ""))
        parts.append("\n📊 *ATS MUVOFIQLIK TAHLILI (ATS AUDIT)*")
        parts.append(f"📈 *ATS Score:* {data.get('ats_score', 0)}/100")
        
        missing_secs = data.get("missing_sections", [])
        if missing_secs:
            parts.append(f"\n🔍 *Etishmayotgan bo'limlar (Missing Sections):*\n" + "\n".join([f"• {s}" for s in missing_secs]))
            
        missing_kws = data.get("missing_keywords", [])
        if missing_kws:
            parts.append(f"\n🔑 *Etishmayotgan kalit so'zlar (Missing Keywords):*\n" + ", ".join(missing_kws))
            
        critical_recs = data.get("critical_recommendations", [])
        if critical_recs:
            parts.append(f"\n⚠️ *Kritik Tavsiyalar (Critical Recommendations):*\n" + "\n".join([f"• {r}" for r in critical_recs]))
            
        return "\n".join(parts)
    except Exception:
        return json_str

def run_vacancy_agent_turn(telegram_id: int, conversation_id: int, user_message: str,
                           student_profile: dict, language: str) -> str:
    """Runs a turn in the stateful Vacancy Matchmaker & Cover Letter Copilot."""
    target_role = student_profile.get("target_role", "Developer")
    skills = student_profile.get("skills", "N/A")

    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    system_instruction = f"""Sen professional IT recruiter va karyera matchmaking agentisan.
Talabaning maqsadli yo'nalishi ({target_role}) va ko'nikmalariga ({skills}) eng mos keladigan vakansiyalarni aniqla.
Javoblarni faqat {lang_instruction} yoz.

Qoidalar:
1. `search_vacancies` tool'idan foydalanib bazadagi mos vakansiyalarni qidir.
2. Topilgan vakansiya talablarini talabaning skillari ({skills}) bilan taqqosla.
3. Har bir mos vakansiya uchun nega aynan shu vakansiya talabaga to'g'ri kelishini (match score: X%) va mavjud ko'nikmalar farqini (skill gaps) tushuntirib ber.
4. Tanlangan vakansiya uchun talabaga professional va ta'sirchan Cover Letter (muqova xati) va kompaniya vakili bilan bog'lanish uchun tayyor networking chat xabarini yozib ber.
"""
    json_str = run_agent_turn(
        telegram_id=telegram_id,
        conversation_id=conversation_id,
        user_message=user_message,
        system_instruction=system_instruction
    )
    try:
        data = json.loads(json_str)
        matches = data.get("matches", [])
        if not matches:
            if language == "ru":
                return "😔 К сожалению, подходящих вакансий не найдено."
            elif language == "en":
                return "😔 Sorry, no matching vacancies were found."
            return "😔 Afsuski, mos keladigan vakansiyalar topilmadi."
            
        parts = []
        parts.append("💼 *MOS KELUVCHI VAKANSIYALAR (MATCHED VACANCIES)*\n")
        
        for idx, match in enumerate(matches, 1):
            parts.append(f"{idx}️⃣ *{match.get('vacancy_title')}* - *{match.get('company')}*")
            parts.append(f"📈 *Moslik darajasi (Match Score):* {match.get('match_score')}%")
            parts.append(f"🎯 *Nega mos keladi:* {match.get('why_matches')}")
            
            gaps = match.get("skill_gaps", [])
            if gaps:
                parts.append(f"⚠️ *Skill Gaps:* {', '.join(gaps)}")
                
            parts.append(f"\n✉️ *Cover Letter (Muqova xati):*\n{match.get('cover_letter')}")
            parts.append(f"\n💬 *Networking Xabari (Networking Message):*\n`{match.get('networking_message')}`")
            parts.append("\n" + "─"*20 + "\n")
            
        return "\n".join(parts)
    except Exception:
        return json_str

def run_quiz_agent_turn(telegram_id: int, conversation_id: int, user_message: str,
                        student_profile: dict, language: str) -> str:
    """Runs a turn in the stateful Dynamic Quiz & Homework Assessor."""
    target_role = student_profile.get("target_role", "Developer")
    skills = student_profile.get("skills", "N/A")

    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    system_instruction = f"""Sen professional IT mentor va bilim baholovchi agentisan.
Talabaning "{target_role}" yo'nalishi va ko'nikmalari ({skills}) bo'yicha amaliy va nazariy bilimini tekshirish uchun quiz va homework feedback o'tkaz.
Javoblarni faqat {lang_instruction} yoz.

Qoidalar:
1. Talabaning yo'nalishiga mos 3 ta texnik/mantiqiy savoldan iborat quiz tayyorla.
2. Savollarni bittadan ber. Talaba javob bergandan so'ng, keyingi savolga o't.
3. Jami 3 ta savol yakunlangach, uning javoblarini tahlil qil va quyidagi formatda to'liq feedback ber:
   - 📊 Quiz Natijasi: X/3
   - 💡 Xatolar va kamchiliklar tahlili
   - 🎯 Kelgusi safar nimalarga e'tibor qaratish kerakligi
4. Agent loop tugashi bilan uning quiz natijasini bazaga saqla.
"""
    json_str = run_agent_turn(
        telegram_id=telegram_id,
        conversation_id=conversation_id,
        user_message=user_message,
        system_instruction=system_instruction
    )
    try:
        data = json.loads(json_str)
        parts = []
        if data.get("feedback_on_previous"):
            parts.append(f"💡 *Feedback:* {data['feedback_on_previous']}\n")
            
        parts.append(data.get("question_text", ""))
        
        if data.get("is_completed") or data.get("final_report"):
            report = data.get("final_report")
            if report:
                parts.append("\n📊 *QUIZ NATIJALARI (QUIZ RESULTS)*")
                parts.append(f"🏆 *Quiz Natijasi:* {report.get('score', 0)}/3")
                
                if report.get("quiz_topic"):
                    parts.append(f"📚 *Quiz Mavzusi (Topic):* {report['quiz_topic']}")
                
                if report.get("errors_analysis"):
                    parts.append(f"\n💡 *Xatolar va kamchiliklar tahlili (Error Analysis):*\n{report['errors_analysis']}")
                    
                if report.get("future_recommendations"):
                    parts.append(f"\n🎯 *Kelgusi safar tavsiyalar (Recommendations):*\n{report['future_recommendations']}")
                    
        return "\n".join(parts), data
    except Exception:
        return json_str, {}

# ──────────────── Static Fallbacks & Helpers (Safe Compatibility) ────────────────

def assess_skills(student_profile: dict, skill_data: dict, language: str = "uz",
                  provider: str = None) -> str:
    """Analyze student skills and provide gap analysis for their target role."""
    if provider is None:
        provider = DEFAULT_PROVIDER
    target_role = student_profile.get("target_role", "Developer")
    chunks = retrieve_context(f"{target_role} skill requirements", provider=provider)
    context_str = "\n".join([c["text"] for c in chunks]) if chunks else ""
    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    prompt = f"""Sen professional karyera maslahatchisisan. Talabaning ko'nikmalarini tahlil qilib, 
"{target_role}" pozitsiyasi uchun batafsil Skill Passport hisoboti tuzib ber.

Talaba profili:
- Ism: {student_profile.get('name', 'N/A')}
- Universitet: {student_profile.get('university', 'N/A')}
- Yo'nalish: {student_profile.get('faculty', 'N/A')}
- Kurs: {student_profile.get('year', 'N/A')}
- Maqsad: {target_role}

Talaba ko'rsatgan ko'nikmalar:
- Texnologiyalar: {skill_data.get('technologies', 'N/A')}
- Loyihalar: {skill_data.get('projects', 'N/A')}
- Tajriba: {skill_data.get('experience', 'N/A')}
- Ingliz tili: {skill_data.get('english_level', 'N/A')}

{target_role} uchun talab qilinadigan ko'nikmalar (bilim bazasidan):
{context_str}

Quyidagi formatda hisobot tuzib ber ({lang_instruction}):

📊 *SKILL PASSPORT HISOBOTI*

✅ *Kuchli tomonlar:*
(talabaning mavjud ko'nikmalari orasidan target role uchun mos kelganlarini ro'yxatla)

⚠️ *Rivojlantirish kerak (Skill Gap):*
(talabada yo'q lekin target role uchun zarur bo'lgan ko'nikmalar)

📚 *O'rganish Rejasi (3-6 oy):*
(aniq qadamlar: qaysi texnologiya, qaysi resurs, qancha vaqt)

💡 *Darhol qilish kerak bo'lgan 3 qadam:*
(eng birinchi navbatda nima qilish kerak)

🎯 *Umumiy Tayyorlik Darajasi:* X/10
"""
    try:
        return call_llm(prompt, provider=provider, temperature=0.3)
    except Exception:
        return _mock_skill_assessment(student_profile, skill_data, language)

def _mock_skill_assessment(profile: dict, skill_data: dict, language: str) -> str:
    role = profile.get("target_role", "Developer")
    techs = skill_data.get("technologies", "")
    if language == "ru":
        return f"📊 *SKILL PASSPORT*\n\nЦелевая роль: {role}\nВаши навыки: {techs}\n\n✅ *Сильные стороны:* Базовые навыки есть\n⚠️ *Нужно развить:* Практический опыт, портфолио\n📚 *План:* Создайте 2-3 проекта для портфолио\n🎯 *Готовность:* 5/10"
    elif language == "en":
        return f"📊 *SKILL PASSPORT*\n\nTarget role: {role}\nYour skills: {techs}\n\n✅ *Strengths:* Foundation skills present\n⚠️ *Gaps:* Practical experience, portfolio\n📚 *Plan:* Build 2-3 portfolio projects\n🎯 *Readiness:* 5/10"
    return f"📊 *SKILL PASSPORT*\n\nMaqsad: {role}\nKo'nikmalaringiz: {techs}\n\n✅ *Kuchli tomonlar:* Asosiy ko'nikmalar bor\n⚠️ *Rivojlantirish kerak:* Amaliy tajriba, portfolio\n📚 *Reja:* 2-3 ta portfolio loyiha qiling\n🎯 *Tayyorlik:* 5/10"

def generate_resume(student_profile: dict, target_position: str, experience_text: str,
                    language: str = "uz", provider: str = None) -> str:
    if provider is None:
        provider = DEFAULT_PROVIDER
    chunks = retrieve_context("ATS resume template format tips", provider=provider)
    context_str = "\n".join([c["text"] for c in chunks]) if chunks else ""
    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    phone = student_profile.get("phone_number", "N/A")
    telegram_username = student_profile.get("telegram_username", "")
    telegram = f"@{telegram_username}" if telegram_username else "N/A"
    skills = student_profile.get("skills", "N/A")

    prompt = f"""Sen professional rezyume yozuvchisisan. ATS tizimlaridan o'ta oladigan professional rezyume yaratib ber.

Talaba ma'lumotlari:
- Ism: {student_profile.get('name', 'N/A')}
- Telefon: {phone}
- Telegram: {telegram}
- Universitet: {student_profile.get('university', 'N/A')}
- Yo'nalish: {student_profile.get('faculty', 'N/A')}
- Kurs: {student_profile.get('year', 'N/A')}
- Ko'nikmalar: {skills}
- Maqsad pozitsiya: {target_position}
- Ish tajriba: {experience_text}

Rezyume shablonlari va ATS maslahatlar (bilim bazasidan):
{context_str}

Quyidagilarni amalga oshir:
1. Rezyumeni {lang_instruction} yoz
2. ATS-optimized format ishlatib ber (oddiy matn, kalit so'zlar)
3. Target pozitsiya uchun mos kalit so'zlarni qo'sh
4. Professional Summary qismida eng muhim 3-4 ko'nikmani ta'kidla
5. Loyihalar va tajribani raqamlar bilan tasvirla
6. Telegram markdown formatida ber (*bold* qismlar bilan)
7. Talabaning ismi, telefoni, telegram useri va ko'nikmalarini rezyume matnining yuqori/kontakt qismiga avtomatik ravishda to'g'ri joylashtirganing sababli ularni "Fields to fill" qatorida qayta so'rama.
8. Rezyume oxirida to'ldirilishi kerak bo'lgan faqat boshqa maydonlar ro'yxatini (masalan, Email, Address, LinkedIn) "Fields to fill: [Email], [Address], [LinkedIn]" ko'rinishida qo'sh

Tayyor Rezyume:
"""
    try:
        return call_llm(prompt, provider=provider, temperature=0.2)
    except Exception:
        return _mock_resume(student_profile, target_position, language)

def _mock_resume(profile: dict, target: str, language: str) -> str:
    name = profile.get("name", "Student")
    uni = profile.get("university", "University")
    skills = profile.get("skills", "Python, JavaScript")
    phone = profile.get("phone_number", "+998 XX XXX XX XX")
    telegram_username = profile.get("telegram_username", "")
    telegram = f"@{telegram_username}" if telegram_username else "@student"
    return f"*{name}*\n📧 email@example.com | 📱 {phone} | 💬 {telegram}\n\n*Professional Summary*\nMotivated student at {uni} seeking {target} position. \nSkills: {skills}\n\n*Education*\n{uni}\n\n*Skills*\n{skills}\n\nFields to fill: [Email], [Address], [LinkedIn]\n_Iltimos, API kalitini tekshiring va qayta urinib ko'ring._"

def generate_interview_question(target_role: str, question_type: str = "mixed",
                                language: str = "uz", question_number: int = 1,
                                provider: str = None) -> str:
    if provider is None:
        provider = DEFAULT_PROVIDER
    chunks = retrieve_context(f"{target_role} {question_type} interview questions", provider=provider)
    context_str = "\n".join([c["text"] for c in chunks]) if chunks else ""
    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")
    type_map = {"technical": "texnik (hard skills)", "behavioral": "xulq-atvor (behavioral/soft skills)", "mixed": "aralash (texnik va xulq-atvor)"}
    question_type_desc = type_map.get(question_type, "aralash")

    prompt = f"""Sen tajribali IT intervyuerisan. "{target_role}" pozitsiyasi uchun {question_type_desc} intervyu savoli ber.
Bu {question_number}-savol.

Intervyu savollari bazasidan ma'lumot:
{context_str}

Qoidalar:
1. Savolni {lang_instruction} ber
2. Savol amaliy va real intervyularda beriladigan bo'lsin
3. Junior/entry-level darajadagi talaba uchun mos bo'lsin
4. Faqat BITTA savol ber, hech qanday javob yoki hint berma
5. Savol oldidan emoji qo'y: 💻 texnik uchun, 🤝 behavioral uchun

Savol:
"""
    try:
        return call_llm(prompt, provider=provider, temperature=0.7)
    except Exception:
        return _mock_question(target_role, question_type, language, question_number)

def _mock_question(role: str, qtype: str, lang: str, num: int) -> str:
    questions = {
        "technical": [
            "💻 REST API nima va qanday ishlaydi? Misol keltiring.",
            "💻 Git'da branching strategiyasini tushuntiring.",
            "💻 SQL'da JOIN turlarini tushuntiring.",
        ],
        "behavioral": [
            "🤝 Jamoada qiyin vaziyat bo'lganda qanday hal qildingiz? STAR metodi bilan javob bering.",
            "🤝 Eng katta xatoyingiz nima edi va undan nima o'rgandingiz?",
            "🤝 Tight deadline bilan ishlagan tajribangiz haqida aytib bering.",
        ],
    }
    if qtype == "mixed":
        all_q = questions["technical"] + questions["behavioral"]
    else:
        all_q = questions.get(qtype, questions["technical"])
    idx = (num - 1) % len(all_q)
    return all_q[idx]

def evaluate_interview_answer(question: str, answer: str, target_role: str,
                               language: str = "uz", provider: str = None) -> str:
    if provider is None:
        provider = DEFAULT_PROVIDER
    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    prompt = f"""Sen tajribali IT intervyuer va mentorsan. Talabaning intervyu javobini baholash kerak.

Pozitsiya: {target_role}
Savol: {question}
Talabaning javobi: {answer}

Quyidagi formatda baholash ber ({lang_instruction}):

📊 *Baholash:*
*Kuchli tomonlar:* (javobda yaxshi bo'lgan jihatlar)
*Yaxshilash kerak:* (nimani o'zgartirish/qo'shish kerak)
*STAR Metodi bo'yicha:*
- Situation ✅/❌: (vaziyatni tasvirladimi?)
- Task ✅/❌: (vazifani aniqladimi?)
- Action ✅/❌: (harakatlarini tushuntirdimi?)
- Result ✅/❌: (natijani aytdimi?)
*Namuna javob:* (qisqacha ideal javob qanday bo'lishi kerakligini ko'rsatib ber)
*Ball:* X/10
"""
    try:
        return call_llm(prompt, provider=provider, temperature=0.3)
    except Exception:
        if language == "ru":
            return "📊 *Оценка:* Спасибо за ответ! Попробуйте использовать метод STAR для структурирования ответа.\n*Балл:* 5/10"
        elif language == "en":
            return "📊 *Evaluation:* Thank you for your answer! Try using the STAR method to structure your response.\n*Score:* 5/10"
        return "📊 *Baholash:* Javobingiz uchun rahmat! STAR metodidan foydalanib javob berishga harakat qiling.\n*Ball:* 5/10"

def match_vacancies(student_profile: dict) -> list[dict]:
    vacancies = load_vacancies()
    if not vacancies:
        return []
    student_skills = set()
    skills_str = student_profile.get("skills", "")
    if isinstance(skills_str, str):
        student_skills = {s.strip().lower() for s in skills_str.split(",") if s.strip()}
    elif isinstance(skills_str, list):
        student_skills = {s.strip().lower() for s in skills_str if s.strip()}
    target_role = student_profile.get("target_role", "").lower()

    scored = []
    for v in vacancies:
        score = 0
        required = {s.lower() for s in v.get("skills_required", [])}
        overlap = student_skills & required
        if required:
            score += len(overlap) / len(required) * 60
        title_lower = v.get("title", "").lower()
        if target_role and any(word in title_lower for word in target_role.split()):
            score += 30
        if "intern" in title_lower or "junior" in title_lower:
            score += 10
        scored.append((score, v, len(overlap), len(required)))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, vacancy, overlap_count, required_count in scored:
        if score > 0:
            vacancy_copy = dict(vacancy)
            vacancy_copy["match_score"] = round(score)
            vacancy_copy["skills_matched"] = overlap_count
            vacancy_copy["skills_total"] = required_count
            results.append(vacancy_copy)
    return results

def get_career_advice(telegram_id: int, conversation_id: int, user_message: str,
                      student_profile: dict, language: str) -> str:
    """Runs a turn in the stateful Career Advice chatbot."""
    target_role = student_profile.get("target_role", "Developer")
    skills = student_profile.get("skills", "N/A")

    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    system_instruction = f"""Sen professional IT karyera maslahatchisisan.
Talabaning maqsadli yo'nalishi ({target_role}) va ko'nikmalari ({skills}) bo'yicha amaliy karyera maslahati ber.
Talabaga rezyume, intervyu, networking, ish qidirish strategiyasi bo'yicha maslahat bera olasan.
Javoblarni faqat {lang_instruction} yoz.

Qoidalar:
1. Talabaning savoliga aniq va tizimli javob ber (Telegram Markdown formatida).
2. Javob oxirida talaba uchun 2-3 ta foydali keyingi tavsiya etiladigan qadamlarni qo'shib ber.
"""
    json_str = run_agent_turn(
        telegram_id=telegram_id,
        conversation_id=conversation_id,
        user_message=user_message,
        system_instruction=system_instruction
    )
    try:
        data = json.loads(json_str)
        parts = []
        parts.append(data.get("response_text", ""))
        
        steps = data.get("suggested_next_steps", [])
        if steps:
            parts.append("\n📌 *Keyingi tavsiya etiladigan qadamlar (Next Steps):*")
            for step in steps:
                parts.append(f"• {step}")
        return "\n".join(parts)
    except Exception:
        return json_str
