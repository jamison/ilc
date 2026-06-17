#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1545p-Fix43 spectral/PageRank analysis over the Fix41a Atlas candidate.

PUBLIC_RC_EXCLUDE: genesis_base_graph_spectral_pagerank_fix43_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only structural diagnostics over an unsigned
Atlas candidate; no Genesis signing, canonical graph mutation, public graph
publication, public RC activation, runtime activation, minting, settlement, or
ADR/CDL mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse import csgraph
from scipy.sparse.linalg import eigsh


ROOT = Path(__file__).resolve().parents[2]
PHASE = "1545p-Fix43"
SCHEMA_VERSION = "sim_genesis_base_graph_spectral_pagerank_1545p_fix43.v0.1"
CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
BASELINE = ROOT / "out/sim_atlas_spectral_non_excisability_1545p_fix29.json"
SPECTRAL_OUT = ROOT / "out/genesis_base_graph_spectral_post_fix38.json"
PAGERANK_OUT = ROOT / "out/genesis_base_graph_pagerank_post_fix38.json"
QUEUE_OUT = ROOT / "out/genesis_base_graph_fix44_target_queue.json"
REPORT_OUT = ROOT / "docs/sims/sim_spectral_02/genesis_spectral_delta_fix38_v0.1.md"

PROTOCOL_RELEVANT_PREFIXES = ("ilc_core/", "docs/specs/", "tests/", "tools/")
EXCLUDED_TARGET_PREFIXES = ("out/", ".git/")
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

OUTPUT_TOKENS = [
    "fix43_spectral_analysis_complete",
    "fix43_pagerank_complete",
    "fix43_fix44_target_queue_produced",
    "fix43_complete",
    "public_path_remains_blocked_phase_1545p_fix43",
]

