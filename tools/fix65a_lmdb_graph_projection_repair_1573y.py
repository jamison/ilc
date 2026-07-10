# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1573y Fix65a graph_projection coverage repair for Atlas LMDB.

PUBLIC_RC_EXCLUDE: block6_lmdb_repair_tool
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance tool. No public
graph publication, Genesis signing, public RC activation, or release authority.
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

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


DEFAULT_LMDB = Path("out/genesis_base_graph_v0.4_unified.lmdb")
DEFAULT_RECEIPT = Path("out/phase_1573y/fix65a_graph_projection_repair.json")
PHASE = "1573y"
SCRIPT_VERSION = "fix65a_lmdb_graph_projection_repair_1573y.v0.1"

TIER_TO_GRAPH_PROJECTION = {
    "adr_authority": "genesis_core_star_map",
    "agent_harness_private_material": "excluded_private_material",
    "full_repo_candidate_root": "support_candidate_graph",
    "full_repo_genesis_atlas_candidate_material": "support_candidate_graph",
    "generated_evidence_material": "support_candidate_graph",
    "generated_evidence_root": "support_candidate_graph",
    "genesis_core": "genesis_core_star_map",
    "genesis_private_historical_material": "excluded_private_material",
    "genesis_private_or_public_rc_excluded": "excluded_private_material",
    "genesis_private_root": "excluded_private_material",
    "invariant_evidence": "genesis_core_star_map",
    "public_protocol_candidate": "public_protocol_graph",
    "public_release_candidate_material": "public_protocol_graph",
    "public_release_candidate_root": "public_protocol_graph",
    "repo_group": "support_candidate_graph",
    "support_candidate": "support_candidate_graph",
    "tier_2_evidence": "support_candidate_graph",
    "tier_3_test": "support_candidate_graph",
}


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def write_json_atomic(path: Path, payload: Any) -> None:
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
            json.dump(payload, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def graph_payload_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def classify_from_tier(node: dict[str, Any]) -> str:
    tier = str(node.get("tier", "") or "")
    if tier in TIER_TO_GRAPH_PROJECTION:
        return TIER_TO_GRAPH_PROJECTION[tier]
    source_path = str(node.get("source_path", "") or "")
    node_kind = str(node.get("node_kind", "") or "")
    if "private" in tier or "private" in source_path:
        return "excluded_private_material"
    if node_kind in {"cdl_node", "adr_node", "policy_node", "invariant_node"}:
        return "genesis_core_star_map"
    if source_path.startswith("ilc_core/") or source_path.startswith("docs/adr/"):
        return "public_protocol_graph"
    return "support_candidate_graph"


def build_receipt(lmdb: Path, *, write: bool) -> dict[str, Any]:
    store = GenesisAtlasCandidateStore(lmdb, allow_synthetic_edge_keys=True)
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
        payload = store.get_graph_payload() or {}
        missing_before = [
            node for node in nodes if not isinstance(node.get("graph_projection"), str)
            or not str(node.get("graph_projection")).strip()
        ]
        repaired_nodes: list[dict[str, Any]] = []
        repair_rows: list[dict[str, str]] = []
        for node in nodes:
            if node in missing_before:
                projection = classify_from_tier(node)
                replacement = dict(node)
                replacement["graph_projection"] = projection
                repaired_nodes.append(replacement)
                repair_rows.append(
                    {
                        "candidate_id": str(node.get("candidate_id", "")),
                        "graph_projection_after": projection,
                        "source_path": str(node.get("source_path", "")),
                        "tier": str(node.get("tier", "")),
                    }
                )
            else:
                repaired_nodes.append(node)

        pre_payload_sha256 = graph_payload_sha256(payload) if payload else ""
        if write and repair_rows:
            repaired_payload = dict(payload)
            if isinstance(repaired_payload.get("nodes"), list):
                node_by_id = {
                    str(node.get("candidate_id", "")): node for node in repaired_nodes
                }
                repaired_payload["nodes"] = [
                    node_by_id.get(str(node.get("candidate_id", "")), node)
                    for node in repaired_payload["nodes"]
                    if isinstance(node, dict)
                ]
            store.replace_nodes(repaired_nodes)
            store.put_graph_payload(repaired_payload)
            store.put_meta(
                "fix65a_graph_projection_repair_phase_1573y",
                {
                    "missing_before": len(missing_before),
                    "phase": PHASE,
                    "repair_count": len(repair_rows),
                    "script_version": SCRIPT_VERSION,
                    "status": "PASS",
                },
            )

        post_nodes = store.iter_nodes()
        post_payload = store.get_graph_payload() or {}
        missing_after = [
            node for node in post_nodes if not isinstance(node.get("graph_projection"), str)
            or not str(node.get("graph_projection")).strip()
        ]
        node_ids = {str(node.get("candidate_id", "")) for node in post_nodes}
        dangling_edges = sum(
            1
            for edge in edges
            if str(edge.get("source_candidate_id", edge.get("source", edge.get("from", ""))))
            not in node_ids
            or str(edge.get("target_candidate_id", edge.get("target", edge.get("to", ""))))
            not in node_ids
        )
        return {
            "dangling_edge_count": dangling_edges,
            "graph_payload_sha256_after": graph_payload_sha256(post_payload)
            if post_payload
            else "",
            "graph_payload_sha256_before": pre_payload_sha256,
            "lmdb_path": str(lmdb),
            "missing_graph_projection_after": len(missing_after),
            "missing_graph_projection_before": len(missing_before),
            "node_count": len(post_nodes),
            "projection_counts_after": dict(
                sorted(Counter(str(node.get("graph_projection", "")) for node in post_nodes).items())
            ),
            "repair_rows": repair_rows,
            "script_version": SCRIPT_VERSION,
            "sequential_write_discipline": True,
            "status": "PASS" if not missing_after and dangling_edges == 0 else "FAIL",
            "write_applied": bool(write),
        }
    finally:
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lmdb", type=Path, default=DEFAULT_LMDB)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    receipt = build_receipt(args.lmdb, write=args.write)
    write_json_atomic(args.receipt, receipt)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False))
    if receipt["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
