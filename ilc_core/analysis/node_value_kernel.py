# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Mapping, TypedDict

from ilc_core.analysis.freshness_gate import DEFAULT_FRESHNESS_GATE_POLICY
from ilc_core.analysis.path_lift_counterfactual import (
    build_normalized_path_lift_by_node,
    compute_path_lift_counterfactual,
)
from ilc_core.analysis.node_value_input_canon import NodeValueInputEvent
from ilc_core.analysis.reuse_diversity_invariants import DEFAULT_REUSE_DIVERSITY_POLICY
from ilc_core.exceptions import NodeValueKernelError


ZERO = Decimal("0")
ONE = Decimal("1")
DECIMAL_EPSILON = Decimal("0.000000001")
MIN_REFUTATION_SAFE_FLOOR = Decimal("0.8333333343333333333333333333")


class EwWeights(TypedDict):
    reuse: Decimal
    contradiction_resilience: Decimal
    validation_integrity: Decimal
    path_uplift: Decimal


class NodeEvidenceVector(TypedDict):
    node_id: str
    reuse_count: Decimal
    claim_net_stake: Decimal
    refutation_stake_against: Decimal
    unique_agents_using: Decimal
    max_agent_reuse_share: Decimal
    usage_window: Decimal
    age_epochs: Decimal
    is_genesis: bool
    freshness_gate: Decimal


class NodeScoreVector(TypedDict):
    node_id: str
    reuse_component: Decimal
    contradiction_component: Decimal
    validation_component: Decimal
    path_component: Decimal
    reuse_diversity_multiplier: Decimal
    epistemic_weight: Decimal
    freshness_gate: Decimal
    utility_flow: Decimal


DEFAULT_EW_WEIGHTS: EwWeights = {
    "reuse": Decimal("0.35"),
    "contradiction_resilience": Decimal("0.25"),
    "validation_integrity": Decimal("0.20"),
    "path_uplift": Decimal("0.20"),
}


