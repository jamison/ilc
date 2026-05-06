from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional, List
import json

from ilc_core.exceptions import EventLogValidationError

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
ZERO = Decimal("0")
COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION = "commit_epoch_canonical_constructor_phase_1235.v0.1"


def _validate_event_envelope(kind: Any, payload: Any) -> None:
    if not isinstance(kind, str):
        raise EventLogValidationError("event_envelope_invalid_kind_type")
    if kind not in _ALLOWED_EVENT_KINDS:
        raise EventLogValidationError(f"event_envelope_unknown_kind:{kind}")
    if not isinstance(payload, dict):
        raise EventLogValidationError("event_envelope_invalid_payload_type")


def _str_to_decimal(value: str, token: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise EventLogValidationError(token) from exc


def _to_decimal(value: int | float | str | Decimal, *, token: str) -> Decimal:
    if isinstance(value, bool):
        raise EventLogValidationError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        number = Decimal(str(value))
    elif isinstance(value, str):
        number = _str_to_decimal(value, token)
    else:
        raise EventLogValidationError(token)
    if not number.is_finite():
        raise EventLogValidationError(token)
    return number


def _to_decimal_no_float(value: int | str | Decimal, *, token: str) -> Decimal:
    if isinstance(value, float):
        raise EventLogValidationError(token)
    return _to_decimal(value, token=token)


def _parse_non_negative_decimal(value: int | float | str | Decimal, *, token: str) -> Decimal:
    number = _to_decimal(value, token=token)
    if number < ZERO:
        raise EventLogValidationError(token)
    return number


def _decimal_to_canonical_string(value: Decimal) -> str:
    if value == ZERO:
        return "0"

    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")

    if rendered.startswith("-"):
        sign = "-"
        body = rendered[1:]
    else:
        sign = ""
        body = rendered

    if "." in body:
        whole, fractional = body.split(".", 1)
        whole = whole.lstrip("0") or "0"
        body = f"{whole}.{fractional}"
    else:
        body = body.lstrip("0") or "0"

    normalized = f"{sign}{body}"
    if normalized in {"-0", "-0.0", ""}:
        return "0"
    return normalized


def _normalize_commit_epoch_output(value: Any) -> Any:
    if isinstance(value, Decimal):
        return _decimal_to_canonical_string(value)
    if isinstance(value, dict):
        return {
            str(key): _normalize_commit_epoch_output(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_normalize_commit_epoch_output(item) for item in value]
    return value


def _exact_to_canonical_string(value: int | float | str | Decimal, *, token: str) -> str:
    return _decimal_to_canonical_string(_to_decimal(value, token=token))


def _exact_to_canonical_string_no_float(value: int | str | Decimal, *, token: str) -> str:
    return _decimal_to_canonical_string(_to_decimal_no_float(value, token=token))



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
            json.dump(asdict(event), f, sort_keys=True, allow_nan=False)
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
            validate_any_commit_epoch_payload(payload)
            payload = _normalize_commit_epoch_output(payload)
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
            json.dump(asdict(evt), f, sort_keys=True, allow_nan=False)
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
        _parse_non_negative_decimal(
            summary["reward_total"],
            token="summary.reward_total must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc
    try:
        _parse_non_negative_decimal(
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


def _validate_commit_epoch_common(payload: Dict[str, Any], *, canonical: bool) -> None:
    if not isinstance(payload, dict):
        raise EventLogValidationError("Payload must be a dict")

    required_top = {
        "event_kind",
        "epoch_index",
        "epoch_id",
        "namespace_id",
        "finalization_state",
        "summary",
        "checksums",
    }
    allowed_top = set(required_top)
    if canonical:
        allowed_top.add("schema_version")
    else:
        required_top.add("created_at")
        allowed_top.add("created_at")

    payload_keys = set(payload.keys())
    missing = required_top - payload_keys
    if missing:
        raise EventLogValidationError(f"Missing required top-level fields: {missing}")
    extra = payload_keys - allowed_top
    if extra:
        raise EventLogValidationError(f"Unexpected top-level fields: {extra}")

    if payload["event_kind"] != "commit.epoch":
        raise EventLogValidationError(f"Invalid event_kind: {payload.get('event_kind')}")

    if canonical:
        if "created_at" in payload:
            raise EventLogValidationError("canonical commit.epoch payload must not contain created_at")
        if payload.get("schema_version") != COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION:
            raise EventLogValidationError("canonical commit.epoch schema_version invalid")
    else:
        if not isinstance(payload["created_at"], str):
            raise EventLogValidationError("created_at must be a string")
        try:
            datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise EventLogValidationError("created_at must be ISO 8601 with UTC timezone") from exc

    if not isinstance(payload["epoch_index"], int) or payload["epoch_index"] < 0:
        raise EventLogValidationError("epoch_index must be a non-negative integer")
    if not isinstance(payload["epoch_id"], str):
        raise EventLogValidationError("epoch_id must be a string")
    if not isinstance(payload["namespace_id"], str):
        raise EventLogValidationError("namespace_id must be a string")
    if payload["finalization_state"] not in {"committed", "rolled_back", "superseded"}:
        raise EventLogValidationError(f"Invalid finalization_state: {payload.get('finalization_state')}")

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
        _parse_non_negative_decimal(
            summary["reward_total"],
            token="summary.reward_total must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc
    try:
        _parse_non_negative_decimal(
            summary["stake_total"],
            token="summary.stake_total must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc

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


def validate_canonical_commit_epoch_payload(payload: Dict[str, Any]) -> None:
    """Validate the Phase 1235 canonical commit.epoch payload shape."""
    _validate_commit_epoch_common(payload, canonical=True)


def validate_any_commit_epoch_payload(payload: Dict[str, Any]) -> None:
    """Accept either the legacy RC payload or the canonical Phase 1235 payload."""
    if isinstance(payload, dict) and "created_at" not in payload:
        validate_canonical_commit_epoch_payload(payload)
    else:
        validate_commit_epoch_payload(payload)


def make_canonical_commit_epoch_event(
    epoch_index: int,
    epoch_id: str,
    namespace_id: str,
    finalization_state: Literal["committed", "rolled_back", "superseded"],
    summary: Dict[str, Any],
    checksums: Dict[str, str],
    source: str = "protocol",
) -> ProtocolEvent:
    """Construct a canonical commit.epoch event without wall-clock protocol time."""
    payload = {
        "event_kind": "commit.epoch",
        "schema_version": COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION,
        "epoch_index": epoch_index,
        "epoch_id": epoch_id,
        "namespace_id": namespace_id,
        "finalization_state": finalization_state,
        "summary": {
            **summary,
            "reward_total": _exact_to_canonical_string_no_float(
                summary.get("reward_total", "0"),
                token="summary.reward_total must be a non-negative number",
            ),
            "stake_total": _exact_to_canonical_string_no_float(
                summary.get("stake_total", "0"),
                token="summary.stake_total must be a non-negative number",
            ),
        },
        "checksums": checksums,
    }

    validate_canonical_commit_epoch_payload(payload)

    return make_event(
        kind="commit.epoch",
        payload=payload,
        source=source,
        schema_version=COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION,
    )


# LEGACY_RC_ONLY: This constructor requires wall-clock created_at, which conflicts
# with Phase 1226 epoch_sequence_only_no_wall_clock policy. Use
# make_canonical_commit_epoch_event for all new code. This constructor is retained
# for backward compatibility with existing RC/devnet test fixtures only.
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
            "reward_total": _exact_to_canonical_string(
                summary.get("reward_total", "0"),
                token="summary.reward_total must be a non-negative number",
            ),
            "stake_total": _exact_to_canonical_string(
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
    try:
        _parse_non_negative_decimal(
            payload["reward"],
            token="reward must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc
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
    try:
        _parse_non_negative_decimal(
            payload["total_reward"],
            token="total_reward must be a non-negative number",
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc


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
    reward: int | float | str | Decimal,
    success: bool,
    source: str = "sim",
    **extra_fields: Any
) -> ProtocolEvent:
    """
    Helper to construct a validated task_outcome event.
    Extra fields are passed through to the payload.
    """
    try:
        canonical_reward = _decimal_to_canonical_string(
            _parse_non_negative_decimal(
                reward,
                token="reward must be a non-negative number",
            )
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc
    payload = {
        "agent_id": agent_id,
        "epoch_index": epoch_index,
        "namespace_id": namespace_id,
        "task_type": task_type,
        "reward": canonical_reward,
        "success": success,
        **extra_fields,
    }
    validate_task_outcome_payload(payload)
    return make_event(kind="task_outcome", payload=payload, source=source)


def make_epoch_summary_event(
    epoch_index: int,
    total_tasks: int,
    total_reward: int | float | str | Decimal,
    source: str = "sim",
    **extra_fields: Any
) -> ProtocolEvent:
    """
    Helper to construct a validated epoch_summary event.
    Extra fields are passed through to the payload.
    """
    try:
        canonical_total_reward = _decimal_to_canonical_string(
            _parse_non_negative_decimal(
                total_reward,
                token="total_reward must be a non-negative number",
            )
        )
    except ValueError as exc:
        raise EventLogValidationError(str(exc)) from exc
    payload = {
        "epoch_index": epoch_index,
        "total_tasks": total_tasks,
        "total_reward": canonical_total_reward,
        **extra_fields,
    }
    validate_epoch_summary_payload(payload)
    return make_event(kind="epoch_summary", payload=payload, source=source)
