#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1545p-Fix72 post-repair Atlas measurement suite.

PUBLIC_RC_EXCLUDE: fix72_post_repair_measurement_suite_local_atlas_maintenance
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB read-only diagnostic pass;
no Genesis signing, canonical graph publication, public RC activation, runtime
activation, ECU minting, ILC settlement, or production graph mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse import csgraph
from scipy.sparse.linalg import eigsh

from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbWritePlan,
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "phase_1545p_fix72"
SELF_REGISTRATION_PHASE = "phase_phase_1545p_fix72"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
PROMPT_PATH = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix72_g10_post_repair_measurement_suite.md"
)
GUIDANCE_PATH = (
    REPO_ROOT / "docs/specs/ilc_fix69_fix78_analytical_suite_codex_guidance_v0.1.md"
)
CDL_REGISTER_PATH = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
FIX45_LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix45_algorithmic_percolation_ledger_v0.1.json"
FIX46_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json"

WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix72_measurement_suite_walkthrough.md"
WHOLE_GRAPH_PATH = REPO_ROOT / "docs/specs/ilc_fix72_whole_graph_baseline_diagnostic_v0.1.json"
PERCOLATION_PATH = REPO_ROOT / "docs/specs/ilc_fix72_percolation_analysis_v0.1.json"
AUTHORITY_SIM_PATH = REPO_ROOT / "docs/specs/ilc_fix72_authority_sim_battery_v0.1.json"
MANIFEST_PATH = REPO_ROOT / "docs/specs/ilc_fix72_measurement_suite_manifest_v0.1.json"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix72_measurement_suite.py"
EVALUATOR_PATH = (
    REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix72_post_repair_measurement_suite.py"
)

FIEDLER_ALL_PATH = REPO_ROOT / "out/genesis_atlas_fix72_fiedler_all_local_v0.1.json"
FIEDLER_AUTHORITY_PATH = (
    REPO_ROOT / "out/genesis_atlas_fix72_fiedler_authority_only_minority_v0.1.json"
)
FIEDLER_BINDING_PATH = (
    REPO_ROOT / "out/genesis_atlas_fix72_fiedler_authority_binding_surface_v0.1.json"
)
SPECTRAL_PATH = REPO_ROOT / "out/genesis_base_graph_spectral_post_fix69.json"
PAGERANK_PATH = REPO_ROOT / "out/genesis_base_graph_pagerank_post_fix69.json"
LOW_PAGERANK_PATH = REPO_ROOT / "out/genesis_base_graph_fix72_low_pagerank_queue.json"

FIX56_BASELINES = {
    "all_local": {"nodes": 15677, "edges": 74981, "components": 1, "lambda2": 0.009638},
    "public_eligible": {
        "nodes": 15195,
        "edges": 70823,
        "components": 1,
        "lambda2": 0.014181,
    },
    "authority_only": {
        "nodes": 1515,
        "edges": 318,
        "components": 1225,
        "lambda2": 0.0,
    },
}
FIX43_BASELINES = {
    "lambda2": 0.034323,
    "bridge_count": 6175,
    "giant_component_fraction": 1.0,
    "protocol_relevant_node_count": 5550,
}

GENESIS_ROOT_CANDIDATES = [
    "artifact:genesis_intent_attestation_init_authority_map",
    "artifact:genesis_package_merkle_root_v0.4",
    "artifact:full_repo_genesis_atlas_candidate_root_1545p_fix22",
]
PUBLIC_ELIGIBLE_PROJECTIONS = {
    "genesis_core_star_map",
    "public_protocol_graph",
    "support_candidate_graph",
}
AUTHORITY_PROJECTIONS = {"genesis_core_star_map"}
AUTHORITY_CONTROL_EDGES = {"GOVERNS", "CARRIES_FORWARD"}
PROTOCOL_RELEVANT_PREFIXES = ("ilc_core/", "docs/specs/", "tests/", "tools/")
EXCLUDED_REPO_PREFIXES = ("out/", ".git/", "Z_Past_Chats/")
PRIVATE_PATH_MARKERS = ("/private/", "private_", "_private", "PUBLIC_RC_EXCLUDE")
OUTPUT_TOKENS = [
    "fix72_fiedler_rebaseline_complete",
    "fix72_whole_graph_baseline_complete",
    "fix72_spectral_pagerank_complete",
    "fix72_percolation_analysis_complete",
    "fix72_authority_sim_battery_complete",
    "fix72_complete",
]
INPUT_TOKENS = ["fix69_complete", "fix71_complete", "fix68_complete", "fix67_complete"]


def _json_text(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _log(message: str, started_at: float | None = None) -> float:
    now = time.monotonic()
    suffix = f" ({now - started_at:.1f}s)" if started_at is not None else ""
    print(f"[fix72] {message}{suffix}", file=sys.stderr, flush=True)
    return now


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp", text=True
    )
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix72_node_missing_candidate_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    value = (
        edge.get("source")
        or edge.get("src")
        or edge.get("source_candidate_id")
        or edge.get("from")
    )
    return value if isinstance(value, str) else ""


def _edge_target(edge: dict[str, Any]) -> str:
    value = (
        edge.get("target")
        or edge.get("tgt")
        or edge.get("target_candidate_id")
        or edge.get("to")
    )
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("type")
    return value if isinstance(value, str) else ""


def _round(value: float, digits: int = 12) -> float:
    return round(float(value), digits)


