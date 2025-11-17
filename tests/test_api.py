from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_end_to_end_match_and_outreach():
    # Create startup
    st = client.post(
        "/startups/",
        json={
            "name": "AcmeAI",
            "stage": "series-a",
            "domains": ["fintech", "ai"],
            "location": "SF",
            "stack": ["python", "aws"],
        },
    ).json()

    # Create role
    role = client.post(
        "/roles/",
        json={
            "startup_id": st["id"],
            "title": "VP Engineering",
            "required_skills": ["python", "aws", "fastapi"],
            "nice_to_have_skills": ["kubernetes"],
            "min_years_experience": 8,
            "responsibilities": ["team leadership", "hiring", "platform"],
            "seniority": "vp",
            "remote_ok": True,
        },
    ).json()

    # Create candidates
    c1 = client.post(
        "/candidates/",
        json={
            "full_name": "Alice Smith",
            "current_title": "Director of Engineering",
            "titles": ["Engineering Manager"],
            "years_experience": 10,
            "skills": ["python", "aws", "fastapi", "kubernetes"],
            "domains": ["fintech"],
            "locations": ["San Francisco"],
            "remote_preference": True,
        },
    ).json()

    client.post(
        "/candidates/",
        json={
            "full_name": "Bob Lee",
            "current_title": "Senior Engineer",
            "titles": ["Engineer"],
            "years_experience": 6,
            "skills": ["python"],
            "domains": ["healthtech"],
            "locations": ["New York"],
            "remote_preference": True,
        },
    )

    # Match
    mr = client.post("/match", json={"role_id": role["id"], "limit": 1}).json()
    assert mr["role"]["id"] == role["id"]
    assert len(mr["results"]) == 1
    assert mr["results"][0]["candidate"]["id"] == c1["id"]

    # Outreach
    out = client.post(
        "/outreach",
        json={
            "candidate_id": c1["id"],
            "role_id": role["id"],
            "tone": "professional",
            "channels": ["email", "linkedin"],
        },
    )
    assert out.status_code == 200
    msgs = out.json()["messages"]
    assert any(m["channel"] == "email" for m in msgs)
