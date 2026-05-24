"""
Multilingual support for Career AI Assistant.
Primary: Uzbek (uz), Secondary: Russian (ru), English (en)
"""

TRANSLATIONS = {
    # --- Welcome & Start ---
    "welcome": {
        "uz": (
            "👋 Assalomu alaykum! Men — *hired.uz*, "
            "universitet karyera markazining sun'iy intellekt yordamchisiman.\n\n"
            "Men sizga quyidagilarda yordam bera olaman:\n"
            "📋 Ko'nikmalaringizni baholash (Skill Passport)\n"
            "📝 ATS-optimized rezyume yaratish (Resume Optimizer)\n"
            "💼 Mos vakansiyalarni topish (Smart Vacancies)\n\n"
            "Tilni tanlang / Выберите язык / Choose language:"
        ),
        "ru": (
            "👋 Здравствуйте! Я — *hired.uz*, "
            "AI-помощник карьерного центра университета.\n\n"
            "Я могу помочь вам с:\n"
            "📋 Оценка навыков (Skill Passport)\n"
            "📝 Создание резюме под ATS (Resume Optimizer)\n"
            "💼 Подбор подходящих вакансий (Smart Vacancies)\n\n"
            "Tilni tanlang / Выберите язык / Choose language:"
        ),
        "en": (
            "👋 Hello! I'm *hired.uz*, "
            "your university career center AI helper.\n\n"
            "I can help you with:\n"
            "📋 Skill assessment (Skill Passport)\n"
            "📝 ATS-optimized resume building (Resume Optimizer)\n"
            "💼 Matching vacancies (Smart Vacancies)\n\n"
            "Tilni tanlang / Выберите язык / Choose language:"
        ),
    },

    # --- Main Menu ---
    "main_menu": {
        "uz": "📌 *Asosiy menyu*\nQuyidagi xizmatlardan birini tanlang:",
        "ru": "📌 *Главное меню*\nВыберите один из сервисов:",
        "en": "📌 *Main Menu*\nChoose a service:",
    },

    # --- Button Labels ---
    "btn_skill_passport": {
        "uz": "📋 Skill Passport",
        "ru": "📋 Skill Passport",
        "en": "📋 Skill Passport",
    },
    "btn_resume": {
        "uz": "📝 Rezyume yaratish",
        "ru": "📝 Создать резюме",
        "en": "📝 Build Resume",
    },
    "btn_interview": {
        "uz": "🎤 Intervyu mashqi",
        "ru": "🎤 Практика интервью",
        "en": "🎤 Interview Practice",
    },
    "btn_vacancies": {
        "uz": "💼 Vakansiyalar",
        "ru": "💼 Вакансии",
        "en": "💼 Vacancies",
    },
    "btn_career_advice": {
        "uz": "📚 Karyera maslahat",
        "ru": "📚 Карьерный совет",
        "en": "📚 Career Advice",
    },
    "btn_my_profile": {
        "uz": "👤 Mening profilim",
        "ru": "👤 Мой профиль",
        "en": "👤 My Profile",
    },
    "btn_language": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Сменить язык",
        "en": "🌐 Change Language",
    },
    "btn_quiz": {
        "uz": "📝 Quiz & Homework",
        "ru": "📝 Викторина и ДЗ",
        "en": "📝 Quiz & Homework",
    },
    "btn_back": {
        "uz": "⬅️ Orqaga",
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
    },
    "btn_main_menu": {
        "uz": "🏠 Asosiy menyu",
        "ru": "🏠 Главное меню",
        "en": "🏠 Main Menu",
    },

    # --- Profile Setup ---
    "ask_name": {
        "uz": "Ismingizni kiriting (Ism Familiya):",
        "ru": "Введите ваше имя (Имя Фамилия):",
        "en": "Enter your name (First Last):",
    },
    "ask_university": {
        "uz": "Qaysi universitetda o'qiysiz?",
        "ru": "В каком университете вы учитесь?",
        "en": "What university do you attend?",
    },
    "ask_faculty": {
        "uz": "Fakultet/yo'nalishingiz nomi?",
        "ru": "Название факультета/направления?",
        "en": "Your faculty/major?",
    },
    "ask_year": {
        "uz": "Nechanchi kursda o'qiysiz? (1-4 yoki magistratura)",
        "ru": "На каком курсе учитесь? (1-4 или магистратура)",
        "en": "What year are you in? (1-4 or master's)",
    },
    "ask_target_role": {
        "uz": (
            "Qaysi yo'nalishda ishlashni xohlaysiz?\n\n"
            "1️⃣ Frontend Developer\n"
            "2️⃣ Backend Developer\n"
            "3️⃣ Full-stack Developer\n"
            "4️⃣ Mobile Developer\n"
            "5️⃣ Data Analyst\n"
            "6️⃣ AI/ML Engineer\n"
            "7️⃣ DevOps Engineer\n"
            "8️⃣ UX/UI Designer\n"
            "9️⃣ Project Manager\n"
            "🔟 Boshqa (yozing)"
        ),
        "ru": (
            "В каком направлении хотите работать?\n\n"
            "1️⃣ Frontend Developer\n"
            "2️⃣ Backend Developer\n"
            "3️⃣ Full-stack Developer\n"
            "4️⃣ Mobile Developer\n"
            "5️⃣ Data Analyst\n"
            "6️⃣ AI/ML Engineer\n"
            "7️⃣ DevOps Engineer\n"
            "8️⃣ UX/UI Designer\n"
            "9️⃣ Project Manager\n"
            "🔟 Другое (напишите)"
        ),
        "en": (
            "What role are you targeting?\n\n"
            "1️⃣ Frontend Developer\n"
            "2️⃣ Backend Developer\n"
            "3️⃣ Full-stack Developer\n"
            "4️⃣ Mobile Developer\n"
            "5️⃣ Data Analyst\n"
            "6️⃣ AI/ML Engineer\n"
            "7️⃣ DevOps Engineer\n"
            "8️⃣ UX/UI Designer\n"
            "9️⃣ Project Manager\n"
            "🔟 Other (type it)"
        ),
    },
    "profile_saved": {
        "uz": "✅ Profilingiz saqlandi! Endi asosiy menyudan xizmatlardan foydalanishingiz mumkin.",
        "ru": "✅ Ваш профиль сохранён! Теперь можете пользоваться сервисами из главного меню.",
        "en": "✅ Profile saved! You can now use services from the main menu.",
    },

    # --- Student ID & Phone Registration ---
    "ask_student_id": {
        "uz": "🆔 Talaba ID raqamingizni kiriting (6 ta raqam, masalan: 220019):",
        "ru": "🆔 Введите ваш студенческий ID (6 цифр, например: 220019):",
        "en": "🆔 Enter your 6-digit student ID (e.g. 220019):",
    },
    "invalid_student_id": {
        "uz": "❌ Noto'g'ri format. Talaba ID 6 ta raqamdan iborat bo'lishi kerak (masalan: 220019).",
        "ru": "❌ Неверный формат. Студенческий ID должен содержать ровно 6 цифр (например: 220019).",
        "en": "❌ Invalid format. Student ID must be exactly 6 digits (e.g. 220019).",
    },
    "student_id_taken": {
        "uz": "⚠️ Bu talaba ID allaqachon ro'yxatdan o'tgan. Agar bu sizning ID bo'lsa, karyera markaziga murojaat qiling.",
        "ru": "⚠️ Этот студенческий ID уже зарегистрирован. Если это ваш ID, обратитесь в карьерный центр.",
        "en": "⚠️ This student ID is already registered. Contact the career center if this is your ID.",
    },
    "ask_phone": {
        "uz": (
            "📱 Telefon raqamingizni ulashing.\n\n"
            "Quyidagi \"📱 Raqamni ulashish\" tugmasini bosing.\n"
            "Bu xavfsiz va faqat sizning haqiqiy raqamingiz qabul qilinadi."
        ),
        "ru": (
            "📱 Поделитесь вашим номером телефона.\n\n"
            "Нажмите кнопку \"📱 Поделиться номером\" ниже.\n"
            "Это безопасно — принимается только ваш реальный номер."
        ),
        "en": (
            "📱 Share your phone number.\n\n"
            "Press the \"📱 Share Number\" button below.\n"
            "This is secure — only your real number will be accepted."
        ),
    },
    "btn_share_phone": {
        "uz": "📱 Raqamni ulashish",
        "ru": "📱 Поделиться номером",
        "en": "📱 Share Number",
    },
    "btn_skip_phone": {
        "uz": "⏭ Keyinroq",
        "ru": "⏭ Позже",
        "en": "⏭ Skip for now",
    },
    "phone_verified": {
        "uz": "✅ Telefon raqamingiz tasdiqlandi!",
        "ru": "✅ Ваш номер телефона подтверждён!",
        "en": "✅ Phone number verified!",
    },
    "phone_spoofed": {
        "uz": "⚠️ Iltimos, o'zingizning telefon raqamingizni ulashish uchun tugmani bosing.",
        "ru": "⚠️ Пожалуйста, используйте кнопку для отправки ВАШЕГО номера.",
        "en": "⚠️ Please use the button to share YOUR phone number.",
    },
    "phone_taken": {
        "uz": "⚠️ Bu telefon raqami allaqachon ro'yxatdan o'tgan.",
        "ru": "⚠️ Этот номер телефона уже зарегистрирован.",
        "en": "⚠️ This phone number is already registered.",
    },
    "profile_incomplete": {
        "uz": (
            "👋 Qaytib kelganingizdan xursandmiz! Profilingiz to'liq emas.\n"
            "Iltimos, talaba ID va telefon raqamingizni qo'shing."
        ),
        "ru": (
            "👋 Рады вашему возвращению! Ваш профиль неполный.\n"
            "Пожалуйста, добавьте студенческий ID и номер телефона."
        ),
        "en": (
            "👋 Welcome back! Your profile is incomplete.\n"
            "Please add your student ID and phone number."
        ),
    },

    # --- Skill Passport ---
    "skill_passport_intro": {
        "uz": (
            "📋 *Skill Passport — Ko'nikmalar Baholash*\n\n"
            "Men sizga bir nechta savol beraman va javoblaringiz asosida "
            "ko'nikmalaringizni baholab, qaysi sohalarni rivojlantirish kerakligini aytaman.\n\n"
            "Tayyor bo'lsangiz, \"Boshlash\" tugmasini bosing."
        ),
        "ru": (
            "📋 *Skill Passport — Оценка навыков*\n\n"
            "Я задам вам несколько вопросов и на основе ваших ответов "
            "оценю ваши навыки и подскажу, что стоит развивать.\n\n"
            "Когда будете готовы, нажмите \"Начать\"."
        ),
        "en": (
            "📋 *Skill Passport — Skill Assessment*\n\n"
            "I'll ask you several questions and based on your answers, "
            "I'll assess your skills and suggest areas for improvement.\n\n"
            "When ready, press \"Start\"."
        ),
    },
    "btn_start": {
        "uz": "🚀 Boshlash",
        "ru": "🚀 Начать",
        "en": "🚀 Start",
    },
    "skill_q_technologies": {
        "uz": "Qaysi dasturlash tillari va texnologiyalarni bilasiz? (vergul bilan ajrating)\n\nMasalan: Python, JavaScript, React, Docker, PostgreSQL",
        "ru": "Какие языки программирования и технологии вы знаете? (через запятую)\n\nНапример: Python, JavaScript, React, Docker, PostgreSQL",
        "en": "What programming languages and technologies do you know? (comma-separated)\n\nExample: Python, JavaScript, React, Docker, PostgreSQL",
    },
    "skill_q_projects": {
        "uz": "Qanday loyihalar qilgansiz? (qisqacha tasvirlang, har birini yangi qatordan)\n\nMasalan:\n- E-commerce sayt (React + Node.js)\n- Telegram bot (Python)",
        "ru": "Какие проекты вы делали? (кратко опишите, каждый с новой строки)\n\nНапример:\n- E-commerce сайт (React + Node.js)\n- Telegram бот (Python)",
        "en": "What projects have you built? (briefly describe, each on a new line)\n\nExample:\n- E-commerce site (React + Node.js)\n- Telegram bot (Python)",
    },
    "skill_q_experience": {
        "uz": "Amaliy tajribangiz bormi? (stajirovka, freelance, ish)\nAgar bo'lmasa \"Yo'q\" deb yozing.",
        "ru": "Есть ли у вас практический опыт? (стажировка, фриланс, работа)\nЕсли нет, напишите \"Нет\".",
        "en": "Do you have any practical experience? (internship, freelance, job)\nIf none, type \"None\".",
    },
    "skill_q_english": {
        "uz": "Ingliz tilini qay darajada bilasiz?\n\n1️⃣ Beginner (A1-A2)\n2️⃣ Intermediate (B1-B2)\n3️⃣ Advanced (C1-C2)",
        "ru": "Какой у вас уровень английского?\n\n1️⃣ Beginner (A1-A2)\n2️⃣ Intermediate (B1-B2)\n3️⃣ Advanced (C1-C2)",
        "en": "What is your English level?\n\n1️⃣ Beginner (A1-A2)\n2️⃣ Intermediate (B1-B2)\n3️⃣ Advanced (C1-C2)",
    },
    "skill_analyzing": {
        "uz": "🔄 Ko'nikmalaringizni tahlil qilyapman...",
        "ru": "🔄 Анализирую ваши навыки...",
        "en": "🔄 Analyzing your skills...",
    },

    # --- Resume ---
    "resume_intro": {
        "uz": (
            "📝 *ATS-Optimized Rezyume Yaratish*\n\n"
            "Men sizning profilingiz asosida ATS tizimlaridan o'ta oladigan "
            "professional rezyume yaratib beraman.\n\n"
            "Iltimos, quyidagi ma'lumotlarni kiriting."
        ),
        "ru": (
            "📝 *Создание резюме под ATS*\n\n"
            "Я создам профессиональное резюме на основе вашего профиля, "
            "которое пройдёт ATS-системы.\n\n"
            "Пожалуйста, заполните следующие данные."
        ),
        "en": (
            "📝 *ATS-Optimized Resume Builder*\n\n"
            "I'll create a professional ATS-friendly resume "
            "based on your profile.\n\n"
            "Please provide the following details."
        ),
    },
    "resume_ask_target": {
        "uz": "Qaysi vakansiyaga rezyume yozyapsiz? (masalan: Junior Python Developer at Google)",
        "ru": "На какую вакансию пишете резюме? (например: Junior Python Developer at Google)",
        "en": "What position is this resume for? (e.g.: Junior Python Developer at Google)",
    },
    "resume_ask_experience": {
        "uz": "Ish tajribangizni tasvirlang (agar bo'lmasa \"Yo'q\" yozing):\nFormat: Kompaniya | Lavozim | Davr | Asosiy yutuqlar",
        "ru": "Опишите ваш опыт работы (если нет, напишите \"Нет\"):\nФормат: Компания | Должность | Период | Основные достижения",
        "en": "Describe your work experience (if none, type \"None\"):\nFormat: Company | Position | Period | Key achievements",
    },
    "resume_generating": {
        "uz": "🔄 Rezyumengizni tayyorlayman...",
        "ru": "🔄 Готовлю ваше резюме...",
        "en": "🔄 Generating your resume...",
    },

    # --- Interview ---
    "interview_intro": {
        "uz": (
            "🎤 *Intervyu Simulyatsiyasi*\n\n"
            "Men sizga texnik va xulq-atvor savollar beraman va "
            "javoblaringizni STAR metodi asosida baholayman.\n\n"
            "Savol turini tanlang:"
        ),
        "ru": (
            "🎤 *Симуляция интервью*\n\n"
            "Я буду задавать вам технические и поведенческие вопросы, "
            "оценивая ваши ответы по методу STAR.\n\n"
            "Выберите тип вопросов:"
        ),
        "en": (
            "🎤 *Interview Simulation*\n\n"
            "I'll ask you technical and behavioral questions, "
            "evaluating your answers using the STAR method.\n\n"
            "Choose question type:"
        ),
    },
    "btn_technical": {
        "uz": "💻 Texnik savollar",
        "ru": "💻 Технические вопросы",
        "en": "💻 Technical Questions",
    },
    "btn_behavioral": {
        "uz": "🤝 Xulq-atvor savollari",
        "ru": "🤝 Поведенческие вопросы",
        "en": "🤝 Behavioral Questions",
    },
    "btn_mixed": {
        "uz": "🎯 Aralash",
        "ru": "🎯 Смешанные",
        "en": "🎯 Mixed",
    },
    "interview_answer_prompt": {
        "uz": "Javobingizni yozing:",
        "ru": "Напишите ваш ответ:",
        "en": "Type your answer:",
    },
    "interview_evaluating": {
        "uz": "🔄 Javobingizni baholayman...",
        "ru": "🔄 Оцениваю ваш ответ...",
        "en": "🔄 Evaluating your answer...",
    },
    "btn_next_question": {
        "uz": "➡️ Keyingi savol",
        "ru": "➡️ Следующий вопрос",
        "en": "➡️ Next Question",
    },
    "btn_end_interview": {
        "uz": "🏁 Yakunlash",
        "ru": "🏁 Завершить",
        "en": "🏁 End Interview",
    },

    # --- Vacancies ---
    "vacancies_intro": {
        "uz": (
            "💼 *Vakansiyalar va Stajirovkalar*\n\n"
            "Sizning profilingizga mos vakansiyalar:"
        ),
        "ru": (
            "💼 *Вакансии и Стажировки*\n\n"
            "Вакансии, подходящие вашему профилю:"
        ),
        "en": (
            "💼 *Vacancies & Internships*\n\n"
            "Vacancies matching your profile:"
        ),
    },
    "no_vacancies": {
        "uz": "Hozircha sizning profilingizga mos vakansiya topilmadi. Tez orada yangi vakansiyalar qo'shiladi!",
        "ru": "Пока не найдено вакансий, подходящих вашему профилю. Скоро добавятся новые!",
        "en": "No matching vacancies found yet. New ones will be added soon!",
    },

    # --- Career Advice ---
    "career_advice_intro": {
        "uz": "📚 Karyera haqida savolingizni yozing va men karyera bazasidagi ma'lumotlar asosida javob beraman:",
        "ru": "📚 Задайте вопрос о карьере, и я отвечу на основе нашей базы знаний:",
        "en": "📚 Ask me any career question and I'll answer based on our knowledge base:",
    },

    # --- Admin ---
    "admin_stats": {
        "uz": "📊 *Admin Statistikalar*",
        "ru": "📊 *Статистика Админ*",
        "en": "📊 *Admin Statistics*",
    },
    "not_admin": {
        "uz": "⛔ Sizda admin huquqlari yo'q.",
        "ru": "⛔ У вас нет прав администратора.",
        "en": "⛔ You don't have admin permissions.",
    },

    # --- General ---
    "error_generic": {
        "uz": "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki /start buyrug'ini bering.",
        "ru": "❌ Произошла ошибка. Пожалуйста, попробуйте снова или введите /start.",
        "en": "❌ An error occurred. Please try again or type /start.",
    },
    "processing": {
        "uz": "⏳ Qayta ishlanmoqda...",
        "ru": "⏳ Обрабатывается...",
        "en": "⏳ Processing...",
    },
    "language_changed": {
        "uz": "✅ Til o'zgartirildi: O'zbek tili",
        "ru": "✅ Язык изменён: Русский",
        "en": "✅ Language changed: English",
    },
    # --- LinkedIn Profile Helper ---
    "btn_linkedin": {
        "uz": "🌐 LinkedIn Profil",
        "ru": "🌐 LinkedIn Профиль",
        "en": "🌐 LinkedIn Profile",
    },
    "linkedin_intro": {
        "uz": (
            "🌐 *LinkedIn Profil Yordamchisi*\n\n"
            "LinkedIn tarmog'ida professional brendingizni yaratish uchun xizmatni tanlang:"
        ),
        "ru": (
            "🌐 *Помощник LinkedIn*\n\n"
            "Выберите услугу для создания профессионального бренда в LinkedIn:"
        ),
        "en": (
            "🌐 *LinkedIn Profile Helper*\n\n"
            "Choose a service to build your professional brand on LinkedIn:"
        ),
    },
    "btn_li_bio": {
        "uz": "📝 Bio va Headline",
        "ru": "📝 Био и Заголовок",
        "en": "📝 Bio & Headline",
    },
    "btn_li_outreach": {
        "uz": "🤝 Aloqa xatlari (Outreach)",
        "ru": "🤝 Сообщения рекрутерам",
        "en": "🤝 Outreach Messages",
    },
    "btn_li_posts": {
        "uz": "✍️ Post g'oyalari",
        "ru": "✍️ Идеи для постов",
        "en": "✍️ Post Ideas",
    },
    "li_ask_bio_details": {
        "uz": "Bio va Headline'da alohida ta'kidlashni istagan yutuq yoki loyihalaringiz bormi? (Bo'lmasa 'Yo'q' deb yozing)",
        "ru": "Есть ли проекты или достижения, которые вы хотите выделить в Био? (Если нет, напишите 'Нет')",
        "en": "Are there any specific achievements or projects you want to highlight in your Bio? (If none, type 'None')",
    },
    "li_ask_outreach_details": {
        "uz": "Target kompaniya va lavozimni kiriting:\n(Masalan: Uzum Tech, Junior Backend Developer)",
        "ru": "Введите целевую компанию и должность:\n(Например: Epam, Intern Frontend Developer)",
        "en": "Enter target company and position:\n(Example: Google, Junior Data Analyst)",
    },
    "li_generating": {
        "uz": "🔄 LinkedIn ma'lumotlarini tayyorlayapman...",
        "ru": "🔄 Готовлю материалы для LinkedIn...",
        "en": "🔄 Generating LinkedIn materials...",
    },
}

# Role number to name mapping
ROLE_MAP = {
    "1": "Frontend Developer",
    "2": "Backend Developer",
    "3": "Full-stack Developer",
    "4": "Mobile Developer",
    "5": "Data Analyst",
    "6": "AI/ML Engineer",
    "7": "DevOps Engineer",
    "8": "UX/UI Designer",
    "9": "Project Manager",
}


def t(key: str, lang: str = "uz") -> str:
    """Get translated string for a given key and language."""
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("uz", f"[{key}]"))
