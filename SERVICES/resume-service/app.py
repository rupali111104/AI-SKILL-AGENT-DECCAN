import os
import shutil
import sys
import tempfile
from typing import Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.database import save_analysis_result
from common.skills import clean_text, extract_skills
from common.storage import store_resume_object


app = FastAPI(title="Resume Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SKILL_MATCHING_URL = os.getenv("SKILL_MATCHING_URL", "http://skill-matching-service:8001")
QUESTION_SERVICE_URL = os.getenv("QUESTION_SERVICE_URL", "http://question-generation-service:8002")
LEARNING_PLAN_URL = os.getenv("LEARNING_PLAN_URL", "http://learning-plan-service:8003")


def extract_text(file: UploadFile) -> str:
    extension = file.filename.rsplit(".", 1)[-1].lower()
    if extension not in {"pdf", "docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        if extension == "pdf":
            from pypdf import PdfReader

            reader = PdfReader(temp_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

        from docx import Document

        document = Document(temp_path)
        return "\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip())
    finally:
        os.remove(temp_path)


@app.get("/health")
def health():
    return {"status": "ok", "service": "resume-service"}


@app.post("/analyze-candidate")
@app.post("/resumes/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    jd_file: Optional[UploadFile] = File(None),
    jd_text: str = Form(""),
):
    content = await resume_file.read()
    resume_file.file.seek(0)
    storage_result = store_resume_object(resume_file.filename, content)
    resume_text = extract_text(resume_file)

    if jd_file and jd_file.filename:
        job_description_text = extract_text(jd_file)
    else:
        job_description_text = jd_text

    if not clean_text(resume_text):
        raise HTTPException(status_code=400, detail="No text could be extracted from the resume")
    if not clean_text(job_description_text):
        raise HTTPException(status_code=400, detail="Please upload or paste a job description")

    candidate_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description_text)

    async with httpx.AsyncClient(timeout=30) as client:
        match_response = await client.post(
            f"{SKILL_MATCHING_URL}/match",
            json={
                "resume_text": resume_text,
                "job_description_text": job_description_text,
                "candidate_skills": candidate_skills,
                "required_skills": required_skills,
            },
        )
        match_response.raise_for_status()
        match_result = match_response.json()

        question_response = await client.post(
            f"{QUESTION_SERVICE_URL}/questions",
            json={
                "missing_skills": match_result["missing_skills"],
                "matched_skills": match_result["matched_skills"],
                "required_skills": required_skills,
            },
        )
        question_response.raise_for_status()

        plan_response = await client.post(
            f"{LEARNING_PLAN_URL}/learning-plan",
            json={"missing_skills": match_result["missing_skills"], "weak_skills": []},
        )
        plan_response.raise_for_status()

    result = {
        **match_result,
        "resume_uri": storage_result["uri"],
        "questions": question_response.json()["questions"],
        "learning_plan": plan_response.json()["learning_plan"],
    }
    result["persistence"] = save_analysis_result(result)
    return result


def score_answer(skill: str, answer: str):
    words = answer.lower().split()
    score = 1
    if len(words) >= 25:
        score += 1
    if len(words) >= 60:
        score += 1
    if skill.lower() in answer.lower():
        score += 1
    if {"project", "built", "implemented", "debugged", "deployed", "tested"}.intersection(words):
        score += 1

    score = min(score, 5)
    if score >= 4:
        level = "strong"
        feedback = "The answer shows practical understanding and implementation detail."
    elif score == 3:
        level = "moderate"
        feedback = "The answer has useful detail, but should include clearer trade-offs or examples."
    else:
        level = "needs improvement"
        feedback = "The answer needs a concrete project example and more technical depth."

    return {
        "skill": skill,
        "score": score,
        "level": level,
        "feedback": feedback,
        "next_probe": f"Ask for a deeper example of how the candidate used {skill}.",
    }


@app.post("/evaluate-assessment")
async def evaluate_assessment(data: dict):
    answers = data.get("answers", {})
    missing_skills = data.get("missing_skills", [])
    results = [score_answer(skill, answer) for skill, answer in answers.items() if answer.strip()]
    weak_skills = [item["skill"] for item in results if item["score"] <= 3]
    average_score = 0
    if results:
        average_score = round(sum(item["score"] for item in results) / len(results), 2)

    async with httpx.AsyncClient(timeout=30) as client:
        plan_response = await client.post(
            f"{LEARNING_PLAN_URL}/learning-plan",
            json={"missing_skills": missing_skills, "weak_skills": weak_skills},
        )
        plan_response.raise_for_status()

    return {
        "average_score": average_score,
        "results": results,
        "learning_plan": plan_response.json()["learning_plan"],
    }
