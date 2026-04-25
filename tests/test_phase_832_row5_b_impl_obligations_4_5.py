"""Phase 832 Row-5 B-Impl tests — obligations 4, 5.

Covers:
  Obligation 4 — Group-fill monitoring and fallback activation
  Obligation 5 — Force-release degraded-anonymity notification
"""
from __future__ import annotations

import pytest
from ilc_core.privacy import (
    FALLBACK_ACTIVATION_RATE,
    FILL_ALERT_MULTIPLIER,
    PRIVACY_LANE_MONITOR_VERSION,
    DegradedAnonymityNotification,
    FillAlert,
    FillMetrics,
    FillMonitor,
    PrivacyLane,
    PrivacyLaneConfig,
    ReleaseGroup,
    make_degraded_notifications,
)
from ilc_core.privacy.lane import K_FALLBACK, K_PRIMARY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _contribution(agent: str = "agent_a", amount: int = 100) -> dict:
    return {
        "object_ref": {"agent": agent},
        "amount_micro_ecu": amount,
        "transfer_class": {"type": "Contribution"},
    }


def _fill_lane(cfg: PrivacyLaneConfig, monitor: FillMonitor | None = None,
               epoch: int = 0) -> PrivacyLane:
    return PrivacyLane(cfg, current_epoch=epoch, monitor=monitor)


# ---------------------------------------------------------------------------
# Version pinning
# ---------------------------------------------------------------------------

def test_monitor_version_pin() -> None:
    assert PRIVACY_LANE_MONITOR_VERSION == "privacy_lane_monitor_832.v0.1"


def test_locked_monitor_constants() -> None:
    assert FILL_ALERT_MULTIPLIER == 1.5
    assert FALLBACK_ACTIVATION_RATE == 0.05


# ---------------------------------------------------------------------------
# FillMonitor construction
# ---------------------------------------------------------------------------

def test_fill_monitor_rejects_zero_max_wait() -> None:
    with pytest.raises(ValueError, match="max_wait_must_be_positive"):
        FillMonitor(max_wait_epochs=0)


def test_fill_monitor_initial_state() -> None:
    m = FillMonitor(max_wait_epochs=4)
    metrics = m.metrics()
    assert metrics.groups_completed == 0
    assert metrics.groups_force_released == 0
    assert metrics.fill_failure_rate == 0.0
    assert metrics.fallback_active is False
    assert metrics.alerts_emitted == 0


# ---------------------------------------------------------------------------
# Obligation 4 — Group-fill monitoring
# ---------------------------------------------------------------------------

