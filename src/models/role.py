"""Pydantic model for roles at startups."""

from typing import List, Optional
from pydantic import BaseModel, Field

from .common import Seniority


class Role(BaseModel):
    id: str
    startup_id: str
    title: str
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    min_years_experience: int = 0
    responsibilities: List[str] = Field(default_factory=list)
    seniority: Seniority = Seniority.vp
    location_preference: Optional[str] = None
    remote_ok: bool = True
    compensation_range: Optional[str] = None
    recruiter_notes: Optional[str] = None


class RoleCreate(BaseModel):
    startup_id: str
    title: str
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    min_years_experience: int = 0
    responsibilities: List[str] = Field(default_factory=list)
    seniority: Seniority = Seniority.vp
    location_preference: Optional[str] = None
    remote_ok: bool = True
    compensation_range: Optional[str] = None
    recruiter_notes: Optional[str] = None
