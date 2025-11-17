from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_generate_description_stub_returns_long_text():
    payload = {
        "title": "Senior Platform Engineer",
        "seniority": "vp",
        "startup_name": "AcmeAI",
        "mission": "Make AI safety practical for real products.",
        "required_skills": ["python", "aws", "kubernetes"],
        "nice_to_have_skills": ["terraform", "observability"],
        "responsibilities": [
            "Own platform reliability",
            "Scale CI/CD",
            "Partner with security",
        ],
        "min_years_experience": 8,
        "remote_ok": True,
        "compensation_range": "$180k-$230k + equity",
        "benefits": ["Health, dental, vision", "401(k) with match"],
    }
    r = client.post("/descriptions/generate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert payload["title"] in data["title"]
    text = data["description"]
    # Fallback template should include sections and multiple lines
    assert "Overview" in text
    assert "What you'll do" in text
    assert "What you'll bring" in text
    assert len(text.splitlines()) > 10
