# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import cryptography
import pytest

from ilc_core.network.d2d import spectral_route_token as srt


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"
MODULE_PATH = REPO_ROOT / "ilc_core" / "network" / "d2d" / "spectral_route_token.py"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"
DOWNSTREAM_PROMPTS = [
    REPO_ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1573g_g10_ccss_spectral_01_beacon_emission.md",
    REPO_ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1573h_g10_ccss_spectral_01_full_test_and_sim.md",
    REPO_ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1573i_g10_cdl_sigma_01_adversary_model.md",
]


def test_module_guard_and_constants_are_phase_1573f_locked() -> None:
    assert srt.CCSS_SPECTRAL_01_NOT_ACTIVATED is True
    assert srt.CCSS_SPECTRAL_ROUTE_TOKEN_VERSION == (
        "ccss_spectral_route_token_1573f.v0.1"
    )
    assert srt.CCSS_SPECTRAL_ROUTE_TOKEN_HKDF_INFO_V1 == (
        b"ccss-spectral-route-token-v1"
    )
    assert srt.CCSS_SPECTRAL_HIDING_COMMIT_PREFIX == (
        b"ccss-spectral-lambda-commit-v1"
    )
    assert srt.CCSS_SPECTRAL_CAP_CONTEXT_PREFIX == (
        b"ccss-spectral-cap-context-v1"
    )
    assert srt.CCSS_SPECTRAL_QUANTIZATION_SCALE == 1000
    assert srt.CCSS_SPECTRAL_01_KEM_ALGORITHM != "<SET_FROM_STEP_1_OUTCOME>"
    assert srt.CCSS_SPECTRAL_01_KEM_ALGORITHM == "hybrid_x25519_ml_kem_768_fips203"
    assert srt.CCSS_SPECTRAL_01_KEM_SELECTION_TOKEN == (
        "kem_hybrid_x25519_ml_kem_768_selected_phase_1573f_fix1"
    )
    assert srt.CCSS_SPECTRAL_MAX_LAMBDA_COMPONENTS == 32
    assert srt.CCSS_SPECTRAL_MIN_LAMBDA_VALUE == 0.0
    assert srt.CCSS_SPECTRAL_MAX_LAMBDA_VALUE == 2.0
    assert srt.CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES == 1216
    assert srt.CCSS_SPECTRAL_HYBRID_PRIVATE_KEY_BYTES == 96
    assert srt.CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES == 1120


def test_guarded_entry_points_fail_closed_by_default() -> None:
    with pytest.raises(srt.SpectralRouteTokenError) as kem_exc:
        srt.kem_encap(b"0" * 32)
    assert kem_exc.value.token == "ccss_spectral_01_not_activated_phase_1573f"

    with pytest.raises(srt.SpectralRouteTokenError) as token_exc:
        srt.derive_route_token(
            b"shared",
            b"epoch-root",
            b"nonce",
            b"capability-context",
            b"sender-ephemeral",
            b"kem-ciphertext",
            b"hiding-commitment",
            b"route-purpose",
        )
    assert token_exc.value.token == "ccss_spectral_01_not_activated_phase_1573f"


def test_forbidden_fields_are_rejected_individually_and_recursively() -> None:
    assert len(srt.CCSS_SPECTRAL_FORBIDDEN_WIRE_FIELDS) == 13
    for field in sorted(srt.CCSS_SPECTRAL_FORBIDDEN_WIRE_FIELDS):
        with pytest.raises(srt.SpectralRouteTokenError) as exc_info:
            srt.validate_no_forbidden_fields({"ok": [{"nested": {field: "leak"}}]})
        assert exc_info.value.token == "ccss_spectral_forbidden_wire_field_present"
        assert field in exc_info.value.message


def test_valid_cleartext_shape_passes_forbidden_field_validator() -> None:
    envelope = {
        "ccss_spectral_version": "ccss-spectral-01.v0.1",
        "epoch": 1,
        "route_token": "opaque",
        "sender_ephemeral_pubkey": "opaque",
        "kem_ciphertext": "opaque",
        "message_nonce": "opaque",
        "route_purpose": "coarse",
        "hiding_commitment": "opaque",
        "capability_context_commitment": "opaque",
        "sealed_payload_ciphertext": "opaque",
        "size_class": "coarse",
        "nested": [{"relay_visible": True}],
    }
    srt.validate_no_forbidden_fields(envelope)


