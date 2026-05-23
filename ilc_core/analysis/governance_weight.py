# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_DOWN, localcontext
from typing import Iterable, Mapping, TypeAlias, TypedDict

from ilc_core.exceptions import GovernanceWeightError


ExactNumberish: TypeAlias = Decimal | int | str

GOVERNANCE_WEIGHT_RUNTIME_VERSION = "governance_weight_decimal_runtime_1357.v0.1"
CDL_013_DEPENDENCY = "cdl_013_decay_non_genesis_only_ratified_phase_215.v0.1"
CDL_013_DEPENDENCY_TOKEN = "CDL_013_DEPENDENCY_token_phase_1357"
GOVERNANCE_WEIGHT_NO_FLOAT_ARITHMETIC_TOKEN = (
    "governance_weight_no_float_arithmetic_phase_1357"
)
GOVERNANCE_WEIGHT_VOTE_SHARE_PRECISION_GAP_CLOSED_TOKEN = (
    "governance_weight_vote_share_precision_gap_closed_phase_1357"
)

ZERO = Decimal("0")
ONE = Decimal("1")
VOTE_SHARE_QUANTUM = Decimal("0.0000000000000000000000000001")
QUALITY_SCORE_MAX = ONE


class GovernanceWeightPolicy(TypedDict):
    inactivity_decay_lambda: Decimal
    genesis_baseline_weight: Decimal
    allow_genesis_bonus: bool


class GovernanceWeightInput(TypedDict):
    agent_id: str
    base_weight: Decimal
    quality_score: Decimal
    inactivity_epochs: int
    is_genesis: bool
    contribution_bonus: Decimal


class GovernanceWeightOutput(TypedDict):
    agent_id: str
    governance_weight: Decimal
    vote_share: Decimal


DEFAULT_GOVERNANCE_WEIGHT_POLICY: GovernanceWeightPolicy = {
    "inactivity_decay_lambda": Decimal("0.05"),
    "genesis_baseline_weight": Decimal("1"),
    "allow_genesis_bonus": True,
}


def _to_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise GovernanceWeightError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise GovernanceWeightError(token) from exc
    else:
        raise GovernanceWeightError(token)
    if not number.is_finite():
        raise GovernanceWeightError("invalid_amount_non_finite")
    return ZERO if number.is_signed() and number == ZERO else number


def _to_non_negative_decimal(value: object, token: str) -> Decimal:
    number = _to_decimal(value, token)
    if number < ZERO:
        raise GovernanceWeightError(token)
    return number


def _to_unit_interval_decimal(value: object, token: str) -> Decimal:
    number = _to_non_negative_decimal(value, token)
    if number > QUALITY_SCORE_MAX:
        raise GovernanceWeightError(token)
    return number


def validate_governance_weight_policy(policy: Mapping[str, object]) -> GovernanceWeightPolicy:
    required_keys = {
        "inactivity_decay_lambda",
        "genesis_baseline_weight",
        "allow_genesis_bonus",
    }
    if set(policy.keys()) != required_keys:
        raise GovernanceWeightError("governance_weight_invalid_policy_keys")

    lam = _to_non_negative_decimal(
        policy["inactivity_decay_lambda"],
        "governance_weight_invalid_decay_lambda",
    )
    baseline = _to_non_negative_decimal(
        policy["genesis_baseline_weight"],
        "governance_weight_invalid_genesis_baseline",
    )
    allow_bonus = policy["allow_genesis_bonus"]

    if not isinstance(allow_bonus, bool):
        raise GovernanceWeightError("governance_weight_invalid_allow_genesis_bonus")

    return {
        "inactivity_decay_lambda": lam,
        "genesis_baseline_weight": baseline,
        "allow_genesis_bonus": allow_bonus,
    }


