import os
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.document_utils import pdf_to_text, docx_to_text
from app.embedding_utils import create_embedding, calculate_cosine_similarity
from app.agent_utils import evaluate_answers, generate_learning_plan
from app.agent_graph import run_agent_graph


app = FastAPI(title="Skill Assessment Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Skill Assessment Agent backend is running"}


def save_uploaded_file(file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


def extract_text_from_upload(file: UploadFile) -> str:
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    file_path = save_uploaded_file(file)

    if file_extension == "pdf":
        return pdf_to_text(file_path)

    return docx_to_text(file_path)


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    text = extract_text_from_upload(file)

    if not text:
        return {
            "filename": file.filename,
            "text": "",
            "message": "No text was extracted. This may be a scanned/image-based file."
        }

    return {
        "filename": file.filename,
        "text": text
    }


@app.post("/analyze-candidate")
async def analyze_candidate(
    resume_file: UploadFile = File(...),
    jd_file: Optional[UploadFile] = File(None),
    jd_text: str = Form(""),
):
    resume_text = extract_text_from_upload(resume_file)

    if jd_file and jd_file.filename:
        job_description_text = extract_text_from_upload(jd_file)
    else:
        job_description_text = jd_text

    if not resume_text:
        raise HTTPException(status_code=400, detail="No text could be extracted from the resume.")

    if not job_description_text.strip():
        raise HTTPException(status_code=400, detail="Please upload a job description or paste job description text.")

    return run_agent_graph(job_description_text, resume_text)


@app.post("/evaluate-assessment")
def evaluate_assessment(data: dict):
    answers = data.get("answers", {})
    missing_skills = data.get("missing_skills", [])

    if not answers:
        raise HTTPException(status_code=400, detail="Assessment answers are required.")

    evaluation = evaluate_answers(answers)
    weak_skills = [
        item["skill"]
        for item in evaluation["results"]
        if item["score"] <= 3
    ]

    return {
        **evaluation,
        "learning_plan": generate_learning_plan(missing_skills, weak_skills),
    }



@app.post("/similarity")
def similarity(data: dict):
    text1 = data.get("text1", "")
    text2 = data.get("text2", "")

    if not text1 or not text2:
        raise HTTPException(status_code=400, detail="Both text1 and text2 are required")

    embedding1 = create_embedding(text1)
    embedding2 = create_embedding(text2)

    score = calculate_cosine_similarity(embedding1, embedding2)

    return {
        "similarity_score": score,
        "percentage": round(score * 100, 2)
    }
