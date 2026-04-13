
import pytest
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

from ilc_core.ledger.backend import LedgerBackend, InMemoryLedgerBackend
from ilc_core.ledger.canon_export import export_canon_state_json, compute_canon_hash
from ilc_core.ledger.stake_snapshot import StakeSnapshot

def test_canon_export_determinism():
    """
    Test that exporting the same state twice results in identical hashes and file content.
    """
    ledger = InMemoryLedgerBackend()
    ledger.balances = {"alice": 100.0, "bob": 50.0}
    
    # Add some records
    # Create fake epoch records manually
    record_1 = {
         "epoch_index": 1,
         "epoch_id": "ns:0001",
         "status": "settled",
         "summary": {"tasks": 10, "reward": 50.0}
    }
    ledger.epoch_records["ns:0001"] = record_1
    
    # Add snapshot
    snap = StakeSnapshot(
        epoch_id="ns:0001",
        epoch_index=1,
        namespace_id="ns",
        stakes={"alice": 1.0},
        total_stake=1.0,
        created_at="2026-01-01T00:00:00Z"
    )
    ledger.stake_snapshots["ns:0001"] = snap
    
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = Path(tmpdir) / "canon_1.json"
        p2 = Path(tmpdir) / "canon_2.json"
        
        res1 = export_canon_state_json(ledger, p1)
        res2 = export_canon_state_json(ledger, p2)

        # Check hashes
        # Fix: Now that generated_at is excluded from hashing, the hashes MUST be identical.
        assert res1["canon_hash"] != ""
        assert res1["canon_hash"] == res2["canon_hash"]
        
        # Verify Content Integrity (hash matches payload content minus exclusion)
        with open(p1) as f:
            data1 = json.load(f)
            
        h1 = data1.pop("canon_hash")
         # We must also replicate the exclusion logic used in export
        if "generated_at" in data1:
            del data1["generated_at"]
            
        computed1 = compute_canon_hash(data1)
        assert h1 == computed1

def test_canon_export_structure():
    """
    Verify required fields exist.
    """
    ledger = InMemoryLedgerBackend()
    ledger.balances = {"alice": 10.0}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "out.json"
        res = export_canon_state_json(ledger, p)
        
        assert "canon_hash" in res
        assert "generated_at" in res
        assert res["canon_export_version"] == "v0.1"
        assert res["balances"] == {"alice": "10"}

def test_no_mutation():
    """
    Ensure export doesn't change the ledger.
    """
    ledger = InMemoryLedgerBackend()
    ledger.balances = {"alice": 10.0}
    original_balances = ledger.balances.copy()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "out.json"
        export_canon_state_json(ledger, p)
        
    assert ledger.balances == original_balances
