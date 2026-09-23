# SPDX-License-Identifier: AGPL-3.0-only
"""ECU lifecycle state tokens and claim-bearing disposition matrix."""

from __future__ import annotations

from enum import Enum


class EcuLifecycleState(Enum):
    """Canonical ECU lifecycle states for monthly-close disposition checks."""

    PROVISIONAL = "ecu_state_provisional"
    QUOTED = "ecu_state_quoted"
    ATTRIBUTION_EVENTED = "ecu_state_attribution_evented"
    COMMITTED = "ecu_state_committed"
    LOTIZED = "ecu_state_lotized"
    TRANSFERRED = "ecu_state_transferred"
    EARMARKED = "ecu_state_earmarked"
    CONVERSION_CANDIDATE = "ecu_state_conversion_candidate"
    CONVERTED = "ecu_state_converted"
    EXPIRED = "ecu_state_expired"


# Claim-bearing states may enter EcuAccrualEvidence.agent_ecu_weights.
# Conservative default: only attribution-evented ECU is claim-bearing.
# Governance note: this coded assertion is subject to CDL ratification.
# A future CDL may explicitly add CONTRIBUTION-class TRANSFERRED ECU or other states.
# Until such a CDL is ratified, TRANSFERRED, EARMARKED, CONVERTED, and EXPIRED
# are not claim-bearing.
CLAIM_BEARING_STATES: frozenset[EcuLifecycleState] = frozenset(
    {
        EcuLifecycleState.ATTRIBUTION_EVENTED,
    }
)

NON_CLAIM_BEARING_STATES: frozenset[EcuLifecycleState] = frozenset(
    {
        EcuLifecycleState.PROVISIONAL,
        EcuLifecycleState.QUOTED,
        EcuLifecycleState.COMMITTED,
        EcuLifecycleState.LOTIZED,
        EcuLifecycleState.TRANSFERRED,
        EcuLifecycleState.EARMARKED,
        EcuLifecycleState.CONVERSION_CANDIDATE,
        EcuLifecycleState.CONVERTED,
        EcuLifecycleState.EXPIRED,
    }
)

CONTRIBUTION_TRANSFER_NOT_CLAIM_BEARING_TOKEN = (
    "contribution_transfer_not_claim_bearing_GAP_ECU_LIFECYCLE_DISPOSITION_MATRIX_00"
)
PAYMENT_TRANSFER_NOT_CLAIM_BEARING_TOKEN = (
    "payment_transfer_not_claim_bearing_GAP_ECU_LIFECYCLE_DISPOSITION_MATRIX_00"
)
ECU_LIFECYCLE_DISPOSITION_MATRIX_VERSION = (
    "ecu_lifecycle_disposition_matrix_GAP_ECU_LIFECYCLE_DISPOSITION_MATRIX_00.v0.1"
)
ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN = (
    "ecu_lifecycle_disposition_matrix_partition_invariant_GAP_ECU_LIFECYCLE_DISPOSITION_MATRIX_00"
)


def is_claim_bearing(state: EcuLifecycleState) -> bool:
    """Return True iff ECU in this state may enter monthly close accrual weights.

    Conservative default: only ATTRIBUTION_EVENTED is claim-bearing. This default
    may be expanded by a ratified CDL that explicitly names additional
    claim-bearing states. Do not expand without governance.
    """

    if not isinstance(state, EcuLifecycleState):
        raise TypeError("ecu_lifecycle_state_required")
    return state in CLAIM_BEARING_STATES


if CLAIM_BEARING_STATES | NON_CLAIM_BEARING_STATES != frozenset(EcuLifecycleState):
    raise ValueError(
        ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN + "_incomplete_partition"
    )
if CLAIM_BEARING_STATES & NON_CLAIM_BEARING_STATES != frozenset():
    raise ValueError(ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN + "_overlap")


__all__ = [
    "CLAIM_BEARING_STATES",
    "CONTRIBUTION_TRANSFER_NOT_CLAIM_BEARING_TOKEN",
    "ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN",
    "ECU_LIFECYCLE_DISPOSITION_MATRIX_VERSION",
    "EcuLifecycleState",
    "NON_CLAIM_BEARING_STATES",
    "PAYMENT_TRANSFER_NOT_CLAIM_BEARING_TOKEN",
    "is_claim_bearing",
]
