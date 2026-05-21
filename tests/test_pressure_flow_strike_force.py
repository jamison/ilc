from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from simulations.sim_pressure_flow_strike_force import (
    MODEL_VERSION,
    NO_CWEA_ACTIVATION_TOKEN,
    NO_RUNTIME_ACTIVATION_TOKEN,
    PRESSURE_FLOW_RESEARCH_TOKEN,
    SIMULATION_ID,
    export_suite_json,
    run_default_suite,
    run_scenario,
)


MODULE_PATH = Path("simulations/sim_pressure_flow_strike_force.py")


def _last_metric(scenario_id: str, *, controls_enabled: bool | None = None):
    return run_scenario(scenario_id, controls_enabled=controls_enabled).epochs[-1]


def test_honest_cross_cluster_keeps_high_efficiency_and_cross_cluster_flow() -> None:
    result = run_scenario("honest_cross_cluster", controls_enabled=True)
    last = result.epochs[-1]

    assert last.deployment_efficiency >= Decimal("0.88")
    assert last.cross_cluster_authorized_share == Decimal("1.000000")
    assert last.same_cluster_settlement_share == Decimal("0.000000")
    assert last.mean_agent_capacity > Decimal("85")
    assert PRESSURE_FLOW_RESEARCH_TOKEN in result.tokens
    assert NO_RUNTIME_ACTIVATION_TOKEN in result.tokens


def test_poor_routing_self_dampens_against_honest_baseline() -> None:
    honest = _last_metric("honest_cross_cluster", controls_enabled=True)
    poor = _last_metric("poor_routing_self_dampening", controls_enabled=True)

    assert poor.mean_agent_capacity < honest.mean_agent_capacity
    assert poor.total_outstanding_liability_ecu > honest.total_outstanding_liability_ecu
    assert poor.settlement_eligible_ecu < honest.settlement_eligible_ecu


def test_ring_controls_reduce_extraction_and_increase_throttling() -> None:
    no_controls = run_scenario("ring_no_controls", controls_enabled=False)
    with_controls = run_scenario("ring_with_controls", controls_enabled=True)
    no_controls_last = no_controls.epochs[-1]
    with_controls_last = with_controls.epochs[-1]

    assert with_controls_last.mean_agent_capacity < no_controls_last.mean_agent_capacity
    assert with_controls_last.total_outstanding_liability_ecu > no_controls_last.total_outstanding_liability_ecu
    assert with_controls_last.denied_by_controls_ecu > Decimal("0")
    assert with_controls_last.same_cluster_settlement_share < no_controls_last.same_cluster_settlement_share
    assert sum(agent.settled_total for agent in with_controls.final_agents) < sum(
        agent.settled_total for agent in no_controls.final_agents
    )


def test_pressure_account_fields_track_systolic_diastolic_and_pulse() -> None:
    result = run_scenario("ring_with_controls", controls_enabled=True)
    first = result.epochs[0]

    assert first.systolic_pressure_ecu == first.provisional_created_ecu
    assert first.diastolic_pull_ecu == Decimal("440.000000")
    assert first.pulse_pressure_ecu == abs(
        first.systolic_pressure_ecu - first.diastolic_pull_ecu
    ) + first.clawback_liability_ecu


def test_canonical_export_is_stable_and_non_authorizing() -> None:
    exported = export_suite_json(run_default_suite())
    parsed = json.loads(exported)

    assert exported == json.dumps(
        parsed,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert parsed["simulation_id"] == SIMULATION_ID
    assert parsed["model_version"] == MODEL_VERSION
    assert parsed["tokens"] == [
        PRESSURE_FLOW_RESEARCH_TOKEN,
        NO_RUNTIME_ACTIVATION_TOKEN,
        NO_CWEA_ACTIVATION_TOKEN,
    ]
    for result in parsed["results"]:
        assert result["authorization"] == {
            "cwea_activation_authorized": False,
            "ecu_mint_authorized": False,
            "ilc_settlement_authorized": False,
            "pressure_flow_reputation_authorized": False,
            "public_rc_surface": False,
            "runtime_policy_authorized": False,
        }


def test_simulation_module_is_public_rc_excluded_and_not_runtime_policy() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE: pressure_flow_research_simulation_not_public_rc_surface" in source
    assert "json.dumps(" in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source
    for forbidden in (
        "mint_ecu(",
        "settle_ilc(",
        "write_wallet",
        "PRODUCTION",
        "claimability_activated = True",
        "pressure_flow_reputation_authorized\": True",
    ):
        assert forbidden not in source
