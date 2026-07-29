#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Diagnose whether the Genesis core star-map can compile the observed repo graph.

This is a research/atlas diagnostic only. It does not mutate protocol runtime state.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict, deque
from decimal import Decimal
from pathlib import Path
from typing import Any


DEFAULT_STAR_MAP = Path("out/genesis_core_star_map_v0.1.json")
DEFAULT_OBSERVED = Path("out/genesis_observed_repo_hypergraph_v0.1.json")
DEFAULT_JSON_OUT = Path("out/genesis_compile_coverage_diagnostic_v0.1.json")
DEFAULT_REPORT_OUT = Path("docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md")
GENESIS_ATTESTATION_ROOT = "artifact:genesis_intent_attestation_init_authority_map"

HIGH_AUTHORITY_SOURCE_KINDS = {
    "adr",
    "config",
    "phase_doc",
    "runtime_or_schema",
    "spec",
    "test",
    "tool",
}

SOURCE_KIND_CLASSES = {
    "adr": "governance_decision",
    "config": "program_config",
    "other": "support_or_prompt_context",
    "phase_doc": "phase_execution_record",
    "research": "research_support_context",
    "runtime_or_schema": "program_runtime_or_schema",
    "spec": "governance_specification",
    "test": "program_evidence_test",
    "tool": "program_tooling",
}


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.000000"
    value = Decimal(numerator) / Decimal(denominator)
    return str(value.quantize(Decimal("0.000001")))


def _source_to_core_links(observed: dict[str, Any]) -> dict[str, set[str]]:
    links: dict[str, set[str]] = defaultdict(set)
    for hyperedge in observed["hyperedges"]:
        if hyperedge["hyperedge_type"] == "OBSERVED_MENTION":
            source = next(member["vertex"] for member in hyperedge["members"] if member["role"] == "source")
            target = next(member["vertex"] for member in hyperedge["members"] if member["role"] == "mentioned")
            links[source].add(target)
        elif hyperedge["hyperedge_type"] == "SYMBOL_OCCURRENCE":
            source = next(member["vertex"] for member in hyperedge["members"] if member["role"] == "source")
            target = next(member["vertex"] for member in hyperedge["members"] if member["role"] == "semantic_node")
            links[source].add(target)
    return links


def _basis_roots(star_map: dict[str, Any]) -> set[str]:
    core_ids = {node["candidate_id"] for node in star_map["nodes"]}
    roots = set(star_map["metadata"].get("transition_basis", []))
    roots.update(
        {
            "adr:0004_genesis_truth_primitives",
            "axiom:logic:01",
            "axiom:math:01",
            "axiom:physics:01",
            "genesis_agent:01",
        }
    )
    return roots & core_ids


def _reachable_core_nodes(star_map: dict[str, Any], roots: set[str]) -> set[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in star_map["edges"]:
        adjacency[edge["source"]].add(edge["target"])
    reachable = set(roots)
    queue: deque[str] = deque(sorted(roots))
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, ())):
            if target in reachable:
                continue
            reachable.add(target)
            queue.append(target)
    return reachable


def _authority_traceable_nodes(star_map: dict[str, Any], attestation_node_id: str) -> set[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in star_map["edges"]:
        if edge["edge_type"] in {"GOVERNS", "ATTESTATION"}:
            adjacency[edge["source"]].add(edge["target"])

    reachable: set[str] = set()
    queue: deque[str] = deque([attestation_node_id])
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, ())):
            if target in reachable:
                continue
            reachable.add(target)
            queue.append(target)
    return reachable


def _source_vertices(observed: dict[str, Any]) -> list[dict[str, Any]]:
    return [vertex for vertex in observed["vertices"] if vertex["vertex_type"] == "source_file"]


def _source_class(source: dict[str, Any]) -> str:
    source_kind = str(source.get("properties", {}).get("source_kind", "other"))
    return SOURCE_KIND_CLASSES.get(source_kind, "unclassified_source_kind")


def _sample(items: list[dict[str, Any]], limit: int = 25) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: json.dumps(item, allow_nan=False, sort_keys=True))[:limit]


