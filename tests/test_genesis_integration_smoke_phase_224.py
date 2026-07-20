from __future__ import annotations

from decimal import Decimal
from typing import Any

from ilc_core.analysis.genesis_accrual_governor import (
    THETA_HARD,
    evaluate_genesis_accrual_governor,
)
from ilc_core.analysis.node_value_governance_conformance import (
    evaluate_node_value_governance_conformance,
)
from ilc_core.analysis.node_value_input_canon import collect_node_value_input_events
from ilc_core.analysis.node_value_kernel import (
    build_node_evidence_vectors,
    compute_node_scores,
)
from ilc_core.analysis.utility_flow_rewards import allocate_rewards_with_governor


def _claim_event(
    claim_id: str,
    agent_id: str,
    target_id: str,
    *,
    age_epochs: float,
    target_age_epochs: float,
    net_stake: float,
    target_is_genesis: bool = False,
) -> dict[str, object]:
    return {
        "kind": "claim",
        "payload": {
            "id": claim_id,
            "agent_id": agent_id,
            "timestamp": "2026-02-18T00:00:00Z",
            "net_stake": net_stake,
            "parent_ids": [target_id],
            "target_id": target_id,
            "age_epochs": age_epochs,
            "target_age_epochs": target_age_epochs,
            "target_is_genesis": target_is_genesis,
        },
    }


def _refutation_event(
    refutation_id: str,
    agent_id: str,
    target_id: str,
    *,
    target_age_epochs: float,
    net_stake: float,
) -> dict[str, object]:
    return {
        "kind": "refutation",
        "payload": {
            "id": refutation_id,
            "agent_id": agent_id,
            "timestamp": "2026-02-18T00:10:00Z",
            "target_id": target_id,
            "net_stake": net_stake,
            "target_age_epochs": target_age_epochs,
        },
    }


def _raw_events() -> list[dict[str, object]]:
    return [
        _claim_event(
            "claim:base:alpha",
            "agent-1",
            "axiom:math:01",
            age_epochs=0.0,
            target_age_epochs=120.0,
            net_stake=5.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:base:beta",
            "agent-2",
            "axiom:logic:01",
            age_epochs=6.0,
            target_age_epochs=120.0,
            net_stake=5.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:base:gamma",
            "agent-3",
            "axiom:evidence:01",
            age_epochs=2.0,
            target_age_epochs=120.0,
            net_stake=4.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:axiom:math:diversify",
            "agent-4",
            "axiom:math:01",
            age_epochs=3.0,
            target_age_epochs=120.0,
            net_stake=1.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:axiom:logic:diversify",
            "agent-5",
            "axiom:logic:01",
            age_epochs=3.0,
            target_age_epochs=120.0,
            net_stake=1.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:base:delta",
            "agent-1",
            "claim:base:beta",
            age_epochs=7.0,
            target_age_epochs=6.0,
            net_stake=3.0,
        ),
        _refutation_event(
            "refutation:base:beta",
            "agent-3",
            "claim:base:beta",
            target_age_epochs=6.0,
            net_stake=1.5,
        ),
        _claim_event(
            "claim:reuse:concentrated",
            "agent-1",
            "axiom:math:01",
            age_epochs=5.0,
            target_age_epochs=120.0,
            net_stake=4.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:reuse:diverse",
            "agent-2",
            "axiom:logic:01",
            age_epochs=5.0,
            target_age_epochs=120.0,
            net_stake=4.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:conc:hit:1",
            "agent-1",
            "claim:reuse:concentrated",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:conc:hit:2",
            "agent-1",
            "claim:reuse:concentrated",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:conc:hit:3",
            "agent-1",
            "claim:reuse:concentrated",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:conc:hit:4",
            "agent-1",
            "claim:reuse:concentrated",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:conc:hit:5",
            "agent-2",
            "claim:reuse:concentrated",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:div:hit:1",
            "agent-1",
            "claim:reuse:diverse",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:div:hit:2",
            "agent-2",
            "claim:reuse:diverse",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:div:hit:3",
            "agent-3",
            "claim:reuse:diverse",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:div:hit:4",
            "agent-4",
            "claim:reuse:diverse",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:div:hit:5",
            "agent-5",
            "claim:reuse:diverse",
            age_epochs=1.0,
            target_age_epochs=5.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:pair:validation",
            "agent-1",
            "axiom:evidence:01",
            age_epochs=4.0,
            target_age_epochs=120.0,
            net_stake=3.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:pair:refutation",
            "agent-2",
            "axiom:evidence:01",
            age_epochs=4.0,
            target_age_epochs=120.0,
            net_stake=3.0,
            target_is_genesis=True,
        ),
        _claim_event(
            "claim:pair:use:validation",
            "agent-3",
            "claim:pair:validation",
            age_epochs=1.0,
            target_age_epochs=4.0,
            net_stake=1.0,
        ),
        _claim_event(
            "claim:pair:use:refutation",
            "agent-3",
            "claim:pair:refutation",
            age_epochs=1.0,
            target_age_epochs=4.0,
            net_stake=1.0,
        ),
    ]


