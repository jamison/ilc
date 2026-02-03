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
        
        Settlement rules:
        - committed: Record epoch and apply rewards using stake snapshot.
                     If snapshot missing, stub distribution (no balance change).
        - rolled_back: Mark epoch as rolled back, no balance changes.
        - superseded: Mark prior epoch as superseded, reverse its effects, apply new epoch.
        - Idempotent: Re-applying same epoch_id is a no-op.
        """
        if epoch_event.kind != "commit.epoch":
            raise ValueError(f"Expected commit.epoch event, got {epoch_event.kind}")

        payload = epoch_event.payload
        validate_commit_epoch_payload(payload)

        epoch_id = payload["epoch_id"]
        finalization_state = payload["finalization_state"]
        epoch_index = payload["epoch_index"]

        # Check for existing record
        existing = self.epoch_records.get(epoch_id)
        if existing is not None:
            # Idempotent: if already processed and not superseded, no-op
            if existing.get("status") != "superseded":
                return

        # Handle supersession: find any prior epoch with same epoch_index
        for prior_id, prior_record in self.epoch_records.items():
            if (prior_record.get("epoch_index") == epoch_index and 
                prior_id != epoch_id and
                prior_record.get("status") != "superseded"):
                
                # Reverse effects of prior epoch if it was settled with real distribution
                if prior_record.get("status") == "settled":
                     # Check if we need to reverse balances
                     # Note: we only reverse if distribution actually happened.
                     # But for simplicity in this phase, assuming single thread/process,
                     # we assume only one "settled" epoch at a time per index. 
                     # However, to be strict:
                     # If prior record has "distribution_status" == "distributed", we should reverse.
                     # This requires storing distributed amounts or recalculating them.
                     # Re-calculation needs the *prior* snapshot.
                     # For MVP in 70B, we assume simple overwrite logic: 
                     # if superseded, we don't necessarily "undo" immediately unless we track balances carefully.
                     # But wait, balance updates are cumulative. We MUST undo changes.
                     
                     # 1. Reverse prior rewards if they were applied
                     if prior_record.get("distribution_status") == "distributed":
                         prior_snapshot = self.get_stake_snapshot(prior_id)
                         if prior_snapshot:
                             prior_rewards = prior_record.get("summary", {}).get("reward_total", 0.0)
                             self._apply_rewards(prior_snapshot, -prior_rewards)

                # Mark prior as superseded
                prior_record["status"] = "superseded"
                prior_record["superseded_by"] = epoch_id

        # Create epoch record
        record: Dict[str, Any] = {
            "epoch_id": epoch_id,
            "epoch_index": epoch_index,
            "namespace_id": payload["namespace_id"],
            "created_at": payload["created_at"],
            "finalization_state": finalization_state,
            "summary": payload["summary"],
            "checksums": payload["checksums"],
            "status": "pending",
        }

        if finalization_state == "committed":
            record["status"] = "settled"
            
            # Real distribution using stake snapshot
            snapshot = self.get_stake_snapshot(epoch_id)
            if snapshot:
                # Consistency Checks
                if snapshot.epoch_id != epoch_id:
                    raise ValueError(f"Snapshot epoch_id {snapshot.epoch_id} != payload {epoch_id}")
                if snapshot.epoch_index != epoch_index:
                    raise ValueError(f"Snapshot epoch_index {snapshot.epoch_index} != payload {epoch_index}")
                if snapshot.namespace_id != payload["namespace_id"]:
                    raise ValueError(f"Snapshot namespace_id {snapshot.namespace_id} != payload {payload['namespace_id']}")

                rewards = payload["summary"]["reward_total"]
                self._apply_rewards(snapshot, rewards)
                record["distribution_status"] = "distributed"
            else:
                record["distribution_status"] = "stub_no_snapshot"

        elif finalization_state == "rolled_back":
            record["status"] = "rolled_back"
            # No balance changes for rolled back epochs

        elif finalization_state == "superseded":
            record["status"] = "superseded"
            # This event itself is superseded; no balance changes

        self.epoch_records[epoch_id] = record

    def _apply_rewards(self, snapshot: StakeSnapshot, total_rewards: float) -> None:
        """Helper to apply (or reverse) rewards based on logic."""
        if snapshot.total_stake <= 0:
            return
            
        for agent_id, stake in snapshot.stakes.items():
            share = (stake / snapshot.total_stake) * total_rewards
            current = self.balances.get(agent_id, 0.0)
            self.balances[agent_id] = current + share

    def get_balance(self, agent_id: str) -> float:
        """Get agent balance. Returns 0.0 if not found."""
        return self.balances.get(agent_id, 0.0)

    def get_epoch_record(self, epoch_id: str) -> Optional[Dict[str, Any]]:
        """Get epoch settlement record."""
        return self.epoch_records.get(epoch_id)

    def put_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Store a stake snapshot."""
        self.stake_snapshots[snapshot.epoch_id] = snapshot

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
