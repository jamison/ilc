# SPDX-License-Identifier: AGPL-3.0-only
"""Fix64 file_ref content hash resolution for the unsigned Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix64_file_ref_hash_resolution_local_atlas_maintenance
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance. No Genesis
signing, public graph upload, canonical graph promotion, runtime activation,
ECU minting, or ILC settlement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    repo_file_ref_id,
    write_json_atomic,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix64_file_ref_resolution_queue_v0.1.json"
REPORT_PATH = REPO_ROOT / "docs/specs/ilc_fix64_file_ref_resolution_report_v0.1.json"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix64_file_ref_content_hash_resolution_walkthrough.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix64_file_ref_content_hash_resolution.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix64_file_ref_content_hash_resolution.py"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix64_g10_file_ref_content_hash_resolution.md"
GRAPH_VIZ_EXPORT_PATH = REPO_ROOT / "tools/graph_viz_export.py"
PHASE = "1545p-Fix64"
PHASE_TOKEN = "phase_1545p_fix64"
METHOD = "fix64_file_ref_content_hash_resolution"

INPUT_TOKENS = (
    "fix63_complete",
    "fix63a_complete",
    "fix63c_complete",
    "fix63e_complete",
)
OUTPUT_TOKENS = (
    "fix64_tier1_public_protocol_refs_resolved",
    "fix64_tier2_source_path_refs_resolved",
    "fix64_tier3_label_path_refs_resolved",
    "fix64_file_ref_source_sha256_coverage_reported",
    "fix64_complete",
)
TIER1_FILE_REFS = {
    "repo:file_ref:ilc_core_cli_atlas_lmdb_cli_py": "ilc_core/cli/atlas_lmdb_cli.py",
    "repo:file_ref:ilc_core_storage_genesis_atlas_lmdb_writer_py": "ilc_core/storage/genesis_atlas_lmdb_writer.py",
    "repo:file_ref:tests_test_phase_1545p_fix59b_atlas_lmdb_safe_writer_py": "tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py",
    "repo:file_ref:tests_test_phase_1545p_fix59c_atlas_lmdb_read_cli_py": "tests/test_phase_1545p_fix59c_atlas_lmdb_read_cli.py",
    "repo:file_ref:tests_test_phase_1545p_fix59d_atlas_lmdb_write_cli_py": "tests/test_phase_1545p_fix59d_atlas_lmdb_write_cli.py",
    "repo:file_ref:tests_test_phase_1545p_fix59e_atlas_lmdb_write_guard_py": "tests/test_phase_1545p_fix59e_atlas_lmdb_write_guard.py",
}


@dataclass(frozen=True)
class PathIdentity:
    repo_path: str
    sha256: str
    size_bytes: int
    identity_kind: str = "repo_file"


def file_sha256(path: Path, chunk_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix64_node_missing_candidate_id")
    return value


def edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix64_edge_source_missing")


def edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix64_edge_target_missing")


def edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix64_edge_type_missing")
    return value


def edge(
    *,
    source: str,
    edge_type_value: str,
    target: str,
    evidence: str,
    status: str,
) -> dict[str, Any]:
    edge_id = deterministic_edge_id(source, edge_type_value, target)
    return {
        "annotation_method": METHOD,
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": status,
        "confidence": "high",
        "edge_id": edge_id,
        "edge_type": edge_type_value,
        "evidence": evidence,
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def node_id_for_repo_file(repo_path: str, sha256: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", repo_path.lower()).strip("_")
    return f"repo:file:{sha256[:16]}:{slug}"


def node_id_for_identity(identity: PathIdentity) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", identity.repo_path.lower()).strip("_")
    if identity.identity_kind == "repo_directory_manifest":
        return f"repo:dir:{identity.sha256[:16]}:{slug}"
    if identity.identity_kind == "external_file":
        return f"external:file:{identity.sha256[:16]}:{slug}"
    return f"repo:file:{identity.sha256[:16]}:{slug}"


def infer_node_kind(repo_path: str) -> str:
    path = Path(repo_path)
    if repo_path.startswith("ilc_core/") and path.suffix == ".py":
        return "runtime_source_file_node"
    if repo_path.startswith("tests/") and path.suffix == ".py":
        return "test_evidence_node"
    if repo_path.startswith("tools/") and path.suffix == ".py":
        return "tooling_source_file_node"
    if repo_path.startswith("docs/") and path.suffix == ".md":
        return "spec_document_node"
    return "repo_material_node"


def repo_file_node(repo_path: str, identity: PathIdentity) -> dict[str, Any]:
    if identity.identity_kind == "repo_directory_manifest":
        return {
            "annotation_method": METHOD,
            "annotation_phase": PHASE_TOKEN,
            "candidate_id": node_id_for_identity(identity),
            "candidate_status": "fix64_materialized_repo_directory_manifest_counterpart",
            "creator_agent_id": "genesis_agent:01",
            "genesis_attested": False,
            "graph_delta": "support_only",
            "graph_projection": "support_candidate_graph",
            "label": repo_path,
            "node_kind": "repo_directory_manifest_node",
            "size_bytes": identity.size_bytes,
            "source_path": repo_path,
            "source_sha256": identity.sha256,
            "source_identity_status": "directory_manifest_content_addressed_by_fix64",
            "tier": "support_candidate",
        }
    if identity.identity_kind == "external_file":
        return {
            "annotation_method": METHOD,
            "annotation_phase": PHASE_TOKEN,
            "candidate_id": node_id_for_identity(identity),
            "candidate_status": "fix64_materialized_external_file_counterpart",
            "creator_agent_id": "genesis_agent:01",
            "genesis_attested": False,
            "graph_delta": "support_only",
            "graph_projection": "support_candidate_graph",
            "label": repo_path,
            "node_kind": "external_source_file_node",
            "size_bytes": identity.size_bytes,
            "source_path": repo_path,
            "source_sha256": identity.sha256,
            "source_identity_status": "external_path_content_addressed_by_fix64_non_repo",
            "tier": "support_candidate",
        }
    return {
        "annotation_method": METHOD,
        "annotation_phase": PHASE_TOKEN,
        "candidate_id": node_id_for_identity(identity),
        "candidate_status": "fix64_materialized_repo_file_counterpart",
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": repo_path,
        "node_kind": infer_node_kind(repo_path),
        "size_bytes": identity.size_bytes,
        "source_path": repo_path,
        "source_sha256": identity.sha256,
        "tier": "support_candidate",
    }


def normalize_repo_relative_path(raw_path: str) -> str | None:
    if not raw_path:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        resolved = path.resolve()
        try:
            return resolved.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            return None
    normalized = Path(raw_path).as_posix()
    if normalized.startswith("../") or normalized == "..":
        return None
    return normalized


def path_for_file_ref(node: dict[str, Any]) -> str | None:
    for key in ("source_path", "label"):
        value = node.get(key)
        if isinstance(value, str) and value:
            normalized = normalize_repo_relative_path(value)
            if normalized:
                return normalized
            if value.startswith("../") and (REPO_ROOT / value).is_file():
                return Path(value).as_posix()
    return None


def path_identity(repo_path: str) -> PathIdentity | None:
    path = REPO_ROOT / repo_path
    if repo_path.startswith("../") and path.is_file():
        return PathIdentity(
            repo_path=repo_path,
            sha256=file_sha256(path),
            size_bytes=path.stat().st_size,
            identity_kind="external_file",
        )
    if not path.is_file():
        if path.is_dir():
            rows = []
            for child in sorted(item for item in path.rglob("*") if item.is_file()):
                rows.append(
                    {
                        "path": child.relative_to(path).as_posix(),
                        "sha256": file_sha256(child),
                        "size_bytes": child.stat().st_size,
                    }
                )
            payload = canonical_json(rows).encode("utf-8")
            return PathIdentity(
                repo_path=repo_path,
                sha256=hashlib.sha256(payload).hexdigest(),
                size_bytes=len(payload),
                identity_kind="repo_directory_manifest",
            )
        return None
    return PathIdentity(
        repo_path=repo_path,
        sha256=file_sha256(path),
        size_bytes=path.stat().st_size,
        identity_kind="repo_file",
    )


def tier_for_file_ref(node: dict[str, Any]) -> int:
    node_id = candidate_id(node)
    if node_id in TIER1_FILE_REFS:
        return 1
    if isinstance(node.get("source_path"), str) and node.get("source_path"):
        return 2
    return 3


def build_indexes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    node_by_id = {candidate_id(node): dict(node) for node in nodes}
    repo_files_by_path: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        node_id = candidate_id(node)
        if node_id.startswith("repo:file:") and not node_id.startswith("repo:file_ref:"):
            source_path = node.get("source_path")
            if isinstance(source_path, str) and source_path:
                repo_files_by_path.setdefault(source_path, []).append(dict(node))
    same_source_targets: dict[str, list[str]] = {}
    edge_semantics = set()
    for row in edges:
        source = edge_source(row)
        target = edge_target(row)
        kind = edge_type(row)
        edge_semantics.add((source, kind, target))
        if kind == "SAME_SOURCE":
            same_source_targets.setdefault(source, []).append(target)
    return {
        "edge_semantics": edge_semantics,
        "node_by_id": node_by_id,
        "repo_files_by_path": repo_files_by_path,
        "same_source_targets": same_source_targets,
    }


def counterpart_for_path(
    *,
    repo_path: str,
    identity: PathIdentity,
    indexes: dict[str, Any],
    created_nodes: dict[str, dict[str, Any]],
    counterpart_updates: dict[str, dict[str, Any]],
) -> tuple[str | None, str, list[dict[str, Any]], dict[str, Any] | None]:
    if identity.identity_kind != "repo_file":
        new_node = repo_file_node(repo_path, identity)
        new_id = candidate_id(new_node)
        existing = indexes["node_by_id"].get(new_id)
        if existing:
            return new_id, f"existing_{identity.identity_kind}_counterpart", [], None
        created_nodes[new_id] = new_node
        indexes["node_by_id"][new_id] = new_node
        return new_id, f"new_{identity.identity_kind}_counterpart_created", [new_node], None

    repo_files_by_path: dict[str, list[dict[str, Any]]] = indexes["repo_files_by_path"]
    candidates = sorted(repo_files_by_path.get(repo_path, []), key=candidate_id)
    matching = [
        node
        for node in candidates
        if node.get("source_sha256") == identity.sha256
    ]
    if matching:
        return candidate_id(matching[0]), "existing_matching_counterpart", [], None

    missing_hash = [
        node
        for node in candidates
        if not isinstance(node.get("source_sha256"), str) or not node.get("source_sha256")
    ]
    if missing_hash:
        target = candidate_id(missing_hash[0])
        for node in missing_hash:
            counterpart_updates[candidate_id(node)] = {
                "size_bytes": identity.size_bytes,
                "source_path": repo_path,
                "source_sha256": identity.sha256,
                "source_identity_status": "content_addressed_by_fix64_counterpart_refresh",
            }
        return target, "existing_counterpart_hash_filled", [], None

    if candidates:
        new_node = repo_file_node(repo_path, identity)
        new_id = candidate_id(new_node)
        existing = indexes["node_by_id"].get(new_id)
        if existing:
            counterpart_updates[new_id] = {
                "size_bytes": identity.size_bytes,
                "source_path": repo_path,
                "source_sha256": identity.sha256,
                "source_identity_status": "content_addressed_by_fix64_counterpart_refresh",
            }
            return new_id, "existing_current_hash_counterpart_refreshed", [], None
        created_nodes[new_id] = new_node
        repo_files_by_path.setdefault(repo_path, []).append(new_node)
        indexes["node_by_id"][new_id] = new_node
        return new_id, "new_current_hash_counterpart_created_stale_counterpart_retained", [new_node], None

    new_node = repo_file_node(repo_path, identity)
    new_id = candidate_id(new_node)
    existing = indexes["node_by_id"].get(new_id)
    if existing and existing.get("source_path") not in (None, "", repo_path):
        return (
            None,
            "escalated_repo_file_node_id_collision",
            [],
            {
                "path": repo_path,
                "computed_sha256": identity.sha256,
                "existing_candidate_id": new_id,
            },
        )
    if existing:
        counterpart_updates[new_id] = {
            "size_bytes": identity.size_bytes,
            "source_path": repo_path,
            "source_sha256": identity.sha256,
            "source_identity_status": "content_addressed_by_fix64_counterpart_refresh",
        }
        return new_id, "existing_current_hash_counterpart_refreshed", [], None
    created_nodes[new_id] = new_node
    repo_files_by_path.setdefault(repo_path, []).append(new_node)
    indexes["node_by_id"][new_id] = new_node
    return new_id, "new_counterpart_created", [new_node], None


def file_ref_patch(node: dict[str, Any], identity: PathIdentity) -> dict[str, Any]:
    status = "content_addressed_by_fix64"
    if identity.identity_kind == "repo_directory_manifest":
        status = "directory_manifest_content_addressed_by_fix64"
    elif identity.identity_kind == "external_file":
        status = "external_path_content_addressed_by_fix64_non_repo"
    patch = {
        "size_bytes": identity.size_bytes,
        "source_identity_status": status,
        "source_path": identity.repo_path,
        "source_sha256": identity.sha256,
    }
    if identity.identity_kind != "repo_file":
        patch["source_identity_kind"] = identity.identity_kind
    if not node.get("label"):
        patch["label"] = identity.repo_path
    return patch


def process_tier(
    *,
    tier: int,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    selected_ids: set[str] | None = None,
) -> dict[str, Any]:
    indexes = build_indexes(nodes, edges)
    file_refs = [
        dict(node)
        for node in nodes
        if candidate_id(node).startswith("repo:file_ref:")
        and (candidate_id(node) in selected_ids if selected_ids is not None else tier_for_file_ref(node) == tier)
    ]
    created_nodes: dict[str, dict[str, Any]] = {}
    node_updates: dict[str, dict[str, Any]] = {}
    counterpart_updates: dict[str, dict[str, Any]] = {}
    same_source_edges: list[dict[str, Any]] = []
    stale_same_source_semantics: list[tuple[str, str, str]] = []
    escalations: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    already_resolved_count = 0

    for node in sorted(file_refs, key=candidate_id):
        node_id = candidate_id(node)
        repo_path = path_for_file_ref(node)
        entry: dict[str, Any] = {
            "candidate_id": node_id,
            "graph_projection": node.get("graph_projection", ""),
            "initial_source_sha256_present": bool(node.get("source_sha256")),
            "label": node.get("label", ""),
            "source_path": node.get("source_path", ""),
            "tier": tier,
        }
        if not repo_path:
            escalation = {
                "candidate_id": node_id,
                "reason": "escalated_path_ambiguous",
                "tier": tier,
            }
            escalations.append(escalation)
            entry.update({"disposition": "escalated_path_ambiguous", "reason": escalation["reason"]})
            entries.append(entry)
            continue

        identity = path_identity(repo_path)
        if identity is None:
            escalation = {
                "candidate_id": node_id,
                "path": repo_path,
                "reason": "escalated_file_not_found",
                "tier": tier,
            }
            escalations.append(escalation)
            entry.update({"disposition": "escalated_file_not_found", "reason": escalation["reason"]})
            entries.append(entry)
            continue

        target_id, target_status, _, counterpart_escalation = counterpart_for_path(
            repo_path=repo_path,
            identity=identity,
            indexes=indexes,
            created_nodes=created_nodes,
            counterpart_updates=counterpart_updates,
        )
        if counterpart_escalation:
            escalation = {
                "candidate_id": node_id,
                "reason": target_status,
                "tier": tier,
                **counterpart_escalation,
            }
            escalations.append(escalation)
            entry.update({"disposition": target_status, "reason": target_status})
            entries.append(entry)
            continue
        if not target_id:
            raise RuntimeError("fix64_counterpart_resolution_internal_error")

        existing_same_source_targets = indexes["same_source_targets"].get(node_id, [])
        for existing_target in existing_same_source_targets:
            if existing_target != target_id:
                stale_same_source_semantics.append((node_id, "SAME_SOURCE", existing_target))
        matching_existing_edge = target_id in existing_same_source_targets
        if (
            node.get("source_sha256") == identity.sha256
            and node.get("source_path") == repo_path
            and matching_existing_edge
        ):
            already_resolved_count += 1
            entry.update(
                {
                    "counterpart": target_id,
                    "counterpart_status": target_status,
                    "disposition": "already_resolved",
                    "sha256": identity.sha256,
                }
            )
            entries.append(entry)
            continue

        node_updates[node_id] = file_ref_patch(node, identity)
        same_source = edge(
            source=node_id,
            edge_type_value="SAME_SOURCE",
            target=target_id,
            evidence=f"{repo_path}:sha256:{identity.sha256}",
            status="fix64_same_source_identity_link",
        )
        if (node_id, "SAME_SOURCE", target_id) not in indexes["edge_semantics"]:
            same_source_edges.append(same_source)
            indexes["edge_semantics"].add((node_id, "SAME_SOURCE", target_id))
            indexes["same_source_targets"].setdefault(node_id, []).append(target_id)

        entry.update(
            {
                "counterpart": target_id,
                "counterpart_status": target_status,
                "disposition": "resolved",
                "sha256": identity.sha256,
                "size_bytes": identity.size_bytes,
            }
        )
        entries.append(entry)

    return {
        "already_resolved_count": already_resolved_count,
        "counterpart_updates": counterpart_updates,
        "created_nodes": sorted(created_nodes.values(), key=candidate_id),
        "entries": entries,
        "escalations": escalations,
        "file_ref_updates": node_updates,
        "same_source_edges": same_source_edges,
        "stale_same_source_semantics": stale_same_source_semantics,
        "tier": tier,
    }


def queue_payload(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    same_source_sources = {
        edge_source(edge)
        for edge in edges
        if edge_type(edge) == "SAME_SOURCE"
    }
    entries = []
    counts = {
        "already_content_addressed": 0,
        "already_same_source_linked": 0,
        "missing_source_sha256": 0,
        "tier1": 0,
        "tier2": 0,
        "tier3": 0,
        "total_file_refs": 0,
    }
    for node in sorted(
        [node for node in nodes if candidate_id(node).startswith("repo:file_ref:")],
        key=candidate_id,
    ):
        tier = tier_for_file_ref(node)
        node_id = candidate_id(node)
        counts["total_file_refs"] += 1
        counts[f"tier{tier}"] += 1
        if node.get("source_sha256"):
            counts["already_content_addressed"] += 1
        else:
            counts["missing_source_sha256"] += 1
        if node_id in same_source_sources:
            counts["already_same_source_linked"] += 1
        entries.append(
            {
                "candidate_id": node_id,
                "graph_projection": node.get("graph_projection", ""),
                "has_same_source_edge": node_id in same_source_sources,
                "has_source_path": bool(node.get("source_path")),
                "has_source_sha256": bool(node.get("source_sha256")),
                "label": node.get("label", ""),
                "path": path_for_file_ref(node) or "",
                "source_path": node.get("source_path", ""),
                "tier": tier,
            }
        )
    return {
        "counts": counts,
        "description": "Pre-execution file_ref resolution queue generated from the unified LMDB at Fix64 execution time.",
        "entries": entries,
        "generated_by": EVALUATOR_PATH.relative_to(REPO_ROOT).as_posix(),
        "lmdb_root": LMDB_ROOT.relative_to(REPO_ROOT).as_posix(),
        "phase": PHASE,
        "schema_version": "fix64_file_ref_resolution_queue.v0.1",
        "tier1_expected_ids": TIER1_FILE_REFS,
    }


def post_counts(writer: AtlasLmdbSafeWriter) -> dict[str, int]:
    nodes = writer.store.iter_nodes()
    edges = writer.store.iter_edges()
    refs = [
        node
        for node in nodes
        if candidate_id(node).startswith("repo:file_ref:")
    ]
    same_source_sources = {
        edge_source(edge)
        for edge in edges
        if edge_type(edge) == "SAME_SOURCE"
    }
    return {
        "file_ref_count": len(refs),
        "file_refs_missing_same_source": sum(
            1 for node in refs if candidate_id(node) not in same_source_sources
        ),
        "file_refs_missing_source_path": sum(1 for node in refs if not node.get("source_path")),
        "file_refs_missing_source_sha256": sum(1 for node in refs if not node.get("source_sha256")),
        "same_source_edge_count": sum(1 for edge in edges if edge_type(edge) == "SAME_SOURCE"),
    }


def append_status_tokens_if_needed() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    if all(token in text for token in OUTPUT_TOKENS):
        return
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n### Phase 1545p-Fix64 file_ref content hash resolution\n\n")
        handle.write(
            "**Tokens:** "
            + ",".join(OUTPUT_TOKENS)
            + "\n"
        )


def write_walkthrough(report: dict[str, Any]) -> None:
    lines = [
        "# Phase 1545p-Fix64 file_ref Content Hash Resolution Walkthrough",
        "",
        "## Summary",
        "",
        f"- Phase: `{PHASE}`",
        f"- LMDB: `{LMDB_ROOT.relative_to(REPO_ROOT).as_posix()}`",
        f"- Status: `{report['status']}`",
        f"- File refs: `{report['post_counts']['file_ref_count']}`",
        f"- Missing source_sha256 after run: `{report['post_counts']['file_refs_missing_source_sha256']}`",
        f"- Missing SAME_SOURCE after run: `{report['post_counts']['file_refs_missing_same_source']}`",
        f"- New repo:file counterparts: `{report['write_receipts']['apply_plan']['accepted_node_count']}`",
        f"- New SAME_SOURCE edges: `{report['write_receipts']['apply_plan']['accepted_edge_count']}`",
        "",
        "## Commands",
        "",
        "- `python -m py_compile tools/evaluators/sim_genesis_atlas_fix64_file_ref_content_hash_resolution.py`",
        "- `python tools/evaluators/sim_genesis_atlas_fix64_file_ref_content_hash_resolution.py --tier 1`",
        "- `python tools/evaluators/sim_genesis_atlas_fix64_file_ref_content_hash_resolution.py --tier 2`",
        "- `python tools/evaluators/sim_genesis_atlas_fix64_file_ref_content_hash_resolution.py --tier 3`",
        "- `python -m pytest tests/test_phase_1545p_fix64_file_ref_content_hash_resolution.py -q`",
        "- `python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb`",
        "",
        "## Non-Claims",
        "",
        "- No Genesis signing was performed.",
        "- No public graph was uploaded or activated.",
        "- No file_ref was promoted to `genesis_core_star_map`.",
        "- No runtime activation, ECU minting, or ILC settlement occurred.",
        "",
    ]
    WALKTHROUGH_PATH.write_text("\n".join(lines), encoding="utf-8")


def phase_file_registrations() -> list[AtlasPhaseFileRegistration]:
    return [
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "policy:public_path_still_blocked_phase_1545p"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "policy:public_path_still_blocked_phase_1545p"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="phase_queue_artifact",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "policy:public_path_still_blocked_phase_1545p"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_PATH.relative_to(REPO_ROOT),
            node_kind="phase_report_artifact",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "policy:public_path_still_blocked_phase_1545p"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "policy:public_path_still_blocked_phase_1545p"),),
        ),
        AtlasPhaseFileRegistration(
            path=STATUS_PATH.relative_to(REPO_ROOT),
            node_kind="phase_status_ledger",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix64"),),
            skip_carries_forward=True,
        ),
        AtlasPhaseFileRegistration(
            path=PROMPT_PATH.relative_to(REPO_ROOT),
            node_kind="phase_prompt",
            graph_projection="support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix64"),),
        ),
    ]


def register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = phase_file_registrations()
    return writer.register_phase_files(PHASE, files, dry_run=False)


def validate_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    missing = [token for token in INPUT_TOKENS if token not in status]
    if missing:
        raise ValueError(f"fix64_missing_input_tokens:{missing}")


def summarize_tier_result(result: dict[str, Any]) -> dict[str, Any]:
    entries = result["entries"]
    return {
        "already_resolved": result["already_resolved_count"],
        "counterpart_field_updates": len(result["counterpart_updates"]),
        "entries": len(entries),
        "escalated": len(result["escalations"]),
        "new_counterpart_nodes": len(result["created_nodes"]),
        "resolved_or_updated": sum(1 for entry in entries if entry.get("disposition") == "resolved"),
        "same_source_edges_prepared": len(result["same_source_edges"]),
        "stale_same_source_edges_removed": len(result["stale_same_source_semantics"]),
        "tier": result["tier"],
    }


def apply_resolution_result(
    *,
    writer: AtlasLmdbSafeWriter,
    result: dict[str, Any],
    phase: str,
    operation: str,
) -> dict[str, Any]:
    field_updates = dict(result["counterpart_updates"])
    field_updates.update(result["file_ref_updates"])
    removal_receipt: dict[str, Any] = {
        "removed_edge_count": 0,
        "status": "PASS",
    }
    if result["stale_same_source_semantics"]:
        removal_receipt = writer.remove_edges_by_semantic(
            result["stale_same_source_semantics"],
            phase=f"{phase}:stale_same_source_removal",
            dry_run=False,
            metadata={
                "operation": f"{operation}_stale_same_source_removal",
                "tier": result["tier"],
            },
        )
        if removal_receipt["status"] != "PASS":
            raise ValueError(f"fix64_stale_same_source_removal_status:{removal_receipt['status']}")
    plan = AtlasLmdbWritePlan(
        nodes_to_add=result["created_nodes"],
        edges_to_add=result["same_source_edges"],
        metadata={
            "operation": operation,
            "tier": result["tier"],
        },
        phase=phase,
        dry_run=False,
    )
    apply_receipt = writer.apply_plan(plan)
    if apply_receipt["rejected_edge_count"]:
        raise ValueError(f"fix64_apply_rejected_edges:{apply_receipt['rejected_edges'][:5]}")
    if apply_receipt["status"] != "PASS":
        raise ValueError(f"fix64_apply_status:{apply_receipt['status']}")

    update_receipt = writer.update_node_fields(
        field_updates,
        phase=f"{phase}:content_identity_fields",
        dry_run=False,
        metadata={"operation": f"{operation}_field_update", "tier": result["tier"]},
    )
    if update_receipt["rejected_update_count"]:
        raise ValueError(f"fix64_update_rejections:{update_receipt['rejected_updates'][:5]}")
    if update_receipt["status"] != "PASS":
        raise ValueError(f"fix64_update_status:{update_receipt['status']}")
    return {
        "apply_plan": apply_receipt,
        "remove_stale_same_source": removal_receipt,
        "update_node_fields": update_receipt,
    }


def execute(tier: int) -> dict[str, Any]:
    validate_tokens()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        if not QUEUE_PATH.exists():
            write_json_atomic(QUEUE_PATH, queue_payload(nodes, edges))

        result = process_tier(tier=tier, nodes=nodes, edges=edges)
        write_receipts = apply_resolution_result(
            writer=writer,
            result=result,
            phase=f"{PHASE}:tier{tier}",
            operation="fix64_file_ref_content_hash_resolution",
        )

        counts = post_counts(writer)
        final_run = counts["file_refs_missing_source_sha256"] == 0 and counts["file_refs_missing_same_source"] == 0
        report = {
            "escalation_count": len(result["escalations"]),
            "escalations": result["escalations"][:100],
            "lmdb_root": LMDB_ROOT.relative_to(REPO_ROOT).as_posix(),
            "phase": PHASE,
            "post_counts": counts,
            "schema_version": "fix64_file_ref_resolution_report.v0.1",
            "status": "PASS" if final_run and not result["escalations"] else "PARTIAL",
            "tier_executed": tier,
            "tier_result": summarize_tier_result(result),
            "write_receipts": write_receipts,
        }
        write_json_atomic(REPORT_PATH, report)
        write_walkthrough(report)
        if final_run and not result["escalations"]:
            append_status_tokens_if_needed()
            registration = register_phase_files(writer)
            if registration["rejected_edge_count"]:
                raise ValueError(f"fix64_registration_rejected_edges:{registration['rejected_edges'][:5]}")
            if registration["status"] != "PASS":
                raise ValueError(f"fix64_registration_status:{registration['status']}")
            phase_file_ids = {
                repo_file_ref_id(registration_row.path)
                for registration_row in phase_file_registrations()
            }
            phase_file_result = process_tier(
                tier=64,
                nodes=writer.store.iter_nodes(),
                edges=writer.store.iter_edges(),
                selected_ids=phase_file_ids,
            )
            phase_file_receipts = apply_resolution_result(
                writer=writer,
                result=phase_file_result,
                phase=f"{PHASE}:phase_file_identity_links",
                operation="fix64_phase_file_registration_same_source_resolution",
            )
            writer.write_metadata(
                "fix64_phase_file_identity_link_resolution",
                {
                    "phase_file_ids": sorted(phase_file_ids),
                    "post_counts": post_counts(writer),
                    "tier_result": summarize_tier_result(phase_file_result),
                    "write_receipts": phase_file_receipts,
                },
                phase=f"{PHASE}:phase_file_identity_links",
                dry_run=False,
            )
        return report
    finally:
        writer.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", type=int, choices=(1, 2, 3), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = execute(args.tier)
    print(canonical_json({"status": report["status"], "tier": args.tier, "post_counts": report["post_counts"]}))


if __name__ == "__main__":
    main()
