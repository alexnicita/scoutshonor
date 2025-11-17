import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from src.integrations.gmail_auth import GmailAuth, GmailToken, TokenStore
from src.integrations.gmail_poll import GmailPoller
from src.services.suppression import suppression_store


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "gmail"


def load_fixture(name: str):
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def make_auth(tmp_path) -> GmailAuth:
    store = TokenStore(tmp_path / "gmail_token.json")
    token = GmailToken(
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    store.save(token)
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=token.to_dict())
        )
    )
    return GmailAuth(
        client_id="client-id",
        client_secret="client-secret",
        redirect_uri="http://localhost:8000/oauth",
        token_store=store,
        http_client=client,
    )


def test_gmail_poller_detects_events_and_updates_suppression(tmp_path):
    suppression_store.reset()
    auth = make_auth(tmp_path)
    fixtures = {
        "bounce-1": load_fixture("bounce.json"),
        "reply-1": load_fixture("reply.json"),
        "ooo-1": load_fixture("out_of_office.json"),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/messages"):
            return httpx.Response(
                200,
                json={
                    "messages": [
                        {"id": "bounce-1", "threadId": "thread-1"},
                        {"id": "reply-1", "threadId": "thread-3"},
                        {"id": "ooo-1", "threadId": "thread-2"},
                    ]
                },
            )
        message_id = request.url.path.split("/")[-1]
        payload = fixtures.get(message_id)
        if payload:
            return httpx.Response(200, json=payload)
        return httpx.Response(404)

    poller = GmailPoller(
        auth=auth, http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    events = poller.poll()

    event_types = {evt.event for evt in events}
    assert {"bounce", "reply", "out_of_office"}.issubset(event_types)
    assert suppression_store.is_suppressed("sender@example.com")