def test_quantize_lambda_is_deterministic_and_integer_only() -> None:
    assert srt.quantize_lambda([0.0, 0.001, 1.2345, 2.0]) == [0, 1, 1234, 2000]
    result = srt.quantize_lambda([2, 1.75], scale=10)
    assert result == [20, 17]
    assert all(isinstance(item, int) and not isinstance(item, bool) for item in result)

    with pytest.raises(srt.SpectralRouteTokenError):
        srt.quantize_lambda([float("nan")])
    with pytest.raises(srt.SpectralRouteTokenError):
        srt.quantize_lambda([True])
    with pytest.raises(srt.SpectralRouteTokenError) as negative_exc:
        srt.quantize_lambda([-0.0001])
    assert negative_exc.value.token == "ccss_spectral_lambda_component_out_of_range"
    with pytest.raises(srt.SpectralRouteTokenError) as too_large_exc:
        srt.quantize_lambda([2.0001])
    assert too_large_exc.value.token == "ccss_spectral_lambda_component_out_of_range"
    with pytest.raises(srt.SpectralRouteTokenError) as empty_exc:
        srt.quantize_lambda([])
    assert empty_exc.value.token == "ccss_spectral_lambda_vector_empty"
    with pytest.raises(srt.SpectralRouteTokenError) as vector_too_large_exc:
        srt.quantize_lambda([0.1] * 33)
    assert vector_too_large_exc.value.token == "ccss_spectral_lambda_vector_too_large"


def test_hiding_commitment_is_salt_sensitive_and_stable() -> None:
    quantized_lambda = [1, 2, 2000]
    salt_a = bytes.fromhex("00" * 32)
    salt_b = bytes.fromhex("11" * 32)
    commitment_a = srt.make_hiding_commitment(quantized_lambda, salt_a)
    commitment_a_repeat = srt.make_hiding_commitment(quantized_lambda, salt_a)
    commitment_b = srt.make_hiding_commitment(quantized_lambda, salt_b)

    assert len(commitment_a) == 32
    assert commitment_a == commitment_a_repeat
    assert commitment_a != commitment_b
    with pytest.raises(srt.SpectralRouteTokenError):
        srt.make_hiding_commitment([1, False], salt_a)
    with pytest.raises(srt.SpectralRouteTokenError) as empty_exc:
        srt.make_hiding_commitment([], salt_a)
    assert empty_exc.value.token == "ccss_spectral_quantized_lambda_empty"
    with pytest.raises(srt.SpectralRouteTokenError) as vector_too_large_exc:
        srt.make_hiding_commitment([1] * 33, salt_a)
    assert vector_too_large_exc.value.token == "ccss_spectral_quantized_lambda_too_large"
    with pytest.raises(srt.SpectralRouteTokenError) as negative_exc:
        srt.make_hiding_commitment([-1], salt_a)
    assert negative_exc.value.token == (
        "ccss_spectral_quantized_lambda_component_out_of_range"
    )
    with pytest.raises(srt.SpectralRouteTokenError) as too_large_exc:
        srt.make_hiding_commitment([2001], salt_a)
    assert too_large_exc.value.token == (
        "ccss_spectral_quantized_lambda_component_out_of_range"
    )


def test_capability_context_commitment_rotates_by_epoch() -> None:
    raw_cap_id = "capability:receiver:example"
    epoch_1 = srt.make_capability_context_commitment(raw_cap_id, 1)
    epoch_2 = srt.make_capability_context_commitment(raw_cap_id, 2)

    assert len(epoch_1) == 32
    assert epoch_1 != epoch_2
    assert epoch_1 == srt.make_capability_context_commitment(raw_cap_id, 1)
    with pytest.raises(srt.SpectralRouteTokenError):
        srt.make_capability_context_commitment(raw_cap_id, -1)