def _compute_non_genesis_weight(
    *,
    base_weight: Decimal,
    quality_score: Decimal,
    inactivity_epochs: int,
    inactivity_decay_lambda: Decimal,
) -> Decimal:
    # CDL-013 ratifies decay-non-genesis-only; Decimal exp preserves the formula
    # without reintroducing binary rounding into governance weight.
    with localcontext() as ctx:
        ctx.prec = 50
        decay_multiplier = (-(inactivity_decay_lambda * Decimal(inactivity_epochs))).exp()
    return base_weight * quality_score * decay_multiplier


def _validate_input_row(row: Mapping[str, object]) -> GovernanceWeightInput:
    agent_id = row.get("agent_id")
    base_weight = row.get("base_weight")
    quality_score = row.get("quality_score")
    inactivity_epochs = row.get("inactivity_epochs")
    is_genesis = row.get("is_genesis")
    contribution_bonus = row.get("contribution_bonus", ZERO)

    if not isinstance(agent_id, str) or agent_id == "":
        raise GovernanceWeightError("governance_weight_invalid_agent_id")
    if isinstance(inactivity_epochs, bool) or not isinstance(inactivity_epochs, int) or inactivity_epochs < 0:
        raise GovernanceWeightError("governance_weight_invalid_inactivity_epochs")
    if not isinstance(is_genesis, bool):
        raise GovernanceWeightError("governance_weight_invalid_is_genesis")

    return {
        "agent_id": agent_id,
        "base_weight": _to_non_negative_decimal(
            base_weight,
            "governance_weight_invalid_base_weight",
        ),
        "quality_score": _to_unit_interval_decimal(
            quality_score,
            "governance_weight_invalid_quality_score",
        ),
        "inactivity_epochs": inactivity_epochs,
        "is_genesis": is_genesis,
        "contribution_bonus": _to_non_negative_decimal(
            contribution_bonus,
            "governance_weight_invalid_contribution_bonus",
        ),
    }


def _vote_shares(provisional: list[tuple[str, Decimal]]) -> dict[str, Decimal]:
    total_weight = sum((weight for _, weight in provisional), ZERO)
    if total_weight == ZERO:
        return {agent_id: ZERO for agent_id, _ in provisional}

    shares: dict[str, Decimal] = {}
    running_share = ZERO
    ordered = sorted(provisional, key=lambda item: item[0])
    for agent_id, weight in ordered[:-1]:
        with localcontext() as ctx:
            ctx.prec = 50
            share = (weight / total_weight).quantize(
                VOTE_SHARE_QUANTUM,
                rounding=ROUND_DOWN,
            )
        shares[agent_id] = share
        running_share += share
    shares[ordered[-1][0]] = ONE - running_share
    return shares


def compute_governance_weights(
    inputs: Iterable[Mapping[str, object]],
    *,
    policy: Mapping[str, object] = DEFAULT_GOVERNANCE_WEIGHT_POLICY,
) -> list[GovernanceWeightOutput]:
    resolved_policy = validate_governance_weight_policy(policy)

    rows: list[GovernanceWeightInput] = []
    seen_ids: set[str] = set()
    for raw_row in inputs:
        row = _validate_input_row(raw_row)
        if row["agent_id"] in seen_ids:
            raise GovernanceWeightError("governance_weight_duplicate_agent_id")
        seen_ids.add(row["agent_id"])
        rows.append(row)

    provisional: list[tuple[str, Decimal]] = []
    for row in rows:
        if row["is_genesis"]:
            weight = resolved_policy["genesis_baseline_weight"]
            if resolved_policy["allow_genesis_bonus"]:
                weight += row["contribution_bonus"]
        else:
            weight = _compute_non_genesis_weight(
                base_weight=row["base_weight"],
                quality_score=row["quality_score"],
                inactivity_epochs=row["inactivity_epochs"],
                inactivity_decay_lambda=resolved_policy["inactivity_decay_lambda"],
            )
        provisional.append((row["agent_id"], max(ZERO, weight)))

    shares = _vote_shares(provisional)
    return [
        {
            "agent_id": agent_id,
            "governance_weight": weight,
            "vote_share": shares[agent_id],
        }
        for agent_id, weight in sorted(provisional, key=lambda item: item[0])
    ]
