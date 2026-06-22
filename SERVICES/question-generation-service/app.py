from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Question Generation Service", version="1.0.0")

QUESTION_TEMPLATES = [
    "Explain one real project or task where you used {skill}. What problem did it solve?",
    "What are the most important concepts someone should understand before using {skill} in production?",
    "Describe a mistake or challenge that can happen with {skill}, and how you would handle it.",
]


class QuestionRequest(BaseModel):
    missing_skills: list[str] = []
    matched_skills: list[str] = []
    required_skills: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok", "service": "question-generation-service"}


@app.post("/questions")
def generate_questions(payload: QuestionRequest):
    focus_skills = payload.missing_skills[:3] + payload.matched_skills[:3]
    if not focus_skills:
        focus_skills = payload.required_skills[:6]

    questions = []
    for index, skill in enumerate(focus_skills[:6]):
        template = QUESTION_TEMPLATES[index % len(QUESTION_TEMPLATES)]
        questions.append(
            {
                "id": f"q{index + 1}",
                "skill": skill,
                "difficulty": "practical" if index < 3 else "conceptual",
                "question": template.format(skill=skill),
                "what_good_answer_covers": [
                    "specific project context",
                    "implementation details",
                    "trade-offs or debugging experience",
                ],
            }
        )

    return {"questions": questions}
