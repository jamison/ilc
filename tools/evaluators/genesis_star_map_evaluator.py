#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Genesis star-map candidate evaluator for the idea-descent runner.

PUBLIC_RC_EXCLUDE: idea_descent_genesis_star_map_evaluator_support_only
PUBLIC_RC_EXCLUDE_REASON: Internal local evaluator for Genesis candidate graph
descent. It does not sign, mutate, publish, or serve Genesis artifacts.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from ilc_core.rc.signing_ceremony_status import PHASE_1446_SIGNED_ARTIFACT_HASHES
from ilc_core.sidecars.idea_descent_rehearsal import (
    EVALUATOR_STATIC_AUDIT,
    SEVERITY_CRITICAL,
    SEVERITY_SIGNIFICANT,
)

EVALUATOR_ID = "genesis_star_map_candidate_evaluator"
EVALUATOR_TYPE = EVALUATOR_STATIC_AUDIT
REPLAY_COMMAND_TEMPLATE = (
    ".venv/bin/python tools/idea_descent_runner.py "
    "--objective docs/specs/ilc_idea_descent_genesis_star_map_objective_v0.1.md "
    "--candidate {candidate} "
    "--evaluator tools/evaluators/genesis_star_map_evaluator.py "
    "--trace-out out/idea_descent/genesis_star_map_trace.json"
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

REQUIRED_GENESIS_AUTHORITY_NODES: tuple[str, ...] = (
    "genesis_agent:01",
    "artifact:genesis_agent1_pubkey_record_838a",
    "ceremony:genesis_agent1_keygen_838a",
    "artifact:genesis_authority_assertion_schema",
    "artifact:genesis_intent_attestation_init_authority_map",
)

_OFFICIAL_V03_PATH = "out/genesis_core_star_map_v0.3_candidate.json"
_OFFICIAL_V03_SHA256 = PHASE_1446_SIGNED_ARTIFACT_HASHES[_OFFICIAL_V03_PATH]


def _reject_constant(value: str) -> None:
    raise ValueError(f"non_standard_json_numeric_constant:{value}")


def _load_candidate(candidate_path: str) -> Any:
    text = Path(candidate_path).read_text(encoding="utf-8")
    return json.loads(
        text,
        parse_float=Decimal,
        parse_int=int,
        parse_constant=_reject_constant,
    )


def _report(
    *,
    invariant: str,
    candidate_path: str,
    correction: str,
    severity: str = SEVERITY_SIGNIFICANT,
) -> dict[str, Any]:
    return {
        "failed_invariant": invariant,
        "source_artifact": candidate_path,
        "correction_direction": correction,
        "severity": severity,
        "replay_command": REPLAY_COMMAND_TEMPLATE.format(candidate=candidate_path),
        "affected_obl_or_cdl": None,
    }


def _walk_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        values: list[Any] = []
        for child in value.values():
            values.extend(_walk_values(child))
        return values
    if isinstance(value, list):
        values = []
        for child in value:
            values.extend(_walk_values(child))
        return values
    return [value]


def _node_ids(nodes: list[Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        candidate_id = node.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            continue
        if candidate_id in by_id:
            duplicates.append(candidate_id)
        by_id[candidate_id] = node
    return by_id, duplicates


def _check_candidate_shape(
    data: Any,
    candidate_path: str,
    reports: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[Any], list[Any]]:
    if not isinstance(data, dict):
        reports.append(
            _report(
                invariant="genesis_star_map_not_json_object",
                candidate_path=candidate_path,
                correction="Use a JSON object with metadata, nodes, and edges keys.",
                severity=SEVERITY_CRITICAL,
            )
        )
        return {}, [], []
    metadata = data.get("metadata")
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(metadata, dict):
        reports.append(
            _report(
                invariant="metadata_missing_or_invalid",
                candidate_path=candidate_path,
                correction="Add a metadata object describing derivation, projection rule, and transition basis.",
                severity=SEVERITY_CRITICAL,
            )
        )
        metadata = {}
    if not isinstance(nodes, list):
        reports.append(
            _report(
                invariant="nodes_missing_or_invalid",
                candidate_path=candidate_path,
                correction="Add a nodes array containing Genesis candidate node objects.",
                severity=SEVERITY_CRITICAL,
            )
        )
        nodes = []
    if not isinstance(edges, list):
        reports.append(
            _report(
                invariant="edges_missing_or_invalid",
                candidate_path=candidate_path,
                correction="Add an edges array containing typed star-map edge objects.",
                severity=SEVERITY_CRITICAL,
            )
        )
        edges = []
    return metadata, nodes, edges


def _check_standard_numbers(data: Any, candidate_path: str, reports: list[dict[str, Any]]) -> None:
    for value in _walk_values(data):
        if isinstance(value, Decimal) and not value.is_finite():
            reports.append(
                _report(
                    invariant="non_finite_numeric_value",
                    candidate_path=candidate_path,
                    correction="Remove NaN/Infinity values; Genesis candidate JSON must use finite numeric values only.",
                    severity=SEVERITY_CRITICAL,
                )
            )
            return


def _check_required_nodes(
    by_id: dict[str, dict[str, Any]],
    candidate_path: str,
    reports: list[dict[str, Any]],
) -> None:
    for candidate_id in (*REQUIRED_TRUTH_PRIMITIVES, *REQUIRED_GENESIS_AUTHORITY_NODES):
        node = by_id.get(candidate_id)
        if node is None:
            reports.append(
                _report(
                    invariant=f"required_node_missing:{candidate_id}",
                    candidate_path=candidate_path,
                    correction=f"Restore required Genesis star-map node {candidate_id}.",
                    severity=SEVERITY_CRITICAL,
                )
            )
            continue
        if node.get("genesis_attested") is not True:
            reports.append(
                _report(
                    invariant=f"required_node_not_genesis_attested:{candidate_id}",
                    candidate_path=candidate_path,
                    correction=f"Mark {candidate_id} as genesis_attested=true only if the signed evidence supports it.",
                    severity=SEVERITY_CRITICAL,
                )
            )
        if node.get("genesis_attested_by") != "genesis_agent:01":
            reports.append(
                _report(
                    invariant=f"required_node_wrong_attestor:{candidate_id}",
                    candidate_path=candidate_path,
                    correction=f"Restore genesis_attested_by='genesis_agent:01' for {candidate_id}.",
                    severity=SEVERITY_CRITICAL,
                )
            )
        if node.get("signature_status") != "signed":
            reports.append(
                _report(
                    invariant=f"required_node_not_signed:{candidate_id}",
                    candidate_path=candidate_path,
                    correction=f"Restore signed status for {candidate_id} or route an unsigned successor through a signing phase.",
                    severity=SEVERITY_CRITICAL,
                )
            )


def _check_metadata(
    metadata: dict[str, Any],
    nodes: list[Any],
    candidate_path: str,
    reports: list[dict[str, Any]],
) -> None:
    transition_basis = metadata.get("transition_basis")
    if transition_basis != list(REQUIRED_TRUTH_PRIMITIVES):
        reports.append(
            _report(
                invariant="transition_basis_mismatch",
                candidate_path=candidate_path,
                correction="Restore metadata.transition_basis to the seven Genesis truth primitives in canonical order.",
                severity=SEVERITY_CRITICAL,
            )
        )
    if metadata.get("projection_rule") != "high_authority_core_bootstrap_projection":
        reports.append(
            _report(
                invariant="projection_rule_mismatch",
                candidate_path=candidate_path,
                correction="Restore projection_rule='high_authority_core_bootstrap_projection' for the core Genesis star map.",
            )
        )
    if metadata.get("observer_scope") != "install_load_genesis_agent_view":
        reports.append(
            _report(
                invariant="observer_scope_mismatch",
                candidate_path=candidate_path,
                correction="Restore observer_scope='install_load_genesis_agent_view' for the launch bootstrap projection.",
            )
        )
    if metadata.get("expansion_phase") != "1387e":
        reports.append(
            _report(
                invariant="missing_v03_expansion_phase",
                candidate_path=candidate_path,
                correction="Use the v0.3 candidate lineage that records expansion_phase='1387e'.",
            )
        )
    if len(nodes) < 54:
        reports.append(
            _report(
                invariant="v03_node_floor_not_met",
                candidate_path=candidate_path,
                correction="Restore the v0.3 candidate node floor of 54 nodes or document a superseding signed manifest.",
                severity=SEVERITY_CRITICAL,
            )
        )


def _check_node_list(
    nodes: list[Any],
    candidate_path: str,
    reports: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    by_id, duplicates = _node_ids(nodes)
    if len(by_id) != len(nodes):
        reports.append(
            _report(
                invariant="node_candidate_id_missing_or_duplicate",
                candidate_path=candidate_path,
                correction="Ensure every node has one unique non-empty candidate_id.",
                severity=SEVERITY_CRITICAL,
            )
        )
    if duplicates:
        reports.append(
            _report(
                invariant=f"duplicate_candidate_ids:{','.join(sorted(duplicates))}",
                candidate_path=candidate_path,
                correction="Remove duplicate candidate_id entries before accepting the star-map candidate.",
                severity=SEVERITY_CRITICAL,
            )
        )
    for candidate_id, node in by_id.items():
        confidence = node.get("confidence")
        if not isinstance(confidence, (int, Decimal)) or isinstance(confidence, bool):
            reports.append(
                _report(
                    invariant=f"node_confidence_invalid:{candidate_id}",
                    candidate_path=candidate_path,
                    correction=f"Set {candidate_id}.confidence to a finite JSON number in [0, 1].",
                )
            )
            continue
        if Decimal(confidence) < Decimal("0") or Decimal(confidence) > Decimal("1"):
            reports.append(
                _report(
                    invariant=f"node_confidence_out_of_range:{candidate_id}",
                    candidate_path=candidate_path,
                    correction=f"Set {candidate_id}.confidence to a value in [0, 1].",
                )
            )
    return by_id


def _check_edges(
    edges: list[Any],
    by_id: dict[str, dict[str, Any]],
    candidate_path: str,
    reports: list[dict[str, Any]],
) -> None:
    edge_ids: set[str] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            reports.append(
                _report(
                    invariant="edge_not_object",
                    candidate_path=candidate_path,
                    correction="Every edge must be a JSON object with edge_id, edge_type, source, target, and decomposition_recipe.",
                    severity=SEVERITY_CRITICAL,
                )
            )
            continue
        edge_id = edge.get("edge_id")
        if not isinstance(edge_id, str) or not edge_id:
            reports.append(
                _report(
                    invariant="edge_id_missing",
                    candidate_path=candidate_path,
                    correction="Give every edge a unique non-empty edge_id.",
                    severity=SEVERITY_CRITICAL,
                )
            )
            continue
        if edge_id in edge_ids:
            reports.append(
                _report(
                    invariant=f"duplicate_edge_id:{edge_id}",
                    candidate_path=candidate_path,
                    correction=f"Remove or rename duplicate edge_id {edge_id}.",
                    severity=SEVERITY_CRITICAL,
                )
            )
        edge_ids.add(edge_id)
        source = edge.get("source")
        target = edge.get("target")
        if source not in by_id:
            reports.append(
                _report(
                    invariant=f"edge_source_missing:{edge_id}",
                    candidate_path=candidate_path,
                    correction=f"Restore source node {source!r} or remove edge {edge_id}.",
                    severity=SEVERITY_CRITICAL,
                )
            )
        if target not in by_id:
            reports.append(
                _report(
                    invariant=f"edge_target_missing:{edge_id}",
                    candidate_path=candidate_path,
                    correction=f"Restore target node {target!r} or remove edge {edge_id}.",
                    severity=SEVERITY_CRITICAL,
                )
            )
        recipe = edge.get("decomposition_recipe")
        if not isinstance(recipe, dict) or not recipe.get("primitives"):
            reports.append(
                _report(
                    invariant=f"edge_missing_decomposition_recipe:{edge_id}",
                    candidate_path=candidate_path,
                    correction=f"Add a decomposition_recipe.primitives list for edge {edge_id}.",
                )
            )


def _check_official_v03_hash(candidate_path: str, reports: list[dict[str, Any]]) -> None:
    path = Path(candidate_path)
    if path.as_posix() != _OFFICIAL_V03_PATH:
        return
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != _OFFICIAL_V03_SHA256:
        reports.append(
            _report(
                invariant="official_v03_signed_hash_mismatch",
                candidate_path=candidate_path,
                correction="Do not modify the Phase 1446 signed v0.3 candidate in place; create a successor candidate and route signing separately.",
                severity=SEVERITY_CRITICAL,
            )
        )


def run_evaluation(candidate_path: str, objective_text: str) -> dict[str, Any]:
    """Evaluate a Genesis star-map candidate against v0.3 launch invariants."""
    reports: list[dict[str, Any]] = []
    try:
        data = _load_candidate(candidate_path)
    except Exception as exc:
        reports.append(
            _report(
                invariant="candidate_json_load_failed",
                candidate_path=candidate_path,
                correction=f"Repair candidate JSON parse failure: {exc}",
                severity=SEVERITY_CRITICAL,
            )
        )
        return {
            "passed": False,
            "failure_count": len(reports),
            "summary": "INVALID: candidate JSON did not load",
            "refutation_reports": reports,
        }

    metadata, nodes, edges = _check_candidate_shape(data, candidate_path, reports)
    _check_standard_numbers(data, candidate_path, reports)
    by_id = _check_node_list(nodes, candidate_path, reports)
    _check_required_nodes(by_id, candidate_path, reports)
    _check_metadata(metadata, nodes, candidate_path, reports)
    _check_edges(edges, by_id, candidate_path, reports)
    _check_official_v03_hash(candidate_path, reports)

    passed = not reports
    return {
        "passed": passed,
        "failure_count": len(reports),
        "summary": (
            f"VALID Genesis v0.3 candidate shape: {len(nodes)} nodes, {len(edges)} edges"
            if passed
            else f"INVALID Genesis candidate: {len(reports)} invariant(s) failed"
        ),
        "refutation_reports": reports,
    }


__all__ = [
    "EVALUATOR_ID",
    "EVALUATOR_TYPE",
    "REPLAY_COMMAND_TEMPLATE",
    "REQUIRED_TRUTH_PRIMITIVES",
    "REQUIRED_GENESIS_AUTHORITY_NODES",
    "run_evaluation",
]
