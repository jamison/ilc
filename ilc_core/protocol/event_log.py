from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional, List
import json

from ilc_core.exceptions import EventLogValidationError
from ilc_core.ledger.exact_numeric import exact_to_canonical_string, parse_non_negative_decimal

EventKind = Literal[
    "task_outcome",
    "epoch_summary",
    "epoch_config",
    "claim",
    "refutation",
    "mcp_tool_call",
    "commit.epoch",
]  # keep small for now

_ALLOWED_EVENT_KINDS = {
    "task_outcome",
    "epoch_summary",
    "epoch_config",
    "claim",
    "refutation",
    "mcp_tool_call",
    "commit.epoch",
}


def _validate_event_envelope(kind: Any, payload: Any) -> None:
    if not isinstance(kind, str):
        raise EventLogValidationError("event_envelope_invalid_kind_type")
    if kind not in _ALLOWED_EVENT_KINDS:
        raise EventLogValidationError(f"event_envelope_unknown_kind:{kind}")
    if not isinstance(payload, dict):
        raise EventLogValidationError("event_envelope_invalid_payload_type")



@dataclass
class ProtocolEvent:
    kind: EventKind
    payload: Dict[str, Any]
    received_at: str
    source: str = "sim"
    # Optional versioning hook; keep in but default it.
    schema_version: Optional[str] = None


class ProtocolEventLog:
    """
    Append-only NDJSON log for protocol-shaped events.

    Each line is a JSON object conforming to ProtocolEvent (kind + payload).
    This is a low-level storage primitive, not a protocol validator.
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def append(self, event: ProtocolEvent) -> None:
        _validate_event_envelope(event.kind, event.payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            json.dump(asdict(event), f)
            f.write("\n")

    def iter_events(self) -> Iterable[ProtocolEvent]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                yield ProtocolEvent(**data)


def make_event(
    kind: EventKind,
    payload: Dict[str, Any],
    *,
    source: str = "sim:end_to_end_epoch_playground",
    schema_version: Optional[str] = None,
) -> ProtocolEvent:
    """
    Convenience helper to stamp received_at and optional schema_version.
    """
    now = datetime.now(timezone.utc).isoformat()
    return ProtocolEvent(
        kind=kind,
        payload=payload,
        received_at=now,
        source=source,
        schema_version=schema_version,
    )


@dataclass
class EventLogger:
    """
    In-memory accumulator for events (sim-only).
    """
    events: List[ProtocolEvent]

    def emit(
        self,
        kind: EventKind,
        payload: Dict[str, Any],
        source: str = "sim",
    ) -> None:
        _validate_event_envelope(kind, payload)
        if kind == "commit.epoch":
            validate_commit_epoch_payload(payload)
        elif kind == "epoch_summary":
            validate_epoch_summary_payload(payload)
        evt = make_event(kind, payload, source=source)
        self.events.append(evt)


def write_events_to_file(events: List[ProtocolEvent], path: Path | str) -> None:
    """
    Write a list of ProtocolEvents to an NDJSON file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for evt in events:
            _validate_event_envelope(evt.kind, evt.payload)
            json.dump(asdict(evt), f)
            f.write("\n")


