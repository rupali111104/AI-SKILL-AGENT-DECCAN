import re
from typing import Dict, List


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
    "sentence transformers",
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
    "sentence-transformers": "sentence transformers",
}


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
    required_set = {normalize_skill(skill) for skill in required_skills}
    candidate_set = {normalize_skill(skill) for skill in candidate_skills}
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
