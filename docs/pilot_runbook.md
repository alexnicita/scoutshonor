# Pilot Runbook

Goal: validate the outreach + screening flow with a small set of recruiters and hiring managers, gather feedback, and double-check instrumentation.

## Scope
- Personas: recruiters using outreach sequences; hiring managers reviewing screening summaries.
- Environments: local FastAPI service or internal staging; no production data.
- Success signals: replies routed correctly, ATS notes generated, zero PII leaks.

## Owner + Cadence
- Pilot lead: assign one DRI for comms/changes.
- Stand-ups: 10 minutes daily until exit criteria met.
- Feedback triage: twice weekly, labeled in GitHub.

## Run Steps
1. Prep demo data (candidates, roles, startups) using `scripts/demo-e2e.sh`.
2. Validate instrumentation: run `make test` and confirm metrics hooks fire in logs.
3. Walk pilot users through two flows:
   - Outreach: tone selection → 2-step sequence → reply routing.
   - Screening: resume parse → summary/risk → ATS note (dry-run).
4. Collect feedback using the template in `docs/feedback_template.md`.
5. File issues using the templates under `.github/ISSUE_TEMPLATE/`.

## Exit Criteria
- Outreach replies hit the correct owner; suppressed follow-ups after any reply.
- Screening notes produce clear risks and can be posted to ATS (dry-run).
- Known issues documented with owners; no data handling concerns outstanding.
