# TODO Roadmap — Startup Recruiting Copilot

This file defines a parallelizable roadmap to build an AI recruiting copilot for startup teams. It is organized into workstreams with task IDs, dependencies, acceptance criteria, and test notes. Multiple agents can safely claim tasks concurrently.

Use this as the single source of truth. Keep sections short, atomic, and linked by IDs.

---

## How To Use

- Status keywords: `todo`, `in-progress`, `review`, `blocked`, `done`.
- Priority: `P0` (blocker/critical), `P1` (MVP), `P2` (fast follow), `P3` (nice-to-have).
- Assignment: add `Owner:` GitHub handle or team alias.
- Dependencies: list IDs (tasks or workstreams) that must complete first.
- Deliverables: code paths, scripts, endpoints, docs, and demo assets.
- Tests: at least unit tests where applicable; smoke tests otherwise. Aim for fast, deterministic tests.
- Repo structure to target (create as you go):
  - `src/` (module code), `tests/`, `scripts/`, `docs/`, `examples/`, `assets/`.
  - Scripts and Make targets should be idempotent and non-destructive.

---

## MVP Objectives (Definition of Done)

- Intake → JD/Scorecard generator produces a hiring manager brief and candidate-facing JD, with interview kit templates.
- Sourcing helper generates boolean/X-ray queries and ranks a CSV list of candidates against a scorecard.
- Outreach copilot drafts personalized emails/InMails and supports a 2-step sequence with reply detection.
- Screen summaries produce structured notes and push to ATS as comments/notes (start with Greenhouse read-only, write for notes if feasible).
- Slack digests: daily pipeline summary + feedback nudges; slash commands for drafting outreach and adding notes.
- Metrics: instrument time-to-shortlist, outreach reply rate, feedback SLA; log events for audit.

---

## Parallelization Guide

- Claim tasks by adding `Owner:` and moving `Status` to `in-progress`.
- Keep PRs focused to a single task or a small cluster within one workstream.
- Adhere to naming: scripts in `scripts/` use kebab-case; code in `src/` and `tests/` use snake_case.
- Prefer Make targets (see `WS-FOUND-01`) so any environment can run the same commands.

---

## Workstream Index

- WS-FOUND: Foundation & Repo Scaffolding
- WS-DATA: Data Model & Storage
- WS-AI: AI Services (prompting, embeddings, ranking, summarization)
- WS-INT-ATS: ATS Integrations (Greenhouse → Lever)
- WS-INT-EMAIL: Email Integration (Gmail/Workspace)
- WS-INT-SLACK: Slack Bot & Digests
- WS-FEATURE-INTAKE: Intake → JD/Scorecard
- WS-FEATURE-SOURCING: Sourcing Helper
- WS-FEATURE-OUTREACH: Outreach Copilot
- WS-FEATURE-SCREEN: Screen Summaries → ATS Sync
- WS-EXT-CHROME: Chrome Extension Overlay
- WS-SCHED: Lightweight Scheduling (optional fast follow)
- WS-TRUST: Security, Compliance, and Guardrails
- WS-OBS: Logging, Metrics, Analytics
- WS-PILOT: Pilot Ops and Feedback Loop
- WS-DOCS: Documentation & GTM Collateral

---

## WS-FOUND: Foundation & Repo Scaffolding

- ID: WS-FOUND | Priority: P0 | Status: todo
- Goal: Establish repo structure, Make targets, local env, and CI hooks.

1) T-FOUND-01: Makefile baseline
   - Status: todo | Priority: P0 | Owner: —
   - Deliverables: `Makefile` with `setup`, `run`, `test`, `lint`, `fmt`, `clean`.
   - Acceptance: `make setup` completes without error; `make test` runs a placeholder test suite.
   - Notes: Provide `scripts/` fallbacks if `make` is unavailable.

