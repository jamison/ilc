#!/usr/bin/env python3
"""Remove the Fix22 support-list hub from the unsigned Atlas LMDB topology.

PUBLIC_RC_EXCLUDE: fix66_hub_artifact_removal_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
    write_json_atomic,
)


PHASE = "1545p-Fix66"
HUB_ID = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix66_g10_hub_artifact_removal.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix66_hub_artifact_removal.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix66_hub_artifact_removal.py"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix66_residual_audit_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix66_hub_artifact_removal_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix66_hub_artifact_removal_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix66_hub_artifact_removal_v0.1.json"

INPUT_TOKENS = ("fix65_complete",)
OUTPUT_TOKENS = (
    "fix66_hub_artifact_removal_phase_1545p",
    "hub_artifact_edges_removed_phase_1545p_fix66",
    "hub_artifact_node_removed_phase_1545p_fix66",
    "residual_audit_queue_generated_phase_1545p_fix66",
    "regression_test_no_list_artifact_hub_added_phase_1545p_fix66",
    "governance_export_rebuilt_phase_1545p_fix66",
    "fix66_complete",
)


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix66_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix66_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix66_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type") or edge.get("type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix66_edge_type_missing")
    return value


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix66_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix66_output_token_already_present:{token}")


def _edge_direction(source: str, target: str) -> str:
    if source == HUB_ID and target == HUB_ID:
        return "self"
    if source == HUB_ID:
        return "out"
    if target == HUB_ID:
        return "in"
    return "none"


def _incident_hub_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in edges
        if _edge_source(edge) == HUB_ID or _edge_target(edge) == HUB_ID
    ]


def _hub_edge_breakdown(edges: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        counts[f"{_edge_direction(source, target)}:{_edge_type(edge)}"] += 1
    return dict(sorted(counts.items()))


def _edge_semantics(edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {(_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in edges}


def _degree_by_node(edges: list[dict[str, Any]]) -> Counter[str]:
    degree: Counter[str] = Counter()
    for edge in edges:
        degree[_edge_source(edge)] += 1
        degree[_edge_target(edge)] += 1
    return degree


def _top_classified_targets(edges: list[dict[str, Any]], *, limit: int = 20) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for edge in edges:
        if _edge_type(edge) == "CLASSIFIED_BY":
            counts[_edge_target(edge)] += 1
    return [
        {"node_id": node_id, "classified_by_fan_in": count}
        for node_id, count in counts.most_common(limit)
    ]


def _residual_queue(
    *,
    formerly_connected: set[str],
    nodes_by_id: dict[str, dict[str, Any]],
    pre_edges: list[dict[str, Any]],
    post_edges: list[dict[str, Any]],
) -> dict[str, Any]:
    pre_degree = _degree_by_node(pre_edges)
    post_degree = _degree_by_node(post_edges)
    entries: list[dict[str, Any]] = []
    for node_id in sorted(formerly_connected - {HUB_ID}):
        node = nodes_by_id.get(node_id, {})
        degree_after = post_degree.get(node_id, 0)
        if degree_after > 1:
            continue
        entries.append(
            {
                "candidate_id": node_id,
                "graph_projection": node.get("graph_projection", ""),
                "node_kind": node.get("node_kind") or node.get("kind", ""),
                "post_removal_degree": degree_after,
                "pre_removal_degree": pre_degree.get(node_id, 0),
                "recommended_action": "manual_read_reclassify_if_build_or_governance_relevant",
                "source_path": node.get("source_path", ""),
                "tier": node.get("tier", ""),
            }
        )
    return {
        "entry_count": len(entries),
        "entries": entries,
        "generated_phase": PHASE,
        "hub_artifact_removed": HUB_ID,
        "status": "residual_queue_after_support_list_hub_removal",
        "total_formerly_connected_nodes": len(formerly_connected - {HUB_ID}),
    }


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            PROMPT_PATH.relative_to(REPO_ROOT),
            "phase_prompt_node",
            "support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            EVALUATOR_PATH.relative_to(REPO_ROOT),
            "tooling_source_file_node",
            "support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("ilc_core/storage/genesis_atlas_candidate_lmdb_adapter.py"),
            "runtime_source_file_node",
            "support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("ilc_core/storage/genesis_atlas_lmdb_writer.py"),
            "runtime_source_file_node",
            "support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("tools/evaluators/sim_genesis_atlas_fix62h_priority1_overlay_classification.py"),
            "tooling_source_file_node",
            "support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("tools/evaluators/sim_genesis_atlas_fix62i_support_queue_closure.py"),
            "tooling_source_file_node",
            "support_candidate_graph",
            required_edges=(("CARRIES_FORWARD", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            TEST_PATH.relative_to(REPO_ROOT),
            "test_evidence_node",
            "support_candidate_graph",
            graph_delta="load_bearing_artifact_added",
            required_edges=(("TESTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py"),
            "test_evidence_node",
            "support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("tests/test_phase_1545p_fix62h_priority1_overlay_classification.py"),
            "test_evidence_node",
            "support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("tests/test_phase_1545p_fix62i_support_queue_closure.py"),
            "test_evidence_node",
            "support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            Path("tools/graph_viz_3d.py"),
            "tooling_source_file_node",
            "support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            QUEUE_PATH.relative_to(REPO_ROOT),
            "spec_json_artifact_node",
            "support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            REPORT_MD_PATH.relative_to(REPO_ROOT),
            "spec_document_node",
            "support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            "phase_walkthrough_node",
            "support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix66"),),
        ),
        AtlasPhaseFileRegistration(
            STATUS_PATH.relative_to(REPO_ROOT),
            "phase_status_log",
            "support_candidate_graph",
            skip_carries_forward=True,
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _append_status(report: dict[str, Any]) -> None:
    block = f"""

