from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class FocusArea(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    CASE = "case"
    MIXED = "mixed"


class CandidateProfile(BaseModel):
    target_role: str = Field(..., description="The role the candidate is interviewing for")
    background: Optional[str] = Field(None, description="Optional 2-3 line background or resume snippet")
    focus_area: FocusArea = Field(..., description="Focus area for this interview session")


class AnswerEvaluation(BaseModel):
    turn: int = Field(..., description="Which turn number this evaluation is for")
    question: str = Field(..., description="The question that was asked")
    answer: str = Field(..., description="The candidate's answer")
    scores: dict = Field(..., description="Dimension-wise scores, e.g. {clarity: 3, depth: 2, ...}")
    strengths: List[str] = Field(default_factory=list, description="What the candidate did well")
    gaps: List[str] = Field(default_factory=list, description="Where the candidate fell short")
    answer_quality: str = Field(..., description="One of: strong / adequate / weak / off-topic / incomplete")
    suggested_follow_up: str = Field(..., description="Suggested follow-up question for the interviewer")
    probe_deeper: bool = Field(..., description="True if the interviewer should probe deeper on this answer")


class SessionState(BaseModel):
    candidate: CandidateProfile
    turn: int = Field(default=0, description="Current turn number (0-indexed)")
    max_turns: int = Field(default=6, description="Max number of interview turns")
    conversation_history: List[dict] = Field(default_factory=list, description="Full conversation history")
    evaluations: List[AnswerEvaluation] = Field(default_factory=list, description="All evaluations so far")
    is_complete: bool = Field(default=False, description="Whether the interview is done")


class FinalFeedback(BaseModel):
    overall_rating: str = Field(..., description="Overall rating: Excellent / Good / Needs Work / Poor")
    summary: str = Field(..., description="1-2 sentence overall impression")
    strengths: List[str] = Field(..., description="Top 3 strengths demonstrated")
    gaps: List[str] = Field(..., description="Top 3 areas to improve")
    action_items: List[str] = Field(..., description="Specific, actionable things to practice")
    dimension_scores: dict = Field(..., description="Average scores across all dimensions")