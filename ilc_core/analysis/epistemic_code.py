# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class TargetEpistemicConfig:
    """
    Target epistemic configuration for a namespace.

    These fields are deliberately simple for the MVP. They can be extended later.
    """
    # Desired average validation depth for claims in this namespace.
    target_avg_validation_depth: float = 1.0

    # Maximum acceptable fraction of claims that are in contradiction hotspots.
    max_contradiction_density: float = 0.1

    # Minimum acceptable ratio of cross-namespace links (optional cohesion proxy).
    min_crosslink_ratio: float = 0.0


@dataclass
class NamespaceStats:
    """
    Observed epistemic statistics for a namespace.

    These can be derived from the current graph + KPIs module.
    """
    avg_validation_depth: float
    contradiction_density: float
    crosslink_ratio: float


def compute_config_error(
    target: TargetEpistemicConfig,
    stats: NamespaceStats,
) -> Dict[str, float]:
    """
    Compare NamespaceStats against the TargetEpistemicConfig.

    Returns a small dict of error terms:
      - validation_depth_error: actual - target
      - contradiction_overflow: max(0, actual - max_allowed)
      - crosslink_deficit: max(0, min_required - actual)
    """
    errors: Dict[str, float] = {}

    errors["validation_depth_error"] = (
        stats.avg_validation_depth - target.target_avg_validation_depth
    )

    # Only count 'overflow' of contradiction density above the max.
    if stats.contradiction_density > target.max_contradiction_density:
        errors["contradiction_overflow"] = (
            stats.contradiction_density - target.max_contradiction_density
        )
    else:
        errors["contradiction_overflow"] = 0.0

    # Only count 'deficit' when crosslink_ratio is below the minimum.
    if stats.crosslink_ratio < target.min_crosslink_ratio:
        errors["crosslink_deficit"] = (
            target.min_crosslink_ratio - stats.crosslink_ratio
        )
    else:
        errors["crosslink_deficit"] = 0.0

    return errors
