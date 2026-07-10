# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 831 Row-5 B-Impl — PrivacyLane: obligations 1, 2, 3.

Obligation 1 — Rolling group construction in submission path:
  - Contribution transfers always enter the privacy lane accumulator.
  - Payment transfers default to the same privacy lane.
  - Payment{express: Some(ExpressConsent{agent_acknowledged_timing_disclosure: true})}
    bypasses directly to the express fast path and is returned immediately
    to the caller without entering the accumulator.

Obligation 2 — Deferred release queue with jitter scheduling:
  - When a k-group completes, compute release_epoch = current_epoch + rng(0, J)
    with J = release_jitter_epochs (locked at 3).
  - Queue shape: list of ReleaseGroup(release_epoch, transfers, agent_ids, sealed_epoch).
  - flush(current_epoch) returns all groups whose release_epoch <= current_epoch.

Obligation 3 — bounded_hold carry-over with max-wait enforcement:
  - Transfers that do not fill a complete k-group within max_wait epochs
    must still settle.
  - Force-release the partial group after max_wait — do not fall back to
    single-contributor release.
  - Preserve the largest partial anonymity set available at release time.
  - Released groups carry a degraded_anonymity=True flag so downstream
    can notify contributors (obligation 5, Phase 832).

Token: row5_b_impl_obligation_1_rolling_group_construction
Token: row5_b_impl_obligation_2_deferred_release_queue
Token: row5_b_impl_obligation_3_bounded_hold_carry_over
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ilc_core.privacy.monitor import FillMonitor

PRIVACY_LANE_RUNTIME_VERSION = "privacy_lane_831.v0.1"

# Locked mechanism constants (B-5 mechanism lock).
K_PRIMARY: int = 30
K_FALLBACK: int = 20
RELEASE_JITTER_EPOCHS: int = 3


@dataclass(frozen=True)
class PrivacyLaneConfig:
    """Locked configuration for the Row-5 privacy lane.

    Defaults match the primary lane (k=30). Instantiate with k=K_FALLBACK
    for the fallback lane.

    Token: row5_b_impl_privacy_lane_config
    """
    k: int = K_PRIMARY
    release_jitter_epochs: int = RELEASE_JITTER_EPOCHS
    max_wait_epochs: int = 4  # force-release threshold; SIM-LEAKAGE-03 will validate

    def __post_init__(self) -> None:
        if self.k not in (K_PRIMARY, K_FALLBACK):
            raise ValueError(
                f"privacy_lane_config_k_must_be_primary_or_fallback: "
                f"got {self.k}, valid values are {K_PRIMARY} or {K_FALLBACK}"
            )
        if self.release_jitter_epochs != RELEASE_JITTER_EPOCHS:
            raise ValueError(
                f"privacy_lane_config_jitter_locked_at_{RELEASE_JITTER_EPOCHS}: "
                f"got {self.release_jitter_epochs}"
            )
        if self.max_wait_epochs < 1:
            raise ValueError("privacy_lane_config_max_wait_must_be_positive")


@dataclass
class ReleaseGroup:
    """A completed or force-released group ready for settlement.

    Attributes:
        release_epoch:      The epoch at which this group may be flushed.
        transfers:          The ECUTransfer-like dicts in this group.
        agent_ids:          Ordered list of contributing agent identifiers.
        anonymity_set_size: Actual distinct-contributor set size at release time.
        degraded_anonymity: True when released before reaching k (bounded_hold
                            force-release). Downstream must notify contributors.
        sealed_epoch:       Epoch when this group was sealed. Metrics derive
                            jitter from this value rather than trusting callers.

    Token: row5_b_impl_release_group_shape
    """
    release_epoch: int
    transfers: list[Any]
    agent_ids: list[Any]
    anonymity_set_size: int
    degraded_anonymity: bool = False
    sealed_epoch: int | None = None


