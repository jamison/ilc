#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Generate the Fix51 epistemic_gap seed candidate overlay."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE_CANDIDATES = (
    ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix50.json",
    ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix49.json",
    ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix48.json",
)
OUTPUT = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix51.json"
REPORT = ROOT / "docs" / "specs" / "ilc_fix51_epistemic_gap_schema_report_v0.1.md"
QUEUE = ROOT / "docs" / "specs" / "ilc_fix50_unresolved_authority_repair_queue_v0.1.json"
SCHEMA = ROOT / "docs" / "specs" / "ilc_epistemic_gap_node_schema_v0.1.json"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _edge_id(source: str, edge_type: str, target: str) -> str:
    return "edge:" + hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]


def _gap_id(source_node_id: str, expected_edge_type: str, target_schema_hint: str) -> str:
    preimage = json.dumps(
        {
            "source_node_id": source_node_id,
            "expected_edge_type": expected_edge_type,
            "target_schema_hint": target_schema_hint,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return "gap:" + hashlib.sha256(preimage.encode("utf-8")).hexdigest()[:24]


def _select_base() -> Path:
    for path in BASE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No Fix50/Fix49/Fix48 candidate found")


def _seed_gap_node() -> dict[str, Any]:
    source_node_id = NODE0
    expected_edge_type = "GOVERNS"
    target_schema_hint = (
        "CDL-098 Genesis Graph Update Authority node after Phase 1573a is "
        "ratified and consumed; currently an unconsumed candidate gap"
    )
    target_prefix_hint = "cdl:"
    gap_id = _gap_id(source_node_id, expected_edge_type, target_schema_hint)
    gossip_hash = hashlib.sha256(
        f"{gap_id}{expected_edge_type}{target_prefix_hint}".encode("utf-8")
    ).hexdigest()
    return {
        "annotation_method": "fix51_epistemic_gap_schema",
        "authority_boundary": "not_authority_promotion",
        "authority_effect": "none_until_resolved",
        "candidate_id": gap_id,
        "candidate_status": "fix51_support_only_not_canonical",
        "candidate_targets": [],
        "created_by_phase": "phase_1545p_fix51",
        "expected_edge_type": expected_edge_type,
        "expiry_epochs": None,
        "gap_id": gap_id,
        "gossip_hash": gossip_hash,
        "gossip_publishable": True,
        "label": "Epistemic gap: unconsumed CDL-098 Genesis graph update authority",
        "node_kind": "epistemic_gap",
        "projection_policy": {
            "authority_projection": "excluded",
            "frontier_projection": "included",
            "research_projection": "included",
        },
        "resolved_by_edge_id": None,
        "resolution_phase": None,
        "signature_status": "unsigned_candidate_preimage",
        "signing_posture": "not_atlas_signing_ready",
        "source_node_id": source_node_id,
        "status": "open",
        "target_prefix_hint": target_prefix_hint,
        "target_schema_hint": target_schema_hint,
    }


def _seed_gap_edge(source: str, target: str) -> dict[str, Any]:
    edge_type = "EXPECTS_RESOLUTION"
    return {
        "annotation_method": "fix51_epistemic_gap_schema",
        "annotation_phase": "phase_1545p_fix51",
        "candidate_status": "fix51_support_only_not_canonical",
        "edge_id": _edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "phase": "phase_1545p_fix51",
        "rationale": (
            "NODE0 records an open Genesis graph update authority gap for "
            "unconsumed CDL-098 without treating the gap as authority-bearing."
        ),
        "review_status": "candidate_only_not_authority_promotion",
        "signature_status": "unsigned_candidate_preimage",
        "source": source,
        "target": target,
    }


def main() -> int:
    base_path = _select_base()
    candidate = _load(base_path)
    base_nodes = list(candidate["nodes"])
    base_edges = list(candidate["edges"])
    node_ids = {node.get("candidate_id") for node in base_nodes if isinstance(node, dict)}
    edge_ids = {edge.get("edge_id") for edge in base_edges if isinstance(edge, dict)}

    gap_node = _seed_gap_node()
    gap_edge = _seed_gap_edge(gap_node["source_node_id"], gap_node["candidate_id"])

    nodes_added = 0
    edges_added = 0
    if gap_node["candidate_id"] not in node_ids:
        base_nodes.append(gap_node)
        nodes_added += 1
    if gap_edge["edge_id"] not in edge_ids:
        base_edges.append(gap_edge)
        edges_added += 1

    report = {
        "base_candidate_path": str(base_path.relative_to(ROOT)),
        "base_candidate_sha256": _sha256(base_path),
        "base_node_count": len(candidate["nodes"]),
        "base_edge_count": len(candidate["edges"]),
        "output_candidate_path": str(OUTPUT.relative_to(ROOT)),
        "output_node_count": len(base_nodes),
        "output_edge_count": len(base_edges),
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "seed_gap_nodes_added": nodes_added,
        "expects_resolution_edges_added": edges_added,
        "seed_gap_node_id": gap_node["candidate_id"],
        "seed_gap_source_node_id": gap_node["source_node_id"],
        "seed_gap_expected_edge_type": gap_node["expected_edge_type"],
        "seed_gap_gossip_publishable": gap_node["gossip_publishable"],
        "seed_gap_candidate_targets_count": len(gap_node["candidate_targets"]),
        "non_claims": [
            "Fix51 is an unsigned Atlas candidate schema pass.",
            "Epistemic gap nodes are excluded from authority projection.",
            "No Genesis signing occurred.",
            "No canonical Atlas mutation occurred.",
            "No public graph publication occurred.",
            "No public RC activation occurred.",
            "No runtime, economic, network, ADR, or CDL activation occurred.",
        ],
    }
    output = dict(candidate)
    output["nodes"] = base_nodes
    output["edges"] = base_edges
    output["fix51_generation_report"] = report
    output["candidate_status"] = "fix51_support_only_not_canonical"
    output.setdefault("non_claims", [])
    for non_claim in report["non_claims"]:
        if non_claim not in output["non_claims"]:
            output["non_claims"].append(non_claim)

    _dump(OUTPUT, output)
    _write_text(
        REPORT,
        "\n".join(
            [
                "# Fix51 Epistemic Gap Schema Report v0.1",
                "",
                f"- Base candidate: `{report['base_candidate_path']}`",
                f"- Base candidate SHA-256: `{report['base_candidate_sha256']}`",
                f"- Base nodes: `{report['base_node_count']}`",
                f"- Base edges: `{report['base_edge_count']}`",
                f"- Output candidate: `{report['output_candidate_path']}`",
                f"- Output nodes: `{report['output_node_count']}`",
                f"- Output edges: `{report['output_edge_count']}`",
                f"- Schema: `{report['schema_path']}`",
                f"- Schema SHA-256: `{report['schema_sha256']}`",
                f"- Seed gap node: `{report['seed_gap_node_id']}`",
                f"- Seed source node: `{report['seed_gap_source_node_id']}`",
                f"- Expected edge type: `{report['seed_gap_expected_edge_type']}`",
                f"- Candidate targets count: `{report['seed_gap_candidate_targets_count']}`",
                "",
                "## Non-Claims",
                "",
                "- Fix51 is unsigned, support-only, and noncanonical.",
                "- No Genesis signing occurred.",
                "- No canonical Atlas mutation occurred.",
                "- No public graph publication or public RC activation occurred.",
                "- No runtime, economic, network, ADR, or CDL activation occurred.",
                "",
            ]
        ),
    )
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
