"""Job description generation endpoints."""

from fastapi import APIRouter

from ..models.descriptions import JobDescriptionInput, JobDescriptionResponse
from ..services.descriptions import generate_description


router = APIRouter()


@router.post("/descriptions/generate", response_model=JobDescriptionResponse)
def post_generate_description(payload: JobDescriptionInput) -> JobDescriptionResponse:
    return generate_description(payload)
