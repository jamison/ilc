# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62h_priority1_overlay_classification_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_priority1_overlay_classification_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_manual_graph_finish_queue_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62h_priority1_overlay_classification_report_v0.1.md"

ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt")


def test_fix62h_report_closes_priority1() -> None:
    report = _read_json(REPORT_PATH)
    assert report["status"] == "PASS"
    assert report["processed_priority1_count"] == 1159
    assert report["remaining_priority1_count"] == 0
    assert report["edge_application"]["rejected_edge_count"] == 0
    assert report["node_update"]["accepted_update_count"] == 1159


def test_fix62h_queue_only_priority3_remains() -> None:
    queue = _read_json(QUEUE_PATH)
    assert queue["entry_count"] == 3053
    assert queue["priority_counts"] == {"3": 3053}


def test_fix62h_support_policy_is_rooted_and_overlay_nodes_are_classified() -> None:
    ledger = _read_json(LEDGER_PATH)
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    assert (ROOT, "GOVERNS", SUPPORT_POLICY) in edge_semantics
    for entry in ledger["entries"][:200]:
        node = nodes[entry["candidate_id"]]
        assert node["graph_projection"] == "support_candidate_graph"
        assert node["canonicality_tier"] == "support_trace_not_independent_authority"
        assert (entry["candidate_id"], "CLASSIFIED_BY", SUPPORT_POLICY) in edge_semantics


def test_fix62h_no_dangling_recommended_edges() -> None:
    ledger = _read_json(LEDGER_PATH)
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        node_ids = {node["candidate_id"] for node in store.iter_nodes()}
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    for entry in ledger["entries"]:
        for edge in entry["recommended_edges"]:
            assert edge["source"] in node_ids
            assert edge["target"] in node_ids
            assert (edge["source"], edge["edge_type"], edge["target"]) in edge_semantics


def test_fix62h_status_and_non_claims() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62h_priority1_overlay_classification_complete" in status
    assert "fix62h_invariant_policy_overlays_demoted_to_support_trace" in status
    assert "fix62h_complete" in status
    text = REPORT_MD_PATH.read_text(encoding="utf-8")
    assert "No ECU minting" in text
    assert "not sign Genesis" in text
