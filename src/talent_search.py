"""
Talent search and matching engine for Campus Career Copilot.
Handles ChromaDB indexing of student profiles, hybrid search, and ranking with explanations.
"""
from datetime import datetime
from src.db import get_db_connection, get_student_profile_full

def index_student_profile(student_id: int):
    """Indexes or re-indexes a student profile in ChromaDB for semantic search."""
    from src.ingestion import get_chroma_client, get_embeddings
    
    student = get_student_profile_full(student_id)
    if not student or not student.get("consent_opt_in") or not student.get("profile_completed"):
        # Remove from index if no consent or not completed
        remove_student_from_index(student_id)
        return
        
    # Build a search summary
    # Format: Target role, bio, experiences summary, skills, education, projects.
    summary_parts = []
    summary_parts.append(f"Target Role: {student.get('target_role', '')}")
    
    profile = student.get("profile", {})
    if profile.get("bio"):
        summary_parts.append(f"Bio: {profile.get('bio')}")
    if profile.get("experience_summary"):
        summary_parts.append(f"Experience Summary: {profile.get('experience_summary')}")
        
    skills = [s.get("skill_name") for s in student.get("student_skills", [])]
    if skills:
        summary_parts.append(f"Skills: {', '.join(skills)}")
        
    for exp in student.get("experiences", []):
        summary_parts.append(f"Experience: Worked at {exp.get('company')} as {exp.get('role')}. Details: {exp.get('description', '')}")
        
    for proj in student.get("projects", []):
        summary_parts.append(f"Project: Built '{proj.get('title')}' using {proj.get('tech_stack', '')}. Details: {proj.get('description', '')}")
        
    document_text = "\n\n".join(summary_parts)
    
    # Save/upsert to ChromaDB under collection 'student_profiles'
    client = get_chroma_client()
    if client:
        try:
            collection = client.get_or_create_collection("student_profiles")
            # Embed
            emb = get_embeddings([document_text])[0]
            
            collection.upsert(
                ids=[str(student_id)],
                documents=[document_text],
                embeddings=[emb],
                metadatas=[{
                    "student_id": student_id,
                    "target_role": student.get("target_role", "") or "",
                    "name": student.get("name", "")
                }]
            )
        except Exception as e:
            print(f"Failed to upsert student {student_id} to ChromaDB: {e}")

def remove_student_from_index(student_id: int):
    """Removes a student profile from ChromaDB."""
    from src.ingestion import get_chroma_client
    client = get_chroma_client()
    if client:
        try:
            collection = client.get_collection("student_profiles")
            collection.delete(ids=[str(student_id)])
        except Exception:
            pass

