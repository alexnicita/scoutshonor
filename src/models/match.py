"""Models for matching requests and results."""

from typing import List, Optional
from pydantic import BaseModel, Field

from .candidate import Candidate
from .role import Role


class ScoreBreakdown(BaseModel):
    skills: float = 0.0
    seniority: float = 0.0
    experience: float = 0.0
    stage: float = 0.0
    domain: float = 0.0
    location: float = 0.0
    title: float = 0.0


class MatchResult(BaseModel):
    candidate: Candidate
    score: float
    breakdown: ScoreBreakdown
    reasons: List[str] = Field(default_factory=list)


class MatchRequest(BaseModel):
    # Either role_id references an existing role, or provide a role payload inline.
    role_id: Optional[str] = None
    role: Optional[Role] = None
    candidate_ids: Optional[List[str]] = None
    limit: int = 10


class MatchResponse(BaseModel):
    role: Role
    results: List[MatchResult]