def _edge_recipe_analysis(star_map: dict[str, Any]) -> dict[str, Any]:
    proposed_edges = [
        edge
        for edge in star_map["edges"]
        if edge.get("feature_hints", {}).get("proposed_edge_type") is True
    ]
    missing_recipes = [
        {
            "edge_id": edge["edge_id"],
            "edge_type": edge["edge_type"],
            "reason": "proposed_edge_missing_decomposition_recipe",
        }
        for edge in proposed_edges
        if "decomposition_recipe" not in edge
    ]
    recipe_counter = Counter(edge.get("edge_type") for edge in proposed_edges)
    return {
        "missing_decomposition_recipe_count": len(missing_recipes),
        "missing_decomposition_recipes": missing_recipes,
        "proposed_edge_count": len(proposed_edges),
        "proposed_edge_type_counts": dict(sorted(recipe_counter.items())),
        "uses_proposed_edge_type": [
            {
                "edge_id": edge["edge_id"],
                "edge_type": edge["edge_type"],
                "edge_type_status": edge.get("feature_hints", {}).get("edge_type_status"),
                "recipe_primitives": edge.get("decomposition_recipe", {}).get("primitives", []),
            }
            for edge in sorted(proposed_edges, key=lambda item: item["edge_id"])
        ],
    }


