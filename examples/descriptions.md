# Job Description Generation

Generate a long-form job description from minimal inputs.

```
curl -s http://localhost:8000/descriptions/generate \
  -H 'content-type: application/json' \
  -d '{
    "title": "Senior Platform Engineer",
    "seniority": "vp",
    "startup_name": "AcmeAI",
    "stage": "series-a",
    "mission": "Make AI safety practical for real products.",
    "required_skills": ["python", "aws", "kubernetes"],
    "nice_to_have_skills": ["terraform", "observability"],
    "responsibilities": [
      "Own platform reliability",
      "Scale CI/CD",
      "Partner with security"
    ],
    "min_years_experience": 8,
    "remote_ok": true,
    "location": "SF or Remote",
    "employment_type": "Full-time",
    "compensation_range": "$180k-$230k + equity",
    "benefits": ["Health, dental, vision", "401(k) with match"]
  }' | jq -r .description
```

By default, the service uses a deterministic, offline template (no API calls).
To use an LLM, set environment variables in `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

When configured, the service will send a structured prompt to the provider and
return the expanded description.

