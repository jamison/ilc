# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62g_governance_spine_closure_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_governance_spine_closure_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_manual_graph_finish_queue_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_governance_spine_closure_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62g_governance_spine_closure_walkthrough.md"

CDL074 = "cdl:074_truth_primitive_runtime"
PROPOSED_ADRS = {
    "adr:0015_node_transfer_economics",
    "adr:0018_sequestered_financial_shard",
    "adr:0024_agent_skills_infrastructure",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt")


def test_fix62g_report_closes_governance_spine() -> None:
    report = _read_json(REPORT_PATH)
    assert report["status"] == "PASS"
    assert report["truth_primitive_governs_added"] == 7
    assert report["post_audit"]["truth_primitive_missing_governs_count"] == 0
    assert report["post_audit"]["core_authority_missing_governs_count"] == 0
    assert report["edge_application"]["rejected_edge_count"] == 0


def test_fix62g_truth_primitives_are_governed_by_cdl074() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        truth_primitives = sorted(
            node["candidate_id"]
            for node in store.iter_nodes()
            if node.get("candidate_id", "").startswith("truth_primitive:")
        )
        cdl074_edges = {
            _edge_target(edge)
            for edge in store.iter_edges()
            if _edge_source(edge) == CDL074 and edge.get("edge_type") == "GOVERNS"
        }
    finally:
        store.close()
    assert len(truth_primitives) == 7
    assert set(truth_primitives).issubset(cdl074_edges)


def test_fix62g_proposed_adrs_remain_non_authority() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        root_governs = {
            _edge_target(edge)
            for edge in store.iter_edges()
            if _edge_source(edge) == "artifact:genesis_intent_attestation_init_authority_map"
            and edge.get("edge_type") == "GOVERNS"
        }
    finally:
        store.close()
    for node_id in PROPOSED_ADRS:
        assert node_id not in root_governs
        assert nodes[node_id]["authority_status"] == "proposed_adr_not_authority"
        assert nodes[node_id]["graph_projection"] == "support_candidate_graph"


def test_fix62g_alias_nodes_are_demoted_to_support_trace() -> None:
    ledger = _read_json(LEDGER_PATH)
    alias_rows = [
        row
        for row in ledger["entries"]
        if row["disposition"] == "trace_to_canonical_authority"
    ]
    assert alias_rows
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    for row in alias_rows:
        node = nodes[row["source"]]
        assert node["graph_projection"] == "support_candidate_graph"
        assert node["canonicality_tier"] == "support_trace_not_independent_authority"
        assert (row["source"], row["edge_type"], row["target"]) in edge_semantics


def test_fix62g_status_tokens_and_non_claims() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62g_governance_spine_closure_complete" in status
    assert "fix62g_truth_primitives_governed_by_cdl074" in status
    assert "fix62g_complete" in status
    for path in (REPORT_MD_PATH, WALKTHROUGH_PATH):
        text = path.read_text(encoding="utf-8")
        assert "ECU minting" in text
        assert "No Genesis signing" in text or "not sign Genesis" in text


def test_fix62g_queue_preserves_existing_carry_forward_shape() -> None:
    queue = _read_json(QUEUE_PATH)
    assert queue["entry_count"] == 4212
    assert "2" not in queue["priority_counts"]
