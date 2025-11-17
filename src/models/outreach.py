"""Models for outreach message generation."""

from typing import List, Optional
from pydantic import BaseModel

from .common import Tone, Channel


class OutreachRequest(BaseModel):
    candidate_id: str
    role_id: str
    tone: Tone = "professional"
    channels: List[Channel] = ["email"]
    add_cal_link: Optional[str] = None


class OutreachMessage(BaseModel):
    channel: Channel
    subject: str
    body: str


class OutreachResponse(BaseModel):
    messages: List[OutreachMessage]
