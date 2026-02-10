#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_DIR="${ROOT_DIR}/automation/.batch_loop.lock"
QUEUE_PATH="${ROOT_DIR}/automation/phase_queue.json"
STATE_DIR="${ROOT_DIR}/automation/state"
REPORT_DIR="${ROOT_DIR}/automation/reports"
REVIEW_DIR="${ROOT_DIR}/automation/review_queue"
PROMPT_SETTLE_SECONDS="${PROMPT_SETTLE_SECONDS:-300}"
MIN_PHASE_SYNC="${MIN_PHASE_SYNC:-130}"

mkdir -p "${STATE_DIR}" "${REPORT_DIR}" "${REVIEW_DIR}"

if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  echo "Lock exists: ${LOCK_DIR}. Another runner may be active."
  exit 1
fi

cleanup() {
  rmdir "${LOCK_DIR}" 2>/dev/null || true
}
trap cleanup EXIT

if [[ ! -f "${QUEUE_PATH}" ]]; then
  echo "Queue not found: ${QUEUE_PATH}"
  echo "Run tools/phase_queue_init.sh first."
  exit 1
fi

cd "${ROOT_DIR}"

PROMPT_SETTLE_SECONDS="${PROMPT_SETTLE_SECONDS}" MIN_PHASE_SYNC="${MIN_PHASE_SYNC}" python3 - <<'PY'
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
queue_path = root / "automation" / "phase_queue.json"
state_path = root / "automation" / "state" / "current_phase.json"
report_dir = root / "automation" / "reports"
review_dir = root / "automation" / "review_queue"
prompt_dir = root / "docs" / "antigravity_tasks"
settle_seconds = int(os.getenv("PROMPT_SETTLE_SECONDS", "300"))
min_phase_sync = int(os.getenv("MIN_PHASE_SYNC", "130"))
phase_re = re.compile(r"antigravity_prompt__(phase_(\d+)_.*)\.md$")

doc = json.loads(queue_path.read_text(encoding="utf-8"))
items = doc.get("items", [])
item_by_id = {item.get("phase_id"): item for item in items if item.get("phase_id")}

# Sync queue with prompt directory so new prompt files can be picked up without re-init.
added_count = 0
for prompt_path in sorted(prompt_dir.glob("antigravity_prompt__phase_*.md")):
    match = phase_re.match(prompt_path.name)
    if not match:
        continue
    phase_id = match.group(1)
    phase_number = int(match.group(2))
    if phase_number < min_phase_sync:
        continue
    rel_prompt = str(prompt_path.relative_to(root))
    if phase_id in item_by_id:
        # Keep path fresh if file moved/renamed but phase_id is stable.
        item_by_id[phase_id]["prompt_path"] = rel_prompt
        continue
    new_item = {
        "phase_id": phase_id,
        "phase_number": phase_number,
        "prompt_path": rel_prompt,
        "status": "pending",
        "started_at": None,
        "finished_at": None,
        "walkthrough_path": None,
        "commit": None,
        "failure_reason": None,
    }
    items.append(new_item)
    item_by_id[phase_id] = new_item
    added_count += 1

if added_count:
    print(f"Queue sync: added {added_count} new prompt(s).")

now_epoch = time.time()
def _is_prompt_stable(item):
    prompt_rel = item.get("prompt_path")
    if not prompt_rel:
        return False
    prompt_file = root / prompt_rel
    if not prompt_file.exists():
        return False
    age_seconds = now_epoch - prompt_file.stat().st_mtime
    return age_seconds >= settle_seconds

pending = [
    i
    for i in items
    if i.get("status") == "pending"
    and int(i.get("phase_number", 0)) >= min_phase_sync
    and _is_prompt_stable(i)
]
pending.sort(key=lambda x: (x.get("phase_number", 10**9), x.get("phase_id", "")))

if not pending:
    all_pending = [
        i
        for i in items
        if i.get("status") == "pending" and int(i.get("phase_number", 0)) >= min_phase_sync
    ]
    all_pending.sort(key=lambda x: (x.get("phase_number", 10**9), x.get("phase_id", "")))
    if all_pending:
        first = all_pending[0]
        prompt_file = root / first.get("prompt_path", "")
        if prompt_file.exists():
            age_seconds = int(now_epoch - prompt_file.stat().st_mtime)
            remaining = max(0, settle_seconds - age_seconds)
            print("No pending phases are ready yet (stabilization window).")
            print(f"NEXT: {first.get('phase_id')} (wait {remaining}s)")
        else:
            print("No pending phases are ready yet (missing prompt file for next item).")
            print(f"NEXT: {first.get('phase_id')}")
    else:
        print("No pending phases.")
    doc["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    queue_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0)

item = pending[0]
phase_id = item["phase_id"]
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
start_commit = subprocess.check_output(
    ["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True
).strip()

for i in items:
    if i["phase_id"] == phase_id:
        i["status"] = "running"
        i["started_at"] = ts
        i["start_commit"] = start_commit
        i["failure_reason"] = None
        break

doc["updated_at"] = ts
queue_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

state = {
    "phase_id": phase_id,
    "phase_number": item["phase_number"],
    "prompt_path": item["prompt_path"],
    "started_at": ts,
    "start_commit": start_commit,
    "note": "Antigravity should execute this prompt now."
}
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

print(f"READY: {phase_id}")
print(f"PROMPT: {item['prompt_path']}")
print(f"START_COMMIT: {start_commit}")
print("After Antigravity completes, mark done/failed via queue update script.")
print(f"Handoff marker template path: {review_dir / (phase_id + '.json')}")
PY
