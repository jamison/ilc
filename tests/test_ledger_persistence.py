"""
Tests for FileLedgerBackend persistence and parity.
"""

import pytest
import os
from datetime import datetime, timezone
from typing import Generator, Any

from ilc_core.ledger.persistent_backend import FileLedgerBackend
from ilc_core.ledger import get_ledger_backend
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEvent


@pytest.fixture
def temp_storage_dir(tmp_path: Any) -> Generator[str, None, None]:
    """Provide a temporary directory for storage."""
    d = tmp_path / "ilc_ledger_test"
    d.mkdir()
    yield str(d)


def make_commit_event(epoch_id: str, index: int, reward: float = 100.0) -> ProtocolEvent:
    """Helper to create minimal valid commit event."""
    return ProtocolEvent(
        kind="commit.epoch",
        received_at=datetime.now(timezone.utc).isoformat(),
        source="test",
        payload={
            "event_kind": "commit.epoch",
            "epoch_index": index,
            "epoch_id": epoch_id,
            "namespace_id": "test_ns",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "finalization_state": "committed",
            "summary": {
                "reward_total": reward,
                "stake_total": 1000.0,
                "task_count": 10,
                "agent_count": 2,
            },
            "checksums": {"epoch_events_cid": "QmA", "epoch_state_cid": "QmB"},
        }
    )


class TestFileLedgerBackend:
    def test_persistence_survives_restart(self, temp_storage_dir: str):
        """State should persist across backend re-initialization."""
        # 1. Init backend A
        backend1 = FileLedgerBackend(temp_storage_dir)
        
        # Store snapshot
        snap = StakeSnapshot(
            epoch_id="epoch_persistence",
            epoch_index=1,
            namespace_id="test_ns",
            stakes={"agent_a": 100.0},
            total_stake=100.0,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        backend1.put_stake_snapshot(snap)
        
        # Apply settlement
        event = make_commit_event("epoch_persistence", 1, reward=50.0)
        backend1.apply_epoch_settlement(event)
        
        assert backend1.get_balance("agent_a") == 50.0
        
        # 2. Init backend B (restart)
        backend2 = FileLedgerBackend(temp_storage_dir)
        
        # Check consistency
        rec = backend2.get_epoch_record("epoch_persistence")
        assert rec is not None
        assert rec["status"] == "settled"
        assert rec["distribution_status"] == "distributed"
        
        assert backend2.get_balance("agent_a") == 50.0
        
        snap_retrieved = backend2.get_stake_snapshot("epoch_persistence")
        # Direct comparison might fail due to float epsilon or strict equality, 
        # but StakeSnapshot is frozen dataclass so strict equality should work 
        # IF serialization didn't change types. JSON turns int keys to str, but agent_id is str.
        # But `epoch_index` is int. JSON preserves it.
        # `stakes` values are float.
        # created_at is str.
        # Should be fine.
        assert snap_retrieved == snap

    def test_idempotency_persisted(self, temp_storage_dir: str):
        """Re-applying same epoch after restart is no-op."""
        backend1 = FileLedgerBackend(temp_storage_dir)
        event = make_commit_event("epoch_idem", 2)
        backend1.apply_epoch_settlement(event)
        
        backend2 = FileLedgerBackend(temp_storage_dir)
        # Apply again
        backend2.apply_epoch_settlement(event)
        
        # Should still be 1 record
        # (Implementation detail: keys are IDs, so idempotency is natural)
        assert len(backend2.epoch_records) == 1

    def test_supersession_persistence(self, temp_storage_dir: str):
        """Supersession status updates should persist."""
        backend1 = FileLedgerBackend(temp_storage_dir)
        
        # V1
        backend1.apply_epoch_settlement(make_commit_event("epoch_sup_v1", 3))
        
        # V2 (supersedes V1)
        backend1.apply_epoch_settlement(make_commit_event("epoch_sup_v2", 3))
        
        # Restart
        backend2 = FileLedgerBackend(temp_storage_dir)
        rec1 = backend2.get_epoch_record("epoch_sup_v1")
        assert rec1["status"] == "superseded"
        assert rec1["superseded_by"] == "epoch_sup_v2"
        
        rec2 = backend2.get_epoch_record("epoch_sup_v2")
        assert rec2["status"] == "settled"

    def test_factory_helper(self, temp_storage_dir: str):
        """Factory should return correct types."""
        mem = get_ledger_backend("memory")
        assert not isinstance(mem, FileLedgerBackend)
        
        # For file, storage_dir is required
        with pytest.raises(ValueError):
            get_ledger_backend("file")
            
        file_be = get_ledger_backend("file", storage_dir=temp_storage_dir)
        assert isinstance(file_be, FileLedgerBackend)

    def test_corrupt_file_handling(self, temp_storage_dir: str):
        """Should handle corrupt JSON gracefully (ignore or empty)."""
        # Create corrupt file
        with open(os.path.join(temp_storage_dir, "balances.json"), "w") as f:
            f.write("{ invalid json")
            
        backend = FileLedgerBackend(temp_storage_dir)
        # Should start empty without crashing
        assert backend.balances == {}
        
        # Write valid data
        backend._set_balance("foo", 10.0)
        
        # Restart
        backend2 = FileLedgerBackend(temp_storage_dir)
        assert backend2.get_balance("foo") == 10.0
