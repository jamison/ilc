"""Phase 831 Row-5 B-Impl tests — obligations 1, 2, 3.

Covers:
  Obligation 1 — Rolling group construction / routing
  Obligation 2 — Deferred release queue with jitter scheduling
  Obligation 3 — bounded_hold carry-over with max-wait enforcement
"""
from __future__ import annotations

import pytest
from ilc_core.privacy.lane import (
    K_FALLBACK,
    K_PRIMARY,
    PRIVACY_LANE_RUNTIME_VERSION,
    RELEASE_JITTER_EPOCHS,
    PrivacyLane,
    PrivacyLaneConfig,
    ReleaseGroup,
    _is_express_bypass,
)
from ilc_core.privacy import PRIVACY_LANE_VERSION


# ---------------------------------------------------------------------------
# Transfer factory helpers
# ---------------------------------------------------------------------------

def _contribution(agent: str = "agent_a", amount: int = 100) -> dict:
    return {
        "object_ref": {"agent": agent},
        "amount_micro_ecu": amount,
        "transfer_class": {"type": "Contribution"},
    }


def _payment(agent: str = "agent_b", amount: int = 50, express: bool = False) -> dict:
    express_val = (
        {"agent_acknowledged_timing_disclosure": True}
        if express
        else None
    )
    return {
        "object_ref": {"agent": agent},
        "amount_micro_ecu": amount,
        "transfer_class": {"type": "Payment", "express": express_val},
    }


# ---------------------------------------------------------------------------
# Version pinning
# ---------------------------------------------------------------------------

def test_version_pin() -> None:
    assert PRIVACY_LANE_VERSION == "privacy_lane_831.v0.1"
    assert PRIVACY_LANE_RUNTIME_VERSION == "privacy_lane_831.v0.1"


def test_locked_constants() -> None:
    assert K_PRIMARY == 30
    assert K_FALLBACK == 20
    assert RELEASE_JITTER_EPOCHS == 3


# ---------------------------------------------------------------------------
# PrivacyLaneConfig
# ---------------------------------------------------------------------------

def test_config_defaults_to_primary_k() -> None:
    cfg = PrivacyLaneConfig()
    assert cfg.k == 30
    assert cfg.release_jitter_epochs == 3


def test_config_fallback_k_accepted() -> None:
    cfg = PrivacyLaneConfig(k=20)
    assert cfg.k == 20


def test_config_unknown_k_rejected() -> None:
    with pytest.raises(ValueError, match="primary_or_fallback"):
        PrivacyLaneConfig(k=25)


def test_config_wrong_jitter_rejected() -> None:
    with pytest.raises(ValueError, match="jitter_locked_at_3"):
        PrivacyLaneConfig(release_jitter_epochs=5)


def test_config_zero_max_wait_rejected() -> None:
    with pytest.raises(ValueError, match="max_wait_must_be_positive"):
        PrivacyLaneConfig(max_wait_epochs=0)


# ---------------------------------------------------------------------------
# Obligation 1 — Rolling group construction / routing
# ---------------------------------------------------------------------------

