import json

import httpx

from src.integrations.greenhouse_writer import GreenhouseWriter


def test_greenhouse_writer_dry_run_includes_payload():
    writer = GreenhouseWriter(api_key="secret", dry_run=True)
    result = writer.post_application_note(application_id=99, body="Syncing note", visibility="public")
    assert result["dry_run"] is True
    assert result["path"].endswith("/applications/99/activity_feed/notes")
    assert result["payload"]["body"] == "Syncing note"
    assert result["payload"]["visibility"] == "public"


def test_greenhouse_writer_posts_note_via_api():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path.endswith("/applications/42/activity_feed/notes")
        body = json.loads(request.content.decode())
        assert body["body"] == "New feedback"
        assert body["visibility"] == "private"
        return httpx.Response(201, json={"id": 555, "body": body["body"]})

    writer = GreenhouseWriter(api_key="secret", transport=httpx.MockTransport(handler))
    response = writer.post_application_note(application_id=42, body="New feedback")
    assert response["id"] == 555
    assert response["body"] == "New feedback"
