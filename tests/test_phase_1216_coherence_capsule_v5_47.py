from pathlib import Path


REPORT = Path("docs/specs/ilc_integration_coherence_report_1216_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.47.md")


def _report_text() -> str:
    return REPORT.read_text(encoding="utf-8")


def _capsule_text() -> str:
    return CAPSULE.read_text(encoding="utf-8")


def test_coherence_report_exists():
    assert REPORT.exists()


def test_capsule_v5_47_exists():
    assert CAPSULE.exists()


def test_capsule_contains_token():
    assert "capsule_v5_47_supersedes_v5_46" in _capsule_text()


def test_capsule_records_runtime_version():
    assert "epoch_attribution_settle_runtime_1210.v0.7" in _capsule_text()
    assert "edge_mint_phi_bound_enforcement_implemented_phase_1210" in _capsule_text()


def test_capsule_records_rate_limit_boundary():
    text = _capsule_text()
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in text
    assert "reciprocal_fetch_admission_model_required" in text


def test_report_records_deferred_sensitive_phases():
    text = _report_text()
    assert "cdl_086_ratification_deferred_pending_counsel_disposition" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text


def test_capsule_records_immutable_hashes():
    text = _capsule_text()
    assert "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c" in text
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in text
