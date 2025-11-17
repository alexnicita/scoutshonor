# Compliance & privacy

Guardrails for handling candidate and contact data across sourcing, outreach, and ATS sync.

## PII catalog & redaction
- High-risk fields: `full_name`, `email`, `phone`, `locations`, `linkedin_url`, message `subject`/`body`, free-text `notes`.
- `src/utils/redact.py` walks nested dicts/lists/strings, replacing PII keys and email/phone patterns with `[REDACTED]` placeholders. Use before logging, tracing, or emitting metrics.
- Avoid storing raw headers or message bodies beyond 90 days; prefer summary text or hashes when writing to `audit_logs`.

## Consent + opt-out
- Suppressions live in `suppression_list` (email/phone normalized to lowercase). Attempts to send to a suppressed contact must fail safely and log an `interaction_blocked` audit record; see `src/services/suppression.py`.
- Gmail polling marks bounces as suppressed automatically; manual suppressions and removals are supported.
- Consent events are captured in `consent_events` (status: granted/withdrawn) with optional linkage to `candidate_id` for traceability.
- Include a `/privacy` notice snippet and unsubscribe headers in outbound templates (TODO: wire into outreach generator once email transport is built). `GmailSender` emits `List-Unsubscribe` headers when provided.

## Retention practices
- Candidates: delete or anonymize after withdrawal or 24 months of inactivity; trim interaction bodies after 90 days.
- Roles/scorecards: archive 12–24 months after a role is filled.
- Audit and consent: retain indefinitely but keep entries redacted and minimal.

## Outreach safeguards (email/Slack)
- Honor opt-outs: suppressed addresses are never sent to; suppression events are timestamped for audit.
- Bounces: Gmail polling will mark bounced recipients as suppressed.
- Data handling: keep `.env` and token files (`.cache/`) out of version control; rotate API keys regularly.
- Slack commands return minimal, non-PII responses; avoid logging secrets into chat.
