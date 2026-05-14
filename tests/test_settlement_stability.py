import pytest
from datetime import datetime, timezone
from decimal import Decimal
from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEvent

def make_event(
    epoch_id: str,
    epoch_index: int,
    state: str = "committed",
    rewards: Decimal | str = Decimal("100"),
) -> ProtocolEvent:
    return ProtocolEvent(
        kind="commit.epoch",
        payload={
            "event_kind": "commit.epoch",
            "epoch_index": epoch_index,
            "epoch_id": epoch_id,
            "namespace_id": "test_ns",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "finalization_state": state,
            "summary": {
                "reward_total": str(rewards),
                "stake_total": "1000",
                "task_count": 10,
                "agent_count": 2,
            },
            "checksums": {"epoch_events_cid": "cid1", "epoch_state_cid": "cid2"},
        },
        received_at=datetime.now(timezone.utc).isoformat(),
        source="test"
    )

def test_settlement_stability_sequence():
    """
    Strict regression test for settlement logic stability.
    Sequence:
    1. Commit Epoch 10 (Snapshot exists) -> Distributes
    2. Commit Epoch 11 (No Snapshot) -> Stub
    3. Commit Epoch 12 (Snapshot exists) -> Distributes
    4. Commit Epoch 12_v2 (Supersedes 12) -> Reverses 12, Applies 12_v2
    5. Re-apply Epoch 10 -> Idempotent no-op
    """
    ledger = InMemoryLedgerBackend()
    
    # Setup Snapshots
    # Epoch 10: Alice=60%, Bob=40%
    ledger.put_stake_snapshot(StakeSnapshot(
        epoch_id="epoch_10", epoch_index=10, namespace_id="test_ns",
        stakes={"alice": Decimal("600"), "bob": Decimal("400")}, total_stake=Decimal("1000"),
        created_at="2025-01-01T00:00:00Z"
    ))
    # Epoch 12: Alice=100%
    ledger.put_stake_snapshot(StakeSnapshot(
        epoch_id="epoch_12", epoch_index=12, namespace_id="test_ns",
        stakes={"alice": Decimal("1000")}, total_stake=Decimal("1000"),
        created_at="2025-01-01T00:02:00Z"
    ))
    # Epoch 12_v2: Bob=100%
    ledger.put_stake_snapshot(StakeSnapshot(
        epoch_id="epoch_12_v2", epoch_index=12, namespace_id="test_ns",
        stakes={"bob": Decimal("1000")}, total_stake=Decimal("1000"),
        created_at="2025-01-01T00:02:05Z"
    ))

    # 1. Commit Epoch 10 (Rewards=100)
    # Alice +60, Bob +40
    ledger.apply_epoch_settlement(make_event("epoch_10", 10, rewards=Decimal("100")))
    assert ledger.get_balance("alice") == Decimal("60")
    assert ledger.get_balance("bob") == Decimal("40")
    rec = ledger.get_epoch_record("epoch_10")
    assert rec["status"] == "settled"
    assert rec["distribution_status"] == "distributed"

    # 2. Commit Epoch 11 (No Snapshot, Rewards=100) -> Stub
    # Balances unchanged
    ledger.apply_epoch_settlement(make_event("epoch_11", 11, rewards=Decimal("100")))
    assert ledger.get_balance("alice") == Decimal("60")
    assert ledger.get_balance("bob") == Decimal("40")
    rec = ledger.get_epoch_record("epoch_11")
    assert rec["status"] == "settled"
    assert rec["distribution_status"] == "stub_no_snapshot"

    # 3. Commit Epoch 12 (Rewards=50)
    # Alice +50 -> 110.0
    ledger.apply_epoch_settlement(make_event("epoch_12", 12, rewards=Decimal("50")))
    assert ledger.get_balance("alice") == Decimal("110")
    assert ledger.get_balance("bob") == Decimal("40")

    # 4. Commit Epoch 12_v2 (Rewards=200) -> Supersedes Epoch 12
    # Reverse Epoch 12: Alice -50 -> 60.0
    # Apply Epoch 12_v2: Bob +200 -> 240.0
    ledger.apply_epoch_settlement(make_event("epoch_12_v2", 12, rewards=Decimal("200")))
    
    # Alice back to 60.0
    assert ledger.get_balance("alice") == Decimal("60")
    # Bob: 40 (base) + 200 (new) = 240.0
    assert ledger.get_balance("bob") == Decimal("240")
    
    rec_old = ledger.get_epoch_record("epoch_12")
    assert rec_old["status"] == "superseded"
    assert rec_old["superseded_by"] == "epoch_12_v2"
    
    rec_new = ledger.get_epoch_record("epoch_12_v2")
    assert rec_new["status"] == "settled"

    # 5. Idempotency (Re-apply Epoch 10)
    ledger.apply_epoch_settlement(make_event("epoch_10", 10, rewards=Decimal("100")))
    assert ledger.get_balance("alice") == Decimal("60")
    assert ledger.get_balance("bob") == Decimal("240")
