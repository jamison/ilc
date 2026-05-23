# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 550 passive ECU attribution runtime."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from ilc_core.network.d2d.centrality_delta_gossip_runtime import (
    CDL_060_GOSSIP_RUNTIME_VERSION as _CDL_060_GOSSIP_RUNTIME_CHECK,
)

PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_060_GOSSIP_RUNTIME_DEPENDENCY = "cdl_060_gossip_runtime_548.v0.1"
# M1 audit fix (Phase 946): all ECU rate constants converted to Decimal.
# Decimal * float raises TypeError — all four must be Decimal together.
PASSIVE_ATTRIBUTION_RATE = Decimal("0.20")
DECAY_FLOOR = Decimal("0.05")
ATTRIBUTION_CAP = Decimal("0.15")
GAMMA = Decimal("0.15")
_TWELVE_PLACES = Decimal("0.000000000001")


class PassiveECUAttributionContractError(RuntimeError):
    """Raised when module-level runtime contract invariants are invalid."""


def _validate_runtime_contract() -> None:
    if _CDL_060_GOSSIP_RUNTIME_CHECK != CDL_060_GOSSIP_RUNTIME_DEPENDENCY:
        raise PassiveECUAttributionContractError(
            "passive_ecu_dependency_mismatch"
        )
    if PASSIVE_ATTRIBUTION_RATE * (Decimal("1") + GAMMA) >= Decimal("1"):
        raise PassiveECUAttributionContractError(
            "authorship_primacy_invariant_violated: passive rate exceeds direct reward"
        )
    if ATTRIBUTION_CAP >= Decimal("1"):
        raise PassiveECUAttributionContractError(
            "authorship_primacy_invariant_violated: attribution cap exceeds direct reward"
        )


_validate_runtime_contract()


def _coerce_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if not isinstance(value, (Decimal, int, float, str)):
        raise ValueError(token)
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(token)
    return amount


def quality_factor(q_i: Decimal) -> Decimal:
    """Compute the bounded quality multiplier for a normalized quality score."""

    normalized = _coerce_decimal(q_i, "q_i_must_be_float_in_unit_interval")
    if normalized < Decimal("0") or normalized > Decimal("1"):
        raise ValueError("q_i_must_be_float_in_unit_interval")
    return (Decimal("1") + GAMMA * (Decimal("2") * normalized - Decimal("1"))).quantize(
        _TWELVE_PLACES
    )


def compute_passive_ecu(
    base_reward: Decimal,
    centrality_score: Decimal,
    q_i: Decimal,
) -> Decimal:
    """Compute passive ECU attribution for one reuse path."""

    normalized_base_reward = _coerce_decimal(
        base_reward, "base_reward_must_be_non_negative_float"
    )
    if normalized_base_reward < Decimal("0"):
        raise ValueError("base_reward_must_be_non_negative_float")
    if normalized_base_reward == Decimal("0"):
        return Decimal("0")

    normalized_centrality = _coerce_decimal(
        centrality_score, "centrality_score_must_be_non_negative_float"
    )
    if normalized_centrality < Decimal("0") or normalized_centrality > Decimal("1"):
        raise ValueError("centrality_score_must_be_non_negative_float")
    if normalized_centrality < DECAY_FLOOR:
        return Decimal("0")

    raw = (
        normalized_base_reward
        * PASSIVE_ATTRIBUTION_RATE
        * normalized_centrality
        * quality_factor(q_i)
    )
    cap = normalized_base_reward * ATTRIBUTION_CAP
    return min(raw, cap).quantize(_TWELVE_PLACES)
