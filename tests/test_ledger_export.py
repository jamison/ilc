
import pytest
import json
import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

from ilc_core.ledger.backend import LedgerBackend, InMemoryLedgerBackend
from ilc_core.ledger.ledger_export import (
    export_ledger_state_json,
    export_ledger_state_csv,
    export_ledger_distribution_checks_csv,
)
from ilc_core.ledger.stake_snapshot import StakeSnapshot

def test_ledger_export_in_memory(tmp_path):
    """
    Test that the export helpers produce valid JSON/CSV files from an InMemoryLedgerBackend.
    """
    ledger = InMemoryLedgerBackend()
    
    # 1. Populate some data
    # Create fake epoch records
    record_1 = {
         "epoch_index": 1,
         "epoch_id": "ns:0001",
         "status": "settled",
         "summary": {"tasks": 10, "reward": 50.0},
         "checksums": {"state": "abc"}
    }
    
    # We cheat/use internal storage if available since we know InMemory has it
    # referencing the implementation in `ilc_core/ledger/backend.py` (which we assume has these or we set them)
    # If the InMemoryLedgerBackend doesn't expose `epoch_records` publicly that's an issue for the test setup,
    # but our export code accessed `getattr(ledger, "epoch_records", {})`.
    # So we can just set it on the instance if it's not there by default.
    
    if not hasattr(ledger, "epoch_records"):
        ledger.epoch_records = {} # type: ignore
    if not hasattr(ledger, "stake_snapshots"):
        ledger.stake_snapshots = {} # type: ignore
    if not hasattr(ledger, "balances"):
        ledger.balances = {} # type: ignore
        
    ledger.epoch_records["ns:0001"] = record_1
    ledger.balances["agent_alice"] = 100.0
    ledger.balances["agent_bob"] = 50.0
    
    # Snapshot
    snap = StakeSnapshot(
        epoch_id="ns:0001",
        epoch_index=1,
        namespace_id="ns",
        stakes={"agent_alice": 1.0},
        total_stake=1.0,
        created_at="2026-01-01T00:00:00Z"
    )
    ledger.stake_snapshots["ns:0001"] = snap

    # 2. Run Exports
    json_path = tmp_path / "ledger_state.json"
    csv_path = tmp_path / "ledger_state.csv"
    
    export_ledger_state_json(ledger, json_path)
    export_ledger_state_csv(ledger, csv_path)
    
    # 3. Validation
    assert json_path.exists()
    assert csv_path.exists()
    
    # Check JSON
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert "epoch_records" in data
    assert "stake_snapshots" in data
    assert "balances" in data
    assert data["epoch_records"]["ns:0001"]["status"] == "settled"
    assert data["balances"]["agent_alice"] == 100.0
    
    # Check CSV
    # Should have flattened summary_tasks etc
    content = csv_path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()
    assert len(lines) == 2  # Header + 1 row
    
    header = lines[0].split(",")
    assert "epoch_index" in header
    assert "summary_tasks" in header
    
    row = lines[1]
    assert "settled" in row

def test_export_ledger_distribution_checks_csv(tmp_path):
    """
    Test that distribution checks are exported to CSV correctly.
    """
    checks = [
        {
            "epoch_id": "ns:0001",
            "ok": True,
            "total_delta": 100.0,
            "expected_total": 100.0,
            "max_agent_error": 0.0,
            "top_errors": ["alice:0.000000", "bob:0.000001"],
            "input_hash": "deadbeef",
        }
    ]

    out_path = tmp_path / "ledger_distribution_checks.csv"
    export_ledger_distribution_checks_csv(checks, out_path)

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 2  # header + 1 row

    header = content[0].split(",")
    assert header == [
        "epoch_id",
        "ok",
        "total_delta",
        "expected_total",
        "max_agent_error",
        "top_errors",
        "input_hash",
    ]

    row = content[1].split(",")
    assert row[0] == "ns:0001"
    assert row[1] == "True"
    assert row[2] == "100.0"
    assert row[3] == "100.0"
    assert row[4] == "0.0"
    assert row[5] == "alice:0.000000;bob:0.000001"
    assert row[6] == "deadbeef"
