"""Matching endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException

from ..models.match import MatchRequest, MatchResponse
from ..services.repositories import repo
from ..services.matching import rank_candidates


router = APIRouter()


@router.post("/match", response_model=MatchResponse)
def post_match(payload: MatchRequest) -> MatchResponse:
    # Resolve role (by id or inline)
    if payload.role_id:
        role = repo.get_role(payload.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
    elif payload.role:
        role = payload.role
    else:
        raise HTTPException(status_code=400, detail="Provide role_id or role payload")

    # Resolve startup context for stage/domains
    startup = repo.get_startup(role.startup_id)
    startup_domains: List[str] = startup.domains if startup else []
    startup_stage = startup.stage.value if startup else None

    # Candidate scope
    candidates = repo.list_candidates(ids=payload.candidate_ids)
    ranked = rank_candidates(
        candidates, role, startup_domains=startup_domains, startup_stage=startup_stage
    )

    return MatchResponse(role=role, results=ranked[: payload.limit])
