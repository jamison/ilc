# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 833 Row-5 B-Impl — LeakageMetrics: obligation 6 (SIM-LEAKAGE-03).

Obligation 6 — Live instrumentation for SIM-LEAKAGE-03:
  Expose the minimum metrics required by the live evaluation lane so that
  SIM-LEAKAGE-03 can consume them against the M-009 testbed when the
  runtime-closure window opens.

Minimum metrics (per commissioning spec §3.6):
  - per-epoch group fill rate
  - observed jitter distribution
  - force-release count
  - anonymity-set size histogram per settled batch

Design notes:
  - LeakageMetricsCollector is stateful and epoch-scoped. Call
    record_group_settled() after every flush() or enforce_max_wait() delivery.
  - epoch_snapshot() returns the stats for the requested epoch without
    mutating state; call it after all activity in an epoch is done.
  - global_snapshot() aggregates across all epochs.

Token: row5_b_impl_obligation_6_sim_leakage_03_instrumentation
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ilc_core.privacy.lane import ReleaseGroup

LEAKAGE_METRICS_VERSION = "leakage_metrics_833.v0.1"
CDL_072_DEPENDENCY = "cdl_072_bound_b_formula_amendment_ratified_846.v0.1"

# The bounds SIM-LEAKAGE-03 must satisfy (informational — checked in Phase 834).
SIM_LEAKAGE_03_BOUND_A: float = 0.15   # max fill-failure rate
SIM_LEAKAGE_03_BOUND_B: float = 0.15   # retained for historical reference (Phase 845 structural finding)
SIM_LEAKAGE_03_BOUND_B_MAX_JITTER: int = 3  # CDL-072: max observed jitter ≤ release_jitter_epochs
SIM_LEAKAGE_03_BOUND_C: float = 0.05   # max degraded-anonymity fraction of settled transfers


@dataclass
class EpochMetrics:
    """Statistics for a single epoch.

    Token: row5_b_impl_epoch_metrics_shape
    """
    epoch: int
    groups_completed: int = 0
    groups_force_released: int = 0
    # jitter_distribution: {jitter_delta: count}
    jitter_distribution: dict[int, int] = field(default_factory=dict)
    # anonymity_set_histogram: {set_size: count_of_groups_with_that_size}
    anonymity_set_histogram: dict[int, int] = field(default_factory=dict)
    transfers_settled: int = 0
    transfers_degraded: int = 0

    @property
    def fill_rate(self) -> float:
        """Fraction of groups that sealed normally (not force-released)."""
        total = self.groups_completed + self.groups_force_released
        if total == 0:
            return 1.0   # vacuously full if no activity
        return self.groups_completed / total

    @property
    def degraded_fraction(self) -> float:
        """Fraction of settled transfers that carried degraded_anonymity."""
        if self.transfers_settled == 0:
            return 0.0
        return self.transfers_degraded / self.transfers_settled


@dataclass
class GlobalMetrics:
    """Aggregated statistics across all epochs.

    Token: row5_b_impl_global_metrics_shape
    """
    total_epochs_observed: int
    total_groups_completed: int
    total_groups_force_released: int
    total_transfers_settled: int
    total_transfers_degraded: int
    # Merged jitter distribution across all epochs
    jitter_distribution: dict[int, int]
    # Merged anonymity-set histogram across all epochs
    anonymity_set_histogram: dict[int, int]

    @property
    def global_fill_rate(self) -> float:
        total = self.total_groups_completed + self.total_groups_force_released
        if total == 0:
            return 1.0
        return self.total_groups_completed / total

    @property
    def global_degraded_fraction(self) -> float:
        if self.total_transfers_settled == 0:
            return 0.0
        return self.total_transfers_degraded / self.total_transfers_settled


