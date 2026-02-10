#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE_PATH="${ROOT_DIR}/automation/phase_queue.json"
PROMPT_DIR="${ROOT_DIR}/docs/antigravity_tasks"
MIN_PHASE_SYNC="${MIN_PHASE_SYNC:-130}"

if [[ ! -f "${QUEUE_PATH}" ]]; then
  echo "Queue not found: ${QUEUE_PATH}"
  echo "Run MIN_PHASE=<n> ./tools/phase_queue_init.sh first."
  exit 1
fi

if [[ ! -d "${PROMPT_DIR}" ]]; then
  echo "Prompt directory not found: ${PROMPT_DIR}"
  exit 1
fi

cd "${ROOT_DIR}"

MIN_PHASE_SYNC="${MIN_PHASE_SYNC}" python3 - <<'PY'
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
queue_path = root / "automation" / "phase_queue.json"
prompt_dir = root / "docs" / "antigravity_tasks"
min_phase_sync = int(os.getenv("MIN_PHASE_SYNC", "130"))
phase_re = re.compile(r"antigravity_prompt__(phase_(\d+)_.*)\.md$")

doc = json.loads(queue_path.read_text(encoding="utf-8"))
items = doc.get("items", [])
item_by_id = {item.get("phase_id"): item for item in items if item.get("phase_id")}

added = 0
updated = 0

for prompt_path in sorted(prompt_dir.glob("antigravity_prompt__phase_*.md")):
    match = phase_re.match(prompt_path.name)
    if not match:
        continue

    phase_id = match.group(1)
    phase_number = int(match.group(2))
    if phase_number < min_phase_sync:
        continue

    rel_prompt = str(prompt_path.relative_to(root))
    existing = item_by_id.get(phase_id)
    if existing is None:
        new_item = {
            "phase_id": phase_id,
            "phase_number": phase_number,
            "prompt_path": rel_prompt,
            "status": "pending",
            "started_at": None,
            "start_commit": None,
            "finished_at": None,
            "walkthrough_path": None,
            "commit": None,
            "failure_reason": None,
        }
        items.append(new_item)
        item_by_id[phase_id] = new_item
        added += 1
        continue

    # Keep prompt path and phase number fresh if file moved/renamed.
    if existing.get("prompt_path") != rel_prompt:
        existing["prompt_path"] = rel_prompt
        updated += 1
    if int(existing.get("phase_number", -1)) != phase_number:
        existing["phase_number"] = phase_number
        updated += 1

items.sort(key=lambda x: (int(x.get("phase_number", 10**9)), str(x.get("phase_id", ""))))
doc["items"] = items
doc["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
queue_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

print(f"Queue sync complete: added={added}, updated={updated}, total_items={len(items)}")
PY
