"""Phase 833 Row-5 B-Impl tests — obligation 6 (SIM-LEAKAGE-03 instrumentation).

Covers:
  Obligation 6 — Live metrics surface for SIM-LEAKAGE-03
    - per-epoch group fill rate
    - observed jitter distribution
    - force-release count
    - anonymity-set size histogram per settled batch
    - three-bound check (A, B, C)
"""
from __future__ import annotations

import pytest
from ilc_core.privacy import (
    LEAKAGE_METRICS_VERSION,
    SIM_LEAKAGE_03_BOUND_A,
    SIM_LEAKAGE_03_BOUND_B,
    SIM_LEAKAGE_03_BOUND_C,
    LeakageMetricsCollector,
    PrivacyLane,
    PrivacyLaneConfig,
    ReleaseGroup,
)
from ilc_core.privacy.lane import K_PRIMARY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _contribution(agent: str = "agent_a") -> dict:
    return {
        "object_ref": {"agent": agent},
        "amount_micro_ecu": 100,
        "transfer_class": {"type": "Contribution"},
    }


def _normal_group(
    release_epoch: int = 5,
    sealed_epoch: int | None = None,
    size: int = K_PRIMARY,
) -> ReleaseGroup:
    return ReleaseGroup(
        release_epoch=release_epoch,
        transfers=[_contribution(agent=f"a_{i}") for i in range(size)],
        agent_ids=[f"a_{i}" for i in range(size)],
        anonymity_set_size=size,
        degraded_anonymity=False,
        sealed_epoch=sealed_epoch,
    )


def _degraded_group(
    release_epoch: int = 10,
    sealed_epoch: int | None = None,
    size: int = 5,
) -> ReleaseGroup:
    return ReleaseGroup(
        release_epoch=release_epoch,
        transfers=[_contribution(agent=f"b_{i}") for i in range(size)],
        agent_ids=[f"b_{i}" for i in range(size)],
        anonymity_set_size=size,
        degraded_anonymity=True,
        sealed_epoch=sealed_epoch,
    )


# ---------------------------------------------------------------------------
# Version pinning
# ---------------------------------------------------------------------------

def test_leakage_metrics_version_pin() -> None:
    assert LEAKAGE_METRICS_VERSION == "leakage_metrics_833.v0.1"


def test_sim_leakage_03_bounds_locked() -> None:
    assert SIM_LEAKAGE_03_BOUND_A == 0.15
    assert SIM_LEAKAGE_03_BOUND_B == 0.15
    assert SIM_LEAKAGE_03_BOUND_C == 0.05


# ---------------------------------------------------------------------------
# Obligation 6 — LeakageMetricsCollector: per-epoch fill rate
# ---------------------------------------------------------------------------

class TestObligation6FillRate:

    def test_empty_collector_epoch_snapshot_is_zero(self) -> None:
        c = LeakageMetricsCollector()
        snap = c.epoch_snapshot(epoch=0)
        assert snap.groups_completed == 0
        assert snap.groups_force_released == 0
        assert snap.fill_rate == 1.0  # vacuously full

    def test_normal_group_increments_completed(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=2))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.groups_completed == 1
        assert snap.groups_force_released == 0
        assert snap.fill_rate == 1.0

    def test_force_released_group_increments_forced(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=5, group=_degraded_group(release_epoch=5))
        snap = c.epoch_snapshot(epoch=5)
        assert snap.groups_force_released == 1
        assert snap.groups_completed == 0
        assert snap.fill_rate == 0.0

    def test_fill_rate_mixed_epoch(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=1, group=_normal_group(release_epoch=3))
        c.record_group_settled(sealed_epoch=1, group=_normal_group(release_epoch=4))
        c.record_group_settled(sealed_epoch=1, group=_degraded_group(release_epoch=1))
        snap = c.epoch_snapshot(epoch=1)
        # 2 completed, 1 forced → fill_rate = 2/3
        assert snap.fill_rate == pytest.approx(2 / 3)

    def test_different_epochs_bucketed_separately(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=1))
        c.record_group_settled(sealed_epoch=5, group=_degraded_group(release_epoch=5))
        assert c.epoch_snapshot(epoch=0).groups_completed == 1
        assert c.epoch_snapshot(epoch=5).groups_force_released == 1
        assert c.epoch_snapshot(epoch=0).groups_force_released == 0


