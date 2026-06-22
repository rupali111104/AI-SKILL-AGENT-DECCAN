import os
import sys
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.skills import compare_skills, extract_skills
from common.vectors import cosine_similarity, create_embedding


app = FastAPI(title="Skill Matching Service", version="1.0.0")
model = None

try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
except Exception:
    model = None


class MatchRequest(BaseModel):
    resume_text: str
    job_description_text: str
    candidate_skills: list[str] = []
    required_skills: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok", "service": "skill-matching-service"}


@app.post("/match")
def match_skills(payload: MatchRequest):
    candidate_skills = payload.candidate_skills or extract_skills(payload.resume_text)
    required_skills = payload.required_skills or extract_skills(payload.job_description_text)
    comparison = compare_skills(required_skills, candidate_skills)

    if model:
        embeddings = model.encode([payload.resume_text[:4000], payload.job_description_text[:4000]])
        semantic_similarity = round(cosine_similarity(embeddings[0], embeddings[1]) * 100, 2)
        embedding_engine = "sentence-transformers"
    else:
        resume_embedding = create_embedding(payload.resume_text[:4000])
        jd_embedding = create_embedding(payload.job_description_text[:4000])
        semantic_similarity = round(cosine_similarity(resume_embedding, jd_embedding) * 100, 2)
        embedding_engine = "local-hashing-fallback"

    return {
        "session_id": str(uuid.uuid4()),
        "embedding_engine": embedding_engine,
        "semantic_similarity": semantic_similarity,
        **comparison,
    }
