# SPDX-License-Identifier: AGPL-3.0-or-later
"""CDL-046 timed-out lifecycle amendment runtime.

Implements the CDL-035 timed_out amendment: orphan-timeout epoch check and
recovery-policy constant, with machine-auditable validation tokens.
"""

from __future__ import annotations

from ilc_core.node.validation_lifecycle_runtime_361 import CDL_035_DEPENDENCY

TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"
CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"
# LIFECYCLE_BASE_DEPENDENCY chains to the CDL-035 validation lifecycle runtime,
# which CDL-046 constitutionally amends. CDL-046 is an amendment row for CDL-035;
# this import makes the amendment dependency chain explicit and machine-auditable.
LIFECYCLE_BASE_DEPENDENCY = CDL_035_DEPENDENCY

# Ratified constants from CDL-046 (Phase 409).
# ORPHAN_TIMEOUT_EPOCHS and RECOVERY_POLICY are constitutionally locked;
# changing either requires opening a new CDL lane.
ORPHAN_TIMEOUT_EPOCHS: int = 4
RECOVERY_POLICY: str = "stake_full_release"


class TimedOutLifecycleError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def is_claim_timed_out(current_epoch: int, orphaned_since_epoch: int) -> bool:
    """Return True if a claim has been orphaned for >= ORPHAN_TIMEOUT_EPOCHS."""

    if not isinstance(current_epoch, int) or current_epoch < 0:
        raise TimedOutLifecycleError(
            "cdl_046_current_epoch_invalid",
            "current_epoch must be a non-negative integer",
        )
    if not isinstance(orphaned_since_epoch, int) or orphaned_since_epoch < 0:
        raise TimedOutLifecycleError(
            "cdl_046_orphaned_since_epoch_invalid",
            "orphaned_since_epoch must be a non-negative integer",
        )
    return (current_epoch - orphaned_since_epoch) >= ORPHAN_TIMEOUT_EPOCHS


def get_recovery_policy() -> str:
    """Return the ratified CDL-046 recovery policy for timed-out claims."""

    return RECOVERY_POLICY
