from __future__ import annotations

STAKING_LIVENESS_RUNTIME_VERSION = "staking_liveness_runtime_506.v0.1"
CDL_055_DEPENDENCY = "cdl_055_ratified_496.v0.1"
GENESIS_STAKE_AMOUNT = 400.0
LIVENESS_MISS_THRESHOLD = 8
EQUIVOCATION_FULL_SLASH = 1.0

_LIVENESS_PENALTY_FRACTION = 0.25


def validate_staking_and_liveness_state(
    stake: float,
    consecutive_missed_epochs: int,
    equivocation_state: bool,
) -> dict[str, float | str]:
    if isinstance(stake, bool) or not isinstance(stake, (int, float)) or float(stake) <= 0.0:
        raise ValueError('stake_must_be_positive')
    if not isinstance(consecutive_missed_epochs, int) or consecutive_missed_epochs < 0:
        raise ValueError('consecutive_missed_epochs_must_be_non_negative_int')
    if not isinstance(equivocation_state, bool):
        raise ValueError('equivocation_state_must_be_bool')

    if equivocation_state:
        return {
            'status': 'equivocation_slash',
            'penalty_fraction': EQUIVOCATION_FULL_SLASH,
        }
    if consecutive_missed_epochs >= LIVENESS_MISS_THRESHOLD:
        return {
            'status': 'liveness_penalty',
            'penalty_fraction': _LIVENESS_PENALTY_FRACTION,
        }
    return {
        'status': 'active',
        'penalty_fraction': 0.0,
    }


__all__ = [
    'CDL_055_DEPENDENCY',
    'EQUIVOCATION_FULL_SLASH',
    'GENESIS_STAKE_AMOUNT',
    'LIVENESS_MISS_THRESHOLD',
    'STAKING_LIVENESS_RUNTIME_VERSION',
    'validate_staking_and_liveness_state',
]
