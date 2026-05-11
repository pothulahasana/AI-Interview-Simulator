import os
import sys
from models.schemas import CandidateProfile, FocusArea
from orchestrator.session import InterviewSession


FOCUS_OPTIONS = {
    "1": FocusArea.BEHAVIORAL,
    "2": FocusArea.TECHNICAL,
    "3": FocusArea.CASE,
    "4": FocusArea.MIXED,
}


def prompt_candidate_profile() -> CandidateProfile:
    print("\n" + "═" * 60)
    print("  AI MOCK INTERVIEW COACH")
    print("═" * 60)
    print("  Powered by multi-agent AI\n")

    target_role = input("What role are you interviewing for?\n> ").strip()
    if not target_role:
        print("Role cannot be empty.")
        sys.exit(1)

    print("\nOptional: Paste a 1-3 line background / resume snippet.")
    print("(Press Enter to skip)")
    background = input("> ").strip() or None

    print("\nSelect focus area for this session:")
    print("  1. Behavioral")
    print("  2. Technical")
    print("  3. Case")
    print("  4. Mixed")
    choice = input("> ").strip()

    if choice not in FOCUS_OPTIONS:
        print("Invalid choice — defaulting to Mixed.")
        focus_area = FocusArea.MIXED
    else:
        focus_area = FOCUS_OPTIONS[choice]

    print("\nHow many questions? (default: 6, max: 10)")
    turns_input = input("> ").strip()
    try:
        max_turns = max(2, min(10, int(turns_input)))
    except ValueError:
        max_turns = 6

    return CandidateProfile(
        target_role=target_role,
        background=background,
        focus_area=focus_area,
    ), max_turns



def check_api_key():
    if not os.environ.get("GROQ_API_KEY"):
        print("\n[ERROR] GROQ_API_KEY environment variable is not set.")
        print("Set it with: $env:GROQ_API_KEY='your_key_here'\n")
        sys.exit(1)


def main():
    check_api_key()

    candidate, max_turns = prompt_candidate_profile()

    print("\n[Press Enter when you're ready to begin your interview...]")
    input()

    session = InterviewSession(candidate=candidate, max_turns=max_turns)

    try:
        session.run()
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()