### Phase 1545p-Fix66 — Hub Artifact Removal

**Status:** complete

**Output:** Removed `{report['edge_removal']['live_removed_edge_count']}` incident edges from the Fix22 support-list hub, removed the isolated hub node from the unified LMDB, generated a residual audit queue with `{report['residual_queue_entry_count']}` entries, added safe writer node removal support, and preserved all non-activation boundaries.

**Tokens:** {','.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(STATUS_PATH.read_text(encoding="utf-8").rstrip() + block + "\n", encoding="utf-8")


def _report_markdown(report: dict[str, Any]) -> str:
    return f"""# ILC Fix66 Hub Artifact Removal Report

PUBLIC_RC_EXCLUDE: fix66_hub_artifact_removal_research_only

## Summary

- Hub artifact: `{HUB_ID}`
- Pre-removal LMDB: `{report['pre_counts']['nodes']}` nodes / `{report['pre_counts']['edges']}` edges
- Hub incident edges removed: `{report['edge_removal']['live_removed_edge_count']}`
- Hub node removed: `{report['node_removal']['live_removed_node_count']}`
- Residual audit queue entries: `{report['residual_queue_entry_count']}`
- Post-repair LMDB before phase-file registration: `{report['post_repair_counts']['nodes']}` nodes / `{report['post_repair_counts']['edges']}` edges
- Governance export after repair: `{report['governance_export']['node_count']}` nodes / `{report['governance_export']['edge_count']}` edges

## Hub Edge Breakdown

```json
{json.dumps(report['hub_edge_breakdown_before'], sort_keys=True, indent=2)}
```

## Boundary

This phase repairs the local unsigned Atlas LMDB candidate topology only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, clear a public path gate, or mutate canonical protocol authority.
"""


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix66 Walkthrough

## Commands

```bash
python tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix66_g10_hub_artifact_removal.md
python -m py_compile ilc_core/storage/genesis_atlas_candidate_lmdb_adapter.py ilc_core/storage/genesis_atlas_lmdb_writer.py tools/evaluators/sim_genesis_atlas_fix66_hub_artifact_removal.py
python tools/evaluators/sim_genesis_atlas_fix66_hub_artifact_removal.py
python -m pytest tests/test_phase_1545p_fix66_hub_artifact_removal.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py tests/test_phase_1545p_fix62h_priority1_overlay_classification.py tests/test_phase_1545p_fix62i_support_queue_closure.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
python tools/graph_viz_export.py --view governance --output-dir out/viz_exports --omit-export-time
python tools/graph_viz_3d.py --lmdb --view governance
```

## Result

- Hub artifact existed before repair: `{report['hub_existed_before']}`
- Hub artifact exists after repair: `{report['hub_exists_after_repair']}`
- Incident edge breakdown before repair: `{json.dumps(report['hub_edge_breakdown_before'], sort_keys=True)}`
- Edge dry-run removal count: `{report['edge_removal']['dry_run_removed_edge_count']}`
- Edge live removal count: `{report['edge_removal']['live_removed_edge_count']}`
- Node dry-run removal count: `{report['node_removal']['dry_run_removed_node_count']}`
- Node live removal count: `{report['node_removal']['live_removed_node_count']}`
- Residual audit queue entries: `{report['residual_queue_entry_count']}`
- Post-repair LMDB before phase-file registration: `{report['post_repair_counts']['nodes']}` nodes / `{report['post_repair_counts']['edges']}` edges / `{report['post_repair_counts']['dangling_edge_count']}` dangling / `{report['post_repair_counts']['edge_id_debt_count']}` edge-id debt
- Governance export after repair: `{report['governance_export']['node_count']}` nodes / `{report['governance_export']['edge_count']}` edges

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, ILC settlement, public-path authorization, or
canonical protocol authority mutation occurred.
"""


def _validate_report(report: dict[str, Any]) -> None:
    if not report["hub_existed_before"]:
        raise ValueError("fix66_hub_missing_before_repair")
    if report["edge_removal"]["live_removed_edge_count"] != report["hub_incident_edge_count_before"]:
        raise ValueError("fix66_removed_edge_count_mismatch")
    if report["node_removal"]["live_removed_node_count"] != 1:
        raise ValueError("fix66_hub_node_not_removed")
    if report["hub_exists_after_repair"]:
        raise ValueError("fix66_hub_still_exists_after_repair")
    if report["post_repair_counts"]["dangling_edge_count"] != 0:
        raise ValueError("fix66_dangling_edges_after_repair")
    if report["post_repair_counts"]["edge_id_debt_count"] != 0:
        raise ValueError("fix66_edge_id_debt_after_repair")


def run() -> dict[str, Any]:
    _verify_tokens()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        pre_nodes = writer.store.iter_nodes()
        pre_edges = writer.store.iter_edges()
        nodes_by_id = {_candidate_id(node): node for node in pre_nodes}
        hub_existed_before = HUB_ID in nodes_by_id
        incident_edges = _incident_hub_edges(pre_edges)
        formerly_connected = {HUB_ID}
        for edge in incident_edges:
            formerly_connected.add(_edge_source(edge))
            formerly_connected.add(_edge_target(edge))

        edge_semantics = _edge_semantics(incident_edges)
        edge_dry_run = writer.remove_edges_by_semantic(
            edge_semantics,
            phase=PHASE,
            dry_run=True,
            metadata={"operation": "fix66_hub_incident_edge_removal"},
        )
        edge_live = writer.remove_edges_by_semantic(
            edge_semantics,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix66_hub_incident_edge_removal"},
        )
        node_dry_run = writer.remove_nodes_by_id(
            {HUB_ID},
            phase=PHASE,
            dry_run=True,
            metadata={"operation": "fix66_hub_node_removal"},
        )
        node_live = writer.remove_nodes_by_id(
            {HUB_ID},
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix66_hub_node_removal"},
        )

        post_repair_nodes = writer.store.iter_nodes()
        post_repair_edges = writer.store.iter_edges()
        post_nodes_by_id = {_candidate_id(node): node for node in post_repair_nodes}
        queue = _residual_queue(
            formerly_connected=formerly_connected,
            nodes_by_id=nodes_by_id,
            pre_edges=pre_edges,
            post_edges=post_repair_edges,
        )
        write_json_atomic(QUEUE_PATH, queue)
        post_repair_inspection = writer.inspect()
        export_result = subprocess.run(
            [
                sys.executable,
                "tools/graph_viz_export.py",
                "--view",
                "governance",
                "--output-dir",
                "out/viz_exports",
                "--omit-export-time",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        governance_export = json.loads(
            (REPO_ROOT / "out/viz_exports/graph_view_governance.json").read_text(
                encoding="utf-8"
            )
        )
        report = {
            "edge_removal": {
                "dry_run_removed_edge_count": edge_dry_run["removed_edge_count"],
                "live_removed_edge_count": edge_live["removed_edge_count"],
                "live_status": edge_live["status"],
            },
            "governance_export": {
                "edge_count": governance_export["metadata"]["edge_count"],
                "node_count": governance_export["metadata"]["node_count"],
                "stdout": export_result.stdout.strip(),
            },
            "hub_edge_breakdown_before": _hub_edge_breakdown(incident_edges),
            "hub_exists_after_repair": HUB_ID in post_nodes_by_id,
            "hub_existed_before": hub_existed_before,
            "hub_incident_edge_count_before": len(incident_edges),
            "node_removal": {
                "dry_run_removed_node_count": node_dry_run["removed_node_count"],
                "live_removed_node_count": node_live["removed_node_count"],
                "live_status": node_live["status"],
            },
            "phase": PHASE,
            "post_repair_counts": {
                "dangling_edge_count": post_repair_inspection["dangling_edge_count"],
                "edge_id_debt_count": post_repair_inspection["edge_id_debt_count"],
                "edges": post_repair_inspection["edge_count"],
                "nodes": post_repair_inspection["node_count"],
            },
            "pre_counts": {
                "edges": len(pre_edges),
                "nodes": len(pre_nodes),
            },
            "residual_queue_entry_count": queue["entry_count"],
            "status": "PASS",
            "top_classified_targets_before": _top_classified_targets(pre_edges),
            "top_classified_targets_after_repair": _top_classified_targets(post_repair_edges),
        }
        _validate_report(report)
        REPORT_MD_PATH.write_text(_report_markdown(report), encoding="utf-8")
        WALKTHROUGH_PATH.write_text(_walkthrough_markdown(report), encoding="utf-8")
        _append_status(report)
        registration_receipt = _register_phase_files(writer)
        final_inspection = writer.inspect()
        report["file_registration"] = {
            "accepted_edge_count": registration_receipt["accepted_edge_count"],
            "accepted_node_count": registration_receipt["accepted_node_count"],
        }
        report["final_counts_after_phase_file_registration"] = {
            "dangling_edge_count": final_inspection["dangling_edge_count"],
            "edge_id_debt_count": final_inspection["edge_id_debt_count"],
            "edges": final_inspection["edge_count"],
            "nodes": final_inspection["node_count"],
        }
        write_json_atomic(OUT_REPORT_PATH, report)
        return report
    finally:
        writer.close()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
