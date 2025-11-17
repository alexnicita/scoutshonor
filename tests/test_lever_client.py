import httpx

from src.integrations.lever_client import LeverClient


def test_lever_client_normalizes_payloads():
    postings_payload = {
        "data": [
            {
                "id": "p1",
                "text": "Backend Engineer",
                "categories": {"department": "Engineering", "location": "Remote"},
                "state": "published",
            }
        ]
    }
    candidates_payload = {
        "data": [
            {
                "id": "c1",
                "name": "Taylor",
                "headline": "IC",
                "emails": ["taylor@example.com"],
                "stage": "screen",
            }
        ]
    }
    applications_payload = {
        "data": [
            {"id": "a1", "opportunityId": "opp-1", "posting": "p1", "stage": "new"}
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/postings"):
            return httpx.Response(200, json=postings_payload)
        if request.url.path.endswith("/candidates"):
            return httpx.Response(200, json=candidates_payload)
        if request.url.path.endswith("/applications"):
            return httpx.Response(200, json=applications_payload)
        return httpx.Response(404)

    client = LeverClient(api_key="secret", transport=httpx.MockTransport(handler))
    postings = client.list_postings()
    assert postings[0]["title"] == "Backend Engineer"
    assert postings[0]["department"] == "Engineering"

    candidates = client.list_candidates()
    assert candidates[0]["email"] == "taylor@example.com"
    assert candidates[0]["stage"] == "screen"

    apps = client.list_applications()
    assert apps[0]["posting_id"] == "p1"
    assert apps[0]["status"] == "new"
