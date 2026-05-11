import os
from utils.llm_client import call_llm, parse_json_response
from utils.helpers import format_candidate_context
from models.schemas import CandidateProfile, AnswerEvaluation, FinalFeedback


def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "coach.txt")
    with open(os.path.normpath(prompt_path), "r") as f:
        return f.read()


def _compute_avg_scores(evaluations: list[AnswerEvaluation]) -> dict:
    """Average per-dimension scores across all evaluated turns."""
    combined: dict[str, list] = {}
    for ev in evaluations:
        for dim, score in ev.scores.items():
            combined.setdefault(dim, []).append(score)
    return {dim: round(sum(vals) / len(vals), 1) for dim, vals in combined.items()}


def generate_feedback(
    candidate: CandidateProfile,
    conversation_history: list,
    evaluations: list[AnswerEvaluation],
) -> FinalFeedback:
    """
    Synthesize all per-turn evaluations into a final coaching report.
    Returns a structured FinalFeedback object.
    """
    system_prompt = load_prompt()
    context = format_candidate_context(candidate.target_role, candidate.background, candidate.focus_area)

    # Serialize evaluations compactly for the coach
    eval_summary = "\n\n".join(
        f"Turn {ev.turn}:\n"
        f"  Q: {ev.question}\n"
        f"  A (quality={ev.answer_quality}): {ev.answer[:200]}{'...' if len(ev.answer) > 200 else ''}\n"
        f"  Strengths: {', '.join(ev.strengths) or 'None noted'}\n"
        f"  Gaps: {', '.join(ev.gaps) or 'None noted'}\n"
        f"  Scores: {ev.scores}"
        for ev in evaluations
    )

    avg_scores = _compute_avg_scores(evaluations)

    messages = [
        {
            "role": "user",
            "content": (
                f"Candidate Profile:\n{context}\n\n"
                f"Per-turn Evaluations:\n{eval_summary}\n\n"
                f"Average dimension scores: {avg_scores}\n\n"
                f"Generate the final coaching feedback report as a JSON object."
            ),
        }
    ]

    raw = call_llm(
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=1200,
        expect_json=True,
    )

    data = parse_json_response(raw)

    if data is None:
        return FinalFeedback(
            overall_rating="Needs Work",
            summary="Could not generate feedback due to a parsing error.",
            strengths=["See transcript for details"],
            gaps=["See transcript for details"],
            action_items=["Review your answers and try again"],
            dimension_scores=avg_scores,
        )

    return FinalFeedback(
        overall_rating=data.get("overall_rating", "Needs Work"),
        summary=data.get("summary", ""),
        strengths=data.get("strengths", []),
        gaps=data.get("gaps", []),
        action_items=data.get("action_items", []),
        dimension_scores=data.get("dimension_scores", avg_scores),
    )