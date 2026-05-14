
import pytest
from decimal import Decimal
from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.settlement_metrics import compute_settlement_metrics
from ilc_core.ledger.stake_snapshot import StakeSnapshot

def test_settlement_metrics_empty():
    ledger = InMemoryLedgerBackend()
    metrics = compute_settlement_metrics(ledger)
    assert metrics["num_epochs_total"] == 0
    assert metrics["num_snapshots"] == 0
    assert metrics["total_rewards_distributed"] == "0"

def test_settlement_metrics_mixed_states():
    ledger = InMemoryLedgerBackend()
    
    # 1. Settled + Distributed
    ledger.epoch_records["e1"] = {
        "epoch_index": 1,
        "status": "settled",
        "distribution_status": "distributed",
        "summary": {"reward_total": "100"}
    }
    
    # 2. Settled + Stub (no snapshot)
    ledger.epoch_records["e2"] = {
        "epoch_index": 2,
        "status": "settled",
        "distribution_status": "stub_no_snapshot",
        "summary": {"reward_total": "50"}
    }
    
    # 3. Rolled Back
    ledger.epoch_records["e3"] = {
        "epoch_index": 3,
        "status": "rolled_back",
        "summary": {"reward_total": "200"} # Should not be counted
    }
    
    # 4. Unknown/Pending
    ledger.epoch_records["e4"] = {
        "epoch_index": 4,
        "status": "pending"
    }
    
    # 5. Add a snapshot
    ledger.put_stake_snapshot(StakeSnapshot(
        epoch_id="e1",
        epoch_index=1,
        namespace_id="ns1",
        stakes={"a1": Decimal("1")},
        total_stake=Decimal("1"),
        created_at="now"
    ))
    
    metrics = compute_settlement_metrics(ledger)
    
    assert metrics["num_epochs_total"] == 4
    assert metrics["num_epochs_settled"] == 2
    assert metrics["num_epochs_rolled_back"] == 1
    assert metrics["num_snapshots"] == 1
    
    # Rewards:
    # Distributed: 100.0 (from e1)
    # Stubbed: 50.0 (from e2)
    # Rolled back (e3) ignored
    # Pending (e4) ignored
    assert metrics["total_rewards_distributed"] == "100"
    assert metrics["total_rewards_stubbed"] == "50"
