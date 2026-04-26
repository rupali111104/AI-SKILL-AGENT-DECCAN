import re
import uuid
from typing import Dict, List

from app.embedding_utils import calculate_cosine_similarity, create_embedding


SKILL_LIBRARY = [
    "python",
    "javascript",
    "typescript",
    "react",
    "fastapi",
    "django",
    "flask",
    "node.js",
    "express",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "html",
    "css",
    "tailwind",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "linux",
    "rest api",
    "graphql",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "langchain",
    "langgraph",
    "openai",
    "llm",
    "rag",
    "vector database",
    "faiss",
    "pinecone",
    "chromadb",
    "embeddings",
    "scikit-learn",
    "pandas",
    "numpy",
    "data analysis",
    "data visualization",
    "power bi",
    "tableau",
    "excel",
    "tensorflow",
    "pytorch",
    "api integration",
    "authentication",
    "testing",
    "unit testing",
    "ci/cd",
    "agile",
    "communication",
    "problem solving",
]

ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "apis": "rest api",
    "api": "rest api",
    "gen ai": "llm",
    "generative ai": "llm",
    "large language model": "llm",
    "retrieval augmented generation": "rag",
    "sklearn": "scikit-learn",
}

QUESTION_TEMPLATES = [
    "Explain one real project or task where you used {skill}. What problem did it solve?",
    "What are the most important concepts someone should understand before using {skill} in production?",
    "Describe a mistake or challenge that can happen with {skill}, and how you would handle it.",
]


def make_session_id() -> str:
    return str(uuid.uuid4())


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_skill(skill: str) -> str:
    cleaned = skill.lower().strip()
    cleaned = cleaned.replace("_", " ").replace("-", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return ALIASES.get(cleaned, cleaned)


def extract_skills(text: str) -> List[str]:
    lowered = f" {clean_text(text).lower()} "
    found = set()

    for skill in SKILL_LIBRARY:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill.lower()) + r"(?![a-z0-9+#.])"
        if re.search(pattern, lowered):
            found.add(normalize_skill(skill))

    for alias, canonical in ALIASES.items():
        pattern = r"(?<![a-z0-9+#.])" + re.escape(alias) + r"(?![a-z0-9+#.])"
        if re.search(pattern, lowered):
            found.add(canonical)

    return sorted(found)


def compare_skills(required_skills: List[str], candidate_skills: List[str]) -> Dict:
    required = [normalize_skill(skill) for skill in required_skills]
    candidate = [normalize_skill(skill) for skill in candidate_skills]

    required_set = set(required)
    candidate_set = set(candidate)
    matched = sorted(required_set.intersection(candidate_set))
    missing = sorted(required_set.difference(candidate_set))
    extra = sorted(candidate_set.difference(required_set))

    match_score = 0
    if required_set:
        match_score = round((len(matched) / len(required_set)) * 100, 2)

    return {
        "required_skills": sorted(required_set),
        "candidate_skills": sorted(candidate_set),
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "match_score": match_score,
    }


def generate_readiness_summary(comparison: Dict, semantic_similarity: float) -> Dict:
    match_score = comparison.get("match_score", 0)
    missing_skills = comparison.get("missing_skills", [])
    matched_skills = comparison.get("matched_skills", [])

    if match_score >= 75 and semantic_similarity >= 60:
        level = "Strong fit"
        recommendation = "Move the candidate to a focused technical interview."
    elif match_score >= 45:
        level = "Developing fit"
        recommendation = "Assess the candidate on the missing high-priority skills before making a decision."
    else:
        level = "Early fit"
        recommendation = "Use the learning plan first, then reassess after targeted preparation."

    strongest_signal = "No matching skills detected yet."
    if matched_skills:
        strongest_signal = f"Strongest evidence appears around {', '.join(matched_skills[:3])}."

    biggest_risk = "No major skill gap detected from the current inputs."
    if missing_skills:
        biggest_risk = f"Biggest gap area: {', '.join(missing_skills[:3])}."

    return {
        "level": level,
        "recommendation": recommendation,
        "strongest_signal": strongest_signal,
        "biggest_risk": biggest_risk,
    }


def generate_assessment_questions(skills: List[str]) -> List[Dict]:
    focus_skills = skills[:6]
    questions = []

    for index, skill in enumerate(focus_skills):
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

    return questions


def score_answer(skill: str, answer: str) -> Dict:
    answer_text = clean_text(answer)
    words = re.findall(r"[a-zA-Z0-9+#.]+", answer_text.lower())
    unique_words = set(words)

    score = 1
    if len(words) >= 25:
        score += 1
    if len(words) >= 60:
        score += 1
    if skill.lower() in answer_text.lower():
        score += 1
    if unique_words.intersection({"project", "built", "implemented", "debugged", "deployed", "tested", "optimized", "api", "database", "model"}):
        score += 1
    if unique_words.intersection({"because", "tradeoff", "trade-offs", "latency", "scalable", "security", "validation", "error", "monitoring"}):
        score += 1

    score = min(score, 5)

    if score >= 4:
        level = "strong"
        feedback = "The answer shows practical understanding and enough detail for a confident signal."
    elif score == 3:
        level = "moderate"
        feedback = "The answer has some useful detail, but should include clearer examples, trade-offs, or implementation depth."
    else:
        level = "needs improvement"
        feedback = "The answer is too brief or generic. It needs a concrete example and clearer explanation."

    return {
        "skill": skill,
        "score": score,
        "level": level,
        "feedback": feedback,
        "next_probe": f"Ask for a deeper example of how the candidate would use {skill} in the target role.",
    }


