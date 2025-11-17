from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_end_to_end_full_flow():
    # 1) Create startup
    startup = client.post(
        "/startups/",
        json={
            "name": "E2ECo",
            "stage": "series-a",
            "domains": ["ai", "productivity"],
            "location": "SF",
            "stack": ["python", "aws", "fastapi"],
        },
    )
    assert startup.status_code == 200
    startup = startup.json()

    # 2) Create role
    role = client.post(
        "/roles/",
        json={
            "startup_id": startup["id"],
            "title": "VP Engineering",
            "required_skills": ["python", "aws", "fastapi"],
            "nice_to_have_skills": ["kubernetes"],
            "min_years_experience": 8,
            "responsibilities": [
                "team leadership",
                "hiring",
                "platform",
            ],
            "seniority": "vp",
            "remote_ok": True,
        },
    )
    assert role.status_code == 200
    role = role.json()

    # 3) Create two candidates (one strong match, one weak)
    c1 = client.post(
        "/candidates/",
        json={
            "full_name": "Alice E2E",
            "current_title": "Director of Engineering",
            "titles": ["Engineering Manager"],
            "years_experience": 11,
            "skills": ["python", "aws", "fastapi", "kubernetes"],
            "domains": ["ai"],
            "locations": ["San Francisco"],
            "remote_preference": True,
        },
    )
    assert c1.status_code == 200
    c1 = c1.json()

    c2 = client.post(
        "/candidates/",
        json={
            "full_name": "Bob E2E",
            "current_title": "Senior Engineer",
            "titles": ["Engineer"],
            "years_experience": 5,
            "skills": ["python"],
            "domains": ["healthtech"],
            "locations": ["New York"],
            "remote_preference": True,
        },
    )
    assert c2.status_code == 200
    c2 = c2.json()

    # 4) Candidate search endpoint (skills + location)
    search = client.get(
        "/candidates/search",
        params={"skills": "python,aws,fastapi", "location": "San Francisco"},
    )
    assert search.status_code == 200
    ids = {c["id"] for c in search.json()}
    assert c1["id"] in ids

    # 5) Sourcing boolean generation via role_id
    sourcing = client.post(
        "/sourcing/boolean",
        json={
            "role_id": role["id"],
            "locations": ["San Francisco"],
            "extras": ["startups", "leadership"],
        },
    )
    assert sourcing.status_code == 200
    sr = sourcing.json()
    assert set(sr.keys()) == {"linkedin", "google_xray", "github"}
    assert "python" in sr["linkedin"].lower()
    assert "linkedin.com/in" in sr["google_xray"].lower()

    # 6) Matching scoped to our two candidates for determinism
    match = client.post(
        "/match",
        json={
            "role_id": role["id"],
            "candidate_ids": [c1["id"], c2["id"]],
            "limit": 1,
        },
    )
    assert match.status_code == 200
    mr = match.json()
    assert mr["role"]["id"] == role["id"]
    assert len(mr["results"]) == 1
    assert mr["results"][0]["candidate"]["id"] == c1["id"]

    # 7) Outreach for the top match
    outreach = client.post(
        "/outreach",
        json={
            "candidate_id": c1["id"],
            "role_id": role["id"],
            "tone": "professional",
            "channels": ["email", "linkedin"],
            "add_cal_link": "https://cal.example.com/e2e",
        },
    )
    assert outreach.status_code == 200
    msgs = outreach.json()["messages"]
    channels = {m["channel"] for m in msgs}
    assert {"email", "linkedin"}.issubset(channels)

    # 8) Long job description generation
    desc = client.post(
        "/descriptions/generate",
        json={
            "title": role["title"],
            "seniority": role["seniority"],
            "startup_name": "E2ECo",
            "stage": "series-a",
            "required_skills": role["required_skills"],
            "nice_to_have_skills": role["nice_to_have_skills"],
            "responsibilities": role["responsibilities"],
            "min_years_experience": role["min_years_experience"],
            "location": "San Francisco",
            "remote_ok": True,
            "employment_type": "full-time",
            "benefits": ["Health", "401k"],
        },
    )
    assert desc.status_code == 200
    body = desc.json()
    assert body["title"] == role["title"]
    assert isinstance(body["description"], str) and len(body["description"]) > 40
