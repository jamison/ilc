"""Phase 1357 H11 Decimal reputation runtime.

This module preserves the legacy voting-power and atrophy formulas while
removing binary numeric arithmetic and caller trust-vector mutation. It does not
activate production reputation scoring.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import Mapping, TypeAlias


ExactNumberish: TypeAlias = Decimal | int | str

REPUTATION_RUNTIME_VERSION = "reputation_runtime_h11_float_kill_1357.v0.1"
REPUTATION_RUNTIME_VERSION_TOKEN = "REPUTATION_RUNTIME_VERSION_token_phase_1357"
REPUTATION_RUNTIME_H11_FLOAT_KILL_TOKEN = (
    "reputation_runtime_h11_float_kill_phase_1357.v0.1"
)
REPUTATION_NO_FLOAT_ARITHMETIC_TOKEN = "reputation_no_float_arithmetic_phase_1357"
PRODUCTION_REPUTATION_SCORING_NOT_ACTIVATED_TOKEN = (
    "production_reputation_scoring_not_activated_phase_1357"
)

ZERO = Decimal("0")
ONE = Decimal("1")
HALF = Decimal("0.5")
MAX_POTENTIAL_BOOST = Decimal("0.5")
ACCURACY_WEIGHT = Decimal("0.7")
PRECISION_WEIGHT = Decimal("0.3")
ATROPHY_HALF_LIFE_EPOCHS = 262800
ATROPHY_GRACE_EPOCHS = 1440
REPUTATION_SCORE_QUANTUM = Decimal("0.000000000001")


def _to_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(token) from exc
    else:
        raise ValueError(token)
    if not number.is_finite():
        raise ValueError("invalid_amount_non_finite")
    return ZERO if number.is_signed() and number == ZERO else number


def _non_negative_decimal(value: object, token: str) -> Decimal:
    number = _to_decimal(value, token)
    if number < ZERO:
        raise ValueError(token)
    return number


def _require_epoch(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _decay_multiplier(inactive_epochs: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 50
        return (HALF.ln() * (Decimal(inactive_epochs) / Decimal(ATROPHY_HALF_LIFE_EPOCHS))).exp()


def calculate_voting_power(stake: ExactNumberish, trust_vector: Mapping[str, object]) -> Decimal:
    """Calculate L1 voting power with exact Decimal arithmetic."""

    if not isinstance(trust_vector, Mapping):
        raise ValueError("reputation_trust_vector_must_be_mapping_phase_1357")

    normalized_stake = _non_negative_decimal(
        stake,
        "reputation_stake_must_be_non_negative_decimal_phase_1357",
    )
    accuracy = _non_negative_decimal(
        trust_vector.get("accuracy", ZERO),
        "reputation_accuracy_must_be_non_negative_decimal_phase_1357",
    )
    precision = _non_negative_decimal(
        trust_vector.get("precision", ZERO),
        "reputation_precision_must_be_non_negative_decimal_phase_1357",
    )
    potential = _non_negative_decimal(
        trust_vector.get("potential", ZERO),
        "reputation_potential_must_be_non_negative_decimal_phase_1357",
    )

    epistemic_score = (accuracy * ACCURACY_WEIGHT) + (precision * PRECISION_WEIGHT)
    efficiency_multiplier = ONE + (potential * MAX_POTENTIAL_BOOST)
    return normalized_stake * epistemic_score * efficiency_multiplier


def apply_atrophy(agent_state: Mapping[str, object], current_epoch: int) -> dict[str, object]:
    """Return an atrophy-adjusted copy of agent_state without mutating the caller."""

    if not isinstance(agent_state, Mapping):
        raise ValueError("reputation_agent_state_must_be_mapping_phase_1357")
    normalized_current_epoch = _require_epoch(
        current_epoch,
        "reputation_current_epoch_must_be_non_negative_int_phase_1357",
    )
    last_active_epoch = _require_epoch(
        agent_state.get("last_active_epoch", normalized_current_epoch),
        "reputation_last_active_epoch_must_be_non_negative_int_phase_1357",
    )
    if normalized_current_epoch < last_active_epoch:
        raise ValueError("reputation_current_epoch_precedes_last_active_epoch_phase_1357")

    trust_vector = agent_state.get("trust_vector")
    if not isinstance(trust_vector, Mapping):
        raise ValueError("reputation_trust_vector_must_be_mapping_phase_1357")

    next_state = dict(agent_state)
    next_trust_vector = dict(trust_vector)
    inactive_epochs = normalized_current_epoch - last_active_epoch

    if inactive_epochs > ATROPHY_GRACE_EPOCHS:
        decay = _decay_multiplier(inactive_epochs)
        for key, token in (
            ("accuracy", "reputation_accuracy_must_be_non_negative_decimal_phase_1357"),
            ("precision", "reputation_precision_must_be_non_negative_decimal_phase_1357"),
        ):
            score = _non_negative_decimal(next_trust_vector.get(key, ZERO), token)
            next_trust_vector[key] = (score * decay).quantize(REPUTATION_SCORE_QUANTUM)

    next_state["trust_vector"] = next_trust_vector
    return next_state


def require_production_reputation_scoring_activation(activation_token: str | None = None) -> None:
    raise ValueError(PRODUCTION_REPUTATION_SCORING_NOT_ACTIVATED_TOKEN)
