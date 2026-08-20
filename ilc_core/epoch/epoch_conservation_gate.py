# SPDX-License-Identifier: AGPL-3.0-only
"""Epoch distribution conservation gate for future epoch runner code.

Callers that compute an ``EpochDistributionOutput`` and then decide whether to
commit it must invoke ``verify_epoch_conservation_before_commit(output)`` before
calling ``commit_epoch_distribution``. This phase creates the standalone gate
and tests it; no epoch runner exists in this scope, so the call order is a
documented convention until a runner or ceremony module wires it explicitly.

The gate complements the generic inline check inside ``commit_epoch_distribution``.
It does not replace that check and does not special-case epoch 0.
"""

from __future__ import annotations

from decimal import Decimal

from ilc_core.epoch.epoch_distribution_writer import EpochDistributionOutput


EPOCH_CONSERVATION_GATE_VERSION = (
    "epoch_conservation_gate_GAP_PUBLIC_RC_EPOCH_FIX1_00C.v0.1"
)
EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN = (
    "epoch_gate_conservation_check_added_GAP_PUBLIC_RC_EPOCH_FIX1_00C"
)
NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN = (
    "no_unsettled_ilc_issuance_gate_hard_check_GAP_PUBLIC_RC_EPOCH_FIX1_00C"
)
EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN = (
    "epoch_0_to_1_transition_conservation_enforced_GAP_PUBLIC_RC_EPOCH_FIX1_00C"
)

_ZERO = Decimal("0")


def verify_epoch_conservation_before_commit(output: EpochDistributionOutput) -> None:
    """Raise unless an epoch distribution output is exactly conserved."""
    if not isinstance(output, EpochDistributionOutput):
        raise ValueError("conservation_gate_requires_epoch_distribution_output")
    if output.conservation_verified is not True:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if output.conservation_record.difference_ilc != _ZERO:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    return None


__all__ = [
    "EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN",
    "EPOCH_CONSERVATION_GATE_VERSION",
    "EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN",
    "NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN",
    "verify_epoch_conservation_before_commit",
]
