from __future__ import annotations

import pytest

from ilc_core.analysis.spectral_utils import add_noise
from ilc_core.network.d2d.spectral_beacon import (
    BEACON_EMISSION_MODE_MAINNET,
    BEACON_EMISSION_MODE_TESTNET,
    SpectralBeaconReplayCache,
    generate_beacon_signing_keypair,
    generate_sealed_sender_keypair,
    open_terminal_layer,
    peel_relay_layer,
)
from ilc_core.network.d2d.spectral_sigma_policy import (
    H013_SIGMA_POLICY_STATUS,
    H013_TESTNET_EMISSION_SIGMA,
    MIN_NOISE_SIGMA,
    SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN,
    SIGMA_DP_CALIBRATION_VALIDATED,
    SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS,
    SIGMA_MAINNET_PROVISIONAL_STATUS,
    SIGMA_OBLIGATION_ID,
    SIGMA_POLICY_STATUS,
    SIGMA_PRE_PUBLIC_RC_BLOCKER,
    SIGMA_REVOCATION_PATH,
    SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED,
    SIM_BEACON_01_PRIVACY_TARGET_VALIDATED,
    SpectralSigmaPolicyError,
    build_sigma_policy_status_record,
    normalize_noise_sigma,
    validate_noise_sigma_for_mode,
)
from ilc_core.node import node_startup_runtime


def test_h013_sigma_policy_records_no_privacy_calibration_claim() -> None:
    assert SIGMA_POLICY_STATUS == "specified_floor_testnet_candidate_obl_046_open"
    assert H013_SIGMA_POLICY_STATUS == SIGMA_POLICY_STATUS
    assert SIGMA_DP_CALIBRATION_VALIDATED is False
    assert SIM_BEACON_01_PRIVACY_TARGET_VALIDATED is False
    assert SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED is True
    assert node_startup_runtime.H013_SIGMA_STATUS == SIGMA_POLICY_STATUS
    assert node_startup_runtime.H013_SIGMA_DP_CALIBRATION_VALIDATED is False
    assert node_startup_runtime.H013_SIGMA_PRIVACY_TARGET_VALIDATED is False
    assert SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS is True
    assert (
        SIGMA_MAINNET_PROVISIONAL_STATUS
        == "genesis_authorized_provisional_mainnet_sigma_obl_046_open"
    )
    assert (
        node_startup_runtime.H013_SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS
        is True
    )
    assert SIGMA_OBLIGATION_ID == "OBL-046"
    assert SIGMA_PRE_PUBLIC_RC_BLOCKER is True
    assert (
        SIGMA_REVOCATION_PATH
        == "close_obl_046_with_validated_sigma_or_revoke_genesis_provisional_authority"
    )
    assert node_startup_runtime.H013_SIGMA_ADVERSARY_MODEL_REVISION_REQUIRED is True


def test_h013_sigma_policy_status_record_surfaces_provisional_boundary() -> None:
    record = build_sigma_policy_status_record()

    assert record["version"] == "h013_spectral_sigma_policy.v0.1"
    assert record["sigma_policy_status"] == SIGMA_POLICY_STATUS
    assert record["obl_id"] == "OBL-046"
    assert record["pre_public_rc_blocker"] is True
    assert record["h013_testnet_emission_sigma"] == H013_TESTNET_EMISSION_SIGMA
    assert record["sigma_dp_calibration_validated"] is False
    assert (
        record["sigma_dp_calibration_not_validated_token"]
        == SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN
    )
    assert record["sigma_mainnet_provisional_authorized_by_genesis"] is True
    assert (
        record["sigma_mainnet_provisional_status"]
        == "genesis_authorized_provisional_mainnet_sigma_obl_046_open"
    )
    assert record["revocation_or_replacement_path"] == SIGMA_REVOCATION_PATH


