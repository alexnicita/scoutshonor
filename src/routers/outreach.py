"""Outreach endpoints."""

from fastapi import APIRouter, HTTPException

from ..models.outreach import OutreachRequest, OutreachResponse
from ..services.repositories import repo
from ..services.outreach import generate_messages


router = APIRouter()


@router.post("/outreach", response_model=OutreachResponse)
def post_outreach(payload: OutreachRequest) -> OutreachResponse:
    cand = repo.get_candidate(payload.candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    role = repo.get_role(payload.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    startup = repo.get_startup(role.startup_id)
    startup_name = startup.name if startup else "Your startup"

    msgs = generate_messages(
        candidate=cand,
        role=role,
        startup_name=startup_name,
        tone=payload.tone,
        channels=payload.channels,
        cal_link=payload.add_cal_link,
    )
    return OutreachResponse(messages=msgs)
