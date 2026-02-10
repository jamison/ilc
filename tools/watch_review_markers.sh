#!/usr/bin/env bash
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCH_DIR="${ROOT_DIR}/automation/review_queue"
STATE_FILE="${ROOT_DIR}/automation/state/review_marker_watch_state.json"
HEARTBEAT_FILE="${ROOT_DIR}/automation/state/watch_review_markers_heartbeat.json"

POLL_SECONDS="${POLL_SECONDS:-15}"
AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW:-1}"
REVIEW_ON_FAILED="${REVIEW_ON_FAILED:-1}"

mkdir -p "${WATCH_DIR}" "${ROOT_DIR}/automation/state"
cd "${ROOT_DIR}"

write_heartbeat() {
  local status="$1"
  local note="${2:-}"
  HEARTBEAT_FILE_ENV="${HEARTBEAT_FILE}" STATUS_ENV="${status}" NOTE_ENV="${note}" python3 - <<'PY' >/dev/null 2>&1 || true
import json
import os
from datetime import datetime, timezone
from pathlib import Path

path = Path(os.environ["HEARTBEAT_FILE_ENV"])
status = os.environ.get("STATUS_ENV", "unknown")
note = os.environ.get("NOTE_ENV", "")
payload = {
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "pid": os.getpid(),
    "status": status,
    "note": note,
}
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
}

init_state_if_needed() {
  # Reinitialize state if missing or invalid JSON to avoid permanent crashes.
  ROOT_DIR_ENV="${ROOT_DIR}" STATE_FILE_ENV="${STATE_FILE}" python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["ROOT_DIR_ENV"])
watch_dir = root / "automation" / "review_queue"
state_path = Path(os.environ["STATE_FILE_ENV"])

def rebuild():
    seen = {}
    for p in sorted(watch_dir.glob("*.json")):
        rel = str(p.relative_to(root))
        seen[rel] = int(p.stat().st_mtime)
    payload = {
        "seen_mtimes": seen,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Initialized review marker watcher with {len(seen)} existing marker(s).")

if not state_path.exists():
    rebuild()
else:
    try:
        json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        rebuild()
PY
}

shutdown() {
  write_heartbeat "stopped" "signal_or_exit"
}
trap shutdown EXIT INT TERM

init_state_if_needed
write_heartbeat "starting" "watcher_initialized"

echo "Watching ${WATCH_DIR} (poll=${POLL_SECONDS}s, auto_review=${AUTO_CODEX_REVIEW})"

while true; do
  write_heartbeat "alive" "polling"
  EVENTS=""
  if ! EVENTS="$(ROOT_DIR_ENV="${ROOT_DIR}" STATE_FILE_ENV="${STATE_FILE}" python3 - <<'PY'
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
)"; then
    echo "WARN: failed to scan marker events; retrying next cycle"
    write_heartbeat "error" "event_scan_failed"
    sleep "${POLL_SECONDS}"
    continue
  fi

  if [[ -n "${EVENTS}" ]]; then
    while IFS=$'\t' read -r rel latest_epoch; do
      [[ -z "${rel}" || -z "${latest_epoch}" ]] && continue
      marker_path="${ROOT_DIR}/${rel}"

      # Mark mtime as seen first so malformed markers don't crash-loop.
      if ! STATE_FILE_ENV="${STATE_FILE}" REL_ENV="${rel}" LATEST_EPOCH_ENV="${latest_epoch}" python3 - <<'PY'
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
      then
        echo "WARN: failed to update watcher state for ${rel}"
      fi

      if [[ ! -f "${marker_path}" ]]; then
        continue
      fi

      parsed=""
      if ! parsed="$(MARKER_ENV="${marker_path}" python3 - <<'PY'
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
)"; then
        echo "WARN: failed to parse marker JSON ${marker_path}; skipped"
        write_heartbeat "warn" "invalid_marker_json"
        continue
      fi

      status="$(printf '%s\n' "${parsed}" | sed -n '1p')"
      walkthrough="$(printf '%s\n' "${parsed}" | sed -n '2p')"
      phase_id="$(printf '%s\n' "${parsed}" | sed -n '3p')"

      echo "Detected marker: ${phase_id} status=${status}"
      write_heartbeat "alive" "marker:${phase_id}:${status}"

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
