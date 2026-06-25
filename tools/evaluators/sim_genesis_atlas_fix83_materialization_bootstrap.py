# SPDX-License-Identifier: AGPL-3.0-only
"""Fix83 public-RC materialization profile LMDB synchronization.

PUBLIC_RC_EXCLUDE: fix83_materialization_bootstrap_lmdb_sync
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance for the
pre-RC materialization bootstrap profile. This does not sign Genesis material,
activate public RC, publish a graph, mint ECU, or settle ILC.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping

from ilc_core.distribution.materialization import (
    sha256_file,
    write_json_atomic,
)
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    deterministic_edge_id,
    repo_file_ref_id,
)


PHASE = "1545p-Fix83"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LMDB = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
DEFAULT_PROFILE = REPO_ROOT / "docs/specs/ilc_public_rc_package_profile_v0.1.json"
DEFAULT_REPORT = REPO_ROOT / "docs/specs/ilc_fix83_materialization_bootstrap_lmdb_sync_v0.1.json"


def _candidate_id(node: Mapping[str, Any]) -> str:
    value = node.get("candidate_id") or node.get("node_id") or node.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("node_missing_candidate_id")
    return value


def _edge_source(edge: Mapping[str, Any]) -> str:
    return str(edge.get("source") or edge.get("src") or "")


def _edge_target(edge: Mapping[str, Any]) -> str:
    return str(edge.get("target") or edge.get("tgt") or "")


def _edge_type(edge: Mapping[str, Any]) -> str:
    return str(edge.get("edge_type") or edge.get("type") or "")


def _path_slug(repo_path: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", repo_path.lower()).strip("_")


def _repo_file_id(repo_path: str, source_sha256: str) -> str:
    return f"repo:file:{source_sha256[:16]}:{_path_slug(repo_path)}"


def _repo_file_node_kind(repo_path: str, fallback: str) -> str:
    path = Path(repo_path)
    if repo_path.startswith("ilc_core/") and path.suffix == ".py":
        return "runtime_source_file_node"
    if repo_path.startswith("tests/") and path.suffix == ".py":
        return "test_evidence_node"
    if repo_path.startswith("tools/") and path.suffix == ".py":
        return "tooling_source_file_node"
    if repo_path.startswith("docs/adr/") and path.suffix == ".md":
        return "adr_document_node"
    if repo_path.startswith("docs/") and path.suffix == ".md":
        return "spec_document_node"
    if repo_path.startswith("docs/") and path.suffix == ".json":
        return "spec_data_node"
    return fallback or "repo_material_node"


def _file_ref_node(row: Mapping[str, Any], *, source_sha256: str, size_bytes: int) -> dict[str, Any]:
    source_path = str(row["source_path"])
    return {
        "annotation_method": "fix83_materialization_profile_lmdb_sync",
        "annotation_phase": f"phase_{PHASE.lower().replace('-', '_')}",
        "candidate_id": repo_file_ref_id(source_path),
        "candidate_status": "fix83_public_rc_profile_file_ref_registered",
        "content_node_id": _repo_file_id(source_path, source_sha256),
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": "support_only",
        "graph_projection": row.get("graph_projection", "public_protocol_graph"),
        "label": source_path,
        "node_kind": row.get("node_kind", _repo_file_node_kind(source_path, "")),
        "package_membership": True,
        "profile_name": "ilc-public-rc",
        "size_bytes": size_bytes,
        "source_identity_status": "content_addressed_by_fix83_materialization_profile",
        "source_path": source_path,
        "source_sha256": source_sha256,
        "tier": "support_candidate",
    }


def _repo_file_node(row: Mapping[str, Any], *, source_sha256: str, size_bytes: int) -> dict[str, Any]:
    source_path = str(row["source_path"])
    return {
        "annotation_method": "fix83_materialization_profile_content_addressing",
        "annotation_phase": f"phase_{PHASE.lower().replace('-', '_')}",
        "candidate_id": _repo_file_id(source_path, source_sha256),
        "candidate_status": "fix83_public_rc_profile_content_addressed_repo_file",
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": "support_only",
        "graph_projection": row.get("graph_projection", "public_protocol_graph"),
        "label": source_path,
        "node_kind": _repo_file_node_kind(source_path, str(row.get("node_kind", ""))),
        "package_membership": True,
        "profile_name": "ilc-public-rc",
        "size_bytes": size_bytes,
        "source_identity_status": "content_addressed_by_fix83_materialization_profile",
        "source_path": source_path,
        "source_sha256": source_sha256,
        "tier": "support_candidate",
    }


def _same_source_edge(source: str, target: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix83_materialization_profile_lmdb_sync",
        "annotation_phase": f"phase_{PHASE.lower().replace('-', '_')}",
        "candidate_status": "fix83_public_rc_profile_same_source",
        "edge_id": deterministic_edge_id(source, "SAME_SOURCE", target),
        "edge_type": "SAME_SOURCE",
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def sync_profile(*, lmdb_root: Path, profile_path: Path, report_path: Path, dry_run: bool) -> dict[str, Any]:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict) or not isinstance(profile.get("files"), list):
        raise ValueError("profile_files_missing")

    writer = AtlasLmdbSafeWriter(lmdb_root)
    try:
        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        node_ids = {_candidate_id(node) for node in nodes}

        nodes_to_add: list[dict[str, Any]] = []
        edges_to_add: list[dict[str, Any]] = []
        updates: dict[str, dict[str, Any]] = {}
        stale_same_source: list[tuple[str, str, str]] = []
        changed_profile_rows: list[dict[str, Any]] = []
        missing_profile_paths: list[str] = []

        for row in profile["files"]:
            if not isinstance(row, dict):
                raise ValueError("profile_file_entry_not_object")
            source_path = str(row["source_path"])
            path = REPO_ROOT / source_path
            if not path.is_file():
                missing_profile_paths.append(source_path)
                continue
            source_sha256 = sha256_file(path)
            size_bytes = path.stat().st_size
            file_ref_id = repo_file_ref_id(source_path)
            content_node_id = _repo_file_id(source_path, source_sha256)
            if (
                row.get("source_sha256") != source_sha256
                or row.get("size_bytes") != size_bytes
                or row.get("node_id") != file_ref_id
                or row.get("content_node_id") != content_node_id
            ):
                changed_profile_rows.append(
                    {
                        "content_node_id": content_node_id,
                        "node_id": file_ref_id,
                        "source_path": source_path,
                    }
                )

            file_ref = _file_ref_node(row, source_sha256=source_sha256, size_bytes=size_bytes)
            repo_file = _repo_file_node(row, source_sha256=source_sha256, size_bytes=size_bytes)
            if file_ref_id not in node_ids:
                nodes_to_add.append(file_ref)
                node_ids.add(file_ref_id)
            else:
                updates[file_ref_id] = {
                    "content_node_id": content_node_id,
                    "package_membership": True,
                    "profile_name": "ilc-public-rc",
                    "size_bytes": size_bytes,
                    "source_identity_status": "content_addressed_by_fix83_materialization_profile",
                    "source_path": source_path,
                    "source_sha256": source_sha256,
                }
            if content_node_id not in node_ids:
                nodes_to_add.append(repo_file)
                node_ids.add(content_node_id)
            edges_to_add.append(_same_source_edge(file_ref_id, content_node_id))

        desired_same_source = {
            (edge["source"], edge["target"]) for edge in edges_to_add
        }
        desired_sources = {source for source, _target in desired_same_source}
        for edge in edges:
            if _edge_type(edge) != "SAME_SOURCE":
                continue
            source = _edge_source(edge)
            target = _edge_target(edge)
            if source in desired_sources and (source, target) not in desired_same_source:
                stale_same_source.append((source, "SAME_SOURCE", target))

        removal_dry = writer.remove_edges_by_semantic(
            stale_same_source,
            phase=f"{PHASE}:profile_stale_same_source",
            dry_run=True,
            metadata={"operation": "fix83_remove_stale_same_source_edges"},
        )
        removal_live = {}
        if stale_same_source and not dry_run:
            removal_live = writer.remove_edges_by_semantic(
                stale_same_source,
                phase=f"{PHASE}:profile_stale_same_source",
                dry_run=False,
                metadata={"operation": "fix83_remove_stale_same_source_edges"},
            )

        update_dry = writer.update_node_fields(
            updates,
            phase=f"{PHASE}:profile_file_ref_identity_refresh",
            dry_run=True,
            metadata={"operation": "fix83_profile_file_ref_identity_refresh"},
        )
        update_live = {}
        if updates and not dry_run:
            update_live = writer.update_node_fields(
                updates,
                phase=f"{PHASE}:profile_file_ref_identity_refresh",
                dry_run=False,
                metadata={"operation": "fix83_profile_file_ref_identity_refresh"},
            )

        plan = AtlasLmdbWritePlan(
            nodes_to_add=nodes_to_add,
            edges_to_add=edges_to_add,
            metadata={"operation": "fix83_materialization_profile_lmdb_sync"},
            phase=f"{PHASE}:profile_lmdb_sync",
            dry_run=dry_run,
        )
        apply_receipt = writer.apply_plan(plan)
        final = writer.inspect()
    finally:
        writer.close()

    report = {
        "changed_profile_row_count": len(changed_profile_rows),
        "changed_profile_rows": changed_profile_rows,
        "dry_run": dry_run,
        "edge_addition_receipt": apply_receipt,
        "file_ref_update_receipt": {"dry_run": update_dry, "live": update_live},
        "final_lmdb_counts": {
            "dangling": final["dangling_edge_count"],
            "edges": final["edge_count"],
            "missing_edge_id": final["edge_id_debt_count"],
            "nodes": final["node_count"],
        },
        "missing_profile_path_count": len(missing_profile_paths),
        "missing_profile_paths": missing_profile_paths,
        "phase": PHASE,
        "profile_file_count": len(profile["files"]),
        "profile_path": str(profile_path.relative_to(REPO_ROOT)),
        "stale_same_source_removal_receipt": {"dry_run": removal_dry, "live": removal_live},
        "status": "PASS"
        if not missing_profile_paths
        and final["dangling_edge_count"] == 0
        and final["edge_id_debt_count"] == 0
        else "FAIL",
    }
    write_json_atomic(report_path, report, indent=2)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lmdb", default=str(DEFAULT_LMDB))
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    report = sync_profile(
        lmdb_root=Path(args.lmdb),
        profile_path=Path(args.profile),
        report_path=Path(args.report),
        dry_run=bool(args.dry_run),
    )
    print(json.dumps({"status": report["status"], "final_lmdb_counts": report["final_lmdb_counts"]}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":  # pragma: no cover - CLI wrapper
    raise SystemExit(main())
