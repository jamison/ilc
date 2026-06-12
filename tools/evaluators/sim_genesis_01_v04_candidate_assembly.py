#!/usr/bin/env python3
"""SIM-GENESIS-01: assemble an unsigned v0.4 Genesis core star-map candidate.

PUBLIC_RC_EXCLUDE: genesis_successor_manifest_sim_private
PUBLIC_RC_EXCLUDE_REASON: support-only pre-public-RC SIM output; not canonical Genesis state
PUBLIC_RC_INCLUDE_REQUIRES: Block 6 public-RC gate, successor manifest review, and signing authority
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


DEFAULT_V03 = Path("out/genesis_core_star_map_v0.3_candidate.json")
DEFAULT_FIX7_QUEUE = Path("out/genesis_common_registry_node_candidates_1545p_fix7.json")
DEFAULT_FIX9_SCORES = Path("out/genesis_optimization_candidate_scores_1545p_fix9.json")
DEFAULT_OBSERVED = Path("out/genesis_observed_repo_hypergraph_v0.1.json")
DEFAULT_V04 = Path("out/genesis_core_star_map_v0.4_candidate.json")
DEFAULT_JSON_OUT = Path("out/sim_genesis_01_v04_candidate_assembly_1545p_fix18.json")
DEFAULT_REPORT_OUT = Path("docs/sims/sim_genesis_01_v04_candidate_assembly_1545p_fix18_v0.1.md")

GENESIS_ATTESTATION_ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SIM_ID = "SIM-GENESIS-01"
MODEL_VERSION = "sim_genesis_01_v04_candidate_assembly.v0.1"
PHASE_ID = "1545p-Fix18"


NODE_OVERRIDES: dict[str, dict[str, Any]] = {
    "adr:0009_protocol_native_bundle_distribution": {
        "category": "protocol_native_distribution",
        "edge_hints": ["GOVERNS", "ATTESTATION", "CONTENT_ADDRESSING"],
        "economic_boundary": "none",
        "label": "ADR-0009 protocol-native bundle distribution",
        "layer": "L2_protocol_distribution",
        "node_kind": "protocol_architecture_authority",
        "source_kind": "adr",
    },
    "adr:0035_type_definition_authority": {
        "category": "homoiconic_type_authority",
        "edge_hints": ["GOVERNS", "ATTESTATION", "TYPE_DEFINITION"],
        "economic_boundary": "none",
        "label": "ADR-0035 homoiconic type definition authority",
        "layer": "L1_type_authority",
        "node_kind": "type_definition_authority",
        "source_kind": "adr",
    },
    "cdl:096_werner_global_tier_authority": {
        "category": "constitutional_flow_and_finality_authority",
        "edge_hints": ["GOVERNS", "ATTESTATION", "FLOW_CONTROL", "JURY_FINALITY"],
        "economic_boundary": "not_ecu_not_ilc_not_claimability",
        "label": "CDL-096 Werner flow-governor and global-tier jury authority",
        "layer": "L3_constitutional_authority",
        "node_kind": "constitutional_authority",
        "source_kind": "spec",
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json_object_required:{path}")
    return data


def _canonical_dumps(data: Any) -> str:
    return json.dumps(data, allow_nan=False, indent=2, sort_keys=True) + "\n"


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _evidence_for(candidate_id: str, evidence_paths: list[str]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for raw_path in evidence_paths:
        path = Path(raw_path)
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            first_nonblank = next((line.strip() for line in text.splitlines() if line.strip()), "")
            digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        else:
            first_nonblank = "source path not present at SIM execution time"
            digest = _sha256_text(f"{candidate_id}:{raw_path}:missing")
        evidence.append(
            {
                "evidence_hash": digest,
                "evidence_text": first_nonblank[:240],
                "source_line": 1,
                "source_path": raw_path,
            }
        )
    return evidence


def _node_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    override = NODE_OVERRIDES[candidate_id]
    return {
        "applies_to": [],
        "attestation_type": "successor_candidate",
        "authority_status": "successor_candidate_support_only",
        "candidate_id": candidate_id,
        "canonicality_tier": "unsigned_successor_candidate",
        "category": override["category"],
        "confidence": 1.0,
        "core_star_map_candidate": True,
        "decision_log_refs": ["phase_1545p_fix6", "phase_1545p_fix7", "phase_1545p_fix9"],
        "depth_index": None,
        "economic_boundary": override["economic_boundary"],
        "economic_cap_policy": None,
        "edge_hints": override["edge_hints"],
        "evidence": _evidence_for(candidate_id, list(candidate.get("evidence_paths", []))),
        "genesis_attested": False,
        "genesis_attested_by": None,
        "genesis_exempt": False,
        "graph_projection": "core_star_map",
        "inclusion_status": "must_include",
        "label": override["label"],
        "layer": override["layer"],
        "node_kind": override["node_kind"],
        "promotion_path": "successor_manifest_candidate_requires_block6_signing",
        "rationale": candidate.get("notes", ""),
        "reuse_economic_surface": "not_economic_runtime",
        "sensitivity": "NON-SENSITIVE",
        "signature_envelope_ref": None,
        "signature_file_ref": None,
        "signature_scope": "unsigned_successor_manifest_candidate_v0.4",
        "signature_status": "unsigned_support_only",
        "signing_key_ref": None,
        "source_kind": override["source_kind"],
        "star_map_version": "v0.4_candidate",
        "sunset_status": "not_applicable",
        "superseded_by": None,
        "symbol": None,
        "valid_epoch_range": [0, None],
        "value": None,
        "version": "v0.4_candidate",
    }


def _edge_for(candidate_id: str) -> dict[str, Any]:
    edge_stem = (
        candidate_id.replace(":", "_")
        .replace("-", "_")
        .replace(".", "_")
    )
    return {
        "confidence": 0.92,
        "decision_log_refs": ["phase_1545p_fix6", "phase_1545p_fix7"],
        "decomposition_recipe": {
            "composition": "attest.successor_candidate(authority_root, candidate) then govern.successor_manifest(candidate)",
            "distinction_rationale": "support-only successor-manifest edge; does not sign or activate the target",
            "distinguishes_from": "RUNTIME_ACTIVATION",
            "irreducible": False,
            "primitives": ["attest.successor_candidate", "govern.successor_manifest"],
            "scope": "successor_genesis_manifest_candidate",
        },
        "edge_id": f"edge:v04_attestation_to_{edge_stem}",
        "edge_type": "GOVERNS",
        "feature_hints": {
            "directional": True,
            "edge_type_status": "support_only_successor_candidate",
            "layer_span": "L3_to_successor_candidate",
            "proposed_edge_type": False,
            "sim_weight_seed": 0.92,
        },
        "rationale": "The Genesis attestation root is the support-only authority trace for post-v0.3 must-include successor manifest candidates.",
        "relation": "records_successor_manifest_candidate",
        "source": GENESIS_ATTESTATION_ROOT,
        "target": candidate_id,
    }


def _select_candidates(queue: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = queue.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("fix7_candidate_queue_missing_candidates")

    selected = [
        candidate for candidate in candidates
        if candidate.get("classification") == "must_include_genesis_node"
    ]
    deferred = [
        candidate for candidate in candidates
        if candidate.get("classification") != "must_include_genesis_node"
    ]
    selected_ids = {str(candidate.get("candidate_id")) for candidate in selected}
    expected_ids = set(NODE_OVERRIDES)
    if selected_ids != expected_ids:
        raise ValueError(
            "must_include_candidate_set_mismatch:"
            f"expected={sorted(expected_ids)} actual={sorted(selected_ids)}"
        )
    return sorted(selected, key=lambda item: str(item["candidate_id"])), deferred


def _endpoint_errors(graph: dict[str, Any]) -> list[dict[str, str]]:
    node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    errors: list[dict[str, str]] = []
    for edge in graph["edges"]:
        source = str(edge["source"])
        target = str(edge["target"])
        if source not in node_ids:
            errors.append({"edge_id": edge["edge_id"], "missing": source, "role": "source"})
        if target not in node_ids:
            errors.append({"edge_id": edge["edge_id"], "missing": target, "role": "target"})
    return errors


def _basis_roots(graph: dict[str, Any]) -> set[str]:
    node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    roots = set(graph["metadata"].get("transition_basis", []))
    roots.update(
        {
            "adr:0004_genesis_truth_primitives",
            "axiom:logic:01",
            "axiom:math:01",
            "axiom:physics:01",
            "genesis_agent:01",
            GENESIS_ATTESTATION_ROOT,
            "artifact:genesis_agent1_pubkey_record_838a",
            "ceremony:genesis_agent1_keygen_838a",
        }
    )
    return roots & node_ids


def _reachable_nodes(graph: dict[str, Any], roots: set[str], edge_types: set[str] | None = None) -> set[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        if edge_types is None or edge["edge_type"] in edge_types:
            adjacency[str(edge["source"])].add(str(edge["target"]))
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


def _score_summary(scores: dict[str, Any]) -> dict[str, Any]:
    objective_vector = scores.get("objective_vector", {})
    if not isinstance(objective_vector, dict):
        objective_vector = {}
    return {
        "diagnostic_verdict": scores.get("diagnostic_verdict"),
        "harness_id": scores.get("harness_id"),
        "objective_vector": objective_vector,
        "source_coverage_baseline_ratio": scores.get("source_coverage_baseline_ratio"),
    }


def _assemble(
    v03: dict[str, Any],
    queue: dict[str, Any],
    scores: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    selected, deferred = _select_candidates(queue)
    selected_nodes = [_node_from_candidate(candidate) for candidate in selected]
    selected_edges = [_edge_for(str(candidate["candidate_id"])) for candidate in selected]

    graph = copy.deepcopy(v03)
    existing_node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    duplicate_nodes = sorted(existing_node_ids & {node["candidate_id"] for node in selected_nodes})
    if duplicate_nodes:
        raise ValueError(f"v04_candidate_duplicate_node_ids:{duplicate_nodes}")

    existing_edge_ids = {str(edge["edge_id"]) for edge in graph["edges"]}
    duplicate_edges = sorted(existing_edge_ids & {edge["edge_id"] for edge in selected_edges})
    if duplicate_edges:
        raise ValueError(f"v04_candidate_duplicate_edge_ids:{duplicate_edges}")

    graph["nodes"].extend(selected_nodes)
    graph["edges"].extend(selected_edges)
    graph["nodes"] = sorted(graph["nodes"], key=lambda item: str(item["candidate_id"]))
    graph["edges"] = sorted(graph["edges"], key=lambda item: str(item["edge_id"]))

    metadata = copy.deepcopy(graph.get("metadata", {}))
    metadata.update(
        {
            "derived_from": str(DEFAULT_V03),
            "description": "Unsigned support-only Genesis core star-map v0.4 candidate assembled from post-v0.3 must-include governance candidates.",
            "fix7_candidate_queue": str(DEFAULT_FIX7_QUEUE),
            "fix9_objective_harness": str(DEFAULT_FIX9_SCORES),
            "format_version": "genesis_core_star_map_v0.4_candidate",
            "public_path": "blocked",
            "signature_status": "unsigned_support_only",
            "successor_candidate_phase": PHASE_ID,
            "successor_candidate_status": "support_only_not_canonical",
            "successor_deferred_candidate_count": len(deferred),
            "successor_selected_candidate_count": len(selected),
        }
    )
    graph["metadata"] = metadata

    endpoint_errors = _endpoint_errors(graph)
    node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    roots = _basis_roots(graph)
    basis_reachable = _reachable_nodes(graph, roots) & node_ids
    authority_traceable = (
        _reachable_nodes(graph, {GENESIS_ATTESTATION_ROOT}, {"GOVERNS", "ATTESTATION"})
        - {GENESIS_ATTESTATION_ROOT}
    ) & node_ids

    metrics = {
        "assembly": {
            "baseline_edge_count": len(v03["edges"]),
            "baseline_node_count": len(v03["nodes"]),
            "deferred_candidate_count": len(deferred),
            "deferred_candidate_ids": sorted(str(item["candidate_id"]) for item in deferred),
            "selected_candidate_count": len(selected),
            "selected_candidate_ids": sorted(str(item["candidate_id"]) for item in selected),
            "v04_edge_count": len(graph["edges"]),
            "v04_node_count": len(graph["nodes"]),
        },
        "authority_traceability": {
            "authority_traceable_node_count": len(authority_traceable),
            "authority_traceable_ratio": f"{len(authority_traceable)}/{len(node_ids)}",
            "new_nodes_authority_traceable": sorted(
                node["candidate_id"]
                for node in selected_nodes
                if node["candidate_id"] in authority_traceable
            ),
        },
        "basis_reachability": {
            "basis_reachable_node_count": len(basis_reachable),
            "basis_reachable_ratio": f"{len(basis_reachable)}/{len(node_ids)}",
        },
        "edge_endpoint_validity": {
            "invalid_endpoint_count": len(endpoint_errors),
            "invalid_endpoints": endpoint_errors,
        },
        "fix9_score_context": _score_summary(scores),
        "signals": {
            "observed_baseline": "out/genesis_core_star_map_v0.3_candidate.json",
            "observed_queue": "out/genesis_common_registry_node_candidates_1545p_fix7.json",
            "observed_scores": "out/genesis_optimization_candidate_scores_1545p_fix9.json",
            "synthetic_output": "out/genesis_core_star_map_v0.4_candidate.json",
        },
    }
    return graph, metrics


def _report(metrics: dict[str, Any]) -> str:
    assembly = metrics["assembly"]
    endpoints = metrics["edge_endpoint_validity"]
    authority = metrics["authority_traceability"]
    basis = metrics["basis_reachability"]
    selected = assembly["selected_candidate_ids"]
    deferred = assembly["deferred_candidate_ids"]
    lines = [
        "# SIM-GENESIS-01 v0.4 Candidate Assembly 1545p-Fix18 v0.1",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: genesis_successor_manifest_sim_private -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: support-only SIM report; not canonical Genesis state -->",
        "",
        f"**SIM ID:** `{SIM_ID}`",
        f"**Model version:** `{MODEL_VERSION}`",
        f"**Phase:** `{PHASE_ID}`",
        "**Status:** deterministic support-only SIM; advisory, not authority",
        "",
        "## Signal Definition",
        "",
        "- `selected_candidate_count`: number of Fix7 candidates classified as `must_include_genesis_node`.",
        "- `deferred_candidate_count`: number of Fix7 candidates left in the common/sidecar/research queue.",
        "- `edge_endpoint_validity`: whether every v0.4 candidate edge endpoint resolves to an existing node.",
        "- `basis_reachability`: authority-basis reachability over the assembled v0.4 candidate graph.",
        "- `authority_traceability`: reachability from the Genesis attestation root via `GOVERNS` / `ATTESTATION` edges.",
        "",
        "## Input Separation",
        "",
        "- Observed baseline input: `out/genesis_core_star_map_v0.3_candidate.json`.",
        "- Observed candidate queue: `out/genesis_common_registry_node_candidates_1545p_fix7.json`.",
        "- Observed optimization context: `out/genesis_optimization_candidate_scores_1545p_fix9.json`.",
        "- Synthetic/support-only output: `out/genesis_core_star_map_v0.4_candidate.json`.",
        "",
        "## Findings",
        "",
        f"- Baseline v0.3 graph: `{assembly['baseline_node_count']}` nodes / `{assembly['baseline_edge_count']}` edges.",
        f"- v0.4 candidate graph: `{assembly['v04_node_count']}` nodes / `{assembly['v04_edge_count']}` edges.",
        f"- Selected must-include candidates: `{assembly['selected_candidate_count']}`.",
        f"- Deferred queue candidates: `{assembly['deferred_candidate_count']}`.",
        f"- Invalid edge endpoints: `{endpoints['invalid_endpoint_count']}`.",
        f"- Basis-reachable nodes: `{basis['basis_reachable_ratio']}`.",
        f"- Authority-traceable nodes: `{authority['authority_traceable_ratio']}`.",
        "",
        "## Selected v0.4 Additions",
        "",
    ]
    lines.extend(f"- `{candidate_id}`" for candidate_id in selected)
    lines.extend(
        [
            "",
            "## Deferred Candidate Queue",
            "",
        ]
    )
    lines.extend(f"- `{candidate_id}`" for candidate_id in deferred)
    lines.extend(
        [
            "",
            "## Disposition",
            "",
            "The SIM assembles the unsigned v0.4 candidate by promoting only the three Fix7 `must_include_genesis_node` entries. "
            "It does not promote common nodes, sidecar recipes, reward mechanics, visualization affordances, or research methods into Genesis core.",
            "",
            "The v0.4 candidate artifact is support-only and not canonical. It does not mutate the signed v0.3 baseline, does not sign a successor manifest, "
            "does not activate public RC, and does not authorize any runtime, economic, or sidecar behavior. Canonical successor-manifest authority remains gated by Block 6 / `PUBLIC-RC-GATE-001`.",
            "",
            "## Output Tokens",
            "",
            "- `sim_genesis_01_v04_candidate_assembly_committed_phase_1545p_fix18`",
            "- `genesis_v04_candidate_assembled_phase_1545p_fix18`",
            "- `genesis_v04_candidate_unsigned_support_only_phase_1545p_fix18`",
            "- `fix7_must_include_candidates_consumed_phase_1545p_fix18`",
            "- `public_path_remains_blocked_phase_1545p_fix18`",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    v03_path: Path = DEFAULT_V03,
    fix7_queue_path: Path = DEFAULT_FIX7_QUEUE,
    fix9_scores_path: Path = DEFAULT_FIX9_SCORES,
    v04_path: Path = DEFAULT_V04,
    json_out_path: Path = DEFAULT_JSON_OUT,
    report_out_path: Path = DEFAULT_REPORT_OUT,
) -> dict[str, Any]:
    v03 = _read_json(v03_path)
    queue = _read_json(fix7_queue_path)
    scores = _read_json(fix9_scores_path)
    graph, metrics = _assemble(v03, queue, scores)

    payload = {
        "artifact_status": "support_only_sim_output",
        "authority_status": "not_authority_bearing",
        "canonicality": "unsigned_not_canonical",
        "graph_output": str(v04_path),
        "metrics": metrics,
        "model_version": MODEL_VERSION,
        "non_claims": [
            "no_signed_successor_manifest",
            "no_genesis_canonical_mutation",
            "no_public_rc",
            "no_public_repo_push",
            "no_runtime_activation",
            "no_economic_activation",
            "no_sidecar_activation",
        ],
        "phase": PHASE_ID,
        "public_path": "blocked",
        "sim_id": SIM_ID,
        "tokens": [
            "sim_genesis_01_v04_candidate_assembly_committed_phase_1545p_fix18",
            "genesis_v04_candidate_assembled_phase_1545p_fix18",
            "genesis_v04_candidate_unsigned_support_only_phase_1545p_fix18",
            "fix7_must_include_candidates_consumed_phase_1545p_fix18",
            "public_path_remains_blocked_phase_1545p_fix18",
        ],
    }

    _atomic_write_text(v04_path, _canonical_dumps(graph))
    _atomic_write_text(json_out_path, _canonical_dumps(payload))
    _atomic_write_text(report_out_path, _report(metrics))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v03", type=Path, default=DEFAULT_V03)
    parser.add_argument("--fix7-queue", type=Path, default=DEFAULT_FIX7_QUEUE)
    parser.add_argument("--fix9-scores", type=Path, default=DEFAULT_FIX9_SCORES)
    parser.add_argument("--v04-out", type=Path, default=DEFAULT_V04)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    args = parser.parse_args()
    payload = run(
        v03_path=args.v03,
        fix7_queue_path=args.fix7_queue,
        fix9_scores_path=args.fix9_scores,
        v04_path=args.v04_out,
        json_out_path=args.json_out,
        report_out_path=args.report_out,
    )
    print(_canonical_dumps(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
