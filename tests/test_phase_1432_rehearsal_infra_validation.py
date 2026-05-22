from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "docs/specs/ilc_rehearsal_infra_validation_evidence_1432_v0.1.md"
PROMPT = REPO / "docs/antigravity_tasks/antigravity_prompt__phase_1432_g8_rehearsal_infra_validation.md"
AGENT_LOOP = REPO / "tools/agent_loop_v1.py"
TESTBED_DIR = REPO / "tools/testbed"
SCENARIO = REPO / "testbed/scenarios/seven_agent_cycle_v1.json"


REQUIRED_TOKENS = {
    "rehearsal_infra_validation_complete_phase_1432",
    "rehearsal_epoch_cycling_confirmed_phase_1432",
    "rehearsal_review_lane_vrf_panel_confirmed_phase_1432",
    "openclaw_p2p_path_tested_phase_1432",
    "no_live_llm_api_phase_1432",
}


NON_ACTIVATION_TOKENS = {
    "phase_1432_no_public_serving",
    "phase_1432_no_public_rc_publication",
    "phase_1432_no_epoch_0_to_1_transition",
    "phase_1432_no_cdl_mutation",
    "phase_1432_no_production_graph_write",
    "phase_1432_no_wallet_write",
    "phase_1432_no_treasury_write",
    "phase_1432_native_rust_p2p_not_activated",
    "phase_1432_openclaw_gateway_not_publicly_activated",
}


def _evidence_text() -> str:
    return EVIDENCE.read_text(encoding="utf-8")


def test_phase_1432_evidence_record_exists_with_required_tokens() -> None:
    text = _evidence_text()

    assert "PUBLIC_RC_EXCLUDE: private_rehearsal_evidence" in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_1432_evidence_records_non_activation_boundaries() -> None:
    text = _evidence_text()

    for token in NON_ACTIVATION_TOKENS:
        assert token in text


def test_phase_1432_evidence_records_topology_and_transport_results() -> None:
    text = _evidence_text()

    assert "three_node_exchange_ok" in text
    assert "home_to_https://100.112.32.42:443=202" in text
    assert "home_to_https://100.91.33.46:443=202" in text
    assert "home_to_https://100.72.17.38:443=202" in text
    assert "private-rehearsal HTTP/HTTPS gossip fallback" in text
    assert "Native Rust/QUIC P2P remains deferred" in text


def test_phase_1432_evidence_records_epoch_review_and_economic_cycle() -> None:
    text = _evidence_text()

    assert "epoch=574" in text
    assert "submission_count=7" in text
    assert "panel_verdict_token=panel_quorum_passed" in text
    assert "yes_votes=7" in text
    assert "no_votes=1" in text
    assert "ecu_claim_count=6" in text
    assert "economic_distribution_check_ok=true" in text
    assert "economic_wallet_count=8" in text


def test_phase_1432_evidence_records_synthetic_dataset_and_review_lane() -> None:
    text = _evidence_text()

    assert "node_count=64" in text
    assert "review_lane_decision_count=64" in text
    assert "admitted_count=64" in text
    assert "TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION" in text
    assert "graph_write_authorized=false" in text
    assert "reviewer_payment_authorized=false" in text


def test_phase_1432_evidence_records_vrf_fixture_scope_without_key_overclaim() -> None:
    text = _evidence_text()

    assert "assignment_mode=vrf_verified" in text
    assert "regular_panel_size=7" in text
    assert "outsider_panel_size=1" in text
    assert "No Phase 1431 private identity key material" in text
    assert "production proof-generation" in text


def test_phase_1432_evidence_records_openclaw_harness_without_public_gateway() -> None:
    text = _evidence_text()

    assert "OpenClaw 2026.5.7" in text
    assert "ilc-local Ready" in text
    assert "No OpenClaw gateway listener was active on `:18789` or `:19001`" in text
    assert "Public OpenClaw P2P activation remains Phase 1437" in text


def test_phase_1432_no_live_llm_api_references_in_rehearsal_runtime() -> None:
    combined = AGENT_LOOP.read_text(encoding="utf-8")
    for path in sorted(TESTBED_DIR.glob("*.sh")) + sorted(TESTBED_DIR.glob("*.py")):
        combined += "\n" + path.read_text(encoding="utf-8")
    combined += "\n" + SCENARIO.read_text(encoding="utf-8")
    lowered = combined.lower()

    banned_terms = (
        "openai_api_key",
        "anthropic_api_key",
        "anthropic.com",
        "api.openai.com",
        "chat.completions",
        "responses.create",
    )
    for term in banned_terms:
        assert term not in lowered


def test_phase_1432_prompt_retains_unknown_unknown_discovery_structure() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")

    assert "§0a — Known-token audit" in prompt
    assert "§0b — Concept-discovery search" in prompt
    assert "§0c — Contradiction and non-claim search" in prompt
    assert "§0d — Source expansion and newly discovered tokens" in prompt
