"""Sourcing endpoints (boolean/X-Ray string generation)."""

from fastapi import APIRouter, HTTPException

from ..models.sourcing import BooleanRequest, BooleanResponse
from ..services.repositories import repo
from ..services.sourcing import build_boolean_strings


router = APIRouter()


@router.post("/sourcing/boolean", response_model=BooleanResponse)
def post_boolean(payload: BooleanRequest) -> BooleanResponse:
    # Resolve role by id or inline
    if payload.role_id:
        role = repo.get_role(payload.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
    elif payload.role:
        role = payload.role
    else:
        raise HTTPException(status_code=400, detail="Provide role_id or role payload")

    strings = build_boolean_strings(
        role=role, locations=payload.locations, extras=payload.extras
    )
    return BooleanResponse(**strings)

