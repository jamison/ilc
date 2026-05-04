#!/usr/bin/env python3
"""Build the SIM-SPECTRAL-05 branchial claim-state projection.

The artifact is research/simulation scope. It is deterministic and leaves signed
Genesis v0.1 artifacts untouched.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STAR_MAP_PATH = ROOT / "out/genesis_core_star_map_v0.1.json"
CLAIM_PROJECTION_PATH = ROOT / "out/genesis_claim_composition_projection_v0.1.json"
ROOT_ENVELOPE_PATH = ROOT / "out/genesis_signing_root_envelope_v0.1.json"
OUTPUT_PATH = ROOT / "out/genesis_branchial_claim_projection_v0.1.json"

ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"

CLAIM_EDGE_OPERATION = {
    "defines_claim": "compose",
    "derives_from": "compose",
    "invokes_primitive": "compose",
    "constrains_policy": "amend",
    "implements_runtime": "succeed",
}

STAR_EDGE_OPERATION = {
    "ATTESTATION": "succeed",
    "PROVENANCE": "succeed",
    "PRIMITIVE_INVOCATION": "compose",
    "CONSTRAINS": "amend",
    "GOVERNS": "amend",
}

GENESIS_ANCHOR_CATEGORIES = {
    "authority_document",
    "bootstrap_artifact",
    "bootstrap_lineage",
    "constitutional_artifact",
    "genesis_authority",
    "genesis_authority_artifact",
    "genesis_authority_ceremony",
    "genesis_authority_schema",
    "genesis_axiom",
    "governance_event",
    "truth_primitive",
}


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("branchial_projection_expected_json_object")
    return data


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    if not slug:
        raise ValueError("branchial_projection_empty_slug")
    return slug


def _state_id(claim_id: str, version: str, status: str) -> str:
    return f"state:{_slug(claim_id)}:{_slug(version)}:{_slug(status)}"


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _status_from_authority(authority_status: str, signature_status: str) -> str:
    if signature_status == "signed":
        if authority_status.startswith("ratified"):
            return "ratified_signed"
        if authority_status.startswith("accepted"):
            return "accepted_signed"
        return "signed"
    return authority_status or "current"


def _is_genesis_anchor(node: dict[str, Any]) -> bool:
    category = str(node.get("category", ""))
    authority_status = str(node.get("authority_status", ""))
    signature_status = str(node.get("signature_status", ""))
    return (
        signature_status == "signed"
        and (
            category in GENESIS_ANCHOR_CATEGORIES
            or authority_status.startswith("accepted_ADR")
            or authority_status.startswith("ratified")
        )
    )


def _star_vertex(node: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(node["candidate_id"])
    version = str(node.get("star_map_version") or "v0.1")
    status = _status_from_authority(
        str(node.get("authority_status", "")),
        str(node.get("signature_status", "")),
    )
    genesis_anchor = _is_genesis_anchor(node)
    return {
        "authority_status": node.get("authority_status"),
        "claim_id": candidate_id,
        "derivation_state_type": "signed_v0_1_authority_state",
        "genesis_anchor": genesis_anchor,
        "genesis_anchor_id": candidate_id if genesis_anchor else None,
        "id": _state_id(candidate_id, version, status),
        "label": node.get("label", candidate_id),
        "source_category": node.get("category"),
        "source_signature_status": node.get("signature_status"),
        "status": status,
        "version": version,
    }


def _claim_vertex(vertex: dict[str, Any], anchor_ids: set[str]) -> dict[str, Any]:
    claim_id = str(vertex["vertex_id"])
    version = str(vertex.get("source_star_map_version") or "v0.1")
    vertex_kind = str(vertex.get("vertex_kind", "claim_state"))
    source_node_id = str(vertex.get("source_node_id") or "")
    authority_source_ref = str(vertex.get("authority_source_ref") or "")
    genesis_anchor = vertex_kind in {"primitive", "historical_artifact"}
    direct_anchor = source_node_id if source_node_id in anchor_ids else authority_source_ref
    return {
        "authority_source_ref": authority_source_ref,
        "claim_id": claim_id,
        "content_hash": vertex.get("content_hash"),
        "derivation_state_type": f"{vertex_kind}_state",
        "genesis_anchor": genesis_anchor,
        "genesis_anchor_id": claim_id if genesis_anchor else direct_anchor,
        "id": _state_id(claim_id, version, "current"),
        "label": vertex.get("label", claim_id),
        "source_node_id": source_node_id,
        "status": "current",
        "version": version,
    }


def _edge_id(source: str, target: str, operation_type: str, index: int) -> str:
    return f"branchial_edge:{_slug(operation_type)}:{index:04d}:{_slug(source)[-32:]}:{_slug(target)[-32:]}"


def _make_edge(
    source: str,
    target: str,
    operation_type: str,
    reason: str,
    index: int,
    primitive_hook: str,
) -> dict[str, Any]:
    return {
        "edge_id": _edge_id(source, target, operation_type, index),
        "operation_type": operation_type,
        "primitive_hook": primitive_hook,
        "reason": reason,
        "source": source,
        "target": target,
    }


def build_projection() -> dict[str, Any]:
    star_map = _read_json(STAR_MAP_PATH)
    claim_projection = _read_json(CLAIM_PROJECTION_PATH)
    root_envelope = _read_json(ROOT_ENVELOPE_PATH)
    if root_envelope.get("envelope_hash") != ROOT_HASH:
        raise ValueError("branchial_projection_unexpected_root_hash")

    star_nodes = sorted(star_map["nodes"], key=lambda node: str(node["candidate_id"]))
    claim_vertices = sorted(
        claim_projection["vertices"],
        key=lambda vertex: str(vertex["vertex_id"]),
    )

    star_vertices = [_star_vertex(node) for node in star_nodes]
    star_state_by_claim = {vertex["claim_id"]: vertex["id"] for vertex in star_vertices}
    anchor_ids = {
        vertex["claim_id"]
        for vertex in star_vertices
        if bool(vertex["genesis_anchor"])
    }

    claim_state_vertices = [_claim_vertex(vertex, anchor_ids) for vertex in claim_vertices]
    claim_state_by_claim = {
        vertex["claim_id"]: vertex["id"]
        for vertex in claim_state_vertices
    }

    vertices = sorted(star_vertices + claim_state_vertices, key=lambda vertex: vertex["id"])
    edge_index = 0
    edges: list[dict[str, Any]] = []

    for claim_edge in sorted(claim_projection["edges"], key=lambda edge: str(edge["edge_id"])):
        source = claim_state_by_claim.get(str(claim_edge["source"]))
        target = claim_state_by_claim.get(str(claim_edge["target"]))
        if source is None or target is None:
            continue
        reason = str(claim_edge["reason"])
        operation = CLAIM_EDGE_OPERATION.get(reason, "compose")
        primitive_hook = "revise.assert" if operation == "amend" else "link.claim"
        if operation == "succeed":
            primitive_hook = "commit.epoch"
        edge_index += 1
        edges.append(_make_edge(source, target, operation, reason, edge_index, primitive_hook))

    for claim_vertex in claim_vertices:
        claim_state = claim_state_by_claim[str(claim_vertex["vertex_id"])]
        source_node_id = str(claim_vertex.get("source_node_id") or "")
        authority_state = star_state_by_claim.get(source_node_id)
        if authority_state is None:
            continue
        edge_index += 1
        edges.append(
            _make_edge(
                claim_state,
                authority_state,
                "succeed",
                "observer_trace_to_signed_authority_source",
                edge_index,
                "commit.epoch",
            )
        )

    for star_edge in sorted(star_map["edges"], key=lambda edge: str(edge["edge_id"])):
        source = star_state_by_claim.get(str(star_edge["source"]))
        target = star_state_by_claim.get(str(star_edge["target"]))
        if source is None or target is None:
            continue
        edge_type = str(star_edge.get("edge_type", "PROVENANCE"))
        operation = STAR_EDGE_OPERATION.get(edge_type, "succeed")
        primitive_hook = "commit.epoch" if operation == "succeed" else "link.claim"
        if operation == "amend":
            primitive_hook = "revise.assert"
        edge_index += 1
        edges.append(_make_edge(source, target, operation, edge_type, edge_index, primitive_hook))

    refute_state = star_state_by_claim.get("truth_primitive:refute.claim")
    if refute_state is not None:
        refutable_claims = [
            vertex
            for vertex in claim_state_vertices
            if vertex["derivation_state_type"] == "claim_composite_state"
        ][:12]
        for claim_state in refutable_claims:
            edge_index += 1
            edges.append(
                _make_edge(
                    str(claim_state["id"]),
                    refute_state,
                    "refute",
                    "cdl_v7_popperian_refutation_hook",
                    edge_index,
                    "refute.claim",
                )
            )

    edges = sorted(edges, key=lambda edge: edge["edge_id"])
    genesis_primitives = sorted(
        {
            str(vertex["claim_id"])
            for vertex in vertices
            if bool(vertex["genesis_anchor"])
        }
    )

    payload: dict[str, Any] = {
        "edge_count": len(edges),
        "edges": edges,
        "genesis_primitives": genesis_primitives,
        "metadata": {
            "branchial_projection_design": "docs/sims/sim_spectral_05/branchial_projection_design_1170_v0.1.md",
            "cdl_v7_runtime_reference": CDL_V7_RUNTIME_VERSION,
            "claim_projection": str(CLAIM_PROJECTION_PATH.relative_to(ROOT)),
            "observer_slice": "claim_composition_plus_authority",
            "provenance_equivalence_criterion": "ADR-0037 §3.2",
            "root_envelope_hash": ROOT_HASH,
            "source_star_map": str(STAR_MAP_PATH.relative_to(ROOT)),
            "sybil_branchial_template": {
                "convergence_failure": "paths converge first at non-Genesis injection point",
                "operation_pattern": [
                    "sybil_claim_i -> sybil_injection_point",
                    "sybil_injection_point -> coordinated_issuer",
                ],
                "topology_label": "sybil_cluster_branchial",
            },
        },
        "phase": 1170,
        "projection_type": "branchial_claim_state",
        "token": "sim_spectral_05_track_b_projection_built_phase_1170",
        "version": "v0.1",
        "vertex_count": len(vertices),
        "vertex_schema": "(claim_id, version, status)",
        "vertices": vertices,
    }
    payload["projection_hash"] = _canonical_hash(payload)
    return payload


def main() -> None:
    projection = build_projection()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(projection, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