2) T-FOUND-02: Scripts scaffolding
   - Status: todo | Priority: P0 | Owner: —
   - Deliverables: `scripts/test.sh`, `scripts/lint.sh`, `scripts/fmt.sh`, `scripts/run.sh`.
   - Acceptance: All scripts are executable, shellcheck-clean (basic), and respect env vars.

3) T-FOUND-03: Base README and docs index
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: `README.md` (quickstart, prerequisites, Make targets), `docs/INDEX.md`.
   - Acceptance: A new developer can run `make setup` and `make run` per README.

4) T-FOUND-04: Env management
   - Status: todo | Priority: P0 | Owner: —
   - Deliverables: `.env.example`, `.gitignore` entries, secret handling guidance in README.
   - Acceptance: No secrets in repo; app reads config from env.

5) T-FOUND-05: CI skeleton (optional if local only)
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: CI workflow running lint/tests on PRs.
   - Acceptance: PR triggers lints/tests; artifacts or coverage summary visible.

---

## WS-DATA: Data Model & Storage

- ID: WS-DATA | Priority: P0 | Status: todo
- Goal: Define core objects and minimal persistence with migrations.

Core objects: `role`, `scorecard`, `candidate`, `profile_source`, `interaction` (email/call/note), `sequence`, `stage_event`.

1) T-DATA-01: Schema draft
   - Status: todo | Priority: P0 | Owner: — | Depends: WS-FOUND
   - Deliverables: `docs/schema.md` with ERD and field definitions (ids, keys, PII marking).
   - Acceptance: All MVP features map to fields; PII clearly marked; retention noted.

2) T-DATA-02: Storage adapter
   - Status: todo | Priority: P1 | Owner: — | Depends: T-DATA-01
   - Deliverables: `src/data/store.py` (or equivalent) with CRUD for core objects; in-memory or SQLite initially.
   - Acceptance: Unit tests in `tests/test_store.py` covering CRUD and basic constraints.

3) T-DATA-03: Migrations
   - Status: todo | Priority: P1 | Owner: — | Depends: T-DATA-02
   - Deliverables: Simple migration runner, `scripts/migrate.sh`, and `make migrate` target.
   - Acceptance: Fresh clone runs `make setup && make migrate` without errors.

---

## WS-AI: AI Services

- ID: WS-AI | Priority: P0 | Status: todo
- Goal: Provide prompting, embeddings, ranking, and summarization interfaces with pluggable providers.

1) T-AI-01: Prompt registry
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: `src/ai/prompts/` with versioned prompt files for intake, sourcing, outreach, screening; `docs/prompts.md`.
   - Acceptance: Each prompt has purpose, inputs, and output schema; unit tests validate schema conformance (mock LLM).

2) T-AI-02: Embeddings + similarity
   - Status: todo | Priority: P1 | Owner: — | Depends: T-DATA-02
   - Deliverables: `src/ai/embeddings.py` with provider interface, cosine similarity utilities; `tests/test_embeddings.py`.
   - Acceptance: Deterministic tests via fixed vectors; supports pluggable providers.

3) T-AI-03: Ranker against scorecard
   - Status: todo | Priority: P1 | Owner: — | Depends: T-AI-02, T-DATA-02
   - Deliverables: `src/ai/ranker.py` that returns score, evidence snippets, and explainability metadata.
   - Acceptance: Given sample candidates and scorecard, rank order matches expected; explanations reference source fields.

4) T-AI-04: Summarizer for screening
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: `src/ai/summarizer.py` to produce resume summary, risks, gaps, and suggested questions.
   - Acceptance: Unit tests verify schema; mock provider used to keep tests offline.

---

## WS-INT-ATS: ATS Integrations (Greenhouse → Lever)

- ID: WS-INT-ATS | Priority: P1 | Status: todo
- Goal: Read roles/candidates/interviews; write notes/comments where available.

1) T-ATS-01: Greenhouse read-only client
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-DATA
   - Deliverables: `src/integrations/greenhouse_client.py` with auth, pagination, and endpoints to fetch jobs, candidates, applications.
   - Acceptance: Mocked tests hit fixtures; `scripts/gh_fetch_sample.sh` outputs normalized JSON.

