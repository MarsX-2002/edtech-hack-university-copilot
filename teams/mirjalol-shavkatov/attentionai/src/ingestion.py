import os
import hashlib
import json
from pathlib import Path
try:
    import pypdf
except ImportError:
    pypdf = None  # PDF parsing unavailable
import chromadb
from src.config import CHROMA_DIR, UPLOAD_DIR, DATA_DIR, GEMINI_API_KEY, OPENAI_API_KEY, DEFAULT_PROVIDER, API_FAILED
import numpy as np
import google.genai as genai

# Initialize Gemini client if API key is provided (no explicit configure needed)
if GEMINI_API_KEY:
    # No explicit configuration needed; GEMINI_API_KEY is read from environment
    pass
else:
    # No API key; embeddings will fallback to mock implementations.
    pass
# Chroma DB Client
_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        try:
            _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        except Exception as e:
            print(f"Error initializing Chroma DB client: {e}")
    return _chroma_client

def get_collection_name(course_id: str) -> str:
    # Chroma collection name must be 3-63 chars, start/end with alpha, only alphanumeric, underscores, hyphens
    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in course_id)
    safe_name = f"course-{safe_name}"
    # Ensure it starts with alphanumeric
    if not safe_name[0].isalnum():
        safe_name = "c-" + safe_name
    return safe_name[:63]

def parse_file(file_path: Path) -> str:
    """Parses TXT or PDF files and extracts text."""
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif suffix == ".pdf":
        if pypdf is None:
            print("pypdf not installed; cannot parse PDF files.")
            return ""
        text = []
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n\n".join(text)
        except Exception as e:
            print(f"Error reading PDF {file_path.name}: {e}")
            return ""
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Splits text into chunks with a specified overlap."""
    if not text:
        return []
    
    # Simple chunking by character count
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def get_embeddings(texts: list[str], provider: str = None) -> list[list[float]]:
    """Computes embeddings for a list of texts in batch mode to maximize speed."""
    import src.config
    
    if provider is None:
        provider = DEFAULT_PROVIDER
        
    if not texts:
        return []
        
    # If the API key was flagged as failing, skip network calls immediately
    if not src.config.API_FAILED:
        if provider == "gemini" and GEMINI_API_KEY:
            def embed_batch(batch_texts: list[str]):
                """Embed a batch of texts using Gemini's embed_content API with fallback handling."""
                embeddings = []
                for text in batch_texts:
                    try:
                        client = genai.Client()
                        result = client.models.embed_content(
                            model=src.config.GEMINI_EMBED_MODEL,
                            contents=text
                        )
                        embeddings.append(result.embeddings[0].values)
                    except Exception as primary_err:
                        print(f"Gemini primary embedding failed ({src.config.GEMINI_EMBED_MODEL}): {primary_err}")
                        # Attempt fallback model
                        try:
                            fallback_result = client.models.embed_content(
                                model="models/gemini-embedding-001",
                                contents=text
                            )
                            embeddings.append(fallback_result.embeddings[0].values)
                        except Exception as fallback_err:
                            print(f"Gemini fallback embedding failed: {fallback_err}. Using mock embeddings.")
                            src.config.API_FAILED = True
                            return None
                return embeddings
            # Process texts in batches
            embeddings = []
            batch_size = 50
            total_batches = (len(texts) + batch_size - 1) // batch_size
            import time
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                print(f"[Gemini] Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks) using {src.config.GEMINI_EMBED_MODEL}...")
                batch_embeds = embed_batch(batch)
                if batch_embeds is None:
                    # Mock fallback was triggered; break out to use mock embeddings later
                    break
                embeddings.extend(batch_embeds)
                if i + batch_size < len(texts):
                    time.sleep(1.0)  # Respect rate limits
            if embeddings:
                return embeddings
        elif provider == "openai" and OPENAI_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                embeddings = []
                batch_size = 100
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i+batch_size]
                    response = client.embeddings.create(
                        model="text-embedding-3-small",
                        input=batch
                    )
                    embeddings.extend([data.embedding for data in response.data])
                return embeddings
            except Exception as e:
                print(f"OpenAI batch embedding failed: {e}. Disabling OpenAI network calls and falling back to mock.")
                src.config.API_FAILED = True

    # Fallback/Mock embeddings
    embeddings = []
    for text in texts:
        dim = 768
        vec = np.zeros(dim)
        words = text.lower().split()
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        embeddings.append(vec.tolist())
    return embeddings

def get_embedding(text: str, provider: str = None) -> list[float]:
    """Computes embedding for a single text using selected provider."""
    return get_embeddings([text], provider=provider)[0]

