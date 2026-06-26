#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Export deterministic browser view-model JSON from the Genesis Atlas LMDB.

PUBLIC_RC_EXCLUDE: graph_viz_export_research_tool
PUBLIC_RC_EXCLUDE_REASON: Local visualization adapter for unsigned Atlas
candidate projections; no signing, publication, upload, or canonical graph
mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
DEFAULT_DIGEST_MANIFEST = REPO_ROOT / "out/genesis_base_graph_v0.4_unified_lmdb_digest_fix61.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "out/viz_exports"
DEFAULT_SOURCE_CANDIDATE = "out/genesis_base_graph_v0.4_unified.lmdb"
KNOWN_SOURCE_SHA256S = {
    "fix41a": "3bcf8cdf248ea44248e72dce0c8209c92302826399b42524235cf8ee59936e52",
    "fix53": "5a8c6fb0787596e1b67976b66a395cead90a16cb42c432a1510c864ed56977f9",
}
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

VIZ_METADATA_PURPOSE = "diagnostic_input_identity_only_not_signing_proof"

VIEWS = ("all-local", "public-material", "private-local", "governance", "authority-core", "test-registry")

PRIVATE_GENERATED_TIERS = frozenset(
    {
        "genesis_private_or_public_rc_excluded",
        "genesis_private_historical_material",
        "agent_harness_private_material",
        "generated_evidence_material",
        "generated_evidence_root",
    }
)

AUTHORITY_PREFIXES = frozenset(
    {"truth_primitive", "policy", "artifact", "genesis_agent", "adr", "cdl", "ceremony"}
)
GOVERNANCE_EDGE_TYPES = frozenset(
    {
        "GOVERNS",
        "ATTESTATION",
        "REFERENCES_AUTHORITY",
        "IMPLEMENTS",
        "EVIDENCES",
        "CLASSIFIED_BY",
        "SAME_AUTHORITY",
        "OPENED_FOR",
        "PRELOCK_FOR",
        "RATIFICATION_EVIDENCE_FOR",
        "PROPOSES_CHANGE_TO",
        "RESOLVED_BY",
        "DERIVED_FROM",
        "CARRIES_FORWARD",
    }
)
TEST_EDGE_TYPES = frozenset({"TESTS", "COVERS_SYMBOL", "IMPLEMENTS", "IMPORTS_MODULE"})

PREFIX_COLORS: dict[str, str] = {
    "genesis_authority_root": "#ffffff",
    "truth_primitive": "#ff4444",
    "policy": "#ff9900",
    "phase": "#ccaa44",
    "artifact": "#ffcc00",
    "material_manifest_root": "#d6b24a",
    "material_partition_root": "#9f8a4a",
    "package_material_root": "#ffd966",
    "source_tree_overlay": "#7a7a55",
    "genesis_agent": "#ff66ff",
    "adr": "#7d5cff",
    "cdl": "#00bfff",
    "ceremony": "#ff88ff",
    "invariant": "#ff7744",
    "target": "#66aa66",
    "source": "#44cc88",
    "repo": "#888888",
    "atlas": "#aaaaaa",
    "other": "#cccccc",
}

EDGE_COLORS: dict[str, str] = {
    "GOVERNS": "#ff4444",
    "ATTESTATION": "#ff9900",
    "IMPLEMENTS": "#88aaff",
    "TESTS": "#44cccc",
    "COVERS_SYMBOL": "#33bbbb",
    "EVIDENCES": "#ffaa44",
    "REFERENCES_AUTHORITY": "#00cccc",
    "DERIVED_FROM": "#cc88ff",
    "CLASSIFIED_BY": "#cc44ff",
    "SAME_AUTHORITY": "#ee88ff",
    "SAME_SOURCE": "#44ff88",
    "OPENED_FOR": "#88ddff",
    "PRELOCK_FOR": "#88bbff",
    "RATIFICATION_EVIDENCE_FOR": "#88ffaa",
    "PROPOSES_CHANGE_TO": "#ffaa88",
    "RESOLVED_BY": "#aaff88",
    "CARRIES_FORWARD": "#aa66cc",
    "SOURCE_TREE_MEMBER": "#448844",
    "CONTAINS_FILE": "#444444",
    "CONTAINS_GROUP": "#444444",
    "CONTAINS_PARTITION": "#444444",
    "IMPORTS_MODULE": "#555555",
    "USES": "#7777aa",
    "PROVENANCE": "#888844",
    "PRIMITIVE_INVOCATION": "#ff6644",
    "CONSTRAINS": "#886644",
}