class TestObligation1RollingGroupConstruction:

    def test_contribution_enters_accumulator(self) -> None:
        lane = PrivacyLane(PrivacyLaneConfig(), current_epoch=1)
        result = lane.submit(_contribution(), current_epoch=1)
        assert result is None  # not bypassed
        assert lane.accumulator_size == 1

    def test_payment_without_express_enters_accumulator(self) -> None:
        lane = PrivacyLane(PrivacyLaneConfig(), current_epoch=1)
        result = lane.submit(_payment(express=False), current_epoch=1)
        assert result is None
        assert lane.accumulator_size == 1

    def test_payment_with_express_consent_bypasses(self) -> None:
        lane = PrivacyLane(PrivacyLaneConfig(), current_epoch=1)
        t = _payment(express=True)
        result = lane.submit(t, current_epoch=1)
        assert result is t  # returned immediately
        assert lane.accumulator_size == 0  # not added to accumulator

    def test_contribution_cannot_bypass_even_if_express_field_present(self) -> None:
        # Transfer_class=Contribution ignores any express-like field
        t = {
            "object_ref": {"agent": "a"},
            "transfer_class": {
                "type": "Contribution",
                "express": {"agent_acknowledged_timing_disclosure": True},
            },
        }
        lane = PrivacyLane(PrivacyLaneConfig(), current_epoch=1)
        result = lane.submit(t, current_epoch=1)
        assert result is None
        assert lane.accumulator_size == 1

    def test_k_transfers_seal_one_group(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=1)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"agent_{i}"), current_epoch=1)
        assert lane.accumulator_size == 0
        assert lane.release_queue_depth == 1

    def test_k_plus_one_transfers_one_in_accumulator(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=1)
        for i in range(cfg.k + 1):
            lane.submit(_contribution(agent=f"agent_{i}"), current_epoch=1)
        assert lane.accumulator_size == 1
        assert lane.release_queue_depth == 1

    def test_fallback_lane_seals_at_k20(self) -> None:
        cfg = PrivacyLaneConfig(k=K_FALLBACK)
        lane = PrivacyLane(cfg, current_epoch=1)
        for i in range(K_FALLBACK):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=1)
        assert lane.accumulator_size == 0
        assert lane.release_queue_depth == 1

    def test_stats_track_express_bypasses(self) -> None:
        lane = PrivacyLane(PrivacyLaneConfig(), current_epoch=1)
        lane.submit(_payment(express=True), current_epoch=1)
        lane.submit(_payment(express=True), current_epoch=1)
        assert lane.stats["express_bypasses"] == 2
        assert lane.stats["total_submitted"] == 2

    def test_stats_track_groups_completed(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=1)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=1)
        assert lane.stats["groups_completed"] == 1


# ---------------------------------------------------------------------------
# Obligation 2 — Deferred release queue with jitter scheduling
# ---------------------------------------------------------------------------