# ---------------------------------------------------------------------------
# Obligation 6 — jitter distribution
# ---------------------------------------------------------------------------

class TestObligation6JitterDistribution:

    def test_normal_group_records_jitter_delta(self) -> None:
        c = LeakageMetricsCollector()
        # sealed_epoch=0, release_epoch=2 → jitter=2
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=2))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.jitter_distribution == {2: 1}

    def test_multiple_groups_same_jitter_accumulate(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=1))
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=1))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.jitter_distribution == {1: 2}

    def test_multiple_jitter_values_tracked(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=0))
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=1))
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=3))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.jitter_distribution == {0: 1, 1: 1, 3: 1}

    def test_force_released_group_not_in_jitter_distribution(self) -> None:
        """Degraded groups are excluded from jitter tracking."""
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=5, group=_degraded_group(release_epoch=5))
        snap = c.epoch_snapshot(epoch=5)
        assert snap.jitter_distribution == {}

    def test_runtime_group_sealed_epoch_is_authoritative(self) -> None:
        c = LeakageMetricsCollector()
        group = _normal_group(sealed_epoch=4, release_epoch=7)
        c.record_group_settled(group=group)
        assert c.epoch_snapshot(epoch=4).jitter_distribution == {3: 1}

    def test_legacy_positional_arguments_still_work(self) -> None:
        c = LeakageMetricsCollector()
        group = _normal_group(release_epoch=2)
        c.record_group_settled(0, group)
        assert c.epoch_snapshot(epoch=0).jitter_distribution == {2: 1}

    def test_single_group_positional_argument_uses_group_epoch(self) -> None:
        c = LeakageMetricsCollector()
        group = _normal_group(sealed_epoch=4, release_epoch=7)
        c.record_group_settled(group)
        assert c.epoch_snapshot(epoch=4).jitter_distribution == {3: 1}

    def test_mismatched_sealed_epoch_argument_rejected(self) -> None:
        c = LeakageMetricsCollector()
        group = _normal_group(sealed_epoch=4, release_epoch=7)
        with pytest.raises(ValueError, match="sealed_epoch_mismatch"):
            c.record_group_settled(sealed_epoch=7, group=group)

    def test_missing_sealed_epoch_rejected_without_legacy_override(self) -> None:
        c = LeakageMetricsCollector()
        group = ReleaseGroup(
            release_epoch=3,
            transfers=[_contribution(agent="a")],
            agent_ids=["a"],
            anonymity_set_size=1,
            degraded_anonymity=False,
        )
        with pytest.raises(ValueError, match="missing_sealed_epoch"):
            c.record_group_settled(group=group)


# ---------------------------------------------------------------------------
# Obligation 6 — anonymity-set size histogram
# ---------------------------------------------------------------------------

