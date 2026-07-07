# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import hmac
import inspect
import json
from pathlib import Path

import pytest

from ilc_core.network.d2d import spectral_route_token as srt


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"
SIM_RESULTS_PATH = REPO_ROOT / "out" / "sim_ccss_spectral_01_adversary_model_results.json"


def _bytes(label: str, index: int, length: int = 32) -> bytes:
    digest = hashlib.sha512(f"{label}:{index}".encode("utf-8")).digest()
    return digest[:length]


@pytest.fixture()
def activated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srt, "CCSS_SPECTRAL_01_NOT_ACTIVATED", False)


def test_1573h_recipient_path_functions_exist_and_guard_remains_true() -> None:
    assert srt.CCSS_SPECTRAL_01_NOT_ACTIVATED is True
    assert callable(srt.kem_decap)
    assert callable(srt.authenticate_route_token)
    assert callable(srt.validate_route_purpose)


def test_1573h_authenticate_route_token_uses_constant_time_compare() -> None:
    source = inspect.getsource(srt.authenticate_route_token)
    assert "hmac.compare_digest" in source
    assert " == " not in source
    assert " != " not in source
    assert hmac.compare_digest(b"same", b"same") is True


def test_1573h_guarded_recipient_entry_points_fail_closed() -> None:
    with pytest.raises(srt.SpectralRouteTokenError) as decap_exc:
        srt.kem_decap(b"0" * srt.CCSS_SPECTRAL_HYBRID_PRIVATE_KEY_BYTES, b"1")
    assert decap_exc.value.token == "ccss_spectral_01_not_activated_phase_1573f"

    with pytest.raises(srt.SpectralRouteTokenError) as auth_exc:
        srt.authenticate_route_token(
            b"token",
            b"shared",
            b"epoch-root",
            b"nonce",
            b"capability-context",
            b"sender-ephemeral",
            b"kem-ciphertext",
            b"hiding-commitment",
            b"relay",
        )
    assert auth_exc.value.token == "ccss_spectral_01_not_activated_phase_1573f"


def test_1573h_unlinkability_vectors_same_recipient_distinct_tokens(activated: None) -> None:
    recipient_public_key, _recipient_private_key = srt.generate_hybrid_recipient_keypair()
    tokens: list[bytes] = []
    for index in range(20):
        shared_secret, kem_ciphertext = srt.kem_encap(recipient_public_key)
        sender_ephemeral_pubkey, _mlkem_ciphertext = srt.split_hybrid_kem_ciphertext(
            kem_ciphertext
        )
        token = srt.derive_route_token(
            shared_secret,
            b"epoch-root",
            _bytes("nonce", index),
            b"capability-context",
            sender_ephemeral_pubkey,
            kem_ciphertext,
            _bytes("hiding", index),
            b"direct-message",
        )
        tokens.append(token)

    assert len(tokens) == 20
    assert len(set(tokens)) == 20


def test_1573h_forbidden_fields_reject_all_names_and_nested_depths() -> None:
    for field_name in sorted(srt.CCSS_SPECTRAL_FORBIDDEN_WIRE_FIELDS):
        with pytest.raises(srt.SpectralRouteTokenError) as top_exc:
            srt.validate_no_forbidden_fields({field_name: "leak"})
        assert top_exc.value.token == "ccss_spectral_forbidden_wire_field_present"
        assert field_name in top_exc.value.message

    with pytest.raises(srt.SpectralRouteTokenError):
        srt.validate_no_forbidden_fields({"outer": {"lambda_local": 1.0}})

    with pytest.raises(srt.SpectralRouteTokenError):
        srt.validate_no_forbidden_fields({"a": {"b": {"noise_sigma": 0.05}}})


def test_1573h_allowed_cleartext_envelope_passes_forbidden_field_validation() -> None:
    envelope = {
        "ccss_spectral_version": "ccss-spectral-01.v0.1",
        "epoch": 1,
        "route_token": "00" * 32,
        "sender_ephemeral_pubkey": "11" * 32,
        "kem_ciphertext": "22" * srt.CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES,
        "message_nonce": "33" * 32,
        "route_purpose": "relay",
        "hiding_commitment": "44" * 32,
        "capability_context_commitment": "55" * 32,
        "sealed_payload_ciphertext": "66" * 96,
        "size_class": "small",
    }
    assert set(envelope).issubset(srt.CCSS_SPECTRAL_ALLOWED_CLEARTEXT_FIELDS)
    srt.validate_no_forbidden_fields(envelope)


