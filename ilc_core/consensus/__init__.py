"""CDL-V3 consensus runtime package."""

from .diversity_floor_runtime import (
    CDL_V2_DEPENDENCY,
    CDL_V3_DEPENDENCY,
    CDL_V3_RUNTIME_VERSION,
    DiversityFloorValidationError,
    compute_diversity_floor_penalty,
    compute_max_cluster_share,
    meets_distinct_cluster_floor,
    meets_max_cluster_share_ceiling,
)

__all__ = [
    "CDL_V3_RUNTIME_VERSION",
    "CDL_V3_DEPENDENCY",
    "CDL_V2_DEPENDENCY",
    "DiversityFloorValidationError",
    "compute_max_cluster_share",
    "meets_distinct_cluster_floor",
    "meets_max_cluster_share_ceiling",
    "compute_diversity_floor_penalty",
]
