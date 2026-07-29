# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-V2 sybil-resistance runtime.

Deterministic heuristic scoring helpers with bounded risk-to-penalty mapping
and tokenized validation failures.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from ilc_core.reputation.temporal_decay_runtime import CDL_V1_DEPENDENCY

CDL_V2_RUNTIME_VERSION = "cdl_v2_sybil_resistance_runtime_389.v0.1"
CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"


class SybilResistanceValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


_ZERO = Decimal("0")
_ONE = Decimal("1")
_ROUNDING_QUANTUM = Decimal("0.000000000001")


def _require_numeric(name: str, value: float) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_invalid_numeric",
            f"{name} must be a numeric value",
        )
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_invalid_numeric",
            f"{name} must be a finite numeric value",
        ) from exc
    if not number.is_finite():
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_invalid_numeric",
            f"{name} must be a finite numeric value",
        )
    return _ZERO if number.is_signed() and number == _ZERO else number


def _require_unit_interval(name: str, value: float) -> Decimal:
    number = _require_numeric(name, value)
    if number < _ZERO or number > _ONE:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_out_of_range",
            f"{name} must be in [0, 1]",
        )
    return number


def _require_validation_epoch(epoch_type: str) -> None:
    if epoch_type != "validation_epoch":
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_epoch_context_invalid",
            "sybil-resistance heuristics are validation-epoch scoped",
        )


def _score(value: Decimal) -> float:
    """Return a bounded float risk signal, not a consensus or settlement weight.

    The CDL-V2 runtime predates Decimal-only settlement surfaces. Callers use
    these scores as advisory anti-sybil heuristics; they are not consumed by
    epoch settlement roots or validator quorum weights in current code.
    """
    return float(value.quantize(_ROUNDING_QUANTUM))


def compute_identity_cluster_risk(
    *,
    shared_operator_fraction: float,
    shared_infrastructure_fraction: float,
    key_rotation_overlap_fraction: float,
) -> float:
    """Compute bounded cluster-risk signal from overlap indicators.

    Return value is an advisory float. It MUST NOT be passed into ECU, stake,
    settlement, or quorum-weight computations. Convert to Decimal only within a
    CDL-107-authorized scoring path.
    """

    operator = _require_unit_interval("shared_operator_fraction", shared_operator_fraction)
    infrastructure = _require_unit_interval(
        "shared_infrastructure_fraction", shared_infrastructure_fraction
    )
    key_overlap = _require_unit_interval(
        "key_rotation_overlap_fraction", key_rotation_overlap_fraction
    )

    risk = (
        (Decimal("0.50") * operator)
        + (Decimal("0.30") * infrastructure)
        + (Decimal("0.20") * key_overlap)
    )
    return _score(max(_ZERO, min(_ONE, risk)))


def compute_burst_write_penalty(
    *,
    writes_per_validation_epoch: float,
    baseline_writes_per_validation_epoch: float,
    burst_sensitivity: float = 0.35,
    epoch_type: str = "validation_epoch",
) -> float:
    """Compute bounded penalty for burst-write anomalies.

    Return value is an advisory float. It MUST NOT be passed into ECU, stake,
    settlement, or quorum-weight computations. Convert to Decimal only within a
    CDL-107-authorized scoring path.
    """

    writes = _require_numeric("writes_per_validation_epoch", writes_per_validation_epoch)
    baseline = _require_numeric(
        "baseline_writes_per_validation_epoch", baseline_writes_per_validation_epoch
    )
    sensitivity = _require_numeric("burst_sensitivity", burst_sensitivity)
    _require_validation_epoch(epoch_type)

    if writes < _ZERO or baseline <= _ZERO:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_rate_non_positive",
            "writes must be >= 0 and baseline must be > 0",
        )
    if sensitivity <= _ZERO or sensitivity > _ONE:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_burst_sensitivity_out_of_range",
            "burst_sensitivity must be in (0, 1]",
        )

    ratio = writes / baseline
    if ratio <= _ONE:
        return 0.0

    penalty = min(_ONE, (ratio - _ONE) * sensitivity)
    return _score(penalty)


def compute_diversity_floor_contribution(
    *,
    distinct_cluster_refs: float,
    expected_diversity_floor: float,
) -> float:
    """Compute contribution signal for diversity-floor satisfaction.

    Return value is an advisory float. It MUST NOT be passed into ECU, stake,
    settlement, or quorum-weight computations. Convert to Decimal only within a
    CDL-107-authorized scoring path.
    """

    distinct_refs = _require_numeric("distinct_cluster_refs", distinct_cluster_refs)
    expected_floor = _require_numeric("expected_diversity_floor", expected_diversity_floor)

    if distinct_refs < _ZERO or expected_floor <= _ZERO:
        raise SybilResistanceValidationError(
            "cdl_v2_sybil_diversity_floor_invalid",
            "distinct refs must be >= 0 and expected floor must be > 0",
        )

    contribution = min(_ONE, distinct_refs / expected_floor)
    return _score(contribution)


def compute_sybil_penalty(
    *,
    cluster_risk: float,
    burst_write_penalty: float,
    diversity_floor_contribution: float,
) -> float:
    """Map risk signals to bounded sybil penalty score in [0, 1].

    Return value is an advisory float. It MUST NOT be passed into ECU, stake,
    settlement, or quorum-weight computations. Convert to Decimal only within a
    CDL-107-authorized scoring path.
    """

    risk = _require_unit_interval("cluster_risk", cluster_risk)
    burst = _require_unit_interval("burst_write_penalty", burst_write_penalty)
    diversity = _require_unit_interval(
        "diversity_floor_contribution", diversity_floor_contribution
    )

    raw_penalty = (
        (Decimal("0.55") * risk)
        + (Decimal("0.35") * burst)
        - (Decimal("0.25") * diversity)
    )
    bounded = max(_ZERO, min(_ONE, raw_penalty))
    return _score(bounded)