def _decimal_from_value(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise NodeValueKernelError(token)
    try:
        out = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise NodeValueKernelError(token) from None
    if not out.is_finite():
        raise NodeValueKernelError(token)
    return out


def _non_negative_decimal(value: object, token: str) -> Decimal:
    out = _decimal_from_value(value, token)
    if out < ZERO:
        raise NodeValueKernelError(token)
    return out


def _positive_decimal(value: object, token: str) -> Decimal:
    out = _non_negative_decimal(value, token)
    if out <= ZERO:
        raise NodeValueKernelError(token)
    return out


def _clamp(value: Decimal, lower: Decimal = ZERO, upper: Decimal = ONE) -> Decimal:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def validate_ew_weights(weights: Mapping[str, object]) -> EwWeights:
    expected_keys = set(DEFAULT_EW_WEIGHTS.keys())
    got_keys = set(weights.keys())
    if got_keys != expected_keys:
        raise NodeValueKernelError("node_value_kernel_invalid_weight_keys")

    normalized: EwWeights = {
        "reuse": _decimal_from_value(weights["reuse"], "node_value_kernel_invalid_weight"),
        "contradiction_resilience": _decimal_from_value(
            weights["contradiction_resilience"],
            "node_value_kernel_invalid_weight",
        ),
        "validation_integrity": _decimal_from_value(
            weights["validation_integrity"],
            "node_value_kernel_invalid_weight",
        ),
        "path_uplift": _decimal_from_value(weights["path_uplift"], "node_value_kernel_invalid_weight"),
    }
    if any(value < ZERO for value in normalized.values()):
        raise NodeValueKernelError("node_value_kernel_negative_weight")

    total = sum(normalized.values(), ZERO)
    if abs(total - ONE) > DECIMAL_EPSILON:
        raise NodeValueKernelError("node_value_kernel_weight_sum_not_one")

    return normalized


def _reuse_component(reuse_count: Decimal) -> Decimal:
    return _clamp(reuse_count / Decimal("5"))


def _contradiction_component(
    claim_net_stake: Decimal,
    refutation_stake_against: Decimal,
) -> Decimal:
    base = max(ONE, abs(claim_net_stake))
    return _clamp((claim_net_stake - refutation_stake_against) / base)


def _validation_component(unique_agents_using: Decimal) -> Decimal:
    return _clamp(unique_agents_using / Decimal("3"))


def _legacy_path_component(reuse_count: Decimal) -> Decimal:
    return _clamp(reuse_count / Decimal("4"))


def _resolve_freshness_gate(
    *,
    age_epochs: Decimal,
    is_genesis: bool,
    policy: Mapping[str, object],
) -> Decimal:
    if set(policy.keys()) != {"decay_lambda", "freshness_floor", "genesis_exempt"}:
        raise NodeValueKernelError("freshness_gate_invalid_policy_keys")

    decay_lambda = _non_negative_decimal(policy["decay_lambda"], "freshness_gate_invalid_decay_lambda")
    freshness_floor = _positive_decimal(policy["freshness_floor"], "freshness_gate_invalid_freshness_floor")
    if freshness_floor > ONE:
        raise NodeValueKernelError("freshness_gate_invalid_freshness_floor")
    if freshness_floor < MIN_REFUTATION_SAFE_FLOOR:
        raise NodeValueKernelError("freshness_gate_floor_below_refutation_safety")
    genesis_exempt = policy["genesis_exempt"]
    if not isinstance(genesis_exempt, bool):
        raise NodeValueKernelError("freshness_gate_invalid_genesis_exempt")

    if genesis_exempt and is_genesis:
        return ONE

    raw_decay = (ZERO - decay_lambda * age_epochs).exp()
    return max(freshness_floor, min(ONE, raw_decay))


def _resolve_reuse_diversity_multiplier(
    *,
    reuse_count: Decimal,
    distinct_agent_count: Decimal,
    max_agent_reuse_share: Decimal,
    policy: Mapping[str, object],
) -> Decimal:
    if set(policy.keys()) != {
        "min_distinct_agents",
        "max_single_agent_share",
        "penalty_floor",
    }:
        raise NodeValueKernelError("reuse_diversity_invalid_policy_keys")

    min_distinct_agents = policy["min_distinct_agents"]
    if (
        isinstance(min_distinct_agents, bool)
        or not isinstance(min_distinct_agents, int)
        or min_distinct_agents < 1
    ):
        raise NodeValueKernelError("reuse_diversity_invalid_min_distinct_agents")

    max_single_agent_share = _positive_decimal(
        policy["max_single_agent_share"],
        "reuse_diversity_invalid_max_single_agent_share",
    )
    if max_single_agent_share > ONE:
        raise NodeValueKernelError("reuse_diversity_invalid_max_single_agent_share")

    penalty_floor = _non_negative_decimal(
        policy["penalty_floor"],
        "reuse_diversity_invalid_penalty_floor",
    )
    if penalty_floor > ONE:
        raise NodeValueKernelError("reuse_diversity_invalid_penalty_floor")
    if penalty_floor < MIN_REFUTATION_SAFE_FLOOR:
        raise NodeValueKernelError("reuse_diversity_penalty_floor_below_refutation_safety")

    if reuse_count > ZERO and distinct_agent_count <= ZERO:
        raise NodeValueKernelError("reuse_diversity_missing_provenance")
    if reuse_count > ZERO and distinct_agent_count > reuse_count + DECIMAL_EPSILON:
        raise NodeValueKernelError("reuse_diversity_inconsistent_distinct_and_reuse")
    if reuse_count <= ZERO and distinct_agent_count > ZERO:
        raise NodeValueKernelError("reuse_diversity_inconsistent_distinct_and_reuse")
    if reuse_count <= ZERO and max_agent_reuse_share > ZERO:
        raise NodeValueKernelError("reuse_diversity_inconsistent_distinct_and_reuse")

    if reuse_count <= ONE:
        return ONE

    distinct_ratio = min(
        ONE,
        distinct_agent_count / Decimal(min_distinct_agents),
    )
    if max_agent_reuse_share <= max_single_agent_share:
        concentration_factor = ONE
    else:
        denominator = max(DECIMAL_EPSILON, ONE - max_single_agent_share)
        overflow = (max_agent_reuse_share - max_single_agent_share) / denominator
        concentration_factor = max(ZERO, ONE - overflow)

    raw_multiplier = distinct_ratio * concentration_factor
    return max(penalty_floor, min(ONE, raw_multiplier))


def compute_epistemic_weight(
    evidence: NodeEvidenceVector,
    *,
    weights: Mapping[str, object] = DEFAULT_EW_WEIGHTS,
    path_lift_score: object | None = None,
    reuse_diversity_multiplier: object = ONE,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    ew_weights = validate_ew_weights(weights)

    reuse_component = _clamp(
        _reuse_component(_non_negative_decimal(evidence["reuse_count"], "node_value_kernel_invalid_reuse_count"))
        * _non_negative_decimal(
            reuse_diversity_multiplier,
            "node_value_kernel_invalid_reuse_diversity_multiplier",
        )
    )
    contradiction_component = _contradiction_component(
        _decimal_from_value(evidence["claim_net_stake"], "node_value_kernel_invalid_claim_net_stake"),
        _non_negative_decimal(
            evidence["refutation_stake_against"],
            "node_value_kernel_invalid_refutation_stake_against",
        ),
    )
    validation_component = _validation_component(
        _non_negative_decimal(
            evidence["unique_agents_using"],
            "node_value_kernel_invalid_unique_agents_using",
        )
    )
    if path_lift_score is None:
        path_component = _legacy_path_component(
            _non_negative_decimal(evidence["reuse_count"], "node_value_kernel_invalid_reuse_count")
        )
    else:
        path_component = _clamp(
            _non_negative_decimal(path_lift_score, "node_value_kernel_invalid_path_lift_score")
        )

    epistemic_weight = (
        ew_weights["reuse"] * reuse_component
        + ew_weights["contradiction_resilience"] * contradiction_component
        + ew_weights["validation_integrity"] * validation_component
        + ew_weights["path_uplift"] * path_component
    )
    return (
        reuse_component,
        contradiction_component,
        validation_component,
        path_component,
        epistemic_weight,
    )


def compute_utility_flow(
    epistemic_weight: object,
    usage_window: object,
    freshness_gate: object,
) -> Decimal:
    resolved_weight = _non_negative_decimal(epistemic_weight, "node_value_kernel_invalid_epistemic_weight")
    resolved_usage = _non_negative_decimal(usage_window, "node_value_kernel_negative_usage_window")
    resolved_freshness = _non_negative_decimal(freshness_gate, "node_value_kernel_invalid_freshness_gate")
    if resolved_freshness > ONE:
        raise NodeValueKernelError("node_value_kernel_invalid_freshness_gate")
    return resolved_weight * resolved_usage * resolved_freshness


def _build_default_node_evidence_row(node_id: str) -> NodeEvidenceVector:
    return {
        "node_id": node_id,
        "reuse_count": ZERO,
        "claim_net_stake": ZERO,
        "refutation_stake_against": ZERO,
        "unique_agents_using": ZERO,
        "max_agent_reuse_share": ZERO,
        "usage_window": ONE,
        "age_epochs": ZERO,
        "is_genesis": False,
        "freshness_gate": ONE,
    }


def _read_optional_age_epochs(payload: Mapping[str, object], key: str) -> Decimal | None:
    value = payload.get(key)
    if value is None:
        return None
    return _non_negative_decimal(value, "freshness_gate_invalid_age_epochs")


def _read_optional_is_genesis(payload: Mapping[str, object], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise NodeValueKernelError("freshness_gate_invalid_is_genesis")
    return value


def _apply_freshness_metadata(
    row: NodeEvidenceVector,
    *,
    age_epochs: Decimal | None,
    is_genesis: bool | None,
) -> None:
    if age_epochs is not None:
        row["age_epochs"] = (
            age_epochs
            if row["age_epochs"] <= ZERO
            else min(row["age_epochs"], age_epochs)
        )
    if is_genesis is not None:
        row["is_genesis"] = bool(row["is_genesis"]) or is_genesis


def build_node_evidence_vectors(
    events: list[NodeValueInputEvent],
    *,
    freshness_policy: Mapping[str, object] = DEFAULT_FRESHNESS_GATE_POLICY,
) -> list[NodeEvidenceVector]:
    evidence: dict[str, NodeEvidenceVector] = {}
    agents_per_node: dict[str, set[str]] = {}
    agent_reuse_counts_by_node: dict[str, dict[str, int]] = {}

    for event in events:
        kind = event["kind"]
        payload = event["payload"]

        if kind == "claim":
            node_id = str(payload["id"])
            row = evidence.setdefault(node_id, _build_default_node_evidence_row(node_id))
            row["claim_net_stake"] = _decimal_from_value(
                payload["net_stake"],
                "node_value_kernel_invalid_claim_net_stake",
            )
            _apply_freshness_metadata(
                row,
                age_epochs=_read_optional_age_epochs(payload, "age_epochs"),
                is_genesis=_read_optional_is_genesis(payload, "is_genesis"),
            )

            target_id = str(payload["target_id"])
            target_row = evidence.setdefault(target_id, _build_default_node_evidence_row(target_id))
            target_row["reuse_count"] += ONE
            _apply_freshness_metadata(
                target_row,
                age_epochs=_read_optional_age_epochs(payload, "target_age_epochs"),
                is_genesis=_read_optional_is_genesis(payload, "target_is_genesis"),
            )
            agent_id = str(payload["agent_id"])
            agents_per_node.setdefault(target_id, set()).add(agent_id)
            counts = agent_reuse_counts_by_node.setdefault(target_id, {})
            counts[agent_id] = counts.get(agent_id, 0) + 1

        elif kind == "refutation":
            target_id = str(payload["target_id"])
            target_row = evidence.setdefault(target_id, _build_default_node_evidence_row(target_id))
            target_row["refutation_stake_against"] += _non_negative_decimal(
                payload["net_stake"],
                "node_value_kernel_invalid_refutation_stake_against",
            )
            target_row["reuse_count"] += ONE
            _apply_freshness_metadata(
                target_row,
                age_epochs=_read_optional_age_epochs(payload, "target_age_epochs"),
                is_genesis=_read_optional_is_genesis(payload, "target_is_genesis"),
            )
            agent_id = str(payload["agent_id"])
            agents_per_node.setdefault(target_id, set()).add(agent_id)
            counts = agent_reuse_counts_by_node.setdefault(target_id, {})
            counts[agent_id] = counts.get(agent_id, 0) + 1

    for node_id, agents in agents_per_node.items():
        row = evidence[node_id]
        row["unique_agents_using"] = Decimal(len(agents))
        row["usage_window"] = row["reuse_count"]

        reuse_count = row["reuse_count"]
        counts = agent_reuse_counts_by_node.get(node_id, {})
        max_agent_count = max(counts.values(), default=0)
        row["max_agent_reuse_share"] = (
            Decimal(max_agent_count) / reuse_count
            if reuse_count > ZERO
            else ZERO
        )

    for row in evidence.values():
        row["freshness_gate"] = _resolve_freshness_gate(
            age_epochs=row["age_epochs"],
            is_genesis=bool(row["is_genesis"]),
            policy=freshness_policy,
        )

    return [evidence[node_id] for node_id in sorted(evidence.keys())]


def compute_node_scores(
    events: list[NodeValueInputEvent],
    *,
    weights: Mapping[str, object] = DEFAULT_EW_WEIGHTS,
    path_witnesses: list[Mapping[str, object]] | None = None,
    reuse_diversity_policy: Mapping[str, object] = DEFAULT_REUSE_DIVERSITY_POLICY,
    freshness_policy: Mapping[str, object] = DEFAULT_FRESHNESS_GATE_POLICY,
) -> list[NodeScoreVector]:
    vectors = build_node_evidence_vectors(events, freshness_policy=freshness_policy)
    path_lift_by_node: dict[str, Decimal] = {}
    if path_witnesses is not None:
        path_lift_report = compute_path_lift_counterfactual(path_witnesses)
        path_lift_by_node = {
            node_id: _non_negative_decimal(value, "node_value_kernel_invalid_path_lift_score")
            for node_id, value in build_normalized_path_lift_by_node(path_lift_report).items()
        }

    output: list[NodeScoreVector] = []
    for vector in vectors:
        reuse_diversity_multiplier = _resolve_reuse_diversity_multiplier(
            reuse_count=vector["reuse_count"],
            distinct_agent_count=vector["unique_agents_using"],
            max_agent_reuse_share=vector["max_agent_reuse_share"],
            policy=reuse_diversity_policy,
        )
        path_lift_score = path_lift_by_node.get(vector["node_id"])
        (
            reuse_component,
            contradiction_component,
            validation_component,
            path_component,
            epistemic_weight,
        ) = compute_epistemic_weight(
            vector,
            weights=weights,
            path_lift_score=path_lift_score,
            reuse_diversity_multiplier=reuse_diversity_multiplier,
        )
        utility_flow = compute_utility_flow(
            epistemic_weight,
            vector["usage_window"],
            vector["freshness_gate"],
        )
        output.append(
            {
                "node_id": vector["node_id"],
                "reuse_component": reuse_component,
                "contradiction_component": contradiction_component,
                "validation_component": validation_component,
                "path_component": path_component,
                "reuse_diversity_multiplier": reuse_diversity_multiplier,
                "epistemic_weight": epistemic_weight,
                "freshness_gate": vector["freshness_gate"],
                "utility_flow": utility_flow,
            }
        )
    return output
