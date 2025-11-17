"""Models for long job description generation.

Purpose:
  Define request/response schemas for generating rich job descriptions
  from minimal user input. Used by the descriptions service and API router.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .common import Seniority, Stage


class JobDescriptionInput(BaseModel):
    # Minimal required inputs
    title: str
    seniority: Seniority = Seniority.vp

    # Company context (optional but helpful)
    startup_id: Optional[str] = None
    startup_name: Optional[str] = None
    stage: Optional[Stage] = None
    mission: Optional[str] = None
    product_description: Optional[str] = None
    team_description: Optional[str] = None

    # Role details
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    min_years_experience: int = 0

    # Logistics
    location: Optional[str] = None
    remote_ok: bool = True
    employment_type: Optional[str] = None  # e.g., full-time, contract
    compensation_range: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)


class JobDescriptionResponse(BaseModel):
    title: str
    description: str