def test_h013_generic_sigma_floor_validation() -> None:
    assert normalize_noise_sigma(MIN_NOISE_SIGMA) == MIN_NOISE_SIGMA
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        normalize_noise_sigma(MIN_NOISE_SIGMA - 0.001)
    assert exc.value.token == "h013_noise_sigma_below_floor"


def test_h013_testnet_sigma_candidate_is_pinned() -> None:
    assert (
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA,
            mode=BEACON_EMISSION_MODE_TESTNET,
        )
        == H013_TESTNET_EMISSION_SIGMA
    )
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(MIN_NOISE_SIGMA, mode=BEACON_EMISSION_MODE_TESTNET)
    assert exc.value.token == "h013_noise_sigma_testnet_candidate_mismatch"

    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA + 0.001,
            mode=BEACON_EMISSION_MODE_TESTNET,
        )
    assert exc.value.token == "h013_noise_sigma_testnet_candidate_mismatch"


def test_h013_mainnet_sigma_is_genesis_authorized_provisional() -> None:
    assert (
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA,
            mode=BEACON_EMISSION_MODE_MAINNET,
        )
        == H013_TESTNET_EMISSION_SIGMA
    )
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA + 0.001,
            mode=BEACON_EMISSION_MODE_MAINNET,
        )
    assert exc.value.token == "h013_noise_sigma_mainnet_candidate_mismatch"


def test_h013_privacy_calibrated_sigma_request_fails_closed() -> None:
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA,
            mode=BEACON_EMISSION_MODE_TESTNET,
            require_privacy_calibrated=True,
        )
    assert exc.value.token == SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN
    assert str(exc.value) == SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN

    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA,
            mode=BEACON_EMISSION_MODE_MAINNET,
            require_privacy_calibrated=True,
        )
    assert exc.value.token == SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN


def test_add_noise_enforces_shared_sigma_floor() -> None:
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        add_noise([0.1, 0.2], sigma=0.0)
    assert exc.value.token == "h013_noise_sigma_below_floor"


def test_node_startup_validates_h013_testnet_sigma_policy() -> None:
    assert (
        node_startup_runtime._validate_h013_startup_sigma_policy()
        == H013_TESTNET_EMISSION_SIGMA
    )


def test_node_startup_rejects_h013_testnet_sigma_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        node_startup_runtime,
        "H013_TESTNET_EMISSION_SIGMA",
        H013_TESTNET_EMISSION_SIGMA + 0.001,
    )
    with pytest.raises(ValueError) as exc:
        node_startup_runtime._validate_h013_startup_sigma_policy()
    assert str(exc.value) == "h013_noise_sigma_testnet_candidate_mismatch"


def test_maybe_emit_spectral_beacon_allows_genesis_provisional_mainnet_mode() -> None:
    relay_keypair = generate_sealed_sender_keypair()
    terminal_keypair = generate_sealed_sender_keypair()
    emission_state = node_startup_runtime.SpectralEmissionState()

    envelope = node_startup_runtime.maybe_emit_spectral_beacon(
        emission_state,
        generate_beacon_signing_keypair(),
        relay_peer_id="peer:relay001",
        relay_public_key=relay_keypair.public_key_bytes,
        terminal_peer_id="peer:terminal001",
        terminal_public_key=terminal_keypair.public_key_bytes,
        channel_id="cid:0000000000000000",
        current_epoch=7,
        lambda_local=[0.25, 0.5, 0.75],
        mode=BEACON_EMISSION_MODE_MAINNET,
    )

    assert envelope is not None
    assert emission_state.last_emit_epoch == 7
    assert emission_state.prev_lambda == [0.25, 0.5, 0.75]
    relay_result = peel_relay_layer(envelope, relay_keypair.private_key)
    terminal_result = open_terminal_layer(
        relay_result,
        terminal_keypair.private_key,
        replay_cache=SpectralBeaconReplayCache(),
    )
    assert terminal_result.beacon.lambda_local != [0.25, 0.5, 0.75]
    assert all(0.0 <= value <= 2.0 for value in terminal_result.beacon.lambda_local)
