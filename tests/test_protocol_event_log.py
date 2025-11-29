from pathlib import Path
from ilc_core.protocol.event_log import ProtocolEventLog, make_event


def test_protocol_event_log_append_and_iter(tmp_path):
    log_path = tmp_path / "events.ndjson"
    event_log = ProtocolEventLog(log_path)

    e1 = make_event(
        kind="task_outcome",
        payload={"task_type": "claim.submit", "epoch": 1},
        source="test",
        schema_version="0.1.0",
    )
    e2 = make_event(
        kind="task_outcome",
        payload={"task_type": "claim.submit", "epoch": 2},
        source="test",
        schema_version="0.1.0",
    )

    event_log.append(e1)
    event_log.append(e2)

    assert log_path.exists()

    events = list(event_log.iter_events())
    assert len(events) == 2
    assert events[0].kind == "task_outcome"
    assert events[0].payload["epoch"] == 1
    assert events[1].payload["epoch"] == 2
    assert events[0].source == "test"

def test_protocol_event_log_empty_iter(tmp_path):
    log_path = tmp_path / "events_empty.ndjson"
    event_log = ProtocolEventLog(log_path)

    events = list(event_log.iter_events())
    assert events == []
