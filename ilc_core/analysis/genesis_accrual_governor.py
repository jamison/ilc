# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import Iterable, Mapping, TypedDict

from ilc_core.economic_constants import C_MAX_ILC
from ilc_core.exceptions import GenesisAccrualGovernorError


_DECIMAL_PRECISION = 50
_RATIO_QUANTUM = Decimal("0.000000000001")
THETA_HARD = Decimal("1") / Decimal("20")
with localcontext() as _ctx:
    _ctx.prec = _DECIMAL_PRECISION
    THETA_SOFT = (-Decimal("3")).exp()
GENESIS_ACCRUAL_GOVERNOR_RUNTIME_VERSION = "genesis_accrual_governor_runtime_1575c_fix3c.v0.1"
GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN = (
    "genesis_accrual_governor_decimal_migration_1575c_fix3c.v0.1"
)
CDL_029_AMENDMENT_2_DEPENDENCY = "cdl_029_amendment_2_cmax_denominator_phase_1573aa"
_RATIO_TOLERANCE = 1e-12


class GenesisAccrualGovernorPolicy(TypedDict):
    theta_hard: Decimal
    theta_soft: Decimal
    taper_steepness: Decimal


class GenesisAccrualSignal(TypedDict):
    genesis_cumulative_accrual: Decimal
    total_cumulative_issuance: Decimal


class GenesisAccrualGovernorReport(TypedDict):
    genesis_share_ratio: Decimal
    taper_multiplier: Decimal
    cap_blocked: bool


class GenesisAccrualTrajectoryRow(TypedDict):
    step_index: int
    genesis_cumulative_accrual: Decimal
    total_cumulative_issuance: Decimal
    genesis_share_ratio: Decimal
    taper_multiplier: Decimal
    cap_blocked: bool


DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY: GenesisAccrualGovernorPolicy = {
    "theta_hard": THETA_HARD,
    "theta_soft": THETA_SOFT,
    "taper_steepness": Decimal("40"),
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


def _require_ratio_parameter(value: object, token: str) -> Decimal:
    """Accept exact dimensionless ratio parameters; reject float."""
    if isinstance(value, bool) or isinstance(value, float):
        raise GenesisAccrualGovernorError(token)
    try:
        normalized = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise GenesisAccrualGovernorError(token) from None
    if not normalized.is_finite() or normalized < Decimal("0"):
        raise GenesisAccrualGovernorError(token)
    return normalized


def _sigmoid(value: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = _DECIMAL_PRECISION
        if value >= Decimal("0"):
            exp_value = (-value).exp()
            return Decimal("1") / (Decimal("1") + exp_value)
        exp_value = value.exp()
        return exp_value / (Decimal("1") + exp_value)


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

    if taper_steepness <= Decimal("0"):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_taper_steepness")
    if abs(theta_hard - THETA_HARD) > Decimal(str(_RATIO_TOLERANCE)):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_theta_hard_constant_mismatch")
    if abs(theta_soft - THETA_SOFT) > Decimal(str(_RATIO_TOLERANCE)):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_theta_soft_constant_mismatch")
    if theta_soft > theta_hard + Decimal(str(_RATIO_TOLERANCE)):
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


def compute_genesis_share_ratio(signal: Mapping[str, object]) -> Decimal:
    resolved_signal = validate_genesis_accrual_signal(signal)
    return _compute_genesis_share_ratio_decimal(resolved_signal).quantize(_RATIO_QUANTUM)


def _compute_genesis_share_ratio_decimal(signal: GenesisAccrualSignal) -> Decimal:
    total_issuance = signal["total_cumulative_issuance"]
    if total_issuance == Decimal("0"):
        return Decimal("0")
    return signal["genesis_cumulative_accrual"] / C_MAX_ILC


def compute_taper_multiplier(
    genesis_share_ratio: Decimal | int | str,
    *,
    policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> Decimal:
    if isinstance(genesis_share_ratio, bool) or isinstance(genesis_share_ratio, float):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_genesis_share_ratio")
    try:
        normalized_ratio = (
            genesis_share_ratio
            if isinstance(genesis_share_ratio, Decimal)
            else Decimal(str(genesis_share_ratio))
        )
    except (InvalidOperation, ValueError):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_genesis_share_ratio") from None
    if not normalized_ratio.is_finite() or normalized_ratio < Decimal("0"):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_genesis_share_ratio")

    resolved_policy = validate_genesis_accrual_governor_policy(policy)

    if normalized_ratio >= resolved_policy["theta_hard"]:
        return Decimal("0")

    with localcontext() as ctx:
        ctx.prec = _DECIMAL_PRECISION
        numerator = _sigmoid(
            resolved_policy["taper_steepness"] * (resolved_policy["theta_soft"] - normalized_ratio)
        )
        denominator = _sigmoid(resolved_policy["taper_steepness"] * resolved_policy["theta_soft"])
    if denominator <= Decimal("0"):
        raise GenesisAccrualGovernorError("genesis_accrual_governor_invalid_sigmoid_denominator")

    bounded = max(Decimal("0"), min(Decimal("1"), numerator / denominator))
    return bounded.quantize(_RATIO_QUANTUM)


def evaluate_genesis_accrual_governor(
    signal: Mapping[str, object],
    *,
    policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> GenesisAccrualGovernorReport:
    resolved_policy = validate_genesis_accrual_governor_policy(policy)
    resolved_signal = validate_genesis_accrual_signal(signal)
    raw_ratio_decimal = _compute_genesis_share_ratio_decimal(resolved_signal)
    report_ratio_decimal = raw_ratio_decimal.quantize(_RATIO_QUANTUM)
    taper_multiplier = compute_taper_multiplier(raw_ratio_decimal, policy=resolved_policy)
    cap_blocked = bool(raw_ratio_decimal >= resolved_policy["theta_hard"])

    return {
        "genesis_share_ratio": report_ratio_decimal,
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
    prev_ratio = Decimal("-1")

    for step_index, raw_row in enumerate(cumulative_rows):
        resolved_signal = validate_genesis_accrual_signal(raw_row)
        accrual = resolved_signal["genesis_cumulative_accrual"]
        issuance = resolved_signal["total_cumulative_issuance"]

        if accrual < prev_accrual:
            raise GenesisAccrualGovernorError("genesis_accrual_governor_non_monotonic_accrual")
        if issuance < prev_issuance:
            raise GenesisAccrualGovernorError("genesis_accrual_governor_non_monotonic_issuance")

        ratio = compute_genesis_share_ratio(resolved_signal)
        if ratio < prev_ratio:
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
