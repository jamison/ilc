# H-006b Part 2 + Part 4: local lambda2 and Fiedler centrality delta analytics.
#
# Gate history:
#   H-006a positive → build_hypergraph_laplacian + compute_fiedler available
#   sim_local_lambda2_viable=true (H-006b Part 2 SIM, commit d76c562e)
#     → implementation cleared; induced-subgraph contract confirmed on N=500 T2-class graph
#   run_h006b_multiscale_spectral_verdict=pass (commit 0e494432)
#
# Authority: docs/antigravity_tasks/codex_brief__h006b_multiscale_spectral_analysis.md §3+§5
# SIM results: docs/research/ilc_sim_spectral_multiscale_results_v0.1.md §§9-12
# ADR-0032 §2.5: sparse-but-healthy vs. near-partition posture note
#
# Induced-subgraph contract (Part 2 §9):
#   For each content_type cluster, local λ₂ is computed on the subgraph formed by
#   keeping only nodes in that cluster AND only hyperedges whose ALL members belong
#   to that cluster. Partial-membership hyperedges are excluded because they couple
#   inter-cluster topology into what must be a cluster-local connectivity measure.
#   Including them would make local λ₂ sensitive to cross-domain structure and
#   break the "mature vs. emerging domain" classification.
#
# Scope: pure Python analytics. No CDL mutations, no EpochSettlementRecord changes,
#   no gossip wiring (H-013 scope after SIM-BEACON-01).

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
    content_type and only hyperedges whose members ALL belong to that cluster
    (partial-membership hyperedges are excluded — see module header).
    Clusters with fewer than two nodes or no internal non-degenerate hyperedges
    return 0.0.

    SIM baseline (N=500, T2-class): local λ₂ ranged 0.124–0.172 across four
    content_type clusters, all >100× above THETA_FLOOR=0.001 (sparse-but-healthy,
    not near-partition). See docs/research/ilc_sim_spectral_multiscale_results_v0.1.md §10.

    Raises:
        LaplacianError: if a hyperedge member is not in ``nodes``, if a node has
        no content_type assignment, or if a node is absent from ``stakes``
        (absent stake is not silently defaulted to zero — that would drop all
        edges for that node from the induced Laplacian without a visible error).
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
        if node_id not in stakes:
            raise LaplacianError(f"node '{node_id}' is missing from stakes")
        cluster_members.setdefault(content_type_map[node_id], []).append(node_id)

    results: dict[str, float] = {}
    for content_type, members in cluster_members.items():
        member_set = set(members)
        # Induced-subgraph filter: keep only hyperedges where every member is in
        # this cluster. A hyperedge spanning two clusters is excluded entirely —
        # it is NOT split or truncated. This preserves the all-or-nothing semantics
        # of the hyperedge weight W(e) = stake_harmonic_mean(members).
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


def fiedler_centrality_delta(
    centrality_t: Dict[str, float],
    centrality_prev: Dict[str, float],
) -> Dict[str, float]:
    """Return per-node delta Fiedler centrality (t minus t-1).

    Missing nodes are treated as ``0.0``. The result includes every node that
    appears in either snapshot.

    Non-redundancy note (H-005 R5 / SIM-SPECTRAL-01): Fiedler centrality
    ``|v2[i]|`` has Pearson ``rho ~= 0.40-0.52`` versus stake-weighted degree on
    T2-class topologies. The delta therefore carries structure that is not
    recoverable from stake changes alone and is a valid reputation input signal.

    Ordering: result keys follow ``centrality_t`` insertion order; nodes
    present only in ``centrality_prev`` are appended after in their insertion
    order.
    """
    all_nodes = list(centrality_t) + [
        n for n in centrality_prev if n not in centrality_t
    ]
    return {
        node_id: centrality_t.get(node_id, 0.0) - centrality_prev.get(node_id, 0.0)
        for node_id in all_nodes
    }
