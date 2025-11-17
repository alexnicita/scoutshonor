# Compliance & Respectful Sending

- Honor opt-outs: addresses in the suppression list are never sent to. Suppression events are timestamped for audit (`src/services/suppression.py`).
- Bounces: Gmail polling will mark bounced recipients as suppressed.
- Unsubscribe: pass an `unsubscribe_link` to `GmailSender` to emit `List-Unsubscribe` and `List-Unsubscribe-Post` headers.
- Data handling: keep `.env` and token files (`.cache/`) out of version control; rotate API keys regularly.
- Slack commands return minimal, non-PII responses; avoid logging secrets into chat.
