# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization

from ilc_core.network.d2d import spectral_route_token as srt


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"
MODULE_PATH = REPO_ROOT / "ilc_core" / "network" / "d2d" / "spectral_route_token.py"


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
    assert srt.CCSS_SPECTRAL_01_KEM_ALGORITHM == "x25519_ecdh_contingency"


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
    assert srt.quantize_lambda([0.0, 0.001, 1.2345, -0.0001]) == [0, 1, 1234, -1]
    result = srt.quantize_lambda([2, 3.75], scale=10)
    assert result == [20, 37]
    assert all(isinstance(item, int) and not isinstance(item, bool) for item in result)

    with pytest.raises(srt.SpectralRouteTokenError):
        srt.quantize_lambda([float("nan")])
    with pytest.raises(srt.SpectralRouteTokenError):
        srt.quantize_lambda([True])


def test_hiding_commitment_is_salt_sensitive_and_stable() -> None:
    quantized_lambda = [1, 2, 3000]
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


def test_capability_context_commitment_rotates_by_epoch() -> None:
    raw_cap_id = "capability:receiver:example"
    epoch_1 = srt.make_capability_context_commitment(raw_cap_id, 1)
    epoch_2 = srt.make_capability_context_commitment(raw_cap_id, 2)

    assert len(epoch_1) == 32
    assert epoch_1 != epoch_2
    assert epoch_1 == srt.make_capability_context_commitment(raw_cap_id, 1)
    with pytest.raises(srt.SpectralRouteTokenError):
        srt.make_capability_context_commitment(raw_cap_id, -1)


def test_x25519_contingency_and_hkdf_are_testable_when_guard_is_monkeypatched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(srt, "CCSS_SPECTRAL_01_NOT_ACTIVATED", False)
    recipient_private_key = X25519PrivateKey.generate()
    recipient_public_key = recipient_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    shared_secret, sender_public_key = srt.kem_encap(recipient_public_key)
    decapsulated = recipient_private_key.exchange(
        srt.X25519PublicKey.from_public_bytes(sender_public_key)
    )
    assert shared_secret == decapsulated

    token_a = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce-a",
        b"capability-context",
        sender_public_key,
        sender_public_key,
        b"hiding-commitment",
        b"direct-message",
    )
    token_a_repeat = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce-a",
        b"capability-context",
        sender_public_key,
        sender_public_key,
        b"hiding-commitment",
        b"direct-message",
    )
    token_b = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce-b",
        b"capability-context",
        sender_public_key,
        sender_public_key,
        b"hiding-commitment",
        b"direct-message",
    )
    assert len(token_a) == 32
    assert token_a == token_a_repeat
    assert token_a != token_b

    with pytest.raises(srt.SpectralRouteTokenError) as invalid_key:
        srt.kem_encap(b"too-short")
    assert invalid_key.value.token == "ccss_spectral_recipient_public_key_invalid"


def test_status_records_exactly_one_kem_outcome_token() -> None:
    status_text = STATUS_PATH.read_text(encoding="utf-8")
    selected_tokens = [
        "kem_ml_kem_768_primary_selected_phase_1573f",
        "kem_x25519_contingency_selected_phase_1573f",
    ]
    present = [token for token in selected_tokens if token in status_text]
    assert present == ["kem_x25519_contingency_selected_phase_1573f"]
    assert "ccss_spectral_01_crypto_primitives_committed_phase_1573f" in status_text
    assert "spectral_route_token_module_created_phase_1573f" in status_text
    assert "ccss_spectral_01_not_activated_guard_installed_phase_1573f" in status_text
    assert "public_path_remains_blocked_phase_1573f" in status_text


def test_x25519_contingency_disclaimer_is_operator_visible() -> None:
    assert "post-quantum" in srt.CCSS_SPECTRAL_01_KEM_NON_PQ_DISCLAIMER
    assert "contingency" in srt.CCSS_SPECTRAL_01_KEM_NON_PQ_DISCLAIMER
    assert "kem_x25519_contingency_selected_phase_1573f" in (
        srt.CCSS_SPECTRAL_01_KEM_NON_PQ_DISCLAIMER
    )


def test_module_does_not_import_random() -> None:
    module_text = MODULE_PATH.read_text(encoding="utf-8")
    assert "import random" not in module_text
    assert "from random" not in module_text
