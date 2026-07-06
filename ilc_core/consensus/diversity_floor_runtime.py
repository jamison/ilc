# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-V3 diversity-floor runtime.

Deterministic cluster-diversity helpers with bounded penalty scoring and
machine-auditable validation tokens.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from ilc_core.identity.sybil_resistance_runtime import CDL_V2_DEPENDENCY

CDL_V3_RUNTIME_VERSION = "cdl_v3_diversity_floor_runtime_397.v0.1"
CDL_V3_DEPENDENCY = "cdl_v3_diversity_floor_397.v0.1"


class DiversityFloorValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


_ZERO = Decimal("0")
_ONE = Decimal("1")
_ROUNDING_QUANTUM = Decimal("0.000000000001")


def _require_numeric(name: str, value: float) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_invalid_numeric",
            f"{name} must be a numeric value",
        )
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_invalid_numeric",
            f"{name} must be a finite numeric value",
        ) from exc
    if not number.is_finite():
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_invalid_numeric",
            f"{name} must be a finite numeric value",
        )
    return number


def _require_positive(name: str, value: float) -> Decimal:
    number = _require_numeric(name, value)
    if number <= _ZERO:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_non_positive",
            f"{name} must be > 0",
        )
    return number


def _score(value: Decimal) -> float:
    return float(value.quantize(_ROUNDING_QUANTUM))


def compute_max_cluster_share(*, largest_cluster_slots: float, total_panel_slots: float) -> float:
    """Compute max cluster share in [0, 1] from panel slot counts."""

    largest = _require_numeric("largest_cluster_slots", largest_cluster_slots)
    total = _require_positive("total_panel_slots", total_panel_slots)

    if largest < _ZERO:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_negative_largest_cluster",
            "largest_cluster_slots must be >= 0",
        )
    if largest > total:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_cluster_exceeds_total",
            "largest_cluster_slots cannot exceed total_panel_slots",
        )

    return _score(largest / total)


def meets_distinct_cluster_floor(*, distinct_clusters: float, distinct_cluster_floor: float) -> bool:
    """Return whether the distinct-cluster floor is satisfied."""

    distinct = _require_numeric("distinct_clusters", distinct_clusters)
    floor = _require_positive("distinct_cluster_floor", distinct_cluster_floor)

    if distinct < _ZERO:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_negative_distinct_clusters",
            "distinct_clusters must be >= 0",
        )

    return distinct >= floor


def meets_max_cluster_share_ceiling(*, max_cluster_share: float, max_cluster_share_ceiling: float) -> bool:
    """Return whether the max-cluster-share ceiling is satisfied."""

    share = _require_numeric("max_cluster_share", max_cluster_share)
    ceiling = _require_numeric("max_cluster_share_ceiling", max_cluster_share_ceiling)

    if share < _ZERO or share > _ONE:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_share_out_of_range",
            "max_cluster_share must be in [0, 1]",
        )
    if ceiling <= _ZERO or ceiling > _ONE:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_ceiling_out_of_range",
            "max_cluster_share_ceiling must be in (0, 1]",
        )

    return share <= ceiling


def compute_diversity_floor_penalty(
    *,
    distinct_clusters: float,
    distinct_cluster_floor: float,
    max_cluster_share: float,
    max_cluster_share_ceiling: float,
) -> float:
    """Compute bounded diversity-floor penalty score in [0, 1]."""

    distinct = _require_numeric("distinct_clusters", distinct_clusters)
    floor = _require_positive("distinct_cluster_floor", distinct_cluster_floor)
    share = _require_numeric("max_cluster_share", max_cluster_share)
    ceiling = _require_numeric("max_cluster_share_ceiling", max_cluster_share_ceiling)

    if distinct < _ZERO:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_negative_distinct_clusters",
            "distinct_clusters must be >= 0",
        )
    if share < _ZERO or share > _ONE:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_share_out_of_range",
            "max_cluster_share must be in [0, 1]",
        )
    if ceiling <= _ZERO or ceiling > _ONE:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_ceiling_out_of_range",
            "max_cluster_share_ceiling must be in (0, 1]",
        )

    floor_deficit = max(_ZERO, (floor - distinct) / floor)
    concentration_excess = max(_ZERO, (share - ceiling) / ceiling)

    penalty = (Decimal("0.6") * floor_deficit) + (Decimal("0.4") * concentration_excess)
    return _score(max(_ZERO, min(_ONE, penalty)))
