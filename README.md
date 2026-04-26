# AI Skill Assessment Agent

This project is an AI powered skill assessment and learning plan app.

The idea is simple. A resume can show what a person claims to know, but it does not always show how well they actually know it. This app takes a candidate resume and a job description, compares the skills, asks a few assessment questions, scores the answers, and then creates a learning plan for the missing or weak skills.

I built this as a working prototype for the Deccan AI Catalyst hackathon.

## What The App Does

The user uploads a resume as a PDF or DOCX file. The user can also upload a job description file or paste the job description text directly into the app.

After clicking analyze, the backend extracts text from the files and finds the important skills in both the resume and the job description. Then it compares both sides and shows matched skills, missing skills, a skill match score, and a semantic similarity score.

After that, the app asks skill-based assessment questions. The candidate can answer those questions, and the app gives a basic proficiency score for each answer. Finally, it creates a personalized learning plan with priority, time estimate, resources, and a small project idea for practice.

## Main Features

1. Upload resume as PDF or DOCX
2. Upload or paste job description
3. Extract text from PDF and DOCX files
4. Find required skills from the job description
5. Find candidate skills from the resume
6. Show matched skills and skill gaps
7. Create embeddings using a local model
8. Compare resume and job description using cosine similarity
9. Ask assessment questions for important skills
10. Score candidate answers
11. Generate a personalized learning plan

## Tech Stack

-> React for frontend
-> FastAPI for backend
-> Python
-> LangGraph for agent workflow
-> sentence-transformers for local embeddings
-> scikit-learn for cosine similarity
-> pypdf for PDF text extraction
-> python-docx for DOCX text extraction

## Project Structure

```text
AI-SKILL-AGENT-DECCAN/
  BACKEND/
    app/
      main.py
      document_utils.py
      embedding_utils.py
      agent_utils.py
      agent_graph.py
    requirements.txt

  FRONTEND/
    src/
      App.jsx
      App.css
      main.jsx
      index.css
    package.json
```

## How It Works

```text
Resume + Job Description
        ↓
Text extraction from PDF/DOCX
        ↓
Skill extraction
        ↓
Skill matching and gap analysis
        ↓
Assessment questions
        ↓
Answer scoring
        ↓
Personalized learning plan
```

The backend workflow is separated into different files so the code is easier to understand. Document extraction, embeddings, skill logic, and the agent workflow are not mixed together in one large file.

## Backend Setup

Open a terminal in the project folder and run:

```powershell
cd BACKEND
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend will run here:

```text
http://127.0.0.1:8000
```

FastAPI docs will be here:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a second terminal and run:

```powershell
cd FRONTEND
npm install
npm run dev
```

The frontend will usually run here:

```text
http://localhost:5173
```

Sometimes Vite may start on another port like `5174` or `5175`. That is okay.

## Sample Job Description

```text
We are hiring a Python backend developer to build AI-powered assessment applications. The candidate should have experience with FastAPI, React, REST API design, SQL, Git, Docker, machine learning, embeddings, scikit-learn, LangGraph, LLMs, and RAG. Strong communication and problem solving skills are required.
```

## Sample Output

```json
{
  "match_score": 55.56,
  "semantic_similarity": 62.18,
  "matched_skills": ["python", "react", "git"],
  "missing_skills": ["fastapi", "docker", "langgraph", "llm"],
  "questions": [
    {
      "skill": "fastapi",
      "question": "Explain one real project or task where you used fastapi. What problem did it solve?"
    }
  ]
}
```

## Scoring Logic

The skill match score is calculated by checking how many required job skills are also found in the resume.

The semantic similarity score is calculated using embeddings and cosine similarity. This gives a rough idea of how close the resume is to the job description in meaning, not only exact skill words.

The answer score is from 1 to 5. Longer and more practical answers get better scores, especially when they include real project details, implementation work, testing, deployment, debugging, or trade-offs.

The learning plan is created from missing skills and weak assessment scores. Each item includes why the skill matters, what to learn, a small project idea, resources, and estimated time.

## Architecture Diagram

```text
React Frontend
      ↓
FastAPI Backend
      ↓
PDF/DOCX Text Extraction
      ↓
LangGraph Agent Workflow
      ↓
Skill Gap Analysis
      ↓
Assessment Question Generator
      ↓
Answer Scoring
      ↓
Personalized Learning Plan
```

## Demo

Demo video link:

```text
https://drive.google.com/file/d/1mUPIx_SF_xJdaeIYgOC1u6Irafh4deR6/view?usp=sharing
```


## Notes

This is a prototype, so the skill extraction is intentionally kept simple and transparent. It uses a skill list, local embeddings, and clear scoring rules so the result is easy to understand and explain during a demo.

In a future version, the skill extraction and answer evaluation can be improved using a stronger LLM-based structured output system.
