# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix63_manual_governs_audit_report_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63_manual_governs_audit_ledger_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix63_manual_governs_audit.py"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix63_manual_governs_audit_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix63_manual_governs_audit_walkthrough.md"

ROOT = "artifact:genesis_intent_attestation_init_authority_map"
ACCEPTED_ADR_NODES = {
    "adr:0001_canonical_encoding_and_mcp_mvp",
    "adr:0022_local_first_private_use_and_publication_bound_economics",
    "adr:0022_local_first_private_use_publication_bound_economics",
    "adr:0023_quality_signal",
    "adr:0026_protocol_vs_harness_boundary",
    "adr:0028_consensus_production_bridge",
    "adr:0030_node_embedding",
    "adr:0031_subgraph_homomorphism",
    "adr:ADR_0029",
}
PROPOSED_ADR_NODES = {
    "adr:0015_node_transfer_economics",
    "adr:0018_sequestered_financial_shard",
    "adr:0021_epistemic_finality_claims",
    "adr:0024_agent_skills_infrastructure",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt")


def test_fix63_report_and_ledger_cover_all_nodes() -> None:
    report = _read_json(REPORT_PATH)
    ledger = _read_json(LEDGER_PATH)
    assert report["status"] == "PASS"
    assert report["total_reviewed"] == 497
    assert report["category_counts"] == {"adr": 15, "cdl": 31, "invariant": 451}
    assert ledger["entry_count"] == 497
    assert len(ledger["entries"]) == 497
    assert report["edge_application"]["rejected_edge_count"] == 0
    assert report["node_update"]["rejected_update_count"] == 0


def test_fix63_accepted_adrs_are_root_governed_and_proposed_are_not() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    for node_id in ACCEPTED_ADR_NODES:
        assert (ROOT, "GOVERNS", node_id) in edge_semantics
    for node_id in PROPOSED_ADR_NODES:
        assert (ROOT, "GOVERNS", node_id) not in edge_semantics


def test_fix63_cdl_shadow_duplicates_are_support_projection() -> None:
    ledger = _read_json(LEDGER_PATH)
    shadow_ids = {
        entry["candidate_id"]
        for entry in ledger["entries"]
        if entry["disposition"] == "shadow_duplicate_deduped"
    }
    assert shadow_ids
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
    finally:
        store.close()
    for node_id in shadow_ids:
        assert nodes[node_id]["graph_projection"] == "support_candidate_graph"
        assert nodes[node_id]["canonicality_tier"] == "shadow_duplicate_deduped"


def test_fix63_truth_primitive_governs_regression_guard() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        truth_primitives = {
            node["candidate_id"]
            for node in store.iter_nodes()
            if node.get("candidate_id", "").startswith("truth_primitive:")
        }
        governed = {
            _edge_target(edge)
            for edge in store.iter_edges()
            if edge.get("edge_type") == "GOVERNS"
        }
    finally:
        store.close()
    assert len(truth_primitives) == 7
    assert truth_primitives.issubset(governed)


def test_fix63_evaluator_uses_safe_writer_not_raw_adapter_writes() -> None:
    text = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in text
    for forbidden in (".put_edges(", ".put_nodes(", ".put_preimages(", ".put_meta("):
        assert forbidden not in text


def test_fix63_status_tokens_and_non_claims() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix63_manual_governs_audit_complete",
        "fix63_cdl_orphans_dispositioned",
        "fix63_adr_orphans_dispositioned",
        "fix63_invariant_batch_1_of_5_complete",
        "fix63_invariant_batch_5_of_5_complete",
        "fix63_complete",
    ):
        assert token in status
    for path in (REPORT_MD_PATH, WALKTHROUGH_PATH):
        text = path.read_text(encoding="utf-8")
        assert "ECU minting" in text
        assert "No Genesis signing" in text or "does\nnot sign Genesis" in text
