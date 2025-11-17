# Security Posture

- Data scope: demo/staging users only; no production PII stored. In-memory repos reset on restart.
- Transport: rely on local network or trusted staging; enable TLS/identity if exposed beyond localhost.
- Secrets: keep API keys out of the repo; use `.env` with non-sensitive defaults and load via environment.
- Logging: avoid writing raw resumes or emails to logs; log only counts and event types (e.g., `reply_routed`).
- Access: limit pilot access to named users; rotate any shared links weekly.
- Dependencies: pinned in `requirements.txt` where possible; review additions for CVEs.
- Third-party sync: ATS integration runs in dry-run mode; inspect payloads before enabling live posting.
