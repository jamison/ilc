import csv
import json
from pathlib import Path
from typing import Dict, Union, Any, List, Optional

PathLike = Union[str, Path]

# Canonical CSV Headers
TASK_OUTCOME_HEADERS = [
    "task_id",
    "task_type",
    "domain",
    "agent_id",
    "epoch",
    "stake_spent",
    "reward_paid",
    "success",
]

EPOCH_SUMMARY_HEADERS = [
    "epoch",
    "total_tasks",
    "total_ecu_spent",
    "total_reward_paid",
    "clearing_price_ilc_per_ecu",
]

def flatten_task_outcome_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a task_outcome event into a row dict.
    Accepts wrapped event {"type": "task_outcome", "payload": {...}}
    or bare payload if it looks like one.
    """
    payload = event.get("payload", event)
    # If it was wrapped but payload is missing, fallback to event itself (bare)
    if not payload: 
        payload = event

    # Handle "body" key if present (some older/test events might use it)
    if "body" in event:
        payload = event["body"]

    return {
        "task_id": payload.get("task_id"),
        "task_type": payload.get("task_type", "unknown"),
        "domain": payload.get("domain", "unknown"),
        "agent_id": payload.get("agent_id"),
        "epoch": payload.get("epoch"),
        "stake_spent": payload.get("stake_spent", 0.0),
        "reward_paid": payload.get("reward_paid", 0.0),
        "success": payload.get("success", False),
    }

def flatten_epoch_summary_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten an epoch_summary event into a row dict.
    """
    payload = event.get("payload", event)
    if not payload:
        payload = event
    
    if "body" in event:
        payload = event["body"]

    return {
        "epoch": payload.get("epoch", -1),
        "total_tasks": payload.get("total_tasks", 0),
        "total_ecu_spent": payload.get("total_ecu_spent", 0.0),
        "total_reward_paid": payload.get("total_reward_paid", 0.0),
        "clearing_price_ilc_per_ecu": payload.get("clearing_price_ilc_per_ecu", 0.0),
    }

def export_event_log_to_csv(
    ndjson_path: PathLike,
    *,
    tasks_csv_path: PathLike,
    epochs_csv_path: PathLike,
) -> Dict[str, int]:
    """
    Read a ProtocolEventLog NDJSON file and export:
    - task_outcome events -> tasks_csv_path
    - epoch_summary events -> epochs_csv_path

    Returns a dict with simple counts.
    """
    ndjson_path = Path(ndjson_path)
    tasks_csv_path = Path(tasks_csv_path)
    epochs_csv_path = Path(epochs_csv_path)

    counts = {"task_outcomes": 0, "epoch_summaries": 0}
    
    # Prepare lists to hold rows (for MVP, in-memory is fine)
    task_rows: List[Dict[str, Any]] = []
    epoch_rows: List[Dict[str, Any]] = []

    if ndjson_path.exists():
        with ndjson_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    # Detect type
                    # 1. Wrapped event
                    kind = event.get("kind") or event.get("type")
                    
                    # 2. Bare event inference (fallback)
                    if not kind:
                        if "task_type" in event:
                            kind = "task_outcome"
                        elif "total_tasks" in event:
                            kind = "epoch_summary"
                    
                    if kind == "task_outcome":
                        task_rows.append(flatten_task_outcome_event(event))
                        counts["task_outcomes"] += 1
                    elif kind == "epoch_summary":
                        epoch_rows.append(flatten_epoch_summary_event(event))
                        counts["epoch_summaries"] += 1
                    
                except json.JSONDecodeError:
                    continue

    # Write Tasks CSV
    tasks_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with tasks_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TASK_OUTCOME_HEADERS)
        writer.writeheader()
        writer.writerows(task_rows)

    # Write Epochs CSV
    epochs_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with epochs_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EPOCH_SUMMARY_HEADERS)
        writer.writeheader()
        writer.writerows(epoch_rows)

    return counts