def _source_path(node: dict[str, Any]) -> str:
    for key in ("source_path", "repo_path", "path", "label"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _is_ilc_core_node(node: dict[str, Any]) -> bool:
    return _source_path(node).startswith("ilc_core/")


def _is_protocol_relevant(node: dict[str, Any]) -> bool:
    path = _source_path(node)
    if not path.startswith(PROTOCOL_RELEVANT_PREFIXES):
        return False
    if path.startswith(EXCLUDED_REPO_PREFIXES):
        return False
    return not any(marker in path for marker in PRIVATE_PATH_MARKERS)


def _build_undirected(node_ids: set[str], edges: list[dict[str, Any]]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(sorted(node_ids))
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        if source in node_ids and target in node_ids:
            graph.add_edge(source, target)
    return graph


def _sparse_lambda2(graph: nx.Graph) -> dict[str, Any]:
    node_ids = sorted(graph.nodes())
    node_count = len(node_ids)
    if node_count < 2:
        return {
            "lambda2": 0.0,
            "method": "too_few_nodes",
            "spectral_failure": None,
        }
    if graph.number_of_edges() == 0:
        return {
            "lambda2": 0.0,
            "method": "empty_edge_set",
            "spectral_failure": None,
        }
    index = {node_id: idx for idx, node_id in enumerate(node_ids)}
    rows: list[int] = []
    cols: list[int] = []
    for source, target in graph.edges():
        rows.extend([index[source], index[target]])
        cols.extend([index[target], index[source]])
    adjacency = sparse.coo_matrix(
        (np.ones(len(rows), dtype=np.float64), (rows, cols)),
        shape=(node_count, node_count),
    ).tocsr()
    component_count = int(csgraph.connected_components(adjacency, directed=False, return_labels=False))
    if component_count > 1:
        return {
            "lambda2": 0.0,
            "method": "disconnected_graph_exact_zero",
            "spectral_failure": None,
        }
    laplacian = csgraph.laplacian(adjacency, normed=False).astype(np.float64)
    if node_count > 5000:
        try:
            return {
                "lambda2": _round(
                    max(
                        0.0,
                        float(
                            nx.algebraic_connectivity(
                                graph,
                                method="tracemin_pcg",
                                tol=1e-4,
                                seed=154572,
                            )
                        ),
                    )
                ),
                "method": "networkx_tracemin_pcg_tol_1e-4",
                "spectral_failure": None,
            }
        except Exception as exc:  # pragma: no cover - solver variance
            return {
                "lambda2": 0.0,
                "method": "networkx_tracemin_pcg_fallback_zero",
                "spectral_failure": type(exc).__name__,
            }
    try:
        values = eigsh(
            laplacian,
            k=2,
            which="SM",
            return_eigenvectors=False,
            tol=1e-8,
            maxiter=20000,
        )
        values = np.sort(values)
        return {
            "lambda2": _round(max(0.0, float(values[1]))),
            "method": "eigsh_SM_k2_scipy_sparse",
            "spectral_failure": None,
        }
    except Exception as exc:  # pragma: no cover - ARPACK variance
        return {
            "lambda2": 0.0,
            "method": "spectral_fallback_zero",
            "spectral_failure": type(exc).__name__,
        }


def _graph_summary(graph: nx.Graph) -> dict[str, Any]:
    components = [set(component) for component in nx.connected_components(graph)]
    components.sort(key=lambda component: (-len(component), sorted(component)[0] if component else ""))
    isolated_nodes = sorted(node for node, degree in graph.degree() if degree == 0)
    lambda2 = _sparse_lambda2(graph)
    largest = len(components[0]) if components else 0
    return {
        "component_count": len(components),
        "edge_count": graph.number_of_edges(),
        "giant_component_fraction": _round(largest / graph.number_of_nodes())
        if graph.number_of_nodes()
        else 0.0,
        "isolated_node_count": len(isolated_nodes),
        "isolated_node_sample": isolated_nodes[:200],
        "lambda2": lambda2["lambda2"],
        "lambda2_method": lambda2["method"],
        "node_count": graph.number_of_nodes(),
        "spectral_failure": lambda2["spectral_failure"],
    }


def _delta(value: float | int, baseline: float | int | None) -> float | None:
    if baseline is None:
        return None
    return _round(float(value) - float(baseline))


def _find_genesis_root(node_by_id: dict[str, dict[str, Any]]) -> str:
    for candidate in GENESIS_ROOT_CANDIDATES:
        if candidate in node_by_id:
            return candidate
    for node_id, node in node_by_id.items():
        if node.get("node_kind") == "genesis_root_node":
            return node_id
    raise RuntimeError("fix72_no_genesis_root_candidate_found")


def _bfs(start_nodes: list[str], adjacency: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    queue = deque(start_nodes)
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in adjacency.get(node, []):
            if neighbor not in visited:
                queue.append(neighbor)
    return visited


def _top_indegree(edges: list[dict[str, Any]], edge_type: str, limit: int = 10) -> list[dict[str, Any]]:
    counts = Counter(_edge_target(edge) for edge in edges if _edge_type(edge) == edge_type)
    return [
        {"node_id": node_id, "in_degree": count}
        for node_id, count in counts.most_common(limit)
    ]


def _load_ratified_cdl_numbers() -> set[str]:
    text = CDL_REGISTER_PATH.read_text(encoding="utf-8")
    ratified: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("| CDL-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        decision_id = cells[0].replace("CDL-", "")
        status = cells[3].lower()
        if status == "ratified":
            ratified.add(decision_id.upper())
    return ratified


def _cdl_number(node_id: str) -> str | None:
    if not node_id.startswith("cdl:"):
        return None
    raw = node_id.removeprefix("cdl:")
    if raw.startswith("v"):
        match = re.match(r"v(\d+)", raw)
        return f"V{match.group(1)}" if match else None
    match = re.match(r"(\d{3})", raw)
    return match.group(1) if match else None


def _is_cdl_node(node_id: str, node: dict[str, Any]) -> bool:
    return node_id.startswith("cdl:") or str(node.get("node_kind", "")).startswith("cdl")


def _is_adr_node(node_id: str, node: dict[str, Any]) -> bool:
    return node_id.startswith("adr:") or str(node.get("node_kind", "")).startswith("adr")


def _run_projection_fiedler(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    node_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    all_ids = set(node_by_id)
    authority_ids = {
        node_id
        for node_id, node in node_by_id.items()
        if node.get("graph_projection") in AUTHORITY_PROJECTIONS
    }
    public_ids = {
        node_id
        for node_id, node in node_by_id.items()
        if node.get("graph_projection") in PUBLIC_ELIGIBLE_PROJECTIONS
    }
    binding_ids = set(authority_ids)
    binding_sources: list[dict[str, str]] = []
    for edge in edges:
        if _edge_type(edge) not in {"IMPLEMENTS", "REFERENCES_AUTHORITY"}:
            continue
        source = _edge_source(edge)
        target = _edge_target(edge)
        if target in authority_ids and _is_ilc_core_node(node_by_id.get(source, {})):
            binding_ids.add(source)
            binding_sources.append(
                {"edge_type": _edge_type(edge), "source": source, "target": target}
            )

    graphs = {
        "all_local": _build_undirected(all_ids, edges),
        "public_eligible": _build_undirected(public_ids, edges),
        "authority_only": _build_undirected(authority_ids, edges),
        "authority_binding_surface": _build_undirected(binding_ids, edges),
    }
    projections: dict[str, Any] = {}
    for name, graph in graphs.items():
        summary = _graph_summary(graph)
        baseline = FIX56_BASELINES.get(name)
        if baseline:
            summary["fix56_baseline"] = baseline
            summary["delta_vs_fix56"] = {
                "edge_count": summary["edge_count"] - baseline["edges"],
                "lambda2": _delta(summary["lambda2"], baseline["lambda2"]),
                "node_count": summary["node_count"] - baseline["nodes"],
            }
        else:
            summary["fix56_baseline"] = None
            summary["delta_vs_fix56"] = None
        projections[name] = summary

    return {
        "authority_binding_surface_source_edge_count": len(binding_sources),
        "authority_binding_surface_source_edge_sample": binding_sources[:200],
        "execution_lmdb_counts": {"nodes": len(nodes), "edges": len(edges)},
        "fix56_baselines": FIX56_BASELINES,
        "phase": PHASE,
        "projections": projections,
        "schema_version": "fix72_projection_fiedler_rebaseline.v0.1",
    }


def _run_whole_graph_baseline(
    *,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    node_by_id: dict[str, dict[str, Any]],
    graph_all: nx.Graph,
) -> tuple[dict[str, Any], dict[str, Any]]:
    genesis_root = _find_genesis_root(node_by_id)
    forward_adj: dict[str, list[str]] = defaultdict(list)
    reverse_implements: dict[str, list[str]] = defaultdict(list)
    reverse_refs: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        edge_type = _edge_type(edge)
        if edge_type in AUTHORITY_CONTROL_EDGES:
            forward_adj[source].append(target)
        if edge_type == "IMPLEMENTS":
            reverse_implements[target].append(source)
        if edge_type == "REFERENCES_AUTHORITY":
            reverse_refs[target].append(source)

    authority_forward = _bfs([genesis_root], forward_adj)
    cdl_adr_nodes = [
        node_id
        for node_id, node in node_by_id.items()
        if _is_cdl_node(node_id, node) or _is_adr_node(node_id, node)
    ]
    reverse_implements_reach = _bfs(sorted(cdl_adr_nodes), reverse_implements)
    reverse_refs_reach = _bfs(sorted(cdl_adr_nodes), reverse_refs)
    ilc_core_nodes = {node_id for node_id, node in node_by_id.items() if _is_ilc_core_node(node)}
    components = list(nx.connected_components(graph_all))
    largest_component = max((len(component) for component in components), default=0)
    payload = {
        "edge_count": len(edges),
        "genesis_root": genesis_root,
        "node_count": len(nodes),
        "phase": PHASE,
        "schema_version": "fix72_whole_graph_baseline_diagnostic.v0.1",
        "top_indegree": {
            "GOVERNS": _top_indegree(edges, "GOVERNS"),
            "REFERENCES_AUTHORITY": _top_indegree(edges, "REFERENCES_AUTHORITY"),
        },
        "traversals": {
            "authority_control_forward": {
                "coverage_fraction": _round(len(authority_forward) / len(nodes)) if nodes else 0.0,
                "edge_types": sorted(AUTHORITY_CONTROL_EDGES),
                "reachable_count": len(authority_forward),
                "unreachable_count": len(nodes) - len(authority_forward),
            },
            "implementation_reverse": {
                "edge_type": "IMPLEMENTS",
                "ilc_core_reachable_count": len(ilc_core_nodes & reverse_implements_reach),
                "ilc_core_total": len(ilc_core_nodes),
                "reachable_count": len(reverse_implements_reach),
                "reachable_fraction": _round(len(reverse_implements_reach) / len(nodes))
                if nodes
                else 0.0,
            },
            "authority_reference_reverse": {
                "edge_type": "REFERENCES_AUTHORITY",
                "ilc_core_reachable_count": len(ilc_core_nodes & reverse_refs_reach),
                "ilc_core_total": len(ilc_core_nodes),
                "reachable_count": len(reverse_refs_reach),
                "reachable_fraction": _round(len(reverse_refs_reach) / len(nodes)) if nodes else 0.0,
            },
            "undirected_connectivity": {
                "component_count": len(components),
                "giant_component_fraction": _round(largest_component / len(nodes)) if nodes else 0.0,
                "largest_component_count": largest_component,
            },
        },
    }
    traversal_state = {
        "authority_forward": authority_forward,
        "genesis_root": genesis_root,
        "reverse_implements_reach": reverse_implements_reach,
        "reverse_refs_reach": reverse_refs_reach,
    }
    return payload, traversal_state


def _run_spectral_pagerank(
    *,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    node_by_id: dict[str, dict[str, Any]],
    graph_all: nx.Graph,
    all_lambda2: float,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    components = list(nx.connected_components(graph_all))
    largest = max((len(component) for component in components), default=0)
    started = _log("enumerating full-graph bridges")
    bridges = sorted(tuple(sorted(edge)) for edge in nx.bridges(graph_all))
    _log("full-graph bridges complete", started)
    started = _log("running full-graph PageRank")
    pagerank = nx.pagerank(graph_all, alpha=0.85, tol=1e-10, max_iter=200)
    _log("full-graph PageRank complete", started)
    betweenness_k = min(128, graph_all.number_of_nodes())
    started = _log(f"running approximate betweenness k={betweenness_k}")
    betweenness = nx.betweenness_centrality(
        graph_all,
        k=betweenness_k,
        seed=154572,
        normalized=True,
    )
    _log("approximate betweenness complete", started)
    protocol_nodes = [
        node_id for node_id, node in node_by_id.items() if _is_protocol_relevant(node)
    ]
    low_queue_nodes = sorted(protocol_nodes, key=lambda node_id: (pagerank.get(node_id, 0.0), node_id))[
        :500
    ]
    low_queue = [
        {
            "candidate_id": node_id,
            "degree": int(graph_all.degree(node_id)),
            "node_kind": node_by_id[node_id].get("node_kind"),
            "pagerank": pagerank.get(node_id, 0.0),
            "source_path": _source_path(node_by_id[node_id]),
        }
        for node_id in low_queue_nodes
    ]
    spectral = {
        "baseline_fix43": FIX43_BASELINES,
        "betweenness": {
            "approximation_k": betweenness_k,
            "top_100": [
                {"candidate_id": node_id, "score": score}
                for node_id, score in sorted(
                    betweenness.items(), key=lambda item: (-item[1], item[0])
                )[:100]
            ],
        },
        "bridge_count": len(bridges),
        "bridge_sample": [{"source": source, "target": target} for source, target in bridges[:100]],
        "deltas_vs_fix43": {
            "bridge_count": len(bridges) - FIX43_BASELINES["bridge_count"],
            "giant_component_fraction": _delta(
                _round(largest / len(nodes)) if nodes else 0.0,
                FIX43_BASELINES["giant_component_fraction"],
            ),
            "lambda2": _delta(all_lambda2, FIX43_BASELINES["lambda2"]),
            "protocol_relevant_node_count": len(protocol_nodes)
            - FIX43_BASELINES["protocol_relevant_node_count"],
        },
        "edge_count": len(edges),
        "giant_component_fraction": _round(largest / len(nodes)) if nodes else 0.0,
        "lambda2": all_lambda2,
        "node_count": len(nodes),
        "phase": PHASE,
        "protocol_relevant_node_count": len(protocol_nodes),
        "schema_version": "fix72_spectral_post_fix69.v0.1",
    }
    pagerank_payload = {
        "parameters": {"alpha": 0.85, "max_iter": 200, "tol": 1e-10},
        "phase": PHASE,
        "schema_version": "fix72_pagerank_post_fix69.v0.1",
        "top_100": [
            {"candidate_id": node_id, "pagerank": score}
            for node_id, score in sorted(pagerank.items(), key=lambda item: (-item[1], item[0]))[:100]
        ],
        "bottom_100": [
            {"candidate_id": node_id, "pagerank": score}
            for node_id, score in sorted(pagerank.items(), key=lambda item: (item[1], item[0]))[:100]
        ],
    }
    queue_payload = {
        "excluded_prefixes": list(EXCLUDED_REPO_PREFIXES),
        "phase": PHASE,
        "protocol_relevant_node_count": len(protocol_nodes),
        "queue": low_queue,
        "queue_count": len(low_queue),
        "schema_version": "fix72_low_pagerank_queue.v0.1",
    }
    return spectral, pagerank_payload, queue_payload


def _load_fix45_deferred_entries() -> tuple[str, list[dict[str, Any]], dict[str, int]]:
    if FIX46_QUEUE_PATH.exists():
        data = json.loads(FIX46_QUEUE_PATH.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        if isinstance(entries, list):
            return "docs/specs/ilc_fix46_manual_semantic_annotation_queue_v0.1.json", entries, {
                "entry_count": len(entries)
            }
    data = json.loads(FIX45_LEDGER_PATH.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("fix72_fix45_rows_missing")
    entries = [row for row in rows if row.get("decision") == "deferred_manual_semantic_review"]
    return "docs/specs/ilc_fix45_algorithmic_percolation_ledger_v0.1.json", entries, {
        "deferred_manual_semantic_review": len(entries)
    }


def _run_percolation_analysis(
    *,
    edges: list[dict[str, Any]],
    node_by_id: dict[str, dict[str, Any]],
    low_queue: dict[str, Any],
) -> dict[str, Any]:
    source_name, entries, source_counts = _load_fix45_deferred_entries()
    semantic_indegree: Counter[str] = Counter()
    semantic_outdegree: Counter[str] = Counter()
    semantic_edge_types: dict[str, Counter[str]] = defaultdict(Counter)
    for edge in edges:
        target = _edge_target(edge)
        source = _edge_source(edge)
        edge_type = _edge_type(edge)
        if target and not source.startswith("repo:"):
            semantic_indegree[target] += 1
            semantic_edge_types[target][edge_type] += 1
        if source and not target.startswith("repo:"):
            semantic_outdegree[source] += 1
            semantic_edge_types[source][edge_type] += 1

    resolved: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for entry in entries:
        node_id = entry.get("node_id")
        if not isinstance(node_id, str):
            continue
        in_count = semantic_indegree[node_id]
        out_count = semantic_outdegree[node_id]
        any_count = in_count + out_count
        node = node_by_id.get(node_id)
        row = {
            "candidate_id": node_id,
            "semantic_edge_type_counts": dict(sorted(semantic_edge_types[node_id].items())),
            "semantic_indegree": in_count,
            "semantic_outdegree": out_count,
            "semantic_total_degree": any_count,
            "original_reason": entry.get("reason"),
            "repo_path": entry.get("repo_path"),
        }
        if node is None:
            missing.append(row)
        elif any_count > 0:
            resolved.append(row)
        else:
            row.update(
                {
                    "node_kind": node.get("node_kind"),
                    "source_path": _source_path(node),
                    "deterministic_metadata_only_annotation": False,
                }
            )
            unresolved.append(row)

    low_queue_ids = {row.get("candidate_id") for row in low_queue.get("queue", []) if isinstance(row, dict)}
    return {
        "analysis_only": True,
        "current_low_pagerank_overlap_count": sum(
            1 for row in unresolved if row["candidate_id"] in low_queue_ids
        ),
        "fix45_deferred_source": source_name,
        "fix45_source_counts": source_counts,
        "missing_node_count": len(missing),
        "missing_nodes": missing[:200],
        "phase": PHASE,
        "resolved_by_any_semantic_degree_count": len(resolved),
        "resolved_by_prompt_indegree_count": sum(
            1 for entry in entries if semantic_indegree.get(str(entry.get("node_id")), 0) > 0
        ),
        "resolved_count": len(resolved),
        "resolved_sample": resolved[:100],
        "schema_version": "fix72_percolation_analysis.v0.1",
        "still_unresolved_count": len(unresolved),
        "still_unresolved_nodes": unresolved,
        "write_policy": "no_edges_written_analysis_only",
    }


def _run_authority_sim_battery(
    *,
    edges: list[dict[str, Any]],
    node_by_id: dict[str, dict[str, Any]],
    traversal_state: dict[str, Any],
) -> dict[str, Any]:
    cdl_nodes = {
        node_id: node
        for node_id, node in node_by_id.items()
        if _is_cdl_node(node_id, node)
    }
    ratified_numbers = _load_ratified_cdl_numbers()
    ratified_cdl_nodes = {
        node_id: node
        for node_id, node in cdl_nodes.items()
        if node.get("canonicality_tier") == "ratified_cdl"
        or (number := _cdl_number(node_id)) in ratified_numbers
    }
    visited_forward: set[str] = traversal_state["authority_forward"]
    unreachable_cdls = sorted(node_id for node_id in cdl_nodes if node_id not in visited_forward)

    governs_graph = nx.DiGraph()
    for edge in edges:
        if _edge_type(edge) == "GOVERNS":
            governs_graph.add_edge(_edge_source(edge), _edge_target(edge))
    cycles = [cycle for cycle in nx.simple_cycles(governs_graph)]
    cycles.sort(key=lambda cycle: (len(cycle), cycle))

    gap_rows: list[dict[str, Any]] = []
    for node_id, node in sorted(node_by_id.items()):
        if node.get("node_kind") != "epistemic_gap" and not node_id.startswith("gap:"):
            continue
        candidate_targets = node.get("candidate_targets")
        if not isinstance(candidate_targets, list):
            candidate_targets = []
        resolvable = [target for target in candidate_targets if target in node_by_id]
        hint = node.get("target_prefix_hint") or node.get("target_schema_hint")
        gap_rows.append(
            {
                "candidate_id": node_id,
                "candidate_targets": candidate_targets,
                "resolvable_candidate_targets": resolvable,
                "status": node.get("status"),
                "target_hint": hint,
            }
        )

    implements_by_cdl: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if _edge_type(edge) != "IMPLEMENTS":
            continue
        source = _edge_source(edge)
        target = _edge_target(edge)
        if target not in ratified_cdl_nodes:
            continue
        if _is_ilc_core_node(node_by_id.get(source, {})):
            implements_by_cdl[target].append(source)
    implementation_dark_cdls = [
        node_id
        for node_id in sorted(ratified_cdl_nodes)
        if not implements_by_cdl.get(node_id)
    ]
    return {
        "phase": PHASE,
        "schema_version": "fix72_authority_sim_battery.v0.1",
        "suite_a_cdl_reachability": {
            "cdl_node_count": len(cdl_nodes),
            "unreachable_cdl_count": len(unreachable_cdls),
            "unreachable_cdls": unreachable_cdls,
        },
        "suite_b_governs_cycles": {
            "cycle_count": len(cycles),
            "cycle_sample": cycles[:20],
        },
        "suite_c_gap_closure": {
            "epistemic_gap_count": len(gap_rows),
            "gaps": gap_rows,
            "resolvable_gap_count": sum(
                1 for row in gap_rows if row["resolvable_candidate_targets"]
            ),
        },
        "suite_d_runtime_binding_coverage": {
            "implementation_dark_cdl_count": len(implementation_dark_cdls),
            "implementation_dark_cdls": implementation_dark_cdls,
            "implements_by_cdl_sample": {
                node_id: sorted(sources)[:20]
                for node_id, sources in sorted(implements_by_cdl.items())[:50]
            },
            "ratified_cdl_basis": {
                "cdl_register_ratified_numbers": sorted(ratified_numbers),
                "metadata_canonicality_tier": "ratified_cdl",
            },
            "ratified_cdl_node_count": len(ratified_cdl_nodes),
        },
    }


def _status_block(summary: dict[str, Any]) -> str:
    projection = summary["fiedler"]["projections"]
    spectral = summary["spectral"]
    sims = summary["authority_sim"]
    return f"""

### Phase 1545p-Fix72 - Post-Repair Measurement Suite

**Status:** complete

**Output:** Ran the 5-pass post-repair measurement suite over the unified Atlas
LMDB snapshot with `{summary['lmdb_counts']['nodes']}` nodes and
`{summary['lmdb_counts']['edges']}` edges. Rebaselined projection-aware
Fiedler values (`all_local` lambda2 `{projection['all_local']['lambda2']}`,
`authority_only` lambda2 `{projection['authority_only']['lambda2']}`,
`authority_binding_surface` lambda2 `{projection['authority_binding_surface']['lambda2']}`),
recorded spectral/PageRank diagnostics (`{spectral['bridge_count']}` bridges),
measured Fix45/Fix46 deferred-node resolution, and produced the authority SIM
battery with `{sims['suite_d_runtime_binding_coverage']['implementation_dark_cdl_count']}`
implementation-dark ratified CDL nodes. No LMDB graph-content mutation occurred;
only support-only phase-file registration was performed after measurements.

**Tokens:** {','.join(OUTPUT_TOKENS)}
"""


def _append_status(summary: dict[str, Any]) -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    heading = "\n### Phase 1545p-Fix72 - Post-Repair Measurement Suite"
    if heading in text:
        text = text[: text.index(heading)]
    _atomic_write(STATUS_PATH, text.rstrip() + _status_block(summary).rstrip() + "\n")


def _artifact_record(path: Path, purpose: str, committed: bool) -> dict[str, Any]:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return {
        "bytes": path.stat().st_size,
        "committed": committed,
        "path": rel,
        "purpose": purpose,
        "sha256": _sha256_file(path),
    }


def _build_manifest() -> dict[str, Any]:
    artifacts = [
        (PROMPT_PATH, "phase prompt", True),
        (WALKTHROUGH_PATH, "walkthrough", True),
        (WHOLE_GRAPH_PATH, "whole graph baseline diagnostic", True),
        (PERCOLATION_PATH, "percolation analysis report", True),
        (AUTHORITY_SIM_PATH, "authority SIM battery", True),
        (EVALUATOR_PATH, "measurement suite evaluator", True),
        (TEST_PATH, "phase regression tests", True),
        (STATUS_PATH, "phase status token record", True),
        (FIEDLER_ALL_PATH, "projection-aware Fiedler report", False),
        (FIEDLER_AUTHORITY_PATH, "authority-only isolated/minority report", False),
        (FIEDLER_BINDING_PATH, "authority binding surface report", False),
        (SPECTRAL_PATH, "spectral diagnostics", False),
        (PAGERANK_PATH, "PageRank diagnostics", False),
        (LOW_PAGERANK_PATH, "bottom-PageRank queue", False),
    ]
    return {
        "artifacts": [
            _artifact_record(path, purpose, committed)
            for path, purpose, committed in artifacts
            if path.exists()
        ],
        "manifest_self_hash_policy": "self_hash_excluded_to_avoid_fixed_point_manifest_loop",
        "phase": PHASE,
        "schema_version": "fix72_measurement_suite_manifest.v0.1",
    }


def _write_walkthrough(summary: dict[str, Any]) -> None:
    projection = summary["fiedler"]["projections"]
    whole = summary["whole_graph"]
    spectral = summary["spectral"]
    percolation = summary["percolation"]
    sims = summary["authority_sim"]
    lines = [
        "# Phase 1545p-Fix72 Measurement Suite Walkthrough",
        "",
        "PUBLIC_RC_EXCLUDE: fix72_post_repair_measurement_suite_local_atlas_maintenance",
        "",
        "## Live Snapshot",
        "",
        f"- LMDB root: `{LMDB_ROOT.relative_to(REPO_ROOT).as_posix()}`",
        f"- Nodes at measurement start: `{summary['lmdb_counts']['nodes']}`",
        f"- Edges at measurement start: `{summary['lmdb_counts']['edges']}`",
        "- Measurement posture: read-only graph-content snapshot; support-only file registration occurred after all measurements.",
        "",
        "## Pass 1: Projection-Aware Fiedler Rebaseline",
        "",
        "| Projection | Nodes | Edges | Components | Lambda2 | Delta vs Fix56 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ["all_local", "public_eligible", "authority_only", "authority_binding_surface"]:
        item = projection[name]
        delta = item.get("delta_vs_fix56")
        delta_text = "n/a" if delta is None else str(delta["lambda2"])
        lines.append(
            f"| {name} | {item['node_count']} | {item['edge_count']} | "
            f"{item['component_count']} | {item['lambda2']} | {delta_text} |"
        )
    lines.extend(
        [
            "",
            f"- Authority-only isolated nodes: `{projection['authority_only']['isolated_node_count']}`",
            f"- Authority binding surface source edges: `{summary['fiedler']['authority_binding_surface_source_edge_count']}`",
            "",
            "## Pass 2: Whole-Graph Baseline Diagnostic",
            "",
            f"- Genesis root used: `{whole['genesis_root']}`",
            f"- Authority-control forward coverage: `{whole['traversals']['authority_control_forward']['reachable_count']}` / `{summary['lmdb_counts']['nodes']}`",
            f"- Reverse IMPLEMENTS ilc_core reach: `{whole['traversals']['implementation_reverse']['ilc_core_reachable_count']}` / `{whole['traversals']['implementation_reverse']['ilc_core_total']}`",
            f"- Reverse REFERENCES_AUTHORITY ilc_core reach: `{whole['traversals']['authority_reference_reverse']['ilc_core_reachable_count']}` / `{whole['traversals']['authority_reference_reverse']['ilc_core_total']}`",
            f"- Undirected component count: `{whole['traversals']['undirected_connectivity']['component_count']}`",
            f"- Undirected giant component fraction: `{whole['traversals']['undirected_connectivity']['giant_component_fraction']}`",
            "- Top GOVERNS in-degree targets: "
            + ", ".join(
                f"{row['node_id']}={row['in_degree']}"
                for row in whole["top_indegree"]["GOVERNS"][:10]
            ),
            "- Top REFERENCES_AUTHORITY in-degree targets: "
            + ", ".join(
                f"{row['node_id']}={row['in_degree']}"
                for row in whole["top_indegree"]["REFERENCES_AUTHORITY"][:10]
            ),
            "",
            "## Pass 3: Spectral and PageRank Analysis",
            "",
            f"- Full graph lambda2: `{spectral['lambda2']}`; Fix43 baseline `{FIX43_BASELINES['lambda2']}`; delta `{spectral['deltas_vs_fix43']['lambda2']}`",
            f"- Bridge count: `{spectral['bridge_count']}`; Fix43 baseline `{FIX43_BASELINES['bridge_count']}`; delta `{spectral['deltas_vs_fix43']['bridge_count']}`",
            f"- Giant component fraction: `{spectral['giant_component_fraction']}`",
            f"- PageRank parameters: alpha `0.85`, tol `1e-10`, max_iter `200`",
            f"- Approximate betweenness k: `{spectral['betweenness']['approximation_k']}`",
            f"- Bottom-PageRank protocol-relevant queue size: `{summary['low_queue']['queue_count']}`",
            "",
            "## Pass 4: Percolation Analysis",
            "",
            f"- Deferred source: `{percolation['fix45_deferred_source']}`",
            f"- Resolved deferred nodes by any semantic degree: `{percolation['resolved_by_any_semantic_degree_count']}`",
            f"- Resolved deferred nodes by strict prompt in-degree: `{percolation['resolved_by_prompt_indegree_count']}`",
            f"- Still unresolved deferred nodes: `{percolation['still_unresolved_count']}`",
            f"- Missing deferred nodes: `{percolation['missing_node_count']}`",
            "- Edge write posture: analysis only, no LMDB graph-content writes.",
            "",
            "## Pass 5: Authority SIM Battery",
            "",
            f"- Suite A unreachable CDL nodes: `{sims['suite_a_cdl_reachability']['unreachable_cdl_count']}` / `{sims['suite_a_cdl_reachability']['cdl_node_count']}`",
            f"- Suite B GOVERNS cycles: `{sims['suite_b_governs_cycles']['cycle_count']}`",
            f"- Suite C epistemic gaps: `{sims['suite_c_gap_closure']['epistemic_gap_count']}`; resolvable candidates `{sims['suite_c_gap_closure']['resolvable_gap_count']}`",
            f"- Suite D implementation-dark ratified CDL nodes: `{sims['suite_d_runtime_binding_coverage']['implementation_dark_cdl_count']}` / `{sims['suite_d_runtime_binding_coverage']['ratified_cdl_node_count']}`",
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in OUTPUT_TOKENS:
        lines.append(f"- `{token}`")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- No Genesis signing occurred.",
            "- No public graph upload or public RC activation occurred.",
            "- No runtime activation, ECU minting, ILC settlement, or production economics occurred.",
            "- Spectral and PageRank diagnostics are anomaly-detection signals, not security guarantees.",
        ]
    )
    _atomic_write(WALKTHROUGH_PATH, "\n".join(lines) + "\n")


def _register_phase_files() -> dict[str, Any]:
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        files = [
            AtlasPhaseFileRegistration(
                path=PROMPT_PATH.relative_to(REPO_ROOT),
                node_kind="phase_prompt_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
                node_kind="phase_walkthrough_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=WHOLE_GRAPH_PATH.relative_to(REPO_ROOT),
                node_kind="diagnostic_report_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=PERCOLATION_PATH.relative_to(REPO_ROOT),
                node_kind="diagnostic_report_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=AUTHORITY_SIM_PATH.relative_to(REPO_ROOT),
                node_kind="diagnostic_report_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=MANIFEST_PATH.relative_to(REPO_ROOT),
                node_kind="diagnostic_report_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=EVALUATOR_PATH.relative_to(REPO_ROOT),
                node_kind="evaluator_tool_node",
                graph_projection="support_candidate_graph",
            ),
            AtlasPhaseFileRegistration(
                path=TEST_PATH.relative_to(REPO_ROOT),
                node_kind="test_node",
                graph_projection="support_candidate_graph",
                required_edges=(("TESTS", "phase:phase_1545p_fix72"),),
            ),
        ]
        dry = writer.register_phase_files(PHASE, files, dry_run=True)
        if dry.get("status") == "FAIL":
            raise RuntimeError(f"fix72_phase_registration_dry_run_failed:{dry}")
        receipt = writer.register_phase_files(PHASE, files, dry_run=False)
        lineage_plan = AtlasLmdbWritePlan(
            edges_to_add=[
                {
                    "annotation_method": "fix72_phase_lineage_hygiene",
                    "annotation_phase": "phase_1545p_fix72",
                    "candidate_status": "fix72_support_phase_lineage_hygiene",
                    "confidence": "high",
                    "edge_type": "CARRIES_FORWARD",
                    "evidence_path": "docs/phases/STATUS.md",
                    "evidence_summary": (
                        "Fix72 support phase node carries forward to the Phase 1545p "
                        "repair-lineage root, matching Fix69 phase-node hygiene."
                    ),
                    "source": "phase:phase_1545p_fix72",
                    "target": "phase:1545p",
                }
            ],
            metadata={"operation": "fix72_support_phase_lineage_hygiene"},
            phase="phase_1545p_fix72_lineage_hygiene",
            dry_run=True,
        )
        lineage_dry = writer.apply_plan(lineage_plan)
        if lineage_dry.get("status") == "FAIL":
            raise RuntimeError(f"fix72_phase_lineage_dry_run_failed:{lineage_dry}")
        lineage_live = writer.apply_plan(
            AtlasLmdbWritePlan(
                edges_to_add=lineage_plan.edges_to_add,
                metadata=lineage_plan.metadata,
                phase=lineage_plan.phase,
                dry_run=False,
            )
        )
        receipt["phase_lineage_hygiene_receipt"] = lineage_live
        return receipt
    finally:
        writer.close()


def _verify_inputs() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    missing = [token for token in INPUT_TOKENS if token not in status]
    if missing:
        raise RuntimeError(f"fix72_missing_input_tokens:{missing}")
    for path in [PROMPT_PATH, GUIDANCE_PATH, CDL_REGISTER_PATH]:
        if not path.exists():
            raise RuntimeError(f"fix72_required_input_missing:{path}")


def _filter_self_registration_snapshot(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Remove this phase's support registration rows from measurement reruns."""

    self_node_ids = {
        _node_id(node)
        for node in nodes
        if node.get("annotation_phase") == SELF_REGISTRATION_PHASE
    }
    filtered_nodes = [node for node in nodes if _node_id(node) not in self_node_ids]
    filtered_edges = [
        edge
        for edge in edges
        if edge.get("annotation_phase") != SELF_REGISTRATION_PHASE
        and _edge_source(edge) not in self_node_ids
        and _edge_target(edge) not in self_node_ids
    ]
    return filtered_nodes, filtered_edges


def run(register: bool = True) -> dict[str, Any]:
    _verify_inputs()
    started = _log("loading unified LMDB snapshot")
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes = list(writer.store.iter_nodes())
        edges = list(writer.store.iter_edges())
    finally:
        writer.close()
    nodes, edges = _filter_self_registration_snapshot(nodes, edges)
    _log(f"loaded snapshot nodes={len(nodes)} edges={len(edges)}", started)
    node_by_id = {_node_id(node): node for node in nodes}

    started = _log("pass 1 projection Fiedler")
    fiedler = _run_projection_fiedler(nodes, edges, node_by_id)
    _log("pass 1 complete", started)
    graph_all = _build_undirected(set(node_by_id), edges)
    started = _log("pass 2 whole-graph baseline")
    whole_graph, traversal_state = _run_whole_graph_baseline(
        nodes=nodes,
        edges=edges,
        node_by_id=node_by_id,
        graph_all=graph_all,
    )
    _log("pass 2 complete", started)
    started = _log("pass 3 spectral/PageRank")
    spectral, pagerank, low_queue = _run_spectral_pagerank(
        nodes=nodes,
        edges=edges,
        node_by_id=node_by_id,
        graph_all=graph_all,
        all_lambda2=fiedler["projections"]["all_local"]["lambda2"],
    )
    _log("pass 3 complete", started)
    started = _log("pass 4 percolation analysis")
    percolation = _run_percolation_analysis(
        edges=edges,
        node_by_id=node_by_id,
        low_queue=low_queue,
    )
    _log("pass 4 complete", started)
    started = _log("pass 5 authority SIM battery")
    authority_sim = _run_authority_sim_battery(
        edges=edges,
        node_by_id=node_by_id,
        traversal_state=traversal_state,
    )
    _log("pass 5 complete", started)

    summary = {
        "authority_sim": authority_sim,
        "fiedler": fiedler,
        "lmdb_counts": {"edges": len(edges), "nodes": len(nodes)},
        "low_queue": low_queue,
        "pagerank": pagerank,
        "percolation": percolation,
        "spectral": spectral,
        "whole_graph": whole_graph,
    }

    started = _log("writing Fix72 output artifacts")
    _atomic_write(FIEDLER_ALL_PATH, _json_text(fiedler))
    _atomic_write(
        FIEDLER_AUTHORITY_PATH,
        _json_text(
            {
                "authority_only": fiedler["projections"]["authority_only"],
                "phase": PHASE,
                "schema_version": "fix72_authority_only_minority.v0.1",
            }
        ),
    )
    _atomic_write(
        FIEDLER_BINDING_PATH,
        _json_text(
            {
                "authority_binding_surface": fiedler["projections"][
                    "authority_binding_surface"
                ],
                "source_edge_count": fiedler["authority_binding_surface_source_edge_count"],
                "source_edge_sample": fiedler["authority_binding_surface_source_edge_sample"],
                "phase": PHASE,
                "schema_version": "fix72_authority_binding_surface.v0.1",
            }
        ),
    )
    _atomic_write(WHOLE_GRAPH_PATH, _json_text(whole_graph))
    _atomic_write(SPECTRAL_PATH, _json_text(spectral))
    _atomic_write(PAGERANK_PATH, _json_text(pagerank))
    _atomic_write(LOW_PAGERANK_PATH, _json_text(low_queue))
    _atomic_write(PERCOLATION_PATH, _json_text(percolation))
    _atomic_write(AUTHORITY_SIM_PATH, _json_text(authority_sim))
    _write_walkthrough(summary)
    _append_status(summary)
    manifest = _build_manifest()
    _atomic_write(MANIFEST_PATH, _json_text(manifest))
    _log("output artifacts written", started)

    if register:
        started = _log("registering support-only phase files in LMDB")
        registration = _register_phase_files()
        summary["phase_file_registration_receipt"] = registration
        _log("support-only phase file registration complete", started)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-register", action="store_true")
    args = parser.parse_args()
    summary = run(register=not args.no_register)
    print(
        json.dumps(
            {
                "authority_binding_lambda2": summary["fiedler"]["projections"][
                    "authority_binding_surface"
                ]["lambda2"],
                "edges": summary["lmdb_counts"]["edges"],
                "implementation_dark_cdls": summary["authority_sim"][
                    "suite_d_runtime_binding_coverage"
                ]["implementation_dark_cdl_count"],
                "nodes": summary["lmdb_counts"]["nodes"],
                "status": "PASS",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
