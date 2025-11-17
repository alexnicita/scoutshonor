"""Models for sourcing helpers (boolean search generation)."""

from typing import List, Optional
from pydantic import BaseModel

from .role import Role


class BooleanRequest(BaseModel):
    role_id: Optional[str] = None
    role: Optional[Role] = None
    locations: List[str] = []
    extras: List[str] = []


class BooleanResponse(BaseModel):
    linkedin: str
    google_xray: str
    github: str