def load_chunks_cache(course_id: str) -> list:
    """Loads chunks from the course's local JSON cache."""
    cache_file = DATA_DIR / f"chunks_{course_id}.json"
    if not cache_file.exists():
        return []
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_chunks_cache(course_id: str, chunks: list):
    """Saves chunks to the course's local JSON cache."""
    cache_file = DATA_DIR / f"chunks_{course_id}.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

def ingest_document(course_id: str, filename: str, file_content: bytes = None):
    """Parses, chunks, embeds, and indexes a course document."""
    file_path = UPLOAD_DIR / filename
    
    # If content was provided, write it to file
    if file_content is not None:
        with open(file_path, "wb") as f:
            f.write(file_content)
            
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Parse text
    text = parse_file(file_path)
    if not text:
        print(f"No text extracted from {filename}")
        return

    # 2. Chunk text
    chunks = chunk_text(text)
    print(f"Split {filename} into {len(chunks)} chunks.")

    # 3. Add to JSON cache
    cache = load_chunks_cache(course_id)
    
    new_records = []
    for idx, chunk in enumerate(chunks):
        record = {
            "id": f"{filename}_chunk_{idx}",
            "filename": filename,
            "chunk_index": idx,
            "text": chunk
        }
        new_records.append(record)
        
    # Remove existing chunks for this filename to prevent duplicate indexing
    cache = [c for c in cache if c["filename"] != filename]
    cache.extend(new_records)
    save_chunks_cache(course_id, cache)

    # 4. Add to Chroma DB (if Chroma is available and provider is not mock)
    client = get_chroma_client()
    if client:
        try:
            col_name = get_collection_name(course_id)
            collection = client.get_or_create_collection(col_name)
            
            # Embed chunks in batch
            embeddings = get_embeddings(chunks)
            documents = []
            ids = []
            metadatas = []
            
            for idx, chunk in enumerate(chunks):
                doc_id = f"{filename}_chunk_{idx}"
                documents.append(chunk)
                ids.append(doc_id)
                metadatas.append({"filename": filename, "course_id": course_id})
                
            # Delete old documents for this file in Chroma first
            try:
                collection.delete(where={"filename": filename})
            except Exception:
                pass
                
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"Indexed {len(chunks)} chunks into Chroma collection {col_name}.")
        except Exception as e:
            print(f"Failed to ingest in Chroma DB: {e}. Cached locally in JSON.")


def ingest_knowledge_base(provider: str = None):
    """Parses, chunks, embeds, and indexes all documents in knowledge_base/ folder."""
    from src.config import KNOWLEDGE_BASE_DIR, KB_COLLECTION
    client = get_chroma_client()
    if not client:
        print("Chroma DB client not available. Cannot ingest knowledge base.")
        return

    # Create/get the collection
    try:
        collection = client.get_or_create_collection(KB_COLLECTION)
    except Exception as e:
        print(f"Failed to create collection {KB_COLLECTION}: {e}")
        return

    kb_files = list(KNOWLEDGE_BASE_DIR.glob("**/*.txt")) + list(KNOWLEDGE_BASE_DIR.glob("**/*.pdf"))
    if not kb_files:
        print("No knowledge base files found.")
        return

    all_kb_chunks = []
    
    for file_path in kb_files:
        filename = file_path.name
        print(f"Ingesting KB file: {filename}")
        text = parse_file(file_path)
        if not text:
            continue
        
        chunks = chunk_text(text)
        print(f"Split {filename} into {len(chunks)} chunks.")
        
        for idx, chunk in enumerate(chunks):
            record = {
                "id": f"kb_{filename}_chunk_{idx}",
                "filename": filename,
                "chunk_index": idx,
                "text": chunk
            }
            all_kb_chunks.append(record)

    # Save to local JSON cache for fallback keyword search
    save_chunks_cache("knowledge-base", all_kb_chunks)

    # Index in Chroma DB
    try:
        # Reset collection if exists to avoid duplicates
        try:
            client.delete_collection(KB_COLLECTION)
        except Exception as e:
            print(f"Note: Collection reset skipped or collection did not exist: {e}")

        try:
            collection = client.get_or_create_collection(KB_COLLECTION)
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise

        # Chunk and embed
        texts = [c["text"] for c in all_kb_chunks]
        ids = [c["id"] for c in all_kb_chunks]
        metadatas = [{"filename": c["filename"]} for c in all_kb_chunks]

        if texts:
            embeddings = get_embeddings(texts, provider=provider)
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"Successfully indexed {len(texts)} chunks from knowledge base into Chroma collection '{KB_COLLECTION}'.")
    except Exception as e:
        print(f"Failed to index knowledge base in Chroma DB: {e}. Cached locally in JSON for keyword search.")

