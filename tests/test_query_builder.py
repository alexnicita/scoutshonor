import json
from pathlib import Path

from src.features.sourcing.query_builder import SearchProfile, build_queries


def test_query_builder_matches_snapshot():
    profile = SearchProfile(
        title="Backend Engineer",
        must_have_skills=["python", "aws"],
        nice_to_have_skills=["kubernetes"],
        locations=["Remote", "Austin"],
        industries=["fintech"],
        exclude_terms=["intern"],
    )

    expected = json.loads(
        Path("tests/fixtures/query_builder_snapshot.json").read_text(encoding="utf-8")
    )

    assert build_queries(profile) == expected
