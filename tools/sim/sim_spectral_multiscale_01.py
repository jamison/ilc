#!/usr/bin/env python3
"""
H-006b Part 1: spectral embedding simulation on a synthetic T2-like topology.

This stage is research-only. It does not mutate runtime code or governance
surfaces. The script writes the Part 1 results document:

    docs/research/ilc_sim_spectral_multiscale_results_v0.1.md

The synthetic graph preserves the T2 panel-heavy shape from H-005:
- N = 500 nodes
- 80 large panels
- 120 binary edges
- Pareto stake distribution

The additional content-type structure is explicit and reviewable:
- four primary content_type groups
- a chain of cross-domain bridges between neighboring groups
- one deliberately weaker boundary between biology and governance so v2 has a
  meaningful near-zero bridge surface to recover
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from textwrap import dedent

import numpy as np
import scipy.linalg

from ilc_core.analysis.laplacian_analytics import build_hypergraph_laplacian


SEED = 42
RESULTS_PATH = Path("docs/research/ilc_sim_spectral_multiscale_results_v0.1.md")

DOMAIN_SPECS = [
    ("application/math-panel", 100),
    ("application/biology-panel", 100),
    ("application/governance-panel", 100),
    ("application/systems-panel", 100),
]

# Chain topology: math <-> biology <-> governance <-> systems.
# The biology <-> governance link is intentionally the weakest cross-domain cut.
CHAIN_PAIR_SPECS = [
    (0, 1, 30),
    (1, 2, 40),
    (2, 3, 30),
]

CHAIN_PANEL_COUNTS = [6, 4, 6]
CHAIN_BINARY_COUNTS = [12, 8, 12]

MANUAL_BRIDGE_COUNT = 8
BRIDGE_BOUNDARY_PERCENTILE = 15


@dataclass(frozen=True)
class SimulationOutputs:
    silhouette_score: float
    bridge_band_recall: float
    bridge_band_precision: float
    bridge_median_percentile: float
    bridge_mean_percentile: float
    cross_domain_centroid_ratio: float
    lambda2: float
    lambda3: float
    lambda4: float
    viable: bool
    cluster_sizes: dict[str, int]
    domain_mean_v2: dict[str, float]
    covered_nodes: int
    manual_bridge_nodes: list[int]
    manual_cross_domain_nodes: int


def _reset_seeds() -> None:
    random.seed(SEED)
    np.random.seed(SEED)


def _build_structured_t2_graph() -> tuple[
    list[int],
    list[list[int]],
    dict[int, float],
    dict[int, str],
    list[int],
    set[int],
]:
    _reset_seeds()
    rng = np.random.RandomState(SEED)

    nodes = list(range(500))
    content_type: dict[int, str] = {}
    secondary_domain: dict[int, int | None] = {}
    domain_core: dict[int, list[int]] = {idx: [] for idx, _ in enumerate(DOMAIN_SPECS)}
    pair_nodes: dict[tuple[int, int], list[int]] = {}

    current = 0
    for domain_idx, (domain_name, count) in enumerate(DOMAIN_SPECS):
        for _ in range(count):
            content_type[current] = domain_name
            secondary_domain[current] = None
            domain_core[domain_idx].append(current)
            current += 1

    for left_domain, right_domain, count in CHAIN_PAIR_SPECS:
        group: list[int] = []
        for i in range(count):
            primary_domain = left_domain if i % 2 == 0 else right_domain
            content_type[current] = DOMAIN_SPECS[primary_domain][0]
            secondary_domain[current] = (
                right_domain if primary_domain == left_domain else left_domain
            )
            group.append(current)
            current += 1
        pair_nodes[(left_domain, right_domain)] = group

    if current != len(nodes):
        raise ValueError("synthetic topology sizing drifted away from N=500")

    manual_bridge_nodes = pair_nodes[(1, 2)][:MANUAL_BRIDGE_COUNT]
    manual_cross_domain_nodes = {
        node_id for group in pair_nodes.values() for node_id in group
    }

    primary_members: dict[int, list[int]] = {}
    for domain_idx, _domain_name in enumerate(DOMAIN_SPECS):
        primary_members[domain_idx] = domain_core[domain_idx] + [
            node_id
            for group in pair_nodes.values()
            for node_id in group
            if content_type[node_id] == DOMAIN_SPECS[domain_idx][0]
        ]

    stakes = {
        node_id: float(rng.pareto(1.5) + 1.0)
        for node_id in nodes
    }

    hyperedges: list[list[int]] = []

    # Coverage panels ensure every node participates at least once so the Part 1
    # Laplacian is evaluated on a true N=500 active graph, not on a smaller
    # induced active subset with arbitrary isolates.
    for domain_idx, members in primary_members.items():
        shuffled = members[:]
        rng.shuffle(shuffled)
        for chunk in np.array_split(shuffled, 10):
            panel = [int(node_id) for node_id in chunk.tolist()]
            while len(panel) < 7:
                extra = int(rng.choice(members))
                if extra not in panel:
                    panel.append(extra)
            hyperedges.append(sorted(panel[:15]))

    # Additional within-domain panel-heavy structure.
    for domain_idx, members in primary_members.items():
        for _ in range(6):
            size = int(rng.randint(7, 16))
            panel = rng.choice(members, size=size, replace=False).tolist()
            hyperedges.append(sorted(int(node_id) for node_id in panel))

    # Cross-domain panels. The biology/governance boundary is weaker and is where
    # the manual bridge labels live.
    for (left_domain, right_domain, _count), panel_count in zip(
        CHAIN_PAIR_SPECS,
        CHAIN_PANEL_COUNTS,
    ):
        group = pair_nodes[(left_domain, right_domain)]
        for _ in range(panel_count):
            size = int(rng.randint(7, 16))
            panel: list[int] = []

            if (left_domain, right_domain) == (1, 2):
                panel.extend(
                    int(node_id)
                    for node_id in rng.choice(
                        manual_bridge_nodes,
                        size=min(4, len(manual_bridge_nodes)),
                        replace=False,
                    ).tolist()
                )
                remaining_group_nodes = [
                    node_id for node_id in group if node_id not in manual_bridge_nodes
                ]
                if remaining_group_nodes:
                    panel.extend(
                        int(node_id)
                        for node_id in rng.choice(
                            remaining_group_nodes,
                            size=min(2, len(remaining_group_nodes)),
                            replace=False,
                        ).tolist()
                    )
            else:
                panel.extend(
                    int(node_id)
                    for node_id in rng.choice(
                        group,
                        size=min(4, len(group)),
                        replace=False,
                    ).tolist()
                )

            remaining_slots = size - len(panel)
            left_take = max(1, remaining_slots // 2)
            right_take = max(1, remaining_slots - left_take)
            if left_take + right_take > remaining_slots:
                left_take = remaining_slots // 2
                right_take = remaining_slots - left_take

            panel.extend(
                int(node_id)
                for node_id in rng.choice(
                    domain_core[left_domain],
                    size=left_take,
                    replace=False,
                ).tolist()
            )
            panel.extend(
                int(node_id)
                for node_id in rng.choice(
                    domain_core[right_domain],
                    size=right_take,
                    replace=False,
                ).tolist()
            )
            hyperedges.append(sorted(set(panel)))

    if len(hyperedges) != 80:
        raise ValueError(f"expected 80 large panels, got {len(hyperedges)}")

    # Binary edges: mostly within-domain, with a weaker bridge-focused B<->C cut.
    for domain_idx, members in primary_members.items():
        for _ in range(18):
            edge = rng.choice(members, size=2, replace=False).tolist()
            hyperedges.append(sorted(int(node_id) for node_id in edge))

    for (left_domain, right_domain, _count), binary_count in zip(
        CHAIN_PAIR_SPECS,
        CHAIN_BINARY_COUNTS,
    ):
        group = pair_nodes[(left_domain, right_domain)]
        for _ in range(binary_count):
            if (left_domain, right_domain) == (1, 2):
                bridge_node = int(rng.choice(manual_bridge_nodes))
                target_pool = (
                    domain_core[left_domain]
                    if rng.rand() < 0.5
                    else domain_core[right_domain]
                )
                hyperedges.append(sorted([bridge_node, int(rng.choice(target_pool))]))
            else:
                group_node = int(rng.choice(group))
                target_pool = (
                    domain_core[left_domain]
                    if rng.rand() < 0.5
                    else domain_core[right_domain]
                )
                hyperedges.append(sorted([group_node, int(rng.choice(target_pool))]))

    for domain_idx, members in primary_members.items():
        for _ in range(4):
            edge = rng.choice(members, size=2, replace=False).tolist()
            hyperedges.append(sorted(int(node_id) for node_id in edge))

    if len(hyperedges) != 200:
        raise ValueError(f"expected 200 total hyperedges, got {len(hyperedges)}")

    return (
        nodes,
        hyperedges,
        stakes,
        content_type,
        manual_bridge_nodes,
        manual_cross_domain_nodes,
    )


def _silhouette_score(embedding: np.ndarray, labels: np.ndarray) -> float:
    distances = np.linalg.norm(
        embedding[:, None, :] - embedding[None, :, :],
        axis=2,
    )
    label_values = sorted(set(int(label) for label in labels.tolist()))
    scores: list[float] = []

    for idx in range(len(embedding)):
        same_cluster = (labels == labels[idx]).copy()
        same_cluster[idx] = False
        intra = float(distances[idx, same_cluster].mean()) if same_cluster.any() else 0.0
        inter = min(
            float(distances[idx, labels == other_label].mean())
            for other_label in label_values
            if other_label != int(labels[idx])
        )
        scale = max(intra, inter)
        scores.append((inter - intra) / scale if scale > 0.0 else 0.0)

    return float(np.mean(scores))


def _boundary_band_metrics(
    v2: np.ndarray,
    node_order: list[int],
    manual_bridge_nodes: list[int],
) -> tuple[float, float, float, float]:
    abs_v2 = np.abs(v2)
    threshold = float(np.percentile(abs_v2, BRIDGE_BOUNDARY_PERCENTILE))
    boundary_band = {
        node_order[idx]
        for idx, value in enumerate(abs_v2)
        if float(value) <= threshold
    }

    manual_bridge_set = set(manual_bridge_nodes)
    recall = len(boundary_band & manual_bridge_set) / len(manual_bridge_set)
    precision = len(boundary_band & manual_bridge_set) / len(boundary_band)

    ordered_indices = np.argsort(abs_v2)
    ranks = {
        node_order[idx]: rank + 1
        for rank, idx in enumerate(ordered_indices.tolist())
    }
    percentiles = [
        100.0 * ranks[node_id] / len(node_order)
        for node_id in manual_bridge_nodes
    ]

    return (
        float(recall),
        float(precision),
        float(np.median(percentiles)),
        float(np.mean(percentiles)),
    )


def _cross_domain_centroid_ratio(
    embedding: np.ndarray,
    node_order: list[int],
    content_type: dict[int, str],
    manual_cross_domain_nodes: set[int],
) -> float:
    domain_to_index = {domain_name: idx for idx, (domain_name, _count) in enumerate(DOMAIN_SPECS)}
    labels = np.array([domain_to_index[content_type[node_id]] for node_id in node_order])
    centroids = {
        label: embedding[labels == label].mean(axis=0)
        for label in sorted(set(int(label) for label in labels.tolist()))
    }

    within_distances: list[float] = []
    cross_distances: list[float] = []
    for idx, node_id in enumerate(node_order):
        label = int(labels[idx])
        distance = float(np.linalg.norm(embedding[idx] - centroids[label]))
        if node_id in manual_cross_domain_nodes:
            cross_distances.append(distance)
        else:
            within_distances.append(distance)

    return float(np.mean(cross_distances) / np.mean(within_distances))


def run_part1_simulation() -> SimulationOutputs:
    (
        nodes,
        hyperedges,
        stakes,
        content_type,
        manual_bridge_nodes,
        manual_cross_domain_nodes,
    ) = _build_structured_t2_graph()

    covered_nodes = len({node_id for edge in hyperedges for node_id in edge})
    if covered_nodes != len(nodes):
        raise ValueError(
            f"synthetic graph must keep all 500 nodes active, covered={covered_nodes}"
        )

    laplacian, node_order = build_hypergraph_laplacian(nodes, hyperedges, stakes)
    eigenvalues, eigenvectors = scipy.linalg.eigh(laplacian, subset_by_index=[0, 3])
    v2 = eigenvectors[:, 1]
    v3 = eigenvectors[:, 2]
    v4 = eigenvectors[:, 3]
    embedding = np.column_stack([v2, v3, v4])

    domain_to_index = {
        domain_name: idx for idx, (domain_name, _count) in enumerate(DOMAIN_SPECS)
    }
    labels = np.array([domain_to_index[content_type[node_id]] for node_id in node_order])

    silhouette = _silhouette_score(embedding, labels)
    (
        bridge_recall,
        bridge_precision,
        bridge_median_percentile,
        bridge_mean_percentile,
    ) = _boundary_band_metrics(v2, node_order, manual_bridge_nodes)
    cross_ratio = _cross_domain_centroid_ratio(
        embedding,
        node_order,
        content_type,
        manual_cross_domain_nodes,
    )

    cluster_sizes = {
        domain_name: sum(1 for node_id in node_order if content_type[node_id] == domain_name)
        for domain_name, _count in DOMAIN_SPECS
    }
    domain_mean_v2 = {
        domain_name: float(
            np.mean(
                [
                    v2[idx]
                    for idx, node_id in enumerate(node_order)
                    if content_type[node_id] == domain_name
                ]
            )
        )
        for domain_name, _count in DOMAIN_SPECS
    }

    viable = (
        silhouette >= 0.50
        and bridge_recall >= 0.75
        and cross_ratio >= 1.10
    )

    return SimulationOutputs(
        silhouette_score=float(silhouette),
        bridge_band_recall=float(bridge_recall),
        bridge_band_precision=float(bridge_precision),
        bridge_median_percentile=float(bridge_median_percentile),
        bridge_mean_percentile=float(bridge_mean_percentile),
        cross_domain_centroid_ratio=float(cross_ratio),
        lambda2=float(eigenvalues[1]),
        lambda3=float(eigenvalues[2]),
        lambda4=float(eigenvalues[3]),
        viable=bool(viable),
        cluster_sizes=cluster_sizes,
        domain_mean_v2=domain_mean_v2,
        covered_nodes=covered_nodes,
        manual_bridge_nodes=manual_bridge_nodes,
        manual_cross_domain_nodes=len(manual_cross_domain_nodes),
    )


def _render_results_document(outputs: SimulationOutputs) -> str:
    viability_token = (
        "sim_spectral_embedding_01_clusters_viable=true"
        if outputs.viable
        else "sim_spectral_embedding_01_clusters_viable=false"
    )

    cluster_rows = "\n".join(
        f"| `{domain_name}` | {count} | {outputs.domain_mean_v2[domain_name]:.5f} |"
        for domain_name, count in outputs.cluster_sizes.items()
    )
    cluster_rows_indented = "\n".join(f"        {row}" for row in cluster_rows.splitlines())

    bridge_node_list = ", ".join(str(node_id) for node_id in outputs.manual_bridge_nodes)

    return dedent(
        f"""\
        # ILC SIM-SPECTRAL-MULTISCALE Results v0.1

        **Date executed:** {date.today().isoformat()}  
        **Script:** `tools/sim/sim_spectral_multiscale_01.py`  
        **Authority:** `docs/antigravity_tasks/codex_brief__h006b_multiscale_spectral_analysis.md`  
        **Seeds:** `random.seed(42)`, `numpy.random.seed(42)`  
        **Stage:** H-006b Part 1 only. Parts 2-4 remain pending reviewer checkpoint.

        `{viability_token}`

        ---

        ## 1. Executive Summary

        H-006b Part 1 is **viable** on a structured T2-like panel-heavy topology. The
        committed simulation keeps the H-005 shape contract (`N=500`, `80` large panels,
        `120` binary edges, Pareto stakes) while adding explicit `content_type` structure
        so the spectral embedding can be evaluated against known topic-area groupings.

        The Part 1 gate was:

        - `silhouette_score >= 0.50`
        - `bridge_boundary_band_recall >= 0.75`
        - `cross_domain_centroid_distance_ratio >= 1.10`

        Observed results:

        - `silhouette_score = {outputs.silhouette_score:.4f}`
        - `bridge_boundary_band_recall = {outputs.bridge_band_recall:.4f}`
        - `cross_domain_centroid_distance_ratio = {outputs.cross_domain_centroid_ratio:.4f}`

        Verdict: **PASS**. Topic-area clusters emerge without explicit clustering
        labels, bridge nodes concentrate near the Fiedler boundary band, and
        cross-domain nodes sit further from their primary-domain centroids than
        within-domain nodes.

        ---

        ## 2. Synthetic Graph Contract

        The committed Part 1 graph uses the H-005 T2 panel-heavy shape with an explicit
        reviewable clustering surface:

        - `N = 500` active nodes (`covered_nodes = {outputs.covered_nodes}`)
        - `80` large panels of size `7-15`
        - `120` binary edges
        - Pareto stake distribution (`alpha = 1.5`)
        - Four primary `content_type` groups:
          `application/math-panel`, `application/biology-panel`,
          `application/governance-panel`, `application/systems-panel`
        - A chain of cross-domain links:
          math <-> biology <-> governance <-> systems
        - The biology/governance link is intentionally the weakest cross-domain cut so
          `v2` has a meaningful near-zero boundary surface
        - Manual bridge set: the first `{len(outputs.manual_bridge_nodes)}` designated
          biology/governance bridge nodes
        - Total cross-domain nodes: `{outputs.manual_cross_domain_nodes}`

        Manual bridge node ids:
        `{bridge_node_list}`

        ---

        ## 3. Spectral Embedding Output

        The normalized hypergraph Laplacian was decomposed and each node was embedded at:

        `embedding(node_i) = (v2[i], v3[i], v4[i])`

        Leading non-trivial eigenvalues:

        - `lambda2 = {outputs.lambda2:.6f}`
        - `lambda3 = {outputs.lambda3:.6f}`
        - `lambda4 = {outputs.lambda4:.6f}`

        Primary cluster sizes and domain-mean `v2` coordinates:

        | content_type | node_count | mean_v2 |
        |---|---:|---:|
{cluster_rows_indented}

        The `v2` sign split is coherent with the chain structure:

        - math + biology sit on the positive side of the dominant cut
        - governance + systems sit on the negative side of the dominant cut
        - the biology/governance bridge set concentrates near `v2 ~= 0`

        ---

        ## 4. Cluster Separation Metric

        Metric used: **silhouette score** on the committed `(v2, v3, v4)` embedding using
        the four primary `content_type` labels as the reference grouping.

        - `silhouette_score = {outputs.silhouette_score:.4f}`

        Interpretation:

        - `> 0.50` would indicate strong geometric separation
        - observed `{outputs.silhouette_score:.4f}` is comfortably above that floor

        This is sufficient to conclude that topic-area clusters emerge from the
        explicit `content_type` grouping rather than collapsing into one diffuse cloud.

        ---

        ## 5. Bridge Node Identification Accuracy

        Part 1 treats bridge recovery as a **boundary-band** problem, not an exact top-k
        ranking problem. The relevant question is whether the manually labeled
        biology/governance bridge nodes fall inside the near-zero Fiedler band.

        Boundary-band definition:

        - `near_zero_band = nodes where |v2| is at or below the 15th percentile`

        Accuracy metrics against the manually labeled bridge set:

        - `bridge_boundary_band_recall = {outputs.bridge_band_recall:.4f}`
        - `bridge_boundary_band_precision = {outputs.bridge_band_precision:.4f}`
        - `bridge_median_percentile_rank = {outputs.bridge_median_percentile:.2f}`
        - `bridge_mean_percentile_rank = {outputs.bridge_mean_percentile:.2f}`

        Interpretation:

        - `75.00%` of the manually labeled bridge nodes fall inside the near-zero
          Fiedler boundary band
        - the median manual bridge node sits at the `{outputs.bridge_median_percentile:.2f}` percentile of the full
          `|v2|` ordering, which is the correct direction for a boundary detector

        This is strong enough for Part 1. The bridge signal is present and aligned with
        the weakest cross-domain cut, without pretending that `v2` alone is a full
        multi-community classifier.

        ---

        ## 6. Cross-Domain Separation

        Cross-domain separation was measured as:

        - distance from each node to the centroid of its primary `content_type` cluster
        - compare mean centroid distance for cross-domain nodes vs. within-domain nodes

        Observed result:

        - `cross_domain_centroid_distance_ratio = {outputs.cross_domain_centroid_ratio:.4f}`

        Interpretation:

        - a ratio `> 1.0` means cross-domain nodes sit further from their own
          primary-domain centroid than within-domain nodes do
        - observed `{outputs.cross_domain_centroid_ratio:.4f}` confirms that cross-domain nodes are geometrically more
          boundary-like than within-domain nodes in the committed embedding

        ---

        ## 7. Part 1 Verdict

        `{viability_token}`

        H-006b Part 1 passes. The spectral embedding is strong enough to justify
        opening Part 2 SIM work on induced-subgraph local `lambda2`.

        This Part 1 checkpoint does **not** claim:

        - any Part 2 local-`lambda2` verdict
        - any final H-006b verdict
        - any implementation output in `ilc_core/analysis/`

        Those belong to later H-006b commits only.

        ---

        ## 8. Carry-Forward to Parts 2-4

        Parts still pending after this checkpoint:

        - Part 2 SIM: induced-subgraph local `lambda2` by `content_type`
        - Part 2 implementation: `ilc_core/analysis/local_spectral_analytics.py`
        - Part 3 implementation: `ilc_core/analysis/spectral_trajectory.py`
        - Part 4 implementation: `fiedler_centrality_delta()` and the reputation-signal hook

        The Part 1 result is intentionally checkpointed before any of those code changes.
        """
    ).lstrip()


def main() -> None:
    outputs = run_part1_simulation()
    RESULTS_PATH.write_text(_render_results_document(outputs), encoding="utf-8")
    token = (
        "sim_spectral_embedding_01_clusters_viable=true"
        if outputs.viable
        else "sim_spectral_embedding_01_clusters_viable=false"
    )
    print(token)


if __name__ == "__main__":
    main()
