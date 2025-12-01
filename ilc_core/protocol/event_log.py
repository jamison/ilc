from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional
import json

EventKind = Literal[
    "task_outcome",
    "epoch_summary",
    "claim",
    "refutation",
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
