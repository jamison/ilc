from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERDICT = REPO_ROOT / "docs/specs/ilc_rehearsal_verdict_1433_v0.1.md"


def _text() -> str:
    return VERDICT.read_text(encoding="utf-8")


def test_phase_1433_verdict_document_exists_and_is_private_rehearsal_only() -> None:
    text = _text()

    assert "PUBLIC_RC_EXCLUDE: private_rehearsal_evidence" in text
    assert "public_rc_rehearsal_evidence_allowlist_review" in text
    assert "**Status:** PASS - private soft-RC rehearsal complete" in text


def test_phase_1433_required_tokens_and_binary_pass_verdict_present() -> None:
    text = _text()

    for token in (
        "rehearsal_verdict_phase_1433",
        "rehearsal_phase_2_complete_phase_1433",
        "rehearsal_lean_mathlib_dataset_complete_phase_1433",
        "rehearsal_verdict=pass_phase_1433",
    ):
        assert token in text

    assert "rehearsal_verdict=remediation_required_phase_1433" not in text
    assert "verdict=PASS" in text
    assert "remediation_required=false" in text


def test_phase_1433_lean_mathlib_dataset_is_rights_safe_and_bounded() -> None:
    text = _text()

    assert "source_repo=https://github.com/leanprover-community/mathlib4" in text
    assert "source_commit=b115fc31f3f5cf2ea5991fcc01a7d7772c0324bb" in text
    assert "license=Apache-2.0" in text
    assert "theorem_count=5" in text
    assert "no_verbatim_source=true" in text
    assert "rights_profile=metadata_extracted_claims_source_span_only_phase_1420" in text
    assert "file_sha256=c49a41482706c13df748a2c263ed7e636494c97901337a65ac8d2c6b3655e185" in text
    assert "manifest_sha256=d9b055d98d7f1e491b0977c821fd17dbdd39526f39717bef8f1c8e0780ce68d2" in text


def test_phase_1433_taxonomy_variety_uses_authoritative_enum_names() -> None:
    text = _text()

    assert "TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE" in text
    assert "TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM" in text
    assert "TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM" in text
    assert "T1+" not in text
    assert "T0.5" not in text


def test_phase_1433_execution_evidence_records_panel_and_economics_pass() -> None:
    text = _text()

    for expected in (
        "scenario_runtime_version=agent_loop_v1_runtime_575.v0.1",
        "epoch=575",
        "submission_count=7",
        "panel_verdict_token=panel_quorum_passed",
        "panel_passed=true",
        "yes_votes=7",
        "no_votes=1",
        "agreement_score=0.875",
        "ecu_claim_count=6",
        "economic_distribution_check_ok=true",
        "economic_wallet_count=8",
    ):
        assert expected in text


def test_phase_1433_preserves_phase_1432_transport_scope_correction() -> None:
    text = _text()

    assert "private HTTP/HTTPS gossip fallback over Tailscale" in text
    assert "transport_scope_correction=private_http_https_gossip_fallback_over_tailscale_not_native_rust_quic" in text
    assert "Native Rust/QUIC P2P remains deferred" in text
    assert "phase_1433_native_rust_p2p_not_activated" in text


def test_phase_1433_wipe_right_exercised_without_touching_key_material() -> None:
    text = _text()

    for expected in (
        "wipe_right_exercised_phase_1433=true",
        "rehearsal_state_wiped_phase_1433=true",
        "topology_torn_down_phase_1433=true",
        "production_keypairs_preserved_off_machine_phase_1433=true",
        "key_material_touched_by_wipe=false",
        "private_key_material_paths_accessed=[]",
        "failed_labels=[]",
    ):
        assert expected in text


def test_phase_1433_non_activation_claims_present() -> None:
    text = _text()

    for token in (
        "no_live_llm_api_phase_1433",
        "phase_1433_no_public_serving",
        "phase_1433_no_public_rc_publication",
        "phase_1433_no_epoch_0_to_1_transition",
        "phase_1433_no_cdl_mutation",
        "phase_1433_no_production_graph_write",
        "phase_1433_no_wallet_write",
        "phase_1433_no_treasury_write",
        "phase_1433_openclaw_gateway_not_publicly_activated",
    ):
        assert token in text


def test_phase_1433_next_phase_is_sensitive_transport_principal_opening() -> None:
    text = _text()

    assert "next_phase=1434" in text
    assert "next_phase_sensitivity=SENSITIVE" in text
    assert "next_phase_go_required=GO Phase 1434" in text
