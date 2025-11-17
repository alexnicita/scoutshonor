# Recruiter Flow (End-to-End)

This walks through using the API to go from job posting → matched candidates → outreach messages.

## 0) Start the server

- `make setup` (create venv if needed)
- `make run` (starts FastAPI on `http://localhost:8000`)
- Open `http://localhost:8000/docs` for interactive API docs.

## 1) Create a startup

```bash
curl -sS -X POST http://localhost:8000/startups/ \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "AcmeAI",
    "stage": "series-a",
    "domains": ["fintech", "ai"],
    "location": "SF",
    "stack": ["python", "aws", "fastapi"]
  }' | jq .
```

Note the `id` from the response (e.g., `STARTUP_ID`).

## 2) Create your role (job posting)

```bash
curl -sS -X POST http://localhost:8000/roles/ \
  -H 'Content-Type: application/json' \
  -d "{
    \"startup_id\": \"$STARTUP_ID\",
    \"title\": \"VP Engineering\",
    \"required_skills\": [\"python\", \"aws\", \"fastapi\"],
    \"nice_to_have_skills\": [\"kubernetes\"],
    \"min_years_experience\": 8,
    \"responsibilities\": [\"team leadership\", \"hiring\", \"platform\"],
    \"seniority\": \"vp\",
    \"remote_ok\": true
  }" | jq .
```

Note the `id` from the response (e.g., `ROLE_ID`).

## 3) Add candidates to your pool

```bash
# Strong match
curl -sS -X POST http://localhost:8000/candidates/ -H 'Content-Type: application/json' -d '{
  "full_name": "Alice Smith",
  "current_title": "Director of Engineering",
  "titles": ["Engineering Manager"],
  "years_experience": 10,
  "skills": ["python", "aws", "fastapi", "kubernetes"],
  "domains": ["fintech"],
  "locations": ["San Francisco"],
  "remote_preference": true
}' | jq .

# Weaker match
curl -sS -X POST http://localhost:8000/candidates/ -H 'Content-Type: application/json' -d '{
  "full_name": "Bob Lee",
  "current_title": "Senior Engineer",
  "titles": ["Engineer"],
  "years_experience": 6,
  "skills": ["python"],
  "domains": ["healthtech"],
  "locations": ["New York"],
  "remote_preference": true
}' | jq .
```

## 4) Rank candidates for the role

```bash
curl -sS -X POST http://localhost:8000/match \
  -H 'Content-Type: application/json' \
  -d "{ \"role_id\": \"$ROLE_ID\", \"limit\": 5 }" | jq .
```

You’ll get a sorted list with an overall score, a breakdown, and reasons (signals).

## 5) Generate outreach for a top match

```bash
curl -sS -X POST http://localhost:8000/outreach \
  -H 'Content-Type: application/json' \
  -d '{
    "candidate_id": "<TOP_CANDIDATE_ID>",
    "role_id": "'$ROLE_ID'",
    "tone": "professional",
    "channels": ["email", "linkedin"]
  }' | jq .
```

This returns ready-to-send subject + body for each channel.

## Tips

- Adjust signal weights via env vars before starting the server (e.g. `WEIGHT_SKILLS=0.4 WEIGHT_LOCATION=0.05 make run`).
- Scope matches by list of candidate IDs with `candidate_ids` in the `/match` request.
- Use `/docs` to try requests interactively and see schemas.
- Persisting data: this demo uses an in-memory store. Restarting resets data.

