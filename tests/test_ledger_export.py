
import pytest
import json
import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

from ilc_core.ledger.backend import LedgerBackend, InMemoryLedgerBackend
from ilc_core.ledger.ledger_export import export_ledger_state_json, export_ledger_state_csv
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
         "status": "committed",
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
    assert data["epoch_records"]["ns:0001"]["status"] == "committed"
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
    assert "committed" in row
