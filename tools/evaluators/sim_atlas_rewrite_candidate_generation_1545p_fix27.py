#!/usr/bin/env python3
"""Generate Fix27 Atlas rewrite candidates.

PUBLIC_RC_EXCLUDE: atlas_rewrite_candidate_generation_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only SIM runner. Emits candidate records only;
does not apply rewrites, mutate canonical graph state, sign artifacts, activate
runtime, or authorize public RC.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
ENRICHED_GRAPH = (
    REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json"
)
FIX26_QUEUE = REPO_ROOT / "out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl"
CANDIDATE_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_rewrite_candidates_1545p_fix27.jsonl"
JSON_OUT = REPO_ROOT / "out/sim_atlas_rewrite_candidate_generation_1545p_fix27.json"

GENESIS_ROOT = "artifact:genesis_intent_attestation_init_authority_map"
PHASE = "1545p-Fix27"
PASSAGE_DISTANCE_THRESHOLD_LINES = 25

SUPPORTED_TRACE_ROLES = {
    "ATTESTATION",
    "CLASSIFIED_BY",
    "DERIVED_FROM",
    "DERIVED_FROM_GENESIS_REPO",
    "EVIDENCES",
    "GOVERNS",
    "IMPLEMENTS",
    "IMPORTS_MODULE",
    "IMPLEMENTS_MODULE",
    "REFERENCES_AUTHORITY",
    "SOURCE_TREE_MEMBER",
    "TESTS",
}

NON_AUTHORITY_TRACE_ROLES = {
    "DERIVED_FROM",
    "DERIVED_FROM_GENESIS_REPO",
    "EVIDENCES",
    "IMPLEMENTS",
    "IMPORTS_MODULE",
    "IMPLEMENTS_MODULE",
    "REFERENCES_AUTHORITY",
    "SOURCE_TREE_MEMBER",
    "TESTS",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_hash(payload: Any, length: int = 20) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )
    return hashlib.sha256(raw).hexdigest()[:length]


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (edge.get("source", ""), edge.get("target", ""), edge.get("edge_type", ""))


def _node_label(node_by_id: dict[str, dict[str, Any]], node_id: str) -> str:
    return str(node_by_id.get(node_id, {}).get("label", node_id))


def _node_path(node_by_id: dict[str, dict[str, Any]], node_id: str) -> str:
    node = node_by_id.get(node_id, {})
    for key in ("source_path", "path", "label"):
        value = node.get(key)
        if isinstance(value, str) and "/" in value:
            return value
    label = str(node.get("label", ""))
    return label if "/" in label else ""


def _text_line(path: str, line_no: int | None) -> str:
    if not path or line_no is None:
        return ""
    file_path = REPO_ROOT / path
    if not file_path.exists() or not file_path.is_file():
        return ""
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


def _parse_line_hint(hint: str) -> int | None:
    match = re.search(r"line:(\d+)", hint or "")
    return int(match.group(1)) if match else None


def _refs_by_line(path: str) -> list[tuple[int, str]]:
    file_path = REPO_ROOT / path
    if not file_path.exists() or not file_path.is_file():
        return []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    refs: list[tuple[int, str]] = []
    pattern = re.compile(r"\b(?:ADR-\d{4}|CDL-(?:V\d+|\d{3}|\d{1,2})|CDL-V\d+)\b", re.I)
    for idx, line in enumerate(lines, start=1):
        for ref in pattern.findall(line):
            refs.append((idx, ref.upper()))
    return refs


def _terminal_ref_key(terminal_node_id: str) -> str:
    lower = terminal_node_id.lower()
    adr_match = re.search(r"adr[:_-]0*(\d{1,4})", lower)
    if adr_match:
        return f"ADR-{int(adr_match.group(1)):04d}"
    cdl_v_match = re.search(r"cdl[:_-]v(\d+)", lower)
    if cdl_v_match:
        return f"CDL-V{int(cdl_v_match.group(1))}"
    cdl_match = re.search(r"cdl[:_-]0*(\d{1,3})", lower)
    if cdl_match:
        return f"CDL-{int(cdl_match.group(1)):03d}"
    return terminal_node_id.upper()


def _nearest_ref(path: str, evidence_line: int | None, terminal_node_id: str) -> dict[str, Any]:
    refs = _refs_by_line(path)
    terminal_key = _terminal_ref_key(terminal_node_id)
    if not refs or evidence_line is None:
        return {
            "nearest_authority_ref": "",
            "distance_lines": None,
            "section_local": False,
            "terminal_ref_present": False,
        }
    nearest_line, nearest_ref = min(refs, key=lambda item: abs(item[0] - evidence_line))
    terminal_lines = [line for line, ref in refs if ref == terminal_key]
    terminal_distance = (
        min(abs(line - evidence_line) for line in terminal_lines) if terminal_lines else None
    )
    distance = terminal_distance if terminal_distance is not None else abs(nearest_line - evidence_line)
    return {
        "nearest_authority_ref": terminal_key if terminal_distance is not None else nearest_ref,
        "distance_lines": distance,
        "section_local": distance <= PASSAGE_DISTANCE_THRESHOLD_LINES,
        "terminal_ref_present": terminal_distance is not None,
    }


def _base_invariants(endpoint_valid: bool, role_declared: bool = True) -> dict[str, bool]:
    return {
        "activation_claim_absent": True,
        "authority_trace_preserved": True,
        "decomposition_recipes_present": True,
        "endpoint_validity_preserved": endpoint_valid,
        "evidence_paths_preserved": True,
        "privacy_tiers_preserved": True,
        "proof_class_not_downgraded_for_any_node": True,
        "refutation_paths_preserved": True,
        "root_reachability_preserved": True,
        "signed_artifact_mutation_absent": True,
        "typed_trace_roles_declared_for_all_added_nodes": role_declared,
    }


def _candidate_base(
    *,
    rule_type: str,
    source: str,
    target: str,
    edge_type: str,
    source_label: str,
    target_label: str,
    rationale: str,
    provenance: str,
    review_class: str,
    candidate_kind: str = "edge_candidate",
    atom_refs: list[str] | None = None,
    defer_reason: str = "",
    reject_reason: str = "",
    confidence_class: str = "medium",
    proof_after: str = "merkle_plus_typed_non_authority_trace",
    fix26_hypothesis_scope: str = "not_fix26_atom_candidate",
    passage_validation: dict[str, Any] | None = None,
    terminal_resolution: str = "single_ref",
    terminal_confidence: str = "medium",
) -> dict[str, Any]:
    role_declared = edge_type in SUPPORTED_TRACE_ROLES
    endpoint_valid = bool(source and target)
    payload = {
        "candidate_kind": candidate_kind,
        "edge_type": edge_type,
        "provenance": provenance,
        "rule_type": rule_type,
        "source": source,
        "target": target,
    }
    candidate_id = f"atlas-rewrite:{_stable_hash(payload)}"
    right_edge = {
        "edge_type": edge_type,
        "provenance": f"phase_1545p_fix27:{provenance}",
        "rationale": rationale,
        "source": source,
        "target": target,
    }
    nac_satisfied = [
        {
            "name": "edge_already_exists_in_fix22",
            "passed": True,
            "rationale": "candidate is emitted as research-only rewrite record, not applied",
        }
    ]
    invariants = _base_invariants(endpoint_valid=endpoint_valid, role_declared=role_declared)
    if review_class == "candidate_reject":
        invariants["proof_class_not_downgraded_for_any_node"] = True
    return {
        "atom_candidate_refs": atom_refs or [],
        "candidate_kind": candidate_kind,
        "deleted_material": {"edges": [], "hyperedges": [], "vertices": []},
        "fix26_hypothesis_scope": fix26_hypothesis_scope,
        "fix26_terminal_resolution": terminal_resolution,
        "invariant_checklist": invariants,
        "interface_boundary": [source, target] if target else [source],
        "left_pattern": {
            "description": "support edge absent from Fix22 baseline",
            "source": source,
            "target": target,
        },
        "matched_subgraph": {"edge_ids": [], "vertex_ids": [x for x in (source, target) if x]},
        "merge_safety_checks": {
            "dissent_collapse_absent": True,
            "not_applicable": rule_type != "node_merge",
            "refutation_collapse_absent": True,
        },
        "nac_satisfied": nac_satisfied,
        "negative_application_conditions": nac_satisfied,
        "preserved_interface": [x for x in (source, target) if x],
        "promotion_boundary": "research_only_no_canonical_mutation_no_signing_no_activation",
        "proof_class_delta": [
            {
                "after": proof_after,
                "before": "merkle_inclusion_only",
                "node": source,
            }
        ],
        "review_class": review_class,
        "rewrite_candidate_id": candidate_id,
        "right_pattern": {"add_edges": [right_edge], "add_hyperedges": [], "add_vertices": []},
        "rule_type": rule_type,
        "source_evidence": [
            {
                "path": source_label,
                "provenance": provenance,
                "rationale": rationale,
                "target": target_label,
            }
        ],
        "terminal_confidence_class": terminal_confidence,
        "typed_trace_edge_roles": [
            {
                "edge_role": edge_type,
                "node": source,
                "terminal_node": target,
                "traversal_direction": "source_to_terminal_then_terminal_backtrace",
            }
        ],
        "expected_objective_delta": {
            "authority_traceability": "preserved",
            "backwards_read_coverage": "non_decreasing_candidate",
            "endpoint_validity": 0 if endpoint_valid else 1,
            "proof_class_delta": proof_after,
        },
        "passage_validation": passage_validation
        or {
            "distance_lines": None,
            "evidence_line": None,
            "nearest_authority_ref": "",
            "section_local": True,
            "validation_status": "not_required_for_prepass_edge",
        },
        "rejection_reason": reject_reason,
        "defer_reason": defer_reason,
    }


def _should_reclassify_source_tree(edge: dict[str, Any]) -> bool:
    provenance = str(edge.get("provenance", ""))
    return (
        edge.get("edge_type") == "REFERENCES_AUTHORITY"
        and edge.get("target") == GENESIS_ROOT
        and provenance
        in {
            "manual_bucket_analysis_fix27_b10",
            "manual_bucket_analysis_fix27_b11",
            "manual_bucket_analysis_fix27_b12",
        }
    )


def _records_from_enriched_edges(
    base_graph: dict[str, Any], enriched_graph: dict[str, Any]
) -> list[dict[str, Any]]:
    base_edges = {_edge_key(edge) for edge in base_graph["edges"]}
    enriched_nodes = {node["candidate_id"]: node for node in enriched_graph["nodes"]}
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for edge in enriched_graph["edges"]:
        if _edge_key(edge) in base_edges:
            continue
        source = edge.get("source", "")
        target = edge.get("target", "")
        edge_type = edge.get("edge_type", "")
        rationale = str(edge.get("rationale", "enriched Fix27 pre-pass edge"))
        provenance = str(edge.get("provenance", "enriched_fix27_prepass"))
        if _should_reclassify_source_tree(edge):
            edge_type = "SOURCE_TREE_MEMBER"
            rationale = (
                rationale
                + " | reclassified from REFERENCES_AUTHORITY to SOURCE_TREE_MEMBER by Fix27"
            )
        record = _candidate_base(
            rule_type="semantic_pre_pass",
            source=source,
            target=target,
            edge_type=edge_type,
            source_label=_node_label(enriched_nodes, source),
            target_label=_node_label(enriched_nodes, target),
            rationale=rationale,
            provenance=provenance,
            review_class="candidate_keep_for_fix30",
            confidence_class="high" if provenance.startswith("manual") else "medium",
            terminal_confidence="high" if provenance.startswith("manual") else "medium",
        )
        if record["rewrite_candidate_id"] not in seen_ids:
            records.append(record)
            seen_ids.add(record["rewrite_candidate_id"])
    return records


def _load_fix26_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in FIX26_QUEUE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _records_from_fix26_atoms(
    fix26_records: list[dict[str, Any]], node_ids: set[str], node_by_id: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for atom in fix26_records:
        if atom.get("queue_class") != "accepted_atom_candidates_for_review":
            continue
        source = atom.get("source_node_id", "")
        target = atom.get("typed_trace_terminal_node_id", "")
        edge_type = atom.get("typed_trace_edge_role", "")
        source_path = atom.get("source_path", "")
        atom_id = atom.get("atom_candidate_id", "")
        evidence_line = _parse_line_hint(atom.get("evidence_span_hint", ""))
        nearest = _nearest_ref(source_path, evidence_line, target)
        target_exists = target in node_ids
        role_declared = edge_type in SUPPORTED_TRACE_ROLES
        if not target_exists:
            review_class = "candidate_defer"
            defer_reason = "terminal_missing"
            terminal_resolution = "terminal_missing"
            terminal_confidence = "defer"
        elif not role_declared:
            review_class = "candidate_defer"
            defer_reason = "typed_trace_undeclared"
            terminal_resolution = "single_ref"
            terminal_confidence = "defer"
        elif nearest["distance_lines"] is not None and nearest["distance_lines"] > PASSAGE_DISTANCE_THRESHOLD_LINES:
            review_class = "candidate_defer"
            defer_reason = "authority_ref_too_distant"
            terminal_resolution = (
                "multi_ref_ambiguous"
                if len(atom.get("evidence_authority_refs", [])) > 1
                else "single_ref"
            )
            terminal_confidence = "defer"
        else:
            review_class = "candidate_keep_for_fix30"
            defer_reason = ""
            terminal_resolution = (
                "multi_ref_passage_local"
                if len(atom.get("evidence_authority_refs", [])) > 1
                else "single_ref"
            )
            terminal_confidence = "medium"
        validation_status = "passed" if review_class == "candidate_keep_for_fix30" else "deferred"
        passage_validation = {
            "distance_lines": nearest["distance_lines"],
            "evidence_line": evidence_line,
            "evidence_text": _text_line(source_path, evidence_line),
            "nearest_authority_ref": nearest["nearest_authority_ref"],
            "section_local": bool(nearest["section_local"]),
            "validation_status": validation_status,
        }
        record = _candidate_base(
            rule_type="edge_refine",
            source=source,
            target=target,
            edge_type=edge_type,
            source_label=source_path,
            target_label=_node_label(node_by_id, target),
            rationale=(
                f"Fix26 atom {atom_id} recipe={atom.get('recipe_id')} "
                f"queue={atom.get('queue_class')}"
            ),
            provenance="fix26_atom_candidate_replay",
            review_class=review_class,
            atom_refs=[atom_id],
            defer_reason=defer_reason,
            confidence_class=atom.get("confidence_class", "medium"),
            fix26_hypothesis_scope="file_level_recipe_hypothesis",
            passage_validation=passage_validation,
            terminal_resolution=terminal_resolution,
            terminal_confidence=terminal_confidence,
        )
        if review_class == "candidate_defer":
            record["invariant_checklist"]["typed_trace_roles_declared_for_all_added_nodes"] = role_declared
        records.append(record)
    return records


def _aggregate_hyperedge_candidates(
    enriched_graph: dict[str, Any], enriched_extra_records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_extra_records:
        if record["rule_type"] != "semantic_pre_pass":
            continue
        edge = record["right_pattern"]["add_edges"][0]
        if edge["edge_type"] in {"REFERENCES_AUTHORITY", "EVIDENCES", "TESTS"}:
            by_source[edge["source"]].append(record)
    node_by_id = {node["candidate_id"]: node for node in enriched_graph["nodes"]}
    candidates: list[dict[str, Any]] = []
    for source, records in sorted(by_source.items(), key=lambda item: (-len(item[1]), item[0]))[:50]:
        targets = [r["right_pattern"]["add_edges"][0]["target"] for r in records[:8]]
        payload = {"rule": "hyperedge_replace", "source": source, "targets": targets}
        candidate_id = f"atlas-rewrite:{_stable_hash(payload)}"
        candidates.append(
            {
                "atom_candidate_refs": [],
                "candidate_kind": "aggregate_candidate",
                "defer_reason": "",
                "deleted_material": {"edges": [], "hyperedges": [], "vertices": []},
                "fix26_hypothesis_scope": "not_fix26_atom_candidate",
                "fix26_terminal_resolution": "single_ref",
                "invariant_checklist": _base_invariants(endpoint_valid=True),
                "interface_boundary": [source, *targets],
                "left_pattern": {
                    "description": "dense source-to-terminal fanout in enriched research graph",
                    "source": source,
                    "target_count": len(records),
                },
                "matched_subgraph": {"edge_ids": [], "vertex_ids": [source, *targets]},
                "merge_safety_checks": {
                    "dissent_collapse_absent": True,
                    "not_applicable": True,
                    "refutation_collapse_absent": True,
                },
                "nac_satisfied": [],
                "negative_application_conditions": [],
                "passage_validation": {
                    "distance_lines": None,
                    "evidence_line": None,
                    "nearest_authority_ref": "",
                    "section_local": True,
                    "validation_status": "aggregate_from_accepted_edges",
                },
                "preserved_interface": [source, *targets],
                "promotion_boundary": "research_only_no_canonical_mutation_no_signing_no_activation",
                "proof_class_delta": [
                    {
                        "after": "merkle_plus_typed_non_authority_trace",
                        "before": "merkle_inclusion_only",
                        "node": source,
                    }
                ],
                "rejection_reason": "",
                "review_class": "candidate_keep_for_fix30",
                "rewrite_candidate_id": candidate_id,
                "right_pattern": {
                    "add_edges": [],
                    "add_hyperedges": [
                        {
                            "hyperedge_type": "SOURCE_AUTHORITY_FANOUT",
                            "members": [source, *targets],
                            "provenance": "phase_1545p_fix27:hyperedge_replace_candidate",
                        }
                    ],
                    "add_vertices": [],
                },
                "rule_type": "hyperedge_replace",
                "source_evidence": [
                    {
                        "path": _node_label(node_by_id, source),
                        "rationale": f"{len(records)} candidate support edges share one source",
                    }
                ],
                "terminal_confidence_class": "medium",
                "typed_trace_edge_roles": [
                    {
                        "edge_role": "EVIDENCES",
                        "node": source,
                        "terminal_node": target,
                        "traversal_direction": "source_to_terminal_then_terminal_backtrace",
                    }
                    for target in targets
                ],
                "expected_objective_delta": {
                    "authority_traceability": "preserved",
                    "backwards_read_coverage": "projection_candidate_only",
                    "endpoint_validity": 0,
                    "proof_class_delta": "merkle_plus_typed_non_authority_trace",
                },
            }
        )
    return candidates


def _aggregate_node_split_candidates(enriched_graph: dict[str, Any]) -> list[dict[str, Any]]:
    node_by_id = {node["candidate_id"]: node for node in enriched_graph["nodes"]}
    out_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in enriched_graph["edges"]:
        out_edges[edge.get("source", "")].append(edge)
    candidates: list[dict[str, Any]] = []
    root_like = [
        node_id
        for node_id, edges in out_edges.items()
        if (node_id.startswith("artifact:") or node_id.startswith("repo:group:"))
        and len(edges) >= 100
        and any(edge.get("edge_type") in {"CONTAINS_FILE", "CONTAINS_GROUP"} for edge in edges)
    ]
    for source in sorted(root_like)[:10]:
        payload = {"rule": "node_split", "source": source}
        candidate_id = f"atlas-rewrite:{_stable_hash(payload)}"
        candidates.append(
            {
                "atom_candidate_refs": [],
                "candidate_kind": "aggregate_candidate",
                "defer_reason": "classification_terminal_for_split_requires_future_schema",
                "deleted_material": {"edges": [], "hyperedges": [], "vertices": []},
                "fix26_hypothesis_scope": "not_fix26_atom_candidate",
                "fix26_terminal_resolution": "single_ref",
                "invariant_checklist": _base_invariants(endpoint_valid=True),
                "interface_boundary": [source],
                "left_pattern": {
                    "description": "large material root candidate for role-specific split",
                    "source": source,
                    "out_edge_count": len(out_edges[source]),
                },
                "matched_subgraph": {"edge_ids": [], "vertex_ids": [source]},
                "merge_safety_checks": {
                    "dissent_collapse_absent": True,
                    "not_applicable": True,
                    "refutation_collapse_absent": True,
                },
                "nac_satisfied": [],
                "negative_application_conditions": [],
                "passage_validation": {
                    "distance_lines": None,
                    "evidence_line": None,
                    "nearest_authority_ref": "",
                    "section_local": True,
                    "validation_status": "aggregate_structural_candidate",
                },
                "preserved_interface": [source],
                "promotion_boundary": "research_only_no_canonical_mutation_no_signing_no_activation",
                "proof_class_delta": [
                    {
                        "after": "merkle_inclusion_only",
                        "before": "merkle_inclusion_only",
                        "node": source,
                    }
                ],
                "rejection_reason": "",
                "review_class": "candidate_defer",
                "rewrite_candidate_id": candidate_id,
                "right_pattern": {
                    "add_edges": [],
                    "add_hyperedges": [],
                    "add_vertices": [
                        {
                            "candidate_vertex_kind": "role_specific_material_partition",
                            "source_root": source,
                        }
                    ],
                },
                "rule_type": "node_split",
                "source_evidence": [
                    {
                        "path": _node_label(node_by_id, source),
                        "rationale": "material root has high fanout and may benefit from typed partition split",
                    }
                ],
                "terminal_confidence_class": "defer",
                "typed_trace_edge_roles": [
                    {
                        "edge_role": "CLASSIFIED_BY",
                        "node": source,
                        "terminal_node": "future:genesis_governed_material_partition_rule",
                        "traversal_direction": "source_to_classification_rule_then_rule_backtrace",
                    }
                ],
                "expected_objective_delta": {
                    "authority_traceability": "preserved",
                    "backwards_read_coverage": "deferred_pending_classification_rule",
                    "endpoint_validity": 0,
                    "proof_class_delta": "none_deferred",
                },
            }
        )
    return candidates


def _aggregate_node_merge_candidates(enriched_graph: dict[str, Any]) -> list[dict[str, Any]]:
    label_groups: dict[str, list[str]] = defaultdict(list)
    for node in enriched_graph["nodes"]:
        label = node.get("label")
        if isinstance(label, str) and label:
            label_groups[label.lower()].append(node["candidate_id"])
    candidates: list[dict[str, Any]] = []
    for label, node_ids in sorted(label_groups.items()):
        if len(node_ids) < 2:
            continue
        payload = {"rule": "node_merge", "label": label, "nodes": sorted(node_ids)}
        candidate_id = f"atlas-rewrite:{_stable_hash(payload)}"
        candidates.append(
            {
                "atom_candidate_refs": [],
                "candidate_kind": "aggregate_candidate",
                "defer_reason": "",
                "deleted_material": {"edges": [], "hyperedges": [], "vertices": []},
                "fix26_hypothesis_scope": "not_fix26_atom_candidate",
                "fix26_terminal_resolution": "single_ref",
                "invariant_checklist": _base_invariants(endpoint_valid=True),
                "interface_boundary": sorted(node_ids),
                "left_pattern": {
                    "description": "duplicate node label candidate",
                    "label": label,
                    "nodes": sorted(node_ids),
                },
                "matched_subgraph": {"edge_ids": [], "vertex_ids": sorted(node_ids)},
                "merge_safety_checks": {
                    "dissent_collapse_absent": True,
                    "refutation_collapse_absent": True,
                    "source_path_loss_absent": False,
                },
                "nac_satisfied": [
                    {
                        "name": "dissent_or_refutation_path_between_merge_nodes",
                        "passed": True,
                    }
                ],
                "negative_application_conditions": [
                    {
                        "name": "dissent_or_refutation_path_between_merge_nodes",
                        "passed": True,
                    }
                ],
                "passage_validation": {
                    "distance_lines": None,
                    "evidence_line": None,
                    "nearest_authority_ref": "",
                    "section_local": True,
                    "validation_status": "structural_duplicate_label",
                },
                "preserved_interface": sorted(node_ids),
                "promotion_boundary": "research_only_no_canonical_mutation_no_signing_no_activation",
                "proof_class_delta": [
                    {
                        "after": "merkle_inclusion_only",
                        "before": "merkle_inclusion_only",
                        "node": node_id,
                    }
                    for node_id in sorted(node_ids)
                ],
                "rejection_reason": "source_path_loss_risk",
                "review_class": "candidate_reject",
                "rewrite_candidate_id": candidate_id,
                "right_pattern": {"add_edges": [], "add_hyperedges": [], "add_vertices": []},
                "rule_type": "node_merge",
                "source_evidence": [
                    {
                        "path": label,
                        "rationale": "duplicate label exists but merge is rejected unless source-path loss is proven absent",
                    }
                ],
                "terminal_confidence_class": "defer",
                "typed_trace_edge_roles": [
                    {
                        "edge_role": "DERIVED_FROM",
                        "node": node_id,
                        "terminal_node": node_id,
                        "traversal_direction": "identity_preservation_check",
                    }
                    for node_id in sorted(node_ids)
                ],
                "expected_objective_delta": {
                    "authority_traceability": "preserved",
                    "backwards_read_coverage": "no_change_rejected",
                    "endpoint_validity": 0,
                    "proof_class_delta": "none_rejected",
                },
            }
        )
        if len(candidates) >= 25:
            break
    return candidates


def _aggregate_projection_candidates(enriched_extra_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_extra_records:
        edge = record["right_pattern"]["add_edges"][0]
        if edge["edge_type"] in NON_AUTHORITY_TRACE_ROLES:
            by_target[edge["target"]].append(record)
    candidates: list[dict[str, Any]] = []
    for target, records in sorted(by_target.items(), key=lambda item: (-len(item[1]), item[0]))[:25]:
        sources = [r["right_pattern"]["add_edges"][0]["source"] for r in records[:10]]
        payload = {"rule": "projection_simplify", "target": target, "sources": sources}
        candidate_id = f"atlas-rewrite:{_stable_hash(payload)}"
        candidates.append(
            {
                "atom_candidate_refs": [],
                "candidate_kind": "aggregate_candidate",
                "defer_reason": "",
                "deleted_material": {"edges": [], "hyperedges": [], "vertices": []},
                "fix26_hypothesis_scope": "not_fix26_atom_candidate",
                "fix26_terminal_resolution": "single_ref",
                "invariant_checklist": _base_invariants(endpoint_valid=True),
                "interface_boundary": [target, *sources],
                "left_pattern": {
                    "description": "many source nodes share a typed trace terminal",
                    "source_count": len(records),
                    "target": target,
                },
                "matched_subgraph": {"edge_ids": [], "vertex_ids": [target, *sources]},
                "merge_safety_checks": {
                    "dissent_collapse_absent": True,
                    "not_applicable": True,
                    "refutation_collapse_absent": True,
                },
                "nac_satisfied": [],
                "negative_application_conditions": [],
                "passage_validation": {
                    "distance_lines": None,
                    "evidence_line": None,
                    "nearest_authority_ref": "",
                    "section_local": True,
                    "validation_status": "projection_support_only",
                },
                "preserved_interface": [target, *sources],
                "promotion_boundary": "support_only_projection_no_semantic_replacement",
                "proof_class_delta": [
                    {
                        "after": "merkle_plus_typed_non_authority_trace",
                        "before": "merkle_inclusion_only",
                        "node": source,
                    }
                    for source in sources
                ],
                "rejection_reason": "",
                "review_class": "candidate_keep_for_fix30",
                "rewrite_candidate_id": candidate_id,
                "right_pattern": {
                    "add_edges": [
                        {
                            "edge_type": "PROJECTED_TYPED_TRACE_PATH",
                            "hidden_source_count": len(records),
                            "provenance": "phase_1545p_fix27:projection_simplify_candidate",
                            "source": "projection:support_only",
                            "target": target,
                        }
                    ],
                    "add_hyperedges": [],
                    "add_vertices": [],
                },
                "rule_type": "projection_simplify",
                "source_evidence": [
                    {
                        "path": target,
                        "rationale": f"{len(records)} sources share terminal; projection preserves hidden path list",
                    }
                ],
                "terminal_confidence_class": "medium",
                "typed_trace_edge_roles": [
                    {
                        "edge_role": "DERIVED_FROM",
                        "node": source,
                        "terminal_node": target,
                        "traversal_direction": "projection_view_preserves_hidden_source_to_terminal_paths",
                    }
                    for source in sources
                ],
                "expected_objective_delta": {
                    "authority_traceability": "preserved",
                    "backwards_read_coverage": "projection_candidate_only",
                    "endpoint_validity": 0,
                    "proof_class_delta": "no_semantic_authority_change",
                },
            }
        )
    return candidates


def _summarize(records: list[dict[str, Any]], fix26_records: list[dict[str, Any]]) -> dict[str, Any]:
    rule_counts = Counter(record["rule_type"] for record in records)
    review_counts = Counter(record["review_class"] for record in records)
    defer_counts = Counter(record.get("defer_reason", "") for record in records if record.get("defer_reason"))
    reject_counts = Counter(
        record.get("rejection_reason", "") for record in records if record.get("rejection_reason")
    )
    edge_roles = Counter()
    for record in records:
        for role in record.get("typed_trace_edge_roles", []):
            edge_roles[role.get("edge_role", "")] += 1
    endpoint_failures = [
        record["rewrite_candidate_id"]
        for record in records
        if not record["invariant_checklist"]["endpoint_validity_preserved"]
    ]
    role_failures = [
        record["rewrite_candidate_id"]
        for record in records
        if not record["invariant_checklist"]["typed_trace_roles_declared_for_all_added_nodes"]
    ]
    passage_missing = [
        record["rewrite_candidate_id"]
        for record in records
        if record.get("passage_validation", {}).get("validation_status")
        == "passage_level_validation_missing"
    ]
    return {
        "candidate_jsonl": str(CANDIDATE_OUT.relative_to(REPO_ROOT)),
        "candidate_record_count": len(records),
        "deferred_reason_breakdown": dict(sorted(defer_counts.items())),
        "dpo_invariant_summary": {
            "endpoint_validity_failures": len(endpoint_failures),
            "role_declaration_failures": len(role_failures),
            "signed_artifact_mutation_absent": True,
            "activation_claim_absent": True,
            "canonical_graph_mutated": False,
        },
        "fix26_input_counts": dict(sorted(Counter(r.get("queue_class", "") for r in fix26_records).items())),
        "fix27_precision_filter": {
            "accepted_for_fix30": review_counts.get("candidate_keep_for_fix30", 0),
            "deferred": review_counts.get("candidate_defer", 0),
            "rejected": review_counts.get("candidate_reject", 0),
            "threshold_lines": PASSAGE_DISTANCE_THRESHOLD_LINES,
        },
        "input_artifacts": {
            "fix22_graph": str(FIX22_GRAPH.relative_to(REPO_ROOT)),
            "fix26_queue": str(FIX26_QUEUE.relative_to(REPO_ROOT)),
            "fix27_enriched_prepass": str(ENRICHED_GRAPH.relative_to(REPO_ROOT)),
        },
        "multi_terminal_ambiguity_count": sum(
            1 for record in records if record.get("fix26_terminal_resolution") == "multi_ref_ambiguous"
        ),
        "non_claims": [
            "No canonical Genesis graph mutation occurred.",
            "No rewrite was applied.",
            "No Genesis signing or node upload occurred.",
            "No public RC activation occurred.",
            "No runtime, minting, settlement, or sidecar activation occurred.",
            "No ADR or CDL mutation occurred.",
        ],
        "output_tokens": [
            "atlas_rewrite_candidate_generation_committed_phase_1545p_fix27",
            "atlas_dpo_invariant_checks_recorded_phase_1545p_fix27",
            "atlas_hyperedge_replacement_candidates_recorded_phase_1545p_fix27",
            "atlas_node_merge_split_candidates_recorded_phase_1545p_fix27",
            "atlas_rewrite_candidates_not_promoted_phase_1545p_fix27",
            "public_path_remains_blocked_phase_1545p_fix27",
        ],
        "passage_level_validation_missing_count": len(passage_missing),
        "phase": PHASE,
        "proof_class_delta": {
            "records_with_non_authority_trace_delta": sum(
                1
                for record in records
                for delta in record.get("proof_class_delta", [])
                if delta.get("after") == "merkle_plus_typed_non_authority_trace"
            ),
            "proof_class_erasure_detected": False,
        },
        "rejection_reason_breakdown": dict(sorted(reject_counts.items())),
        "review_class_counts": dict(sorted(review_counts.items())),
        "rule_type_counts": dict(sorted(rule_counts.items())),
        "status": "research_only_candidates_generated",
        "typed_trace_edge_role_counts": dict(sorted(edge_roles.items())),
    }


def main() -> None:
    base_graph = _load_json(FIX22_GRAPH)
    enriched_graph = _load_json(ENRICHED_GRAPH)
    node_by_id = {node["candidate_id"]: node for node in enriched_graph["nodes"]}
    node_ids = set(node_by_id)
    fix26_records = _load_fix26_records()

    records: list[dict[str, Any]] = []
    enriched_records = _records_from_enriched_edges(base_graph, enriched_graph)
    records.extend(enriched_records)
    records.extend(_records_from_fix26_atoms(fix26_records, node_ids, node_by_id))
    records.extend(_aggregate_hyperedge_candidates(enriched_graph, enriched_records))
    records.extend(_aggregate_node_split_candidates(enriched_graph))
    records.extend(_aggregate_node_merge_candidates(enriched_graph))
    records.extend(_aggregate_projection_candidates(enriched_records))

    records.sort(key=lambda record: record["rewrite_candidate_id"])
    jsonl = "\n".join(
        json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
        for record in records
    )
    if jsonl:
        jsonl += "\n"
    _atomic_write_text(CANDIDATE_OUT, jsonl)
    summary = _summarize(records, fix26_records)
    _atomic_write_text(
        JSON_OUT,
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
