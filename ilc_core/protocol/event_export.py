# SPDX-License-Identifier: AGPL-3.0-or-later
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

CLAIM_HEADERS = [
    "id",
    "type",
    "agent_id",
    "content",
    "net_stake",
    "timestamp",
    "parent_ids",
    "target_id",
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

def flatten_claim_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a 'claim' or 'refutation' event into a row dict.

    Accepts wrapped event {"kind": "claim", "payload": {...}}
    or bare payload if it looks like one.
    """
    payload = event.get("payload", event)
    if not payload:
        payload = event
    if "body" in event:
        payload = event["body"]

    parent_ids = payload.get("parent_ids") or []
    if isinstance(parent_ids, list):
        parent_ids_str = ";".join(str(p) for p in parent_ids)
    else:
        parent_ids_str = str(parent_ids)

    return {
        "id": payload.get("id"),
        "type": payload.get("type", "claim"),
        "agent_id": payload.get("agent_id"),
        "content": payload.get("content"),
        "net_stake": payload.get("net_stake", 0.0),
        "timestamp": payload.get("timestamp"),
        "parent_ids": parent_ids_str,
        "target_id": payload.get("target_id"),
    }

def _detect_event_kind(event: Dict[str, Any]) -> str | None:
    kind = event.get("kind") or event.get("type")
    if kind:
        return kind
    if "task_type" in event:
        return "task_outcome"
    if "total_tasks" in event:
        return "epoch_summary"
    return None

def _read_ndjson_events(path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not path.exists():
        return events
    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events

def export_event_log_to_csv(
    ndjson_path: PathLike,
    *,
    tasks_csv_path: PathLike,
    epochs_csv_path: PathLike,
    claims_csv_path: Optional[PathLike] = None,
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

    counts = {
        "task_outcomes": 0,
        "epoch_summaries": 0,
        "claims": 0,
    }
    
    # Prepare lists to hold rows (for MVP, in-memory is fine)
    task_rows: List[Dict[str, Any]] = []
    epoch_rows: List[Dict[str, Any]] = []
    claim_rows: List[Dict[str, Any]] = []

    for event in _read_ndjson_events(ndjson_path):
        kind = _detect_event_kind(event)
        if kind == "task_outcome":
            task_rows.append(flatten_task_outcome_event(event))
            counts["task_outcomes"] += 1
        elif kind == "epoch_summary":
            epoch_rows.append(flatten_epoch_summary_event(event))
            counts["epoch_summaries"] += 1
        elif kind in ("claim", "refutation"):
            claim_rows.append(flatten_claim_event(event))
            counts["claims"] += 1

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

    # Write Claims CSV (if requested)
    if claims_csv_path is not None:
        claims_csv_path = Path(claims_csv_path)
        claims_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with claims_csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CLAIM_HEADERS)
            writer.writeheader()
            writer.writerows(claim_rows)

    return counts
