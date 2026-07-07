# SPDX-License-Identifier: AGPL-3.0-only
"""H-013 spectral sigma policy boundary.

SIM-BEACON-01 did not validate a differential-privacy sigma. It recorded a
minimum construction floor, a testnet candidate, and a required adversary-model
revision before any privacy-calibrated claim can be made. Genesis authority
separately authorizes provisional mainnet-mode use of the same pinned candidate
without creating a DP calibration claim.
"""

from __future__ import annotations

import math
from typing import Any


SPECTRAL_SIGMA_POLICY_VERSION = "h013_spectral_sigma_policy.v0.1"
# Pending CDL-SIGMA-01 ratification (OBL-046).
MIN_NOISE_SIGMA = 0.005
# Pending CDL-SIGMA-01 ratification (OBL-046).
H013_TESTNET_EMISSION_SIGMA = 0.05
SIGMA_DP_CALIBRATION_VALIDATED = False
SIM_BEACON_01_PRIVACY_TARGET_VALIDATED = SIGMA_DP_CALIBRATION_VALIDATED
SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED = True
SIGMA_POLICY_STATUS = "specified_floor_testnet_candidate_obl_046_open"
H013_SIGMA_POLICY_STATUS = SIGMA_POLICY_STATUS
SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN = (
    "sigma_dp_calibration_not_validated_obl_046_open"
)
# Provisional Genesis authority pending CDL-SIGMA-01 ratification (OBL-046).
# Revocation/replacement path: when OBL-046 closes, either keep the pinned
# candidate only if the adversary model validates it and ratified authority
# flips SIGMA_DP_CALIBRATION_VALIDATED, or set this flag False and replace
# H013_TESTNET_EMISSION_SIGMA with the ratified sigma before public RC.
SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS = True
SIGMA_MAINNET_PROVISIONAL_STATUS = (
    "genesis_authorized_provisional_mainnet_sigma_obl_046_open"
)
SIGMA_MAINNET_PROVISIONAL_TOKEN = (
    "genesis_authorized_provisional_mainnet_sigma_obl_046_open"
)
SIGMA_OBLIGATION_ID = "OBL-046"
SIGMA_PRE_PUBLIC_RC_BLOCKER = True
SIGMA_REVOCATION_PATH = (
    "close_obl_046_with_validated_sigma_or_revoke_genesis_provisional_authority"
)
SIGMA_NO_DP_CLAIM_AT_PUBLIC_RC = True
# CDL-SIGMA-01 ratified Phase 1573e: sigma is a local simulation parameter only.
# ILC makes no differential-privacy or anonymity claim about spectral routing
# at public RC unless CCSS_SPECTRAL_01_NOT_ACTIVATED is cleared and the
# Phase 1574 activation matrix authorizes the claim.
CDLSIGMA01_RATIFICATION_PHASE = "cdl_sigma_01_ratified_phase_1573e"