2) T-ATS-02: Greenhouse write notes
   - Status: todo | Priority: P1 | Owner: — | Depends: T-ATS-01
   - Deliverables: `src/integrations/greenhouse_writer.py` to post notes/comments.
   - Acceptance: Dry-run mode; unit tests with recorded fixtures.

3) T-ATS-03: Lever read-only client (fast follow)
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: `src/integrations/lever_client.py` and fixtures.
   - Acceptance: Same as Greenhouse client parity for reads.

---

## WS-INT-EMAIL: Gmail/Workspace

- ID: WS-INT-EMAIL | Priority: P1 | Status: todo
- Goal: Send emails, detect replies/bounces, and track opt-outs respectfully.

1) T-EMAIL-01: OAuth2 + token storage
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-DATA
   - Deliverables: `src/integrations/gmail_auth.py`, token persistence; `docs/gmail_setup.md` with console steps.
   - Acceptance: Local flow obtains and refreshes tokens; secrets never committed.

2) T-EMAIL-02: Send email API
   - Status: todo | Priority: P1 | Owner: — | Depends: T-EMAIL-01
   - Deliverables: `src/integrations/gmail_send.py` with plaintext + simple HTML; `tests/test_gmail_send.py` (mocked).
   - Acceptance: Emails constructed with personalization slots; dry-run renders to stdout for tests.

3) T-EMAIL-03: Reply + bounce detection
   - Status: todo | Priority: P1 | Owner: — | Depends: T-EMAIL-01
   - Deliverables: `src/integrations/gmail_poll.py` with label-based polling; reply/bounce parsers.
   - Acceptance: Fixture-based tests detect reply, out-of-office, bounce; updates an `interaction` record.

4) T-EMAIL-04: Opt-out/suppression
   - Status: todo | Priority: P1 | Owner: — | Depends: T-EMAIL-02
   - Deliverables: Suppression list management in data layer; headers to respect unsubscribe; `docs/compliance.md` section.
   - Acceptance: System prevents sending to suppressed addresses; audit log entry created.

---

## WS-INT-SLACK: Slack Bot & Digests

- ID: WS-INT-SLACK | Priority: P1 | Status: todo
- Goal: Daily pipeline digest, feedback nudges, and quick slash commands.

1) T-SLACK-01: App bootstrap
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: `src/integrations/slack_app.py`, app manifest in `docs/slack_app.yaml`.
   - Acceptance: Local bot posts a message to a test channel using a bot token env var.

2) T-SLACK-02: Daily digest job
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-DATA
   - Deliverables: `src/jobs/digest.py`, `make cron` or `scripts/run_digest.sh`.
   - Acceptance: Digest includes roles in-flight, candidates stalled >5 days, missing scorecards.

3) T-SLACK-03: Slash commands
   - Status: todo | Priority: P1 | Owner: — | Depends: T-SLACK-01
   - Deliverables: `/recruit draft-outreach`, `/recruit add-note`, `/recruit who-is-stuck` endpoints.
   - Acceptance: Commands respond within 3s with actionable content.

---

## WS-FEATURE-INTAKE: Intake → JD/Scorecard

- ID: WS-FEATURE-INTAKE | Priority: P0 | Status: todo
- Goal: Convert business goals into JD, scorecard, interview kit, knockout questions.

1) T-INTAKE-01: Intake schema + form
   - Status: todo | Priority: P0 | Owner: — | Depends: WS-DATA
   - Deliverables: `src/features/intake/schema.py`, CLI or minimal UI form; `examples/intake_sample.json`.
   - Acceptance: Form validates required fields; sample JSON saved and reloaded.