class TestObligation4GroupFillMonitoring:

    def test_fill_success_increments_completed(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        m.record_fill_success(epoch=1)
        m.record_fill_success(epoch=2)
        assert m.metrics().groups_completed == 2

    def test_force_release_increments_force_released(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        m.record_force_release(epoch=5)
        assert m.metrics().groups_force_released == 1

    def test_failure_rate_zero_when_no_groups(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        assert m.metrics().fill_failure_rate == 0.0

    def test_failure_rate_all_completed(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        m.record_fill_success(epoch=1)
        m.record_fill_success(epoch=2)
        assert m.metrics().fill_failure_rate == 0.0

    def test_failure_rate_mixed(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        for _ in range(19):
            m.record_fill_success(epoch=1)
        m.record_force_release(epoch=2)
        # 1/20 = 0.05 exactly — at the threshold
        assert m.metrics().fill_failure_rate == pytest.approx(0.05)

    def test_fallback_not_active_below_threshold(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        for _ in range(100):
            m.record_fill_success(epoch=1)
        # 0 force releases → rate=0
        assert m.fallback_active is False

    def test_fallback_activated_at_threshold(self) -> None:
        """Exactly 5% force-release rate activates fallback."""
        m = FillMonitor(max_wait_epochs=4)
        for _ in range(19):
            m.record_fill_success(epoch=1)
        m.record_force_release(epoch=2)   # 1/20 = 5%
        assert m.fallback_active is True

    def test_fallback_activated_above_threshold(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        for _ in range(9):
            m.record_fill_success(epoch=1)
        m.record_force_release(epoch=2)   # 1/10 = 10%
        assert m.fallback_active is True

    def test_fallback_latches_stays_true_after_recovery(self) -> None:
        """Once activated, fallback stays active even if rate drops back below 5%."""
        m = FillMonitor(max_wait_epochs=4)
        for _ in range(9):
            m.record_fill_success(epoch=1)
        m.record_force_release(epoch=2)   # triggers fallback
        # Now fill many more groups to bring rate below 5%
        for _ in range(1000):
            m.record_fill_success(epoch=3)
        assert m.fallback_active is True   # still latched

    def test_fallback_reset_clears_latch(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        for _ in range(9):
            m.record_fill_success(epoch=1)
        m.record_force_release(epoch=2)
        assert m.fallback_active is True
        m.reset()
        assert m.fallback_active is False

    def test_fill_alert_not_emitted_below_threshold(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        # entry_epoch=0, current_epoch=5 → epochs_waiting=5 < 1.5*4=6
        alert = m.check_fill_alert(entry_epoch=0, current_epoch=5)
        assert alert is None

    def test_fill_alert_emitted_at_threshold(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        # entry_epoch=0, current_epoch=6 → epochs_waiting=6 >= 1.5*4=6
        alert = m.check_fill_alert(entry_epoch=0, current_epoch=6)
        assert isinstance(alert, FillAlert)
        assert alert.epoch == 6
        assert alert.epochs_waiting == 6
        assert alert.alert_threshold == 6.0

    def test_fill_alert_emitted_above_threshold(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        alert = m.check_fill_alert(entry_epoch=0, current_epoch=10)
        assert alert is not None
        assert alert.epochs_waiting == 10

    def test_fill_alert_increments_counter(self) -> None:
        m = FillMonitor(max_wait_epochs=4)
        m.check_fill_alert(entry_epoch=0, current_epoch=6)
        m.check_fill_alert(entry_epoch=0, current_epoch=7)
        assert m.metrics().alerts_emitted == 2

    def test_monitor_wired_to_lane_fill_success(self) -> None:
        """PrivacyLane calls monitor.record_fill_success when a group seals."""
        m = FillMonitor(max_wait_epochs=4)
        cfg = PrivacyLaneConfig()
        lane = _fill_lane(cfg, monitor=m, epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        assert m.metrics().groups_completed == 1
        assert m.metrics().groups_force_released == 0

    def test_monitor_wired_to_lane_force_release(self) -> None:
        """PrivacyLane calls monitor.record_force_release on enforce_max_wait."""
        m = FillMonitor(max_wait_epochs=2)
        cfg = PrivacyLaneConfig(max_wait_epochs=2)
        lane = _fill_lane(cfg, monitor=m, epoch=0)
        lane.submit(_contribution(), current_epoch=0)
        lane.enforce_max_wait(current_epoch=2)
        assert m.metrics().groups_force_released == 1
        assert m.metrics().groups_completed == 0

    def test_no_monitor_lane_still_works(self) -> None:
        """PrivacyLane with monitor=None (default) should not raise."""
        cfg = PrivacyLaneConfig()
        lane = _fill_lane(cfg, monitor=None, epoch=0)
        for i in range(cfg.k):
            lane.submit(_contribution(agent=f"a_{i}"), current_epoch=0)
        assert lane.release_queue_depth == 1


# ---------------------------------------------------------------------------
# Obligation 5 — Degraded-anonymity notification
# ---------------------------------------------------------------------------

class TestObligation5DegradedAnonymityNotification:

    def _make_group(
        self,
        n: int = 5,
        degraded: bool = True,
        release_epoch: int = 7,
    ) -> ReleaseGroup:
        transfers = [_contribution(agent=f"a_{i}") for i in range(n)]
        return ReleaseGroup(
            release_epoch=release_epoch,
            transfers=transfers,
            agent_ids=[f"a_{i}" for i in range(n)],
            anonymity_set_size=n,
            degraded_anonymity=degraded,
        )

    def test_degraded_group_produces_notifications(self) -> None:
        group = self._make_group(n=5, degraded=True)
        notifs = make_degraded_notifications(group, nominal_k=K_PRIMARY)
        assert len(notifs) == 5

    def test_non_degraded_group_produces_no_notifications(self) -> None:
        group = self._make_group(n=30, degraded=False)
        notifs = make_degraded_notifications(group, nominal_k=K_PRIMARY)
        assert notifs == []

    def test_notification_carries_correct_agent_id(self) -> None:
        group = self._make_group(n=3)
        notifs = make_degraded_notifications(group)
        agent_ids = [n.agent_id for n in notifs]
        assert agent_ids == ["a_0", "a_1", "a_2"]

    def test_notification_carries_actual_set_size(self) -> None:
        group = self._make_group(n=7)
        notifs = make_degraded_notifications(group)
        assert all(n.actual_set_size == 7 for n in notifs)

    def test_notification_carries_nominal_k(self) -> None:
        group = self._make_group(n=5)
        notifs = make_degraded_notifications(group, nominal_k=30)
        assert all(n.nominal_k == 30 for n in notifs)

    def test_notification_carries_release_epoch(self) -> None:
        group = self._make_group(n=5, release_epoch=42)
        notifs = make_degraded_notifications(group)
        assert all(n.release_epoch == 42 for n in notifs)

    def test_notification_default_nominal_k_is_primary(self) -> None:
        group = self._make_group(n=5)
        notifs = make_degraded_notifications(group)
        assert all(n.nominal_k == K_PRIMARY for n in notifs)

    def test_notification_shape(self) -> None:
        group = self._make_group(n=1, release_epoch=9)
        notif = make_degraded_notifications(group)[0]
        assert isinstance(notif, DegradedAnonymityNotification)
        assert notif.agent_id == "a_0"
        assert notif.actual_set_size == 1
        assert notif.nominal_k == K_PRIMARY
        assert notif.release_epoch == 9

    def test_lane_force_release_notifications_roundtrip(self) -> None:
        """Full roundtrip: lane force-release → make_degraded_notifications."""
        cfg = PrivacyLaneConfig(max_wait_epochs=2)
        lane = PrivacyLane(cfg, current_epoch=0)
        for i in range(5):
            lane.submit(_contribution(agent=f"agent_{i}"), current_epoch=0)
        forced = lane.enforce_max_wait(current_epoch=2)
        assert len(forced) == 1
        notifs = make_degraded_notifications(forced[0])
        assert len(notifs) == 5
        notif_agents = {n.agent_id for n in notifs}
        assert notif_agents == {f"agent_{i}" for i in range(5)}

    def test_fallback_k_reflected_in_notification(self) -> None:
        group = self._make_group(n=3)
        notifs = make_degraded_notifications(group, nominal_k=K_FALLBACK)
        assert all(n.nominal_k == K_FALLBACK for n in notifs)


# ---------------------------------------------------------------------------
# FillMetrics shape
# ---------------------------------------------------------------------------

def test_fill_metrics_shape() -> None:
    m = FillMonitor(max_wait_epochs=4)
    m.record_fill_success(epoch=1)
    m.record_force_release(epoch=2)
    metrics = m.metrics()
    assert isinstance(metrics, FillMetrics)
    assert metrics.groups_completed == 1
    assert metrics.groups_force_released == 1
    assert metrics.fill_failure_rate == pytest.approx(0.5)
    assert metrics.fallback_active is True  # 50% > 5% threshold
    assert metrics.alerts_emitted == 0


# ---------------------------------------------------------------------------
# FillAlert shape
# ---------------------------------------------------------------------------

def test_fill_alert_shape() -> None:
    alert = FillAlert(epoch=10, epochs_waiting=6, alert_threshold=6.0)
    assert alert.epoch == 10
    assert alert.epochs_waiting == 6
    assert alert.alert_threshold == 6.0
