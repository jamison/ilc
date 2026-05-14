
import pytest
from decimal import Decimal
from ilc_core.ledger.settlement_verification import verify_stake_distribution
from ilc_core.ledger.stake_snapshot import StakeSnapshot

def test_verify_stake_distribution_ok():
    """
    Test a perfect distribution scenario.
    """
    epoch_record = {
        "distribution_status": "distributed",
        "summary": {"reward_total": "100"}
    }
    
    snapshot = StakeSnapshot(
        epoch_id="test", epoch_index=1, namespace_id="ns",
        stakes={"a": Decimal("10"), "b": Decimal("30")},
        total_stake=Decimal("40"),
        created_at="now"
    )
    
    # Expected: a gets 25, b gets 75
    balances_before = {"a": "0", "b": "0"}
    balances_after = {"a": "25", "b": "75"} # 100 total
    
    result = verify_stake_distribution(epoch_record, snapshot, balances_before, balances_after)
    
    assert result["ok"] is True
    assert result["total_delta"] == "100"
    assert result["expected_total"] == "100"
    assert result["max_agent_error"] == "0"
    assert not result["top_errors"]

def test_verify_stub_ok():
    """
    Test stub distribution (no changes allowed).
    """
    epoch_record = {
        "distribution_status": "stub_no_snapshot",
        "summary": {"reward_total": "100"}
    }
    # Snapshot might be None or irrelevant
    # Verification should handle None snapshot if stub status
    
    balances_before = {"a": "10"}
    balances_after = {"a": "10"}
    
    result = verify_stake_distribution(epoch_record, None, balances_before, balances_after)
    
    assert result["ok"] is True
    assert result["total_delta"] == "0"
    assert result["expected_total"] == "0"

def test_verify_mismatch():
    """
    Test incorrect distribution detection.
    """
    epoch_record = {
        "distribution_status": "distributed",
        "summary": {"reward_total": "100"}
    }
    snapshot = StakeSnapshot(
        epoch_id="test", epoch_index=1, namespace_id="ns",
        stakes={"a": Decimal("1")},
        total_stake=Decimal("1"),
        created_at="now"
    )
    
    # Expected: 100. Actual: 90
    balances_before = {"a": "0"}
    balances_after = {"a": "90"}
    
    result = verify_stake_distribution(epoch_record, snapshot, balances_before, balances_after)
    
    assert result["ok"] is False
    assert result["total_delta"] == "90"
    assert result["expected_total"] == "100"
    assert result["max_agent_error"] == "10"
    assert result["top_errors"] # should contain info about agent 'a'

def test_verify_extra_agent_leak():
    """
    Test if an agent not in stake map receives funds.
    """
    epoch_record = {
        "distribution_status": "distributed",
        "summary": {"reward_total": "10"}
    }
    snapshot = StakeSnapshot(
        epoch_id="test", epoch_index=1, namespace_id="ns",
        stakes={"a": Decimal("1")},
        total_stake=Decimal("1"),
        created_at="now"
    )
    
    # 'a' gets correct 10. But 'b' gets 5 from nowhere.
    balances_before = {"a": "0", "b": "0"}
    balances_after = {"a": "10", "b": "5"}
    
    result = verify_stake_distribution(epoch_record, snapshot, balances_before, balances_after)
    
    assert result["ok"] is False # Total mismatch (15 vs 10) AND individual mismatch for b
    assert result["total_delta"] == "15"

def test_verify_distributed_without_snapshot_fails():
    """
    Test that distributed status without a snapshot fails verification.
    """
    epoch_record = {
        "distribution_status": "distributed",
        "summary": {"reward_total": "10"}
    }
    balances_before = {"a": "0"}
    balances_after = {"a": "10"}

    result = verify_stake_distribution(epoch_record, None, balances_before, balances_after)

    assert result["ok"] is False
    assert result["top_errors"]
    assert "missing_snapshot_or_total_stake" in result["top_errors"][0]

def test_verify_distributed_no_snapshot():
    """
    Test guard against 'distributed' status with missing snapshot.
    """
    epoch_record = {
        "distribution_status": "distributed",
        "summary": {"reward_total": "100"}
    }
    # No snapshot
    balances_before = {"a": "0"}
    balances_after = {"a": "10"}
    
    result = verify_stake_distribution(epoch_record, None, balances_before, balances_after)
    
    assert result["ok"] is False
    assert "missing_snapshot_or_total_stake" in result["top_errors"][0]
