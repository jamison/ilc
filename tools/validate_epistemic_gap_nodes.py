#!/usr/bin/env python3
"""Validate epistemic_gap nodes in a Genesis Atlas candidate graph.

This validator intentionally avoids a jsonschema runtime dependency. It checks
the Fix51 schema constraints that are load-bearing for graph safety:

- required fields and fixed non-authority posture;
- decimal-string KGC scores;
- authority/frontier/research projection policy;
- no GOVERNS edge touching an epistemic_gap node;
- inbound EXPECTS_RESOLUTION from an existing non-gap source.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "candidate_id",
    "node_kind",
    "gap_id",
    "status",
    "source_node_id",
    "expected_edge_type",
    "target_schema_hint",
    "target_prefix_hint",
    "candidate_targets",
    "authority_effect",
    "signing_posture",
    "projection_policy",
    "created_by_phase",
    "annotation_method",
    "candidate_status",
    "signature_status",
    "authority_boundary",
    "resolved_by_edge_id",
    "resolution_phase",
    "expiry_epochs",
    "gossip_publishable",
    "gossip_hash",
)

VALID_STATUSES = {"open", "resolved", "expired_unresolved", "deferred"}
VALID_KGC_METHODS = {"TransE", "RotatE", "manual"}
DECIMAL_SCORE = re.compile(r"^(0|1)(\.\d+)?$")
GAP_ID = re.compile(r"^gap:[0-9a-f]{24}$")
GOSSIP_HASH = re.compile(r"^[0-9a-f]{64}$")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised by CLI users
        raise ValueError(f"{path}: cannot read JSON: {exc}") from exc


def _node_id(node: dict[str, Any]) -> str | None:
    return node.get("candidate_id") or node.get("node_id") or node.get("id")


def _validate_gap_node(node: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate_id = str(node.get("candidate_id", "<missing>"))

    for field in REQUIRED_FIELDS:
        if field not in node:
            errors.append(f"{candidate_id}: missing required field {field}")

    if node.get("node_kind") != "epistemic_gap":
        errors.append(f"{candidate_id}: node_kind must be epistemic_gap")
    if not str(node.get("candidate_id", "")).startswith("gap:"):
        errors.append(f"{candidate_id}: candidate_id must start with gap:")
    if not isinstance(node.get("gap_id"), str) or not GAP_ID.match(node["gap_id"]):
        errors.append(f"{candidate_id}: gap_id must match gap:<24 hex chars>")
    if node.get("status") not in VALID_STATUSES:
        errors.append(f"{candidate_id}: invalid status {node.get('status')!r}")

    fixed_values = {
        "authority_effect": "none_until_resolved",
        "signing_posture": "not_atlas_signing_ready",
        "created_by_phase": "phase_1545p_fix51",
        "annotation_method": "fix51_epistemic_gap_schema",
        "candidate_status": "fix51_support_only_not_canonical",
        "signature_status": "unsigned_candidate_preimage",
        "authority_boundary": "not_authority_promotion",
    }
    for field, expected in fixed_values.items():
        if node.get(field) != expected:
            errors.append(f"{candidate_id}: {field} must be {expected!r}")

    policy = node.get("projection_policy")
    if policy != {
        "authority_projection": "excluded",
        "frontier_projection": "included",
        "research_projection": "included",
    }:
        errors.append(f"{candidate_id}: invalid projection_policy")

    candidate_targets = node.get("candidate_targets")
    if not isinstance(candidate_targets, list):
        errors.append(f"{candidate_id}: candidate_targets must be a list")
    else:
        for index, target in enumerate(candidate_targets):
            if not isinstance(target, dict):
                errors.append(f"{candidate_id}: candidate_targets[{index}] must be object")
                continue
            score = target.get("kgc_score")
            if not isinstance(score, str) or not DECIMAL_SCORE.match(score):
                errors.append(
                    f"{candidate_id}: candidate_targets[{index}].kgc_score must be decimal string"
                )
            if target.get("kgc_method") not in VALID_KGC_METHODS:
                errors.append(f"{candidate_id}: candidate_targets[{index}].kgc_method invalid")
            if not isinstance(target.get("candidate_id"), str):
                errors.append(f"{candidate_id}: candidate_targets[{index}].candidate_id missing")
            if not isinstance(target.get("kgc_phase"), str):
                errors.append(f"{candidate_id}: candidate_targets[{index}].kgc_phase missing")

    if node.get("expiry_epochs") is not None:
        if not isinstance(node["expiry_epochs"], int) or node["expiry_epochs"] < 1:
            errors.append(f"{candidate_id}: expiry_epochs must be positive integer or null")

    gossip_publishable = node.get("gossip_publishable")
    gossip_hash = node.get("gossip_hash")
    if not isinstance(gossip_publishable, bool):
        errors.append(f"{candidate_id}: gossip_publishable must be boolean")
    elif gossip_publishable:
        if not isinstance(gossip_hash, str) or not GOSSIP_HASH.match(gossip_hash):
            errors.append(f"{candidate_id}: gossip_hash required when gossip_publishable")
    elif gossip_hash is not None:
        errors.append(f"{candidate_id}: gossip_hash must be null when not gossip_publishable")

    if not isinstance(node.get("source_node_id"), str):
        errors.append(f"{candidate_id}: source_node_id must be string")
    if not isinstance(node.get("expected_edge_type"), str):
        errors.append(f"{candidate_id}: expected_edge_type must be string")
    if not isinstance(node.get("target_schema_hint"), str):
        errors.append(f"{candidate_id}: target_schema_hint must be string")
    if node.get("target_prefix_hint") is not None and not isinstance(
        node.get("target_prefix_hint"), str
    ):
        errors.append(f"{candidate_id}: target_prefix_hint must be string or null")

    return errors


def validate_candidate(candidate: dict[str, Any]) -> list[str]:
    nodes = candidate.get("nodes")
    edges = candidate.get("edges")
    if not isinstance(nodes, list):
        return ["candidate: nodes must be a list"]
    if not isinstance(edges, list):
        return ["candidate: edges must be a list"]

    node_ids = {_node_id(node) for node in nodes if isinstance(node, dict)}
    node_ids.discard(None)
    gap_nodes = [
        node
        for node in nodes
        if isinstance(node, dict) and node.get("node_kind") == "epistemic_gap"
    ]
    gap_ids = {node["candidate_id"] for node in gap_nodes if "candidate_id" in node}
    non_gap_ids = node_ids - gap_ids

    errors: list[str] = []
    for node in gap_nodes:
        errors.extend(_validate_gap_node(node))
        source = node.get("source_node_id")
        if source not in non_gap_ids:
            errors.append(f"{node.get('candidate_id')}: source_node_id must be an existing non-gap node")

    inbound_expects: dict[str, int] = {gap_id: 0 for gap_id in gap_ids}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = edge.get("source")
        target = edge.get("target")
        edge_type = edge.get("edge_type")
        if edge_type == "GOVERNS" and (source in gap_ids or target in gap_ids):
            errors.append(f"{source}->{target}: GOVERNS must not touch epistemic_gap nodes")
        if edge_type == "EXPECTS_RESOLUTION" and target in inbound_expects:
            if source not in non_gap_ids:
                errors.append(f"{source}->{target}: EXPECTS_RESOLUTION source must be non-gap")
            inbound_expects[target] += 1
    for gap_id, count in inbound_expects.items():
        if count == 0:
            errors.append(f"{gap_id}: missing inbound EXPECTS_RESOLUTION edge")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="Genesis Atlas candidate JSON")
    args = parser.parse_args()

    try:
        candidate = _load_json(args.candidate)
        errors = validate_candidate(candidate)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"VALID: {args.candidate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
