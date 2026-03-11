"""CDL-V3/V7 consensus runtime package."""

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
from .popperian_gate_runtime import (
    CDL_V7_DEPENDENCY,
    CDL_V7_RUNTIME_VERSION,
    PopperianGateValidationError,
    evaluate_decomposition_admissibility,
    is_claim_form_admissible,
    meets_reproducibility_threshold,
    passes_falsifiability_gate,
    reject_inadmissible_counterexample,
)

__all__ = [
    "CDL_V3_RUNTIME_VERSION",
    "CDL_V3_DEPENDENCY",
    "CDL_V2_DEPENDENCY",
    "CDL_V7_RUNTIME_VERSION",
    "CDL_V7_DEPENDENCY",
    "DiversityFloorValidationError",
    "PopperianGateValidationError",
    "compute_max_cluster_share",
    "meets_distinct_cluster_floor",
    "meets_max_cluster_share_ceiling",
    "compute_diversity_floor_penalty",
    "is_claim_form_admissible",
    "passes_falsifiability_gate",
    "reject_inadmissible_counterexample",
    "meets_reproducibility_threshold",
    "evaluate_decomposition_admissibility",
]