class PrivacyLane:
    """Row-5 privacy lane accumulator — Phase 831 obligations 1, 2, 3.

    Thread safety: this class is NOT thread-safe. Callers must serialise
    access (the Rust submission path will hold the in_flight lock while
    calling the Python simulation layer; the live Rust port in Phase 832
    will use a Mutex).

    Usage::

        lane = PrivacyLane(config=PrivacyLaneConfig(), current_epoch=1)

        # Submission path (obligation 1)
        express = lane.submit(transfer, current_epoch=1)
        if express is not None:
            # settle immediately — express fast path
            ...

        # Epoch tick — flush ready groups (obligation 2)
        ready = lane.flush(current_epoch=2)
        for group in ready:
            settle(group.transfers)

        # Epoch tick — enforce max_wait (obligation 3)
        forced = lane.enforce_max_wait(current_epoch=5)
        for group in forced:
            if not group.degraded_anonymity:
                raise RuntimeError("privacy_lane_degraded_anonymity_invariant_violation")
            settle(group.transfers)

    Token: row5_b_impl_privacy_lane_api
    """

    def __init__(
        self,
        config: PrivacyLaneConfig,
        current_epoch: int = 0,
        monitor: FillMonitor | None = None,
    ) -> None:
        self._config = config
        self._monitor = monitor
        self._accumulator: list[Any] = []          # pending transfers not yet grouped
        self._accumulator_agent_ids: list[Any] = []
        self._accumulator_entry_epoch: int = current_epoch  # epoch when first transfer entered
        self._release_queue: list[ReleaseGroup] = []
        # Per-epoch stats for obligation 6 (SIM-LEAKAGE-03 instrumentation, Phase 833)
        self._stats: dict[str, Any] = {
            "groups_completed": 0,
            "groups_force_released": 0,
            "express_bypasses": 0,
            "total_submitted": 0,
        }

    # ------------------------------------------------------------------
    # Obligation 1 — Rolling group construction
    # ------------------------------------------------------------------

    def submit(
        self,
        transfer: Any,
        current_epoch: int,
    ) -> Any | None:
        """Submit a transfer to the privacy lane.

        Returns:
            None if the transfer was accepted into the accumulator.
            The transfer itself if it bypasses to the express fast path
            (Payment with agent_acknowledged_timing_disclosure=True).

        Token: row5_b_impl_obligation_1_routing
        """
        self._stats["total_submitted"] += 1
        transfer_class = _get_transfer_class(transfer)

        if _is_express_bypass(transfer_class):
            # Payment{express: Some(ExpressConsent{acknowledged=True})} — bypass.
            # Express path is immediate; do not enter accumulator.
            self._stats["express_bypasses"] += 1
            return transfer

        # Contribution or Payment without express consent — privacy lane.
        agent_id = _get_agent_id(transfer)
        if agent_id is None:
            raise ValueError(
                "privacy_lane_submit_missing_agent_id: "
                "transfer must have a resolvable object_ref.agent field"
            )
        if len(self._accumulator) == 0:
            self._accumulator_entry_epoch = current_epoch

        self._accumulator.append(transfer)
        self._accumulator_agent_ids.append(agent_id)

        if _distinct_agent_count(self._accumulator_agent_ids) >= self._config.k:
            self._seal_group(current_epoch)

        return None

    # ------------------------------------------------------------------
    # Obligation 2 — Deferred release queue with jitter scheduling
    # ------------------------------------------------------------------

    def flush(self, current_epoch: int) -> list[ReleaseGroup]:
        """Return all groups whose release_epoch <= current_epoch.

        Token: row5_b_impl_obligation_2_flush
        """
        ready = [g for g in self._release_queue if g.release_epoch <= current_epoch]
        self._release_queue = [g for g in self._release_queue if g.release_epoch > current_epoch]
        return ready

    # ------------------------------------------------------------------
    # Obligation 3 — bounded_hold carry-over with max-wait enforcement
    # ------------------------------------------------------------------

    def enforce_max_wait(self, current_epoch: int) -> list[ReleaseGroup]:
        """Force-release the partial accumulator if max_wait has elapsed.

        Does NOT fall back to single-contributor release — the full partial
        anonymity set is released as a single group.  The released group
        carries degraded_anonymity=True so contributors can be notified
        (obligation 5, Phase 832).

        Token: row5_b_impl_obligation_3_bounded_hold
        """
        if not self._accumulator:
            return []
        epochs_waiting = current_epoch - self._accumulator_entry_epoch
        if epochs_waiting < self._config.max_wait_epochs:
            return []

        # Force-release: preserve largest partial anonymity set, mark degraded.
        group = ReleaseGroup(
            release_epoch=current_epoch,
            transfers=list(self._accumulator),
            agent_ids=list(self._accumulator_agent_ids),
            anonymity_set_size=_distinct_agent_count(self._accumulator_agent_ids),
            degraded_anonymity=True,
            sealed_epoch=current_epoch,
        )
        self._accumulator.clear()
        self._accumulator_agent_ids.clear()
        self._stats["groups_force_released"] += 1
        if self._monitor is not None:
            self._monitor.record_force_release(current_epoch)
        return [group]

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def accumulator_size(self) -> int:
        """Current number of transfers in the accumulator (not yet grouped)."""
        return len(self._accumulator)

    @property
    def release_queue_depth(self) -> int:
        """Number of groups waiting in the release queue."""
        return len(self._release_queue)

    @property
    def stats(self) -> dict[str, Any]:
        """Read-only snapshot of lane statistics.

        Used by obligation 6 (SIM-LEAKAGE-03 instrumentation, Phase 832).
        """
        return dict(self._stats)

    @property
    def config(self) -> PrivacyLaneConfig:
        return self._config

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _seal_group(self, current_epoch: int) -> None:
        """Seal a complete k-group into the release queue with jitter."""
        jitter = secrets.randbelow(self._config.release_jitter_epochs + 1)
        release_epoch = current_epoch + jitter
        group = ReleaseGroup(
            release_epoch=release_epoch,
            transfers=list(self._accumulator),
            agent_ids=list(self._accumulator_agent_ids),
            anonymity_set_size=_distinct_agent_count(self._accumulator_agent_ids),
            degraded_anonymity=False,
            sealed_epoch=current_epoch,
        )
        self._release_queue.append(group)
        self._accumulator.clear()
        self._accumulator_agent_ids.clear()
        self._stats["groups_completed"] += 1
        if self._monitor is not None:
            self._monitor.record_fill_success(current_epoch)