def test_1573h_recipient_authentication_round_trip_and_tamper_cases(
    activated: None,
) -> None:
    recipient_public_key, recipient_private_key = srt.generate_hybrid_recipient_keypair()
    shared_secret, kem_ciphertext = srt.kem_encap(recipient_public_key)
    decapsulated_secret = srt.kem_decap(recipient_private_key, kem_ciphertext)
    sender_ephemeral_pubkey, _mlkem_ciphertext = srt.split_hybrid_kem_ciphertext(
        kem_ciphertext
    )
    token = srt.derive_route_token(
        shared_secret,
        b"epoch-root",
        b"nonce",
        b"capability-context",
        sender_ephemeral_pubkey,
        kem_ciphertext,
        b"hiding-commitment",
        b"relay",
    )

    assert shared_secret == decapsulated_secret
    assert srt.authenticate_route_token(
        token,
        decapsulated_secret,
        b"epoch-root",
        b"nonce",
        b"capability-context",
        sender_ephemeral_pubkey,
        kem_ciphertext,
        b"hiding-commitment",
        b"relay",
    ) is True

    tampered_token = bytes([token[0] ^ 1]) + token[1:]
    assert srt.authenticate_route_token(
        tampered_token,
        decapsulated_secret,
        b"epoch-root",
        b"nonce",
        b"capability-context",
        sender_ephemeral_pubkey,
        kem_ciphertext,
        b"hiding-commitment",
        b"relay",
    ) is False

    assert srt.authenticate_route_token(
        token,
        decapsulated_secret,
        b"wrong-epoch-root",
        b"nonce",
        b"capability-context",
        sender_ephemeral_pubkey,
        kem_ciphertext,
        b"hiding-commitment",
        b"relay",
    ) is False


def test_1573h_route_purpose_values_are_coarse_and_enforced() -> None:
    assert srt.ROUTE_PURPOSE_VALUES == {
        b"bootstrap",
        b"direct-message",
        b"query",
        b"relay",
    }
    for value in srt.ROUTE_PURPOSE_VALUES:
        srt.validate_route_purpose(value)

    with pytest.raises(srt.SpectralRouteTokenError) as exc:
        srt.validate_route_purpose(b"free-form-high-entropy-recipient-hint")
    assert exc.value.token == (
        "ccss_spectral_01_invalid_route_purpose:"
        "free-form-high-entropy-recipient-hint"
    )


def test_1573h_commitment_non_reversibility_smoke() -> None:
    commitments = []
    prefixes = []
    for index in range(100):
        quantized = [index, index * 3, index * 7, index * 11]
        salt = _bytes("commitment-salt", index)
        commitment = srt.make_hiding_commitment(quantized, salt)
        commitments.append(commitment)
        prefixes.append(commitment[:4])

    assert len(set(commitments)) == 100
    assert len(set(prefixes)) >= 95


def test_1573h_sender_anonymity_tokens_have_no_shared_prefix_or_suffix(
    activated: None,
) -> None:
    recipient_public_key, _recipient_private_key = srt.generate_hybrid_recipient_keypair()
    quantized = srt.quantize_lambda([0.1, 0.2, 0.3, 0.4])
    tokens: list[bytes] = []
    for index in range(20):
        shared_secret, kem_ciphertext = srt.kem_encap(recipient_public_key)
        sender_ephemeral_pubkey, _mlkem_ciphertext = srt.split_hybrid_kem_ciphertext(
            kem_ciphertext
        )
        hiding_commitment = srt.make_hiding_commitment(
            quantized,
            _bytes("sender-anonymity-salt", index),
        )
        tokens.append(
            srt.derive_route_token(
                shared_secret,
                b"epoch-root",
                _bytes("sender-anonymity-nonce", index),
                b"capability-context",
                sender_ephemeral_pubkey,
                kem_ciphertext,
                hiding_commitment,
                b"direct-message",
            )
        )

    assert len(set(tokens)) == 20
    assert len({token[:4] for token in tokens}) == 20
    assert len({token[-4:] for token in tokens}) == 20


def test_1573h_sim_results_exist_and_pass() -> None:
    data = json.loads(SIM_RESULTS_PATH.read_text(encoding="utf-8"))
    assert data["sim_version"] == "ccss_spectral_01_adversary_model_1573h.v0.1"
    assert data["kem_algorithm"] == "hybrid_x25519_ml_kem_768_fips203"
    assert data["verdict"] == "pass"
    assert data["non_claim"] == "SIM pass does not constitute a formal cryptographic proof"
    assert len(data["results"]) == 18
    for row in data["results"]:
        assert row["pass"] is True
        assert row["linking_probability"] <= row["threshold"]
    for row in data["t_obs_correlation_by_n"]:
        assert row["slope"] == 0.0
        assert row["pearson_r"] == 0.0
        assert row["positive_t_obs_signal"] is False


def test_1573h_status_tokens_record_pass_not_activation() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "ccss_spectral_01_recipient_path_committed_phase_1573h" in text
    assert "ccss_spectral_01_full_test_suite_pass_phase_1573h" in text
    assert "ccss_spectral_01_sim_adversary_model_pass_phase_1573h" in text
    assert "ccss_spectral_01_sim_adversary_model_results_committed_phase_1573h" in text
    assert "public_path_remains_blocked_phase_1573h" in text
    assert "ccss_spectral_01_sim_adversary_model_fail_phase_1573h" not in text
