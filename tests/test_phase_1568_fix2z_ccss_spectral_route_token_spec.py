from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/specs/ilc_ccss_spectral_01_spectral_route_token_spec_v0.1.md"
CDL_SIGMA = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_sigma_01_spectral_sigma_adversary_model_authority_v0.1.md"
)
STATUS = REPO_ROOT / "docs/phases/STATUS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cdl_sigma_01_content_review_routes_to_ccss_spectral() -> None:
    text = _text(CDL_SIGMA)

    assert "structural rather than a mere calibration miss" in text
    assert "CCSS-SPECTRAL-01 SpectralRouteToken" in text
    assert "sigma is not a wire-level privacy primitive" in text
    assert "not a standalone differential" in text
    assert "does not activate CCSS-SPECTRAL-01" in text


def test_spectral_route_token_spec_has_non_runtime_boundary() -> None:
    text = _text(SPEC)

    assert "PUBLIC_RC_EXCLUDE" in text
    assert "This spec does not:" in text
    assert "Activate route-token runtime emission" in text
    assert "Authorize differential privacy" in text
    assert "phase_1568_fix2z_no_runtime_activation" in text


def test_spectral_route_token_derivation_uses_secret_capability_material() -> None:
    text = _text(SPEC)

    assert "ss_recipient_capability" in text
    assert "key  = ss_recipient_capability" in text
    assert "raw_contact_capability_id is not an HKDF secret" in text
    assert "capability_context_commitment" in text
    assert "key  = raw_contact_capability_id" not in text
    assert "key  = contact_capability_id" not in text


def test_cleartext_forbidden_fields_include_spectral_and_identity_leaks() -> None:
    text = _text(SPEC)

    required_forbidden = [
        "lambda_local",
        "lambda_vector",
        "eigenvalue",
        "eigenvalues",
        "spectral_fingerprint",
        "noise_sigma",
        "sender_agent_id",
        "recipient_agent_id",
        "raw_contact_capability_id",
    ]
    for field in required_forbidden:
        assert field in text

    assert "forbidden anywhere in the cleartext envelope" in text
    assert "including nested structures" in text


def test_commitment_lifecycle_blocks_relay_visible_salt() -> None:
    text = _text(SPEC)

    assert "commitment salt is not relay-visible" in text
    assert "Revealing `commitment_salt` changes the privacy surface" in text
    assert "separate governed event" in text


def test_fix2z_status_tokens_present() -> None:
    text = _text(STATUS)

    assert "phase_1568_fix2z_cdl_sigma_content_review_committed" in text
    assert "phase_1568_fix2z_ccss_spectral_route_token_spec_committed" in text
    assert "phase_1568_fix2z_forbidden_wire_fields_defined" in text
    assert "phase_1568_fix2z_no_runtime_activation" in text
    assert "public_path_remains_blocked_phase_1568_fix2z" in text
