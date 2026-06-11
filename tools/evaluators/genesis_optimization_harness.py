#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic support-only Genesis optimization harness.

PUBLIC_RC_EXCLUDE: genesis_optimization_harness_support_only_fix9
PUBLIC_RC_EXCLUDE_REASON: Internal pre-public Genesis candidate scoring helper.
It does not sign, mutate, publish, activate registries, or promote candidates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping


HARNESS_ID = "genesis_optimization_autoresearch_harness_phase_1545p_fix9"
ARTIFACT_STATUS = "support_only_candidate_evaluation"
AUTHORITY_STATUS = "not_authority_bearing"

OBJECTIVE_FIELDS: tuple[str, ...] = (
    "authority_traceability_preservation",
    "basis_reachability_preservation",
    "source_coverage_improvement",
    "decomposition_recipe_coverage",
    "edge_endpoint_validity",
    "minimality",
    "semantic_justification_strength",
    "registry_namespace_hygiene",
    "visualization_projection_clarity",
    "non_gaming_penalty",
)

REQUIRED_TRUTH_PRIMITIVES: tuple[str, ...] = (
    "truth_primitive:assert.truth",
    "truth_primitive:validate.claim",
    "truth_primitive:contradict.assert",
    "truth_primitive:refute.claim",
    "truth_primitive:revise.assert",
    "truth_primitive:link.claim",
    "truth_primitive:commit.epoch",
)

REQUIRED_AUTHORITY_NODES: tuple[str, ...] = (
    "genesis_agent:01",
    "artifact:genesis_agent1_pubkey_record_838a",
    "ceremony:genesis_agent1_keygen_838a",
    "artifact:genesis_authority_assertion_schema",
    "artifact:genesis_intent_attestation_init_authority_map",
)

_SIX = Decimal("0.000001")


@dataclass(frozen=True)
class HarnessInputs:
    candidate_path: Path
    baseline_path: Path
    diagnostic_path: Path
    registry_queue_path: Path


def _reject_constant(value: str) -> None:
    raise ValueError(f"genesis_optimization_non_standard_json_number:{value}")


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_float=Decimal,
        parse_int=int,
        parse_constant=_reject_constant,
    )


