"""Pydantic model for candidate profiles."""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

from .common import Stage


class Candidate(BaseModel):
    id: str = Field(..., description="Unique candidate ID")
    full_name: str
    current_title: Optional[str] = None
    titles: List[str] = Field(default_factory=list, description="Past titles")
    years_experience: int = 0
    skills: List[str] = Field(default_factory=list)
    domains: List[str] = Field(
        default_factory=list, description="Industry/domain expertise"
    )
    locations: List[str] = Field(
        default_factory=list,
        description="City/region strings the candidate is linked to",
    )
    timezone: Optional[str] = None
    remote_preference: Optional[bool] = None
    stage_preferences: List[Stage] = Field(default_factory=list)
    linkedin_url: Optional[HttpUrl] = None
    email: Optional[str] = None


class CandidateCreate(BaseModel):
    full_name: str
    current_title: Optional[str] = None
    titles: List[str] = Field(default_factory=list)
    years_experience: int = 0
    skills: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    timezone: Optional[str] = None
    remote_preference: Optional[bool] = None
    stage_preferences: List[Stage] = Field(default_factory=list)
    linkedin_url: Optional[HttpUrl] = None
    email: Optional[str] = None
