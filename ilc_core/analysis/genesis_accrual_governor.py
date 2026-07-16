# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping, TypedDict

from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC
from ilc_core.exceptions import GenesisAccrualGovernorError


THETA_HARD = 1.0 / 20.0
THETA_SOFT = math.exp(-3.0)
GENESIS_ACCRUAL_GOVERNOR_RUNTIME_VERSION = "genesis_accrual_governor_runtime_1575c_fix3c.v0.1"
GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN = (
    "genesis_accrual_governor_decimal_migration_1575c_fix3c.v0.1"
)
CDL_029_AMENDMENT_2_DEPENDENCY = "cdl_029_amendment_2_cmax_denominator_phase_1573aa"
_RATIO_TOLERANCE = 1e-12


class GenesisAccrualGovernorPolicy(TypedDict):
    theta_hard: float
    theta_soft: float
    taper_steepness: float


class GenesisAccrualSignal(TypedDict):
    genesis_cumulative_accrual: Decimal
    total_cumulative_issuance: Decimal


class GenesisAccrualGovernorReport(TypedDict):
    genesis_share_ratio: float
    taper_multiplier: float
    cap_blocked: bool


class GenesisAccrualTrajectoryRow(TypedDict):
    step_index: int
    genesis_cumulative_accrual: Decimal
    total_cumulative_issuance: Decimal
    genesis_share_ratio: float
    taper_multiplier: float
    cap_blocked: bool


DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY: GenesisAccrualGovernorPolicy = {
    "theta_hard": THETA_HARD,
    "theta_soft": THETA_SOFT,
    "taper_steepness": 40.0,
}


def _require_monetary_decimal(value: object, token: str) -> Decimal:
    """Accept Decimal or int for ILC monetary amounts; reject float and bool."""
    if isinstance(value, bool) or isinstance(value, float):
        raise GenesisAccrualGovernorError(token)
    if isinstance(value, Decimal):
        normalized = value
    elif isinstance(value, int):
        normalized = Decimal(value)
    else:
        try:
            normalized = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise GenesisAccrualGovernorError(token) from None
    if not normalized.is_finite() or normalized < Decimal("0"):
        raise GenesisAccrualGovernorError(token)
    return normalized