class TestObligation6AnonymitySetHistogram:

    def test_normal_group_k30_in_histogram(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.anonymity_set_histogram == {30: 1}

    def test_degraded_group_size_in_histogram(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_degraded_group(size=7))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.anonymity_set_histogram == {7: 1}

    def test_mixed_sizes_accumulated(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=0, group=_degraded_group(size=5))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.anonymity_set_histogram == {30: 2, 5: 1}


# ---------------------------------------------------------------------------
# Obligation 6 — transfer-level counts
# ---------------------------------------------------------------------------

class TestObligation6TransferCounts:

    def test_normal_group_transfers_counted(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.transfers_settled == 30
        assert snap.transfers_degraded == 0

    def test_degraded_group_transfers_counted_as_degraded(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_degraded_group(size=7))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.transfers_settled == 7
        assert snap.transfers_degraded == 7
        assert snap.degraded_fraction == 1.0

    def test_mixed_degraded_fraction(self) -> None:
        c = LeakageMetricsCollector()
        # 30 normal + 5 degraded = 35 total, 5 degraded → 5/35 ≈ 0.143
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=0, group=_degraded_group(size=5))
        snap = c.epoch_snapshot(epoch=0)
        assert snap.degraded_fraction == pytest.approx(5 / 35)


# ---------------------------------------------------------------------------
# Obligation 6 — global snapshot
# ---------------------------------------------------------------------------

class TestObligation6GlobalSnapshot:

    def test_global_aggregates_across_epochs(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=1, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=2, group=_degraded_group(size=5))
        gm = c.global_snapshot()
        assert gm.total_groups_completed == 2
        assert gm.total_groups_force_released == 1
        assert gm.total_transfers_settled == 65
        assert gm.total_transfers_degraded == 5
        assert gm.total_epochs_observed == 3

    def test_global_fill_rate_no_groups(self) -> None:
        c = LeakageMetricsCollector()
        gm = c.global_snapshot()
        assert gm.global_fill_rate == 1.0  # vacuously full

    def test_global_jitter_merged(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(release_epoch=1))  # jitter=1
        c.record_group_settled(sealed_epoch=2, group=_normal_group(release_epoch=4))  # jitter=2
        gm = c.global_snapshot()
        assert gm.jitter_distribution == {1: 1, 2: 1}

    def test_global_histogram_merged(self) -> None:
        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=1, group=_degraded_group(size=5))
        gm = c.global_snapshot()
        assert gm.anonymity_set_histogram == {30: 1, 5: 1}


# ---------------------------------------------------------------------------
# Obligation 6 — bound checks
# ---------------------------------------------------------------------------

class TestObligation6BoundChecks:

    def test_all_bounds_satisfied_clean_run(self) -> None:
        c = LeakageMetricsCollector()
        # 100 normal groups, 0 force-released
        for i in range(100):
            c.record_group_settled(
                sealed_epoch=i,
                group=_normal_group(release_epoch=i + 1, size=30),  # jitter always 1
            )
        bounds = c.check_bounds()
        assert bounds["A"] is True   # 0% fill failure
        assert bounds["B"] is True   # zero spread (all jitter=1)
        assert bounds["C"] is True   # 0% degraded

    def test_bound_a_violated_high_force_release_rate(self) -> None:
        c = LeakageMetricsCollector()
        # 84 normal, 16 forced → 16% force-release > 15%
        for i in range(84):
            c.record_group_settled(sealed_epoch=i, group=_normal_group(release_epoch=i + 1))
        for i in range(84, 100):
            c.record_group_settled(sealed_epoch=i, group=_degraded_group(release_epoch=i))
        bounds = c.check_bounds()
        assert bounds["A"] is False

    def test_bound_a_satisfied_clearly_below_threshold(self) -> None:
        c = LeakageMetricsCollector()
        # 86 normal, 14 forced → 14% < 15% → satisfied
        for i in range(86):
            c.record_group_settled(sealed_epoch=i, group=_normal_group(release_epoch=i + 1))
        for i in range(86, 100):
            c.record_group_settled(sealed_epoch=i, group=_degraded_group(release_epoch=i))
        bounds = c.check_bounds()
        assert bounds["A"] is True

    def test_bound_c_violated_high_degraded_fraction(self) -> None:
        c = LeakageMetricsCollector()
        # 30 normal (30 transfers) + 5-member degraded = 5/35 ≈ 14.3% > 5%
        c.record_group_settled(sealed_epoch=0, group=_normal_group(size=30))
        c.record_group_settled(sealed_epoch=1, group=_degraded_group(size=5))
        bounds = c.check_bounds()
        assert bounds["C"] is False

    def test_bound_c_satisfied_low_degraded_fraction(self) -> None:
        c = LeakageMetricsCollector()
        # 600 normal (30 each) + 1 degraded (5 transfers) = 5/605 ≈ 0.83% <= 5%
        # release_epoch=i ensures jitter >= 0 (sealed_epoch == release_epoch, jitter=0).
        for i in range(20):
            c.record_group_settled(sealed_epoch=i, group=_normal_group(size=30, release_epoch=i))
        c.record_group_settled(sealed_epoch=20, group=_degraded_group(size=5))
        bounds = c.check_bounds()
        assert bounds["C"] is True

    def test_bound_b_satisfied_uniform_jitter(self) -> None:
        """All jitter = 2 → std=0 → spread=0 <= 0.15."""
        c = LeakageMetricsCollector()
        for i in range(10):
            c.record_group_settled(
                sealed_epoch=i,
                group=_normal_group(release_epoch=i + 2),  # jitter always 2
            )
        bounds = c.check_bounds()
        assert bounds["B"] is True

    def test_bound_b_satisfied_zero_jitter(self) -> None:
        """All jitter=0 → max=0 → spread check vacuously passes."""
        c = LeakageMetricsCollector()
        for i in range(5):
            c.record_group_settled(
                sealed_epoch=i,
                group=_normal_group(release_epoch=i),  # jitter=0
            )
        bounds = c.check_bounds()
        assert bounds["B"] is True

    def test_empty_collector_all_bounds_satisfied(self) -> None:
        """Vacuous case: no groups recorded → all bounds trivially satisfied."""
        c = LeakageMetricsCollector()
        bounds = c.check_bounds()
        assert bounds == {"A": True, "B": True, "C": True}


