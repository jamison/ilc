from __future__ import annotations

from typing import Mapping, TypedDict

from ilc_core.analysis.freshness_gate import (
    DEFAULT_FRESHNESS_GATE_POLICY,
    compute_freshness_gate,
)
from ilc_core.analysis.path_lift_counterfactual import (
    build_normalized_path_lift_by_node,
    compute_path_lift_counterfactual,
)
from ilc_core.analysis.node_value_input_canon import NodeValueInputEvent
from ilc_core.analysis.reuse_diversity_invariants import (
    DEFAULT_REUSE_DIVERSITY_POLICY,
    compute_reuse_diversity_multiplier,
)
from ilc_core.exceptions import NodeValueKernelError


class EwWeights(TypedDict):
    reuse: float
    contradiction_resilience: float
    validation_integrity: float
    path_uplift: float


class NodeEvidenceVector(TypedDict):
    node_id: str
    reuse_count: float
    claim_net_stake: float
    refutation_stake_against: float
    unique_agents_using: float
    max_agent_reuse_share: float
    usage_window: float
    age_epochs: float
    is_genesis: bool
    freshness_gate: float


class NodeScoreVector(TypedDict):
    node_id: str
    reuse_component: float
    contradiction_component: float
    validation_component: float
    path_component: float
    reuse_diversity_multiplier: float
    epistemic_weight: float
    freshness_gate: float
    utility_flow: float


DEFAULT_EW_WEIGHTS: EwWeights = {
    "reuse": 0.35,
    "contradiction_resilience": 0.25,
    "validation_integrity": 0.20,
    "path_uplift": 0.20,
}


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def validate_ew_weights(weights: Mapping[str, float]) -> EwWeights:
    expected_keys = set(DEFAULT_EW_WEIGHTS.keys())
    got_keys = set(weights.keys())
    if got_keys != expected_keys:
        raise NodeValueKernelError("node_value_kernel_invalid_weight_keys")

    normalized: EwWeights = {
        "reuse": float(weights["reuse"]),
        "contradiction_resilience": float(weights["contradiction_resilience"]),
        "validation_integrity": float(weights["validation_integrity"]),
        "path_uplift": float(weights["path_uplift"]),
    }
    if any(v < 0.0 for v in normalized.values()):
        raise NodeValueKernelError("node_value_kernel_negative_weight")

    total = sum(normalized.values())
    if abs(total - 1.0) > 1e-9:
        raise NodeValueKernelError("node_value_kernel_weight_sum_not_one")

    return normalized


def _reuse_component(reuse_count: float) -> float:
    return _clamp(reuse_count / 5.0)


def _contradiction_component(claim_net_stake: float, refutation_stake_against: float) -> float:
    base = max(1.0, abs(claim_net_stake))
    return _clamp((claim_net_stake - refutation_stake_against) / base)


def _validation_component(unique_agents_using: float) -> float:
    return _clamp(unique_agents_using / 3.0)


def _legacy_path_component(reuse_count: float) -> float:
    return _clamp(reuse_count / 4.0)


def compute_epistemic_weight(
    evidence: NodeEvidenceVector,
    *,
    weights: Mapping[str, float] = DEFAULT_EW_WEIGHTS,
    path_lift_score: float | None = None,
    reuse_diversity_multiplier: float = 1.0,
) -> tuple[float, float, float, float, float]:
    ew_weights = validate_ew_weights(weights)

    reuse_component = _clamp(
        _reuse_component(float(evidence["reuse_count"])) * float(reuse_diversity_multiplier)
    )
    contradiction_component = _contradiction_component(
        float(evidence["claim_net_stake"]),
        float(evidence["refutation_stake_against"]),
    )
    validation_component = _validation_component(float(evidence["unique_agents_using"]))
    if path_lift_score is None:
        path_component = _legacy_path_component(float(evidence["reuse_count"]))
    else:
        path_component = _clamp(path_lift_score)

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


