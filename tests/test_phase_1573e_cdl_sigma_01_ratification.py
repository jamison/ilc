from __future__ import annotations

from pathlib import Path

from ilc_core.network.d2d import spectral_sigma_policy


REPO_ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
EVIDENCE = (
    REPO_ROOT / "docs/specs/ilc_cdl_sigma_01_ratification_evidence_1573e_v0.1.md"
)
SIGMA_POLICY = REPO_ROOT / "ilc_core/network/d2d/spectral_sigma_policy.py"
STATUS = REPO_ROOT / "docs/phases/STATUS.md"

FORBIDDEN_WIRE_FIELDS = [
    "lambda_local",
    "lambda_vector",
    "eigenvalue",
    "eigenvalues",
    "spectral_fingerprint",
    "noise_sigma",
    "sigma",
    "agent_id",
    "sender_agent_id",
    "recipient_agent_id",
    "recipient_public_key",
    "raw_contact_capability_id",
]

OUTPUT_TOKENS = [
    "cdl_sigma_01_ratified_phase_1573e",
    "sigma_not_wire_level_primitive_phase_1573e",
    "lambda_local_eigenvalue_array_wire_banned_phase_1573e",
    "ccss_spectral_01_ratified_successor_mechanism_phase_1573e",
    "kem_ml_kem_768_primary_target_phase_1573e",
    "kem_selection_delegated_to_phase_1573f",
    "sigma_local_obfuscation_only_phase_1573e",
    "non_dp_non_anonymity_at_public_rc_ratified_phase_1573e",
    "ccss_spectral_01_implementation_authorized_phase_1573e",
    "public_path_remains_blocked_phase_1573e",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_sigma_row() -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-SIGMA-01 |"):
            return line
    raise AssertionError("CDL-SIGMA-01 row missing")


def test_cdl_register_contains_sigma_01_ratified_row() -> None:
    row = _cdl_sigma_row()

    assert "| CDL-SIGMA-01 |" in row
    assert "| ratified | phase_1573e | cdl_sigma_01_ratified_phase_1573e |" in row


def test_cdl_register_row_preserves_non_activation_boundary() -> None:
    row = _cdl_sigma_row()

    assert "SIGMA_PRE_PUBLIC_RC_BLOCKER" in row
    assert "CCSS_SPECTRAL_01_NOT_ACTIVATED" in row
    assert "runtime_activation_status: not_authorized_until_phase_1574_activation_matrix" in row
    assert "public_path_status: blocked" in row


def test_evidence_document_exists_and_records_ratification_token() -> None:
    assert EVIDENCE.exists()
    assert "cdl_sigma_01_ratified_phase_1573e" in _read(EVIDENCE)


def test_evidence_contains_primary_target_and_delegated_kem_selection() -> None:
    text = _read(EVIDENCE)

    assert "kem_ml_kem_768_primary_target_phase_1573e" in text
    assert "kem_selection_delegated_to_phase_1573f" in text


def test_evidence_references_future_kem_outcomes_without_emitting_them() -> None:
    text = _read(EVIDENCE)

    assert "kem_ml_kem_768_primary_selected_phase_1573f" in text
    assert "kem_x25519_contingency_selected_phase_1573f" in text
    assert "not emitted by Phase 1573e" in text
    assert "future mutually exclusive outcomes" in text


def test_evidence_contains_all_forbidden_wire_fields() -> None:
    text = _read(EVIDENCE)

    for field in FORBIDDEN_WIRE_FIELDS:
        assert field in text
    assert "forbidden anywhere in the cleartext envelope" in text


def test_evidence_contains_allowed_cleartext_fields() -> None:
    text = _read(EVIDENCE)

    for field in [
        "ccss_spectral_version",
        "epoch",
        "route_token",
        "sender_ephemeral_pubkey",
        "kem_ciphertext",
        "message_nonce",
        "route_purpose",
        "hiding_commitment",
        "capability_context_commitment",
        "sealed_payload_ciphertext",
        "size_class",
    ]:
        assert field in text


def test_sigma_policy_constants_are_present_and_true() -> None:
    text = _read(SIGMA_POLICY)

    assert "SIGMA_NO_DP_CLAIM_AT_PUBLIC_RC = True" in text
    assert (
        'CDLSIGMA01_RATIFICATION_PHASE = "cdl_sigma_01_ratified_phase_1573e"'
        in text
    )
    assert spectral_sigma_policy.SIGMA_NO_DP_CLAIM_AT_PUBLIC_RC is True
    assert (
        spectral_sigma_policy.CDLSIGMA01_RATIFICATION_PHASE
        == "cdl_sigma_01_ratified_phase_1573e"
    )


def test_existing_sigma_fail_closed_policy_remains_in_place() -> None:
    assert spectral_sigma_policy.SIGMA_PRE_PUBLIC_RC_BLOCKER is True
    assert spectral_sigma_policy.SIGMA_DP_CALIBRATION_VALIDATED is False
    assert spectral_sigma_policy.SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS is True


def test_no_ccss_spectral_guard_clearance_in_code() -> None:
    for path in (REPO_ROOT / "ilc_core").rglob("*.py"):
        assert "CCSS_SPECTRAL_01_NOT_ACTIVATED = False" not in _read(path)


def test_status_contains_all_phase_1573e_tokens() -> None:
    text = _read(STATUS)

    for token in OUTPUT_TOKENS:
        assert token in text
