#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <phase_id> <done|failed> [walkthrough_path] [commit_hash] [failure_reason]"
  exit 2
fi

PHASE_ID="$1"
STATUS="$2"
WALKTHROUGH_PATH="${3:-}"
COMMIT_HASH="${4:-}"
FAILURE_REASON="${5:-}"

if [[ "${STATUS}" != "done" && "${STATUS}" != "failed" ]]; then
  echo "Invalid status: ${STATUS}. Use done|failed."
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE_PATH="${ROOT_DIR}/automation/phase_queue.json"
REVIEW_DIR="${ROOT_DIR}/automation/review_queue"
REPORT_DIR="${ROOT_DIR}/automation/reports"

mkdir -p "${REVIEW_DIR}" "${REPORT_DIR}"

cd "${ROOT_DIR}"

if [[ "${STATUS}" == "done" ]]; then
  if [[ -z "${WALKTHROUGH_PATH}" ]]; then
    echo "done status requires walkthrough_path"
    exit 2
  fi
  if [[ ! -f "${ROOT_DIR}/${WALKTHROUGH_PATH}" ]]; then
    echo "walkthrough_path not found on disk: ${WALKTHROUGH_PATH}"
    exit 2
  fi
  case "${WALKTHROUGH_PATH}" in
    docs/phases/*_walkthrough.md) ;;
    *)
      echo "walkthrough_path must be under docs/phases/*_walkthrough.md"
      exit 2
      ;;
  esac

  if [[ -z "${COMMIT_HASH}" ]]; then
    echo "done status requires commit_hash"
    exit 2
  fi
  if ! git rev-parse --verify "${COMMIT_HASH}^{commit}" >/dev/null 2>&1; then
    echo "commit_hash does not resolve to a commit: ${COMMIT_HASH}"
    exit 2
  fi
fi

PHASE_ID_ENV="${PHASE_ID}" STATUS_ENV="${STATUS}" WALKTHROUGH_PATH_ENV="${WALKTHROUGH_PATH}" COMMIT_HASH_ENV="${COMMIT_HASH}" FAILURE_REASON_ENV="${FAILURE_REASON}" python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

phase_id = os.environ["PHASE_ID_ENV"]
status = os.environ["STATUS_ENV"]
walkthrough = os.environ["WALKTHROUGH_PATH_ENV"]
commit = os.environ["COMMIT_HASH_ENV"]
failure_reason = os.environ["FAILURE_REASON_ENV"]

root = Path.cwd()
queue_path = root / "automation" / "phase_queue.json"
review_dir = root / "automation" / "review_queue"
report_dir = root / "automation" / "reports"

doc = json.loads(queue_path.read_text(encoding="utf-8"))
items = doc.get("items", [])

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
target = None
for item in items:
    if item.get("phase_id") == phase_id:
        target = item
        break

if target is None:
    raise SystemExit(f"phase_id not found: {phase_id}")

if status == "done":
    start_commit = target.get("start_commit")
    started_at = target.get("started_at")
    if start_commit:
        if commit == start_commit:
            raise SystemExit(
                f"done status rejected: commit {commit} equals start_commit {start_commit}; no new commit was created for this phase"
            )
    else:
        # Migration-safe fallback for queue items created before start_commit was tracked.
        if not started_at:
            raise SystemExit(
                "done status rejected: missing start_commit and started_at; cannot verify that a new commit was created during this phase"
            )
        import subprocess

        commit_epoch = int(
            subprocess.check_output(
                ["git", "show", "-s", "--format=%ct", commit], cwd=root, text=True
            ).strip()
        )
        started_dt = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        started_epoch = int(started_dt.timestamp())
        if commit_epoch < started_epoch:
            raise SystemExit(
                f"done status rejected: commit {commit} timestamp is older than phase started_at {started_at}"
            )

target["status"] = status
target["finished_at"] = now
if walkthrough:
    target["walkthrough_path"] = walkthrough
if commit:
    target["commit"] = commit
if status == "failed":
    target["failure_reason"] = failure_reason or "unspecified_failure"

doc["updated_at"] = now
queue_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

marker = {
    "phase_id": phase_id,
    "status": status,
    "prompt_path": target.get("prompt_path"),
    "walkthrough_path": target.get("walkthrough_path"),
    "commit": target.get("commit"),
    "timestamp": now
}
marker_path = review_dir / f"{phase_id}.json"
marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

if status == "failed":
    report_path = report_dir / f"{phase_id}_failure.md"
    report_path.write_text(
        f"# {phase_id} failure\\n\\n- Time: {now}\\n- Reason: {target.get('failure_reason')}\\n",
        encoding="utf-8",
    )

print(f"Updated {phase_id} -> {status}")
print(f"Review marker: {marker_path}")
PY