# ---------------------------------------------------------------------------
# Integration: lane + collector full roundtrip
# ---------------------------------------------------------------------------

class TestObligation6IntegrationRoundtrip:

    def test_sealed_group_roundtrip(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        groups = lane.flush(current_epoch=10)
        assert len(groups) == 1

        c = LeakageMetricsCollector()
        for g in groups:
            c.record_group_settled(sealed_epoch=0, group=g)
        gm = c.global_snapshot()
        assert gm.total_groups_completed == 1
        assert gm.total_groups_force_released == 0
        assert gm.total_transfers_settled == cfg.k
        assert gm.anonymity_set_histogram == {cfg.k: 1}

    def test_force_release_roundtrip(self) -> None:
        cfg = PrivacyLaneConfig(max_wait_epochs=2)
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(7):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        forced = lane.enforce_max_wait(current_epoch=2)
        assert len(forced) == 1

        c = LeakageMetricsCollector()
        c.record_group_settled(sealed_epoch=2, group=forced[0])
        gm = c.global_snapshot()
        assert gm.total_groups_force_released == 1
        assert gm.total_transfers_degraded == 7
        assert gm.anonymity_set_histogram == {7: 1}

    def test_mixed_run_bounds_pass(self) -> None:
        """Simulate a realistic run: many normal groups, a few forced."""
        cfg = PrivacyLaneConfig()
        c = LeakageMetricsCollector()
        # 19 normal k=30 groups
        for epoch in range(19):
            lane = PrivacyLane(cfg, current_epoch=epoch)
            for i in range(cfg.k):
                lane.submit(_contribution(agent=f"e{epoch}_a{i}"), current_epoch=epoch)
            for g in lane.flush(current_epoch=epoch + 1):
                c.record_group_settled(sealed_epoch=epoch, group=g)
        # 1 force-released with 5 transfers
        forced_group = _degraded_group(release_epoch=20, size=5)
        c.record_group_settled(sealed_epoch=20, group=forced_group)
        # 1/20 = 5% → Bound A exactly satisfied; C: 5/575 < 5% → satisfied
        bounds = c.check_bounds()
        assert bounds["A"] is True
        assert bounds["C"] is True