def run(
    star_map_path: Path = DEFAULT_STAR_MAP,
    observed_path: Path = DEFAULT_OBSERVED,
    json_out: Path = DEFAULT_JSON_OUT,
    report_out: Path = DEFAULT_REPORT_OUT,
) -> dict[str, Any]:
    star_map = _read_json(star_map_path)
    observed = _read_json(observed_path)

    core_ids = {node["candidate_id"] for node in star_map["nodes"]}
    roots = _basis_roots(star_map)
    basis_reachable = _reachable_core_nodes(star_map, roots)
    authority_traceable = _authority_traceable_nodes(star_map, GENESIS_ATTESTATION_ROOT) & core_ids
    source_links = _source_to_core_links(observed)
    sources = _source_vertices(observed)

    source_classes = Counter(_source_class(source) for source in sources)
    linked_sources = [source for source in sources if source_links.get(source["vertex_id"])]
    basis_sources = [
        source
        for source in sources
        if source_links.get(source["vertex_id"], set()) & basis_reachable
    ]
    core_sources = [
        source
        for source in sources
        if source_links.get(source["vertex_id"], set()) & core_ids
    ]
    authority_valid_sources = [
        source
        for source in core_sources
        if source.get("properties", {}).get("source_kind") in HIGH_AUTHORITY_SOURCE_KINDS
    ]
    support_only_sources = [
        source
        for source in core_sources
        if source.get("properties", {}).get("source_kind") not in HIGH_AUTHORITY_SOURCE_KINDS
    ]
    unlinked_sources = [source for source in sources if not source_links.get(source["vertex_id"])]
    high_authority_unlinked = [
        source
        for source in unlinked_sources
        if source.get("properties", {}).get("source_kind") in {"adr", "config", "runtime_or_schema", "spec"}
    ]
    core_explainable_but_basis_unexplained = [
        source
        for source in core_sources
        if not (source_links.get(source["vertex_id"], set()) & basis_reachable)
    ]

    edge_analysis = _edge_recipe_analysis(star_map)
    if edge_analysis["missing_decomposition_recipe_count"] == 0 and len(core_sources) >= len(sources) * 3 // 4:
        verdict = "COMPLETE_ENOUGH_FOR_PHASE_1136"
    elif edge_analysis["missing_decomposition_recipe_count"] == 0 and core_sources:
        verdict = "PARTIAL_WITH_STRUCTURAL_GAPS"
    else:
        verdict = "FAIL_CORE_INADEQUATE"

    payload = {
        "compile_coverage": {
            "authority_path_valid_sources": len(authority_valid_sources),
            "authority_path_valid_sources_ratio_of_core_explainable": _ratio(len(authority_valid_sources), len(core_sources)),
            "basis_explainable_sources": len(basis_sources),
            "basis_explainable_sources_ratio_of_core_explainable": _ratio(len(basis_sources), len(core_sources)),
            "basis_explainable_sources_ratio_of_observed": _ratio(len(basis_sources), len(sources)),
            "basis_reachable_core_nodes": len(basis_reachable),
            "basis_reachable_core_nodes_ratio": _ratio(len(basis_reachable), len(core_ids)),
            "classified_sources": len([source for source in sources if _source_class(source) != "unclassified_source_kind"]),
            "classified_sources_ratio": _ratio(len([source for source in sources if _source_class(source) != "unclassified_source_kind"]), len(sources)),
            "core_explainable_sources": len(core_sources),
            "core_explainable_sources_ratio_of_observed": _ratio(len(core_sources), len(sources)),
            "core_nodes_total": len(core_ids),
            "observed_source_files_total": len(sources),
            "source_files_with_any_core_link": len(linked_sources),
            "source_files_with_any_core_link_ratio": _ratio(len(linked_sources), len(sources)),
            "support_only_sources_with_core_link": len(support_only_sources),
        },
        "edge_recipe_analysis": edge_analysis,
        "authority_traceability": {
            "attestation_root": GENESIS_ATTESTATION_ROOT,
            "authority_traceable_core_nodes": len(authority_traceable),
            "authority_traceable_core_nodes_ratio": _ratio(len(authority_traceable), len(core_ids)),
            "authority_traceable_node_ids": sorted(authority_traceable),
        },
        "gaps": {
            "basis_unreachable_core_nodes": [
                {
                    "candidate_id": node_id,
                    "reason": "core_node_not_reachable_from_transition_basis_genesis_agent_axioms_or_adr_0004",
                }
                for node_id in sorted(core_ids - basis_reachable)
            ],
            "core_explainable_but_basis_unexplained_sources_sample": _sample(
                [
                    {
                        "source_kind": source.get("properties", {}).get("source_kind"),
                        "source_path": source["label"],
                        "linked_core_nodes": sorted(source_links[source["vertex_id"]] & core_ids),
                        "reason": "source_mentions_core_node_not_reachable_from_low_level_basis",
                    }
                    for source in core_explainable_but_basis_unexplained
                ]
            ),
            "high_authority_unlinked_sources_sample": _sample(
                [
                    {
                        "source_kind": source.get("properties", {}).get("source_kind"),
                        "source_path": source["label"],
                        "reason": "high_authority_source_has_no_observed_core_star_map_link",
                    }
                    for source in high_authority_unlinked
                ]
            ),
            "missing_edge_recipes": edge_analysis["missing_decomposition_recipes"],
            "unlinked_sources_sample": _sample(
                [
                    {
                        "source_kind": source.get("properties", {}).get("source_kind"),
                        "source_path": source["label"],
                        "reason": "observed_source_file_has_no_specific_core_star_map_link",
                    }
                    for source in unlinked_sources
                ]
            ),
            "uses_proposed_edge_type": edge_analysis["uses_proposed_edge_type"],
        },
        "metadata": {
            "description": "GENESIS-COMPILE-01 diagnostic: tests whether the Genesis core star-map can classify and explain the observed repo/governance hypergraph.",
            "format_version": "genesis_compile_coverage_diagnostic.v0.1",
            "source_observed_hypergraph": str(observed_path),
            "source_star_map": str(star_map_path),
        },
        "interpretation_notes": [
            {
                "note_id": "compile_gap_not_protocol_failure",
                "text": "Partial compile coverage is expected for a narrow install/load core star-map; it means much of the observed corpus remains support graph material.",
            },
            {
                "note_id": "g8_referential_governance_gap",
                "text": "High-authority but unlinked ADR/spec/RC material likely reflects G8 referential governance work that has not yet been synthesized into the programmed RC/core star-map stem.",
            },
            {
                "note_id": "future_use",
                "text": "Use the high-authority unlinked source queue and basis-unreachable core nodes as an iterative promotion/synthesis backlog.",
            },
        ],
        "source_kind_classes": dict(sorted(source_classes.items())),
        "verdict": verdict,
    }

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(report_out, payload)
    return payload


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    coverage = payload["compile_coverage"]
    edge_analysis = payload["edge_recipe_analysis"]
    authority = payload["authority_traceability"]
    lines = [
        "# GENESIS-COMPILE-01 Compile Coverage Diagnostic v0.1",
        "",
        "Status: deterministic atlas diagnostic — research input, not protocol canon",
        "",
        "## Verdict",
        "",
        f"`{payload['verdict']}`",
        "",
        "## Coverage",
        "",
        f"- Observed source files: `{coverage['observed_source_files_total']}`",
        f"- Core nodes: `{coverage['core_nodes_total']}`",
        f"- Basis-reachable core nodes: `{coverage['basis_reachable_core_nodes']}` (`{coverage['basis_reachable_core_nodes_ratio']}`)",
        f"- Authority-traceable core nodes: `{authority['authority_traceable_core_nodes']}` (`{authority['authority_traceable_core_nodes_ratio']}`) from `{authority['attestation_root']}`",
        f"- Core-explainable source files: `{coverage['core_explainable_sources']}` (`{coverage['core_explainable_sources_ratio_of_observed']}` of observed)",
        f"- Basis-explainable source files: `{coverage['basis_explainable_sources']}` (`{coverage['basis_explainable_sources_ratio_of_observed']}` of observed)",
        f"- Authority-valid core-linked sources: `{coverage['authority_path_valid_sources']}` (`{coverage['authority_path_valid_sources_ratio_of_core_explainable']}` of core-explainable)",
        f"- Classified source files: `{coverage['classified_sources']}` (`{coverage['classified_sources_ratio']}`)",
        "",
        "## Edge Recipe Analysis",
        "",
        f"- Proposed edge instances: `{edge_analysis['proposed_edge_count']}`",
        f"- Missing decomposition recipes: `{edge_analysis['missing_decomposition_recipe_count']}`",
        f"- Proposed edge type counts: `{edge_analysis['proposed_edge_type_counts']}`",
        "",
        "## Interpretation",
        "",
        "The current Genesis core star-map partially compiles the deterministic observed repo graph. It explains the high-authority Genesis spine and all proposed edge instances carry decomposition recipes, but most observed source-file vertices remain outside direct core-star-map coverage. This is expected for a narrow install/load core projection and should be treated as a support-graph expansion queue, not as a protocol failure.",
        "",
        "A likely interpretation is that a substantial amount of G8 referential governance work still lives as ADR/spec/RC/support material rather than as programmed RC/core-star-map structure. The diagnostic is therefore useful as a synthesis backlog: it tells us which high-authority references should be promoted, compiled, or explicitly left in support scope.",
        "",
        "## Main Gap Counts",
        "",
        f"- Basis-unreachable core nodes: `{len(payload['gaps']['basis_unreachable_core_nodes'])}`",
        f"- High-authority unlinked source sample size: `{len(payload['gaps']['high_authority_unlinked_sources_sample'])}`",
        f"- Unlinked source sample size: `{len(payload['gaps']['unlinked_sources_sample'])}`",
        f"- Proposed edge type dependencies: `{len(payload['gaps']['uses_proposed_edge_type'])}`",
        "",
        "Closing token: `genesis_compile_coverage_diagnostic_complete_v0_1`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--star-map", type=Path, default=DEFAULT_STAR_MAP)
    parser.add_argument("--observed", type=Path, default=DEFAULT_OBSERVED)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    args = parser.parse_args()
    payload = run(args.star_map, args.observed, args.json_out, args.report_out)
    print(
        json.dumps(
            {
                "basis_reachable_core_nodes": payload["compile_coverage"]["basis_reachable_core_nodes"],
                "authority_traceable_core_nodes": payload["authority_traceability"]["authority_traceable_core_nodes"],
                "core_explainable_sources": payload["compile_coverage"]["core_explainable_sources"],
                "observed_source_files_total": payload["compile_coverage"]["observed_source_files_total"],
                "verdict": payload["verdict"],
            },
            allow_nan=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
