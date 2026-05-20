"""Regression tests for Phase 1410 ADR-0042 VRF proof verifier specification."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_PATH = REPO_ROOT / "docs/adr/ADR_0042_VRF_Proof_Verifier.md"
RUNTIME_PATH = REPO_ROOT / "ilc_core/epistemic/vrf_proof_verifier.py"


def _adr_text() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0042_exists_with_required_phase_tokens() -> None:
    text = _adr_text()

    assert ADR_PATH.exists()
    assert "vrf_proof_verifier_adr_accepted_phase_1410" in text
    assert "vrf_proof_verifier_not_activated_phase_1410" in text


def test_adr_records_algorithm_selection() -> None:
    text = _adr_text()

    assert "ECVRF-EDWARDS25519-SHA512-ELL2" in text
    assert "RFC 9381" in text
    assert "RFC 9380" in text


def test_adr_records_python_library_selection_and_rejections() -> None:
    text = _adr_text()

    assert "PyNaCl==1.6.2" in text
    assert "python-ecvrf-4o==0.1.1" in text
    assert "vrf==1.0.7" in text
    assert "rejected" in text.lower()


def test_adr_records_proof_format_and_alpha_contract() -> None:
    text = _adr_text()

    assert "public_key_b64u" in text
    assert "alpha_b64u" in text
    assert "pi_b64u" in text
    assert "beta_b64u" in text
    assert "80 bytes" in text
    assert "64 bytes" in text
    assert "sort_keys=True" in text
    assert 'separators=(",", ":")' in text
    assert "allow_nan=False" in text
    assert "ilc.vrf.jury_assignment.v1" in text


def test_adr_records_integration_contract_for_jury_assignment_runtime() -> None:
    text = _adr_text()

    assert "jury_assignment_runtime.py" in text
    assert "verify_vrf_proof" in text
    assert "vrf_beta_from_proof" in text
    assert 'assignment_mode="epoch_hash_shadow"' in text
    assert "PRODUCTION_ASSIGNMENT_NOT_ACTIVATED: bool = True" in text
    assert "J-008" in text


def test_phase_1410_does_not_create_vrf_runtime() -> None:
    assert not RUNTIME_PATH.exists()


def test_adr_does_not_claim_runtime_implementation() -> None:
    text = _adr_text()

    assert "does not implement a verifier" in text
    assert "does not activate production assignment" not in text
    assert "mark J-008 `VRF_VERIFIER_IMPLEMENTED` as MET" in text
