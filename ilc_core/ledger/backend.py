"""
ILC Ledger Backend: In-memory settlement implementation.

This module provides the minimal ledger backend for commit.epoch settlement.
Phase 70B: In-memory only, no persistence, snapshot-based distribution + stub fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Literal

from ilc_core.protocol.event_log import ProtocolEvent, validate_commit_epoch_payload
from ilc_core.ledger.stake_snapshot import StakeSnapshot


class LedgerBackend(ABC):
    """Abstract interface for ledger backends."""

    @abstractmethod
    def apply_epoch_settlement(self, epoch_event: ProtocolEvent) -> None:
        """
        Apply settlement for a commit.epoch event.
        
        Args:
            epoch_event: A ProtocolEvent with kind="commit.epoch"
        """
        pass

    @abstractmethod
    def get_balance(self, agent_id: str) -> float:
        """
        Get the current balance for an agent.
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            Current balance (0.0 if agent has no balance)
        """
        pass

    @abstractmethod
    def get_epoch_record(self, epoch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the settlement record for an epoch.
        
        Args:
            epoch_id: The unique epoch identifier
            
        Returns:
            Epoch record dict or None if not found
        """
        pass

    @abstractmethod
    def put_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """
        Store a stake snapshot for an epoch.
        
        Args:
            snapshot: The stake snapshot to store
        """
        pass

    @abstractmethod
    def get_stake_snapshot(self, epoch_id: str) -> Optional[StakeSnapshot]:
        """
        Retrieve a stake snapshot for an epoch.
        
        Args:
            epoch_id: The unique epoch identifier
            
        Returns:
            The stake snapshot or None if not found
        """
        pass