def _path_witnesses() -> list[dict[str, object]]:
    return [
        {
            "witness_id": "witness:001",
            "source_id": "axiom:math:01",
            "target_id": "claim:reuse:concentrated",
            "nodes": [
                {"node_id": "axiom:math:01", "agent_id": "genesis"},
                {"node_id": "claim:reuse:concentrated", "agent_id": "agent-1"},
                {"node_id": "claim:conc:hit:5", "agent_id": "agent-2"},
            ],
            "path_weight": 6.0,
            "path_cost": 2.0,
        },
        {
            "witness_id": "witness:002",
            "source_id": "axiom:logic:01",
            "target_id": "claim:reuse:diverse",
            "nodes": [
                {"node_id": "axiom:logic:01", "agent_id": "genesis"},
                {"node_id": "claim:reuse:diverse", "agent_id": "agent-2"},
                {"node_id": "claim:div:hit:5", "agent_id": "agent-5"},
            ],
            "path_weight": 6.0,
            "path_cost": 2.0,
        },
        {
            "witness_id": "witness:003",
            "source_id": "axiom:evidence:01",
            "target_id": "claim:pair:validation",
            "nodes": [
                {"node_id": "axiom:evidence:01", "agent_id": "genesis"},
                {"node_id": "claim:pair:validation", "agent_id": "agent-1"},
                {"node_id": "claim:pair:refutation", "agent_id": "agent-2"},
            ],
            "path_weight": 6.0,
            "path_cost": 2.0,
        },
    ]


def test_phase_224_full_constitutional_pipeline_integration_smoke() -> None:
    accepted_events, telemetry = collect_node_value_input_events(_raw_events())

    assert telemetry["rejected_invalid_shape"] == 0
    assert telemetry["rejected_unknown_kind"] == 0
    assert telemetry["accepted"] == telemetry["total_seen"]

    score_rows = compute_node_scores(accepted_events, path_witnesses=_path_witnesses())
    evidence_rows = build_node_evidence_vectors(accepted_events)

    score_by_node = {row["node_id"]: row for row in score_rows}
    evidence_by_node = {row["node_id"]: row for row in evidence_rows}

    assert score_by_node["axiom:math:01"]["freshness_gate"] == 1.0
    assert score_by_node["axiom:logic:01"]["freshness_gate"] == 1.0
    assert score_by_node["axiom:evidence:01"]["freshness_gate"] == 1.0

    assert score_by_node["claim:reuse:diverse"]["utility_flow"] > score_by_node["claim:reuse:concentrated"]["utility_flow"]

    assert score_by_node["claim:base:beta"]["freshness_gate"] < score_by_node["claim:base:alpha"]["freshness_gate"]

    expected_score_keys = {
        "node_id",
        "reuse_component",
        "contradiction_component",
        "validation_component",
        "path_component",
        "reuse_diversity_multiplier",
        "epistemic_weight",
        "freshness_gate",
        "utility_flow",
    }
    for row in score_rows:
        assert set(row.keys()) == expected_score_keys

    reward_inputs: list[dict[str, Any]] = []
    for row in score_rows:
        node_id = row["node_id"]
        action_kind = "other"
        pairing_key = ""
        stake_spent = 0.0
        effort_units = 1.0
        if node_id == "claim:pair:validation":
            action_kind = "validation"
            pairing_key = "pair:claim:001"
            stake_spent = 1.0
            effort_units = 3.0
        elif node_id == "claim:pair:refutation":
            action_kind = "refutation"
            pairing_key = "pair:claim:001"
            stake_spent = 1.0
            effort_units = 3.0

        reward_inputs.append(
            {
                "node_id": node_id,
                "utility_flow": row["utility_flow"],
                "is_genesis": bool(evidence_by_node[node_id]["is_genesis"]),
                "action_kind": action_kind,
                "pairing_key": pairing_key,
                "stake_spent": stake_spent,
                "effort_units": effort_units,
                "reuse_diversity_multiplier": row["reuse_diversity_multiplier"],
                "diversity_applied_in_scoring": True,
                "freshness_gate": row["freshness_gate"],
                "freshness_applied_in_scoring": True,
            }
        )

    reward_report = allocate_rewards_with_governor(
        reward_inputs,
        policy={
            "epoch_reward_budget": 250.0,
            "max_genesis_share": 1.0,
            "min_flow_threshold": 0.0,
        },
    )

    allocation_by_node = {row["node_id"]: row for row in reward_report["allocations"]}
    assert allocation_by_node["claim:pair:refutation"]["reward_amount"] > allocation_by_node["claim:pair:validation"]["reward_amount"]
    assert reward_report["refutation_profitability"]["ok"] is True
    assert reward_report["governor"]["total_distributed"] <= reward_report["governor"]["budget"] + 1e-9

    genesis_signal = {
        "genesis_cumulative_accrual": Decimal(
            str(
                sum(
                    row["reward_amount"]
                    for row in reward_report["allocations"]
                    if row["is_genesis"]
                )
            )
        )
        + Decimal("25"),
        "total_cumulative_issuance": Decimal(
            str(reward_report["governor"]["total_distributed"])
        )
        + Decimal("3000"),
    }
    governor_report = evaluate_genesis_accrual_governor(genesis_signal)

    assert Decimal("0") <= governor_report["taper_multiplier"] <= Decimal("1")
    assert governor_report["genesis_share_ratio"] < THETA_HARD
    assert governor_report["cap_blocked"] is False

    cap_report = evaluate_genesis_accrual_governor(
        {
            "genesis_cumulative_accrual": Decimal("1296000"),
            "total_cumulative_issuance": Decimal("5000000"),
        }
    )
    assert cap_report["cap_blocked"] is True
    assert cap_report["taper_multiplier"] == Decimal("0E-12")

    conformance_report = evaluate_node_value_governance_conformance(
        accepted_events,
        reward_allocations=reward_report["allocations"],
        genesis_signal=genesis_signal,
    )
    assert conformance_report["overall_ok"] is True
