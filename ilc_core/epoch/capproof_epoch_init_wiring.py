# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1607 CapProof epoch initialization wiring.

NOT ACTIVATED: CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED = True.
Activation requires a later guard-clear phase after CDL-115 ratification.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, localcontext

from ilc_core.capproof.capability_vector import CapabilityVector
from ilc_core.capproof.multiplier import (
    CAPPROOF_MULTIPLIER_BASELINE,
    CAPPROOF_MULTIPLIER_MAX,
    CAPPROOF_MULTIPLIER_MIN,
    compute_capproof_multiplier,
)
from ilc_core.capproof.probe_runner import CAPPROOF_V1_NO_ILC_MINT
from ilc_core.capproof import probe_runner

CAPPROOF_EPOCH_INIT_RUNTIME_VERSION = "capproof_epoch_init_wiring_phase_1607.v0.1"
CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED = True
CAPPROOF_EPOCH_INIT_NOT_ACTIVATED = CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED
CAPPROOF_EPOCH_GUARD_TOKEN = "capproof_epoch_wiring_not_activated_phase_1607"
CAPPROOF_V1_NO_ILC_MINT_WIRING_CONFIRMED = CAPPROOF_V1_NO_ILC_MINT

CAPPROOF_BAND_FLOOR = CAPPROOF_MULTIPLIER_MIN
CAPPROOF_BAND_CEIL = CAPPROOF_MULTIPLIER_MAX
CAPPROOF_BAND_NEUTRAL = CAPPROOF_MULTIPLIER_BASELINE

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_UNIT_ZERO = Decimal("0")
_UNIT_ONE = Decimal("1")
_BAND_WIDTH = CAPPROOF_BAND_CEIL - CAPPROOF_BAND_FLOOR


class CapProofEpochWiringError(ValueError):
    """Stable-token error for Phase 1607 CapProof epoch wiring."""

    def __init__(self, token: str, message: str = "") -> None:
        super().__init__(message or token)
        self.token = token


@dataclass(frozen=True)
class CapProofEpochInitResult:
    """Output of one agent's CapProof epoch-init wiring run."""

    agent_id: str
    epoch: int
    protocol_executed: bool
    potential_updated: Decimal
    band_multiplier: Decimal
    base_ecu_amount: Decimal
    cap_adjusted_base_ecu_amount: Decimal
    conservation_check_passed: bool
    epoch_seal_token: str
    det_pass: bool
    runtime_version: str = CAPPROOF_EPOCH_INIT_RUNTIME_VERSION
    activation_guard: str = CAPPROOF_EPOCH_GUARD_TOKEN

    def __post_init__(self) -> None:
        _require_agent_id(self.agent_id)
        _require_epoch(self.epoch)
        _require_bool(self.protocol_executed, "capproof_wiring_protocol_executed_must_be_bool")
        _require_bool(
            self.conservation_check_passed,
            "capproof_wiring_conservation_check_must_be_bool",
        )
        _require_bool(self.det_pass, "capproof_wiring_det_pass_must_be_bool")
        _require_decimal(self.potential_updated, "capproof_wiring_potential")
        _require_decimal(self.band_multiplier, "capproof_wiring_band_multiplier")
        _require_decimal(self.base_ecu_amount, "capproof_wiring_base_ecu_amount")
        _require_decimal(
            self.cap_adjusted_base_ecu_amount,
            "capproof_wiring_cap_adjusted_base_ecu_amount",
        )
        if not (_UNIT_ZERO <= self.potential_updated <= _UNIT_ONE):
            raise CapProofEpochWiringError("capproof_wiring_potential_out_of_unit_interval")
        if not (CAPPROOF_BAND_FLOOR <= self.band_multiplier <= CAPPROOF_BAND_CEIL):
            raise CapProofEpochWiringError("capproof_wiring_band_multiplier_out_of_range")
        if self.base_ecu_amount < _UNIT_ZERO:
            raise CapProofEpochWiringError("capproof_wiring_base_ecu_amount_negative")
        if self.cap_adjusted_base_ecu_amount < _UNIT_ZERO:
            raise CapProofEpochWiringError("capproof_wiring_cap_adjusted_base_ecu_amount_negative")
        if not isinstance(self.epoch_seal_token, str) or not self.epoch_seal_token:
            raise CapProofEpochWiringError("capproof_wiring_epoch_seal_token_required")
        if self.runtime_version != CAPPROOF_EPOCH_INIT_RUNTIME_VERSION:
            raise CapProofEpochWiringError("capproof_wiring_runtime_version_mismatch")
        if self.activation_guard != CAPPROOF_EPOCH_GUARD_TOKEN:
            raise CapProofEpochWiringError("capproof_wiring_activation_guard_token_mismatch")
        if self.conservation_check_passed:
            step5_conservation_check(
                self.base_ecu_amount,
                self.cap_adjusted_base_ecu_amount,
                self.band_multiplier,
            )
        elif self.protocol_executed:
            raise CapProofEpochWiringError(
                "capproof_wiring_executed_result_requires_conservation_pass"
            )


