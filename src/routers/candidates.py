"""Candidates CRUD endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

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


@router.post("/bulk", response_model=List[Candidate])
def bulk_create(candidates: List[CandidateCreate]) -> List[Candidate]:
    created: List[Candidate] = []
    for payload in candidates:
        created.append(repo.create_candidate(payload))
    return created


@router.get("/search", response_model=List[Candidate])
def search_candidates(
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    titles: Optional[str] = Query(None, description="Comma-separated titles"),
    domains: Optional[str] = Query(None, description="Comma-separated domains"),
    location: Optional[str] = Query(None, description="Exact location match"),
) -> List[Candidate]:
    def split_csv(v: Optional[str]) -> List[str]:
        return [x.strip() for x in v.split(",")] if v else []

    return repo.search_candidates(
        skills=split_csv(skills),
        titles=split_csv(titles),
        domains=split_csv(domains),
        location=location,
    )
