from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.analysis.node_value_governance_conformance import (
    build_node_value_governance_conformance_report,
)
from ilc_core.analysis.utility_flow_rewards import allocate_rewards_with_governor


def _sample_events() -> list[dict[str, object]]:
    return [
        {
            "kind": "claim",
            "payload": {
                "id": "node-a",
                "agent_id": "agent-1",
                "timestamp": "2026-02-18T00:00:00Z",
                "net_stake": 5.0,
                "parent_ids": ["root"],
                "target_id": "node-root",
                "target_age_epochs": 2.0,
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "node-b",
                "agent_id": "agent-2",
                "timestamp": "2026-02-18T00:01:00Z",
                "net_stake": 3.0,
                "parent_ids": ["node-a"],
                "target_id": "node-a",
                "target_age_epochs": 1.0,
            },
        },
        {
            "kind": "refutation",
            "payload": {
                "id": "ref-1",
                "agent_id": "agent-3",
                "timestamp": "2026-02-18T00:02:00Z",
                "target_id": "node-a",
                "net_stake": 1.0,
                "target_age_epochs": 1.0,
            },
        },
    ]


def _sample_allocations() -> list[dict[str, object]]:
    report = allocate_rewards_with_governor(
        [
            {
                "node_id": "validator-node",
                "utility_flow": 10.0,
                "is_genesis": False,
                "action_kind": "validation",
                "stake_spent": 1.0,
                "effort_units": 5.0,
                "pairing_key": "claim-219",
            },
            {
                "node_id": "refuter-node",
                "utility_flow": 10.0,
                "is_genesis": False,
                "action_kind": "refutation",
                "stake_spent": 1.0,
                "effort_units": 5.0,
                "pairing_key": "claim-219",
            },
        ],
        policy={
            "epoch_reward_budget": 120.0,
            "max_genesis_share": 1.0,
            "min_flow_threshold": 0.0,
        },
    )
    return report["allocations"]


def test_phase_219_conformance_report_is_deterministic() -> None:
    events = _sample_events()
    allocations = _sample_allocations()
    signal = {
        "genesis_cumulative_accrual": Decimal("2"),
        "total_cumulative_issuance": Decimal("80"),
    }

    report_a = build_node_value_governance_conformance_report(
        events,
        reward_allocations=allocations,
        genesis_signal=signal,
    )
    report_b = build_node_value_governance_conformance_report(
        events,
        reward_allocations=allocations,
        genesis_signal=signal,
    )

    assert report_a == report_b
    assert report_a["contract_version"] == "v0.1"
    assert report_a["score_row_count"] > 0
    assert isinstance(report_a["score_rows_sha256"], str)


def test_phase_219_report_delegates_refutation_and_governor_evaluators(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _sample_events()
    allocations = _sample_allocations()
    signal = {
        "genesis_cumulative_accrual": Decimal("2"),
        "total_cumulative_issuance": Decimal("80"),
    }
    calls: dict[str, int] = {"refutation": 0, "governor": 0}

    from ilc_core.analysis import node_value_governance_conformance as module

    def _fake_refutation(rows, *, tolerance: float = 1e-9):  # type: ignore[no-untyped-def]
        assert tolerance == pytest.approx(1e-9)
        calls["refutation"] += 1
        return {
            "ok": True,
            "errors": [],
            "compared_groups": 1,
            "skipped_rows": 0,
        }

    def _fake_governor(sig, *, policy):  # type: ignore[no-untyped-def]
        assert sig == signal
        assert "theta_hard" in policy
        calls["governor"] += 1
        return {
            "genesis_share_ratio": 0.02,
            "taper_multiplier": 0.9,
            "cap_blocked": False,
        }

    monkeypatch.setattr(module, "evaluate_refutation_profitability_invariant", _fake_refutation)
    monkeypatch.setattr(module, "evaluate_genesis_accrual_governor", _fake_governor)

    report = build_node_value_governance_conformance_report(
        events,
        reward_allocations=allocations,
        genesis_signal=signal,
    )

    assert report["checks"]["refutation_profitability"]["ok"] is True
    assert report["checks"]["genesis_accrual_governor"]["ok"] is True
    assert calls == {"refutation": 1, "governor": 1}


def test_phase_219_report_skips_optional_surfaces_when_inputs_are_absent() -> None:
    report = build_node_value_governance_conformance_report(_sample_events())

    assert report["checks"]["refutation_profitability"]["skipped"] is True
    assert report["checks"]["genesis_accrual_governor"]["skipped"] is True
    assert report["checks"]["refutation_profitability"]["detail"]["reason"] == "conformance_missing_reward_allocations"
    assert report["checks"]["genesis_accrual_governor"]["detail"]["reason"] == "conformance_missing_genesis_signal"


def test_phase_219_report_enforces_score_vector_schema() -> None:
    report = build_node_value_governance_conformance_report(_sample_events())
    schema_check = report["checks"]["score_vector_schema"]

    assert schema_check["ok"] is True
    required_keys = schema_check["detail"]["required_keys"]
    assert "reuse_diversity_multiplier" in required_keys
    assert "freshness_gate" in required_keys
    assert "utility_flow" in required_keys


def test_phase_219_invalid_policy_surfaces_fail_without_formula_changes() -> None:
    report = build_node_value_governance_conformance_report(
        _sample_events(),
        reuse_diversity_policy={
            "min_distinct_agents": 2,
            "max_single_agent_share": 0.75,
            "penalty_floor": 0.8,
        },
    )

    assert report["checks"]["reuse_diversity_policy"]["ok"] is False
    assert "reuse_diversity_penalty_floor_below_refutation_safety" in report["checks"]["reuse_diversity_policy"]["errors"]
