#!/usr/bin/env python3
"""Build the SIM-SPECTRAL-04 Genesis claim-composition projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_STAR_MAP = Path("out/genesis_core_star_map_v0.1.json")
DEFAULT_AUDIT = Path("out/genesis_32_node_composability_audit_v0.1.json")
DEFAULT_PLAN = Path("docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md")
DEFAULT_OUTPUT = Path("out/genesis_claim_composition_projection_v0.1.json")
PHASE_TOKEN = "sim_spectral_04_claim_composition_projection_built_phase_1160"
ALLOWED_REASONS = {
    "attests_history",
    "constrains_policy",
    "defines_claim",
    "derives_from",
    "implements_runtime",
    "invokes_primitive",
}
CLASS_VERTEX_COUNTS = {
    "primitive": 1,
    "historical_artifact": 1,
    "parameterized_policy": 2,
    "claim_composite": 3,
    "runtime_binding_pending": 2,
}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("claim_projection_input_must_be_json_object")
    return data


def _slug(value: str) -> str:
    return (
        value.replace(":", "_")
        .replace(".", "_")
        .replace("-", "_")
        .replace("/", "_")
        .lower()
    )


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _vertex_kinds(projection_class: str) -> list[tuple[str, str]]:
    if projection_class == "primitive":
        return [("basis", "primitive")]
    if projection_class == "historical_artifact":
        return [("history_anchor", "historical_artifact")]
    if projection_class == "parameterized_policy":
        return [("policy_claim", "parameterized_policy"), ("parameter", "parameterized_policy")]
    if projection_class == "claim_composite":
        return [
            ("claim_definition", "claim_composite"),
            ("claim_constraint", "claim_composite"),
            ("claim_consequence", "claim_composite"),
        ]
    if projection_class == "runtime_binding_pending":
        return [("runtime_bridge", "runtime_binding_pending"), ("pending_binding", "runtime_binding_pending")]
    raise ValueError(f"claim_projection_unknown_projection_class:{projection_class}")


def _reason_for_class(projection_class: str) -> str:
    return {
        "claim_composite": "defines_claim",
        "historical_artifact": "attests_history",
        "parameterized_policy": "constrains_policy",
        "primitive": "invokes_primitive",
        "runtime_binding_pending": "implements_runtime",
    }[projection_class]


def build_projection(star_map_path: Path, audit_path: Path, plan_path: Path) -> dict[str, Any]:
    star_map = _load_json(star_map_path)
    audit = _load_json(audit_path)
    if not plan_path.exists():
        raise ValueError("claim_projection_plan_missing")
    nodes = star_map.get("nodes")
    entries = audit.get("entries")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("claim_projection_star_map_nodes_missing")
    if not isinstance(entries, list) or not entries:
        raise ValueError("claim_projection_audit_entries_missing")

    star_node_ids = {
        node["candidate_id"]
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("candidate_id"), str)
    }
    if len(star_node_ids) != 32:
        raise ValueError("claim_projection_expected_32_signed_genesis_nodes")

    vertices: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    first_vertex_by_source: dict[str, str] = {}
    primitive_vertices: list[str] = []

    for entry in sorted(entries, key=lambda item: item["node_id"]):
        node_id = entry.get("node_id")
        authority_source_ref = entry.get("authority_source_ref")
        projection_class = entry.get("projection_class")
        if node_id not in star_node_ids or authority_source_ref not in star_node_ids:
            raise ValueError(f"claim_projection_audit_node_missing_from_star_map:{node_id}")
        if not isinstance(projection_class, str):
            raise ValueError("claim_projection_entry_missing_projection_class")

        local_vertices: list[str] = []
        for suffix, vertex_kind in _vertex_kinds(projection_class):
            vertex_id = f"claim:{_slug(node_id)}:{suffix}"
            vertex = {
                "authority_source_ref": authority_source_ref,
                "label": f"{entry.get('label', node_id)} / {suffix}",
                "projection_class": projection_class,
                "source_node_id": node_id,
                "source_star_map_version": entry.get("source_star_map_version", "v0.1"),
                "vertex_id": vertex_id,
                "vertex_kind": vertex_kind,
            }
            vertex["content_hash"] = _canonical_hash(vertex)
            vertices.append(vertex)
            local_vertices.append(vertex_id)
            if projection_class == "primitive":
                primitive_vertices.append(vertex_id)
        first_vertex_by_source[node_id] = local_vertices[0]

        reason = _reason_for_class(projection_class)
        for index in range(len(local_vertices) - 1):
            edges.append(
                {
                    "edge_id": f"claim_edge:{_slug(node_id)}:{index + 1}",
                    "reason": reason,
                    "source": local_vertices[index],
                    "target": local_vertices[index + 1],
                    "weight": 1.0,
                }
            )

    # Preserve the authority star-map relationships as low-weight derived claim links.
    star_edges = star_map.get("edges")
    if not isinstance(star_edges, list):
        raise ValueError("claim_projection_star_map_edges_missing")
    bridge_index = 0
    for edge in sorted(star_edges, key=lambda item: item.get("edge_id", "")):
        source = edge.get("source")
        target = edge.get("target")
        if source in first_vertex_by_source and target in first_vertex_by_source:
            bridge_index += 1
            edges.append(
                {
                    "edge_id": f"claim_edge:authority_bridge:{bridge_index:04d}",
                    "reason": "derives_from",
                    "source": first_vertex_by_source[source],
                    "target": first_vertex_by_source[target],
                    "weight": 0.35,
                }
            )

    # Connect every composite/policy/runtime surface to the primitive basis. This is the
    # claim-composition layer that the raw authority graph intentionally lacks.
    primitive_cycle = sorted(primitive_vertices)
    if not primitive_cycle:
        raise ValueError("claim_projection_missing_primitive_vertices")
    invocation_index = 0
    for vertex in sorted(vertices, key=lambda item: item["vertex_id"]):
        if vertex["projection_class"] == "primitive":
            continue
        primitive = primitive_cycle[invocation_index % len(primitive_cycle)]
        invocation_index += 1
        edges.append(
            {
                "edge_id": f"claim_edge:primitive_invocation:{invocation_index:04d}",
                "reason": "invokes_primitive",
                "source": primitive,
                "target": vertex["vertex_id"],
                "weight": 0.75,
            }
        )

    for edge in edges:
        if edge["reason"] not in ALLOWED_REASONS:
            raise ValueError(f"claim_projection_unknown_edge_reason:{edge['reason']}")

    payload = {
        "allowed_edge_reasons": sorted(ALLOWED_REASONS),
        "artifact": "genesis_claim_composition_projection_v0.1",
        "authority_source_count": len({vertex["authority_source_ref"] for vertex in vertices}),
        "edge_count": len(edges),
        "edges": sorted(edges, key=lambda item: item["edge_id"]),
        "format_version": "genesis_claim_composition_projection_v0.1",
        "phase": "1160",
        "source_audit": str(audit_path),
        "source_plan": str(plan_path),
        "source_root_envelope_hash": star_map.get("metadata", {}).get("root_envelope_hash"),
        "source_star_map": str(star_map_path),
        "token": PHASE_TOKEN,
        "vertex_count": len(vertices),
        "vertices": sorted(vertices, key=lambda item: item["vertex_id"]),
    }
    payload["projection_hash"] = _canonical_hash(
        {
            "edges": payload["edges"],
            "format_version": payload["format_version"],
            "vertices": payload["vertices"],
        }
    )
    return payload


def build_genesis_claim_composition_projection(
    star_map_path: Path = DEFAULT_STAR_MAP,
    audit_path: Path = DEFAULT_AUDIT,
    plan_path: Path = DEFAULT_PLAN,
) -> dict[str, Any]:
    return build_projection(star_map_path, audit_path, plan_path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--star-map", type=Path, default=DEFAULT_STAR_MAP)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> dict[str, Any]:
    args = _build_parser().parse_args(argv)
    payload = build_projection(args.star_map, args.audit, args.plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "projection_hash": payload["projection_hash"]}, sort_keys=True))
    return payload


if __name__ == "__main__":
    main()
