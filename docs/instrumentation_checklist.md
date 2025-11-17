# Instrumentation Checklist

- [ ] Health endpoints respond with status `ok` in under 200ms.
- [ ] Outreach sequence emits `reply_recorded` and `reply_routed` metrics on replies.
- [ ] Sequence engine suppresses follow-ups after replies; log suppression decisions.
- [ ] Resume parser errors surface with actionable messages; malformed files handled.
- [ ] Screening summary logs missing/flagged skills without PII.
- [ ] ATS sync dry-run payload recorded locally with candidate_id and note preview.
- [ ] Tests run locally via `make test` with deterministic fixtures.
- [ ] Alert path defined for failures (email or Slack); owners documented.
- [ ] GitHub issues labeled by area (`outreach`, `screening`, `docs`).