def step1_submit_probe(cv: CapabilityVector, epoch: int) -> str:
    """Step 1: validate that the capability vector belongs to this epoch."""

    _require_cv(cv)
    normalized_epoch = _require_epoch(epoch)
    if cv.epoch != normalized_epoch:
        raise CapProofEpochWiringError("capproof_cv_epoch_mismatch")
    return f"capproof_probe_submitted_epoch_{normalized_epoch}"


def step2_verify_probe(cv: CapabilityVector) -> bool:
    """Step 2: verify the capability-vector shape without adding eligibility rules."""

    _require_cv(cv)
    if (
        not CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED
        and not probe_runner.CAPPROOF_DETERMINISM_PROBE_PRODUCTION_ACTIVATED
    ):
        raise CapProofEpochWiringError("capproof_determinism_probe_not_production_ready")
    return True


def step3_update_potential(cv: CapabilityVector) -> Decimal:
    """Step 3: derive TrustVector potential from the Phase 1606 bounded band."""

    _require_cv(cv)
    if cv.det_pass is False:
        # CDL-115-DELIBERATION-Q3: det_pass=False behavior remains open.
        return _UNIT_ZERO
    multiplier = compute_capproof_multiplier(cv)
    return _clamp_unit((multiplier - CAPPROOF_BAND_FLOOR) / _BAND_WIDTH)


def step4_compute_band_multiplier(cv: CapabilityVector) -> Decimal:
    """Step 4: return the ECU band.

    The band_multiplier replaces, and does NOT compound, other ECU multipliers.
    CapProof v1 modulates ECU band only; it does not mint ILC.
    """

    _require_cv(cv)
    if not CAPPROOF_V1_NO_ILC_MINT:
        raise CapProofEpochWiringError("capproof_no_ilc_mint_invariant_violated")
    multiplier = compute_capproof_multiplier(cv)
    if not (CAPPROOF_BAND_FLOOR <= multiplier <= CAPPROOF_BAND_CEIL):
        raise CapProofEpochWiringError("capproof_wiring_band_multiplier_out_of_range")
    return multiplier


def step5_conservation_check(
    base_ecu_amount: Decimal,
    cap_adjusted_base_ecu_amount: Decimal,
    band_multiplier: Decimal,
) -> bool:
    """Step 5: verify adjusted base ECU amount against high-precision base * band."""

    base = _require_decimal(base_ecu_amount, "capproof_wiring_base_ecu_amount")
    adjusted = _require_decimal(
        cap_adjusted_base_ecu_amount,
        "capproof_wiring_cap_adjusted_base_ecu_amount",
    )
    band = _require_decimal(band_multiplier, "capproof_wiring_band_multiplier")
    if base < _UNIT_ZERO:
        raise CapProofEpochWiringError("capproof_wiring_base_ecu_amount_negative")
    if not (CAPPROOF_BAND_FLOOR <= band <= CAPPROOF_BAND_CEIL):
        raise CapProofEpochWiringError("capproof_conservation_check_failed_band_out_of_range")
    if adjusted != _multiply_decimal(base, band):
        raise CapProofEpochWiringError("capproof_conservation_check_failed_amount_mismatch")
    return True