NON_CLAIMS = [
    "No Genesis signing occurred.",
    "No canonical Atlas mutation occurred.",
    "No public graph publication occurred.",
    "No public repository push occurred.",
    "No public RC activation occurred.",
    "No runtime, economic, sidecar, network, ADR, or CDL activation occurred.",
    "Spectral, PageRank, bridge, and betweenness metrics are structural diagnostics only, not authority proof.",
]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _pretty_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp", text=True)
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("id") or node.get("node_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix43_node_missing_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    value = edge.get("source_candidate_id") or edge.get("source") or edge.get("from")
    return value if isinstance(value, str) else ""


def _edge_target(edge: dict[str, Any]) -> str:
    value = edge.get("target_candidate_id") or edge.get("target") or edge.get("to")
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("type")
    return value if isinstance(value, str) else ""


def _round(value: float, digits: int = 12) -> float:
    return round(float(value), digits)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _repo_path_from_node(node_id: str, node: dict[str, Any]) -> str:
    for key in ("source_path", "repo_path", "path", "label"):
        value = node.get(key)
        if isinstance(value, str) and _looks_like_repo_path(value):
            return value
    if node_id.startswith("repo:file:"):
        raw = node_id.removeprefix("repo:file:")
        if "/" in raw:
            return raw
    if node_id.startswith("repo:file_ref:"):
        raw = node_id.removeprefix("repo:file_ref:")
        return raw.replace("_", "/")
    return ""


def _looks_like_repo_path(value: str) -> bool:
    return value.startswith(PROTOCOL_RELEVANT_PREFIXES) or value.startswith(EXCLUDED_TARGET_PREFIXES)


def _is_protocol_relevant(repo_path: str) -> bool:
    return repo_path.startswith(PROTOCOL_RELEVANT_PREFIXES) and not repo_path.startswith(EXCLUDED_TARGET_PREFIXES)


def _build_graph(data: dict[str, Any]) -> tuple[nx.Graph, dict[str, dict[str, Any]], dict[str, str], dict[str, set[str]]]:
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("fix43_candidate_nodes_edges_required")

    node_records = {_node_id(node): node for node in nodes if isinstance(node, dict)}
    repo_paths = {node_id: _repo_path_from_node(node_id, node) for node_id, node in node_records.items()}
    edge_types_by_node: dict[str, set[str]] = {node_id: set() for node_id in node_records}
    graph = nx.Graph()
    graph.add_nodes_from(sorted(node_records))

    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = _edge_source(edge)
        target = _edge_target(edge)
        edge_type = _edge_type(edge)
        if source not in node_records or target not in node_records:
            continue
        graph.add_edge(source, target)
        edge_types_by_node[source].add(edge_type)
        edge_types_by_node[target].add(edge_type)

    return graph, node_records, repo_paths, edge_types_by_node


def _lambda2_for_nodes(graph: nx.Graph, node_ids: list[str]) -> dict[str, Any]:
    if len(node_ids) < 2:
        return {"lambda_2": 0.0, "method": "too_few_nodes", "spectral_failure": None}

    index = {node_id: idx for idx, node_id in enumerate(node_ids)}
    rows = []
    cols = []
    for source, target in graph.subgraph(node_ids).edges():
        rows.extend([index[source], index[target]])
        cols.extend([index[target], index[source]])
    if not rows:
        return {"lambda_2": 0.0, "method": "empty_edge_set", "spectral_failure": None}

    data = np.ones(len(rows), dtype=np.float64)
    adjacency = sparse.coo_matrix((data, (rows, cols)), shape=(len(node_ids), len(node_ids))).tocsr()
    component_count = csgraph.connected_components(adjacency, directed=False, return_labels=False)
    if int(component_count) > 1:
        return {"lambda_2": 0.0, "method": "disconnected_graph_exact_zero", "spectral_failure": None}
    laplacian = csgraph.laplacian(adjacency, normed=False).astype(np.float64)
    try:
        values = eigsh(laplacian, k=2, which="SM", return_eigenvectors=False, tol=1e-8)
        values = np.sort(values)
        return {"lambda_2": _round(values[1]), "method": "eigsh_SM_k2_scipy_sparse", "spectral_failure": None}
    except Exception as exc:  # pragma: no cover - retained for LAPACK/ARPACK variance
        return {"lambda_2": 0.0, "method": "spectral_fallback_zero", "spectral_failure": type(exc).__name__}


def _spectral_payload(
    *,
    graph: nx.Graph,
    repo_paths: dict[str, str],
    candidate_path: Path,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    components = sorted(nx.connected_components(graph), key=lambda item: (-len(item), sorted(item)[0] if item else ""))
    component_sizes = [len(component) for component in components]
    largest_component = sorted(components[0]) if components else []
    protocol_nodes = sorted(node_id for node_id, path in repo_paths.items() if _is_protocol_relevant(path))
    largest_component_set = set(largest_component)
    protocol_in_giant = [node_id for node_id in protocol_nodes if node_id in largest_component_set]
    full_lambda = _lambda2_for_nodes(graph, sorted(graph.nodes()))
    giant_lambda = _lambda2_for_nodes(graph, largest_component)
    bridges = sorted(tuple(sorted(edge)) for edge in nx.bridges(graph))

    baseline_bridge = baseline.get("bridge_and_articulation_pressure", {}).get("bridge_count")
    baseline_lambda = baseline.get("spectral_diagnostics", {}).get("clique_incidence_projection", {}).get("lambda2")

    return {
        "baseline": {
            "bridge_count": baseline_bridge,
            "lambda_2_clique_incidence": baseline_lambda,
            "source": "out/sim_atlas_spectral_non_excisability_1545p_fix29.json",
        },
        "bridge_count": len(bridges),
        "bridge_sample": [{"source": s, "target": t} for s, t in bridges[:50]],
        "candidate_sha256": _sha256(candidate_path),
        "candidate_source": "genesis_atlas_enriched_candidate_fix41a.json",
        "giant_component_fraction": _round(component_sizes[0] / graph.number_of_nodes()) if graph.number_of_nodes() else 0.0,
        "giant_component_node_count": component_sizes[0] if component_sizes else 0,
        "giant_component_protocol_fraction": _round(len(protocol_in_giant) / len(protocol_nodes)) if protocol_nodes else 0.0,
        "lambda_2": full_lambda["lambda_2"],
        "lambda_2_method": full_lambda["method"],
        "largest_component_lambda_2": giant_lambda["lambda_2"],
        "largest_component_lambda_2_method": giant_lambda["method"],
        "non_claims": NON_CLAIMS,
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "phase": PHASE,
        "protocol_relevant_node_count": len(protocol_nodes),
        "schema_version": SCHEMA_VERSION,
        "spectral_failure": full_lambda["spectral_failure"] or giant_lambda["spectral_failure"],
        "status": "PASS",
        "tokens": OUTPUT_TOKENS[:1],
        "weakly_connected_components": component_sizes,
    }


def _pagerank_payload(
    *,
    graph: nx.Graph,
    node_records: dict[str, dict[str, Any]],
    repo_paths: dict[str, str],
    edge_types_by_node: dict[str, set[str]],
) -> dict[str, Any]:
    pagerank = nx.pagerank(graph, alpha=0.85, tol=1e-10, max_iter=200)
    betweenness_k = min(64, graph.number_of_nodes())
    betweenness = (
        nx.betweenness_centrality(graph, k=betweenness_k, seed=0, normalized=True)
        if betweenness_k
        else {}
    )

    rows = []
    for node_id in sorted(graph.nodes()):
        repo_path = repo_paths.get(node_id, "")
        rows.append(
            {
                "betweenness_centrality": _round(betweenness.get(node_id, 0.0)),
                "current_edge_types": sorted(edge_types_by_node.get(node_id, set())),
                "in_degree": int(graph.degree(node_id)),
                "is_protocol_relevant": _is_protocol_relevant(repo_path),
                "node_id": node_id,
                "node_kind": str(node_records.get(node_id, {}).get("node_kind", "")),
                "out_degree": int(graph.degree(node_id)),
                "pagerank_score": _round(pagerank.get(node_id, 0.0), 16),
                "repo_path": repo_path,
            }
        )

    return {
        "betweenness_method": f"networkx_betweenness_centrality_k{betweenness_k}_seed0_deterministic_research_only",
        "candidate_source": "genesis_atlas_enriched_candidate_fix41a.json",
        "non_claims": NON_CLAIMS,
        "node_count": len(rows),
        "nodes": rows,
        "pagerank_method": "networkx_pagerank_alpha_0_85_tol_1e_10",
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "tokens": ["fix43_pagerank_complete"],
    }

def _queue_payload(pagerank_payload: dict[str, Any]) -> dict[str, Any]:
    protocol_rows = [
        row
        for row in pagerank_payload["nodes"]
        if row["is_protocol_relevant"] and not row["repo_path"].startswith(EXCLUDED_TARGET_PREFIXES)
    ]
    protocol_rows.sort(
        key=lambda row: (
            row["pagerank_score"],
            row["betweenness_centrality"],
            row["repo_path"],
            row["node_id"],
        )
    )
    entries = [
        {
            "betweenness_centrality": row["betweenness_centrality"],
            "current_edge_types": row["current_edge_types"],
            "in_degree": row["in_degree"],
            "node_id": row["node_id"],
            "out_degree": row["out_degree"],
            "pagerank_score": row["pagerank_score"],
            "repo_path": row["repo_path"],
        }
        for row in protocol_rows[:500]
    ]
    return {
        "candidate_source": "genesis_atlas_enriched_candidate_fix41a.json",
        "entry_count": len(entries),
        "entries": entries,
        "excluded_prefixes": list(EXCLUDED_TARGET_PREFIXES),
        "filter": "protocol_relevant_only_lowest_pagerank_bottom_500",
        "non_claims": NON_CLAIMS,
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "tokens": ["fix43_fix44_target_queue_produced"],
    }


def _assessment(spectral: dict[str, Any]) -> str:
    if spectral["giant_component_protocol_fraction"] >= 0.95 and spectral["largest_component_lambda_2"] > 0:
        return "crossed"
    if spectral["giant_component_protocol_fraction"] >= 0.80:
        return "approaching"
    return "not_yet_crossed"


def _report(spectral: dict[str, Any], queue: dict[str, Any]) -> str:
    baseline = spectral["baseline"]
    lambda_delta = _round(spectral["largest_component_lambda_2"] - float(baseline["lambda_2_clique_incidence"]))
    bridge_delta = int(spectral["bridge_count"]) - int(baseline["bridge_count"])
    pageranks = [entry["pagerank_score"] for entry in queue["entries"]]
    min_pr = min(pageranks) if pageranks else 0.0
    max_pr = max(pageranks) if pageranks else 0.0
    by_dir = Counter(entry["repo_path"].split("/", 1)[0] for entry in queue["entries"])
    top_dirs = ", ".join(f"{name}: {count}" for name, count in by_dir.most_common(8))
    if len(spectral["weakly_connected_components"]) == 1:
        full_lambda_note = (
            f"Full-graph λ₂ is `{spectral['lambda_2']}` because the analyzed "
            "simple graph projection is connected."
        )
    else:
        full_lambda_note = (
            f"Full-graph λ₂ is `{spectral['lambda_2']}` because disconnected "
            "components make the exact full-graph Fiedler value zero."
        )

    return f"""# Genesis Spectral Delta After Fix38/Fix41a

Status: research-only structural diagnostic; not protocol canon

## Summary

Phase 1545p-Fix43 measured the latest Fix41a enriched Genesis Atlas candidate
against the Fix29/SIM-SPECTRAL-02 baseline. Metrics are structural diagnostics
only. They do not prove authority, eligibility, claimability, governance effect,
or signing readiness.

## Delta Table

| Metric | Fix29/SIM-SPECTRAL-02 baseline | Fix43 result | Delta |
|---|---:|---:|---:|
| λ₂ / Fiedler value | `{baseline["lambda_2_clique_incidence"]}` | `{spectral["largest_component_lambda_2"]}` | `{lambda_delta}` |
| Bridge count | `{baseline["bridge_count"]}` | `{spectral["bridge_count"]}` | `{bridge_delta}` |
| Giant component fraction | `not_recorded_in_fix29_delta_table` | `{spectral["giant_component_fraction"]}` | `not_comparable` |
| Protocol-relevant node count | `not_recorded_in_fix29_delta_table` | `{spectral["protocol_relevant_node_count"]}` | `not_comparable` |
| Protocol-relevant giant fraction | `not_recorded_in_fix29_delta_table` | `{spectral["giant_component_protocol_fraction"]}` | `not_comparable` |

## Percolation Threshold Assessment

`percolation_threshold_assessment: {_assessment(spectral)}`

The giant component contains `{spectral["giant_component_protocol_fraction"]}`
of protocol-relevant nodes. The largest-component λ₂ is
`{spectral["largest_component_lambda_2"]}`. {full_lambda_note}

## Fix44 Target Queue

- Entry count: `{queue["entry_count"]}`
- Lowest PageRank in queue: `{_round(min_pr, 16)}`
- Highest PageRank in queue: `{_round(max_pr, 16)}`
- Directory distribution: `{top_dirs}`

The queue excludes `out/` and `.git/` material and is sorted by lowest
PageRank among protocol-relevant nodes. It is a target queue for review, not a
canonical edge mutation.

## Non-Claims

- No Genesis signing occurred.
- No canonical Atlas mutation occurred.
- No public graph publication occurred.
- No public repository push occurred.
- No public RC activation occurred.
- No runtime, economic, sidecar, network, ADR, or CDL activation occurred.
- Spectral, PageRank, bridge, and betweenness metrics are structural
  diagnostics only, not authority proof.
"""


def run(
    *,
    candidate_path: Path = CANDIDATE,
    baseline_path: Path = BASELINE,
    spectral_out: Path = SPECTRAL_OUT,
    pagerank_out: Path = PAGERANK_OUT,
    queue_out: Path = QUEUE_OUT,
    report_out: Path = REPORT_OUT,
) -> dict[str, Any]:
    candidate = _load_json(candidate_path)
    baseline = _load_json(baseline_path)
    graph, node_records, repo_paths, edge_types_by_node = _build_graph(candidate)

    spectral = _spectral_payload(
        graph=graph,
        repo_paths=repo_paths,
        candidate_path=candidate_path,
        baseline=baseline,
    )
    pagerank = _pagerank_payload(
        graph=graph,
        node_records=node_records,
        repo_paths=repo_paths,
        edge_types_by_node=edge_types_by_node,
    )
    queue = _queue_payload(pagerank)
    spectral["percolation_threshold_assessment"] = _assessment(spectral)
    spectral["tokens"] = OUTPUT_TOKENS

    _atomic_write(spectral_out, _pretty_json(spectral))
    _atomic_write(pagerank_out, _pretty_json(pagerank))
    _atomic_write(queue_out, _pretty_json(queue))
    _atomic_write(report_out, _report(spectral, queue))

    return {
        "pagerank": pagerank,
        "queue": queue,
        "spectral": spectral,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Fix43 spectral/PageRank diagnostics.")
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    args = parser.parse_args()
    payload = run(candidate_path=args.candidate, baseline_path=args.baseline)
    print(_canonical_json({"status": "PASS", "spectral": payload["spectral"], "queue_count": payload["queue"]["entry_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