def _canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode(
        "utf-8"
    )


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(_canonical_json_bytes(payload))
            handle.write(b"\n")
        os.replace(tmp, path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def _load_digest_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fix42_digest_manifest_not_object")
    digests = payload.get("digests")
    if isinstance(digests, dict):
        source_digest = digests.get("source_file_sha256")
        lmdb_digest = digests.get("reexport_canonical_sha256")
        if not _is_sha256(source_digest) or not _is_sha256(lmdb_digest):
            raise ValueError("fix42_digest_manifest_missing_legacy_digests")
        source_candidate = str(payload.get("source_candidate", ""))
        expected_digest = KNOWN_SOURCE_SHA256S.get(source_candidate)
        if expected_digest is not None and source_digest != expected_digest:
            raise ValueError("fix42_digest_manifest_unexpected_source_sha256")
        return payload
    if payload.get("phase") == "1545p-Fix61":
        for key in ("node_digest", "edge_digest", "preimage_digest"):
            if not _is_sha256(payload.get(key)):
                raise ValueError(f"fix42_digest_manifest_missing_{key}")
        if payload.get("lmdb_path") != "out/genesis_base_graph_v0.4_unified.lmdb":
            raise ValueError("fix42_digest_manifest_unexpected_lmdb_path")
        return payload
    raise ValueError("fix42_digest_manifest_unsupported_schema")


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _manifest_digest_sha256(digest_manifest: dict[str, Any]) -> str:
    digests = digest_manifest.get("digests")
    if isinstance(digests, dict) and _is_sha256(digests.get("reexport_canonical_sha256")):
        return str(digests["reexport_canonical_sha256"])
    return hashlib.sha256(_canonical_json_bytes(digest_manifest)).hexdigest()


def _manifest_source_sha256(digest_manifest: dict[str, Any]) -> str:
    digests = digest_manifest.get("digests")
    if isinstance(digests, dict) and _is_sha256(digests.get("source_file_sha256")):
        return str(digests["source_file_sha256"])
    node_digest = digest_manifest.get("node_digest")
    if _is_sha256(node_digest):
        return str(node_digest)
    return _manifest_digest_sha256(digest_manifest)


def _manifest_source_path(digest_manifest: dict[str, Any]) -> str:
    value = digest_manifest.get("source_candidate_path") or digest_manifest.get("lmdb_path")
    return value if isinstance(value, str) and value else DEFAULT_SOURCE_CANDIDATE


def _prefix(node_id: str) -> str:
    return node_id.split(":", 1)[0]


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("id") or node.get("node_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix42_node_missing_id")
    return value


def _source(edge: dict[str, Any]) -> str:
    value = edge.get("source_candidate_id") or edge.get("source") or edge.get("from")
    return value if isinstance(value, str) else ""


def _target(edge: dict[str, Any]) -> str:
    value = edge.get("target_candidate_id") or edge.get("target") or edge.get("to")
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("type")
    return value if isinstance(value, str) else ""


def _tier(node: dict[str, Any]) -> str:
    value = node.get("tier")
    return value if isinstance(value, str) else ""


def _kind(node: dict[str, Any]) -> str:
    value = node.get("node_kind") or node.get("kind")
    return value if isinstance(value, str) else ""


def _projection(node: dict[str, Any]) -> str:
    value = node.get("graph_projection")
    return value if isinstance(value, str) else ""


def _status(node: dict[str, Any]) -> str:
    value = node.get("candidate_status") or node.get("status")
    return value if isinstance(value, str) else ""


def _label(node_id: str, node: dict[str, Any]) -> str:
    value = node.get("label") or node.get("source_path") or node_id
    label = value if isinstance(value, str) else node_id
    return label[-60:] if len(label) > 60 else label


def _visual_group(node_id: str, node: dict[str, Any]) -> str:
    """Return the UI category without mutating the canonical node ID or kind."""
    if node_id == NODE0:
        return "genesis_authority_root"
    kind = _kind(node)
    tier = _tier(node)
    canonicality_tier = node.get("canonicality_tier")
    if (
        node_id == "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
        or (node_id.startswith("artifact:") and canonicality_tier == "fix38_candidate_overlay")
    ):
        return "source_tree_overlay"
    if node_id.startswith("artifact:") and kind == "repo_manifest_root":
        return "material_manifest_root"
    if node_id.startswith("artifact:") and kind == "repo_material_root":
        return "material_partition_root"
    if node_id.startswith("artifact:") and kind == "package_membership_manifest_artifact":
        return "package_material_root"
    if node_id.startswith("artifact:") and tier in {
        "generated_evidence_root",
        "genesis_private_root",
        "public_release_candidate_root",
    }:
        return "material_partition_root"
    return _prefix(node_id)


def _authority_class(node_id: str, node: dict[str, Any]) -> str:
    group = _visual_group(node_id, node)
    if group == "genesis_authority_root":
        return "genesis_authority_root"
    if group == "source_tree_overlay":
        return "candidate_overlay_not_canonical"
    if group in {"material_manifest_root", "material_partition_root", "package_material_root"}:
        status = node.get("authority_status") or node.get("signature_status") or "support_material_root"
        return str(status)
    value = node.get("authority_status") or node.get("canonicality_tier") or node.get("tier")
    return str(value) if isinstance(value, str) and value else ""


def _node_size(node_id: str, node: dict[str, Any]) -> int:
    group = _visual_group(node_id, node)
    if group == "genesis_authority_root":
        return 20
    if group == "truth_primitive":
        return 12
    if group in {"policy", "artifact", "genesis_agent", "material_manifest_root", "package_material_root"}:
        return 10
    if group == "material_partition_root":
        return 9
    if group == "source_tree_overlay":
        return 7
    if group in {"adr", "cdl", "ceremony"}:
        return 8
    return 4


def _node_color(node_id: str, node: dict[str, Any]) -> str:
    return PREFIX_COLORS.get(_visual_group(node_id, node), PREFIX_COLORS["other"])


def _is_private_or_generated(node: dict[str, Any]) -> bool:
    return _tier(node) in PRIVATE_GENERATED_TIERS


def _is_core_authority(node_id: str, node: dict[str, Any]) -> bool:
    return _prefix(node_id) in AUTHORITY_PREFIXES and (_tier(node) == "genesis_core" or node_id == NODE0)


def _is_test_node(node_id: str, node: dict[str, Any]) -> bool:
    lowered_id = node_id.lower()
    kind = _kind(node).lower()
    label = str(node.get("label", "")).lower()
    source_path = str(node.get("source_path", "")).lower()
    return (
        ("test" in kind)
        or (node_id.startswith("repo:file:") and "test" in lowered_id)
        or "/tests/" in source_path
        or source_path.startswith("tests/")
        or "/tests/" in label
        or label.startswith("tests/")
    )


def _select_node_ids(view: str, nodes_by_id: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> set[str]:
    if view == "all-local":
        return set(nodes_by_id)
    if view == "public-material":
        return {node_id for node_id, node in nodes_by_id.items() if not _is_private_or_generated(node)}
    if view == "private-local":
        return {node_id for node_id, node in nodes_by_id.items() if _is_private_or_generated(node)}
    if view == "authority-core":
        return {node_id for node_id, node in nodes_by_id.items() if _is_core_authority(node_id, node)}
    if view == "governance":
        selected = {node_id for node_id in nodes_by_id if _prefix(node_id) in AUTHORITY_PREFIXES}
        for edge in edges:
            if _edge_type(edge) not in GOVERNANCE_EDGE_TYPES:
                continue
            source = _source(edge)
            target = _target(edge)
            if source in selected or target in selected:
                if source in nodes_by_id:
                    selected.add(source)
                if target in nodes_by_id:
                    selected.add(target)
        return selected
    if view == "test-registry":
        selected = {
            node_id for node_id, node in nodes_by_id.items() if _is_test_node(node_id=node_id, node=node)
        }
        for edge in edges:
            if _edge_type(edge) not in TEST_EDGE_TYPES:
                continue
            source = _source(edge)
            target = _target(edge)
            if source in selected or target in selected:
                if source in nodes_by_id:
                    selected.add(source)
                if target in nodes_by_id:
                    selected.add(target)
        return selected
    raise ValueError(f"fix42_unknown_view:{view}")


def _edge_type_allowed(view: str, edge_type: str) -> bool:
    if view == "governance":
        return edge_type in GOVERNANCE_EDGE_TYPES
    if view == "test-registry":
        return edge_type in TEST_EDGE_TYPES
    return True


def build_view(
    *,
    view: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    digest_manifest: dict[str, Any],
    lmdb_root: Path,
    omit_export_time: bool,
) -> dict[str, Any]:
    nodes_by_id = {_node_id(node): node for node in nodes}
    selected_ids = _select_node_ids(view=view, nodes_by_id=nodes_by_id, edges=edges)
    lmdb_out_degree: dict[str, int] = {}
    lmdb_in_degree: dict[str, int] = {}
    directed_adj: dict[str, list[str]] = {node_id: [] for node_id in nodes_by_id}
    for edge in edges:
        source = _source(edge)
        target = _target(edge)
        if source in nodes_by_id:
            lmdb_out_degree[source] = lmdb_out_degree.get(source, 0) + 1
            directed_adj.setdefault(source, []).append(target)
        if target in nodes_by_id:
            lmdb_in_degree[target] = lmdb_in_degree.get(target, 0) + 1

    directed_hop: dict[str, int] = {}
    if NODE0 in nodes_by_id:
        directed_hop[NODE0] = 0
        queue: deque[str] = deque([NODE0])
        while queue:
            current = queue.popleft()
            for neighbor in directed_adj.get(current, []):
                if neighbor in nodes_by_id and neighbor not in directed_hop:
                    directed_hop[neighbor] = directed_hop[current] + 1
                    queue.append(neighbor)

    view_nodes = [
        {
            "authority_class": _authority_class(node_id, node),
            "color": _node_color(node_id, node),
            "degree_lmdb_in": lmdb_in_degree.get(node_id, 0),
            "degree_lmdb_out": lmdb_out_degree.get(node_id, 0),
            "degree_lmdb_total": lmdb_in_degree.get(node_id, 0) + lmdb_out_degree.get(node_id, 0),
            "directed_hop_from_root": directed_hop.get(node_id),
            "group": _visual_group(node_id, node),
            "id": node_id,
            "kind": _kind(node),
            "label": _label(node_id, node),
            "prefix": _prefix(node_id),
            "projection": _projection(node),
            "size": _node_size(node_id, node),
            "status": _status(node),
            "tier": _tier(node),
            "visual_group": _visual_group(node_id, node),
        }
        for node_id, node in sorted(nodes_by_id.items())
        if node_id in selected_ids
    ]

    view_edges = []
    for edge in edges:
        source = _source(edge)
        target = _target(edge)
        edge_type = _edge_type(edge)
        if source not in selected_ids or target not in selected_ids:
            continue
        if not _edge_type_allowed(view, edge_type):
            continue
        view_edges.append(
            {
                "color": EDGE_COLORS.get(edge_type, "#666666"),
                "source": source,
                "target": target,
                "type": edge_type,
            }
        )
    view_edges.sort(key=lambda item: (item["source"], item["target"], item["type"]))

    metadata: dict[str, Any] = {
        "edge_count": len(view_edges),
        "filters_applied": _filters_for_view(view),
        "lmdb_digest_sha256": _manifest_digest_sha256(digest_manifest),
        "lmdb_root": str(lmdb_root.relative_to(REPO_ROOT) if lmdb_root.is_absolute() else lmdb_root),
        "node_count": len(view_nodes),
        "source_candidate_path": _manifest_source_path(digest_manifest),
        "source_candidate_sha256": _manifest_source_sha256(digest_manifest),
        "view": view,
        "viz_metadata_purpose": VIZ_METADATA_PURPOSE,
    }
    if not omit_export_time:
        metadata["export_time_utc"] = datetime.now(UTC).isoformat(timespec="seconds")

    return {"edges": view_edges, "metadata": metadata, "nodes": view_nodes}


def _filters_for_view(view: str) -> list[str]:
    if view == "all-local":
        return ["all_nodes_including_private_and_generated", "all_edge_types"]
    if view == "public-material":
        return ["exclude_private_and_generated_tiers", "all_edge_types"]
    if view == "private-local":
        return ["only_private_and_generated_tiers", "all_edge_types"]
    if view == "governance":
        return ["authority_prefixes_plus_direct_governance_neighbors", "governance_edge_types"]
    if view == "authority-core":
        return ["authority_prefixes_only", "edges_between_authority_nodes"]
    if view == "test-registry":
        return ["test_nodes_plus_direct_test_edge_targets", "test_edge_types"]
    raise ValueError(f"fix42_unknown_view:{view}")


def _write_report(
    *,
    output_dir: Path,
    exported: dict[str, Path],
    digest_manifest: dict[str, Any],
) -> dict[str, Any]:
    view_digests = {}
    for view, path in sorted(exported.items()):
        payload = json.loads(path.read_text(encoding="utf-8"))
        view_digests[view] = {
            "edge_count": payload["metadata"]["edge_count"],
            "node_count": payload["metadata"]["node_count"],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    report = {
        "lmdb_digest_sha256": _manifest_digest_sha256(digest_manifest),
        "non_claims": [
            "View metadata proves input identity only; it is not a signing proof, authority trace, or Genesis-rootedness proof.",
            "View JSON files are local derived artifacts; only this digest report is committed.",
            "No graph mutation, signing, or public activation occurred.",
        ],
        "phase": "1545p-Fix42",
        "source_candidate_sha256": _manifest_source_sha256(digest_manifest),
        "view_digests": view_digests,
        "views_exported": list(VIEWS),
    }
    _atomic_write_json(output_dir / "fix42_export_report.json", report)
    return report


def export_views(
    *,
    lmdb_root: Path,
    digest_manifest_path: Path,
    output_dir: Path,
    view: str,
    omit_export_time: bool,
) -> dict[str, Path]:
    digest_manifest = _load_digest_manifest(digest_manifest_path)
    views = VIEWS if view == "all" else (view,)

    store = GenesisAtlasCandidateStore(lmdb_root)
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
    finally:
        store.close()

    exported = {}
    for view_name in views:
        payload = build_view(
            view=view_name,
            nodes=nodes,
            edges=edges,
            digest_manifest=digest_manifest,
            lmdb_root=lmdb_root,
            omit_export_time=omit_export_time,
        )
        output_path = output_dir / f"graph_view_{view_name}.json"
        _atomic_write_json(output_path, payload)
        exported[view_name] = output_path

    if view == "all":
        _write_report(output_dir=output_dir, exported=exported, digest_manifest=digest_manifest)

    return exported


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Genesis Atlas LMDB view-model JSON for graph visualization.")
    parser.add_argument("--view", choices=("all", *VIEWS), default="all")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--lmdb-root", type=Path, default=DEFAULT_LMDB_ROOT)
    parser.add_argument("--digest-manifest", type=Path, default=DEFAULT_DIGEST_MANIFEST)
    parser.add_argument("--omit-export-time", action="store_true")
    args = parser.parse_args()

    exported = export_views(
        lmdb_root=args.lmdb_root,
        digest_manifest_path=args.digest_manifest,
        output_dir=args.output_dir,
        view=args.view,
        omit_export_time=args.omit_export_time,
    )
    for view_name, path in sorted(exported.items()):
        print(f"{view_name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