def compute_utility_flow(epistemic_weight: float, usage_window: float, freshness_gate: float) -> float:
    if usage_window < 0.0:
        raise NodeValueKernelError("node_value_kernel_negative_usage_window")
    if freshness_gate < 0.0 or freshness_gate > 1.0:
        raise NodeValueKernelError("node_value_kernel_invalid_freshness_gate")
    return epistemic_weight * usage_window * freshness_gate


def _build_default_node_evidence_row(node_id: str) -> NodeEvidenceVector:
    return {
        "node_id": node_id,
        "reuse_count": 0.0,
        "claim_net_stake": 0.0,
        "refutation_stake_against": 0.0,
        "unique_agents_using": 0.0,
        "max_agent_reuse_share": 0.0,
        "usage_window": 1.0,
        "age_epochs": 0.0,
        "is_genesis": False,
        "freshness_gate": 1.0,
    }


def _read_optional_age_epochs(payload: Mapping[str, object], key: str) -> float | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) < 0.0:
        raise NodeValueKernelError("freshness_gate_invalid_age_epochs")
    return float(value)


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
    age_epochs: float | None,
    is_genesis: bool | None,
) -> None:
    if age_epochs is not None:
        row["age_epochs"] = (
            age_epochs
            if row["age_epochs"] <= 0.0
            else min(float(row["age_epochs"]), age_epochs)
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
            row["claim_net_stake"] = float(payload["net_stake"])
            _apply_freshness_metadata(
                row,
                age_epochs=_read_optional_age_epochs(payload, "age_epochs"),
                is_genesis=_read_optional_is_genesis(payload, "is_genesis"),
            )

            target_id = str(payload["target_id"])
            target_row = evidence.setdefault(target_id, _build_default_node_evidence_row(target_id))
            target_row["reuse_count"] += 1.0
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
            target_row["refutation_stake_against"] += float(payload["net_stake"])
            target_row["reuse_count"] += 1.0
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
        row["unique_agents_using"] = float(len(agents))
        row["usage_window"] = float(row["reuse_count"])

        reuse_count = float(row["reuse_count"])
        counts = agent_reuse_counts_by_node.get(node_id, {})
        max_agent_count = max(counts.values(), default=0)
        row["max_agent_reuse_share"] = (
            float(max_agent_count) / reuse_count
            if reuse_count > 0.0
            else 0.0
        )

    for row in evidence.values():
        row["freshness_gate"] = compute_freshness_gate(
            {
                "age_epochs": float(row["age_epochs"]),
                "is_genesis": bool(row["is_genesis"]),
            },
            policy=freshness_policy,
        )

    return [evidence[node_id] for node_id in sorted(evidence.keys())]


def compute_node_scores(
    events: list[NodeValueInputEvent],
    *,
    weights: Mapping[str, float] = DEFAULT_EW_WEIGHTS,
    path_witnesses: list[Mapping[str, object]] | None = None,
    reuse_diversity_policy: Mapping[str, object] = DEFAULT_REUSE_DIVERSITY_POLICY,
    freshness_policy: Mapping[str, object] = DEFAULT_FRESHNESS_GATE_POLICY,
) -> list[NodeScoreVector]:
    vectors = build_node_evidence_vectors(events, freshness_policy=freshness_policy)
    path_lift_by_node: dict[str, float] = {}
    if path_witnesses is not None:
        path_lift_report = compute_path_lift_counterfactual(path_witnesses)
        path_lift_by_node = build_normalized_path_lift_by_node(path_lift_report)

    output: list[NodeScoreVector] = []
    for vector in vectors:
        reuse_diversity_multiplier = compute_reuse_diversity_multiplier(
            {
                "reuse_count": vector["reuse_count"],
                "distinct_agent_count": vector["unique_agents_using"],
                "max_agent_reuse_share": vector["max_agent_reuse_share"],
            },
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
            float(vector["usage_window"]),
            float(vector["freshness_gate"]),
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
                "freshness_gate": float(vector["freshness_gate"]),
                "utility_flow": utility_flow,
            }
        )
    return output
