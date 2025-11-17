from src.features.intake.schema import ScorecardCompetency
from src.features.sourcing.importer import ImportedCandidate
from src.features.sourcing.rank import rank_candidates


def test_rank_candidates_orders_and_collects_evidence():
    scorecard = [
        ScorecardCompetency(
            name="Leadership",
            weight=0.6,
            signals=["managed team", "roadmap ownership"],
        ),
        ScorecardCompetency(
            name="Reliability",
            weight=0.4,
            signals=["incident response", "on-call"],
        ),
    ]

    strong = ImportedCandidate(
        full_name="Alex Rivera",
        current_title="Engineering Manager",
        company="Atlas Robotics",
        skills=["python", "aws", "incident response"],
        raw={"summary": "Managed team, roadmap ownership, led incident response"},
    )
    mid = ImportedCandidate(
        full_name="Blake Chen",
        current_title="Senior Engineer",
        company="Atlas Robotics",
        skills=["python"],
        raw={"notes": "Owned roadmap ownership for a subsystem"},
    )
    weak = ImportedCandidate(
        full_name="Casey Doe",
        current_title="Engineer",
        company="Other Co",
        skills=["javascript"],
        raw={"summary": "Built UI dashboards"},
    )

    ranked = rank_candidates([mid, strong, weak], scorecard)

    assert ranked[0].candidate.full_name == "Alex Rivera"
    assert ranked[1].candidate.full_name == "Blake Chen"
    assert ranked[0].score > ranked[1].score > ranked[2].score
    assert ranked[0].evidence["Reliability"] == ["incident response"]
