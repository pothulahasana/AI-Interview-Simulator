import os
import json
from utils.llm_client import call_llm, parse_json_response
from utils.helpers import format_candidate_context
from models.schemas import CandidateProfile, AnswerEvaluation


def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "evaluator.txt")
    with open(os.path.normpath(prompt_path), "r") as f:
        return f.read()


def evaluate_answer(
    candidate: CandidateProfile,
    question: str,
    answer: str,
    turn: int,
    conversation_history: list,
) -> AnswerEvaluation:
    """
    Evaluate the candidate's answer to a single question.
    Returns a structured AnswerEvaluation with scores and a follow-up signal.
    """
    system_prompt = load_prompt()
    context = format_candidate_context(candidate.target_role, candidate.background, candidate.focus_area)

    messages = [
        {
            "role": "user",
            "content": (
                f"Candidate Profile:\n{context}\n\n"
                f"Question asked (turn {turn}):\n{question}\n\n"
                f"Candidate's answer:\n{answer}\n\n"
                f"Evaluate the answer and return your assessment as a JSON object."
            ),
        }
    ]

    raw = call_llm(
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=800,
        expect_json=True,
    )

    data = parse_json_response(raw)

    if data is None:
        # Fallback: return a neutral evaluation so the session doesn't crash
        return AnswerEvaluation(
            turn=turn,
            question=question,
            answer=answer,
            scores={"clarity": 3, "depth": 3, "relevance": 3},
            strengths=["Could not parse evaluation"],
            gaps=[],
            answer_quality="adequate",
            suggested_follow_up="Ask a standard follow-up question.",
            probe_deeper=False,
        )

    return AnswerEvaluation(
        turn=turn,
        question=question,
        answer=answer,
        scores=data.get("scores", {}),
        strengths=data.get("strengths", []),
        gaps=data.get("gaps", []),
        answer_quality=data.get("answer_quality", "adequate"),
        suggested_follow_up=data.get("suggested_follow_up", ""),
        probe_deeper=data.get("probe_deeper", False),
    )