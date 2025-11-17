from src.utils.redact import redact_payload


def test_redacts_sensitive_keys_and_patterns():
    payload = {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "notes": "Reached via ada@example.com and +1 (415) 555-0000",
        "metadata": {"thread": "external", "subject": "Hello Ada"},
        "history": [{"email": "nested@example.com"}, "call me at 202-555-1212"],
    }

    redacted = redact_payload(payload)

    assert redacted["full_name"] == "[REDACTED]"
    assert redacted["email"] == "[REDACTED]"
    assert "[REDACTED_EMAIL]" in redacted["notes"]
    assert "[REDACTED_PHONE]" in redacted["notes"]
    assert redacted["history"][0]["email"] == "[REDACTED]"
    assert "555" not in redacted["history"][1]
    assert redacted["metadata"]["subject"] == "[REDACTED]"


def test_non_pii_fields_are_preserved():
    payload = {"skills": ["python", "rust"], "score": 0.92, "active": True}
    redacted = redact_payload(payload)
    assert redacted == payload
