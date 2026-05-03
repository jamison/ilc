"""Phase 1143 GENESIS-COMPILE-01 checkpoint #1 tests."""
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs/sims/sim_spectral_02/genesis_compile_checkpoint_1_1143_v0.1.md"
DIAGNOSTIC = REPO_ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json"
STAR_MAP = REPO_ROOT / "out/genesis_core_star_map_v0.1.json"

ORIGINAL_14 = {
    "artifact:genesis_agent1_pubkey_record_838a",
    "ceremony:genesis_agent1_keygen_838a",
    "policy:genesis_accrual_governor",
    "policy:genesis_authority_sunset",
    "policy:genesis_theta_hard_0_05",
    "policy:genesis_theta_soft_exp_minus_3",
    "policy:provenance_decay_alpha_0_45",
    "cdl:081_hyperedge_ecu_attribution",
    "cdl:083_panel_quorum_refutation",
    "cdl:084_provenance_chain_attribution",
    "adr:0029_hypergraph_substrate",
    "adr:0030_node_embedding_substrate",
    "adr:0032_temporal_hypergraph",
    "adr:0035_homoiconic_type_definition_system",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_c1_checkpoint_report_exists_with_token() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert "atlas_tier1_checkpoint_1_committed_phase_1143" in text
    assert "genesis_compile_checkpoint_1_pass" in text


def test_c2_diagnostic_contains_authority_traceability() -> None:
    diagnostic = _json(DIAGNOSTIC)
    authority = diagnostic["authority_traceability"]
    assert authority["attestation_root"] == "artifact:genesis_intent_attestation_init_authority_map"
    assert "authority_traceable_core_nodes" in authority


def test_c3_authority_traceability_gate_passes() -> None:
    diagnostic = _json(DIAGNOSTIC)
    assert diagnostic["authority_traceability"]["authority_traceable_core_nodes"] >= 28
    assert diagnostic["authority_traceability"]["authority_traceable_core_nodes"] == 31
    assert diagnostic["compile_coverage"]["core_nodes_total"] == 32


def test_c4_report_accounts_for_original_14_nodes() -> None:
    text = REPORT.read_text(encoding="utf-8")
    for node_id in ORIGINAL_14:
        assert node_id in text
    authority_ids = set(_json(DIAGNOSTIC)["authority_traceability"]["authority_traceable_node_ids"])
    assert ORIGINAL_14 <= authority_ids


def test_c5_star_map_contains_32_signed_nodes() -> None:
    star_map = _json(STAR_MAP)
    assert len(star_map["nodes"]) == 32
    for node in star_map["nodes"]:
        assert node["genesis_attested"] is True
        assert node["signature_status"] == "signed"
        assert node["star_map_version"] == "v0.1"


def test_c6_legacy_basis_reachability_remains_documented() -> None:
    diagnostic = _json(DIAGNOSTIC)
    assert diagnostic["compile_coverage"]["basis_reachable_core_nodes"] == 17
    text = REPORT.read_text(encoding="utf-8")
    assert "derivation_reachable (single-BFS)" in text
    assert "authority_traceable (attestation)" in text