def evaluate_answers(answers: Dict[str, str]) -> Dict:
    results = []

    for skill, answer in answers.items():
        results.append(score_answer(skill, answer))

    average_score = 0
    if results:
        average_score = round(sum(item["score"] for item in results) / len(results), 2)

    return {
        "average_score": average_score,
        "results": results,
    }


def estimate_time(skill: str) -> str:
    advanced = {"langgraph", "rag", "vector database", "kubernetes", "deep learning", "llm"}
    medium = {"fastapi", "react", "docker", "postgresql", "machine learning", "scikit-learn"}

    if skill in advanced:
        return "2-3 weeks"
    if skill in medium:
        return "1-2 weeks"
    return "3-5 days"


def learning_resource_pack(skill: str) -> Dict:
    resource_map = {
        "fastapi": [
            "FastAPI official tutorial",
            "Build a CRUD API with validation and error handling",
            "Deploy the API locally and document it with Swagger",
        ],
        "react": [
            "React official Learn guide",
            "Build a form-driven dashboard with API calls",
            "Practice state management and conditional rendering",
        ],
        "langgraph": [
            "LangGraph official quickstart",
            "Model your workflow as nodes and edges",
            "Add one conditional branch for follow-up assessment",
        ],
        "llm": [
            "Prompting and structured-output basics",
            "Build one JSON-producing extraction prompt",
            "Evaluate outputs with realistic examples",
        ],
        "rag": [
            "RAG overview and chunking basics",
            "Build a small vector search over documents",
            "Add answer citation and relevance scoring",
        ],
        "embeddings": [
            "Sentence embeddings introduction",
            "Compare text with cosine similarity",
            "Experiment with resume/JD similarity examples",
        ],
        "docker": [
            "Docker getting-started guide",
            "Containerize the FastAPI backend",
            "Write a simple compose file for local demo",
        ],
        "scikit-learn": [
            "Scikit-learn getting-started guide",
            "Practice cosine similarity and vector operations",
            "Build a small scoring notebook",
        ],
    }
    return {
        "why_it_matters": f"{skill} appears in the target role gap, so improving it directly increases job readiness.",
        "resources": resource_map.get(
            skill,
            [
                f"Official documentation or beginner guide for {skill}",
                f"One focused hands-on crash course for {skill}",
                f"Build a small role-specific project using {skill}",
            ],
        ),
        "mini_project": f"Create a small portfolio task that proves practical use of {skill} in the target job context.",
    }


def generate_learning_plan(missing_skills: List[str], weak_skills: List[str] = None) -> List[Dict]:
    weak_skills = weak_skills or []
    priority_skills = []

    for skill in missing_skills + weak_skills:
        normalized = normalize_skill(skill)
        if normalized not in priority_skills:
            priority_skills.append(normalized)

    plan = []
    for index, skill in enumerate(priority_skills[:8], start=1):
        resource_pack = learning_resource_pack(skill)
        plan.append(
            {
                "week": index,
                "skill": skill,
                "priority": "High" if index <= 3 else "Medium",
                "why_it_matters": resource_pack["why_it_matters"],
                "goal": f"Build practical confidence in {skill} and show evidence through a small deliverable.",
                "resources": resource_pack["resources"],
                "mini_project": resource_pack["mini_project"],
                "time_estimate": estimate_time(skill),
            }
        )

    if not plan:
        plan.append(
            {
                "week": 1,
                "skill": "interview readiness",
                "priority": "High",
                "why_it_matters": "The resume already covers the detected skills, so the next step is proving depth clearly.",
                "goal": "Practice explaining your strongest projects clearly with role-specific examples.",
                "resources": [
                    "Prepare STAR-format project stories",
                    "Map each job requirement to your experience",
                    "Practice 5 mock technical questions",
                ],
                "mini_project": "Create a one-page project story bank mapped to the job requirements.",
                "time_estimate": "2-3 days",
            }
        )

    return plan


def calculate_text_similarity(jd_text: str, resume_text: str) -> float:
    if not jd_text or not resume_text:
        return 0.0

    jd_embedding = create_embedding(jd_text[:4000])
    resume_embedding = create_embedding(resume_text[:4000])
    return round(calculate_cosine_similarity(jd_embedding, resume_embedding) * 100, 2)


def run_skill_assessment_workflow(jd_text: str, resume_text: str) -> Dict:
    jd_clean = clean_text(jd_text)
    resume_clean = clean_text(resume_text)
    required_skills = extract_skills(jd_clean)
    candidate_skills = extract_skills(resume_clean)
    comparison = compare_skills(required_skills, candidate_skills)

    assessment_focus = comparison["missing_skills"][:3] + comparison["matched_skills"][:3]
    if not assessment_focus:
        assessment_focus = required_skills[:6]

    questions = generate_assessment_questions(assessment_focus)
    learning_plan = generate_learning_plan(comparison["missing_skills"])
    semantic_similarity = calculate_text_similarity(jd_clean, resume_clean)

    return {
        "session_id": make_session_id(),
        "jd_text": jd_clean,
        "resume_text": resume_clean,
        "semantic_similarity": semantic_similarity,
        "questions": questions,
        "learning_plan": learning_plan,
        **comparison,
    }