class InMemoryLedgerBackend(LedgerBackend):
    """
    In-memory ledger backend for development and testing.
    
    State is not persisted between process restarts.
    """

    def __init__(self):
        self.balances: Dict[str, float] = {}
        self.epoch_records: Dict[str, Dict[str, Any]] = {}
        self.stake_snapshots: Dict[str, StakeSnapshot] = {}

    def apply_epoch_settlement(self, epoch_event: ProtocolEvent) -> None:
        """
        Apply settlement for a commit.epoch event.
        
        Refactored in Phase 74 for clarity and reduced nesting.
        """
        if epoch_event.kind != "commit.epoch":
            raise ValueError(f"Expected commit.epoch event, got {epoch_event.kind}")

        payload = epoch_event.payload
        validate_commit_epoch_payload(payload)

        epoch_id = payload["epoch_id"]
        
        # Idempotency check
        if self._check_idempotency(epoch_id):
            return

        # Handle supersession of prior epochs
        self._process_supersession(payload["epoch_index"], epoch_id)

        # Create pending record
        record = self._create_pending_record(payload)

        # Finalize based on state
        finalization_state = payload["finalization_state"]
        if finalization_state == "committed":
            self._finalize_committed(record, payload)
        elif finalization_state == "rolled_back":
            self._finalize_rolled_back(record)
        elif finalization_state == "superseded":
            self._finalize_superseded(record)

        self._store_epoch_record(record)

    def _check_idempotency(self, epoch_id: str) -> bool:
        """Return True if epoch already processed and shouldn't be re-applied."""
        existing = self.epoch_records.get(epoch_id)
        if existing is not None:
            # If already processed and not superseded, no-op
            if existing.get("status") != "superseded":
                return True
        return False

    def _process_supersession(self, epoch_index: int, new_epoch_id: str) -> None:
        """Identify and supersede any prior epochs at this index."""
        # Note: Iterating copy of items to allow safe modification
        for prior_id, prior_record in list(self.epoch_records.items()):
            if (prior_record.get("epoch_index") == epoch_index and 
                prior_id != new_epoch_id and
                prior_record.get("status") != "superseded"):
                
                # Reverse effects if it was settled/distributed
                if (prior_record.get("status") == "settled" and 
                    prior_record.get("distribution_status") == "distributed"):
                    
                    prior_snapshot = self.get_stake_snapshot(prior_id)
                    if prior_snapshot:
                        prior_rewards = prior_record.get("summary", {}).get("reward_total", 0.0)
                        self._apply_rewards(prior_snapshot, -prior_rewards)

                # Mark prior as superseded
                prior_record["status"] = "superseded"
                prior_record["superseded_by"] = new_epoch_id
                self._store_epoch_record(prior_record)

    def _create_pending_record(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create the initial epoch record structure."""
        return {
            "epoch_id": payload["epoch_id"],
            "epoch_index": payload["epoch_index"],
            "namespace_id": payload["namespace_id"],
            "created_at": payload["created_at"],
            "finalization_state": payload["finalization_state"],
            "summary": payload["summary"],
            "checksums": payload["checksums"],
            "status": "pending",
        }

    def _finalize_committed(self, record: Dict[str, Any], payload: Dict[str, Any]) -> None:
        """Apply committed state logic: rewards distribution."""
        record["status"] = "settled"
        epoch_id = payload["epoch_id"]
        
        snapshot = self.get_stake_snapshot(epoch_id)
        if snapshot:
            # Consistency Checks
            if snapshot.epoch_id != epoch_id:
                raise ValueError(f"Snapshot epoch_id {snapshot.epoch_id} != payload {epoch_id}")
            if snapshot.epoch_index != payload["epoch_index"]:
                raise ValueError(f"Snapshot epoch_index {snapshot.epoch_index} != payload {payload['epoch_index']}")
            if snapshot.namespace_id != payload["namespace_id"]:
                raise ValueError(f"Snapshot namespace_id {snapshot.namespace_id} != payload {payload['namespace_id']}")

            rewards = payload["summary"]["reward_total"]
            self._apply_rewards(snapshot, rewards)
            record["distribution_status"] = "distributed"
        else:
            record["distribution_status"] = "stub_no_snapshot"

    def _finalize_rolled_back(self, record: Dict[str, Any]) -> None:
        """Apply rolled_back state logic."""
        record["status"] = "rolled_back"
        # No balance changes

    def _finalize_superseded(self, record: Dict[str, Any]) -> None:
        """Apply superseded state logic (for event itself)."""
        record["status"] = "superseded"
        # No balance changes

    def _apply_rewards(self, snapshot: StakeSnapshot, total_rewards: float) -> None:
        """Helper to apply (or reverse) rewards based on logic."""
        if snapshot.total_stake <= 0:
            return
            
        for agent_id, stake in snapshot.stakes.items():
            share = (stake / snapshot.total_stake) * total_rewards
            current = self.balances.get(agent_id, 0.0)
            self._set_balance(agent_id, current + share)

    def _set_balance(self, agent_id: str, new_balance: float) -> None:
        """Set an agent's balance."""
        self.balances[agent_id] = new_balance

    def _store_epoch_record(self, record: Dict[str, Any]) -> None:
        """Store an epoch record."""
        self.epoch_records[record["epoch_id"]] = record

    def get_balance(self, agent_id: str) -> float:
        """Get agent balance. Returns 0.0 if not found."""
        return self.balances.get(agent_id, 0.0)

    def get_epoch_record(self, epoch_id: str) -> Optional[Dict[str, Any]]:
        """Get epoch settlement record."""
        return self.epoch_records.get(epoch_id)

    def put_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Store a stake snapshot."""
        self.stake_snapshots[snapshot.epoch_id] = snapshot
        # Hook for persistence subclass can override this or use _store_snapshot if added
        self._store_stake_snapshot(snapshot)

    def _store_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Hook for persisting snapshot."""
        pass  # InMemory stores in put_stake_snapshot; persistence backends can override

    def get_stake_snapshot(self, epoch_id: str) -> Optional[StakeSnapshot]:
        """Retrieve a stake snapshot."""
        return self.stake_snapshots.get(epoch_id)


def settle_commit_epoch(ledger: LedgerBackend, event: ProtocolEvent) -> None:
    """
    Settlement entrypoint for commit.epoch events.
    
    Args:
        ledger: The ledger backend to use
        event: A ProtocolEvent with kind="commit.epoch"
    """
    ledger.apply_epoch_settlement(event)
