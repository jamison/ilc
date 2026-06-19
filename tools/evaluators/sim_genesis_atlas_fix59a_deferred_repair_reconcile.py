#!/usr/bin/env python3
"""Reconcile the ad hoc Fix59 deferred-repair LMDB mutation.

PUBLIC_RC_EXCLUDE: fix59a_deferred_repair_reconciliation_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB consistency repair; not Genesis signing, public graph upload, canonical mutation, runtime activation, or public RC publication.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import hashlib
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (  # noqa: E402
    GenesisAtlasCandidateStore,
)
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES  # noqa: E402
from tools.evaluators.sim_genesis_atlas_fix56_projection_aware_fiedler_rebaseline import (  # noqa: E402
    _candidate_id,
    _edge_target,
)


PHASE = "1545p-Fix59a"
ANNOTATION_PHASE = "phase_1545p_fix59a_deferred_repair_reconcile"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
SONNET_REPAIR_REPORT = REPO_ROOT / "out/genesis_atlas_fix59_deferred_repair_report_v0.1.json"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix59a_deferred_repair_reconciliation_report_v0.1.json"
PUBLIC_PATH_POLICY = "policy:public_path_still_blocked_phase_1487p"
NON_RATIFIED_CDL_STUBS = frozenset({"cdl:021", "cdl:085_prelock_spec"})
REQUIRED_REPAIR_TARGETS = frozenset(
    {
        "cdl:020",
        "cdl:021",
        "cdl:024",
        "cdl:032",
        "cdl:033",
        "cdl:082",
        "cdl:085_prelock_spec",
        "policy:genesis_optimization_harness_support_only_phase_1545p_fix9",
        "policy:human_objective_selection_boundary_phase_1545p_fix9",
        "policy:launch_roadmap_three_machines_seven_agents_v0_8_testbed_not_public_claim",
        "policy:public_path_still_blocked_phase_1487p",
    }
)
PHASE_NODE_FIX59 = "phase:1545p_fix59_missing_target_materialization"
PHASE_NODE_FIX59A = "phase:1545p_fix59a_deferred_repair_reconciliation"
PHASE_FILE_REGISTRATIONS = (
    (
        "AGENTS.md",
        "agent_guidance_node",
        PHASE_NODE_FIX59A,
        "CARRIES_FORWARD",
    ),
    (
        "docs/phases/STATUS.md",
        "phase_status_log_node",
        PHASE_NODE_FIX59A,
        "EVIDENCES",
    ),
    (
        "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix59_g10_missing_target_materialization.md",
        "phase_prompt_node",
        PHASE_NODE_FIX59,
        "CARRIES_FORWARD",
    ),
    (
        "tools/evaluators/sim_genesis_atlas_fix59_missing_target_materialization.py",
        "tooling_source_file_node",
        PHASE_NODE_FIX59,
        "IMPLEMENTS",
    ),
    (
        "tests/test_phase_1545p_fix59_missing_target_materialization.py",
        "test_evidence_node",
        "repo:file_ref:tools_evaluators_sim_genesis_atlas_fix59_missing_target_materialization_py",
        "TESTS",
    ),
    (
        "docs/phases/phase_1545p_fix59_missing_target_materialization_walkthrough.md",
        "phase_walkthrough_node",
        PHASE_NODE_FIX59,
        "EVIDENCES",
    ),
    (
        "tools/evaluators/sim_genesis_atlas_fix59a_deferred_repair_reconcile.py",
        "tooling_source_file_node",
        PHASE_NODE_FIX59A,
        "IMPLEMENTS",
    ),
    (
        "tests/test_phase_1545p_fix59a_deferred_repair_reconcile.py",
        "test_evidence_node",
        "repo:file_ref:tools_evaluators_sim_genesis_atlas_fix59a_deferred_repair_reconcile_py",
        "TESTS",
    ),
    (
        "docs/phases/phase_1545p_fix59a_deferred_repair_reconciliation_walkthrough.md",
        "phase_walkthrough_node",
        PHASE_NODE_FIX59A,
        "EVIDENCES",
    ),
)


def _canonical_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _atomic_write_json(path: Path, payload: Any) -> None:
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
            handle.write(_canonical_text(payload))
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix59a_json_object_required:{path}")
    return payload


def _patch_non_ratified_cdl_stub(node: dict[str, Any]) -> dict[str, Any]:
    patched = dict(node)
    patched["annotation_method"] = "stub_materialized"
    patched["candidate_status"] = "fix59a_non_ratified_cdl_support_stub"
    patched["category"] = "authority_reference_stub"
    patched["graph_delta"] = "support_only"
    patched["graph_projection"] = "support_candidate_graph"
    patched["node_kind"] = "authority_stub"
    patched["reconciled_by"] = ANNOTATION_PHASE
    patched["reconciliation_reason"] = (
        "Non-ratified/open-prelock CDL endpoint must remain a support stub, "
        "not a genesis_core_star_map authority node."
    )
    patched["tier"] = "support_candidate"
    return patched


def _patch_nodes(nodes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    patched_nodes: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    for node in nodes:
        node_id = _candidate_id(node)
        if node_id in NON_RATIFIED_CDL_STUBS:
            patched = _patch_non_ratified_cdl_stub(node)
            if patched != node:
                changed.append(
                    {
                        "candidate_id": node_id,
                        "from_annotation_method": str(node.get("annotation_method", "")),
                        "from_graph_projection": str(node.get("graph_projection", "")),
                        "from_node_kind": str(node.get("node_kind", "")),
                        "to_annotation_method": patched["annotation_method"],
                        "to_graph_projection": patched["graph_projection"],
                        "to_node_kind": patched["node_kind"],
                    }
                )
            patched_nodes.append(patched)
            continue
        patched_nodes.append(node)
    return patched_nodes, changed


def _file_ref_id(repo_path: str) -> str:
    sanitized = (
        repo_path.replace("/", "_")
        .replace(".", "_")
        .replace("-", "_")
        .replace("__", "_")
    )
    return f"repo:file_ref:{sanitized}"


def _phase_node(node_id: str, label: str) -> dict[str, Any]:
    return {
        "annotation_method": "phase_file_lmdb_registration",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_id": node_id,
        "candidate_status": "fix59a_phase_support_node_registered",
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": label,
        "node_kind": "phase_support_node",
        "source_path": "",
        "tier": "support_candidate",
    }


def _file_node(repo_path: str, node_kind: str) -> dict[str, Any]:
    return {
        "annotation_method": "phase_file_lmdb_registration",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_id": _file_ref_id(repo_path),
        "candidate_status": "fix59a_phase_file_registered",
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": repo_path,
        "node_kind": node_kind,
        "source_path": repo_path,
        "tier": "support_candidate",
    }


def _edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def _phase_file_edge(source: str, edge_type: str, target: str, reason: str) -> dict[str, Any]:
    return {
        "annotation_method": "phase_file_lmdb_registration",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_status": "fix59a_phase_file_edge_registered",
        "edge_id": _edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "registration_reason": reason,
        "source": source,
        "src": source,
        "target": target,
        "tgt": target,
    }


def _register_phase_files(
    *,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    node_by_id = {_candidate_id(node): dict(node) for node in nodes}
    existing_semantics = {
        (
            str(edge.get("source", edge.get("src", ""))),
            str(edge.get("edge_type", "")),
            str(edge.get("target", edge.get("tgt", ""))),
        )
        for edge in edges
    }
    phase_nodes = [
        _phase_node(PHASE_NODE_FIX59, "Phase 1545p-Fix59 missing target materialization"),
        _phase_node(PHASE_NODE_FIX59A, "Phase 1545p-Fix59a deferred repair reconciliation"),
    ]
    created_or_updated_nodes: list[dict[str, Any]] = []
    for node in phase_nodes:
        node_by_id[node["candidate_id"]] = node
        created_or_updated_nodes.append(node)
    for repo_path, node_kind, _, _ in PHASE_FILE_REGISTRATIONS:
        path = REPO_ROOT / repo_path
        if not path.exists():
            raise ValueError(f"fix59a_phase_file_missing:{repo_path}")
        node = _file_node(repo_path, node_kind)
        node_by_id[node["candidate_id"]] = node
        created_or_updated_nodes.append(node)

    candidate_edges: list[dict[str, Any]] = []
    for repo_path, _, target, edge_type in PHASE_FILE_REGISTRATIONS:
        source = _file_ref_id(repo_path)
        candidate_edges.append(
            _phase_file_edge(source, edge_type, target, f"{repo_path} registered for Fix59/Fix59a phase traceability")
        )
    candidate_edges.append(
        _phase_file_edge(PHASE_NODE_FIX59A, "CARRIES_FORWARD", PHASE_NODE_FIX59, "Fix59a reconciles Fix59 deferred-repair state")
    )
    if PUBLIC_PATH_POLICY in node_by_id:
        candidate_edges.append(
            _phase_file_edge(PHASE_NODE_FIX59, "CLASSIFIED_BY", PUBLIC_PATH_POLICY, "Fix59 remains public-path blocked")
        )
        candidate_edges.append(
            _phase_file_edge(PHASE_NODE_FIX59A, "CLASSIFIED_BY", PUBLIC_PATH_POLICY, "Fix59a remains public-path blocked")
        )

    new_edges: list[dict[str, Any]] = []
    for edge in candidate_edges:
        semantic = (edge["source"], edge["edge_type"], edge["target"])
        if edge["source"] not in node_by_id:
            raise ValueError(f"fix59a_phase_file_edge_source_missing:{edge['source']}")
        if edge["target"] not in node_by_id:
            raise ValueError(f"fix59a_phase_file_edge_target_missing:{edge['target']}")
        if semantic in existing_semantics:
            continue
        existing_semantics.add(semantic)
        new_edges.append(edge)

    return (
        sorted(node_by_id.values(), key=_candidate_id),
        new_edges,
        created_or_updated_nodes,
        candidate_edges,
    )


def _tier_counts(nodes: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(node.get("tier", "unknown")) for node in nodes).items()))


def run() -> dict[str, Any]:
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError("fix59a_unified_lmdb_missing")
    sonnet_report = _load_json(SONNET_REPAIR_REPORT)
    if sonnet_report.get("phase") != "phase_1545p_fix59_deferred_repair":
        raise ValueError("fix59a_unexpected_sonnet_repair_report_phase")

    store = GenesisAtlasCandidateStore(
        LMDB_ROOT,
        allow_synthetic_edge_keys=True,
        map_size=DEFAULT_MAP_SIZE_BYTES * 4,
    )
    try:
        pre_nodes = store.iter_nodes()
        pre_edges = store.iter_edges()
        pre_payload = store.get_graph_payload()
        if not isinstance(pre_payload, dict):
            raise ValueError("fix59a_graph_payload_missing")
        node_ids = {_candidate_id(node) for node in pre_nodes}
        missing_required_targets = sorted(REQUIRED_REPAIR_TARGETS - node_ids)
        if missing_required_targets:
            raise ValueError(f"fix59a_required_repair_targets_missing:{missing_required_targets}")
        pre_payload_node_count = len(pre_payload.get("nodes", []))
        pre_payload_edge_count = len(pre_payload.get("edges", []))
        pre_dangling_edges = sum(1 for edge in pre_edges if _edge_target(edge) not in node_ids)

        patched_nodes, patched_non_ratified_cdl_stubs = _patch_nodes(pre_nodes)
        registered_nodes, phase_file_edges, phase_file_nodes, phase_file_candidate_edges = _register_phase_files(
            nodes=patched_nodes,
            edges=pre_edges,
        )
        reconciled_edges = [*pre_edges, *phase_file_edges]
        patched_node_ids = {_candidate_id(node) for node in registered_nodes}
        post_dangling_edges = sum(1 for edge in reconciled_edges if _edge_target(edge) not in patched_node_ids)
        if post_dangling_edges:
            raise ValueError(f"fix59a_dangling_edges_after_reconcile:{post_dangling_edges}")

        # Full-list write is intentional: the adapter rebuilds indexes from the
        # provided node list, so incremental writes would corrupt tier indexes.
        store.put_nodes(registered_nodes)
        if phase_file_edges:
            store.put_edges(phase_file_edges)
        store.put_graph_payload({"nodes": registered_nodes, "edges": reconciled_edges})
        post_nodes = store.iter_nodes()
        post_edges = store.iter_edges()
        post_payload = store.get_graph_payload()
        if not isinstance(post_payload, dict):
            raise ValueError("fix59a_graph_payload_readback_missing")

        actual_tier_counts = _tier_counts(post_nodes)
        index_tier_counts = {
            tier: len(store.node_ids_by_tier(tier)) for tier in sorted(actual_tier_counts)
        }
        mismatched_indexes = {
            tier: {"actual": actual_tier_counts[tier], "index": index_tier_counts.get(tier, 0)}
            for tier in sorted(actual_tier_counts)
            if actual_tier_counts[tier] != index_tier_counts.get(tier, 0)
        }

        report: dict[str, Any] = {
            "edge_count_delta": len(post_edges) - len(pre_edges),
            "graph_payload_rebuilt_from_row_stores": True,
            "index_rebuild_performed": True,
            "index_tier_mismatches_after": mismatched_indexes,
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "non_claims": [
                "Fix59a adds only support nodes/edges for phase-file LMDB registration",
                "Fix59a reconciles local unsigned LMDB projection consistency",
                "Fix59a does not add GOVERNS edges",
                "Fix59a does not sign, publish, activate runtime behavior, activate public serving, or activate economic settlement",
            ],
            "node_count_delta": len(post_nodes) - len(pre_nodes),
            "patched_non_ratified_cdl_stubs": patched_non_ratified_cdl_stubs,
            "phase_file_candidate_edges": [
                {
                    "edge_id": edge["edge_id"],
                    "edge_type": edge["edge_type"],
                    "source": edge["source"],
                    "target": edge["target"],
                }
                for edge in phase_file_candidate_edges
            ],
            "phase_file_edges_added": [
                {
                    "edge_id": edge["edge_id"],
                    "edge_type": edge["edge_type"],
                    "source": edge["source"],
                    "target": edge["target"],
                }
                for edge in phase_file_edges
            ],
            "phase_file_nodes_registered": [
                {
                    "candidate_id": node["candidate_id"],
                    "graph_projection": node["graph_projection"],
                    "node_kind": node["node_kind"],
                    "source_path": node["source_path"],
                }
                for node in phase_file_nodes
            ],
            "phase": PHASE,
            "post_edge_count": len(post_edges),
            "post_node_count": len(post_nodes),
            "post_payload_edge_count": len(post_payload.get("edges", [])),
            "post_payload_node_count": len(post_payload.get("nodes", [])),
            "pre_edge_count": len(pre_edges),
            "pre_node_count": len(pre_nodes),
            "pre_payload_edge_count": pre_payload_edge_count,
            "pre_payload_node_count": pre_payload_node_count,
            "pre_reconcile_dangling_edges": pre_dangling_edges,
            "required_repair_targets_present": True,
            "sonnet_repair_report": str(SONNET_REPAIR_REPORT.relative_to(REPO_ROOT)),
            "status": "PASS",
        }
        if mismatched_indexes:
            raise ValueError(f"fix59a_index_rebuild_failed:{mismatched_indexes}")
        if report["post_payload_node_count"] != report["post_node_count"]:
            raise ValueError("fix59a_payload_node_count_mismatch")
        if report["post_payload_edge_count"] != report["post_edge_count"]:
            raise ValueError("fix59a_payload_edge_count_mismatch")
        store.put_meta("fix59a_deferred_repair_reconciliation", report)
    finally:
        store.close()

    _atomic_write_json(REPORT_PATH, report)
    print(
        "Done. status=PASS, "
        f"nodes={report['post_node_count']}, "
        f"edges={report['post_edge_count']}, "
        f"payload_nodes={report['post_payload_node_count']}, "
        f"payload_edges={report['post_payload_edge_count']}, "
        f"patched_non_ratified_cdl_stubs={len(report['patched_non_ratified_cdl_stubs'])}, "
        f"phase_file_nodes_registered={len(report['phase_file_nodes_registered'])}, "
        f"phase_file_edges_added={len(report['phase_file_edges_added'])}"
    )
    return report


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
