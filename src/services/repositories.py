"""In-memory repositories for candidates, startups, and roles.

Thread-safety is not a focus for this demo. For production, replace with a DB
layer and proper locking/transactions.
"""

from __future__ import annotations

from typing import Dict, Optional, List
from uuid import uuid4

from ..models.candidate import Candidate, CandidateCreate
from ..models.startup import Startup, StartupCreate
from ..models.role import Role, RoleCreate


class InMemoryRepo:
    def __init__(self) -> None:
        self.candidates: Dict[str, Candidate] = {}
        self.startups: Dict[str, Startup] = {}
        self.roles: Dict[str, Role] = {}

    # Candidate ops
    def create_candidate(self, payload: CandidateCreate) -> Candidate:
        cid = str(uuid4())
        cand = Candidate(id=cid, **payload.model_dump())
        self.candidates[cid] = cand
        return cand

    def get_candidate(self, cid: str) -> Optional[Candidate]:
        return self.candidates.get(cid)

    def list_candidates(self, ids: Optional[List[str]] = None) -> List[Candidate]:
        if ids is None:
            return list(self.candidates.values())
        return [c for c in self.candidates.values() if c.id in set(ids)]

    # Startup ops
    def create_startup(self, payload: StartupCreate) -> Startup:
        sid = str(uuid4())
        st = Startup(id=sid, **payload.model_dump())
        self.startups[sid] = st
        return st

    def get_startup(self, sid: str) -> Optional[Startup]:
        return self.startups.get(sid)

    def list_startups(self) -> List[Startup]:
        return list(self.startups.values())

    # Role ops
    def create_role(self, payload: RoleCreate) -> Role:
        rid = str(uuid4())
        role = Role(id=rid, **payload.model_dump())
        self.roles[rid] = role
        return role

    def get_role(self, rid: str) -> Optional[Role]:
        return self.roles.get(rid)

    def list_roles(self, startup_id: Optional[str] = None) -> List[Role]:
        roles = list(self.roles.values())
        if startup_id:
            roles = [r for r in roles if r.startup_id == startup_id]
        return roles


# Single, process-local repo instance for the demo app
repo = InMemoryRepo()
