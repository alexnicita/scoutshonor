#!/usr/bin/env bash
# Run the daily digest job and optionally post to Slack.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}"

python3 - <<'PY'
import os

from src.jobs.digest import run_digest


run_digest(slack_channel=os.environ.get("SLACK_CHANNEL_ID"), slack_bot_token=os.environ.get("SLACK_BOT_TOKEN"))
PY
