from dataclasses import dataclass
from typing import Dict, Iterable

from ilc_core.graph import EpistemicGraph
from ilc_core.types import LinkRecord

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

    # Iterate over all links stored in the graph
    for link in graph.links.values():
        target_id = link.target_id
        s = stats.setdefault(
            target_id,
            ClaimLinkStats(claim_id=target_id),
        )
        if link.link_type == "supports":
            s.supports_in += 1
        elif link.link_type == "refutes":
            s.refutes_in += 1
        elif link.link_type == "equivalent":
            s.equivalent_in += 1
        elif link.link_type == "depends_on":
            s.depends_on_in += 1

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
