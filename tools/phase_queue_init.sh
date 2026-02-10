#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE_PATH="${ROOT_DIR}/automation/phase_queue.json"
PROMPT_DIR="${ROOT_DIR}/docs/antigravity_tasks"
MIN_PHASE="${MIN_PHASE:-0}"

mkdir -p "${ROOT_DIR}/automation"

MIN_PHASE="${MIN_PHASE}" python3 - <<'PY'
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
prompt_dir = root / "docs" / "antigravity_tasks"
queue_path = root / "automation" / "phase_queue.json"
status_path = root / "docs" / "phases" / "STATUS.md"
min_phase = int(os.getenv("MIN_PHASE", "0"))

phase_re = re.compile(r"antigravity_prompt__phase_(\d+)_.*\.md$")
status_re = re.compile(r"^##\s+Phase\s+(\d+)-", re.IGNORECASE)

completed_numbers = set()
if status_path.exists():
    for line in status_path.read_text(encoding="utf-8").splitlines():
        m = status_re.match(line.strip())
        if m:
            completed_numbers.add(int(m.group(1)))

items = []
for p in sorted(prompt_dir.glob("antigravity_prompt__phase_*.md")):
    m = phase_re.match(p.name)
    if not m:
        continue
    n = int(m.group(1))
    if n < min_phase:
        continue
    phase_id = p.stem.replace("antigravity_prompt__", "")
    is_fix_prompt = "_fix" in phase_id
    status = "pending" if is_fix_prompt else ("done" if n in completed_numbers else "pending")
    items.append({
        "phase_id": phase_id,
        "phase_number": n,
        "prompt_path": str(p.relative_to(root)),
        "status": status,
        "started_at": None,
        "start_commit": None,
        "finished_at": None,
        "walkthrough_path": None,
        "commit": None,
        "failure_reason": None,
    })

items.sort(key=lambda x: x["phase_number"])

doc = {
    "queue_version": "v0.1",
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "items": items,
}

queue_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
print(f"Initialized queue with {len(items)} items at {queue_path}")
PY
