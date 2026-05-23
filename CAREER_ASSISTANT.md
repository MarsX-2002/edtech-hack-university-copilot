Eng mukammal variantda AI agent quyidagi funksiyalarni o'z ichiga oladi:
1. Talabalar uchun shaxsiylashtirilgan yordam (Student-Facing Features)
"Skill Passport" va O'sish Tahlili: Talabaning amaliy ko'nikmalarini (Skill Passport) baholash va tahlil qilish. AI talabaning joriy darajasi bilan u ko'zlayotgan pozitsiya o'rtasidagi farqni (skill gap) aniqlab, qaysi texnologiya yoki soft skill'larni o'rganish kerakligini aytadi.
ATS'ga Mos Rezyume va Profil Yaratish: Talaba kiritgan ma'lumotlar asosida yirik kompaniyalarning ATS (Applicant Tracking System) dasturlaridan o'ta oladigan rezyumelarni generatsiya qilish. Shuningdek, LinkedIn profillari uchun professional "Bio" va postlar yozishda yordam berish.
Interaktiv Suhbat Simulyatori: Ovozli yoki matnli rejimda texnik (hard skills) va xulq-atvor (behavioral) intervyular o'tkazish. Su'niy intellekt xalqaro standartlar asosida savollar beradi, talabaning javoblarini tahlil qiladi va qayerda xato qilgani bo'yicha darhol konstruktiv fidbek beradi.
Ko'p Tillilik va Situatsion Treninglar: Xalqaro hamkorlar va xorijiy kompaniyalar uchun ingliz yoki rus tillarida suhbatlarga tayyorlash. Til to'siqlarini yengish uchun maxsus kasbiy dialog simulyatsiyalari.
2. Karyera Markazi va Tahliliy Boshqaruv (Admin & Dashboard Features)
Avtomatlashtirilgan "Matchmaking": Yirik texnologik ekotizimlar, xalqaro ta'lim idoralari yoki mahalliy hamkorlardan kelib tushgan vakansiyalar/stajirovkalar talablariga eng mos keladigan talabalarni bazadan avtomatik tarzda saralab berish.
Talabalar Faolligini Kuzatish (Predictive Analytics): Karyera markazi rahbariyati uchun maxsus oyna. Qaysi talabalar faol ish qidiryapti, kim suhbatlarning qaysi bosqichidan yiqilyapti va buning asosiy sababi nima ekanligini vizual tarzda ko'rsatib beruvchi tahliliy hisobotlar.
Mehnat Bozori Trendlari: AI doimiy ravishda IT va biznes bozorini tahlil qilib, ayni paytda qaysi ko'nikmalarga (masalan, sun'iy intellekt integratsiyasi, ma'lumotlar tahlili) talab yuqori ekanligini markazga hisobot qilib boradi.
3. Operatsion va Texnik Qulayliklar
Omnichannel (Ko'p platformali) Integratsiya: AI agentni nafaqat veb-saytda, balki talabalar va bitiruvchilar eng ko'p vaqt o'tkazadigan platformalarda — masalan, Telegram kanallar va botlar tizimiga ulash.
Avtomatik Tarmoq (Networking) Takliflari: Karyera yarmarkalari, xakatonlar va forumlarda talabalarga qaysi kompaniya vakillari bilan uchrashish va qanday savollar berish bo'yicha skriptlar tayyorlab berish.
Bunday agent karyera markazining operatsion yukini 70-80% ga kamaytirib, e'tiborni ko'proq yirik hamkorliklar va strategik rivojlanishga qaratish imkonini beradi.

Karyera markazi uchun AI agentning dastlabki versiyasini (MVP) yaratishda eng to'g'ri va tejamkor yo'l — sun'iy intellektni noldan o'qitish (fine-tuning) emas, balki RAG (Retrieval-Augmented Generation) texnologiyasidan foydalanishdir.
RAG usuli sun'iy intellektga markazingizning ichki hujjatlari va joriy vakansiyalarni "uzatib", faqat shu ma'lumotlar asosida aniq va to'g'ri javob berishni ta'minlaydi.
Quyida MVP uchun texnik arxitektura va ma'lumotlar bazasini shakllantirish bo'yicha to'liq yo'riqnoma keltirilgan.
1. MVP Texnik Arxitekturasi
Dastlabki versiya tezkor ishlashi va oson sinovdan o'tkazilishi uchun quyidagi qatlamlardan iborat bo'ladi:
Foydalanuvchi interfeysi (Frontend): Telegram Bot eng qulay va tezkor yechim hisoblanadi (talabalar u yerda doim faol, shuningdek, maxsus karyera kanallaringiz bilan integratsiya qilish oson). Keyinchalik uni universitet portaliga veb-vidjet sifatida qo'shish mumkin.
Asosiy mantiq (Backend): Python (FastAPI yoki Flask) yoki Node.js. Bu qatlam Telegram bot, ma'lumotlar bazasi va AI o'rtasidagi ma'lumotlar almashinuvini boshqaradi.
AI Dvigateli (LLM): OpenAI (GPT-4o), Anthropic (Claude 3.5) yoki Google (Gemini 1.5 Pro) API'lari. Ular matnni tushunish va generatsiya qilish uchun asosiy "miya" vazifasini bajaradi.
Vektorli Ma'lumotlar Bazasi (Vector DB): Pinecone, Qdrant yoki Milvus. RAG tizimi aynan shu yerda ishlaydi. Hujjatlar (vakansiyalar, rezyume shablonlari) raqamli vektorlarga aylantirilib, shu bazada saqlanadi. AI kerakli ma'lumotni shu yerdan soniyaning mingdan bir qismida topib oladi.
Relyatsion Ma'lumotlar Bazasi: PostgreSQL. Talabalarning profillari, ularning "Skill Passport" natijalari, qaysi kursda o'qishi va botdan foydalanish tarixini saqlash uchun.
2. Agentni Qanday Ma'lumotlarda "O'qitish" Kerak?
AI agent aniq ishlashi va mavhum javoblar bermasligi (gallyutsinatsiyaning oldini olish) uchun Vektorli Ma'lumotlar Bazasini quyidagi maxsus ma'lumotlar bilan to'ldirish (indexing) kerak:
A. Talaba va Baholash Ma'lumotlari (Ichki Kontekst)
Skill Passport mezonlari: Har bir yo'nalish (Frontend, Backend, AI va h.k.) bo'yicha talabadan qanday amaliy ko'nikmalar talab qilinishi.
O'quv dasturlari va loyihalar: Universitetda talabalar bajaradigan amaliy loyihalar va ularning qisqacha tavsifi (rezyumega portfel sifatida qo'shish uchun).
B. Mehnat Bozori va Hamkorlar Bazasidan
Real Vakansiyalar: Hamkor kompaniyalarning (masalan, yirik texnologik ekotizimlar yoki banklarning) stajirovka va ish o'rinlari talablari.
Kompaniya profillari: Hamkorlarning korporativ madaniyati, ulardagi ish sharoitlari va intervyu jarayonlari haqida ma'lumotlar (talabani suhbatga tayyorlash uchun).
C. Karyera Markazining "Oltin Qoidalari"
Rezyume va Muqova xati (Cover Letter) shablonlari: ATS dasturlaridan muvaffaqiyatli o'tgan, xalqaro va mahalliy bozor uchun moslashtirilgan namunalar.
Intervyu savollari bazasi: Ham texnik (hard skills), ham xulq-atvorga (behavioral) oid savollar to'plami. Ularga qanday qilib STAR (Situation, Task, Action, Result) usulida javob berish bo'yicha ko'rsatmalar.
3. RAG Qanday Ishlaydi? (Jarayon)
Bu jarayon amalda quyidagicha kechadi:
Talaba so'rovi: "Menga Java Junior pozitsiyasiga rezyume yozishga yordam ber."
Ma'lumot qidirish (Retrieval): Backend dastur Vektorli bazadan Java yo'nalishi bo'yicha Skill Passport mezonlarini va to'g'ri rezyume shablonlarini tortib oladi. Shu bilan birga, PostgreSQL'dan o'sha talabaning qaysi kursda o'qiyotgani va avvalgi yutuqlarini oladi.
Prompt shakllantirish: Tizim LLM'ga (Aiga) shunday yopiq buyruq beradi: "Sen universitet karyera maslahatchisisan. Mana bu rezyume shabloni va mana bu talabaning ma'lumotlari. Faqat shu ma'lumotlarga asoslanib, unga ATS'ga mos rezyume tayyorlab ber."
Javob (Generation): AI to'g'ridan-to'g'ri va shaxsiylashtirilgan tayyor rezyumeni talabaga yuboradi.
Ushbu arxitektura orqali siz katta mablag' sarflab maxsus AI model yaratishdan qochasiz, lekin o'z ma'lumotlaringiz asosida juda aniq ishlaydigan mukammal assistentga ega bo'lasiz.

platforma uzbek tilida ishlashi shart, rus va ingliz tiliga o'tish funksiyasi bo'lishi kerak. qandaydir 