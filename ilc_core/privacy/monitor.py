# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 832 Row-5 B-Impl — FillMonitor: obligations 4, 5.

Obligation 4 — Group-fill monitoring and fallback activation:
  - Emit a FillAlert when a k=30 group fails to fill within 1.5x max_wait.
  - Activate the k=20 fallback automatically when the force-release (fill
    failure) rate exceeds 5% of completed+forced windows.
  - Fallback activation latches: once triggered it requires an explicit reset
    so operators can observe and gate the transition.

Obligation 5 — Force-release degraded-anonymity notification:
  - make_degraded_notifications() maps each agent_id in a degraded group to
    a DegradedAnonymityNotification.
  - Notification carries actual_set_size vs nominal_k so downstream can
    display a meaningful signal to contributors.

Token: row5_b_impl_obligation_4_group_fill_monitoring
Token: row5_b_impl_obligation_5_degraded_anonymity_notification
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ilc_core.privacy.lane import K_FALLBACK, K_PRIMARY, ReleaseGroup

PRIVACY_LANE_MONITOR_VERSION = "privacy_lane_monitor_832.v0.1"

# Locked monitoring constants.
FILL_ALERT_MULTIPLIER: float = 1.5        # 1.5 × max_wait triggers a FillAlert
FALLBACK_ACTIVATION_RATE: float = 0.05    # 5 % force-release rate activates fallback


@dataclass(frozen=True)
class FillAlert:
    """Emitted when a group sits in the accumulator past the alert threshold.

    Token: row5_b_impl_fill_alert_shape
    """
    epoch: int
    epochs_waiting: int
    alert_threshold: float  # = 1.5 * max_wait_epochs


@dataclass(frozen=True)
class FillMetrics:
    """Point-in-time snapshot of fill-quality statistics.

    Token: row5_b_impl_fill_metrics_shape
    """
    groups_completed: int
    groups_force_released: int
    fill_failure_rate: float       # force_released / total; 0.0 when no groups yet
    fallback_active: bool
    alerts_emitted: int


@dataclass(frozen=True)
class DegradedAnonymityNotification:
    """Per-contributor notification produced by a force-release.

    Obligation 5 requires that each contributor whose transfer settles under
    a degraded group receives an explicit signal. Downstream layers (Phase 832
    notification path, or Phase 833 SIM-LEAKAGE-03 instrumentation) consume
    these objects.

    Token: row5_b_impl_degraded_anonymity_notification_shape
    """
    agent_id: Any
    actual_set_size: int
    nominal_k: int
    release_epoch: int


class FillMonitor:
    """Monitors k=30 primary lane fill quality and activates the k=20 fallback.

    Instantiate once per lane instance. Pass to PrivacyLane.__init__ so
    the lane can call record_fill_success / record_force_release automatically.

    Fallback activation latches: once fallback_active is True it remains True
    until reset() is called (requires operator intervention).

    Token: row5_b_impl_fill_monitor
    """

    def __init__(self, max_wait_epochs: int, primary_k: int = K_PRIMARY) -> None:
        if max_wait_epochs < 1:
            raise ValueError("fill_monitor_max_wait_must_be_positive")
        self._max_wait_epochs = max_wait_epochs
        self._primary_k = primary_k
        self._groups_completed: int = 0
        self._groups_force_released: int = 0
        self._alerts_emitted: int = 0
        self._fallback_latched: bool = False

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_fill_success(self, epoch: int) -> None:  # noqa: ARG002
        """Record a normally-sealed k-group."""
        self._groups_completed += 1

    def record_force_release(self, epoch: int) -> None:  # noqa: ARG002
        """Record a forced partial release and re-evaluate fallback activation."""
        self._groups_force_released += 1
        rate = self._failure_rate()
        if not self._fallback_latched and rate >= FALLBACK_ACTIVATION_RATE:
            self._fallback_latched = True

    # ------------------------------------------------------------------
    # Alert check (call on each epoch tick for the active accumulator)
    # ------------------------------------------------------------------

    def check_fill_alert(
        self,
        entry_epoch: int,
        current_epoch: int,
    ) -> FillAlert | None:
        """Return a FillAlert if the accumulator has exceeded the alert threshold.

        Threshold: epochs_waiting >= 1.5 * max_wait_epochs.
        Does NOT emit an alert for an empty accumulator (caller must guard).

        Token: row5_b_impl_fill_alert_check
        """
        epochs_waiting = current_epoch - entry_epoch
        threshold = FILL_ALERT_MULTIPLIER * self._max_wait_epochs
        if epochs_waiting >= threshold:
            self._alerts_emitted += 1
            return FillAlert(
                epoch=current_epoch,
                epochs_waiting=epochs_waiting,
                alert_threshold=threshold,
            )
        return None

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def fallback_active(self) -> bool:
        """True when the k=20 fallback should be used instead of k=30."""
        return self._fallback_latched

    def metrics(self) -> FillMetrics:
        """Return a snapshot of current fill-quality statistics."""
        return FillMetrics(
            groups_completed=self._groups_completed,
            groups_force_released=self._groups_force_released,
            fill_failure_rate=self._failure_rate(),
            fallback_active=self._fallback_latched,
            alerts_emitted=self._alerts_emitted,
        )

    def reset(self) -> None:
        """Reset the fallback latch — requires operator decision to invoke."""
        self._fallback_latched = False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _failure_rate(self) -> float:
        total = self._groups_completed + self._groups_force_released
        if total == 0:
            return 0.0
        return self._groups_force_released / total


# ------------------------------------------------------------------
# Obligation 5 helper
# ------------------------------------------------------------------

def make_degraded_notifications(
    group: ReleaseGroup,
    nominal_k: int = K_PRIMARY,
) -> list[DegradedAnonymityNotification]:
    """Produce per-contributor degraded-anonymity notifications from a group.

    Returns an empty list if the group's degraded_anonymity flag is False.
    Each agent_id in group.agent_ids gets one notification.

    Token: row5_b_impl_make_degraded_notifications
    """
    if not group.degraded_anonymity:
        return []
    return [
        DegradedAnonymityNotification(
            agent_id=agent_id,
            actual_set_size=group.anonymity_set_size,
            nominal_k=nominal_k,
            release_epoch=group.release_epoch,
        )
        for agent_id in group.agent_ids
    ]
