# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-031 dynamic ranking multiplier runtime.

Authority: CDL-019 amendment Phase 1501p.

The historical Phase 1344 issuance-gate deferral token remains in
``ilc_core/epoch/issuance_economics_integration_gate.py``. This module is a
standalone guarded runtime surface and does not alter the issuance gate.
"""

from __future__ import annotations

from decimal import Decimal, getcontext, localcontext
from typing import Mapping


DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED: bool = True

CDL_031_DYNAMIC_RANKING_RUNTIME_VERSION = (
    "cdl_031_dynamic_ranking_multiplier_runtime_1502p.v0.1"
)
CDL_031_DYNAMIC_RANKING_RUNTIME_TOKEN = (
    "cdl_031_dynamic_ranking_multiplier_runtime_phase_1502p"
)
CDL_031_AUTHORITY_TOKEN = "cdl_019_amendment_ratified_phase_1501p"
DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED_GUARD_TOKEN = (
    "DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED_guard_set_phase_1502p"
)
CDL_031_DEFERRED_TOKEN_RETAINED = (
    "cdl_031_runtime_deferred_to_governance_weight_lane_phase_1344"
)

DYNAMIC_RANKING_FUNCTION: str = "log"
DYNAMIC_RANKING_F_MIN: Decimal = Decimal("0.80")
DYNAMIC_RANKING_F_MAX: Decimal = Decimal("1.65")
DYNAMIC_RANKING_LOG_B: Decimal = Decimal("5")
DYNAMIC_RANKING_ANTI_DOMINANCE_MAX_SHARE: Decimal = Decimal("0.01")
DYNAMIC_RANKING_TOP_QUINTILE_SHARE_CAP: Decimal = Decimal("0.40")
DYNAMIC_RANKING_REFUTATION_COUPLING_MAX_RATIO: Decimal = Decimal("1.50")

_ZERO = Decimal("0")
_ONE = Decimal("1")
_MIN_PRECISION = 50


def _require_decimal(value: object, token: str) -> Decimal:
    if not isinstance(value, Decimal):
        raise ValueError(token)
    if not value.is_finite():
        raise ValueError(token)
    return value


def _clamp_multiplier(value: Decimal) -> Decimal:
    if value < DYNAMIC_RANKING_F_MIN:
        return DYNAMIC_RANKING_F_MIN
    if value > DYNAMIC_RANKING_F_MAX:
        return DYNAMIC_RANKING_F_MAX
    return value


def compute_dynamic_ranking_multiplier(epistemic_weight: Decimal) -> Decimal:
    """Return the guarded CDL-031 multiplier for an epistemic weight in [0, 1]."""

    weight = _require_decimal(
        epistemic_weight,
        "dynamic_ranking_multiplier_invalid_input",
    )
    if weight < _ZERO or weight > _ONE:
        raise ValueError("dynamic_ranking_multiplier_out_of_range_input")

    with localcontext() as ctx:
        ctx.prec = max(getcontext().prec, _MIN_PRECISION)
        denominator = (_ONE + DYNAMIC_RANKING_LOG_B).ln()
        raw_result = DYNAMIC_RANKING_F_MIN + (
            (DYNAMIC_RANKING_F_MAX - DYNAMIC_RANKING_F_MIN)
            * ((_ONE + DYNAMIC_RANKING_LOG_B * weight).ln() / denominator)
        )

    result = _clamp_multiplier(raw_result)
    if not result.is_finite():
        raise ValueError("dynamic_ranking_multiplier_non_finite_output")
    return result


def compute_dynamic_ranking_multiplier_from_node_score(
    node_score: Mapping[str, object],
) -> Decimal:
    """Read ``NodeScoreVector.epistemic_weight`` from a node-score mapping."""

    if "epistemic_weight" not in node_score:
        raise ValueError("dynamic_ranking_multiplier_missing_epistemic_weight")
    return compute_dynamic_ranking_multiplier(node_score["epistemic_weight"])


def check_anti_dominance(
    multipliers: list[Decimal],
    max_share_cap: Decimal = DYNAMIC_RANKING_ANTI_DOMINANCE_MAX_SHARE,
) -> bool:
    """Return True when no participant exceeds the multiplier share cap."""

    if not multipliers:
        raise ValueError("dynamic_ranking_multiplier_empty_population")

    cap = _require_decimal(
        max_share_cap,
        "dynamic_ranking_multiplier_invalid_max_share_cap",
    )
    if cap <= _ZERO or cap > _ONE:
        raise ValueError("dynamic_ranking_multiplier_invalid_max_share_cap")

    resolved: list[Decimal] = []
    for multiplier in multipliers:
        value = _require_decimal(
            multiplier,
            "dynamic_ranking_multiplier_invalid_population_value",
        )
        if value < _ZERO:
            raise ValueError("dynamic_ranking_multiplier_negative_population_value")
        resolved.append(value)

    total = sum(resolved, _ZERO)
    if total <= _ZERO:
        raise ValueError("dynamic_ranking_multiplier_non_positive_population_total")

    return all((value / total) <= cap for value in resolved)
