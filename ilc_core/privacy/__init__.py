# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 833 Row-5 B-Impl privacy lane sub-package.

Implements the locked Row-5 mechanism:
  primary:  k=30, rolling_threshold, release_jitter_epochs=3, bounded_hold
  fallback: k=20, same parameters

Token: row5_b_impl_privacy_lane_831
Token: row5_b_impl_obligation_4_group_fill_monitoring
Token: row5_b_impl_obligation_5_degraded_anonymity_notification
Token: row5_b_impl_obligation_6_sim_leakage_03_instrumentation
"""
from ilc_core.privacy.lane import PrivacyLane, PrivacyLaneConfig, ReleaseGroup
from ilc_core.privacy.metrics import (
    LEAKAGE_METRICS_VERSION,
    SIM_LEAKAGE_03_BOUND_A,
    SIM_LEAKAGE_03_BOUND_B,
    SIM_LEAKAGE_03_BOUND_C,
    EpochMetrics,
    GlobalMetrics,
    LeakageMetricsCollector,
)
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
from ilc_core.privacy.transfer_mixing_framework import (
    ACTIVATION_GATE_REQUIRED,
    MIXING_FRAMEWORK_NOT_ACTIVATED_PRODUCTION_TOKEN,
    TRANSFER_MIXING_K_ANONYMITY_FRAMEWORK_TOKEN,
    TransferMixingFrameworkQuote,
    build_transfer_mixing_framework_quote,
    route_transfer_through_mixing_framework,
)

PRIVACY_LANE_VERSION = "privacy_lane_831.v0.1"

__all__ = [
    "FALLBACK_ACTIVATION_RATE",
    "FILL_ALERT_MULTIPLIER",
    "LEAKAGE_METRICS_VERSION",
    "PRIVACY_LANE_MONITOR_VERSION",
    "PRIVACY_LANE_VERSION",
    "SIM_LEAKAGE_03_BOUND_A",
    "SIM_LEAKAGE_03_BOUND_B",
    "SIM_LEAKAGE_03_BOUND_C",
    "ACTIVATION_GATE_REQUIRED",
    "MIXING_FRAMEWORK_NOT_ACTIVATED_PRODUCTION_TOKEN",
    "TRANSFER_MIXING_K_ANONYMITY_FRAMEWORK_TOKEN",
    "DegradedAnonymityNotification",
    "EpochMetrics",
    "FillAlert",
    "FillMetrics",
    "FillMonitor",
    "GlobalMetrics",
    "LeakageMetricsCollector",
    "PrivacyLane",
    "PrivacyLaneConfig",
    "ReleaseGroup",
    "TransferMixingFrameworkQuote",
    "build_transfer_mixing_framework_quote",
    "make_degraded_notifications",
    "route_transfer_through_mixing_framework",
]