def _dump_canonical(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n"


def _decimal_ratio(numerator: int, denominator: int) -> Decimal:
    if denominator <= 0:
        return Decimal("0")
    return (Decimal(numerator) / Decimal(denominator)).quantize(_SIX)


def _decimal_str(value: Decimal) -> str:
    return str(value.quantize(_SIX))


def _candidate_ids(nodes: Any) -> set[str]:
    if not isinstance(nodes, list):
        return set()
    ids: set[str] = set()
    for node in nodes:
        if isinstance(node, Mapping):
            candidate_id = node.get("candidate_id")
            if isinstance(candidate_id, str) and candidate_id:
                ids.add(candidate_id)
    return ids


def _edge_endpoint_stats(edges: Any, node_ids: set[str]) -> tuple[int, int, list[str]]:
    if not isinstance(edges, list):
        return 0, 0, ["edges_missing_or_invalid"]
    valid = 0
    reasons: list[str] = []
    for edge in edges:
        if not isinstance(edge, Mapping):
            reasons.append("edge_not_object")
            continue
        edge_id = edge.get("edge_id")
        source = edge.get("source")
        target = edge.get("target")
        if source in node_ids and target in node_ids:
            valid += 1
        else:
            reasons.append(f"edge_endpoint_invalid:{edge_id}")
    return valid, len(edges), reasons


def _recipe_stats(edges: Any) -> tuple[int, int, list[str]]:
    if not isinstance(edges, list):
        return 0, 0, ["edges_missing_or_invalid"]
    valid = 0
    reasons: list[str] = []
    for edge in edges:
        if not isinstance(edge, Mapping):
            continue
        edge_id = edge.get("edge_id")
        recipe = edge.get("decomposition_recipe")
        if isinstance(recipe, Mapping) and recipe.get("primitives"):
            valid += 1
        else:
            reasons.append(f"decomposition_recipe_missing:{edge_id}")
    return valid, len(edges), reasons


def _contains_activation_claim(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        forbidden = (
            "activate public rc",
            "public rc activated",
            "activate registry",
            "mint ilc",
            "mint ecu",
            "settle ilc",
            "wallet write",
            "treasury write",
        )
        return any(token in lowered for token in forbidden)
    if isinstance(value, Mapping):
        return any(_contains_activation_claim(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_activation_claim(child) for child in value)
    return False


def _semantic_strength(data: Mapping[str, Any]) -> Decimal:
    nodes = data.get("nodes")
    edges = data.get("edges")
    checks = 0
    passed = 0
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, Mapping):
                continue
            checks += 2
            if node.get("rationale"):
                passed += 1
            evidence = node.get("evidence")
            if isinstance(evidence, list) and evidence:
                passed += 1
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, Mapping):
                continue
            checks += 2
            if edge.get("rationale"):
                passed += 1
            if isinstance(edge.get("decomposition_recipe"), Mapping):
                passed += 1
    return _decimal_ratio(passed, checks)


def _registry_namespace_hygiene(registry_queue: Mapping[str, Any]) -> Decimal:
    candidates = registry_queue.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return Decimal("0")
    ids: list[str] = []
    clean = 0
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = candidate.get("candidate_id")
        authority_status = candidate.get("authority_status")
        if isinstance(candidate_id, str) and candidate_id and authority_status == AUTHORITY_STATUS:
            clean += 1
            ids.append(candidate_id)
    if len(ids) != len(set(ids)):
        return Decimal("0")
    return _decimal_ratio(clean, len(candidates))


def build_genesis_optimization_evaluation(inputs: HarnessInputs) -> dict[str, Any]:
    candidate = _load_json(inputs.candidate_path)
    baseline = _load_json(inputs.baseline_path)
    diagnostic = _load_json(inputs.diagnostic_path)
    registry_queue = _load_json(inputs.registry_queue_path)

    reject_reasons: list[str] = []
    if not isinstance(candidate, Mapping):
        raise ValueError("genesis_optimization_candidate_not_object")
    if not isinstance(baseline, Mapping):
        raise ValueError("genesis_optimization_baseline_not_object")
    if not isinstance(diagnostic, Mapping):
        raise ValueError("genesis_optimization_diagnostic_not_object")
    if not isinstance(registry_queue, Mapping):
        raise ValueError("genesis_optimization_registry_queue_not_object")

    candidate_nodes = candidate.get("nodes")
    candidate_edges = candidate.get("edges")
    baseline_nodes = baseline.get("nodes")
    node_ids = _candidate_ids(candidate_nodes)

    missing_primitives = sorted(set(REQUIRED_TRUTH_PRIMITIVES) - node_ids)
    missing_authority = sorted(set(REQUIRED_AUTHORITY_NODES) - node_ids)
    if missing_primitives:
        reject_reasons.append("basis_reachability_required_nodes_missing")
    if missing_authority:
        reject_reasons.append("authority_traceability_required_nodes_missing")

    metadata = candidate.get("metadata")
    transition_basis = metadata.get("transition_basis") if isinstance(metadata, Mapping) else None
    if transition_basis != list(REQUIRED_TRUTH_PRIMITIVES):
        reject_reasons.append("transition_basis_mismatch")

    valid_edges, total_edges, endpoint_reasons = _edge_endpoint_stats(candidate_edges, node_ids)
    valid_recipes, total_recipe_edges, recipe_reasons = _recipe_stats(candidate_edges)
    reject_reasons.extend(endpoint_reasons)
    reject_reasons.extend(recipe_reasons)

    if _contains_activation_claim(candidate):
        reject_reasons.append("activation_claim_detected")

    baseline_node_count = len(baseline_nodes) if isinstance(baseline_nodes, list) else 0
    candidate_node_count = len(candidate_nodes) if isinstance(candidate_nodes, list) else 0
    node_delta = abs(candidate_node_count - baseline_node_count)

    compile_coverage = diagnostic.get("compile_coverage", {})
    source_ratio = Decimal("0")
    if isinstance(compile_coverage, Mapping):
        source_ratio_text = compile_coverage.get("core_explainable_sources_ratio")
        if isinstance(source_ratio_text, str):
            try:
                source_ratio = Decimal(source_ratio_text)
            except Exception:
                source_ratio = Decimal("0")
        elif isinstance(compile_coverage.get("core_explainable_sources"), int) and isinstance(
            compile_coverage.get("observed_source_files_total"), int
        ):
            source_ratio = _decimal_ratio(
                int(compile_coverage["core_explainable_sources"]),
                int(compile_coverage["observed_source_files_total"]),
            )

    objective_vector = {
        "authority_traceability_preservation": "0.000000" if missing_authority else "1.000000",
        "basis_reachability_preservation": "0.000000" if missing_primitives else "1.000000",
        "source_coverage_improvement": "0.000000",
        "decomposition_recipe_coverage": _decimal_str(_decimal_ratio(valid_recipes, total_recipe_edges)),
        "edge_endpoint_validity": _decimal_str(_decimal_ratio(valid_edges, total_edges)),
        "minimality": _decimal_str(Decimal(1) / Decimal(1 + node_delta)),
        "semantic_justification_strength": _decimal_str(_semantic_strength(candidate)),
        "registry_namespace_hygiene": _decimal_str(_registry_namespace_hygiene(registry_queue)),
        "visualization_projection_clarity": (
            "1.000000"
            if isinstance(metadata, Mapping)
            and metadata.get("projection_rule")
            and metadata.get("observer_scope")
            else "0.000000"
        ),
        "non_gaming_penalty": "1.000000" if _contains_activation_claim(candidate) else "0.000000",
    }

    return {
        "artifact_status": ARTIFACT_STATUS,
        "authority_status": AUTHORITY_STATUS,
        "baseline_path": inputs.baseline_path.as_posix(),
        "candidate_path": inputs.candidate_path.as_posix(),
        "diagnostic_verdict": str(diagnostic.get("verdict", "unknown")),
        "harness_id": HARNESS_ID,
        "human_objective_selection_required": True,
        "objective_fields": list(OBJECTIVE_FIELDS),
        "objective_vector": objective_vector,
        "public_path": "blocked",
        "registry_queue_path": inputs.registry_queue_path.as_posix(),
        "reject_reasons": sorted(set(reject_reasons)),
        "rejected": bool(reject_reasons),
        "source_coverage_baseline_ratio": _decimal_str(source_ratio),
        "tokens": [
            "phase_1545p_fix9_genesis_optimization_autoresearch_harness_committed",
            "genesis_optimization_harness_support_only_phase_1545p_fix9",
            "human_objective_selection_boundary_recorded_phase_1545p_fix9",
            "candidate_scoring_not_authority_recorded_phase_1545p_fix9",
            "genesis_manifest_not_mutated_phase_1545p_fix9",
            "public_path_remains_blocked_phase_1545p_fix9",
        ],
    }


def export_genesis_optimization_evaluation_json(inputs: HarnessInputs) -> str:
    return _dump_canonical(build_genesis_optimization_evaluation(inputs))


def default_inputs() -> HarnessInputs:
    return HarnessInputs(
        candidate_path=Path("out/genesis_core_star_map_v0.3_candidate.json"),
        baseline_path=Path("out/genesis_core_star_map_v0.3_candidate.json"),
        diagnostic_path=Path("out/genesis_compile_coverage_diagnostic_v0.3_candidate.json"),
        registry_queue_path=Path("out/genesis_common_registry_node_candidates_1545p_fix7.json"),
    )


def main() -> int:
    print(export_genesis_optimization_evaluation_json(default_inputs()), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ARTIFACT_STATUS",
    "AUTHORITY_STATUS",
    "HARNESS_ID",
    "HarnessInputs",
    "OBJECTIVE_FIELDS",
    "build_genesis_optimization_evaluation",
    "default_inputs",
    "export_genesis_optimization_evaluation_json",
]
