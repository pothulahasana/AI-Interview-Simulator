from models.schemas import CandidateProfile, SessionState, FinalFeedback
from agents import interviewer, evaluator, coach
from utils.helpers import format_final_feedback, print_separator


class InterviewSession:
    """
    Orchestrates the full mock interview lifecycle:
      1. Interviewer asks the opening question
      2. Candidate answers
      3. Evaluator scores the answer (silent)
      4. Orchestrator decides: probe deeper or move on
      5. Interviewer asks next question (informed by evaluator signal)
      6. Repeat until max_turns reached
      7. Coach synthesizes all evaluations into a final report
    """

    def __init__(self, candidate: CandidateProfile, max_turns: int = 6):
        self.state = SessionState(candidate=candidate, max_turns=max_turns)

    def _add_to_history(self, role: str, content: str):
        self.state.conversation_history.append({"role": role, "content": content})

    def run(self):
        """Main loop — runs the full interview interactively via CLI."""
        candidate = self.state.candidate

        print_separator("MOCK INTERVIEW SESSION")
        print(f"  Role: {candidate.target_role}")
        print(f"  Focus: {candidate.focus_area.value.capitalize()}")
        if candidate.background:
            print(f"  Background: {candidate.background}")
        print_separator()

        # ── Turn 0: Opening question ──────────────────────────────────────
        print("\n[Generating opening question...]\n")
        opening = interviewer.get_opening_question(candidate)
        self._add_to_history("assistant", opening)

        print(f"[Interviewer]\n{opening}\n")

        # ── Main interview loop ───────────────────────────────────────────
        while self.state.turn < self.state.max_turns:
            self.state.turn += 1

            # Get candidate answer
            answer = input("You: ").strip()
            if not answer:
                print("(No answer provided — please type your response.)")
                self.state.turn -= 1
                continue

            self._add_to_history("user", answer)

            # Silent evaluation
            current_question = self.state.conversation_history[-2]["content"]
            print("\n[Evaluating...]\n")

            eval_result = evaluator.evaluate_answer(
                candidate=candidate,
                question=current_question,
                answer=answer,
                turn=self.state.turn,
                conversation_history=self.state.conversation_history,
            )
            self.state.evaluations.append(eval_result)

            # Check if interview is done
            if self.state.turn >= self.state.max_turns:
                break

            # Interviewer asks next question (guided by evaluator signal)
            next_q = interviewer.get_next_question(
                candidate=candidate,
                conversation_history=self.state.conversation_history,
                evaluation=eval_result,
                turn=self.state.turn,
                max_turns=self.state.max_turns,
            )
            self._add_to_history("assistant", next_q)
            print(f"\n[Interviewer]\n{next_q}\n")

        # ── Closing ───────────────────────────────────────────────────────
        closing = interviewer.get_closing_message(
            conversation_history=self.state.conversation_history,
            candidate=candidate,
        )
        print(f"\n[Interviewer]\n{closing}\n")
        self._add_to_history("assistant", closing)

        # ── Final feedback ────────────────────────────────────────────────
        print("\n[Generating your feedback report...]\n")
        feedback: FinalFeedback = coach.generate_feedback(
            candidate=candidate,
            conversation_history=self.state.conversation_history,
            evaluations=self.state.evaluations,
        )

        print(format_final_feedback(feedback))
        self.state.is_complete = True

        return feedback