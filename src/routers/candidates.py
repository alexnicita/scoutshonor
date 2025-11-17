"""Candidates CRUD endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException

from ..services.repositories import repo
from ..models.candidate import Candidate, CandidateCreate


router = APIRouter()


@router.post("/", response_model=Candidate)
def create_candidate(payload: CandidateCreate) -> Candidate:
    return repo.create_candidate(payload)


@router.get("/", response_model=List[Candidate])
def list_candidates() -> List[Candidate]:
    return repo.list_candidates()


@router.get("/{candidate_id}", response_model=Candidate)
def get_candidate(candidate_id: str) -> Candidate:
    c = repo.get_candidate(candidate_id)
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return c
