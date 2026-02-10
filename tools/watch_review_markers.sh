#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCH_DIR="${ROOT_DIR}/automation/review_queue"
STATE_FILE="${ROOT_DIR}/automation/state/review_marker_watch_state.json"

POLL_SECONDS="${POLL_SECONDS:-15}"
AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW:-1}"
REVIEW_ON_FAILED="${REVIEW_ON_FAILED:-1}"

mkdir -p "${WATCH_DIR}" "${ROOT_DIR}/automation/state"
cd "${ROOT_DIR}"

if [[ ! -f "${STATE_FILE}" ]]; then
  python3 - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
watch_dir = root / "automation" / "review_queue"
state_path = root / "automation" / "state" / "review_marker_watch_state.json"

seen = {}
for p in sorted(watch_dir.glob("*.json")):
    rel = str(p.relative_to(root))
    seen[rel] = int(p.stat().st_mtime)

state_path.write_text(
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
print(f"Initialized review marker watcher with {len(seen)} existing marker(s).")
PY
fi

echo "Watching ${WATCH_DIR} (poll=${POLL_SECONDS}s, auto_review=${AUTO_CODEX_REVIEW})"

while true; do
  EVENTS="$(ROOT_DIR_ENV="${ROOT_DIR}" STATE_FILE_ENV="${STATE_FILE}" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["ROOT_DIR_ENV"])
watch_dir = root / "automation" / "review_queue"
state_path = Path(os.environ["STATE_FILE_ENV"])

state = json.loads(state_path.read_text(encoding="utf-8"))
seen = state.get("seen_mtimes", {})

for p in sorted(watch_dir.glob("*.json")):
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
      marker_path="${ROOT_DIR}/${rel}"

      if [[ ! -f "${marker_path}" ]]; then
        continue
      fi

      parsed="$(MARKER_ENV="${marker_path}" python3 - <<'PY'
import json
import os
from pathlib import Path

marker = Path(os.environ["MARKER_ENV"])
doc = json.loads(marker.read_text(encoding="utf-8"))
status = str(doc.get("status", "")).strip()
walkthrough = str(doc.get("walkthrough_path", "")).strip()
phase_id = str(doc.get("phase_id", "")).strip()
print(status)
print(walkthrough)
print(phase_id)
PY
)"

      status="$(printf '%s\n' "${parsed}" | sed -n '1p')"
      walkthrough="$(printf '%s\n' "${parsed}" | sed -n '2p')"
      phase_id="$(printf '%s\n' "${parsed}" | sed -n '3p')"

      echo "Detected marker: ${phase_id} status=${status}"

      STATE_FILE_ENV="${STATE_FILE}" REL_ENV="${rel}" LATEST_EPOCH_ENV="${latest_epoch}" python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

state_path = Path(os.environ["STATE_FILE_ENV"])
rel = os.environ["REL_ENV"]
epoch = int(os.environ["LATEST_EPOCH_ENV"])
state = json.loads(state_path.read_text(encoding="utf-8"))
seen = state.get("seen_mtimes", {})
seen[rel] = epoch
state["seen_mtimes"] = seen
state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
PY

      if [[ "${AUTO_CODEX_REVIEW}" != "1" ]]; then
        continue
      fi

      if [[ "${status}" == "done" ]]; then
        if [[ -n "${walkthrough}" && -f "${ROOT_DIR}/${walkthrough}" ]]; then
          "${ROOT_DIR}/tools/run_codex_review.sh" "${walkthrough}" || true
        else
          echo "done marker missing walkthrough path/file for ${phase_id}; review skipped"
        fi
      elif [[ "${status}" == "failed" && "${REVIEW_ON_FAILED}" == "1" ]]; then
        if [[ -n "${walkthrough}" && -f "${ROOT_DIR}/${walkthrough}" ]]; then
          "${ROOT_DIR}/tools/run_codex_review.sh" "${walkthrough}" || true
        else
          echo "failed marker has no walkthrough for ${phase_id}; manual follow-up needed"
        fi
      fi

    done <<< "${EVENTS}"
  fi

  sleep "${POLL_SECONDS}"
done
