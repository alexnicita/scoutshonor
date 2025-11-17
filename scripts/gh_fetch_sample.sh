#!/usr/bin/env bash
# Fetch a small Greenhouse sample and print normalized JSON.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}"

if [[ -z "${GREENHOUSE_API_KEY:-}" ]]; then
  echo "Set GREENHOUSE_API_KEY in your environment before running." >&2
  exit 1
fi

BASE_URL="${GREENHOUSE_BASE_URL:-https://harvest.greenhouse.io/v1}"
PAGE_SIZE="${GREENHOUSE_PAGE_SIZE:-25}"

python3 - <<'PY'
import json
import os

from src.integrations.greenhouse_client import GreenhouseClient


api_key = os.environ["GREENHOUSE_API_KEY"]
base_url = os.environ.get("GREENHOUSE_BASE_URL", "https://harvest.greenhouse.io/v1")
page_size = int(os.environ.get("GREENHOUSE_PAGE_SIZE", "25"))

with GreenhouseClient(api_key=api_key, base_url=base_url, page_size=page_size) as client:
    payload = {
        "jobs": client.list_jobs(),
        "candidates": client.list_candidates(),
        "applications": client.list_applications(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
PY
