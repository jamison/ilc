# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from decimal import Decimal

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, to_decimal

STAKING_LIVENESS_RUNTIME_VERSION = "staking_liveness_runtime_506.v0.1"
CDL_055_DEPENDENCY = "cdl_055_ratified_496.v0.1"
GENESIS_STAKE_AMOUNT = Decimal("400")
LIVENESS_MISS_THRESHOLD = 8
EQUIVOCATION_FULL_SLASH = Decimal("1")
LIVENESS_PENALTY_FRACTION = Decimal("0.25")


def validate_staking_and_liveness_state(
    stake: Decimal | int | float | str,
    consecutive_missed_epochs: int,
    equivocation_state: bool,
) -> dict[str, str]:
    if isinstance(stake, bool) or isinstance(stake, str):
        raise ValueError('stake_must_be_positive')
    if to_decimal(stake, token="stake_must_be_positive") <= Decimal("0"):
        raise ValueError('stake_must_be_positive')
    if not isinstance(consecutive_missed_epochs, int) or consecutive_missed_epochs < 0:
        raise ValueError('consecutive_missed_epochs_must_be_non_negative_int')
    if not isinstance(equivocation_state, bool):
        raise ValueError('equivocation_state_must_be_bool')

    if equivocation_state:
        return {
            'status': 'equivocation_slash',
            'penalty_fraction': decimal_to_canonical_string(EQUIVOCATION_FULL_SLASH),
        }
    if consecutive_missed_epochs >= LIVENESS_MISS_THRESHOLD:
        return {
            'status': 'liveness_penalty',
            'penalty_fraction': decimal_to_canonical_string(LIVENESS_PENALTY_FRACTION),
        }
    return {
        'status': 'active',
        'penalty_fraction': '0',
    }


__all__ = [
    'CDL_055_DEPENDENCY',
    'EQUIVOCATION_FULL_SLASH',
    'GENESIS_STAKE_AMOUNT',
    'LIVENESS_MISS_THRESHOLD',
    'LIVENESS_PENALTY_FRACTION',
    'STAKING_LIVENESS_RUNTIME_VERSION',
    'validate_staking_and_liveness_state',
]
