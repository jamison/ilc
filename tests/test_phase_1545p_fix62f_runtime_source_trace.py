# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62f_runtime_source_trace_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_runtime_source_trace_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_manual_graph_finish_queue_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62f_runtime_source_trace.py"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_runtime_source_trace_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62f_runtime_source_trace_walkthrough.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix62f_report_closes_priority2_runtime_queue() -> None:
    report = _read_json(REPORT_PATH)
    assert report["status"] == "PASS"
    assert report["input_priority2_count"] == 190
    assert report["resolved_priority2_count"] == 190
    assert report["carry_forward_priority2_count"] == 0
    assert report["edge_application"]["accepted_edge_count"] >= 190
    assert report["edge_application"]["rejected_edge_count"] == 0


def test_fix62f_queue_has_no_priority2_public_protocol_entries() -> None:
    queue = _read_json(QUEUE_PATH)
    assert queue["entry_count"] == 4212
    assert queue["priority_counts"] == {"1": 1159, "3": 3053}
    assert not [
        entry
        for entry in queue["entries"]
        if entry.get("priority") == 2
        and entry.get("graph_projection") == "public_protocol_graph"
    ]


def test_fix62f_ledger_edges_have_existing_lmdb_endpoints() -> None:
    ledger = _read_json(LEDGER_PATH)
    assert ledger["entry_count"] == 190
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        node_ids = {node["candidate_id"] for node in store.iter_nodes()}
        edge_semantics = {
            (edge.get("source"), edge.get("edge_type"), edge.get("target"))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    for entry in ledger["entries"]:
        assert entry["disposition"] == "add_edges"
        assert entry["candidate_id"] in node_ids
        assert entry["recommended_edges"]
        for edge in entry["recommended_edges"]:
            assert edge["source"] in node_ids
            assert edge["target"] in node_ids
            assert (edge["source"], edge["edge_type"], edge["target"]) in edge_semantics
            assert edge["edge_type"] in {
                "CLASSIFIED_BY",
                "DERIVED_FROM",
                "IMPLEMENTS",
                "REFERENCES_AUTHORITY",
                "SOURCE_TREE_MEMBER",
            }


def test_fix62f_status_tokens_and_non_claims() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62f_runtime_source_trace_complete" in status
    assert "fix62f_priority2_runtime_nodes_repaired" in status
    assert "fix62f_complete" in status
    for path in (EVALUATOR_PATH, REPORT_MD_PATH, WALKTHROUGH_PATH):
        text = path.read_text(encoding="utf-8")
        assert "PUBLIC_RC_EXCLUDE" in text or "No Genesis signing" in text
        assert "ECU mint" in text or "ECU minting" in text
