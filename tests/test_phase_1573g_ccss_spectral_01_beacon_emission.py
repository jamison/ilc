# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from ilc_core.network.d2d import spectral_route_token as srt
from ilc_core.network.d2d.spectral_beacon import (
    CCSS_SPECTRAL_ROUTE_TOKEN_ENVELOPE_VERSION,
    SpectralBeaconValidationError,
    _check_no_lambda_in_envelope,
    build_sealed_spectral_beacon,
    build_spectral_route_token_envelope,
    sign_spectral_beacon,
    validate_relay_envelope,
)
from ilc_core.network.d2d.spectral_sigma_policy import (
    CCSS_SPECTRAL_01_RATIFIED,
    H013_TESTNET_EMISSION_SIGMA,
    SIGMA_DP_CALIBRATION_VALIDATED,
    SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS,
    SIGMA_POLICY_STATUS,
    SIGMA_PRE_PUBLIC_RC_BLOCKER,
    SIGMA_WIRE_EMISSION_FORBIDDEN_AFTER_CDL_SIGMA_01,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"


def test_phase_1573g_route_token_builder_exists_and_guard_remains_on() -> None:
    assert srt.CCSS_SPECTRAL_01_NOT_ACTIVATED is True
    assert callable(build_spectral_route_token_envelope)

    recipient_public_key, _recipient_private_key = srt.generate_hybrid_recipient_keypair()
    with pytest.raises(SpectralBeaconValidationError) as exc:
        build_spectral_route_token_envelope(
            lambda_local=[0.1, 0.2, 0.3],
            recipient_pk_bytes=recipient_public_key,
            epoch=7,
            epoch_root=b"epoch-root",
            raw_cap_id="capability:receiver:example",
            route_purpose=b"direct-message",
        )
    assert exc.value.token == "ccss_spectral_01_not_activated"


def test_phase_1573g_route_token_builder_emits_only_allowed_fields_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(srt, "CCSS_SPECTRAL_01_NOT_ACTIVATED", False)

    recipient_public_key, _recipient_private_key = srt.generate_hybrid_recipient_keypair()
    envelope = build_spectral_route_token_envelope(
        lambda_local=[0.1, 0.2, 0.3],
        recipient_pk_bytes=recipient_public_key,
        epoch=7,
        epoch_root=b"epoch-root",
        raw_cap_id="capability:receiver:example",
        route_purpose=b"direct-message",
    )

    assert set(envelope).issubset(srt.CCSS_SPECTRAL_ALLOWED_CLEARTEXT_FIELDS)
    assert envelope["ccss_spectral_version"] == CCSS_SPECTRAL_ROUTE_TOKEN_ENVELOPE_VERSION
    assert envelope["epoch"] == 7
    assert envelope["route_purpose"] == "direct-message"
    assert len(envelope["route_token"]) == 64
    assert len(envelope["hiding_commitment"]) == 64
    assert len(envelope["capability_context_commitment"]) == 64
    assert len(envelope["message_nonce"]) == 64
    assert len(envelope["sender_ephemeral_pubkey"]) == (
        2 * srt.CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES
    )
    assert len(envelope["kem_ciphertext"]) == (
        2 * srt.CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES
    )
    for forbidden in srt.CCSS_SPECTRAL_FORBIDDEN_WIRE_FIELDS:
        assert forbidden not in envelope
    validate_relay_envelope(envelope)


def test_phase_1573g_relay_validator_rejects_lambda_and_sigma_fields() -> None:
    with pytest.raises(SpectralBeaconValidationError) as lambda_exc:
        validate_relay_envelope({"nested": [{"lambda_local": [0.1, 0.2]}]})
    assert lambda_exc.value.token == "ccss_spectral_forbidden_wire_field_present"

    with pytest.raises(SpectralBeaconValidationError) as sigma_exc:
        validate_relay_envelope({"noise_sigma": 0.05})
    assert sigma_exc.value.token == "ccss_spectral_forbidden_wire_field_present"


def test_phase_1573g_relay_validator_accepts_allowed_wire_shape() -> None:
    validate_relay_envelope(
        {
            "ccss_spectral_version": "ccss-spectral-01.v0.1",
            "epoch": 9,
            "route_token": "00" * 32,
            "sender_ephemeral_pubkey": "11" * 32,
            "kem_ciphertext": "22" * srt.CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES,
            "message_nonce": "33" * 32,
            "route_purpose": "direct-message",
            "hiding_commitment": "44" * 32,
            "capability_context_commitment": "55" * 32,
            "sealed_payload_ciphertext": "66" * 128,
            "size_class": "small",
        }
    )


def test_phase_1573g_check_no_lambda_maps_to_phase_token() -> None:
    with pytest.raises(SpectralBeaconValidationError) as exc:
        _check_no_lambda_in_envelope({"headers": {"lambda_local": [0.1]}})
    assert exc.value.token == "ccss_spectral_01_lambda_wire_emission_forbidden"
    assert str(exc.value) == "ccss_spectral_01_lambda_wire_emission_forbidden"


def test_phase_1573g_sigma_policy_reflects_cdl_sigma_01_boundary() -> None:
    assert CCSS_SPECTRAL_01_RATIFIED is True
    assert SIGMA_WIRE_EMISSION_FORBIDDEN_AFTER_CDL_SIGMA_01 is True
    assert SIGMA_POLICY_STATUS == "sigma_local_simulation_only_cdl_sigma_01_ratified"
    assert SIGMA_PRE_PUBLIC_RC_BLOCKER is True
    assert SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS is True
    assert SIGMA_DP_CALIBRATION_VALIDATED is False
    assert H013_TESTNET_EMISSION_SIGMA == 0.05


def test_phase_1573g_existing_public_beacon_signatures_are_unchanged() -> None:
    assert list(inspect.signature(build_sealed_spectral_beacon).parameters) == [
        "beacon",
        "relay_peer_id",
        "relay_public_key",
        "terminal_peer_id",
        "terminal_public_key",
        "channel_id",
        "emission_id",
    ]
    assert list(inspect.signature(sign_spectral_beacon).parameters) == [
        "epoch",
        "lambda_local",
        "noise_sigma",
        "signing_keypair",
    ]


def test_phase_1573g_status_tokens_record_non_activation_boundary() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "ccss_spectral_01_beacon_emission_path_updated_phase_1573g" in text
    assert "relay_ingress_forbidden_field_validator_installed_phase_1573g" in text
    assert "sigma_policy_updated_cdl_sigma_01_ratified_phase_1573g" in text
    assert "lambda_wire_emission_fail_closed_phase_1573g" in text
    assert "public_path_remains_blocked_phase_1573g" in text
