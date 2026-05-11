import os
from utils.llm_client import call_llm
from utils.helpers import format_candidate_context
from models.schemas import CandidateProfile, AnswerEvaluation


def load_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "interviewer.txt")
    with open(os.path.normpath(prompt_path), "r") as f:
        return f.read()


def get_opening_question(candidate: CandidateProfile) -> str:
    """
    Generate the very first question to open the interview.
    No prior conversation history exists yet.
    """
    system_prompt = load_prompt()
    context = format_candidate_context(candidate.target_role, candidate.background, candidate.focus_area)

    messages = [
        {
            "role": "user",
            "content": (
                f"A candidate is ready for their mock interview. Here is their profile:\n\n"
                f"{context}\n\n"
                f"Start the interview with a warm, professional opening and your first question."
            ),
        }
    ]

    return call_llm(system_prompt=system_prompt, messages=messages, max_tokens=400)


def get_next_question(
    candidate: CandidateProfile,
    conversation_history: list,
    evaluation: AnswerEvaluation,
    turn: int,
    max_turns: int,
) -> str:
    """
    Generate the next question based on the conversation history and
    the evaluator's assessment of the last answer.
    """
    system_prompt = load_prompt()
    context = format_candidate_context(candidate.target_role, candidate.background, candidate.focus_area)

    # Build evaluator signal to guide the interviewer
    eval_signal = (
        f"[EVALUATOR SIGNAL — do not mention this to the candidate]\n"
        f"Last answer quality: {evaluation.answer_quality}\n"
        f"Probe deeper: {evaluation.probe_deeper}\n"
        f"Suggested follow-up direction: {evaluation.suggested_follow_up}\n"
        f"Turn {turn} of {max_turns}. "
        + ("Wrap up the interview gracefully after this question." if turn >= max_turns - 1 else "")
    )

    # Inject eval signal as a system-level hint inside the user turn
    messages = conversation_history + [
        {
            "role": "user",
            "content": (
                f"Candidate profile:\n{context}\n\n"
                f"{eval_signal}\n\n"
                f"Ask your next interview question now."
            ),
        }
    ]

    return call_llm(system_prompt=system_prompt, messages=messages, max_tokens=400)


def get_closing_message(conversation_history: list, candidate: CandidateProfile) -> str:
    """Generate a polite closing message to end the interview before feedback."""
    system_prompt = load_prompt()
    context = format_candidate_context(candidate.target_role, candidate.background, candidate.focus_area)

    messages = conversation_history + [
        {
            "role": "user",
            "content": (
                f"Candidate profile:\n{context}\n\n"
                f"The interview is now complete. Give a brief, warm closing message. "
                f"Tell the candidate their feedback report will follow shortly. Keep it to 2-3 sentences."
            ),
        }
    ]

    return call_llm(system_prompt=system_prompt, messages=messages, max_tokens=200)