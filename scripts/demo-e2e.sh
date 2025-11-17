#!/usr/bin/env bash
set -euo pipefail

# Demo: end-to-end recruiter flow against a local server on :8000
# - Creates a startup and role
# - Creates a few candidates
# - Runs matching to get the top candidate(s)
# - Generates outreach for the top match

BASE_URL=${BASE_URL:-http://localhost:8000}

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing dependency: $1" >&2
    exit 1
  fi
}

require curl
require jq

echo "Checking server at $BASE_URL/health ..."
curl -fsS "$BASE_URL/health" | jq . >/dev/null

echo "Creating startup ..."
STARTUP=$(curl -fsS -X POST "$BASE_URL/startups/" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "AcmeAI",
    "stage": "series-a",
    "domains": ["fintech", "ai"],
    "location": "SF",
    "stack": ["python", "aws", "fastapi"]
  }')
STARTUP_ID=$(echo "$STARTUP" | jq -r .id)
echo "Startup ID: $STARTUP_ID"

echo "Creating role ..."
ROLE=$(curl -fsS -X POST "$BASE_URL/roles/" \
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
  }")
ROLE_ID=$(echo "$ROLE" | jq -r .id)
echo "Role ID: $ROLE_ID"

echo "Creating candidates ..."
ALICE=$(curl -fsS -X POST "$BASE_URL/candidates/" -H 'Content-Type: application/json' -d '{
  "full_name": "Alice Smith",
  "current_title": "Director of Engineering",
  "titles": ["Engineering Manager"],
  "years_experience": 10,
  "skills": ["python", "aws", "fastapi", "kubernetes"],
  "domains": ["fintech"],
  "locations": ["San Francisco"],
  "remote_preference": true
}')
ALICE_ID=$(echo "$ALICE" | jq -r .id)

BOB=$(curl -fsS -X POST "$BASE_URL/candidates/" -H 'Content-Type: application/json' -d '{
  "full_name": "Bob Lee",
  "current_title": "Senior Engineer",
  "titles": ["Engineer"],
  "years_experience": 6,
  "skills": ["python"],
  "domains": ["healthtech"],
  "locations": ["New York"],
  "remote_preference": true
}')
BOB_ID=$(echo "$BOB" | jq -r .id)

echo "Running match (top 1) ..."
MATCH=$(curl -fsS -X POST "$BASE_URL/match" -H 'Content-Type: application/json' \
  -d "{ \"role_id\": \"$ROLE_ID\", \"limit\": 1 }")
TOP_CAND_ID=$(echo "$MATCH" | jq -r '.results[0].candidate.id')
TOP_CAND_NAME=$(echo "$MATCH" | jq -r '.results[0].candidate.full_name')
TOP_SCORE=$(echo "$MATCH" | jq -r '.results[0].score')
echo "Top match: $TOP_CAND_NAME ($TOP_CAND_ID) score=$TOP_SCORE"

echo "Generating outreach for top match (email + linkedin) ..."
OUTREACH=$(curl -fsS -X POST "$BASE_URL/outreach" -H 'Content-Type: application/json' \
  -d "{ \"candidate_id\": \"$TOP_CAND_ID\", \"role_id\": \"$ROLE_ID\", \"tone\": \"professional\", \"channels\": [\"email\", \"linkedin\"] }")
echo "$OUTREACH" | jq .

echo "Done. Use the generated subject/body to reach out."

