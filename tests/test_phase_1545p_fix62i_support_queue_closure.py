# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62i_support_queue_closure_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62i_support_queue_closure_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62i_manual_graph_finish_queue_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62i_support_queue_closure_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62i_support_queue_closure_walkthrough.md"

SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
SOURCE_TREE_MANIFEST = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt")


def _fix66_complete() -> bool:
    return "fix66_complete" in STATUS_PATH.read_text(encoding="utf-8")


def test_fix62i_report_closes_support_queue() -> None:
    report = _read_json(REPORT_PATH)
    assert report["status"] == "PASS"
    assert report["processed_support_count"] == 3053
    assert report["queue_entry_count"] == 0
    assert report["edge_application"]["rejected_edge_count"] == 0
    assert report["node_update"]["accepted_update_count"] == 3053
    assert report["preimage_receipt"]["preimage_count"] > 0


def test_fix62i_queue_is_empty() -> None:
    queue = _read_json(QUEUE_PATH)
    assert queue["entry_count"] == 0
    assert queue["entries"] == []
    assert queue["priority_counts"] == {}
    assert queue["status"] == "manual_graph_finish_queue_empty_after_support_closure"


def test_fix62i_ledger_entries_are_machine_readable() -> None:
    ledger = _read_json(LEDGER_PATH)
    assert ledger["status"] == "support_queue_closure_complete"
    assert ledger["entry_count"] == 3053
    assert len(ledger["entries"]) == 3053
    for entry in ledger["entries"][:100]:
        assert entry["disposition"] == "classified_support_only"
        assert entry["recommended_edges"]
        assert all(edge["source"] == entry["candidate_id"] for edge in entry["recommended_edges"])


def test_fix62i_lmdb_contains_support_edges_and_node_classification() -> None:
    ledger = _read_json(LEDGER_PATH)
    sample = ledger["entries"][:250]
    repo_sample = [entry for entry in ledger["entries"] if entry["candidate_id"].startswith("repo:file:")][:250]
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()

    for entry in sample:
        node_id = entry["candidate_id"]
        assert nodes[node_id]["graph_projection"] == "support_candidate_graph"
        assert nodes[node_id]["canonicality_tier"] == "support_trace_not_independent_authority"
        if _fix66_complete():
            assert SUPPORT_POLICY not in nodes
            assert (node_id, "CLASSIFIED_BY", SUPPORT_POLICY) not in edge_semantics
        else:
            assert (node_id, "CLASSIFIED_BY", SUPPORT_POLICY) in edge_semantics

    for entry in repo_sample:
        node_id = entry["candidate_id"]
        source_tree_edge = (node_id, "SOURCE_TREE_MEMBER", SOURCE_TREE_MANIFEST)
        if _fix66_complete():
            assert source_tree_edge not in edge_semantics
        else:
            assert source_tree_edge in edge_semantics


def test_fix62i_status_tokens_and_non_claims() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62i_support_queue_closure_complete" in status
    assert "fix62i_manual_graph_finish_queue_empty" in status
    assert "fix62i_complete" in status
    for path in (REPORT_MD_PATH, WALKTHROUGH_PATH):
        text = path.read_text(encoding="utf-8")
        assert "No ECU minting" in text or "ECU minting" in text
        assert "not sign Genesis" in text or "No Genesis signing" in text
