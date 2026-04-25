"""Phase 832 Row-5 B-Impl privacy lane sub-package.

Implements the locked Row-5 mechanism:
  primary:  k=30, rolling_threshold, release_jitter_epochs=3, bounded_hold
  fallback: k=20, same parameters

Token: row5_b_impl_privacy_lane_831
Token: row5_b_impl_obligation_4_group_fill_monitoring
Token: row5_b_impl_obligation_5_degraded_anonymity_notification
"""
from ilc_core.privacy.lane import PrivacyLane, PrivacyLaneConfig, ReleaseGroup
from ilc_core.privacy.monitor import (
    FALLBACK_ACTIVATION_RATE,
    FILL_ALERT_MULTIPLIER,
    PRIVACY_LANE_MONITOR_VERSION,
    DegradedAnonymityNotification,
    FillAlert,
    FillMetrics,
    FillMonitor,
    make_degraded_notifications,
)

PRIVACY_LANE_VERSION = "privacy_lane_831.v0.1"

__all__ = [
    "FALLBACK_ACTIVATION_RATE",
    "FILL_ALERT_MULTIPLIER",
    "PRIVACY_LANE_MONITOR_VERSION",
    "PRIVACY_LANE_VERSION",
    "DegradedAnonymityNotification",
    "FillAlert",
    "FillMetrics",
    "FillMonitor",
    "PrivacyLane",
    "PrivacyLaneConfig",
    "ReleaseGroup",
    "make_degraded_notifications",
]
