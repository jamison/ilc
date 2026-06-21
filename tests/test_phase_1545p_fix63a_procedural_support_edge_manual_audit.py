# SPDX-License-Identifier: AGPL-3.0-only
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import repo_file_ref_id


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix63a_procedural_support_edge_manual_audit_report_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63a_procedural_support_edge_manual_audit_ledger_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix63a_procedural_support_edge_manual_audit.py"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix63a_procedural_support_edge_manual_audit_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix63a_procedural_support_edge_manual_audit_walkthrough.md"

SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_source(edge: dict) -> str:
    return edge.get("source") or edge.get("src")


def _edge_target(edge: dict) -> str:
    return edge.get("target") or edge.get("tgt")


def test_fix63a_report_and_ledger_cover_support_rows() -> None:
    report = _read_json(REPORT_PATH)
    ledger = _read_json(LEDGER_PATH)
    assert report["status"] == "PASS"
    assert report["rows_reviewed"] == 373
    assert report["manual_batch_count"] == 38
    assert report["edge_application"]["rejected_edge_count"] == 0
    assert ledger["entry_count"] == 373
    assert ledger["manual_batch_count"] == 38
    assert len(ledger["entries"]) == 373


def test_fix63a_expected_procedural_edges_exist() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    assert ("cdl:085_opening_phase_1172", "OPENED_FOR", "cdl:085_werner_phi_bound") in edge_semantics
    assert ("cdl:085_prelock_spec", "PRELOCK_FOR", "cdl:085_werner_phi_bound") in edge_semantics
    assert ("cdl:085_ratification_phase_1185", "RATIFICATION_EVIDENCE_FOR", "cdl:085_werner_phi_bound") in edge_semantics
    assert ("cdl:001", "SAME_AUTHORITY", "cdl:001_signer_lineage_trust_root") in edge_semantics
    assert (
        "adr:0028_option_b_graduation_posture",
        "DERIVED_FROM",
        "adr:0028_consensus_production_bridge",
    ) in edge_semantics


def test_fix63a_accepted_adr_invariant_edges_exist() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    assert (
        "adr:0020_knowledge_node_first_design_principle",
        "GOVERNS",
        "invariant:adr0020_acceptance_scope_boundary_and_unsigned_v02_candidate_presence",
    ) in edge_semantics
    assert (
        "adr:0036_operational_release_key_genesis_binding",
        "GOVERNS",
        "invariant:adr0036_release_key_draft_status_lineage_separation_and_release_key_chain",
    ) in edge_semantics
    assert (
        "adr:0037_genesis_canonical_lineage_contract",
        "GOVERNS",
        "invariant:branchial_claim_projection_schema_operations_determinism_and_adr0037_criterion",
    ) in edge_semantics


def test_fix63a_status_file_registered_with_edges() -> None:
    status_node = repo_file_ref_id("docs/phases/STATUS.md")
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
        edge_semantics = {
            (_edge_source(edge), edge.get("edge_type"), _edge_target(edge))
            for edge in store.iter_edges()
        }
    finally:
        store.close()
    assert status_node in nodes
    assert (status_node, "CLASSIFIED_BY", "policy:public_path_still_blocked_phase_1545p") in edge_semantics
    assert (status_node, "CARRIES_FORWARD", "phase:1545p_fix63a") in edge_semantics
    assert (status_node, "EVIDENCES", "phase:1545p_fix63a") in edge_semantics


def test_fix63a_evaluator_uses_safe_writer_not_raw_adapter_writes() -> None:
    text = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in text
    for forbidden in (".put_edges(", ".put_nodes(", ".put_preimages(", ".put_meta("):
        assert forbidden not in text


def test_fix63a_status_tokens_and_non_claims() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix63a_procedural_support_edge_audit_complete",
        "fix63a_support_lifecycle_records_enriched",
        "fix63a_complete",
    ):
        assert token in status
    for path in (REPORT_MD_PATH, WALKTHROUGH_PATH):
        text = path.read_text(encoding="utf-8")
        assert "ECU minting" in text
        assert "No Genesis signing" in text or "does not sign Genesis" in text
