import base64
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from src.integrations.gmail_auth import GmailAuth, GmailToken, TokenStore
from src.integrations.gmail_send import GmailSender, SuppressedRecipientError
from src.services.suppression import suppression_store


def make_auth(tmp_path) -> GmailAuth:
    store = TokenStore(tmp_path / "gmail_token.json")
    token = GmailToken(
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    store.save(token)
    # Mock client to avoid outbound calls on refresh.
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=token.to_dict())))
    return GmailAuth(
        client_id="client-id",
        client_secret="client-secret",
        redirect_uri="http://localhost:8000/oauth",
        token_store=store,
        http_client=client,
    )


def test_send_email_renders_dry_run(tmp_path):
    suppression_store.reset()
    auth = make_auth(tmp_path)
    sender = GmailSender(auth=auth, from_address="sender@example.com", dry_run=True)
    result = sender.send_email(
        to="candidate@example.com",
        subject="Hello",
        body_text="Plain",
        body_html="<p>Plain</p>",
        unsubscribe_link="https://example.com/unsub",
    )
    assert result["dry_run"] is True
    raw = result["payload"]["raw"]
    decoded = base64.urlsafe_b64decode(raw.encode()).decode()
    assert "List-Unsubscribe" in decoded
    assert "candidate@example.com" in decoded


def test_send_email_checks_suppression(tmp_path):
    suppression_store.reset()
    suppression_store.suppress("blocked@example.com", reason="manual")
    auth = make_auth(tmp_path)
    sender = GmailSender(auth=auth, from_address="sender@example.com")
    with pytest.raises(SuppressedRecipientError):
        sender.send_email(to="blocked@example.com", subject="Nope", body_text="hi")


def test_send_email_hits_gmail_api(tmp_path):
    suppression_store.reset()
    auth = make_auth(tmp_path)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/users/me/messages/send")
        assert request.headers["Authorization"].startswith("Bearer")
        return httpx.Response(200, json={"id": "abc123", "labelIds": ["SENT"]})

    sender = GmailSender(
        auth=auth,
        from_address="sender@example.com",
        dry_run=False,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    resp = sender.send_email(to="candidate@example.com", subject="Hi", body_text="hello")
    assert resp["id"] == "abc123"
