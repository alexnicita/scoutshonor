"""FastAPI application wiring routers and in-memory repos.

Purpose:
  Expose endpoints for health, startups, roles, candidates, matching, and
  outreach using a simple in-memory repository. Suitable for local testing
  and demos; swap the repo layer for persistence later.
"""

from fastapi import FastAPI

from .routers import (
    health,
    startups,
    roles,
    candidates,
    match,
    outreach,
    sourcing,
    descriptions,
)


app = FastAPI(title="Scoutshonor API")

# Basic status
app.include_router(health.router, tags=["health"])

# CRUD and business logic
app.include_router(startups.router, prefix="/startups", tags=["startups"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
app.include_router(match.router, tags=["match"])
app.include_router(outreach.router, tags=["outreach"])
app.include_router(sourcing.router, tags=["sourcing"])
app.include_router(descriptions.router, tags=["descriptions"])
