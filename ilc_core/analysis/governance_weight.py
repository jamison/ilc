from __future__ import annotations

import math
from typing import Iterable, Mapping, TypedDict

from ilc_core.exceptions import GovernanceWeightError


class GovernanceWeightPolicy(TypedDict):
    inactivity_decay_lambda: float
    genesis_baseline_weight: float
    allow_genesis_bonus: bool


class GovernanceWeightInput(TypedDict):
    agent_id: str
    base_weight: float
    quality_score: float
    inactivity_epochs: int
    is_genesis: bool
    contribution_bonus: float


class GovernanceWeightOutput(TypedDict):
    agent_id: str
    governance_weight: float
    vote_share: float


DEFAULT_GOVERNANCE_WEIGHT_POLICY: GovernanceWeightPolicy = {
    "inactivity_decay_lambda": 0.05,
    "genesis_baseline_weight": 1.0,
    "allow_genesis_bonus": True,
}


def validate_governance_weight_policy(policy: Mapping[str, object]) -> GovernanceWeightPolicy:
    required_keys = {
        "inactivity_decay_lambda",
        "genesis_baseline_weight",
        "allow_genesis_bonus",
    }
    if set(policy.keys()) != required_keys:
        raise GovernanceWeightError("governance_weight_invalid_policy_keys")

    lam = policy["inactivity_decay_lambda"]
    baseline = policy["genesis_baseline_weight"]
    allow_bonus = policy["allow_genesis_bonus"]

    if not isinstance(lam, (int, float)) or lam < 0.0:
        raise GovernanceWeightError("governance_weight_invalid_decay_lambda")
    if not isinstance(baseline, (int, float)) or baseline < 0.0:
        raise GovernanceWeightError("governance_weight_invalid_genesis_baseline")
    if not isinstance(allow_bonus, bool):
        raise GovernanceWeightError("governance_weight_invalid_allow_genesis_bonus")

    return {
        "inactivity_decay_lambda": float(lam),
        "genesis_baseline_weight": float(baseline),
        "allow_genesis_bonus": allow_bonus,
    }


def _compute_non_genesis_weight(
    *,
    base_weight: float,
    quality_score: float,
    inactivity_epochs: int,
    inactivity_decay_lambda: float,
) -> float:
    return base_weight * quality_score * math.exp(-inactivity_decay_lambda * inactivity_epochs)


def _validate_input_row(row: Mapping[str, object]) -> GovernanceWeightInput:
    agent_id = row.get("agent_id")
    base_weight = row.get("base_weight")
    quality_score = row.get("quality_score")
    inactivity_epochs = row.get("inactivity_epochs")
    is_genesis = row.get("is_genesis")
    contribution_bonus = row.get("contribution_bonus", 0.0)

    if not isinstance(agent_id, str) or agent_id == "":
        raise GovernanceWeightError("governance_weight_invalid_agent_id")
    if not isinstance(base_weight, (int, float)) or base_weight < 0.0:
        raise GovernanceWeightError("governance_weight_invalid_base_weight")
    if not isinstance(quality_score, (int, float)) or quality_score < 0.0:
        raise GovernanceWeightError("governance_weight_invalid_quality_score")
    if isinstance(inactivity_epochs, bool) or not isinstance(inactivity_epochs, int) or inactivity_epochs < 0:
        raise GovernanceWeightError("governance_weight_invalid_inactivity_epochs")
    if not isinstance(is_genesis, bool):
        raise GovernanceWeightError("governance_weight_invalid_is_genesis")
    if not isinstance(contribution_bonus, (int, float)) or contribution_bonus < 0.0:
        raise GovernanceWeightError("governance_weight_invalid_contribution_bonus")

    return {
        "agent_id": agent_id,
        "base_weight": float(base_weight),
        "quality_score": float(quality_score),
        "inactivity_epochs": inactivity_epochs,
        "is_genesis": is_genesis,
        "contribution_bonus": float(contribution_bonus),
    }


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

    provisional: list[tuple[str, float]] = []
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
        provisional.append((row["agent_id"], max(0.0, float(weight))))

    total_weight = sum(weight for _, weight in provisional)
    outputs: list[GovernanceWeightOutput] = []
    for agent_id, weight in sorted(provisional, key=lambda item: item[0]):
        vote_share = (weight / total_weight) if total_weight > 0.0 else 0.0
        outputs.append(
            {
                "agent_id": agent_id,
                "governance_weight": weight,
                "vote_share": vote_share,
            }
        )
    return outputs
