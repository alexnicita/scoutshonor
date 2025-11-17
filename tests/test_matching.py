from src.models.candidate import Candidate
from src.models.role import Role
from src.models.common import Seniority
from src.services.matching import rank_candidates


def test_rank_candidates_orders_by_score():
    role = Role(
        id="r1",
        startup_id="s1",
        title="VP Engineering",
        required_skills=["python", "aws", "fastapi"],
        nice_to_have_skills=["kubernetes"],
        min_years_experience=8,
        responsibilities=["lead eng", "hiring", "platform"],
        seniority=Seniority.vp,
        remote_ok=True,
    )

    c1 = Candidate(
        id="c1",
        full_name="Alice Smith",
        current_title="Director of Engineering",
        titles=["Engineering Manager"],
        years_experience=10,
        skills=["python", "aws", "fastapi", "kubernetes"],
        domains=["fintech"],
        locations=["San Francisco"],
        remote_preference=True,
        stage_preferences=[],
    )

    c2 = Candidate(
        id="c2",
        full_name="Bob Lee",
        current_title="Senior Engineer",
        titles=["Engineer"],
        years_experience=6,
        skills=["python"],
        domains=["healthtech"],
        locations=["New York"],
        remote_preference=True,
        stage_preferences=[],
    )

    ranked = rank_candidates(
        [c1, c2], role, startup_domains=["fintech"], startup_stage="series-a"
    )
    assert ranked[0].candidate.id == "c1"
    assert ranked[0].score >= ranked[1].score
