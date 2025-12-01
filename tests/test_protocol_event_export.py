import json
import csv
from ilc_core.protocol.event_export import export_event_log_to_csv

def test_export_synthetic_log(tmp_path):
    """Test exporting a manually constructed log file."""
    log_file = tmp_path / "events.ndjson"
    tasks_csv = tmp_path / "tasks.csv"
    epochs_csv = tmp_path / "epochs.csv"

    events = [
        {"type": "task_outcome", "payload": {
            "task_id": "t1",
            "task_type": "claim.submit",
            "domain": "MEDIUM",
            "agent_id": "agent:demo",
            "epoch": 3,
            "stake_spent": 0.1,
            "reward_paid": 0.2,
            "success": True,
        }},
        {"type": "epoch_summary", "payload": {
            "epoch": 3,
            "total_tasks": 40,
            "total_ecu_spent": 2.0,
            "total_reward_paid": 3.0,
            "clearing_price_ilc_per_ecu": 1.5,
        }},
        # Unknown event type should be ignored
        {"type": "unknown_event", "payload": {"foo": "bar"}}
    ]

    with log_file.open("w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    counts = export_event_log_to_csv(
        log_file,
        tasks_csv_path=tasks_csv,
        epochs_csv_path=epochs_csv
    )

    assert counts["task_outcomes"] == 1
    assert counts["epoch_summaries"] == 1
    
    # Verify Tasks CSV
    with tasks_csv.open("r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["task_id"] == "t1"
        assert rows[0]["stake_spent"] == "0.1"

    # Verify Epochs CSV
    with epochs_csv.open("r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["epoch"] == "3"
        assert rows[0]["total_tasks"] == "40"

def test_export_bare_events(tmp_path):
    """Test exporting bare (unwrapped) protocol events."""
    log_file = tmp_path / "bare_events.ndjson"
    tasks_csv = tmp_path / "tasks.csv"
    epochs_csv = tmp_path / "epochs.csv"

    events = [
        {
            "task_id": "t2",
            "task_type": "refute.attempt",
            "domain": "HARD",
            "stake_spent": 0.5
        },
        {
            "epoch": 4,
            "total_tasks": 10
        }
    ]

    with log_file.open("w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    counts = export_event_log_to_csv(
        log_file,
        tasks_csv_path=tasks_csv,
        epochs_csv_path=epochs_csv
    )

    assert counts["task_outcomes"] == 1
    assert counts["epoch_summaries"] == 1

def test_export_synthetic_log_with_claims(tmp_path):
    log_file = tmp_path / "events.ndjson"
    tasks_csv = tmp_path / "tasks.csv"
    epochs_csv = tmp_path / "epochs.csv"
    claims_csv = tmp_path / "claims.csv"

    events = [
        {"type": "task_outcome", "payload": {
            "task_id": "t1",
            "task_type": "claim.submit",
            "domain": "MEDIUM",
            "agent_id": "agent:demo",
            "epoch": 1,
            "stake_spent": 1.0,
            "reward_paid": 0.5,
            "ecu_spent": 1.0,
            "meta": {},
        }},
        {"type": "epoch_summary", "payload": {
            "epoch": 1,
            "total_tasks": 1,
            "total_ecu_spent": 1.0,
            "total_reward_paid": 0.5,
            "clearing_price_ilc_per_ecu": 0.5,
        }},
        {"type": "claim", "payload": {
            "id": "c1",
            "type": "claim",
            "agent_id": "agent:demo",
            "content": "1 + 1 = 2",
            "net_stake": 10.0,
            "timestamp": "2025-01-01T00:00:00Z",
            "parent_ids": ["axiom:math:01"],
            "target_id": None,
        }},
    ]

    with log_file.open("w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    counts = export_event_log_to_csv(
        log_file,
        tasks_csv_path=tasks_csv,
        epochs_csv_path=epochs_csv,
        claims_csv_path=claims_csv,
    )

    assert counts["task_outcomes"] == 1
    assert counts["epoch_summaries"] == 1
    assert counts["claims"] == 1

    # Verify claims.csv contents
    with claims_csv.open("r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == "c1"
    assert row["agent_id"] == "agent:demo"
    assert row["net_stake"] == "10.0"
