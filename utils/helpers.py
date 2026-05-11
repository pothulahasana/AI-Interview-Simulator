from typing import List
from models.schemas import AnswerEvaluation, FinalFeedback


def format_candidate_context(target_role: str, background: str | None, focus_area: str) -> str:
    """Build a candidate context block to inject into prompts."""
    lines = [
        f"Target Role: {target_role}",
        f"Focus Area: {focus_area}",
    ]
    if background:
        lines.append(f"Candidate Background: {background}")
    return "\n".join(lines)


def format_conversation_for_display(history: List[dict]) -> str:
    """Pretty-print conversation history for CLI display."""
    lines = []
    for msg in history:
        role = "Interviewer" if msg["role"] == "assistant" else "You"
        lines.append(f"\n[{role}]\n{msg['content']}\n")
    return "\n".join(lines)


def format_final_feedback(feedback: FinalFeedback) -> str:
    """Render the final feedback report as a readable CLI string."""
    sep = "─" * 60
    lines = [
        "",
        sep,
        "  INTERVIEW FEEDBACK REPORT",
        sep,
        f"\nOverall Rating:  {feedback.overall_rating}",
        f"\nSummary:\n  {feedback.summary}",
        "\nStrengths:",
    ]
    for s in feedback.strengths:
        lines.append(f"  ✓ {s}")

    lines.append("\nGaps:")
    for g in feedback.gaps:
        lines.append(f"  ✗ {g}")

    lines.append("\nAction Items (what to practice):")
    for i, a in enumerate(feedback.action_items, 1):
        lines.append(f"  {i}. {a}")

    lines.append("\nDimension Scores (avg across all turns):")
    for dim, score in feedback.dimension_scores.items():
        bar = "█" * int(score) + "░" * (5 - int(score))
        lines.append(f"  {dim:<20} {bar}  {score:.1f}/5")

    lines.append(f"\n{sep}\n")
    return "\n".join(lines)


def print_separator(label: str = "") -> None:
    sep = "─" * 60
    if label:
        print(f"\n{sep}")
        print(f"  {label}")
        print(f"{sep}")
    else:
        print(f"\n{sep}")