def search_students_hybrid(query: str = None, target_role: str = None, min_readiness: float = None, skills_filter: list = None) -> list[dict]:
    """
    Performs hybrid search for students:
    1. SQL filters first (consented, active, matching basic fields)
    2. Semantic vector matching using ChromaDB
    3. Deterministic scoring, ranking, and explanation generation
    """
    from src.ingestion import get_chroma_client, get_embeddings
    
    # 1. SQL filtering to find valid matching student candidate IDs
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT id, name, target_role, readiness_score, university, faculty, year FROM students WHERE consent_opt_in = 1 AND is_active = 1 AND profile_completed = 1"
    params = []
    
    if target_role and target_role != "All":
        sql += " AND target_role = ?"
        params.append(target_role)
    if min_readiness is not None:
        sql += " AND readiness_score >= ?"
        params.append(min_readiness)
        
    cursor.execute(sql, tuple(params))
    candidate_rows = cursor.fetchall()
    conn.close()
    
    candidates = {row["id"]: dict(row) for row in candidate_rows}
    if not candidates:
        return []
        
    # Filter candidates by skills_filter (if present)
    if skills_filter:
        conn = get_db_connection()
        cursor = conn.cursor()
        valid_ids = []
        for cid in candidates.keys():
            cursor.execute("SELECT skill_name FROM student_skills WHERE student_id = ?;", (cid,))
            student_skills = {r["skill_name"].lower() for r in cursor.fetchall()}
            # Check if all filtering skills are present
            if all(s.lower() in student_skills for s in skills_filter):
                valid_ids.append(cid)
        conn.close()
        candidates = {cid: candidates[cid] for cid in valid_ids}
        if not candidates:
            return []
            
    # 2. Semantic query vector search (if query text is provided)
    semantic_scores = {} # student_id -> cosine similarity score
    if query and query.strip():
        client = get_chroma_client()
        if client:
            try:
                collection = client.get_collection("student_profiles")
                query_vector = get_embeddings([query])[0]
                
                # Query Chroma
                res = collection.query(
                    query_embeddings=[query_vector],
                    n_results=len(candidates) * 2 # get enough results
                )
                
                if res and res["ids"] and res["ids"][0]:
                    for idx, s_id_str in enumerate(res["ids"][0]):
                        try:
                            s_id = int(s_id_str)
                            # Only score candidates that passed SQL filter
                            if s_id in candidates:
                                # Chroma distance (lower is closer, typically cosine distance = 1 - similarity)
                                distance = res["distances"][0][idx]
                                similarity = 1.0 - distance
                                semantic_scores[s_id] = similarity
                        except ValueError:
                            continue
            except Exception as e:
                print(f"Chroma search failed or collection empty: {e}")
                
    # If vector search didn't run or query is empty, set similarity default to 1.0
    for cid in candidates:
        if cid not in semantic_scores:
            semantic_scores[cid] = 1.0 if not (query and query.strip()) else 0.1
            
    # 3. Load full profile, rank and explain match reason
    results = []
    for cid, cand in candidates.items():
        profile = get_student_profile_full(cid)
        
        # Calculate skill overlap if search query contains skill indicators
        skill_match_cnt = 0
        skills_list = [s["skill_name"].lower() for s in profile.get("student_skills", [])]
        if query:
            for s in skills_list:
                if s in query.lower():
                    skill_match_cnt += 1
                    
        # Deterministic Ranking Score formula:
        # 40% readiness score + 30% semantic score + 20% profile completeness + 10% skills overlap
        readiness = cand.get("readiness_score") or 0.0 # 0 to 100
        semantic = semantic_scores.get(cid, 0.0) # 0.0 to 1.0
        
        # Profile completeness calculation
        completeness = 0.0
        if profile.get("profile", {}).get("bio"): completeness += 20
        if profile.get("profile", {}).get("video_intro_url"): completeness += 10
        if profile.get("profile", {}).get("resume_url"): completeness += 10
        if profile.get("experiences"): completeness += 20
        if profile.get("education"): completeness += 20
        if profile.get("projects"): completeness += 20
        
        ranking_score = (readiness * 0.4) + (semantic * 30) + (completeness * 0.2) + (skill_match_cnt * 5)
        
        # Generate match explanation
        explanation = generate_match_explanation(cand, profile, query, semantic)
        
        results.append({
            "student_id": cid,
            "name": cand["name"],
            "target_role": cand["target_role"],
            "university": cand["university"],
            "faculty": cand["faculty"],
            "year": cand["year"],
            "readiness_score": readiness,
            "completeness_score": completeness,
            "semantic_similarity": semantic,
            "ranking_score": ranking_score,
            "match_explanation": explanation,
            "skills": [s["skill_name"] for s in profile.get("student_skills", [])],
            "verified_skills": [s["skill_name"] for s in profile.get("student_skills", []) if s.get("is_verified")],
            "education": profile.get("education", []),
            "experiences": profile.get("experiences", []),
            "projects": profile.get("projects", []),
            "bio": profile.get("profile", {}).get("bio", ""),
            "video_intro_url": profile.get("profile", {}).get("video_intro_url", ""),
            "resume_url": profile.get("profile", {}).get("resume_url", "")
        })
        
    # Sort descending by ranking_score
    results.sort(key=lambda x: x["ranking_score"], reverse=True)
    return results

def generate_match_explanation(cand: dict, profile: dict, query: str, semantic: float) -> str:
    """Generates an intuitive explanation of why the student matched the query."""
    reasons = []
    
    role = cand.get("target_role")
    if role:
        reasons.append(f"Target role aligns with '{role}'")
        
    skills = [s["skill_name"] for s in profile.get("student_skills", [])]
    verified = [s["skill_name"] for s in profile.get("student_skills", []) if s.get("is_verified")]
    
    if verified:
        reasons.append(f"Has verified skills: {', '.join(verified[:3])}")
    elif skills:
        reasons.append(f"Knows: {', '.join(skills[:3])}")
        
    exps = profile.get("experiences", [])
    if exps:
        reasons.append(f"Has {len(exps)} project/internship experience(s) (e.g. at {exps[0]['company']})")
        
    projs = profile.get("projects", [])
    if projs:
        reasons.append(f"Completed {len(projs)} technical projects (e.g. '{projs[0]['title']}')")
        
    if cand.get("readiness_score") and cand.get("readiness_score") >= 80:
        reasons.append(f"High readiness score of {cand['readiness_score']}%")
        
    if query and semantic > 0.6:
        reasons.append("Strong semantic match to search query")
        
    return " • ".join(reasons)
