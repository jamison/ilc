"""
Tests for ILC Ledger Backend.
"""

import pytest
from datetime import datetime, timezone

from ilc_core.ledger.backend import (
    InMemoryLedgerBackend,
    settle_commit_epoch,
)
from ilc_core.protocol.event_log import ProtocolEvent


def make_commit_epoch_payload(
    epoch_id: str,
    epoch_index: int,
    finalization_state: str = "committed",
    namespace_id: str = "test_ns",
    reward_total: float = 100.0,
    stake_total: float = 1000.0,
    task_count: int = 10,
    agent_count: int = 2,
) -> dict:
    """Helper to create commit.epoch payload."""
    return {
        "event_kind": "commit.epoch",
        "epoch_index": epoch_index,
        "epoch_id": epoch_id,
        "namespace_id": namespace_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "finalization_state": finalization_state,
        "summary": {
            "reward_total": reward_total,
            "stake_total": stake_total,
            "task_count": task_count,
            "agent_count": agent_count,
        },
        "checksums": {
            "epoch_events_cid": "QmTestEventsCid",
            "epoch_state_cid": "QmTestStateCid",
        },
    }


def make_commit_epoch_event(payload: dict, source: str = "test") -> ProtocolEvent:
    """Helper to create ProtocolEvent for commit.epoch."""
    return ProtocolEvent(
        kind="commit.epoch",
        payload=payload,
        received_at=datetime.now(timezone.utc).isoformat(),
        source=source,
    )


class TestInMemoryLedgerBackend:
    def test_apply_committed_epoch_stores_record(self):
        """Committed epoch should store a settled record."""
        ledger = InMemoryLedgerBackend()
        
        payload = make_commit_epoch_payload(
            epoch_id="epoch_42_abc",
            epoch_index=42,
            finalization_state="committed",
        )
        event = make_commit_epoch_event(payload)
        
        ledger.apply_epoch_settlement(event)
        
        record = ledger.get_epoch_record("epoch_42_abc")
        assert record is not None
        assert record["epoch_id"] == "epoch_42_abc"
        assert record["epoch_index"] == 42
        assert record["status"] == "settled"
        assert record["finalization_state"] == "committed"
        # Stub rule: balances unchanged
        assert record["distribution_status"] == "stub_no_balance_change"

    def test_rolled_back_marks_epoch_no_balance_change(self):
        """Rolled back epoch should mark record but not change balances."""
        ledger = InMemoryLedgerBackend()
        
        payload = make_commit_epoch_payload(
            epoch_id="epoch_50_rolled",
            epoch_index=50,
            finalization_state="rolled_back",
        )
        event = make_commit_epoch_event(payload)
        
        ledger.apply_epoch_settlement(event)
        
        record = ledger.get_epoch_record("epoch_50_rolled")
        assert record is not None
        assert record["status"] == "rolled_back"
        # No balance changes
        assert ledger.get_balance("any_agent") == 0.0

    def test_superseded_updates_prior_and_marks_new(self):
        """Superseded flow: prior epoch marked superseded, new epoch applied."""
        ledger = InMemoryLedgerBackend()
        
        # First epoch at index 60
        payload1 = make_commit_epoch_payload(
            epoch_id="epoch_60_v1",
            epoch_index=60,
            finalization_state="committed",
            reward_total=100.0,
        )
        event1 = make_commit_epoch_event(payload1)
        ledger.apply_epoch_settlement(event1)
        
        record1 = ledger.get_epoch_record("epoch_60_v1")
        assert record1["status"] == "settled"
        
        # Superseding epoch at same index
        payload2 = make_commit_epoch_payload(
            epoch_id="epoch_60_v2",
            epoch_index=60,
            finalization_state="committed",
            reward_total=90.0,  # Corrected amount
        )
        event2 = make_commit_epoch_event(payload2)
        ledger.apply_epoch_settlement(event2)
        
        # Prior should be superseded
        record1_after = ledger.get_epoch_record("epoch_60_v1")
        assert record1_after["status"] == "superseded"
        assert record1_after["superseded_by"] == "epoch_60_v2"
        
        # New should be settled
        record2 = ledger.get_epoch_record("epoch_60_v2")
        assert record2["status"] == "settled"

    def test_idempotency_reapply_same_epoch_is_noop(self):
        """Re-applying same epoch_id should be a no-op."""
        ledger = InMemoryLedgerBackend()
        
        payload = make_commit_epoch_payload(
            epoch_id="epoch_70_idem",
            epoch_index=70,
            finalization_state="committed",
        )
        event = make_commit_epoch_event(payload)
        
        # Apply twice
        ledger.apply_epoch_settlement(event)
        ledger.apply_epoch_settlement(event)
        
        record = ledger.get_epoch_record("epoch_70_idem")
        assert record is not None
        assert record["status"] == "settled"
        # Should only have one record for this epoch_id
        assert len([r for r in ledger.epoch_records.values() 
                   if r["epoch_id"] == "epoch_70_idem"]) == 1

    def test_balances_unchanged_with_stub_rule(self):
        """With stub distribution rule, balances remain at 0."""
        ledger = InMemoryLedgerBackend()
        
        payload = make_commit_epoch_payload(
            epoch_id="epoch_80_balance",
            epoch_index=80,
            finalization_state="committed",
            reward_total=500.0,
        )
        event = make_commit_epoch_event(payload)
        
        ledger.apply_epoch_settlement(event)
        
        # Balances should be unchanged (stub rule)
        assert ledger.get_balance("agent_1") == 0.0
        assert ledger.get_balance("agent_2") == 0.0

    def test_get_epoch_record_not_found(self):
        """get_epoch_record returns None for unknown epoch_id."""
        ledger = InMemoryLedgerBackend()
        assert ledger.get_epoch_record("unknown") is None


class TestSettleCommitEpoch:
    def test_settle_commit_epoch_entrypoint(self):
        """settle_commit_epoch should delegate to ledger backend."""
        ledger = InMemoryLedgerBackend()
        
        payload = make_commit_epoch_payload(
            epoch_id="epoch_90_entry",
            epoch_index=90,
            finalization_state="committed",
        )
        event = make_commit_epoch_event(payload)
        
        settle_commit_epoch(ledger, event)
        
        record = ledger.get_epoch_record("epoch_90_entry")
        assert record is not None
        assert record["status"] == "settled"
