"""
Pydantic schemas to enforce structured outputs across agent conversational modes.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Mock Interview ---
class InterviewFeedback(BaseModel):
    strengths: List[str] = Field(description="Kuchli tomonlari / Strengths")
    improvements: List[str] = Field(description="Yaxshilash kerak bo'lgan jihatlar / Areas for improvement")
    star_analysis: str = Field(description="STAR metodi bo'yicha tahlil / STAR method analysis")
    score: int = Field(description="Yakuniy ball (0 dan 10 gacha) / Final score (0-10)")

class MockInterviewOutput(BaseModel):
    question_number: int = Field(description="Savol tartib raqami (1, 2, 3) / Question number")
    question_text: str = Field(description="Talabaga beriladigan navbatdagi savol yoki yakuniy xabar / Question or wrap-up message")
    feedback_on_previous: Optional[str] = Field(None, description="Talabaning oldingi javobiga qisqa micro-feedback / Micro-feedback on previous answer")
    is_completed: bool = Field(description="Intervyu yakunlandimi yoki yo'q / Is interview session finished")
    final_report: Optional[InterviewFeedback] = Field(None, description="Intervyu yakunlanganda beriladigan to'liq hisobot / Full feedback report at end")


# --- Resume Builder & ATS Optimizer ---
class ResumeOptimizationOutput(BaseModel):
    ats_score: int = Field(description="ATS muvofiqlik darajasi (0-100) / ATS score")
    missing_sections: List[str] = Field(description="Qidirilayotgan lekin topilmagan bo'limlar / Missing sections")
    missing_keywords: List[str] = Field(description="Karyera yo'nalishi uchun etishmayotgan kalit so'zlar / Missing role keywords")
    optimized_resume_markdown: str = Field(description="Tayyor optimallashtirilgan rezyume (Telegram Markdown formatida) / Complete optimized resume markdown")
    critical_recommendations: List[str] = Field(description="Tavsiyalar va muhim ko'rsatmalar / Actionable suggestions")


# --- Vacancy Matchmaker ---
class VacancyMatch(BaseModel):
    vacancy_title: str = Field(description="Vakansiya nomi / Vacancy title")
    company: str = Field(description="Kompaniya / Company name")
    match_score: int = Field(description="Mos kelish foizi (0-100) / Match percentage")
    skill_gaps: List[str] = Field(description="Talabada etishmayotgan ko'nikmalar / Skills missing")
    why_matches: str = Field(description="Nega aynan shu vakansiya mos kelishi / Reason for match")
    cover_letter: str = Field(description="Moslashtirilgan Cover Letter (muqova xati) / Customized cover letter")
    networking_message: str = Field(description="Kompaniya vakili bilan bog'lanish uchun xabar / Networking chat template")

class VacancyMatchmakingOutput(BaseModel):
    matches: List[VacancyMatch] = Field(description="Mos keladigan vakansiyalar ro'yxati / List of matched vacancies")


# --- Dynamic Quiz & Homework ---
class QuizFeedback(BaseModel):
    score: int = Field(description="Quiz natijasi (0 dan 3 gacha) / Correct answers count")
    errors_analysis: str = Field(description="Xatolar va kamchiliklar tahlili / Breakdown of errors")
    future_recommendations: str = Field(description="Kelgusi safar nimalarga e'tibor qaratish kerakligi / Next study steps")
    quiz_topic: str = Field(description="Quiz mavzusi yoki asosiy texnologiyasi (masalan: Python, Django, SQL) / The main technology or skill assessed in this quiz")

class QuizOutput(BaseModel):
    question_number: int = Field(description="Savol tartib raqami (1, 2, 3) / Question number")
    question_text: str = Field(description="Talabaga beriladigan navbatdagi savol / The quiz question")
    is_completed: bool = Field(description="Quiz yakunlandimi yoki yo'q / Is quiz session completed")
    feedback_on_previous: Optional[str] = Field(None, description="Talabaning oldingi javobiga feedback / Feedback on previous response")
    final_report: Optional[QuizFeedback] = Field(None, description="Quiz yakunlanganda beriladigan to'liq hisobot / Full quiz score report")


# --- Career Advice & Skill Passport ---
class CareerAdviceOutput(BaseModel):
    response_text: str = Field(description="Tavsiya va javob matni (Telegram Markdown formatida) / Main advice body text")
    suggested_next_steps: List[str] = Field(description="Keyingi tavsiya etiladigan qadamlar ro'yxati / Recommended next actions")
