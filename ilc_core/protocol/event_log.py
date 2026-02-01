from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional, List
import json

EventKind = Literal[
    "task_outcome",
    "epoch_summary",
    "epoch_config",
    "claim",
    "refutation",
    "mcp_tool_call",
    "commit.epoch",
]  # keep small for now




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
            json.dump(asdict(evt), f)
            f.write("\n")


def validate_commit_epoch_payload(payload: Dict[str, Any]) -> None:
    """
    Validate that a payload matches the commit.epoch schema.
    Raises ValueError if invalid.
    """
    required_top = {
        "event_kind", "epoch_index", "epoch_id", "namespace_id",
        "created_at", "finalization_state", "summary", "checksums"
    }
    missing = required_top - set(payload.keys())
    if missing:
        raise ValueError(f"Missing required top-level fields: {missing}")

    if payload["event_kind"] != "commit.epoch":
        raise ValueError(f"Invalid event_kind: {payload.get('event_kind')}")

    if payload["finalization_state"] not in {"committed", "rolled_back", "superseded"}:
        raise ValueError(f"Invalid finalization_state: {payload.get('finalization_state')}")

    # Validate summary
    summary = payload["summary"]
    required_summary = {"task_count", "agent_count", "reward_total", "stake_total"}
    missing_summary = required_summary - set(summary.keys())
    if missing_summary:
        raise ValueError(f"Missing required summary fields: {missing_summary}")

    # Validate checksums
    checksums = payload["checksums"]
    required_checksums = {"epoch_events_cid", "epoch_state_cid"}
    missing_checksums = required_checksums - set(checksums.keys())
    if missing_checksums:
        raise ValueError(f"Missing required checksums fields: {missing_checksums}")


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
        "summary": summary,
        "checksums": checksums,
    }
    
    validate_commit_epoch_payload(payload)
    
    return make_event(
        kind="commit.epoch",
        payload=payload,
        source=source
    )

