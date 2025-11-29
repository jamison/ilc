from pathlib import Path
from ilc_core.protocol.event_log import ProtocolEventLog
from simulations.end_to_end_epoch_playground import run_epoch_playground


def test_epoch_playground_writes_event_log(tmp_path):
    log_path = tmp_path / "epoch_events.ndjson"
    event_log = ProtocolEventLog(log_path)

    stats = run_epoch_playground(num_epochs=2, tasks_per_epoch=9, event_log=event_log)

    # basic sanity check on stats
    assert set(stats.keys()) == {"EASY", "MEDIUM", "HARD"}

    # log file should exist and contain at least one event
    assert log_path.exists()
    with log_path.open("r", encoding="utf-8") as f:
        lines = [line for line in f.readlines() if line.strip()]
    assert len(lines) > 0
