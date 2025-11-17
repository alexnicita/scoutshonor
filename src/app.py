"""
Main FastAPI application for the AI Tech Exec Recruiter.

Wires together routers for candidates, startups, roles, matching, and outreach.
Relies on in-memory repositories; swap with a database-backed implementation later.
"""

from fastapi import FastAPI

from .routers import candidates, startups, roles, match, outreach, health


app = FastAPI(title="AI Tech Exec Recruiter", version="0.1.0")


# Include routers
app.include_router(health.router)
app.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
app.include_router(startups.router, prefix="/startups", tags=["startups"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(match.router, tags=["matching"])
app.include_router(outreach.router, tags=["outreach"])
