# Sourcing Helpers

Generate boolean/X-Ray strings and search your in-memory pool.

## Boolean search strings

1) Create a startup and role (see `examples/recruiter_flow.md`).
2) Generate boolean strings for LinkedIn, Google X-Ray, and GitHub:

```bash
curl -sS -X POST http://localhost:8000/sourcing/boolean \
  -H 'Content-Type: application/json' \
  -d '{
    "role_id": "<ROLE_ID>",
    "locations": ["San Francisco", "Remote"],
    "extras": ["fintech"]
  }' | jq .
```

Paste `linkedin` into LinkedIn search; paste `google_xray` into Google; use `github` at https://github.com/search.

## Bulk import + search

```bash
# Bulk import two candidates
curl -sS -X POST http://localhost:8000/candidates/bulk \
  -H 'Content-Type: application/json' \
  -d '[
    {"full_name": "Casey Doe", "skills": ["python", "aws"], "titles": ["Engineering Manager"], "domains": ["fintech"], "locations": ["San Francisco"]},
    {"full_name": "Dev Patel", "skills": ["golang", "kubernetes"], "titles": ["Senior Engineer"], "domains": ["devtools"], "locations": ["Remote"]}
  ]' | jq .

# Search candidates by skills AND domain
curl -sS "http://localhost:8000/candidates/search?skills=python,aws&domains=fintech" | jq .
```

Note: storage is in-memory; restart clears data.

