from typing import Dict, List, TypedDict

from app.agent_utils import (
    clean_text,
    compare_skills,
    extract_skills,
    generate_assessment_questions,
    generate_learning_plan,
    generate_readiness_summary,
    make_session_id,
    calculate_text_similarity,
)


class AgentState(TypedDict, total=False):
    session_id: str
    jd_text: str
    resume_text: str
    required_skills: List[str]
    candidate_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    match_score: float
    semantic_similarity: float
    questions: List[Dict]
    learning_plan: List[Dict]
    workflow_engine: str
    workflow_steps: List[str]
    readiness_summary: Dict


WORKFLOW_STEPS = [
    "clean_inputs",
    "extract_required_skills",
    "extract_candidate_skills",
    "compare_skill_gap",
    "summarize_readiness",
    "generate_assessment_questions",
    "generate_learning_plan",
]


def clean_inputs_node(state: AgentState) -> AgentState:
    state["session_id"] = make_session_id()
    state["jd_text"] = clean_text(state.get("jd_text", ""))
    state["resume_text"] = clean_text(state.get("resume_text", ""))
    return state


def extract_required_skills_node(state: AgentState) -> AgentState:
    state["required_skills"] = extract_skills(state["jd_text"])
    return state


def extract_candidate_skills_node(state: AgentState) -> AgentState:
    state["candidate_skills"] = extract_skills(state["resume_text"])
    return state


def compare_skill_gap_node(state: AgentState) -> AgentState:
    comparison = compare_skills(
        state.get("required_skills", []),
        state.get("candidate_skills", []),
    )
    state.update(comparison)
    state["semantic_similarity"] = calculate_text_similarity(
        state["jd_text"],
        state["resume_text"],
    )
    return state


def summarize_readiness_node(state: AgentState) -> AgentState:
    state["readiness_summary"] = generate_readiness_summary(
        {
            "match_score": state.get("match_score", 0),
            "matched_skills": state.get("matched_skills", []),
            "missing_skills": state.get("missing_skills", []),
        },
        state.get("semantic_similarity", 0),
    )
    return state


def generate_questions_node(state: AgentState) -> AgentState:
    assessment_focus = state.get("missing_skills", [])[:3] + state.get("matched_skills", [])[:3]
    if not assessment_focus:
        assessment_focus = state.get("required_skills", [])[:6]

    state["questions"] = generate_assessment_questions(assessment_focus)
    return state


def generate_plan_node(state: AgentState) -> AgentState:
    state["learning_plan"] = generate_learning_plan(state.get("missing_skills", []))
    return state


def run_sequential_workflow(jd_text: str, resume_text: str) -> Dict:
    state: AgentState = {
        "jd_text": jd_text,
        "resume_text": resume_text,
        "workflow_engine": "sequential fallback",
        "workflow_steps": WORKFLOW_STEPS,
    }

    for node in [
        clean_inputs_node,
        extract_required_skills_node,
        extract_candidate_skills_node,
        compare_skill_gap_node,
        summarize_readiness_node,
        generate_questions_node,
        generate_plan_node,
    ]:
        state = node(state)

    return dict(state)


def build_langgraph_workflow():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentState)
    graph.add_node("clean_inputs", clean_inputs_node)
    graph.add_node("extract_required_skills", extract_required_skills_node)
    graph.add_node("extract_candidate_skills", extract_candidate_skills_node)
    graph.add_node("compare_skill_gap", compare_skill_gap_node)
    graph.add_node("summarize_readiness", summarize_readiness_node)
    graph.add_node("generate_assessment_questions", generate_questions_node)
    graph.add_node("generate_learning_plan", generate_plan_node)

    graph.set_entry_point("clean_inputs")
    graph.add_edge("clean_inputs", "extract_required_skills")
    graph.add_edge("extract_required_skills", "extract_candidate_skills")
    graph.add_edge("extract_candidate_skills", "compare_skill_gap")
    graph.add_edge("compare_skill_gap", "summarize_readiness")
    graph.add_edge("summarize_readiness", "generate_assessment_questions")
    graph.add_edge("generate_assessment_questions", "generate_learning_plan")
    graph.add_edge("generate_learning_plan", END)

    return graph.compile()


def run_agent_graph(jd_text: str, resume_text: str) -> Dict:
    try:
        app = build_langgraph_workflow()
        result = app.invoke(
            {
                "jd_text": jd_text,
                "resume_text": resume_text,
                "workflow_engine": "langgraph",
                "workflow_steps": WORKFLOW_STEPS,
            }
        )
        return dict(result)
    except ImportError:
        return run_sequential_workflow(jd_text, resume_text)