class TestObligation2DeferredReleaseQueue:

    def test_sealed_group_not_flushed_before_release_epoch(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        # Release epoch is 0 + jitter(0..3). Flush at epoch -1 should return nothing.
        ready = lane.flush(current_epoch=-1)
        assert ready == []
        assert lane.release_queue_depth == 1

    def test_flush_returns_group_at_or_after_release_epoch(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        # Flush at a high epoch — jitter is at most J=3, so epoch 10 will always work.
        ready = lane.flush(current_epoch=10)
        assert len(ready) == 1
        assert lane.release_queue_depth == 0

    def test_flushed_group_has_correct_transfer_count(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        groups = lane.flush(current_epoch=10)
        assert groups[0].anonymity_set_size == cfg.k
        assert len(groups[0].transfers) == cfg.k
        assert len(groups[0].agent_ids) == cfg.k

    def test_flushed_group_not_degraded(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        groups = lane.flush(current_epoch=10)
        assert groups[0].degraded_anonymity is False

    def test_release_epoch_within_jitter_bound(self) -> None:
        cfg = PrivacyLaneConfig()
        current_epoch = 5
        lane = PrivacyLane(cfg, current_epoch=current_epoch)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=current_epoch)
        # Peek at the queued group's release_epoch
        group = lane._release_queue[0]
        assert current_epoch <= group.release_epoch <= current_epoch + RELEASE_JITTER_EPOCHS

    def test_flush_only_returns_ready_groups(self) -> None:
        """Two sealed groups — only the early one is ready at epoch 1."""
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        # First group sealed at epoch 0 — release_epoch in [0, 3]
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        # Force the first group's release_epoch to 0 for determinism
        lane._release_queue[0].release_epoch = 0
        # Second group sealed at epoch 10 — release_epoch in [10, 13]
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"b_{i}"), current_epoch=10)
        lane._release_queue[1].release_epoch = 12

        ready = lane.flush(current_epoch=1)
        assert len(ready) == 1
        assert lane.release_queue_depth == 1

    def test_multiple_groups_flushed_when_all_ready(self) -> None:
        cfg = PrivacyLaneConfig()
        lane = PrivacyLane(cfg, current_epoch=0)
        for grp in range(3):
            for i in range(cfg.k):
                lane.submit(_contribution(agent=f"g{grp}_a{i}"), current_epoch=0)
        assert lane.release_queue_depth == 3
        ready = lane.flush(current_epoch=100)
        assert len(ready) == 3
        assert lane.release_queue_depth == 0


# ---------------------------------------------------------------------------
# Obligation 3 — bounded_hold carry-over with max-wait enforcement
# ---------------------------------------------------------------------------

class TestObligation3BoundedHold:

    def test_partial_group_not_force_released_before_max_wait(self) -> None:
        cfg = PrivacyLaneConfig(max_wait_epochs=4)
        lane = PrivacyLane(cfg, current_epoch=0)
        lane.submit(_contribution(), current_epoch=0)
        # Only 3 epochs have passed — max_wait not reached
        forced = lane.enforce_max_wait(current_epoch=3)
        assert forced == []
        assert lane.accumulator_size == 1

    def test_partial_group_force_released_at_max_wait(self) -> None:
        cfg = PrivacyLaneConfig(max_wait_epochs=4)
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(5):  # fewer than k=30
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        forced = lane.enforce_max_wait(current_epoch=4)
        assert len(forced) == 1
        assert forced[0].degraded_anonymity is True
        assert forced[0].anonymity_set_size == 5
        assert lane.accumulator_size == 0

    def test_force_release_preserves_full_partial_set(self) -> None:
        """Force release must not drop any transfers — all must settle."""
        cfg = PrivacyLaneConfig(max_wait_epochs=2)
        lane = PrivacyLane(cfg, current_epoch=10)
        transfers = [_contribution(agent=f"a_{i}") for i in range(7)]
        for t in transfers:
            lane.submit(t, current_epoch=10)
        forced = lane.enforce_max_wait(current_epoch=12)
        assert len(forced[0].transfers) == 7
        assert len(forced[0].agent_ids) == 7

    def test_force_release_not_single_contributor(self) -> None:
        """Force release must bundle ALL pending — no single-contributor fallback."""
        cfg = PrivacyLaneConfig(max_wait_epochs=1)
        lane = PrivacyLane(cfg, current_epoch=0)
        # Submit transfers from 3 different agents
        for i in range(3):
            lane.submit(_contribution(agent=f"agent_{i}"), current_epoch=0)
        forced = lane.enforce_max_wait(current_epoch=1)
        # Must release all 3 together — not one at a time
        assert len(forced) == 1
        assert forced[0].anonymity_set_size == 3

    def test_empty_accumulator_no_force_release(self) -> None:
        lane = PrivacyLane(PrivacyLaneConfig(), current_epoch=0)
        forced = lane.enforce_max_wait(current_epoch=100)
        assert forced == []

    def test_stats_track_force_releases(self) -> None:
        cfg = PrivacyLaneConfig(max_wait_epochs=1)
        lane = PrivacyLane(cfg, current_epoch=0)
        lane.submit(_contribution(), current_epoch=0)
        lane.enforce_max_wait(current_epoch=1)
        assert lane.stats["groups_force_released"] == 1
        assert lane.stats["groups_completed"] == 0

    def test_force_release_release_epoch_is_current(self) -> None:
        cfg = PrivacyLaneConfig(max_wait_epochs=2)
        lane = PrivacyLane(cfg, current_epoch=5)
        lane.submit(_contribution(), current_epoch=5)
        forced = lane.enforce_max_wait(current_epoch=7)
        assert forced[0].release_epoch == 7


# ---------------------------------------------------------------------------
# Express bypass helper
# ---------------------------------------------------------------------------

class TestExpressBypassHelper:

    def test_none_class_not_express(self) -> None:
        assert _is_express_bypass(None) is False

    def test_contribution_dict_not_express(self) -> None:
        assert _is_express_bypass({"type": "Contribution"}) is False

    def test_payment_no_express_not_bypass(self) -> None:
        assert _is_express_bypass({"type": "Payment", "express": None}) is False

    def test_payment_express_false_not_bypass(self) -> None:
        tc = {"type": "Payment", "express": {"agent_acknowledged_timing_disclosure": False}}
        assert _is_express_bypass(tc) is False

    def test_payment_express_true_is_bypass(self) -> None:
        tc = {"type": "Payment", "express": {"agent_acknowledged_timing_disclosure": True}}
        assert _is_express_bypass(tc) is True

    def test_payment_express_missing_key_not_bypass(self) -> None:
        tc = {"type": "Payment", "express": {"some_other_key": True}}
        assert _is_express_bypass(tc) is False


# ---------------------------------------------------------------------------
# ReleaseGroup shape
# ---------------------------------------------------------------------------

def test_release_group_shape() -> None:
    g = ReleaseGroup(
        release_epoch=5,
        transfers=[{"t": 1}],
        agent_ids=["a"],
        anonymity_set_size=1,
        degraded_anonymity=True,
    )
    assert g.release_epoch == 5
    assert g.anonymity_set_size == 1
    assert g.degraded_anonymity is True