def step6_seal_epoch(
    agent_id: str,
    epoch: int,
    band_multiplier: Decimal,
    cap_adjusted_base_ecu_amount: Decimal,
) -> str:
    """Step 6: produce a deterministic audit seal for this CapProof result."""

    normalized_agent_id = _require_agent_id(agent_id)
    normalized_epoch = _require_epoch(epoch)
    band = _require_decimal(band_multiplier, "capproof_wiring_band_multiplier")
    adjusted = _require_decimal(
        cap_adjusted_base_ecu_amount,
        "capproof_wiring_cap_adjusted_base_ecu_amount",
    )
    payload = json.dumps(
        {
            "agent_id": normalized_agent_id,
            "band_multiplier": _decimal_text(band),
            "cap_adjusted_base_ecu_amount": _decimal_text(adjusted),
            "epoch": normalized_epoch,
            "runtime_version": CAPPROOF_EPOCH_INIT_RUNTIME_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"capproof_epoch_seal_{normalized_epoch}_{digest[:16]}"


def process_capproof_epoch_init(
    cv: CapabilityVector,
    epoch: int,
    base_ecu_amount: Decimal,
) -> CapProofEpochInitResult:
    """Run the guarded CapProof epoch-init path for one capability vector."""

    _require_cv(cv)
    normalized_epoch = _require_epoch(epoch)
    base = _require_decimal(base_ecu_amount, "capproof_wiring_base_ecu_amount")
    if base < _UNIT_ZERO:
        raise CapProofEpochWiringError("capproof_wiring_base_ecu_amount_negative")
    if cv.epoch != normalized_epoch:
        raise CapProofEpochWiringError("capproof_cv_epoch_mismatch")

    if CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED:
        return CapProofEpochInitResult(
            agent_id=cv.agent_id,
            epoch=normalized_epoch,
            protocol_executed=False,
            potential_updated=_UNIT_ZERO,
            band_multiplier=CAPPROOF_BAND_NEUTRAL,
            base_ecu_amount=base,
            cap_adjusted_base_ecu_amount=base,
            conservation_check_passed=True,
            epoch_seal_token=f"capproof_epoch_wiring_bypassed_{normalized_epoch}",
            det_pass=cv.det_pass,
        )

    step1_submit_probe(cv, normalized_epoch)
    step2_verify_probe(cv)
    potential = step3_update_potential(cv)
    band_multiplier = step4_compute_band_multiplier(cv)
    adjusted = _multiply_decimal(base, band_multiplier)
    conservation_ok = step5_conservation_check(base, adjusted, band_multiplier)
    seal_token = step6_seal_epoch(cv.agent_id, normalized_epoch, band_multiplier, adjusted)
    return CapProofEpochInitResult(
        agent_id=cv.agent_id,
        epoch=normalized_epoch,
        protocol_executed=True,
        potential_updated=potential,
        band_multiplier=band_multiplier,
        base_ecu_amount=base,
        cap_adjusted_base_ecu_amount=adjusted,
        conservation_check_passed=conservation_ok,
        epoch_seal_token=seal_token,
        det_pass=cv.det_pass,
    )


def _require_cv(cv: CapabilityVector) -> CapabilityVector:
    if not isinstance(cv, CapabilityVector):
        raise CapProofEpochWiringError("capproof_wiring_capability_vector_required")
    return cv


def _require_agent_id(agent_id: str) -> str:
    if not isinstance(agent_id, str) or _AGENT_ID_RE.fullmatch(agent_id) is None:
        raise CapProofEpochWiringError("capproof_wiring_agent_id_must_be_96_char_hex")
    return agent_id


def _require_epoch(epoch: int) -> int:
    if not isinstance(epoch, int) or type(epoch) is bool or epoch < 0:
        raise CapProofEpochWiringError("capproof_wiring_epoch_must_be_nonnegative_int")
    return epoch


def _require_bool(value: bool, token: str) -> bool:
    if type(value) is not bool:
        raise CapProofEpochWiringError(token)
    return value


def _require_decimal(value: Decimal, token_prefix: str) -> Decimal:
    if not isinstance(value, Decimal):
        raise CapProofEpochWiringError(f"{token_prefix}_must_be_decimal")
    if not value.is_finite():
        raise CapProofEpochWiringError(f"{token_prefix}_must_be_finite")
    return value


def _clamp_unit(value: Decimal) -> Decimal:
    normalized = _require_decimal(value, "capproof_wiring_unit_value")
    if normalized < _UNIT_ZERO:
        return _UNIT_ZERO
    if normalized > _UNIT_ONE:
        return _UNIT_ONE
    return normalized


def _multiply_decimal(left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 50
        return left * right


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")