2) T-INTAKE-02: JD + scorecard generator
   - Status: todo | Priority: P0 | Owner: — | Depends: T-INTAKE-01, T-AI-01
   - Deliverables: `src/features/intake/generate.py` producing two outputs: HM brief and candidate-facing JD; scorecard with competencies/rubrics.
   - Acceptance: Deterministic mocked output; written to `assets/outputs/<role-id>/`.

3) T-INTAKE-03: Interview kit + knockout questions
   - Status: todo | Priority: P1 | Owner: — | Depends: T-INTAKE-02
   - Deliverables: `src/features/intake/interview_kit.py` and templates.
   - Acceptance: Generates role-specific kit with structured questions and scoring guidance.

---

## WS-FEATURE-SOURCING: Sourcing Helper

- ID: WS-FEATURE-SOURCING | Priority: P0 | Status: todo
- Goal: Generate boolean/X-ray queries and rank imported candidate lists.

1) T-SOURCE-01: Query builder
   - Status: todo | Priority: P0 | Owner: — | Depends: T-INTAKE-02
   - Deliverables: `src/features/sourcing/query_builder.py` for LinkedIn/GitHub/Wellfound X-ray search strings.
   - Acceptance: Given a profile template, outputs platform-specific queries; snapshot tests.

2) T-SOURCE-02: CSV import + dedupe + enrich
   - Status: todo | Priority: P0 | Owner: — | Depends: WS-DATA
   - Deliverables: `src/features/sourcing/importer.py` supporting CSV; dedupe by email/name+company; enrichment hooks.
   - Acceptance: Import 100-row sample; duplicates reduced; normalized fields stored.

3) T-SOURCE-03: Ranking against scorecard
   - Status: todo | Priority: P0 | Owner: — | Depends: T-AI-03
   - Deliverables: `src/features/sourcing/rank.py` returns score + evidence snippets; `tests/test_rank.py`.
   - Acceptance: Top-N order matches expected on fixtures; explanations cite resume fields.

---

## WS-FEATURE-OUTREACH: Outreach Copilot

- ID: WS-FEATURE-OUTREACH | Priority: P1 | Status: todo
- Goal: Draft personalized emails/InMails; sequencing with reply tracking.

1) T-OUTREACH-01: Tone profile + personalization slots
   - Status: todo | Priority: P1 | Owner: — | Depends: T-INTAKE-02
   - Deliverables: `src/features/outreach/tone.py` and slots schema (e.g., hooks from candidate evidence).
   - Acceptance: Generated message includes 2+ personalized snippets and role fit rationale.

2) T-OUTREACH-02: Sequence engine (2 steps)
   - Status: todo | Priority: P1 | Owner: — | Depends: T-EMAIL-02, T-EMAIL-03
   - Deliverables: `src/features/outreach/sequence.py` with send windows and wait times.
   - Acceptance: Prevents sending step 2 if reply detected; dry-run mode shows schedule.

3) T-OUTREACH-03: Reply routing + metrics
   - Status: todo | Priority: P1 | Owner: — | Depends: T-EMAIL-03, WS-OBS
   - Deliverables: Update `interaction` and metrics on reply; label candidate as engaged.
   - Acceptance: Dashboard shows reply rate uplift per role and per sequence.

---

## WS-FEATURE-SCREEN: Screen Summaries → ATS Sync

- ID: WS-FEATURE-SCREEN | Priority: P1 | Status: todo
- Goal: Summarize resumes/phone screens; sync notes to ATS.

1) T-SCREEN-01: Resume parser + key facts
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-AI
   - Deliverables: `src/features/screen/parser.py` extracting skills, tenure, education, company stages.
   - Acceptance: Fixture resumes parsed into normalized fields with coverage >=90% on sample.

2) T-SCREEN-02: Summary + risk/gap analysis
   - Status: todo | Priority: P1 | Owner: — | Depends: T-SCREEN-01, T-AI-04
   - Deliverables: `src/features/screen/summary.py` producing structured notes with suggested follow-ups.
   - Acceptance: Output schema validated; human-readable summary + machine fields.

