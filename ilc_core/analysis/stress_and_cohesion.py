# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
from typing import Dict

from ilc_core.analysis.epistemic_code import (
    TargetEpistemicConfig,
    NamespaceStats,
    compute_config_error,
)
from ilc_core.analysis.graph_kpis import (
    compute_claim_link_stats,
    find_conflict_hotspots,
    get_local_influence_scores,
)
from ilc_core.graph import EpistemicGraph
from ilc_core.protocol.params import ProtocolParams

@dataclass
class EpistemicStress:
    namespace_id: str
    validation_depth_error: float
    contradiction_overflow: float
    crosslink_deficit: float
    total_stress: float

@dataclass
class CohesionMetrics:
    namespace_id: str
    support_ratio: float
    controversy_ratio: float
    mean_abs_influence: float
    cohesion_score: float

def compute_epistemic_stress(
    namespace_id: str,
    target: TargetEpistemicConfig,
    stats: NamespaceStats,
    *,
    weight_validation: float = 1.0,
    weight_contradiction: float = 1.0,
    weight_crosslink: float = 1.0,
) -> EpistemicStress:
    """
    Turn config error into a simple scalar stress score plus components.

    total_stress is a weighted L1-like combination:
        |validation_depth_error| * w_v
      + contradiction_overflow * w_c
      + crosslink_deficit * w_x
    """
    errors = compute_config_error(target, stats)
    v_err = float(errors["validation_depth_error"])
    c_over = float(errors["contradiction_overflow"])
    x_def = float(errors["crosslink_deficit"])

    total = (
        abs(v_err) * weight_validation
        + c_over * weight_contradiction
        + x_def * weight_crosslink
    )

    return EpistemicStress(
        namespace_id=namespace_id,
        validation_depth_error=v_err,
        contradiction_overflow=c_over,
        crosslink_deficit=x_def,
        total_stress=float(total),
    )

def compute_cohesion_metrics(
    namespace_id: str,
    graph: EpistemicGraph,
    params: ProtocolParams,
) -> CohesionMetrics:
    """
    Compute a small set of cohesion-related metrics over the claim/link structure:
      - support_ratio: supports / (supports + refutes)
      - controversy_ratio: conflict_hotspots / num_claims_with_links
      - mean_abs_influence: mean |influence_score|
      - cohesion_score: support_ratio * (1 - controversy_ratio)
    """
    link_stats = compute_claim_link_stats(graph)
    hotspots = find_conflict_hotspots(graph)

    total_supports = sum(s.supports_in for s in link_stats.values())
    total_refutes = sum(s.refutes_in for s in link_stats.values())
    denom = total_supports + total_refutes
    support_ratio = float(total_supports / denom) if denom > 0 else 0.0

    num_claims = len(link_stats)
    controversy_ratio = float(len(hotspots) / num_claims) if num_claims > 0 else 0.0

    scores: Dict[str, float] = get_local_influence_scores(graph, params)
    if scores:
        mean_abs_influence = float(
            sum(abs(v) for v in scores.values()) / len(scores)
        )
    else:
        mean_abs_influence = 0.0

    cohesion_score = support_ratio * (1.0 - controversy_ratio)

    return CohesionMetrics(
        namespace_id=namespace_id,
        support_ratio=support_ratio,
        controversy_ratio=controversy_ratio,
        mean_abs_influence=mean_abs_influence,
        cohesion_score=cohesion_score,
    )