def validate_commit_epoch_payload(payload: Dict[str, Any]) -> None:
    """
    Validate that a payload matches the commit.epoch schema.
    Raises EventLogValidationError if invalid.
    """
    if not isinstance(payload, dict):
        raise EventLogValidationError("Payload must be a dict")

    required_top = {
        "event_kind",
        "epoch_index",
        "epoch_id",
        "namespace_id",
        "created_at",
        "finalization_state",
        "summary",
        "checksums",
    }
    payload_keys = set(payload.keys())
    missing = required_top - payload_keys
    if missing:
        raise EventLogValidationError(f"Missing required top-level fields: {missing}")
    extra = payload_keys - required_top
    if extra:
        raise EventLogValidationError(f"Unexpected top-level fields: {extra}")

    if payload["event_kind"] != "commit.epoch":
        raise EventLogValidationError(f"Invalid event_kind: {payload.get('event_kind')}")

    if not isinstance(payload["epoch_index"], int) or payload["epoch_index"] < 0:
        raise EventLogValidationError("epoch_index must be a non-negative integer")
    if not isinstance(payload["epoch_id"], str):
        raise EventLogValidationError("epoch_id must be a string")
    if not isinstance(payload["namespace_id"], str):
        raise EventLogValidationError("namespace_id must be a string")
    if not isinstance(payload["created_at"], str):
        raise EventLogValidationError("created_at must be a string")
    try:
        datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventLogValidationError("created_at must be ISO 8601 with UTC timezone") from exc

    if payload["finalization_state"] not in {"committed", "rolled_back", "superseded"}:
        raise EventLogValidationError(f"Invalid finalization_state: {payload.get('finalization_state')}")

    # Validate summary
    summary = payload["summary"]
    if not isinstance(summary, dict):
        raise EventLogValidationError("summary must be a dict")
    required_summary = {"task_count", "agent_count", "reward_total", "stake_total"}
    summary_keys = set(summary.keys())
    missing_summary = required_summary - summary_keys
    if missing_summary:
        raise EventLogValidationError(f"Missing required summary fields: {missing_summary}")
    extra_summary = summary_keys - required_summary
    if extra_summary:
        raise EventLogValidationError(f"Unexpected summary fields: {extra_summary}")
    if not isinstance(summary["task_count"], int) or summary["task_count"] < 0:
        raise EventLogValidationError("summary.task_count must be a non-negative integer")
    if not isinstance(summary["agent_count"], int) or summary["agent_count"] < 0:
        raise EventLogValidationError("summary.agent_count must be a non-negative integer")
    try:
        parse_non_negative_decimal(
            summary["reward_total"],
            token="summary.reward_total must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc
    try:
        parse_non_negative_decimal(
            summary["stake_total"],
            token="summary.stake_total must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc

    # Validate checksums
    checksums = payload["checksums"]
    if not isinstance(checksums, dict):
        raise EventLogValidationError("checksums must be a dict")
    required_checksums = {"epoch_events_cid", "epoch_state_cid"}
    checksum_keys = set(checksums.keys())
    missing_checksums = required_checksums - checksum_keys
    if missing_checksums:
        raise EventLogValidationError(f"Missing required checksums fields: {missing_checksums}")
    extra_checksums = checksum_keys - required_checksums
    if extra_checksums:
        raise EventLogValidationError(f"Unexpected checksums fields: {extra_checksums}")
    if not isinstance(checksums["epoch_events_cid"], str):
        raise EventLogValidationError("checksums.epoch_events_cid must be a string")
    if not isinstance(checksums["epoch_state_cid"], str):
        raise EventLogValidationError("checksums.epoch_state_cid must be a string")


def make_commit_epoch_event(
    epoch_index: int,
    epoch_id: str,
    namespace_id: str,
    created_at: str,
    finalization_state: Literal["committed", "rolled_back", "superseded"],
    summary: Dict[str, Any],
    checksums: Dict[str, str],
    source: str = "protocol"
) -> ProtocolEvent:
    """
    Helper to construct a validated commit.epoch event.
    """
    payload = {
        "event_kind": "commit.epoch",
        "epoch_index": epoch_index,
        "epoch_id": epoch_id,
        "namespace_id": namespace_id,
        "created_at": created_at,
        "finalization_state": finalization_state,
        "summary": {
            **summary,
            "reward_total": exact_to_canonical_string(
                summary.get("reward_total", "0"),
                token="summary.reward_total must be a non-negative number",
            ),
            "stake_total": exact_to_canonical_string(
                summary.get("stake_total", "0"),
                token="summary.stake_total must be a non-negative number",
            ),
        },
        "checksums": checksums,
    }
    
    validate_commit_epoch_payload(payload)
    
    return make_event(
        kind="commit.epoch",
        payload=payload,
        source=source
    )


# ============================================================
# Lenient validators (allow extra fields, fail on missing required)
# ============================================================

def validate_epoch_config_payload(payload: Dict[str, Any]) -> None:
    """
    Lenient validator for epoch_config payloads.
    Validates required keys + basic types. Allows extra keys.
    """
    if not isinstance(payload, dict):
        raise EventLogValidationError("payload must be a dict")

    required = {"epoch_index", "benchmark_suite_id", "created_at", "namespace_id"}
    missing = required - set(payload.keys())
    if missing:
        raise EventLogValidationError(f"Missing required epoch_config fields: {missing}")

    if not isinstance(payload["epoch_index"], int) or payload["epoch_index"] < 0:
        raise EventLogValidationError("epoch_index must be a non-negative integer")
    if not isinstance(payload["benchmark_suite_id"], str):
        raise EventLogValidationError("benchmark_suite_id must be a string")
    if not isinstance(payload["created_at"], str):
        raise EventLogValidationError("created_at must be a string")
    if not isinstance(payload["namespace_id"], str):
        raise EventLogValidationError("namespace_id must be a string")


def validate_task_outcome_payload(payload: Dict[str, Any]) -> None:
    """
    Lenient validator for task_outcome payloads.
    Validates required keys + basic types. Allows extra keys.
    """
    if not isinstance(payload, dict):
        raise EventLogValidationError("payload must be a dict")

    required = {"agent_id", "epoch_index", "namespace_id", "task_type", "reward", "success"}
    missing = required - set(payload.keys())
    if missing:
        raise EventLogValidationError(f"Missing required task_outcome fields: {missing}")

    if not isinstance(payload["agent_id"], str):
        raise EventLogValidationError("agent_id must be a string")
    if not isinstance(payload["epoch_index"], int) or payload["epoch_index"] < 0:
        raise EventLogValidationError("epoch_index must be a non-negative integer")
    if not isinstance(payload["namespace_id"], str):
        raise EventLogValidationError("namespace_id must be a string")
    if not isinstance(payload["task_type"], str):
        raise EventLogValidationError("task_type must be a string")
    if not isinstance(payload["reward"], (int, float)) or payload["reward"] < 0:
        raise EventLogValidationError("reward must be a non-negative number")
    if not isinstance(payload["success"], bool):
        raise EventLogValidationError("success must be a boolean")


def validate_epoch_summary_payload(payload: Dict[str, Any]) -> None:
    """
    Lenient validator for epoch_summary payloads.
    Validates required keys + basic types. Allows extra keys.
    """
    if not isinstance(payload, dict):
        raise EventLogValidationError("payload must be a dict")

    required = {"epoch_index", "total_tasks", "total_reward"}
    missing = required - set(payload.keys())
    if missing:
        raise EventLogValidationError(f"Missing required epoch_summary fields: {missing}")

    if not isinstance(payload["epoch_index"], int) or payload["epoch_index"] < 0:
        raise EventLogValidationError("epoch_index must be a non-negative integer")
    if not isinstance(payload["total_tasks"], int) or payload["total_tasks"] < 0:
        raise EventLogValidationError("total_tasks must be a non-negative integer")
    if not isinstance(payload["total_reward"], (int, float)) or payload["total_reward"] < 0:
        raise EventLogValidationError("total_reward must be a non-negative number")


# ============================================================
# Helper constructors (parallel to make_commit_epoch_event)
# ============================================================

def make_epoch_config_event(
    epoch_index: int,
    benchmark_suite_id: str,
    created_at: str,
    namespace_id: str,
    source: str = "protocol",
    **extra_fields: Any
) -> ProtocolEvent:
    """
    Helper to construct a validated epoch_config event.
    Extra fields are passed through to the payload.
    """
    payload = {
        "epoch_index": epoch_index,
        "benchmark_suite_id": benchmark_suite_id,
        "created_at": created_at,
        "namespace_id": namespace_id,
        **extra_fields,
    }
    validate_epoch_config_payload(payload)
    return make_event(kind="epoch_config", payload=payload, source=source)


def make_task_outcome_event(
    agent_id: str,
    epoch_index: int,
    namespace_id: str,
    task_type: str,
    reward: float,
    success: bool,
    source: str = "sim",
    **extra_fields: Any
) -> ProtocolEvent:
    """
    Helper to construct a validated task_outcome event.
    Extra fields are passed through to the payload.
    """
    payload = {
        "agent_id": agent_id,
        "epoch_index": epoch_index,
        "namespace_id": namespace_id,
        "task_type": task_type,
        "reward": reward,
        "success": success,
        **extra_fields,
    }
    validate_task_outcome_payload(payload)
    return make_event(kind="task_outcome", payload=payload, source=source)


def make_epoch_summary_event(
    epoch_index: int,
    total_tasks: int,
    total_reward: float,
    source: str = "sim",
    **extra_fields: Any
) -> ProtocolEvent:
    """
    Helper to construct a validated epoch_summary event.
    Extra fields are passed through to the payload.
    """
    payload = {
        "epoch_index": epoch_index,
        "total_tasks": total_tasks,
        "total_reward": total_reward,
        **extra_fields,
    }
    validate_epoch_summary_payload(payload)
    return make_event(kind="epoch_summary", payload=payload, source=source)
