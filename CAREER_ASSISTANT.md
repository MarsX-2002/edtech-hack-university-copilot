# hired.uz — Karyera Markazi va Tasdiqlangan Talabalar Karyera Bozori (Talent Marketplace) 🎓💼

> **Tagline**: from campus to hired.

**hired.uz** — bu universitet karyera markazlari faoliyatini avtomatlashtirish hamda talabalar bilan nufuzli ish beruvchi kompaniyalarni bog'laydigan yagona platformadir. 

Loyiha talabalarning shaxsiy ma'lumotlari va maxfiyligini to'liq himoya qilgan holda, universitetning tasdiqlangan talabalar bazasini (Talent Pool) shakllantiradi va ish beruvchilarga aqlli qidiruv (AI Search) imkoniyatini taqdim etadi.

---

## 💼 Biznes Modeli

Platforma ikki tomonlama tijoriy qiymatga ega:
1. **Universitetlar uchun**: Rezyumelarni avtomatik tekshirish, Skill Passport yaratish, STAR metodologiyasi asosida interaktiv suhbat simulyatsiyasi va mos keladigan vakansiyalarni tavsiya qilish orqali karyera markazi ish hajmini 80% gacha kamaytiradi.
2. **Ish beruvchilar uchun**: Universitet tomonidan tasdiqlangan va saralangan talabalar bazasiga to'g'ridan-to'g'ri va xavfsiz kirish.

---

## 🔒 Maxfiylik va Talabalar Roziligi Tizimi (Data Privacy Moat)

Talabalar ma'lumotlarini ruxsatsiz tarqatish yoki sotish qat'iyan man etiladi. Bog'lanish jarayoni quyidagi ko'p bosqichli ruxsatnomalar asosida amalga oshiriladi:

1. **Talabaning Roziligi (Opt-in)**: Talaba Telegram bot orqali o'z profilini tasdiqlashi va uni qidiruv bazasiga qo'shishga rozilik berishi shart (botdagi `/consent` buyrug'i yoki sozlamalar orqali). Rozilik bermagan talabalar qidiruvda ko'rinmaydi.
2. **Anonymized Cards (Anonim Profil)**: Ish beruvchilar qidiruv davomida talabaning ismi, tajribalari, loyihalari, ta'limi va ko'nikmalarini ko'radi. Biroq, talabaning **telefon raqami**, **Telegram username** va **Student ID** kabi shaxsiy aloqa ma'lumotlari to'liq yashiriladi.
3. **Bog'lanish So'rovi (Introduction Request)**:
   - **Ish beruvchi so'rovi**: Ish beruvchi o'ziga ma'qul kelgan talaba kartasidagi **Request Intro** tugmasini bosadi va taklif qilinayotgan ish yoki stajirovka haqida ma'lumot yozib yuboradi. So'rov holati: `pending_staff_approval`.
   - **Karyera markazi tekshiruvi**: Karyera markazi xodimlari dashboard orqali kelib tushgan so'rovni ko'rib chiqadi. Agar taklif talaba profiliga mos va xavfsiz bo'lsa, xodim so'rovni tasdiqlaydi. So'rov holati: `approved_by_staff`.
   - **Talaba roziligi**: Tizim avtomatik ravishda talabaning Telegram botiga interaktiv tugmali xabar yuboradi: `[ ✅ Ha, ulashish ]` va `[ ❌ Yo'q, rad etish ]`.
   - **Aloqa ochilishi**: Agar talaba **Ha, ulashish** tugmasini bossa, so'rov `completed` holatiga o'tadi va tizim ish beruvchi dashboardida talabaning telefon raqami va Telegram username'ini ochib ko'rsatadi. Har ikki tomonga ulanish haqida xabarnoma boradi.

---

## 🔍 Aqlli Gibrid Qidiruv (Smart Hybrid Search)

Ish beruvchilar uchun talabalarni qidirish tizimi an'anaviy qidiruvdan tubdan farq qiladi va sun'iy intellekt orqali ishlaydi:

* **Tabiiy Tilda So'rovlar (Semantic Search)**: Ish beruvchi qidiruv maydoniga oddiy matn ko'rinishida talab yozishi mumkin. Masalan: *"Python developer, RAG texnologiyasini biladigan va 2 yillik tajribaga ega talaba"*.
* **Gibrid Filtrlash**: Tizim SQL orqali qattiq filtrlarni (maqsadli lavozim, ko'nikmalar ro'yxati, minimum reyting) qo'llaydi va bir vaqtning o'zida ChromaDB orqali profil ma'lumotlarining semantik o'xshashligini hisoblaydi.
* **Tayyorgarlik Reytingi bo'yicha Saralash (Readiness Score)**: Talabalar AI tomonidan 0 dan 100 gacha bo'lgan ball bilan baholanadi va qidiruv natijalarida yuqori ballga ega bo'lgan eng tayyor talabalar birinchi bo'lib ko'rinadi.
* **Tushunarli Moslik Sabablari (AI Match Insights)**: Tizim har bir topilgan talaba kartasida nima sababdan ushbu talaba mos kelganini tushuntirib beradi. Masalan: *"Talabaning profilida Python bo'yicha 2 yillik tajriba va Django loyihalari borligi sababli ushbu so'rovga 95% mos keldi"*.

---

## 🛠️ Loyiha Arxitekturasi va Modullari

Platforma uchta asosiy qismdan tashkil topgan:

1. **Talabalar Telegram Boti (`bot.py`, `src/bot_handlers.py`)**:
   - Rezyume yuklash va matn ko'rinishidagi tajribalarni qabul qilish.
   - **Gemini AI rezyume tahlili (`src/career_modes.py`)**: Yuklangan PDF yoki matnli rezyumeni o'qib, undan tajribalar, loyihalar, ta'lim va ko'nikmalarni JSON formatida ajratib oladi va profiling to'liqligini baholaydi.
   - Profil loyihasini (draft) tasdiqlash va qidiruvga rozilik (consent) boshqaruvi.
   - Ish beruvchilarning bog'lanish so'rovlarini qabul qilish / rad etish.

2. **Backend API Xizmati (`src/api.py`, `src/auth.py`, `src/db.py`)**:
   - SQLite ma'lumotlar bazasida normalized jadvallarni saqlaydi va boshqaradi.
   - Rolga asoslangan xavfsiz avtorizatsiya: `employer` roli faqat qidiruv va so'rovlar bilan ishlay oladi.
   - Shaxsiy ma'lumotlarni yashirish / ochish mantiqiy filtrlari.

3. **Karyera Dashboard UI (`dashboard/src/App.tsx`)**:
   - **Ish beruvchi uchun**: Student Talent Map (aqlli qidiruv va filtrlar paneli, rezyumelarni ochib ko'rish, intro request yuborish) va Intro Tracker (yuborilgan so'rovlar statusi).
   - **Karyera markazi xodimlari uchun**: Overview (tizim statistikasi), Student Talent Map (barcha ma'lumotlar bilan), Intro Approvals (so'rovlarni tasdiqlash/rad etish), Vacancy Matchmaker va Curriculum Deficit Analyzer.