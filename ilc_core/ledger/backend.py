"""
ILC Ledger Backend: In-memory settlement implementation.

This module provides the minimal ledger backend for commit.epoch settlement.
Phase 70A: In-memory only, no persistence, stub distribution rule.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Literal

from ilc_core.protocol.event_log import ProtocolEvent, validate_commit_epoch_payload


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


class InMemoryLedgerBackend(LedgerBackend):
    """
    In-memory ledger backend for development and testing.
    
    State is not persisted between process restarts.
    """

    def __init__(self):
        self.balances: Dict[str, float] = {}
        self.epoch_records: Dict[str, Dict[str, Any]] = {}

    def apply_epoch_settlement(self, epoch_event: ProtocolEvent) -> None:
        """
        Apply settlement for a commit.epoch event.
        
        Settlement rules:
        - committed: Record epoch and apply rewards (stub: no balance changes yet)
        - rolled_back: Mark epoch as rolled back, no balance changes
        - superseded: Mark prior epoch as superseded, apply new epoch
        - Idempotent: Re-applying same epoch_id is a no-op
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
            # TODO: Await per-agent stake snapshot source.
            # For now, reward_total is recorded but balances are unchanged.
            # Real distribution requires stake snapshot per agent.
            record["distribution_status"] = "stub_no_balance_change"

        elif finalization_state == "rolled_back":
            record["status"] = "rolled_back"
            # No balance changes for rolled back epochs

        elif finalization_state == "superseded":
            record["status"] = "superseded"
            # This event itself is superseded; no balance changes

        self.epoch_records[epoch_id] = record

    def get_balance(self, agent_id: str) -> float:
        """Get agent balance. Returns 0.0 if not found."""
        return self.balances.get(agent_id, 0.0)

    def get_epoch_record(self, epoch_id: str) -> Optional[Dict[str, Any]]:
        """Get epoch settlement record."""
        return self.epoch_records.get(epoch_id)


def settle_commit_epoch(ledger: LedgerBackend, event: ProtocolEvent) -> None:
    """
    Settlement entrypoint for commit.epoch events.
    
    Args:
        ledger: The ledger backend to use
        event: A ProtocolEvent with kind="commit.epoch"
    """
    ledger.apply_epoch_settlement(event)
