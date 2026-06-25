# SPDX-License-Identifier: AGPL-3.0-only
"""Fix82 build/package/content-hash closure evaluator.

PUBLIC_RC_EXCLUDE: fix82_build_package_closure_local_maintenance
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB repair and build metadata
closure. No Genesis signing, public RC activation, public serving, ECU minting,
or settlement.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from ilc_core.distribution.genesis_package_manifest import (
    GENESIS_PACKAGE_ARTIFACT_ID,
    build_genesis_package_manifest,
)
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    repo_file_ref_id,
    write_json_atomic,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "phase_1545p_fix82"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
AUDIT_PATH = REPO_ROOT / "docs/specs/ilc_fix76_build_critical_file_audit_v0.1.json"
FIX65_MANIFEST_PATH = REPO_ROOT / "docs/specs/ilc_fix65_package_membership_manifest_v0.1.json"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix82_build_package_closure_v0.1.json"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix82_build_package_closure_walkthrough.md"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix82_g10_build_package_closure.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix82_build_package_closure.py"

INPUT_TOKENS = (
    "fix81_complete",
    "fix81_p10_tls_hardening_complete",
    "fix80_complete",
    "fix79_complete",
)

DEPENDENCY_DECLARATIONS = {
    "ilc_core/analysis/embedding_pipeline.py": ["torch>=2.0.0", "transformers>=4.30.0"],
    "ilc_core/analysis/laplacian_analytics.py": ["scipy>=1.11.0"],
    "ilc_core/analysis/spectral_trajectory.py": ["scipy>=1.11.0"],
    "ilc_core/cli/sidecar_cli.py": ["ilc-graph-viz>=0.1.0"],
    "ilc_core/config.py": ["PyYAML>=6.0.0"],
    "ilc_core/hardware.py": ["PyYAML>=6.0.0"],
    "ilc_core/ledger/backend.py": ["typing-extensions>=4.8.0"],
    "ilc_core/mining/benchmark.py": ["torch>=2.0.0"],
    "ilc_core/network/d2d/bootstrap_fetch_runtime.py": ["liboqs-python>=0.15.0"],
}

MANIFESTS_REQUIRING_SIGNED_FALSE = (
    "docs/specs/canon_bundle_key_registry_bundle_v0.1.json",
    "docs/specs/ilc_fix65_package_membership_manifest_v0.1.json",
    "docs/specs/ilc_release_artifact_manifest_instance_rehearsal_1320_v0.1.json",
    "docs/specs/ilc_release_artifact_production_gate_1334_v0.1.json",
)


def _candidate_id(row: Mapping[str, Any]) -> str:
    value = row.get("candidate_id") or row.get("node_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix82_candidate_id_missing")
    return value


def _edge_source(row: Mapping[str, Any]) -> str:
    value = row.get("source") or row.get("src")
    if not isinstance(value, str) or not value:
        raise ValueError("fix82_edge_source_missing")
    return value


def _edge_target(row: Mapping[str, Any]) -> str:
    value = row.get("target") or row.get("tgt")
    if not isinstance(value, str) or not value:
        raise ValueError("fix82_edge_target_missing")
    return value


def _edge_type(row: Mapping[str, Any]) -> str:
    value = row.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix82_edge_type_missing")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_slug(repo_path: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", repo_path.lower()).strip("_")


def _repo_file_id(repo_path: str, source_sha256: str) -> str:
    return f"repo:file:{source_sha256[:16]}:{_path_slug(repo_path)}"


def _node_kind(repo_path: str) -> str:
    path = Path(repo_path)
    if repo_path.startswith("ilc_core/") and path.suffix == ".py":
        return "runtime_source_file_node"
    if repo_path.startswith("tests/") and path.suffix == ".py":
        return "test_evidence_node"
    if repo_path.startswith("tools/") and path.suffix == ".py":
        return "tooling_source_file_node"
    if repo_path.startswith("docs/adr/") and path.suffix == ".md":
        return "adr_document_node"
    if repo_path.startswith("docs/specs/") and path.suffix == ".json":
        return "spec_json_artifact_node"
    if repo_path.startswith("docs/specs/") and path.suffix == ".md":
        return "spec_document_node"
    if repo_path.startswith("docs/phases/"):
        return "phase_walkthrough_node"
    return "repo_material_node"


def _file_ref_node(repo_path: str, source_sha256: str, size_bytes: int) -> dict[str, Any]:
    return {
        "annotation_method": "fix82_build_package_closure",
        "annotation_phase": PHASE,
        "candidate_id": repo_file_ref_id(repo_path),
        "candidate_status": "fix82_content_hash_identity_node",
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": "support_only_content_identity",
        "graph_projection": "support_candidate_graph",
        "label": repo_path,
        "node_kind": _node_kind(repo_path),
        "size_bytes": size_bytes,
        "source_identity_status": "content_addressed_by_fix82",
        "source_path": repo_path,
        "source_sha256": source_sha256,
        "tier": "support_candidate",
    }


def _repo_file_node(
    repo_path: str,
    source_sha256: str,
    size_bytes: int,
    *,
    public_protocol: bool,
) -> dict[str, Any]:
    return {
        "annotation_method": "fix82_build_package_closure",
        "annotation_phase": PHASE,
        "candidate_id": _repo_file_id(repo_path, source_sha256),
        "candidate_status": (
            "fix82_public_protocol_current_package_member"
            if public_protocol
            else "fix82_content_addressed_repo_file_counterpart"
        ),
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": (
            "package_membership_content_hash_closure"
            if public_protocol
            else "support_only_content_identity"
        ),
        "graph_projection": "public_protocol_graph" if public_protocol else "support_candidate_graph",
        "label": repo_path,
        "node_kind": _node_kind(repo_path),
        "size_bytes": size_bytes,
        "source_identity_status": "content_addressed_by_fix82",
        "source_path": repo_path,
        "source_sha256": source_sha256,
        "tier": "support_candidate",
    }


def _edge(source: str, edge_type: str, target: str, evidence: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix82_build_package_closure",
        "annotation_phase": PHASE,
        "candidate_status": "fix82_build_package_closure_edge",
        "confidence": "high",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": evidence,
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def _load_audit_rows() -> list[dict[str, Any]]:
    payload = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    rows = payload.get("files")
    if not isinstance(rows, list):
        raise ValueError("fix82_audit_files_missing")
    return [dict(row) for row in rows]


def _validate_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    missing = [token for token in INPUT_TOKENS if token not in status]
    if missing:
        raise ValueError(f"fix82_missing_input_tokens:{missing}")


def _indexes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    node_by_id = {_candidate_id(node): dict(node) for node in nodes}
    repo_files_by_path: dict[str, list[dict[str, Any]]] = {}
    file_refs_by_path: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        node_id = _candidate_id(node)
        path = node.get("source_path")
        if isinstance(path, str) and path:
            if node_id.startswith("repo:file:") and not node_id.startswith("repo:file_ref:"):
                repo_files_by_path.setdefault(path, []).append(dict(node))
            if node_id.startswith("repo:file_ref:"):
                file_refs_by_path.setdefault(path, []).append(dict(node))
    edge_semantics = {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}
    return {
        "edge_semantics": edge_semantics,
        "file_refs_by_path": file_refs_by_path,
        "node_by_id": node_by_id,
        "repo_files_by_path": repo_files_by_path,
    }


def _current_file(repo_path: str) -> tuple[str, int] | None:
    path = REPO_ROOT / repo_path
    if not path.is_file():
        return None
    return _sha256(path), path.stat().st_size


def _ensure_current_repo_file(
    *,
    repo_path: str,
    public_protocol: bool,
    indexes: dict[str, Any],
    nodes_to_add: dict[str, dict[str, Any]],
    node_updates: dict[str, dict[str, Any]],
    edges_to_add: dict[tuple[str, str, str], dict[str, Any]],
    removals: set[tuple[str, str, str]],
) -> dict[str, Any]:
    current = _current_file(repo_path)
    if current is None:
        return {"disposition": "path_not_resolved", "source_path": repo_path}
    source_sha256, size_bytes = current
    current_id = _repo_file_id(repo_path, source_sha256)
    current_node = indexes["node_by_id"].get(current_id) or nodes_to_add.get(current_id)
    if current_node is None:
        current_node = _repo_file_node(
            repo_path,
            source_sha256,
            size_bytes,
            public_protocol=public_protocol,
        )
        nodes_to_add[current_id] = current_node
        indexes["node_by_id"][current_id] = current_node
        indexes["repo_files_by_path"].setdefault(repo_path, []).append(current_node)
        created_current = True
    else:
        patch: dict[str, Any] = {
            "size_bytes": size_bytes,
            "source_identity_status": "content_addressed_by_fix82",
            "source_path": repo_path,
            "source_sha256": source_sha256,
        }
        if public_protocol and current_node.get("graph_projection") != "public_protocol_graph":
            patch.update(
                {
                    "candidate_status": "fix82_public_protocol_current_package_member",
                    "graph_delta": "package_membership_content_hash_closure",
                    "graph_projection": "public_protocol_graph",
                }
            )
        if any(current_node.get(key) != value for key, value in patch.items()):
            node_updates[current_id] = patch
            indexes["node_by_id"][current_id] = {**current_node, **patch}
        created_current = False

    superseded: list[str] = []
    for node in sorted(indexes["repo_files_by_path"].get(repo_path, []), key=_candidate_id):
        node_id = _candidate_id(node)
        if node_id == current_id:
            continue
        if node.get("graph_projection") == "public_protocol_graph":
            node_updates[node_id] = {
                "candidate_status": "fix82_superseded_public_protocol_source_hash",
                "graph_delta": "support_only_superseded_source_hash",
                "graph_projection": "support_candidate_graph",
                "source_identity_status": "superseded_by_current_source_hash_at_fix82",
                "superseded_by": current_id,
                "superseded_source_sha256": source_sha256,
            }
            superseded.append(node_id)
            edge = _edge(
                current_id,
                "DERIVED_FROM",
                node_id,
                f"{repo_path}:current_sha256:{source_sha256}:supersedes_stale_package_member",
            )
            semantic = (current_id, "DERIVED_FROM", node_id)
            if semantic not in indexes["edge_semantics"]:
                edges_to_add[semantic] = edge
                indexes["edge_semantics"].add(semantic)
            removals.add((GENESIS_PACKAGE_ARTIFACT_ID, "CONTAINS_FILE", node_id))

    if public_protocol:
        semantic = (GENESIS_PACKAGE_ARTIFACT_ID, "CONTAINS_FILE", current_id)
        if semantic not in indexes["edge_semantics"]:
            edges_to_add[semantic] = _edge(
                GENESIS_PACKAGE_ARTIFACT_ID,
                "CONTAINS_FILE",
                current_id,
                f"{repo_path}:fix82_public_protocol_package_member",
            )
            indexes["edge_semantics"].add(semantic)

    return {
        "created_current_node": created_current,
        "current_candidate_id": current_id,
        "current_sha256": source_sha256,
        "disposition": "current_repo_file_ready",
        "size_bytes": size_bytes,
        "source_path": repo_path,
        "superseded_public_nodes": superseded,
    }


def _ensure_file_ref(
    *,
    repo_path: str,
    indexes: dict[str, Any],
    nodes_to_add: dict[str, dict[str, Any]],
    node_updates: dict[str, dict[str, Any]],
    edges_to_add: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    current = _current_file(repo_path)
    if current is None:
        return {"disposition": "path_not_resolved", "source_path": repo_path}
    source_sha256, size_bytes = current
    ref_id = repo_file_ref_id(repo_path)
    repo_result = _ensure_current_repo_file(
        repo_path=repo_path,
        public_protocol=False,
        indexes=indexes,
        nodes_to_add=nodes_to_add,
        node_updates=node_updates,
        edges_to_add=edges_to_add,
        removals=set(),
    )
    target_id = repo_result["current_candidate_id"]
    existing = indexes["node_by_id"].get(ref_id)
    if existing is None:
        ref_node = _file_ref_node(repo_path, source_sha256, size_bytes)
        nodes_to_add[ref_id] = ref_node
        indexes["node_by_id"][ref_id] = ref_node
        created_ref = True
    else:
        patch = {
            "size_bytes": size_bytes,
            "source_identity_status": "content_addressed_by_fix82",
            "source_path": repo_path,
            "source_sha256": source_sha256,
        }
        if any(existing.get(key) != value for key, value in patch.items()):
            node_updates[ref_id] = patch
            indexes["node_by_id"][ref_id] = {**existing, **patch}
        created_ref = False
    semantic = (ref_id, "SAME_SOURCE", target_id)
    if semantic not in indexes["edge_semantics"]:
        edges_to_add[semantic] = _edge(
            ref_id,
            "SAME_SOURCE",
            target_id,
            f"{repo_path}:sha256:{source_sha256}",
        )
        indexes["edge_semantics"].add(semantic)
    return {
        "created_file_ref_node": created_ref,
        "current_repo_file": target_id,
        "disposition": "content_hash_resolved",
        "file_ref_id": ref_id,
        "source_path": repo_path,
        "source_sha256": source_sha256,
    }


def _live_public_protocol_hash_mismatches(nodes: list[dict[str, Any]]) -> list[str]:
    mismatches: set[str] = set()
    for node in nodes:
        node_id = _candidate_id(node)
        if not node_id.startswith("repo:file:") or node_id.startswith("repo:file_ref:"):
            continue
        if node.get("graph_projection") != "public_protocol_graph":
            continue
        repo_path = node.get("source_path")
        recorded = node.get("source_sha256")
        if not isinstance(repo_path, str) or not repo_path:
            continue
        if not isinstance(recorded, str) or len(recorded) != 64:
            continue
        current = _current_file(repo_path)
        if current is None:
            continue
        current_sha256, _size = current
        if current_sha256 != recorded:
            mismatches.add(repo_path)
    return sorted(mismatches)


def _test_reference_for(repo_path: str, indexes: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        ["rg", "-l", "--fixed-strings", repo_path, "tests"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or "fix82_rg_failed")
    paths = sorted(line.strip() for line in proc.stdout.splitlines() if line.strip())
    if not paths:
        return {"disposition": "no_test_exists", "source_path": repo_path}
    source_ref_id = repo_file_ref_id(repo_path)
    if source_ref_id not in indexes["node_by_id"]:
        return {
            "candidate_test_paths": paths,
            "disposition": "source_file_ref_missing_after_hash_step",
            "source_path": repo_path,
        }
    for test_path in paths:
        by_path = indexes["file_refs_by_path"].get(test_path, [])
        candidates = [_candidate_id(node) for node in by_path]
        if not candidates:
            candidate = repo_file_ref_id(test_path)
            if candidate in indexes["node_by_id"]:
                candidates = [candidate]
        if candidates:
            test_ref_id = sorted(candidates)[0]
            return {
                "disposition": "test_relation_ready",
                "source_file_ref_id": source_ref_id,
                "source_path": repo_path,
                "test_file_ref_id": test_ref_id,
                "test_path": test_path,
            }
    return {
        "candidate_test_paths": paths,
        "disposition": "no_test_file_ref_node_exists",
        "source_path": repo_path,
    }


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=REPORT_PATH.relative_to(REPO_ROOT),
            node_kind="gap_report",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "policy:public_path_still_blocked_phase_1545p"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix82"),),
        ),
        AtlasPhaseFileRegistration(
            path=STATUS_PATH.relative_to(REPO_ROOT),
            node_kind="phase_status_ledger",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix82"),),
            skip_carries_forward=True,
        ),
        AtlasPhaseFileRegistration(
            path=PROMPT_PATH.relative_to(REPO_ROOT),
            node_kind="phase_prompt",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix82"),),
        ),
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="evaluator_tool_node",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix82"),),
        ),
        AtlasPhaseFileRegistration(
            path=FIX65_MANIFEST_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix82"),),
        ),
    )
    dry = writer.register_phase_files(PHASE, files, dry_run=True)
    live = writer.register_phase_files(PHASE, files, dry_run=False)
    return {"dry_run": dry, "live": live}


def _sync_contains_file_edges(
    writer: AtlasLmdbSafeWriter,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    desired_targets = {member["candidate_id"] for member in manifest["members"]}
    current_edges = writer.store.iter_edges()
    current_targets = {
        _edge_target(edge)
        for edge in current_edges
        if _edge_source(edge) == GENESIS_PACKAGE_ARTIFACT_ID
        and _edge_type(edge) == "CONTAINS_FILE"
    }
    extra_targets = sorted(current_targets - desired_targets)
    missing_targets = sorted(desired_targets - current_targets)
    extra_semantics = {
        (GENESIS_PACKAGE_ARTIFACT_ID, "CONTAINS_FILE", target)
        for target in extra_targets
    }
    remove_dry = writer.remove_edges_by_semantic(
        extra_semantics,
        phase=f"{PHASE}:manifest_contains_file_sync",
        dry_run=True,
        metadata={"operation": "fix82_manifest_contains_file_sync_remove_extra"},
    )
    remove_live = writer.remove_edges_by_semantic(
        extra_semantics,
        phase=f"{PHASE}:manifest_contains_file_sync",
        dry_run=False,
        metadata={"operation": "fix82_manifest_contains_file_sync_remove_extra"},
    )
    if remove_live.get("status") != "PASS":
        raise ValueError(f"fix82_manifest_contains_sync_remove_failed:{remove_live}")
    edges_to_add = [
        _edge(
            GENESIS_PACKAGE_ARTIFACT_ID,
            "CONTAINS_FILE",
            target,
            "fix82_manifest_contains_file_sync",
        )
        for target in missing_targets
    ]
    add_dry = writer.apply_plan(
        AtlasLmdbWritePlan(
            edges_to_add=edges_to_add,
            metadata={"operation": "fix82_manifest_contains_file_sync_add_missing"},
            phase=f"{PHASE}:manifest_contains_file_sync",
            dry_run=True,
        )
    )
    add_live = writer.apply_plan(
        AtlasLmdbWritePlan(
            edges_to_add=edges_to_add,
            metadata={"operation": "fix82_manifest_contains_file_sync_add_missing"},
            phase=f"{PHASE}:manifest_contains_file_sync",
            dry_run=False,
        )
    )
    if add_live.get("status") != "PASS" or add_live.get("rejected_edge_count"):
        raise ValueError(f"fix82_manifest_contains_sync_add_failed:{add_live}")
    return {
        "add_dry_run": add_dry,
        "add_live": add_live,
        "extra_removed": len(extra_targets),
        "missing_added": len(missing_targets),
        "remove_dry_run": remove_dry,
        "remove_live": remove_live,
    }


def execute(*, register_only: bool = False) -> dict[str, Any]:
    _validate_tokens()
    rows = _load_audit_rows()
    blocker_counts = {
        "missing_content_hash": sum(1 for row in rows if not row.get("content_hash_present")),
        "missing_dependency_membership": sum(1 for row in rows if not row.get("dependency_membership")),
        "missing_package_membership": sum(1 for row in rows if not row.get("package_membership")),
        "missing_test_relation": sum(1 for row in rows if not row.get("test_relation")),
        "stale_package_member_hash": sum(1 for row in rows if not row.get("package_member_hash_current")),
    }

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        if register_only:
            return {"phase_file_registration": _register_phase_files(writer)}

        pre_inspect = writer.inspect()
        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        indexes = _indexes(nodes, edges)

        nodes_to_add: dict[str, dict[str, Any]] = {}
        node_updates: dict[str, dict[str, Any]] = {}
        edges_to_add: dict[tuple[str, str, str], dict[str, Any]] = {}
        contains_removals: set[tuple[str, str, str]] = set()

        signed_false = []
        for repo_path in MANIFESTS_REQUIRING_SIGNED_FALSE:
            path = REPO_ROOT / repo_path
            payload = json.loads(path.read_text(encoding="utf-8"))
            signed_false.append(
                {
                    "already_present": payload.get("signed") is False,
                    "path": repo_path,
                    "signed_value": payload.get("signed"),
                }
            )

        missing_package_results = []
        for row in sorted((row for row in rows if not row.get("package_membership")), key=lambda item: item["source_path"]):
            result = _ensure_current_repo_file(
                repo_path=row["source_path"],
                public_protocol=True,
                indexes=indexes,
                nodes_to_add=nodes_to_add,
                node_updates=node_updates,
                edges_to_add=edges_to_add,
                removals=contains_removals,
            )
            missing_package_results.append(result)

        stale_package_results = []
        for row in sorted((row for row in rows if not row.get("package_member_hash_current")), key=lambda item: item["source_path"]):
            result = _ensure_current_repo_file(
                repo_path=row["source_path"],
                public_protocol=True,
                indexes=indexes,
                nodes_to_add=nodes_to_add,
                node_updates=node_updates,
                edges_to_add=edges_to_add,
                removals=contains_removals,
            )
            stale_package_results.append(result)

        live_hash_mismatch_results = []
        for repo_path in _live_public_protocol_hash_mismatches(nodes):
            result = _ensure_current_repo_file(
                repo_path=repo_path,
                public_protocol=True,
                indexes=indexes,
                nodes_to_add=nodes_to_add,
                node_updates=node_updates,
                edges_to_add=edges_to_add,
                removals=contains_removals,
            )
            result["source"] = "live_public_protocol_hash_mismatch_scan"
            live_hash_mismatch_results.append(result)

        missing_content_results = []
        for row in sorted((row for row in rows if not row.get("content_hash_present")), key=lambda item: item["source_path"]):
            result = _ensure_file_ref(
                repo_path=row["source_path"],
                indexes=indexes,
                nodes_to_add=nodes_to_add,
                node_updates=node_updates,
                edges_to_add=edges_to_add,
            )
            missing_content_results.append(result)

        test_relation_results = []
        for row in sorted((row for row in rows if not row.get("test_relation")), key=lambda item: item["source_path"]):
            relation = _test_reference_for(row["source_path"], indexes)
            if relation["disposition"] == "test_relation_ready":
                semantic = (
                    relation["test_file_ref_id"],
                    "TESTS",
                    relation["source_file_ref_id"],
                )
                if semantic not in indexes["edge_semantics"]:
                    edges_to_add[semantic] = _edge(
                        relation["test_file_ref_id"],
                        "TESTS",
                        relation["source_file_ref_id"],
                        f"{relation['test_path']} references {row['source_path']}",
                    )
                    indexes["edge_semantics"].add(semantic)
            test_relation_results.append(relation)

        remove_dry = writer.remove_edges_by_semantic(
            contains_removals,
            phase=f"{PHASE}:stale_contains_file_removal",
            dry_run=True,
            metadata={"operation": "fix82_stale_package_contains_file_removal"},
        )
        remove_live = writer.remove_edges_by_semantic(
            contains_removals,
            phase=f"{PHASE}:stale_contains_file_removal",
            dry_run=False,
            metadata={"operation": "fix82_stale_package_contains_file_removal"},
        )
        if remove_live.get("status") != "PASS":
            raise ValueError(f"fix82_contains_removal_failed:{remove_live}")

        plan = AtlasLmdbWritePlan(
            nodes_to_add=sorted(nodes_to_add.values(), key=_candidate_id),
            edges_to_add=[edges_to_add[key] for key in sorted(edges_to_add)],
            metadata={"operation": "fix82_build_package_closure"},
            phase=f"{PHASE}:content_package_test_edges",
            dry_run=True,
        )
        apply_dry = writer.apply_plan(plan)
        apply_live = writer.apply_plan(
            AtlasLmdbWritePlan(
                nodes_to_add=plan.nodes_to_add,
                edges_to_add=plan.edges_to_add,
                metadata=plan.metadata,
                phase=plan.phase,
                dry_run=False,
            )
        )
        if apply_live.get("status") != "PASS" or apply_live.get("rejected_edge_count"):
            raise ValueError(f"fix82_apply_plan_failed:{apply_live}")

        update_dry = writer.update_node_fields(
            node_updates,
            phase=f"{PHASE}:node_field_updates",
            dry_run=True,
            metadata={"operation": "fix82_content_package_node_field_updates"},
        )
        update_live = writer.update_node_fields(
            node_updates,
            phase=f"{PHASE}:node_field_updates",
            dry_run=False,
            metadata={"operation": "fix82_content_package_node_field_updates"},
        )
        if update_live.get("status") != "PASS" or update_live.get("rejected_update_count"):
            raise ValueError(f"fix82_node_updates_failed:{update_live}")

        final_nodes_before_manifest = writer.store.iter_nodes()
        manifest = build_genesis_package_manifest(final_nodes_before_manifest, repo_root=REPO_ROOT)
        FIX65_MANIFEST_PATH.write_text(
            json.dumps(manifest, allow_nan=False, separators=(",", ":"), sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        contains_sync = _sync_contains_file_edges(writer, manifest)
        artifact_update = writer.update_node_fields(
            {
                GENESIS_PACKAGE_ARTIFACT_ID: {
                    "manifest_sha256": manifest["manifest_sha256"],
                    "merkle_root_m0": manifest["merkle_root_m0"],
                    "package_member_count": manifest["member_count"],
                    "signed": False,
                }
            },
            phase=f"{PHASE}:fix65_manifest_artifact_refresh",
            dry_run=False,
            metadata={"operation": "fix82_fix65_manifest_artifact_refresh"},
        )
        if artifact_update.get("status") != "PASS":
            raise ValueError(f"fix82_artifact_update_failed:{artifact_update}")

        post_inspect = writer.inspect()
        report = {
            "blocker_counts_reconfirmed": blocker_counts,
            "contains_file_removals": {
                "count": len(contains_removals),
                "dry_run": remove_dry,
                "live": remove_live,
            },
            "dependency_declarations": DEPENDENCY_DECLARATIONS,
            "edge_additions_by_type": Counter(edge[1] for edge in edges_to_add),
            "fix65_manifest_refresh": {
                "manifest_path": FIX65_MANIFEST_PATH.relative_to(REPO_ROOT).as_posix(),
                "manifest_sha256": manifest["manifest_sha256"],
                "member_count": manifest["member_count"],
                "merkle_root_m0": manifest["merkle_root_m0"],
                "signed": manifest["signed"],
            },
            "fix65_manifest_contains_file_sync": contains_sync,
            "lmdb_counts": {
                "post": post_inspect,
                "pre": pre_inspect,
            },
            "missing_content_hash": missing_content_results,
            "missing_package_membership": missing_package_results,
            "missing_test_relation": test_relation_results,
            "live_public_protocol_hash_mismatches": live_hash_mismatch_results,
            "node_add_count": len(nodes_to_add),
            "node_update_count": len(node_updates),
            "phase": PHASE,
            "safe_writer_receipts": {
                "apply_dry_run": apply_dry,
                "apply_live": apply_live,
                "artifact_update": artifact_update,
                "update_dry_run": update_dry,
                "update_live": update_live,
            },
            "signed_false_annotations": signed_false,
            "stale_package_member_hash": stale_package_results,
            "status": "PASS",
        }
        write_json_atomic(REPORT_PATH, report)
        return report
    finally:
        writer.close()


def main() -> int:
    payload = execute(register_only=False)
    print(json.dumps({"status": payload["status"], "report": REPORT_PATH.as_posix()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
