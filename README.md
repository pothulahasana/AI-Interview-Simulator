# AI Mock Interview Coach

A multi-agent AI system that conducts realistic mock interviews and delivers structured coaching feedback.

---

## Setup

**Prerequisites:** Python 3.11+

```bash
# 1. Clone or unzip the project
cd ai-mock-interview-coach

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here   # Windows: set ANTHROPIC_API_KEY=your_key_here

# 5. Run the interview
python main.py
```

---

## Architecture

The system uses **3 distinct agents** orchestrated by a central `InterviewSession` controller.

### Agent 1 — Interviewer (`agents/interviewer.py`)
Conducts the interview. Asks one question per turn, adapts based on the evaluator's signal (probe deeper vs. move on), calibrates difficulty, and closes the session warmly. Uses the full conversation history as context so each question feels like a natural continuation.

### Agent 2 — Evaluator/Shadow (`agents/evaluator.py`)
Silent scorer. After each candidate answer, it evaluates the response across 5 dimensions (clarity, depth, relevance, structure, confidence) and returns a structured JSON with strengths, gaps, a quality classification, and a follow-up signal. The candidate never sees this output — it feeds directly into the Interviewer's next question.

### Agent 3 — Coach/Mentor (`agents/coach.py`)
Activated only at the end. Synthesizes all per-turn evaluations into a final feedback report: overall rating, top 3 strengths, top 3 gaps, and 3 specific actionable items to practice.

### Orchestration (`orchestrator/session.py`)
```
Interviewer → asks question
     ↓
Candidate answers
     ↓
Evaluator → scores answer (silent)
     ↓
Orchestrator decides: probe_deeper? → Interviewer adjusts next question
     ↓
Repeat until max_turns
     ↓
Coach → generates final report
```

---

## Key Design Decisions

**Why separate Evaluator/Shadow from Interviewer?**  
Mixing scoring logic into the Interviewer prompt creates conflicting objectives. A dedicated Evaluator can be calibrated independently and produces clean, structured output that the Interviewer can act on without over-thinking.

**Evaluator/Shadow signal injection**  
Rather than giving the Interviewer raw scores, we inject a compact signal: `answer_quality`, `probe_deeper`, and `suggested_follow_up`. This gives the Interviewer just enough context to adapt without anchoring it to a number.

**JSON for Evaluator/Shadow + Coach/Mentor**  
Both agents that produce structured data return strict JSON. This makes the outputs machine-readable and prevents the agents from adding unnecessary prose that would bloat the context.

**Prompt files are decoupled from code**  
All agent prompts live in `prompts/` as plain text files. You can iterate on prompts without touching Python code.

**Graceful degradation**  
If the Evaluator or Coach returns malformed JSON, the system falls back to a neutral default rather than crashing the session.

---

## Example Transcripts

### Transcript 1 — Strong Candidate (Product Manager role, Behavioral)

```
[Interviewer]
Welcome! I'm excited to chat with you today about the Product Manager role.
To get us started: tell me about a product decision you made that turned out
to be wrong. What happened, and what did you learn?

You: In my last role I pushed hard to ship a notification feature earlier than
the team was comfortable with. We had data showing users wanted it, but we cut
corners on the permission UX. Post-launch, 30% of users disabled notifications
in the first week — which is the opposite of what we wanted. I learned that
speed is only valuable if the feature actually works for users. After that I
started requiring a "launch readiness" checklist on every feature, including a
UX walkthrough sign-off.

[Interviewer]
That's a clear and honest example. You mentioned introducing a launch
readiness checklist — how did you get the team to actually adopt it
given that it adds friction to shipping?

You: Honestly the checklist itself wasn't the hard part — framing it was.
I stopped calling it a gate and started framing it as a "pre-mortem lite."
I also kept it to 6 items max so it felt lightweight. Within two sprints it
became habit. I also made a point of publicly crediting it when it caught
a real issue before launch.

[Interviewer]
Great. Let's shift topic. Tell me about a time you had to align stakeholders
who had fundamentally different priorities.

...

[FEEDBACK REPORT]
Overall Rating: Excellent
Summary: Strong structured thinking, clear ownership, and consistent use of
specific examples. Ready to interview for mid-level PM roles.
Strengths: Owns mistakes cleanly, shows systems thinking (checklist),
demonstrates stakeholder awareness.
Gaps: Could push further on metrics/impact quantification.
Action Items: ...
```

---

### Transcript 2 — Weak Candidate (Data Analyst, Technical)

```
[Interviewer]
Let's get started. Walk me through how you would approach investigating
a sudden 20% drop in DAU reported in your dashboard.

You: I would look at the data and see what's going on. Maybe check if
it's a real drop or a tracking issue. Then I'd tell my manager.

[Evaluator signal: weak, probe_deeper=true]

[Interviewer]
Okay, let's dig in. What specifically would you check first to determine
if it's a tracking issue versus a real drop in users?

You: I guess I'd check... the logs? Or maybe the database.

[Evaluator signal: weak, probe_deeper=false — no further depth available]

[Interviewer]
Let's move on. Tell me about a time you had to communicate a
complex analysis to a non-technical audience.

You: I once made a presentation with charts and explained things in
simple terms. People seemed to understand it.

...

[FEEDBACK REPORT]
Overall Rating: Needs Work
Summary: Answers were consistently surface-level with no structured
diagnostic approach or concrete examples. Significant prep needed.
Gaps: No framework for root cause analysis, no specific technical methods
cited, no quantified examples.
Action Items: Practice the "funnel-down" debugging framework for data
anomalies. Study SQL window functions and cohort analysis. Prepare 3
STAR-format stories with specific metrics.
```

---

### Transcript 3 — Edge Case (Frontend Engineer Intern, Mixed — "I don't know" answers)

```
[Interviewer]
Let's start with something technical. Can you explain what the virtual
DOM is and why React uses it?

You: I honestly don't know what the virtual DOM is. I've used React
but never looked into how it works under the hood.

[Evaluator signal: incomplete — redirected gracefully]

[Interviewer]
No problem — let's approach it differently. When you've used React,
have you noticed anything about how the UI updates when state changes?
What does that feel like from a developer's perspective?

You: Yeah, it just re-renders the component. It happens fast even when
there's a lot of stuff on the screen. I always assumed React was just
really optimized.

[Interviewer]
That's a fair observation — you're actually describing the benefit of
the virtual DOM without knowing the name. Good instinct. Let's switch
to behavioral: tell me about a bug you spent a long time debugging.

...

[FEEDBACK REPORT]
Overall Rating: Good
Summary: Showed intellectual honesty and strong instincts even when
missing formal knowledge. The "I don't know but here's what I observe"
pattern is actually a green flag for a learning environment.
Strengths: Intellectual honesty, good instincts, coachable under pressure.
Gaps: Gaps in CS fundamentals (DOM, browser rendering), limited exposure
to debugging methodology.
Action Items: Study browser rendering pipeline and virtual DOM. Practice
explaining concepts you "just know" in structured terms.
```