3) T-SCREEN-03: ATS note push
   - Status: todo | Priority: P1 | Owner: — | Depends: T-ATS-02
   - Deliverables: `src/features/screen/ats_sync.py` to post notes/comments to Greenhouse.
   - Acceptance: Dry-run and live mode; success/failure logged with correlation IDs.

---

## WS-EXT-CHROME: Chrome Extension Overlay

- ID: WS-EXT-CHROME | Priority: P2 | Status: todo
- Goal: Surface scorecard fit and one-click actions on LinkedIn/ATS pages.

1) T-CHROME-01: Manifest + injection
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: `extensions/chrome/manifest.json`, content script, basic UI card.
   - Acceptance: Renders overlay on LinkedIn profile; no network calls without consent.

2) T-CHROME-02: Context data extraction
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: DOM selectors for profile fields; sanitize & send to local backend.
   - Acceptance: Extracted fields match 90% of targeted attributes on test pages.

---

## WS-SCHED: Lightweight Scheduling (Optional)

- ID: WS-SCHED | Priority: P2 | Status: todo
- Goal: Propose times, detect conflicts, generate ICS; handoff to Calendars.

1) T-SCHED-01: Availability constraints
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: Inputs for HM work hours, focus blocks, interviewer pools.
   - Acceptance: Time proposals respect constraints and time zones.

2) T-SCHED-02: ICS generator + share link
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: `src/features/scheduling/ics.py` and simple link sharing.
   - Acceptance: ICS opens in common calendars; details accurate.

---

## WS-TRUST: Security, Compliance, Guardrails

- ID: WS-TRUST | Priority: P0 | Status: todo
- Goal: Privacy-first handling of candidate data; explainability and bias checks.

1) T-TRUST-01: PII catalog + redaction
   - Status: todo | Priority: P0 | Owner: — | Depends: WS-DATA
   - Deliverables: Mark PII fields, redact logs; `src/utils/redact.py`; `docs/compliance.md`.
   - Acceptance: No PII in logs/traces; unit tests confirm redaction.

2) T-TRUST-02: Consent + opt-out flows
   - Status: todo | Priority: P0 | Owner: — | Depends: T-EMAIL-04
   - Deliverables: Suppression, audit logs; `/privacy` notice for outbound messages.
   - Acceptance: Attempts to message suppressed contacts fail safely and are logged.

3) T-TRUST-03: JD de-biasing + language checks
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: JD language analyzer; flags gendered/ableist terms; suggestions.
   - Acceptance: Test phrases flagged; suggestions replace with neutral language.

4) T-TRUST-04: Explainability for ranking
   - Status: todo | Priority: P1 | Owner: — | Depends: T-AI-03
   - Deliverables: Evidence snippets with source references; `docs/explainability.md`.
   - Acceptance: Each ranking includes 2–3 evidence snippets and rationale.

---

## WS-OBS: Logging, Metrics, Analytics

- ID: WS-OBS | Priority: P1 | Status: todo
- Goal: Operational visibility and product metrics.

1) T-OBS-01: Structured logging
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-FOUND
   - Deliverables: `src/obs/logging.py` with correlation IDs; redaction middleware.
   - Acceptance: Logs are JSON with request IDs; no PII leaks.

2) T-OBS-02: Product metrics
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: Counters for time-to-shortlist, reply rate, feedback SLA; `docs/metrics.md`.
   - Acceptance: Metrics emitted during e2e demo; smoke test validates increments.

3) T-OBS-03: Daily dashboards (lightweight)
   - Status: todo | Priority: P2 | Owner: —
   - Deliverables: CSV/Markdown reports in `assets/reports/`; Slack posting via T-SLACK-02.
   - Acceptance: Report attached to Slack digest; fields match spec.

---

## WS-PILOT: Pilot Ops and Feedback Loop

- ID: WS-PILOT | Priority: P1 | Status: todo
- Goal: Run with 2–3 teams; collect metrics and feedback to iterate.

