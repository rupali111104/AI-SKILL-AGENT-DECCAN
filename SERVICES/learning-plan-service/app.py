import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.skills import normalize_skill


app = FastAPI(title="Learning Plan Service", version="1.0.0")


class LearningPlanRequest(BaseModel):
    missing_skills: list[str] = []
    weak_skills: list[str] = []


def estimate_time(skill: str) -> str:
    advanced = {"langgraph", "rag", "vector database", "kubernetes", "deep learning", "llm"}
    medium = {"fastapi", "react", "docker", "postgresql", "machine learning", "sentence transformers"}

    if skill in advanced:
        return "2-3 weeks"
    if skill in medium:
        return "1-2 weeks"
    return "3-5 days"


def resource_pack(skill: str):
    resources = {
        "aws": ["S3 object storage basics", "IAM least privilege", "Upload flow with signed URLs"],
        "docker": ["Dockerfile fundamentals", "Container networking", "Compose multi-service workflows"],
        "kubernetes": ["Deployments and Services", "ConfigMaps and Secrets", "Horizontal scaling basics"],
        "postgresql": ["Schema design", "JSONB result storage", "Connection pooling basics"],
        "sentence transformers": ["Embedding model basics", "Cosine similarity", "Model serving trade-offs"],
    }
    return resources.get(
        skill,
        [
            f"Official documentation for {skill}",
            f"One hands-on project using {skill}",
            f"Interview questions focused on {skill}",
        ],
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "learning-plan-service"}


@app.post("/learning-plan")
def generate_learning_plan(payload: LearningPlanRequest):
    priority_skills = []
    for skill in payload.missing_skills + payload.weak_skills:
        normalized = normalize_skill(skill)
        if normalized not in priority_skills:
            priority_skills.append(normalized)

    plan = []
    for index, skill in enumerate(priority_skills[:8], start=1):
        plan.append(
            {
                "week": index,
                "skill": skill,
                "priority": "High" if index <= 3 else "Medium",
                "why_it_matters": f"{skill} is a gap for the target role and should be improved before interview rounds.",
                "goal": f"Build practical confidence in {skill} and produce a small proof-of-work deliverable.",
                "resources": resource_pack(skill),
                "mini_project": f"Create a role-specific project that demonstrates {skill} in a production-like workflow.",
                "time_estimate": estimate_time(skill),
            }
        )

    if not plan:
        plan.append(
            {
                "week": 1,
                "skill": "interview readiness",
                "priority": "High",
                "why_it_matters": "The detected resume skills already cover the role, so the next signal is depth.",
                "goal": "Practice explaining the strongest projects with clear architecture and trade-offs.",
                "resources": ["Prepare project stories", "Map evidence to job requirements", "Run mock interviews"],
                "mini_project": "Create a project evidence bank mapped to the target job description.",
                "time_estimate": "2-3 days",
            }
        )

    return {"learning_plan": plan}
