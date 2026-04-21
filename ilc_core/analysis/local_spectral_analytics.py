"""H-006b Part 2: local lambda2 analytics by content_type."""

from __future__ import annotations

from typing import Dict, Sequence

from ilc_core.analysis.laplacian_analytics import (
    LaplacianError,
    build_hypergraph_laplacian,
    compute_fiedler,
)


def compute_local_lambda2(
    nodes: Sequence[str],
    hyperedges: Sequence[Sequence[str]],
    stakes: Dict[str, float],
    content_type_map: Dict[str, str],
) -> Dict[str, float]:
    """Return content_type -> induced-subgraph lambda2.

    The induced subgraph for a content_type includes only nodes with that
    content_type and only hyperedges whose members all belong to that cluster.
    Clusters with fewer than two nodes or no internal non-degenerate hyperedges
    return 0.0.

    Raises:
        LaplacianError: if a hyperedge references a node outside ``nodes`` or if
        a node in ``nodes`` has no content_type assignment.
    """

    node_list = list(nodes)
    if not node_list:
        return {}

    node_set = set(node_list)
    for edge in hyperedges:
        for member in edge:
            if member not in node_set:
                raise LaplacianError(
                    f"hyperedge member '{member}' is not in the node list"
                )

    cluster_members: dict[str, list[str]] = {}
    for node_id in node_list:
        if node_id not in content_type_map:
            raise LaplacianError(f"node '{node_id}' is missing from content_type_map")
        cluster_members.setdefault(content_type_map[node_id], []).append(node_id)

    results: dict[str, float] = {}
    for content_type, members in cluster_members.items():
        member_set = set(members)
        internal_hyperedges = [
            list(edge)
            for edge in hyperedges
            if len(edge) >= 2 and all(member in member_set for member in edge)
        ]
        if len(members) < 2 or not internal_hyperedges:
            results[content_type] = 0.0
            continue

        laplacian, _ordered_nodes = build_hypergraph_laplacian(
            members,
            internal_hyperedges,
            stakes,
        )
        lambda2, _fiedler = compute_fiedler(laplacian)
        results[content_type] = float(lambda2)

    return results