class LeakageMetricsCollector:
    """Accumulates per-epoch and global metrics for SIM-LEAKAGE-03.

    Usage::

        collector = LeakageMetricsCollector()

        # After each flush() or enforce_max_wait() delivery:
        for group in ready_groups:
            sealed_epoch = group.sealed_epoch    # epoch the group was sealed
            collector.record_group_settled(
                sealed_epoch=sealed_epoch,
                group=group,
            )

        # After epoch completes:
        snap = collector.epoch_snapshot(epoch=current_epoch)
        global_snap = collector.global_snapshot()

    Token: row5_b_impl_leakage_metrics_collector
    """

    def __init__(self) -> None:
        # epoch → EpochMetrics (created on first access)
        self._epochs: dict[int, EpochMetrics] = {}

    def record_group_settled(
        self,
        sealed_epoch: int | ReleaseGroup | None = None,
        group: ReleaseGroup | None = None,
    ) -> None:
        """Record a settled group (normal or force-released).

        Parameters
        ----------
        sealed_epoch:
            Deprecated override retained for older evidence helpers that build
            ReleaseGroup manually. Runtime-created groups carry sealed_epoch;
            for those groups, this argument must be omitted or match the group.
        group:
            The ReleaseGroup returned by flush() or enforce_max_wait().
        """
        if isinstance(sealed_epoch, ReleaseGroup) and group is None:
            group = sealed_epoch
            sealed_epoch = None

        if group is None:
            raise ValueError(
                "privacy_lane_metrics_missing_group: "
                "record_group_settled requires a ReleaseGroup"
            )
        if sealed_epoch is not None and not isinstance(sealed_epoch, int):
            raise ValueError("privacy_lane_metrics_invalid_sealed_epoch")

        if group.sealed_epoch is None:
            if sealed_epoch is None:
                raise ValueError(
                    "privacy_lane_metrics_missing_sealed_epoch: "
                    "ReleaseGroup.sealed_epoch is required for runtime metrics"
                )
            effective_sealed_epoch = sealed_epoch
        else:
            effective_sealed_epoch = group.sealed_epoch

        if sealed_epoch is not None and sealed_epoch != effective_sealed_epoch:
            raise ValueError(
                f"privacy_lane_metrics_sealed_epoch_mismatch: "
                f"argument={sealed_epoch} group={group.sealed_epoch}; "
                f"metrics must use the epoch carried by ReleaseGroup"
            )

        em = self._get_or_create(effective_sealed_epoch)

        if group.degraded_anonymity:
            em.groups_force_released += 1
        else:
            em.groups_completed += 1

        # Jitter delta: for normal groups, release_epoch - sealed_epoch.
        # For force-released groups the jitter concept doesn't apply cleanly;
        # we skip them from the jitter distribution (degraded_anonymity guard).
        if not group.degraded_anonymity:
            jitter = group.release_epoch - effective_sealed_epoch
            if jitter < 0:
                raise ValueError(
                    f"privacy_lane_metrics_negative_jitter: "
                    f"release_epoch={group.release_epoch} < sealed_epoch={effective_sealed_epoch}"
                )
            em.jitter_distribution[jitter] = em.jitter_distribution.get(jitter, 0) + 1

        # Anonymity-set histogram: keyed by actual set size.
        sz = group.anonymity_set_size
        em.anonymity_set_histogram[sz] = em.anonymity_set_histogram.get(sz, 0) + 1

        # Transfer-level counts.
        em.transfers_settled += len(group.transfers)
        if group.degraded_anonymity:
            em.transfers_degraded += len(group.transfers)

    def epoch_snapshot(self, epoch: int) -> EpochMetrics:
        """Return a copy of the metrics for the given epoch (empty if unseen)."""
        if epoch not in self._epochs:
            return EpochMetrics(epoch=epoch)
        em = self._epochs[epoch]
        return EpochMetrics(
            epoch=em.epoch,
            groups_completed=em.groups_completed,
            groups_force_released=em.groups_force_released,
            jitter_distribution=dict(em.jitter_distribution),
            anonymity_set_histogram=dict(em.anonymity_set_histogram),
            transfers_settled=em.transfers_settled,
            transfers_degraded=em.transfers_degraded,
        )

    def global_snapshot(self) -> GlobalMetrics:
        """Return aggregated metrics across all epochs."""
        total_completed = 0
        total_forced = 0
        total_settled = 0
        total_degraded = 0
        merged_jitter: dict[int, int] = {}
        merged_histogram: dict[int, int] = {}

        for em in self._epochs.values():
            total_completed += em.groups_completed
            total_forced += em.groups_force_released
            total_settled += em.transfers_settled
            total_degraded += em.transfers_degraded
            for k, v in em.jitter_distribution.items():
                merged_jitter[k] = merged_jitter.get(k, 0) + v
            for k, v in em.anonymity_set_histogram.items():
                merged_histogram[k] = merged_histogram.get(k, 0) + v

        return GlobalMetrics(
            total_epochs_observed=len(self._epochs),
            total_groups_completed=total_completed,
            total_groups_force_released=total_forced,
            total_transfers_settled=total_settled,
            total_transfers_degraded=total_degraded,
            jitter_distribution=merged_jitter,
            anonymity_set_histogram=merged_histogram,
        )

    def check_bounds(self, global_metrics: GlobalMetrics | None = None) -> dict[str, bool]:
        """Check whether current metrics satisfy the three SIM-LEAKAGE-03 bounds.

        Returns a dict with keys 'A', 'B', 'C' mapping to True (bound satisfied)
        or False (bound violated).

        Bound A: global_fill_rate >= (1 - SIM_LEAKAGE_03_BOUND_A)
                 i.e. force-release fraction <= 0.15
        Bound B (CDL-072): max observed jitter <= release_jitter_epochs (=3).
                 True vacuously when no normal groups have settled.
        Bound C: global_degraded_fraction <= SIM_LEAKAGE_03_BOUND_C

        Token: row5_b_impl_bound_check
        """
        gm = global_metrics if global_metrics is not None else self.global_snapshot()

        # Bound A: fill-failure rate <= 15%
        fill_failure_rate = 1.0 - gm.global_fill_rate
        bound_a_ok = fill_failure_rate <= SIM_LEAKAGE_03_BOUND_A

        # Bound B: jitter spread check
        bound_b_ok = self._check_jitter_spread(gm)

        # Bound C: degraded-anonymity fraction <= 5%
        bound_c_ok = gm.global_degraded_fraction <= SIM_LEAKAGE_03_BOUND_C

        return {"A": bound_a_ok, "B": bound_b_ok, "C": bound_c_ok}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_or_create(self, epoch: int) -> EpochMetrics:
        if epoch not in self._epochs:
            self._epochs[epoch] = EpochMetrics(epoch=epoch)
        return self._epochs[epoch]

    def _check_jitter_spread(self, gm: GlobalMetrics) -> bool:
        """Bound B (revised CDL-072): max observed jitter ≤ release_jitter_epochs.

        Tests that no group settled later than the locked jitter window permits.
        Replaces the structurally-incompatible std/max relative formula (Phase 845
        honest non-closure finding `sim_leakage_03_bound_b_fail_structural`).

        A correct `secrets.randbelow(J+1)` implementation always passes; a PRNG
        overflow or off-by-one epoch error would produce jitter > J and fail.

        Token: cdl_072_bound_b_max_jitter_check
        """
        jd = gm.jitter_distribution
        if not jd:
            return True
        max_observed_jitter = max(jd.keys())
        return max_observed_jitter <= SIM_LEAKAGE_03_BOUND_B_MAX_JITTER
