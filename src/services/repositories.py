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

    def search_candidates(
        self,
        skills: Optional[List[str]] = None,
        titles: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        location: Optional[str] = None,
    ) -> List[Candidate]:
        skills_s = {s.strip().lower() for s in (skills or []) if s}
        titles_s = {t.strip().lower() for t in (titles or []) if t}
        domains_s = {d.strip().lower() for d in (domains or []) if d}
        loc = (location or "").strip().lower()

        def matches(c: Candidate) -> bool:
            if skills_s:
                cand_sk = {s.strip().lower() for s in c.skills}
                if not skills_s.issubset(cand_sk):
                    return False
            if titles_s:
                cand_titles = [*(c.titles or []), c.current_title or ""]
                cand_titles_s = {t.strip().lower() for t in cand_titles if t}
                if not (titles_s & cand_titles_s):
                    return False
            if domains_s:
                cand_domains = {d.strip().lower() for d in c.domains}
                if not (domains_s & cand_domains):
                    return False
            if loc:
                cand_locs = {l.strip().lower() for l in c.locations}
                if loc not in cand_locs:
                    return False
            return True

        return [c for c in self.candidates.values() if matches(c)]

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