def _require_ratio_parameter(value: object, token: str) -> float:
    """Accept float or int for dimensionless ratio parameters, not money."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GenesisAccrualGovernorError(token)
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0.0:
        raise GenesisAccrualGovernorError(token)
    return normalized


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        exp_value = math.exp(-value)
        return 1.0 / (1.0 + exp_value)
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def validate_genesis_accrual_governor_policy(
    policy: Mapping[str, object],
) -> GenesisAccrualGovernorPolicy:
    required_keys = {"theta_hard", "theta_soft", "taper_steepness"}
    if set(policy.keys()) != required_keys:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_policy_keys")

    theta_hard = _require_ratio_parameter(
        policy.get("theta_hard"),
        "genesis_accrual_governor_invalid_theta_hard",
    )
    theta_soft = _require_ratio_parameter(
        policy.get("theta_soft"),
        "genesis_accrual_governor_invalid_theta_soft",
    )
    taper_steepness = _require_ratio_parameter(
        policy.get("taper_steepness"),
        "genesis_accrual_governor_invalid_taper_steepness",
    )

    if taper_steepness <= 0.0:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_taper_steepness")
    if abs(theta_hard - THETA_HARD) > _RATIO_TOLERANCE:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_theta_hard_constant_mismatch")
    if abs(theta_soft - THETA_SOFT) > _RATIO_TOLERANCE:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_theta_soft_constant_mismatch")
    if theta_soft > theta_hard + _RATIO_TOLERANCE:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_theta_ordering")

    return {
        "theta_hard": theta_hard,
        "theta_soft": theta_soft,
        "taper_steepness": taper_steepness,
    }


def validate_genesis_accrual_signal(
    signal: Mapping[str, object],
) -> GenesisAccrualSignal:
    required_keys = {"genesis_cumulative_accrual", "total_cumulative_issuance"}
    if set(signal.keys()) != required_keys:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_signal_keys")

    genesis_cumulative_accrual = _require_monetary_decimal(
        signal.get("genesis_cumulative_accrual"),
        "genesis_accrual_governor_invalid_genesis_cumulative_accrual",
    )
    total_cumulative_issuance = _require_monetary_decimal(
        signal.get("total_cumulative_issuance"),
        "genesis_accrual_governor_invalid_total_cumulative_issuance",
    )

    if (
        total_cumulative_issuance == Decimal("0")
        and genesis_cumulative_accrual > Decimal("0")
    ):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_inconsistent_zero_issuance")
    if genesis_cumulative_accrual > total_cumulative_issuance:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_accrual_exceeds_issuance")

    return {
        "genesis_cumulative_accrual": genesis_cumulative_accrual,
        "total_cumulative_issuance": total_cumulative_issuance,
    }


def compute_genesis_share_ratio(signal: Mapping[str, object]) -> float:
    resolved_signal = validate_genesis_accrual_signal(signal)
    return float(_compute_genesis_share_ratio_decimal(resolved_signal))


def _compute_genesis_share_ratio_decimal(signal: GenesisAccrualSignal) -> Decimal:
    total_issuance = signal["total_cumulative_issuance"]
    if total_issuance == Decimal("0"):
        return Decimal("0")
    return signal["genesis_cumulative_accrual"] / C_MAX_ILC


def compute_taper_multiplier(
    genesis_share_ratio: float,
    *,
    policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> float:
    if (
        isinstance(genesis_share_ratio, bool)
        or not isinstance(genesis_share_ratio, (int, float))
        or not math.isfinite(float(genesis_share_ratio))
        or float(genesis_share_ratio) < 0.0
    ):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_genesis_share_ratio")

    resolved_policy = validate_genesis_accrual_governor_policy(policy)
    normalized_ratio = float(genesis_share_ratio)

    if normalized_ratio >= resolved_policy["theta_hard"]:
        return 0.0

    numerator = _sigmoid(
        resolved_policy["taper_steepness"] * (resolved_policy["theta_soft"] - normalized_ratio)
    )
    denominator = _sigmoid(resolved_policy["taper_steepness"] * resolved_policy["theta_soft"])
    if denominator <= 0.0:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_sigmoid_denominator")

    return float(max(0.0, min(1.0, numerator / denominator)))


def evaluate_genesis_accrual_governor(
    signal: Mapping[str, object],
    *,
    policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> GenesisAccrualGovernorReport:
    resolved_policy = validate_genesis_accrual_governor_policy(policy)
    resolved_signal = validate_genesis_accrual_signal(signal)
    ratio_decimal = _compute_genesis_share_ratio_decimal(resolved_signal)
    ratio = float(ratio_decimal)
    taper_multiplier = compute_taper_multiplier(ratio, policy=resolved_policy)
    cap_blocked = bool(ratio_decimal >= Decimal(str(resolved_policy["theta_hard"])))

    return {
        "genesis_share_ratio": ratio,
        "taper_multiplier": taper_multiplier,
        "cap_blocked": cap_blocked,
    }


def simulate_genesis_accrual_governor_trajectory(
    cumulative_rows: Iterable[Mapping[str, object]],
    *,
    policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> list[GenesisAccrualTrajectoryRow]:
    validate_genesis_accrual_governor_policy(policy)

    trajectory: list[GenesisAccrualTrajectoryRow] = []
    prev_accrual = Decimal("0")
    prev_issuance = Decimal("0")
    prev_ratio = -1.0

    for step_index, raw_row in enumerate(cumulative_rows):
        resolved_signal = validate_genesis_accrual_signal(raw_row)
        accrual = resolved_signal["genesis_cumulative_accrual"]
        issuance = resolved_signal["total_cumulative_issuance"]

        if accrual < prev_accrual:
            raise GenesisAccrualGovernorError("genesis_accrual_governor_non_monotonic_accrual")
        if issuance < prev_issuance:
            raise GenesisAccrualGovernorError("genesis_accrual_governor_non_monotonic_issuance")

        ratio = compute_genesis_share_ratio(resolved_signal)
        if ratio < prev_ratio - _RATIO_TOLERANCE:
            raise GenesisAccrualGovernorError("genesis_accrual_governor_non_monotonic_ratio")
        governor_row = evaluate_genesis_accrual_governor(resolved_signal, policy=policy)
        trajectory.append(
            {
                "step_index": step_index,
                "genesis_cumulative_accrual": accrual,
                "total_cumulative_issuance": issuance,
                "genesis_share_ratio": governor_row["genesis_share_ratio"],
                "taper_multiplier": governor_row["taper_multiplier"],
                "cap_blocked": governor_row["cap_blocked"],
            }
        )
        prev_accrual = accrual
        prev_issuance = issuance
        prev_ratio = ratio

    return trajectory