class SpectralSigmaPolicyError(ValueError):
    """Sigma policy exception with deterministic token semantics."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def normalize_noise_sigma(value: Any) -> float:
    """Normalize a generic H-013 sigma and enforce the construction floor."""

    if (
        not isinstance(value, (float, int))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise SpectralSigmaPolicyError("h013_noise_sigma_invalid", "noise_sigma_invalid")
    normalized = float(value)
    if normalized < MIN_NOISE_SIGMA:
        raise SpectralSigmaPolicyError(
            "h013_noise_sigma_below_floor",
            "noise_sigma_below_floor",
        )
    return normalized


def validate_noise_sigma_for_mode(
    value: Any,
    *,
    mode: str,
    require_privacy_calibrated: bool = False,
) -> float:
    """Validate sigma for an activated H-013 emission mode.

    Testnet and Genesis-authorized provisional mainnet emission are pinned to
    the Phase-939 candidate value. Privacy-calibrated use remains fail-closed
    until the adversary-model revision validates a sigma and a later authority
    updates this policy.
    """

    normalized = normalize_noise_sigma(value)
    if require_privacy_calibrated:
        raise SpectralSigmaPolicyError(
            SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN,
            SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN,
        )
    if mode == "testnet":
        if normalized != H013_TESTNET_EMISSION_SIGMA:
            raise SpectralSigmaPolicyError(
                "h013_noise_sigma_testnet_candidate_mismatch",
                "testnet_sigma_must_match_h013_candidate",
            )
        return normalized
    if mode == "mainnet":
        if not SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS:
            raise SpectralSigmaPolicyError(
                "h013_noise_sigma_mainnet_not_activated",
                "mainnet_sigma_requires_adversary_model_revision",
            )
        if normalized != H013_TESTNET_EMISSION_SIGMA:
            raise SpectralSigmaPolicyError(
                "h013_noise_sigma_mainnet_candidate_mismatch",
                "mainnet_sigma_must_match_genesis_authorized_h013_candidate",
            )
        return normalized
    raise SpectralSigmaPolicyError("h013_noise_sigma_mode_invalid", "sigma_mode_invalid")


def build_sigma_policy_status_record() -> dict[str, Any]:
    """Return the operator-facing H-013 sigma policy status record."""

    return {
        "version": SPECTRAL_SIGMA_POLICY_VERSION,
        "sigma_policy_status": SIGMA_POLICY_STATUS,
        "obl_id": SIGMA_OBLIGATION_ID,
        "pre_public_rc_blocker": SIGMA_PRE_PUBLIC_RC_BLOCKER,
        "min_noise_sigma": MIN_NOISE_SIGMA,
        "h013_testnet_emission_sigma": H013_TESTNET_EMISSION_SIGMA,
        "sigma_dp_calibration_validated": SIGMA_DP_CALIBRATION_VALIDATED,
        "sigma_dp_calibration_not_validated_token": (
            SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN
        ),
        "sigma_mainnet_provisional_authorized_by_genesis": (
            SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS
        ),
        "sigma_mainnet_provisional_status": SIGMA_MAINNET_PROVISIONAL_STATUS,
        "sigma_mainnet_provisional_token": SIGMA_MAINNET_PROVISIONAL_TOKEN,
        "sigma_no_dp_claim_at_public_rc": SIGMA_NO_DP_CLAIM_AT_PUBLIC_RC,
        "cdl_sigma_01_ratification_phase": CDLSIGMA01_RATIFICATION_PHASE,
        "sim_beacon_01_adversary_model_revision_required": (
            SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED
        ),
        "revocation_or_replacement_path": SIGMA_REVOCATION_PATH,
    }


__all__ = [
    "CDLSIGMA01_RATIFICATION_PHASE",
    "H013_SIGMA_POLICY_STATUS",
    "H013_TESTNET_EMISSION_SIGMA",
    "MIN_NOISE_SIGMA",
    "SIGMA_DP_CALIBRATION_NOT_VALIDATED_TOKEN",
    "SIGMA_DP_CALIBRATION_VALIDATED",
    "SIGMA_MAINNET_PROVISIONAL_AUTHORIZED_BY_GENESIS",
    "SIGMA_MAINNET_PROVISIONAL_STATUS",
    "SIGMA_MAINNET_PROVISIONAL_TOKEN",
    "SIGMA_OBLIGATION_ID",
    "SIGMA_NO_DP_CLAIM_AT_PUBLIC_RC",
    "SIGMA_POLICY_STATUS",
    "SIGMA_PRE_PUBLIC_RC_BLOCKER",
    "SIGMA_REVOCATION_PATH",
    "SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED",
    "SIM_BEACON_01_PRIVACY_TARGET_VALIDATED",
    "SPECTRAL_SIGMA_POLICY_VERSION",
    "SpectralSigmaPolicyError",
    "build_sigma_policy_status_record",
    "normalize_noise_sigma",
    "validate_noise_sigma_for_mode",
]
