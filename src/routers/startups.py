"""Startups CRUD endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException

from ..services.repositories import repo
from ..models.startup import Startup, StartupCreate


router = APIRouter()


@router.post("/", response_model=Startup)
def create_startup(payload: StartupCreate) -> Startup:
    return repo.create_startup(payload)


@router.get("/", response_model=List[Startup])
def list_startups() -> List[Startup]:
    return repo.list_startups()


@router.get("/{startup_id}", response_model=Startup)
def get_startup(startup_id: str) -> Startup:
    st = repo.get_startup(startup_id)
    if not st:
        raise HTTPException(status_code=404, detail="Startup not found")
    return st