# ------------------------------------------------------------------
# Transfer introspection helpers (obligation 1 routing logic)
# ------------------------------------------------------------------

def _get_transfer_class(transfer: Any) -> Any:
    """Extract transfer_class from a transfer dict or object."""
    if isinstance(transfer, dict):
        return transfer.get("transfer_class")
    return getattr(transfer, "transfer_class", None)


def _distinct_agent_count(agent_ids: list[Any]) -> int:
    """Count distinct contributors without assuming agent IDs are hashable."""
    distinct: list[Any] = []
    for agent_id in agent_ids:
        if not any(agent_id == existing for existing in distinct):
            distinct.append(agent_id)
    return len(distinct)


def _get_agent_id(transfer: Any) -> Any:
    """Extract sender agent_id from a transfer dict or object.

    Supports two formats:
    - Typed/Rust format: ``transfer.object_ref.agent`` (nested path).
    - Simulation/flat format: ``transfer["agent_id"]`` or ``transfer.agent_id``
      used in test and Python-layer simulation contexts.

    Returns None only if neither path resolves an agent identifier.
    """
    if isinstance(transfer, dict):
        obj_ref = transfer.get("object_ref")
        if obj_ref is not None:
            if isinstance(obj_ref, dict):
                agent = obj_ref.get("agent")
            else:
                agent = getattr(obj_ref, "agent", None)
            if agent is not None:
                return agent
        # Fallback: flat dict format (simulation/test contexts).
        return transfer.get("agent_id")
    obj_ref = getattr(transfer, "object_ref", None)
    if obj_ref is not None:
        return getattr(obj_ref, "agent", None)
    # Fallback: flat attribute (simulation/test objects).
    return getattr(transfer, "agent_id", None)


def _is_express_bypass(transfer_class: Any) -> bool:
    """Return True if transfer_class requests the express fast path.

    Express bypass requires Payment with express consent where
    agent_acknowledged_timing_disclosure is True.

    Token: row5_b_impl_express_bypass_rule
    """
    if transfer_class is None:
        return False

    # Dict form (used in simulation / Python-side tests)
    if isinstance(transfer_class, dict):
        if transfer_class.get("type") != "Payment":
            return False
        express = transfer_class.get("express")
        if not isinstance(express, dict):
            return False
        return express.get("agent_acknowledged_timing_disclosure", False) is True

    # Object form (for future Rust FFI / typed Python classes)
    class_name = type(transfer_class).__name__
    if class_name != "Payment":
        return False
    express = getattr(transfer_class, "express", None)
    if express is None:
        return False
    return getattr(express, "agent_acknowledged_timing_disclosure", False) is True
