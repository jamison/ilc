# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
HUB_ID = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix66_residual_audit_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix66_hub_artifact_removal_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix66_hub_artifact_removal_walkthrough.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix66_hub_artifact_removal.py"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix66_g10_hub_artifact_removal.md"

CLASSIFIED_BY_FANIN_ALLOWLIST = {
    "policy:formal_publication_gate_required",
    "policy:public_path_still_blocked_phase_1545p",
}


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src") or edge.get("source_candidate_id") or edge.get("from")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt") or edge.get("target_candidate_id") or edge.get("to")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix66_prompt_validates_required_surface() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    assert text.startswith("# Phase 1545p-Fix66-G10: Hub Artifact Removal")
    assert "## LMDB Node Registration" in text
    assert "If MemPalace is used, direct-read every returned path." in text
    assert "No ellipses in walkthrough." in text


def test_fix66_status_tokens_present() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix66_hub_artifact_removal_phase_1545p",
        "hub_artifact_edges_removed_phase_1545p_fix66",
        "hub_artifact_node_removed_phase_1545p_fix66",
        "residual_audit_queue_generated_phase_1545p_fix66",
        "regression_test_no_list_artifact_hub_added_phase_1545p_fix66",
        "governance_export_rebuilt_phase_1545p_fix66",
        "fix66_complete",
    ):
        assert token in status


def test_fix66_hub_node_and_incident_edges_removed() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        node_ids = {node["candidate_id"] for node in store.iter_nodes()}
        edges = store.iter_edges()
    finally:
        store.close()

    assert HUB_ID not in node_ids
    assert all(_edge_source(edge) != HUB_ID and _edge_target(edge) != HUB_ID for edge in edges)


def test_fix66_no_non_allowlisted_support_trace_classified_by_superhub() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        fan_in = Counter(
            _edge_target(edge)
            for edge in store.iter_edges()
            if edge.get("edge_type") == "CLASSIFIED_BY"
        )
    finally:
        store.close()

    for node_id, count in fan_in.items():
        if node_id in CLASSIFIED_BY_FANIN_ALLOWLIST:
            continue
        node = nodes.get(node_id, {})
        kind = str(node.get("node_kind") or node.get("kind") or "")
        if kind in {"policy_support_trace_node", "policy_support_node"}:
            assert count <= 100, f"{node_id} has unsupported CLASSIFIED_BY fan-in {count}"


def test_fix66_residual_queue_is_machine_readable() -> None:
    payload = _read_json(QUEUE_PATH)
    assert payload["status"] == "residual_queue_after_support_list_hub_removal"
    assert payload["hub_artifact_removed"] == HUB_ID
    assert payload["entry_count"] == len(payload["entries"])
    for entry in payload["entries"]:
        assert entry["candidate_id"]
        assert entry["post_removal_degree"] <= 1
        assert entry["recommended_action"] == "manual_read_reclassify_if_build_or_governance_relevant"


def test_fix66_safe_writer_boundary_and_reports() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    for forbidden in (
        ".store.put_nodes(",
        ".store.put_edges(",
        ".store.replace_edges(",
        ".store.replace_nodes(",
        ".store.put_graph_payload(",
        ".store.put_meta(",
    ):
        assert forbidden not in source
    assert "remove_edges_by_semantic" in source
    assert "remove_nodes_by_id" in source

    report = REPORT_MD_PATH.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH_PATH.read_text(encoding="utf-8")
    assert "No Genesis signing" in walkthrough
    assert "does\nnot sign Genesis" in report