def test_hybrid_kem_and_hkdf_are_testable_when_guard_is_monkeypatched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(srt, "CCSS_SPECTRAL_01_NOT_ACTIVATED", False)

    recipient_public_key, recipient_private_key = srt.generate_hybrid_recipient_keypair()
    shared_secret, kem_ciphertext = srt.kem_encap(recipient_public_key)
    decapsulated = srt.kem_decap(recipient_private_key, kem_ciphertext)
    sender_public_key, mlkem_ciphertext = srt.split_hybrid_kem_ciphertext(kem_ciphertext)

    assert shared_secret == decapsulated
    assert len(sender_public_key) == srt.CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES
    assert len(mlkem_ciphertext) == srt.CCSS_SPECTRAL_MLKEM768_CIPHERTEXT_BYTES

    token_a = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce-a",
        b"capability-context",
        sender_public_key,
        kem_ciphertext,
        b"hiding-commitment",
        b"direct-message",
    )
    token_a_repeat = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce-a",
        b"capability-context",
        sender_public_key,
        kem_ciphertext,
        b"hiding-commitment",
        b"direct-message",
    )
    token_b = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce-b",
        b"capability-context",
        sender_public_key,
        kem_ciphertext,
        b"hiding-commitment",
        b"direct-message",
    )
    assert len(token_a) == 32
    assert token_a == token_a_repeat
    assert token_a != token_b

    with pytest.raises(srt.SpectralRouteTokenError) as invalid_key:
        srt.kem_encap(b"too-short")
    assert invalid_key.value.token == "ccss_spectral_hybrid_public_key_length_invalid"

    with pytest.raises(srt.SpectralRouteTokenError) as invalid_ct:
        srt.kem_decap(recipient_private_key, b"too-short")
    assert invalid_ct.value.token == "ccss_spectral_hybrid_ciphertext_length_invalid"


def test_status_records_historical_contingency_and_current_hybrid_fix1_token() -> None:
    status_text = STATUS_PATH.read_text(encoding="utf-8")
    assert "kem_x25519_contingency_selected_phase_1573f" in status_text
    assert "kem_hybrid_x25519_ml_kem_768_selected_phase_1573f_fix1" in status_text
    assert "ml_kem_768_dependency_resolved_phase_1573f_fix1" in status_text
    assert "kem_ml_kem_768_primary_selected_phase_1573f" not in status_text
    assert "ccss_spectral_01_crypto_primitives_committed_phase_1573f" in status_text
    assert "spectral_route_token_module_created_phase_1573f" in status_text
    assert "ccss_spectral_01_not_activated_guard_installed_phase_1573f" in status_text
    assert "public_path_remains_blocked_phase_1573f_fix1" in status_text


def test_hybrid_security_note_is_operator_visible() -> None:
    assert "X25519" in srt.CCSS_SPECTRAL_01_KEM_SECURITY_NOTE
    assert "ML-KEM-768" in srt.CCSS_SPECTRAL_01_KEM_SECURITY_NOTE
    assert "post-quantum" in srt.CCSS_SPECTRAL_01_KEM_SECURITY_NOTE
    assert "kem_hybrid_x25519_ml_kem_768_selected_phase_1573f_fix1" in (
        srt.CCSS_SPECTRAL_01_KEM_SECURITY_NOTE
    )


def test_module_does_not_import_random() -> None:
    module_text = MODULE_PATH.read_text(encoding="utf-8")
    assert "import random" not in module_text
    assert "from random" not in module_text


def test_phase_1573f_fix1_dependency_floor_uses_cryptography_48() -> None:
    assert tuple(int(part) for part in cryptography.__version__.split(".")[:2]) >= (48, 0)
    pyproject_text = PYPROJECT_PATH.read_text(encoding="utf-8")
    requirements_text = REQUIREMENTS_PATH.read_text(encoding="utf-8")
    assert "cryptography>=48.0.0" in pyproject_text
    assert "cryptography>=48.0.0" in requirements_text
    assert "liboqs-python" not in pyproject_text


def test_phase_1573f_fix1_downstream_prompts_use_hybrid_kem_posture() -> None:
    forbidden_fragments = [
        "x25519_ecdh_initial",
        "X25519 ECDH is the current KEM",
        "no post-quantum security",
        "Any claim of PQ security for X25519",
    ]
    for prompt_path in DOWNSTREAM_PROMPTS:
        prompt_text = prompt_path.read_text(encoding="utf-8")
        assert "hybrid" in prompt_text.lower(), prompt_path
        assert "ML-KEM-768" in prompt_text, prompt_path
        for fragment in forbidden_fragments:
            assert fragment not in prompt_text, (prompt_path, fragment)
