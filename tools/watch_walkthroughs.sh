#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCH_DIR="${ROOT_DIR}/docs/phases"
STATE_FILE="${ROOT_DIR}/automation/state/walkthrough_watch_state.json"
REVIEW_DIR="${ROOT_DIR}/automation/review_queue"

POLL_SECONDS="${POLL_SECONDS:-30}"
SETTLE_SECONDS="${SETTLE_SECONDS:-120}"
AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW:-0}"

mkdir -p "${ROOT_DIR}/automation/state" "${REVIEW_DIR}"
cd "${ROOT_DIR}"

if [[ ! -f "${STATE_FILE}" ]]; then
  python3 - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
watch_dir = root / "docs" / "phases"
state_file = root / "automation" / "state" / "walkthrough_watch_state.json"

seen = {}
for p in sorted(watch_dir.glob("*_walkthrough.md")):
    rel = str(p.relative_to(root))
    seen[rel] = int(p.stat().st_mtime)

state_file.write_text(
    json.dumps(
        {
            "seen_mtimes": seen,
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(f"Initialized watch state with {len(seen)} existing walkthrough file(s).")
PY
fi

echo "Watching ${WATCH_DIR} (poll=${POLL_SECONDS}s, settle=${SETTLE_SECONDS}s, auto_review=${AUTO_CODEX_REVIEW})"

while true; do
  EVENTS="$(ROOT_DIR_ENV="${ROOT_DIR}" STATE_FILE_ENV="${STATE_FILE}" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["ROOT_DIR_ENV"])
watch_dir = root / "docs" / "phases"
state_file = Path(os.environ["STATE_FILE_ENV"])

state = json.loads(state_file.read_text(encoding="utf-8"))
seen = state.get("seen_mtimes", {})

for p in sorted(watch_dir.glob("*_walkthrough.md")):
    rel = str(p.relative_to(root))
    mt = int(p.stat().st_mtime)
    prev = int(seen.get(rel, 0))
    if mt > prev:
        print(f"{rel}\t{mt}")
PY
)"

  if [[ -n "${EVENTS}" ]]; then
    while IFS=$'\t' read -r rel latest_epoch; do
      [[ -z "${rel}" || -z "${latest_epoch}" ]] && continue
      latest="${ROOT_DIR}/${rel}"

      echo "Detected new/updated walkthrough: ${latest}"
      sleep "${SETTLE_SECONDS}"

      if [[ ! -f "${latest}" ]]; then
        continue
      fi

      current_epoch=$(stat -f "%m" "${latest}" 2>/dev/null || echo 0)
      if [[ "${current_epoch}" -ne "${latest_epoch}" ]]; then
        echo "Walkthrough changed during settle window, deferring: ${latest}"
        continue
      fi

      phase_id="$(basename "${latest}" .md)"
      marker="${REVIEW_DIR}/${phase_id}.json"

      MARKER_ENV="${marker}" STATE_FILE_ENV="${STATE_FILE}" REL_ENV="${rel}" LATEST_EPOCH_ENV="${latest_epoch}" PHASE_ID_ENV="${phase_id}" python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

marker = Path(os.environ["MARKER_ENV"])
state_path = Path(os.environ["STATE_FILE_ENV"])
rel = os.environ["REL_ENV"]
epoch = int(os.environ["LATEST_EPOCH_ENV"])
phase_id = os.environ["PHASE_ID_ENV"]
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

marker.write_text(
    json.dumps(
        {
            "phase_id": phase_id,
            "walkthrough_path": rel,
            "status": "pending_review",
            "timestamp": now,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

state = json.loads(state_path.read_text(encoding="utf-8"))
seen = state.get("seen_mtimes", {})
seen[rel] = epoch
state["seen_mtimes"] = seen
state["updated_at"] = now
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
PY

      echo "Queued review marker: ${marker}"
      if [[ "${AUTO_CODEX_REVIEW}" == "1" ]]; then
        "${ROOT_DIR}/tools/run_codex_review.sh" "${rel}" || true
      fi
    done <<< "${EVENTS}"
  fi

  sleep "${POLL_SECONDS}"
done
