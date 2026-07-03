from __future__ import annotations

import pytest

from ilc_core.analysis.spectral_utils import add_noise
from ilc_core.network.d2d.spectral_beacon import (
    BEACON_EMISSION_MODE_MAINNET,
    BEACON_EMISSION_MODE_TESTNET,
)
from ilc_core.network.d2d.spectral_sigma_policy import (
    H013_SIGMA_POLICY_STATUS,
    H013_TESTNET_EMISSION_SIGMA,
    MIN_NOISE_SIGMA,
    SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN,
    SIGMA_DP_CALIBRATION_VALIDATED,
    SIGMA_POLICY_STATUS,
    SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED,
    SIM_BEACON_01_PRIVACY_TARGET_VALIDATED,
    SpectralSigmaPolicyError,
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
    assert node_startup_runtime.H013_SIGMA_ADVERSARY_MODEL_REVISION_REQUIRED is True


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


def test_h013_mainnet_sigma_fails_until_adversary_model_revision() -> None:
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA,
            mode=BEACON_EMISSION_MODE_MAINNET,
        )
    assert exc.value.token == "h013_noise_sigma_mainnet_not_activated"


def test_h013_privacy_calibrated_sigma_request_fails_closed() -> None:
    with pytest.raises(SpectralSigmaPolicyError) as exc:
        validate_noise_sigma_for_mode(
            H013_TESTNET_EMISSION_SIGMA,
            mode=BEACON_EMISSION_MODE_TESTNET,
            require_privacy_calibrated=True,
        )
    assert exc.value.token == SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN
    assert str(exc.value) == SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN


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
