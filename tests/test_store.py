import pytest

from src.data.store import DataStore


@pytest.fixture()
def store() -> DataStore:
    ds = DataStore(db_path=":memory:")
    yield ds
    ds.close()


def test_candidate_crud_round_trip(store: DataStore) -> None:
    candidate = store.create_candidate(
        {
            "full_name": "Test User",
            "email": "test@example.com",
            "skills": ["python"],
            "domains": ["infrastructure"],
            "locations": ["San Francisco"],
            "remote_preference": True,
        }
    )
    fetched = store.get_candidate(candidate["id"])
    assert fetched["email"] == "test@example.com"
    assert fetched["skills"] == ["python"]

    updated = store.update_candidate(candidate["id"], {"skills": ["python", "sql"]})
    assert "sql" in updated["skills"]

    store.delete_candidate(candidate["id"])
    assert store.get_candidate(candidate["id"]) is None


def test_role_and_scorecard_flows(store: DataStore) -> None:
    startup = store.create_startup({"name": "Acme", "stage": "seed"})
    role = store.create_role(
        {
            "startup_id": startup["id"],
            "title": "Backend Engineer",
            "required_skills": ["python"],
            "min_years_experience": 5,
            "seniority": "director",
        }
    )
    scorecard = store.create_scorecard(
        {
            "role_id": role["id"],
            "summary": "Backend leadership",
            "must_haves": ["python", "distributed systems"],
            "evaluation_points": ["system design", "mentorship"],
        }
    )

    assert role["startup_id"] == startup["id"]
    assert scorecard["role_id"] == role["id"]
    assert len(store.list_roles(startup_id=startup["id"])) == 1
    assert store.list_scorecards(role_id=role["id"])[0]["must_haves"][0] == "python"


def test_sequences_stage_events_and_sources(store: DataStore) -> None:
    startup = store.create_startup({"name": "Beta", "stage": "series-a"})
    role = store.create_role({"startup_id": startup["id"], "title": "Designer"})
    candidate = store.create_candidate({"full_name": "Jamie Smith", "email": "jamie@example.com"})

    sequence = store.create_sequence(
        {
            "role_id": role["id"],
            "name": "Outreach v1",
            "steps": [{"offset_days": 0, "channel": "email"}],
        }
    )
    event = store.record_stage_event(
        {
            "candidate_id": candidate["id"],
            "role_id": role["id"],
            "stage": "screen",
            "status": "scheduled",
        }
    )
    source = store.add_profile_source(
        {
            "candidate_id": candidate["id"],
            "source": "linkedin",
            "url": "https://www.linkedin.com/in/example",
        }
    )

    assert sequence["steps"][0]["channel"] == "email"
    assert store.list_stage_events(candidate["id"])[0]["stage"] == event["stage"]
    assert store.get_profile_source(source["id"])["source"] == "linkedin"


def test_suppression_blocks_interactions(store: DataStore) -> None:
    candidate = store.create_candidate({"full_name": "Opt Out", "email": "optout@example.com"})
    store.suppress_contact(candidate["email"], reason="user_opt_out", source="test")

    with pytest.raises(PermissionError):
        store.log_interaction(
            {
                "candidate_id": candidate["id"],
                "channel": "email",
                "direction": "outbound",
                "subject": "Hello",
                "body": "Should not send",
            }
        )

    audit_events = store.list_audit_events(event_type="interaction_blocked")
    assert audit_events[0]["detail"]["contact"] == candidate["email"]
