from __future__ import annotations

import math
from typing import Iterable, Mapping, TypedDict

from ilc_core.exceptions import GenesisAccrualGovernorError


THETA_HARD = 1.0 / 20.0
THETA_SOFT = math.exp(-3.0)
_RATIO_TOLERANCE = 1e-12


class GenesisAccrualGovernorPolicy(TypedDict):
    theta_hard: float
    theta_soft: float
    taper_steepness: float


class GenesisAccrualSignal(TypedDict):
    genesis_cumulative_accrual: float
    total_cumulative_issuance: float


class GenesisAccrualGovernorReport(TypedDict):
    genesis_share_ratio: float
    taper_multiplier: float
    cap_blocked: bool


class GenesisAccrualTrajectoryRow(TypedDict):
    step_index: int
    genesis_cumulative_accrual: float
    total_cumulative_issuance: float
    genesis_share_ratio: float
    taper_multiplier: float
    cap_blocked: bool


DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY: GenesisAccrualGovernorPolicy = {
    "theta_hard": THETA_HARD,
    "theta_soft": THETA_SOFT,
    "taper_steepness": 40.0,
}


def _require_finite_non_negative(value: object, token: str) -> float:
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

    theta_hard = _require_finite_non_negative(
        policy.get("theta_hard"),
        "genesis_accrual_governor_invalid_theta_hard",
    )
    theta_soft = _require_finite_non_negative(
        policy.get("theta_soft"),
        "genesis_accrual_governor_invalid_theta_soft",
    )
    taper_steepness = _require_finite_non_negative(
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

    genesis_cumulative_accrual = _require_finite_non_negative(
        signal.get("genesis_cumulative_accrual"),
        "genesis_accrual_governor_invalid_genesis_cumulative_accrual",
    )
    total_cumulative_issuance = _require_finite_non_negative(
        signal.get("total_cumulative_issuance"),
        "genesis_accrual_governor_invalid_total_cumulative_issuance",
    )

    if (
        total_cumulative_issuance == 0.0
        and genesis_cumulative_accrual > 0.0
    ):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_inconsistent_zero_issuance")
    if genesis_cumulative_accrual > total_cumulative_issuance + _RATIO_TOLERANCE:
        raise GenesisAccrualGovernorError("genesis_accrual_governor_accrual_exceeds_issuance")

    return {
        "genesis_cumulative_accrual": genesis_cumulative_accrual,
        "total_cumulative_issuance": total_cumulative_issuance,
    }


def compute_genesis_share_ratio(signal: Mapping[str, object]) -> float:
    resolved_signal = validate_genesis_accrual_signal(signal)
    total_issuance = resolved_signal["total_cumulative_issuance"]
    if total_issuance == 0.0:
        return 0.0
    return resolved_signal["genesis_cumulative_accrual"] / total_issuance


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

    if normalized_ratio >= resolved_policy["theta_hard"] - _RATIO_TOLERANCE:
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
    ratio = compute_genesis_share_ratio(signal)
    taper_multiplier = compute_taper_multiplier(ratio, policy=resolved_policy)
    cap_blocked = bool(ratio >= resolved_policy["theta_hard"] - _RATIO_TOLERANCE)

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
    prev_accrual = 0.0
    prev_issuance = 0.0
    prev_ratio = -1.0

    for step_index, raw_row in enumerate(cumulative_rows):
        resolved_signal = validate_genesis_accrual_signal(raw_row)
        accrual = resolved_signal["genesis_cumulative_accrual"]
        issuance = resolved_signal["total_cumulative_issuance"]

        if accrual < prev_accrual - _RATIO_TOLERANCE:
            raise GenesisAccrualGovernorError("genesis_accrual_governor_non_monotonic_accrual")
        if issuance < prev_issuance - _RATIO_TOLERANCE:
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
