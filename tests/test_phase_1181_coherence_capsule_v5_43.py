from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHERENCE = ROOT / "docs/specs/ilc_integration_coherence_report_1181_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.43.md"


def test_phase_1181_coherence_report_exists():
    assert COHERENCE.exists()


def test_phase_1181_coherence_report_records_phase_outcomes():
    text = COHERENCE.read_text(encoding="utf-8")
    assert "coherence_report_1181_verdict=pass" in text
    assert "cdl_085_prelock_committed_phase_1177" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "sim_spectral_05_runtime_binding_slice_pass" in text
    assert "sim_spectral_05_economic_flow_slice_pass" in text


def test_phase_1181_capsule_v543_supersedes_v542():
    text = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_43_supersedes_v5_42" in text
    assert "Phase 1181 complete" in text
    assert "Phase 1182 closure gate pending" in text


def test_phase_1181_capsule_contains_cdl_085_prelock_and_candidate():
    text = CAPSULE.read_text(encoding="utf-8")
    assert "cdl_085_prelock_committed_phase_1177" in text
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in text
    assert "not active in `ilc_core/`" in text


def test_phase_1181_capsule_records_sim_slice_outcomes_and_signing_deferral():
    text = CAPSULE.read_text(encoding="utf-8")
    assert "sim_spectral_05_runtime_binding_slice_pass" in text
    assert "sim_spectral_05_economic_flow_slice_pass" in text
    assert "sim_spectral_05_gossip_slice_deferred_window_1176" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