1) T-PILOT-01: Pilot runbook
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: `docs/pilot_runbook.md` with onboarding steps, data sharing, success metrics.
   - Acceptance: A PM can run a pilot with no further guidance.

2) T-PILOT-02: Instrumentation checklist
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-OBS
   - Deliverables: `docs/instrumentation_checklist.md` mapping events to metrics.
   - Acceptance: All MVP features emit required events.

3) T-PILOT-03: Feedback collection + triage
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: Template for user interviews; GitHub labels and issue templates.
   - Acceptance: Feedback organized into prioritized backlog.

---

## WS-DOCS: Documentation & GTM

- ID: WS-DOCS | Priority: P1 | Status: todo
- Goal: Clear setup docs, user guides, and positioning assets.

1) T-DOCS-01: Setup & quickstart
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-FOUND
   - Deliverables: `README.md` quickstart, `.env.example` with safe defaults.
   - Acceptance: New dev completes setup in <15 minutes.

2) T-DOCS-02: User workflows
   - Status: todo | Priority: P1 | Owner: —
   - Deliverables: `docs/user_flows.md` for intake, sourcing, outreach, screening.
   - Acceptance: Each flow includes screenshots or example outputs.

3) T-DOCS-03: Security posture summary
   - Status: todo | Priority: P1 | Owner: — | Depends: WS-TRUST
   - Deliverables: `docs/security_posture.md` with data flows and retention policy.
   - Acceptance: Meets baseline expectations for SOC2 readiness narrative (non-audited).

---

## Milestones (Time-Boxed)

- Week 1: WS-FOUND, WS-DATA (draft), WS-INT-ATS (read-only), WS-INT-EMAIL (auth), WS-INT-SLACK (bootstrap)
- Week 2: WS-FEATURE-INTAKE (JD/scorecard), WS-AI (prompts), WS-OBS (logging), Docs quickstart
- Week 3: WS-FEATURE-SOURCING (query + import + rank), ATS write notes
- Week 4: WS-FEATURE-OUTREACH (drafts + seq), Email reply detection, Slack digest
- Week 5: WS-FEATURE-SCREEN (summary + ATS sync), Metrics dashboards, Compliance items
- Week 6: Pilot run + instrumentation; refine bottlenecks

---

## Acceptance Test Matrix (High Level)

- Intake: Given intake JSON, generate JD/scorecard and interview kit artifacts stored under `assets/outputs/<role-id>/`.
- Sourcing: Given scorecard and candidate CSV, produce ranked list with evidence snippets and explanations.
- Outreach: Given ranked candidate and tone profile, produce a personalized email; reply detection suppresses step 2.
- Screening: Given a resume file, output structured summary + risks/gaps; push a note to ATS (dry-run ok).
- Slack: Daily digest includes bottlenecks; slash commands respond within 3 seconds with actionable content.
- Metrics: Export CSV report summarizing the above for a given date range.

---

## Risk Register (Mitigations)

- Provider limits: Mocked providers and dry-run paths; retries with backoff.
- Data privacy: Redaction in logs and PII labeling; opt-out enforcement at send-time.
- ATS API variance: Start with Greenhouse; keep a normalization layer; add fixtures.
- Time-to-first-value: Prioritize intake→JD/scorecard and sourcing ranker; ensure sample data.
- Over-automation risk: Human-in-the-loop defaults; require confirmation before sends and ATS writes.

---

## Backlog (Post-MVP)

- Improved scheduling with calendar reads/writes.
- Chrome extension deep integration for ATS pages.
- Multi-variant outreach experiments and Bayesian optimization.
- Auto load-balance across multi-role pipelines.
- Deeper interview feedback nudge timing (panel-aware).

---

## Task Claiming Template

Copy-paste this under any task when claiming:

```
Status: in-progress
Owner: @your-handle
Branch: <feature/short-id>
Notes: <link to design/doc/POC>
ETA: <date>
```

