"""Roles CRUD endpoints."""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException

from ..services.repositories import repo
from ..models.role import Role, RoleCreate


router = APIRouter()


@router.post("/", response_model=Role)
def create_role(payload: RoleCreate) -> Role:
    # Validate startup exists
    if not repo.get_startup(payload.startup_id):
        raise HTTPException(status_code=400, detail="Startup does not exist")
    return repo.create_role(payload)


@router.get("/", response_model=List[Role])
def list_roles(startup_id: Optional[str] = None) -> List[Role]:
    return repo.list_roles(startup_id)


@router.get("/{role_id}", response_model=Role)
def get_role(role_id: str) -> Role:
    r = repo.get_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    return r
