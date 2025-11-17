"""Pydantic model for startup profiles."""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

from .common import Stage


class Startup(BaseModel):
    id: str
    name: str
    stage: Stage
    domains: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    mission: Optional[str] = None
    stack: List[str] = Field(default_factory=list)


class StartupCreate(BaseModel):
    name: str
    stage: Stage
    domains: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    mission: Optional[str] = None
    stack: List[str] = Field(default_factory=list)
