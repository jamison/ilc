"""Phase 831 Row-5 B-Impl privacy lane sub-package.

Implements the locked Row-5 mechanism:
  primary:  k=30, rolling_threshold, release_jitter_epochs=3, bounded_hold
  fallback: k=20, same parameters

Token: row5_b_impl_privacy_lane_831
"""
from ilc_core.privacy.lane import PrivacyLane, PrivacyLaneConfig, ReleaseGroup

PRIVACY_LANE_VERSION = "privacy_lane_831.v0.1"

__all__ = ["PrivacyLane", "PrivacyLaneConfig", "ReleaseGroup", "PRIVACY_LANE_VERSION"]
