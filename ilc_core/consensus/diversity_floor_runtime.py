"""CDL-V3 diversity-floor runtime.

Deterministic cluster-diversity helpers with bounded penalty scoring and
machine-auditable validation tokens.
"""

from __future__ import annotations

from ilc_core.identity.sybil_resistance_runtime import CDL_V2_DEPENDENCY

CDL_V3_RUNTIME_VERSION = "cdl_v3_diversity_floor_runtime_397.v0.1"
CDL_V3_DEPENDENCY = "cdl_v3_diversity_floor_397.v0.1"


class DiversityFloorValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_numeric(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_invalid_numeric",
            f"{name} must be a numeric value",
        )
    return float(value)


def _require_positive(name: str, value: float) -> float:
    number = _require_numeric(name, value)
    if number <= 0.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_non_positive",
            f"{name} must be > 0",
        )
    return number


def compute_max_cluster_share(*, largest_cluster_slots: float, total_panel_slots: float) -> float:
    """Compute max cluster share in [0, 1] from panel slot counts."""

    largest = _require_numeric("largest_cluster_slots", largest_cluster_slots)
    total = _require_positive("total_panel_slots", total_panel_slots)

    if largest < 0.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_negative_largest_cluster",
            "largest_cluster_slots must be >= 0",
        )
    if largest > total:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_cluster_exceeds_total",
            "largest_cluster_slots cannot exceed total_panel_slots",
        )

    return round(largest / total, 12)


def meets_distinct_cluster_floor(*, distinct_clusters: float, distinct_cluster_floor: float) -> bool:
    """Return whether the distinct-cluster floor is satisfied."""

    distinct = _require_numeric("distinct_clusters", distinct_clusters)
    floor = _require_positive("distinct_cluster_floor", distinct_cluster_floor)

    if distinct < 0.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_negative_distinct_clusters",
            "distinct_clusters must be >= 0",
        )

    return distinct >= floor


def meets_max_cluster_share_ceiling(*, max_cluster_share: float, max_cluster_share_ceiling: float) -> bool:
    """Return whether the max-cluster-share ceiling is satisfied."""

    share = _require_numeric("max_cluster_share", max_cluster_share)
    ceiling = _require_numeric("max_cluster_share_ceiling", max_cluster_share_ceiling)

    if share < 0.0 or share > 1.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_share_out_of_range",
            "max_cluster_share must be in [0, 1]",
        )
    if ceiling <= 0.0 or ceiling > 1.0:
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

    if distinct < 0.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_negative_distinct_clusters",
            "distinct_clusters must be >= 0",
        )
    if share < 0.0 or share > 1.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_share_out_of_range",
            "max_cluster_share must be in [0, 1]",
        )
    if ceiling <= 0.0 or ceiling > 1.0:
        raise DiversityFloorValidationError(
            "cdl_v3_diversity_floor_ceiling_out_of_range",
            "max_cluster_share_ceiling must be in (0, 1]",
        )

    floor_deficit = max(0.0, (floor - distinct) / floor)
    concentration_excess = max(0.0, (share - ceiling) / ceiling)

    penalty = (0.6 * floor_deficit) + (0.4 * concentration_excess)
    return round(max(0.0, min(1.0, penalty)), 12)
