"""
ILC Ledger Backend: in-memory settlement implementation.

This module provides the minimal ledger backend for commit.epoch settlement.
Phase 70B: In-memory only, no persistence, snapshot-based distribution + stub fallback.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Literal, Optional, TypeAlias, TypedDict, cast

try:
    from typing import NotRequired
except ImportError:  # pragma: no cover - Python 3.10 compatibility path.
    from typing_extensions import NotRequired

from ilc_core.ledger.exact_numeric import (
    ZERO,
    to_decimal,
)
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEvent, validate_any_commit_epoch_payload


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class EpochSummary(TypedDict):
    task_count: int
    agent_count: int
    reward_total: str
    stake_total: str


class EpochChecksums(TypedDict):
    epoch_events_cid: str
    epoch_state_cid: str


FinalizationState = Literal["committed", "rolled_back", "superseded"]


class CommitEpochPayload(TypedDict):
    event_kind: Literal["commit.epoch"]
    epoch_index: int
    epoch_id: str
    namespace_id: str
    finalization_state: FinalizationState
    summary: EpochSummary
    checksums: EpochChecksums
    created_at: NotRequired[str]
    schema_version: NotRequired[str]


class EpochRecord(TypedDict, total=False):
    epoch_id: str
    epoch_index: int
    namespace_id: str
    created_at: str
    finalization_state: FinalizationState
    summary: EpochSummary
    checksums: EpochChecksums
    status: str
    distribution_status: str
    superseded_by: str


class LedgerBackend(ABC):
    """Abstract interface for ledger backends."""

    @abstractmethod
    def apply_epoch_settlement(self, epoch_event: ProtocolEvent) -> None:
        """
        Apply settlement for a commit.epoch event.

        Args:
            epoch_event: A ProtocolEvent with kind="commit.epoch"
        """

    @abstractmethod
    def get_balance(self, agent_id: str) -> float:
        """
        Get the current balance for an agent.

        Args:
            agent_id: The agent identifier

        Returns:
            Current balance (0.0 if agent has no balance)
        """

    @abstractmethod
    def get_epoch_record(self, epoch_id: str) -> Optional[EpochRecord]:
        """
        Get the settlement record for an epoch.

        Args:
            epoch_id: The unique epoch identifier

        Returns:
            Epoch record dict or None if not found
        """

    @abstractmethod
    def put_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """
        Store a stake snapshot for an epoch.

        Args:
            snapshot: The stake snapshot to store
        """

    @abstractmethod
    def get_stake_snapshot(self, epoch_id: str) -> Optional[StakeSnapshot]:
        """
        Retrieve a stake snapshot for an epoch.

        Args:
            epoch_id: The unique epoch identifier

        Returns:
            The stake snapshot or None if not found
        """


class InMemoryLedgerBackend(LedgerBackend):
    """
    In-memory ledger backend for development and testing.

    State is not persisted between process restarts.
    """

    def __init__(self) -> None:
        self.balances: dict[str, Decimal] = {}
        self.epoch_records: dict[str, EpochRecord] = {}
        self.stake_snapshots: dict[str, StakeSnapshot] = {}

    def apply_epoch_settlement(self, epoch_event: ProtocolEvent) -> None:
        """
        Apply settlement for a commit.epoch event.

        Refactored in Phase 74 for clarity and reduced nesting.
        """
        if epoch_event.kind != "commit.epoch":
            raise ValueError(f"Expected commit.epoch event, got {epoch_event.kind}")

        payload = cast(CommitEpochPayload, epoch_event.payload)
        validate_any_commit_epoch_payload(payload)

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
        """Return True if epoch already processed and should not be re-applied."""
        existing = self.epoch_records.get(epoch_id)
        if existing is not None:
            # If already processed and not superseded, no-op
            if existing.get("status") != "superseded":
                return True
        return False

    def _extract_reward_total(self, record: EpochRecord) -> Decimal:
        summary = record.get("summary")
        if isinstance(summary, dict):
            reward_value = summary.get("reward_total", "0")
            try:
                return to_decimal(reward_value, token="epoch_reward_total_invalid")
            except ValueError:
                return ZERO
        return ZERO

    def _process_supersession(self, epoch_index: int, new_epoch_id: str) -> None:
        """Identify and supersede any prior epochs at this index."""
        # Note: Iterating copy of items to allow safe modification
        for prior_id, prior_record in list(self.epoch_records.items()):
            if (
                prior_record.get("epoch_index") == epoch_index
                and prior_id != new_epoch_id
                and prior_record.get("status") != "superseded"
            ):
                # Reverse effects if it was settled/distributed
                if (
                    prior_record.get("status") == "settled"
                    and prior_record.get("distribution_status") == "distributed"
                ):
                    prior_snapshot = self.get_stake_snapshot(prior_id)
                    if prior_snapshot:
                        prior_rewards = self._extract_reward_total(prior_record)
                        self._apply_rewards(prior_snapshot, -prior_rewards)

                # Mark prior as superseded
                prior_record["status"] = "superseded"
                prior_record["superseded_by"] = new_epoch_id
                self._store_epoch_record(prior_record)

    def _create_pending_record(self, payload: CommitEpochPayload) -> EpochRecord:
        """Create the initial epoch record structure."""
        return {
            "epoch_id": payload["epoch_id"],
            "epoch_index": payload["epoch_index"],
            "namespace_id": payload["namespace_id"],
            "created_at": payload.get("created_at", ""),
            "finalization_state": payload["finalization_state"],
            "summary": payload["summary"],
            "checksums": payload["checksums"],
            "status": "pending",
        }

    def _finalize_committed(
        self, record: EpochRecord, payload: CommitEpochPayload
    ) -> None:
        """Apply committed state logic: rewards distribution."""
        record["status"] = "settled"
        epoch_id = payload["epoch_id"]

        snapshot = self.get_stake_snapshot(epoch_id)
        if snapshot:
            # Consistency checks
            if snapshot.epoch_id != epoch_id:
                raise ValueError(
                    f"Snapshot epoch_id {snapshot.epoch_id} != payload {epoch_id}"
                )
            if snapshot.epoch_index != payload["epoch_index"]:
                raise ValueError(
                    f"Snapshot epoch_index {snapshot.epoch_index} != payload {payload['epoch_index']}"
                )
            if snapshot.namespace_id != payload["namespace_id"]:
                raise ValueError(
                    f"Snapshot namespace_id {snapshot.namespace_id} != payload {payload['namespace_id']}"
                )

            rewards = to_decimal(
                payload["summary"]["reward_total"],
                token="payload_reward_total_invalid",
            )
            self._apply_rewards(snapshot, rewards)
            record["distribution_status"] = "distributed"
        else:
            record["distribution_status"] = "stub_no_snapshot"

    def _finalize_rolled_back(self, record: EpochRecord) -> None:
        """Apply rolled_back state logic."""
        record["status"] = "rolled_back"
        # No balance changes

    def _finalize_superseded(self, record: EpochRecord) -> None:
        """Apply superseded state logic (for event itself)."""
        record["status"] = "superseded"
        # No balance changes

    def _apply_rewards(self, snapshot: StakeSnapshot, total_rewards: Decimal) -> None:
        """Apply (or reverse) rewards based on stake share."""
        if snapshot.total_stake <= ZERO:
            return

        for agent_id, stake in snapshot.stakes.items():
            share = (stake / snapshot.total_stake) * total_rewards
            current = self.balances.get(agent_id, ZERO)
            self._set_balance(agent_id, current + share)

    def _set_balance(self, agent_id: str, new_balance: Decimal | int | float | str) -> None:
        """Set an agent's balance."""
        self.balances[agent_id] = to_decimal(
            new_balance,
            token="ledger_balance_invalid",
        )

    def _store_epoch_record(self, record: EpochRecord) -> None:
        """Store an epoch record."""
        epoch_id = cast(str, record["epoch_id"])
        self.epoch_records[epoch_id] = record

    def get_balance(self, agent_id: str) -> float:
        """Get agent balance. Returns 0.0 if not found."""
        return float(self.balances.get(agent_id, ZERO))

    def get_epoch_record(self, epoch_id: str) -> Optional[EpochRecord]:
        """Get epoch settlement record."""
        return self.epoch_records.get(epoch_id)

    def put_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Store a stake snapshot."""
        self.stake_snapshots[snapshot.epoch_id] = snapshot
        # Hook for persistence subclass can override this.
        self._store_stake_snapshot(snapshot)

    def _store_stake_snapshot(self, snapshot: StakeSnapshot) -> None:
        """Hook for persisting snapshot."""
        # InMemory stores in put_stake_snapshot; persistence backends can override.
        pass

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
