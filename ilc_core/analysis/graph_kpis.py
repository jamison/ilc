# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, List

from ilc_core.graph import EpistemicGraph
from ilc_core.types import LinkRecord
from ilc_core.protocol.params import ProtocolParams

@dataclass
class ClaimLinkStats:
    claim_id: str
    supports_in: int = 0
    refutes_in: int = 0
    equivalent_in: int = 0
    depends_on_in: int = 0

    @property
    def net_support(self) -> int:
        return self.supports_in - self.refutes_in

    @property
    def is_controversial(self) -> bool:
        return self.supports_in > 0 and self.refutes_in > 0

def compute_claim_link_stats(graph: EpistemicGraph) -> Dict[str, ClaimLinkStats]:
    """
    Compute per-claim link statistics based on incoming links.

    For each claim_id that appears as a target of any LinkRecord,
    count incoming supports/refutes/equivalent/depends_on links.
    """
    stats: Dict[str, ClaimLinkStats] = {}

    counters = {
        "supports": "supports_in",
        "refutes": "refutes_in",
        "equivalent": "equivalent_in",
        "depends_on": "depends_on_in",
    }

    for link in graph.links.values():
        target_id = link.target_id
        s = stats.setdefault(target_id, ClaimLinkStats(claim_id=target_id))
        field = counters.get(link.link_type)
        if field:
            setattr(s, field, getattr(s, field) + 1)

    return stats

def find_conflict_hotspots(
    graph: EpistemicGraph,
    *,
    min_supports: int = 1,
    min_refutes: int = 1,
) -> Dict[str, ClaimLinkStats]:
    """
    Return claims that have both supports and refutes above the given thresholds.
    """
    stats = compute_claim_link_stats(graph)
    hotspots: Dict[str, ClaimLinkStats] = {}

    for claim_id, s in stats.items():
        if s.supports_in >= min_supports and s.refutes_in >= min_refutes:
            hotspots[claim_id] = s

    return hotspots

def compute_local_influence_scores(
    graph: EpistemicGraph,
    *,
    weight_supports: float = 1.0,
    weight_refutes: float = 1.0,
    weight_equivalent: float = 0.0,
    weight_depends_on: float = 0.0,
) -> Dict[str, float]:
    """
    Compute a simple local influence score for each claim based on incoming links.

    score = + w_s * supports_in
            - w_r * refutes_in
            + w_e * equivalent_in
            + w_d * depends_on_in
    """
    stats = compute_claim_link_stats(graph)
    scores: Dict[str, float] = {}

    for claim_id, s in stats.items():
        score = (
            weight_supports * s.supports_in
            - weight_refutes * s.refutes_in
            + weight_equivalent * s.equivalent_in
            + weight_depends_on * s.depends_on_in
        )
        scores[claim_id] = float(score)

    return scores

def rank_claims_by_influence(
    scores: Dict[str, float],
    *,
    descending: bool = True,
) -> List[Tuple[str, float]]:
    """
    Return a sorted list of (claim_id, score) pairs.

    By default, highest influence first.
    """
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=descending)

def get_local_influence_scores(
    graph: EpistemicGraph,
    params: ProtocolParams,
) -> Dict[str, float]:
    """
    Dispatch to the configured local influence algorithm.

    For now we only support "algo.local_influence.v0_toy", which delegates
    to compute_local_influence_scores with the configured weights.
    """
    algo_id = params.local_influence_algorithm_id

    if algo_id == "algo.local_influence.v0_toy":
        return compute_local_influence_scores(
            graph,
            weight_supports=params.weight_supports,
            weight_refutes=params.weight_refutes,
            weight_equivalent=params.weight_equivalent,
            weight_depends_on=params.weight_depends_on,
        )

    # Future: add additional algorithms and selection logic here.
    raise ValueError(f"Unsupported local_influence_algorithm_id: {algo_id!r}")
