from pathlib import Path
import json

import httpx

from src.integrations.greenhouse_client import GreenhouseClient


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "greenhouse"


def load_fixture(name: str):
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def greenhouse_transport() -> httpx.MockTransport:
    jobs_page1 = load_fixture("jobs_page1.json")
    jobs_page2 = load_fixture("jobs_page2.json")
    candidates = load_fixture("candidates.json")
    applications = load_fixture("applications.json")

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        query_params = request.url.params
        if path.endswith("/jobs") and query_params.get("page") == "2":
            return httpx.Response(200, json=jobs_page2)
        if path.endswith("/jobs"):
            headers = {"Link": '<https://harvest.greenhouse.io/v1/jobs?page=2>; rel="next"'}
            return httpx.Response(200, json=jobs_page1, headers=headers)
        if path.endswith("/candidates"):
            return httpx.Response(200, json=candidates)
        if path.endswith("/applications"):
            return httpx.Response(200, json=applications)
        return httpx.Response(404, json={"error": "not found"})

    return httpx.MockTransport(handler)


def test_greenhouse_client_paginates_and_normalizes():
    client = GreenhouseClient(api_key="secret", transport=greenhouse_transport(), page_size=2)
    jobs = client.list_jobs()
    assert len(jobs) == 3
    assert jobs[0]["departments"] == ["Engineering"]
    assert jobs[-1]["offices"] == ["San Francisco"]

    candidates = client.list_candidates()
    assert candidates[0]["emails"] == ["ada@example.com"]
    assert candidates[1]["first_name"] == "Grace"

    applications = client.list_applications()
    assert applications[0]["candidate_id"] == 11
    assert applications[0]["job_ids"] == [1]
    assert applications[1]["job_ids"] == [3]
