from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.exceptions import EventLogValidationError
from ilc_core.protocol.event_log import ProtocolEvent, ProtocolEventLog, write_events_to_file


SCOPED_EMITTER_FILES = [
    Path("ilc_core/sim/devnet_epoch_orchestrator.py"),
    Path("ilc_core/sim/devnet_multi_epoch.py"),
]


def test_phase_195_protocol_event_log_append_rejects_invalid_payload_type(tmp_path: Path) -> None:
    event_log = ProtocolEventLog(tmp_path / "events.ndjson")

    bad_event = ProtocolEvent(
        kind="task_outcome",
        payload="not_a_dict",  # type: ignore[arg-type]
        received_at="2026-02-16T00:00:00Z",
        source="test:phase195",
    )

    with pytest.raises(EventLogValidationError, match="event_envelope_invalid_payload_type"):
        event_log.append(bad_event)


def test_phase_195_write_events_rejects_unknown_kind(tmp_path: Path) -> None:
    out_path = tmp_path / "events.ndjson"
    bad_event = ProtocolEvent(
        kind="unknown_kind",  # type: ignore[arg-type]
        payload={"value": 1},
        received_at="2026-02-16T00:00:00Z",
        source="test:phase195",
    )

    with pytest.raises(EventLogValidationError, match="event_envelope_unknown_kind"):
        write_events_to_file([bad_event], out_path)


def test_phase_195_scoped_emitters_do_not_use_direct_event_list_append_shortcut() -> None:
    for path in SCOPED_EMITTER_FILES:
        source = path.read_text(encoding="utf-8")
        assert "event_logger.events.append(" not in source, (
            f"{path}: direct event list append detected; use logger emit pathway"
        )
