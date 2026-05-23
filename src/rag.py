"""
RAG (Retrieval-Augmented Generation) module for Career AI Assistant.
Handles context retrieval from Chroma vector DB and LLM generation
with career counselor persona and multilingual support.
"""
import os
from pathlib import Path
from src.config import (
    GEMINI_API_KEY, OPENAI_API_KEY, DEFAULT_PROVIDER,
    GEMINI_MODEL, OPENAI_MODEL, KB_COLLECTION
)
from src.ingestion import get_chroma_client, get_embedding, load_chunks_cache
import numpy as np

# Simple stop words for keyword retrieval fallback
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "at", "by",
    "for", "with", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "s", "t", "can", "will", "just", "don", "should", "now", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "i", "you",
    "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their",
    # Uzbek stop words
    "va", "yoki", "bu", "uchun", "bilan", "bo'lsa", "kerak", "qanday", "nima",
    "men", "siz", "u", "ular", "bizning", "ham", "esa", "da", "ga", "ni", "dan",
}


def clean_and_tokenize(text: str) -> list[str]:
    """Cleans punctuation and tokenizes text, removing stop words."""
    cleaned = "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in text)
    tokens = cleaned.split()
    return [t for t in tokens if t not in STOP_WORDS]


def keyword_search(query: str, top_k: int = 5) -> list[dict]:
    """Fallback keyword search over cached JSON chunks from knowledge base."""
    chunks = load_chunks_cache("knowledge-base")
    if not chunks:
        return []

    query_tokens = clean_and_tokenize(query)
    if not query_tokens:
        return chunks[:top_k]

    scored_chunks = []
    for chunk in chunks:
        chunk_text_lower = chunk["text"].lower()
        score = 0
        for token in query_tokens:
            score += chunk_text_lower.count(token)
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_chunks[:top_k]]


def retrieve_context(query: str, provider: str = None, top_k: int = 5) -> list[dict]:
    """Retrieves relevant text chunks from knowledge base using Chroma or keyword fallback."""
    import src.config

    if provider is None:
        provider = DEFAULT_PROVIDER

    if provider == "mock" or src.config.API_FAILED:
        return keyword_search(query, top_k)

    client = get_chroma_client()
    if client:
        try:
            collection = client.get_collection(KB_COLLECTION)

            # Embed the query
            query_vector = get_embedding(query, provider=provider)

            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )

            retrieved = []
            if results and results["documents"] and results["documents"][0]:
                for idx in range(len(results["documents"][0])):
                    metadata = results["metadatas"][0][idx] if results.get("metadatas") else None
                    filename = metadata.get("filename", "unknown") if metadata else "unknown"
                    retrieved.append({
                        "id": results["ids"][0][idx],
                        "text": results["documents"][0][idx],
                        "filename": filename,
                    })
                return retrieved
        except Exception as e:
            print(f"Chroma retrieval failed: {e}. Falling back to keyword search.")

    return keyword_search(query, top_k)


def call_llm(prompt: str, provider: str = None, temperature: float = 0.3) -> str:
    """Calls Gemini or OpenAI LLM using structured prompt."""
    import src.config

    if provider is None:
        provider = DEFAULT_PROVIDER

    if src.config.API_FAILED:
        raise RuntimeError("Skipping API call because the active provider has failed.")

    if provider == "gemini" and GEMINI_API_KEY:
        try:
            import google.genai as genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            result = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature
                )
            )
            return result.text.strip()
        except Exception as e:
            print(f"Gemini generation failed: {e}.")
            # Try OpenAI as fallback
            if OPENAI_API_KEY:
                provider = "openai"
            else:
                src.config.API_FAILED = True
                raise

    if provider == "openai" and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI generation failed: {e}.")
            src.config.API_FAILED = True
            raise

    raise RuntimeError("Both LLM providers failed or API keys are missing.")


def career_query(query: str, student_profile: dict = None, language: str = "uz",
                 provider: str = None, system_instruction: str = "") -> str:
    """
    Main RAG query function for career assistant.
    Retrieves relevant career knowledge base context and generates a grounded answer.
    """
    if provider is None:
        provider = DEFAULT_PROVIDER

    # 1. Retrieve context
    retrieved_chunks = retrieve_context(query, provider=provider)

    # 2. Build context text
    context_str = ""
    if retrieved_chunks:
        for chunk in retrieved_chunks:
            context_str += f"\n--- {chunk.get('filename', 'knowledge_base')} ---\n"
            context_str += chunk["text"]
            context_str += "\n---\n"

    # 3. Build student profile context
    profile_str = ""
    if student_profile:
        profile_str = f"""
Student Profile:
- Name: {student_profile.get('name', 'N/A')}
- University: {student_profile.get('university', 'N/A')}
- Faculty: {student_profile.get('faculty', 'N/A')}
- Year: {student_profile.get('year', 'N/A')}
- Target Role: {student_profile.get('target_role', 'N/A')}
- Known Technologies: {student_profile.get('skills', 'N/A')}
"""

    # Language instruction
    lang_map = {"uz": "O'zbek tilida", "ru": "На русском языке", "en": "In English"}
    lang_instruction = lang_map.get(language, "O'zbek tilida")

    # 4. Build prompt
    prompt = f"""Sen universitet karyera markazining professional AI maslahatchisisan.
{system_instruction}

{profile_str}

Quyidagi bilim bazasi kontekstidan foydalanib javob ber:
{context_str if context_str else "(Bilim bazasidan ma'lumot topilmadi)"}

Talaba so'rovi: "{query}"

Qoidalar:
1. Javobni {lang_instruction} ber.
2. Faqat bilim bazasidagi ma'lumotlarga va karyera sohasidagi umumiy bilimlaringga asoslan.
3. Aniq, amaliy va foydali maslahatlar ber.
4. Javobni Telegram formatida ber (markdown: *bold*, _italic_, •bullet points).
5. Talabaning profiliga moslab shaxsiylashtirilgan javob ber.

Javob:
"""

    try:
        return call_llm(prompt, provider=provider, temperature=0.3)
    except Exception as e:
        print(f"LLM call failed: {e}")
        # Provide a basic fallback response
        if language == "uz":
            return "Kechirasiz, hozir javob bera olmadim. Iltimos, qayta urinib ko'ring yoki /start buyrug'ini bering."
        elif language == "ru":
            return "Извините, не смог ответить. Пожалуйста, попробуйте снова или введите /start."
        else:
            return "Sorry, I couldn't generate a response. Please try again or type /start."
