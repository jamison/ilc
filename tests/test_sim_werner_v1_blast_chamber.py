# SPDX-License-Identifier: AGPL-3.0-only
"""Regression tests for the Werner v1 blast-chamber SIM."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from tools.sim import sim_werner_v1_blast_chamber as sim


def test_artifact_contains_all_required_scenarios() -> None:
    artifact = sim.build_artifact()
    assert [row["scenario"] for row in artifact["scenarios"]] == list(sim.REQUIRED_SCENARIOS)


def test_flow_budgets_never_exceed_cdl109_cap() -> None:
    artifact = sim.build_artifact()
    for scenario in artifact["scenarios"]:
        for row in scenario["agent_results"]:
            assert Decimal(row["flow_budget"]) <= sim.FLOW_BUDGET_CAP


def test_local_only_receipts_contribute_zero_signal() -> None:
    rows = {
        row["agent_id"]: row
        for row in sim.evaluate_scenario("consent_status_edge_cases")["agent_results"]
    }
    assert Decimal(rows["local_only_heavy"]["raw_signal"]) == Decimal("0.000000000000")
    assert Decimal(rows["local_only_heavy"]["flow_budget"]) == Decimal("0.000000000000")


def test_failure_receipts_contribute_zero_signal() -> None:
    rows = {
        row["agent_id"]: row
        for row in sim.evaluate_scenario("failed_partial_receipt_farming")["agent_results"]
    }
    assert Decimal(rows["failed_farmer"]["raw_signal"]) == Decimal("0.000000000000")
    assert Decimal(rows["failed_farmer"]["flow_budget"]) == Decimal("0.000000000000")


def test_clustered_collusion_is_capped_in_every_feasible_scenario() -> None:
    artifact = sim.build_artifact()
    for scenario in artifact["scenarios"]:
        if scenario["cluster_cap_feasible"]:
            assert scenario["cluster_cap_holds"] is True
            assert (
                Decimal(scenario["strongest_multi_agent_cluster_share_after_cap"])
                <= sim.CLUSTER_SHARE_CAP
            )


def test_cluster_cap_is_not_order_dependent_for_competing_clusters() -> None:
    signals = {
        "a1": Decimal("40"),
        "a2": Decimal("40"),
        "b1": Decimal("40"),
        "b2": Decimal("40"),
        "solo": Decimal("80"),
    }
    clusters = {
        "a1": "cluster_a",
        "a2": "cluster_a",
        "b1": "cluster_b",
        "b2": "cluster_b",
        "solo": "solo",
    }
    capped, share, feasible = sim._cluster_cap(signals, clusters)
    reversed_clusters = {
        "a1": "cluster_b",
        "a2": "cluster_b",
        "b1": "cluster_a",
        "b2": "cluster_a",
        "solo": "solo",
    }
    reversed_capped, reversed_share, reversed_feasible = sim._cluster_cap(signals, reversed_clusters)
    assert feasible is True
    assert reversed_feasible is True
    assert share <= sim.CLUSTER_SHARE_CAP
    assert reversed_share <= sim.CLUSTER_SHARE_CAP
    assert capped == reversed_capped


def test_pool_conservation_holds_for_every_scenario() -> None:
    artifact = sim.build_artifact()
    assert artifact["invariants"]["pool_total_unchanged"] is True
    for scenario in artifact["scenarios"]:
        assert scenario["pool_total_before"] == scenario["pool_total_after_normalization"]
        assert scenario["pool_conservation_difference"] == "0.000000000000"
        assert scenario["pool_conservation_holds"] is True
        allocation_total = sum(
            Decimal(row["normalized_pool_allocation"])
            for row in scenario["normalized_pool_allocations"]
        )
        assert allocation_total == sim.POOL_TOTAL


def test_receipt_splitting_advantage_is_explicit_and_bounded() -> None:
    rows = {
        row["agent_id"]: row
        for row in sim.evaluate_scenario("receipt_splitting")["agent_results"]
    }
    splitter = Decimal(rows["splitter"]["raw_signal"])
    single_large = Decimal(rows["single_large"]["raw_signal"])
    assert splitter > single_large
    assert splitter <= sim.MAX_AGENT_SIGNAL
    assert Decimal(rows["splitter"]["flow_budget"]) <= sim.FLOW_BUDGET_CAP


def test_artifact_is_deterministic() -> None:
    assert sim.build_artifact() == sim.build_artifact()


def test_candidate_formula_names_pre_normalization_no_stacking() -> None:
    artifact = sim.build_artifact()
    formula = artifact["candidate_formula"]
    assert "pre-normalization" in formula
    assert "z_i'(e)" in formula
    assert "unchanged pool B_e * M_e" in formula
    assert "20000" in formula
    assert "12.0" in formula
    assert "0.10" in formula
    assert "35%" in formula
    assert artifact["invariants"]["no_capproof_stacking"] is True
    assert artifact["invariants"]["no_passive_ecu_quality_factor_stacking"] is True


def test_committed_artifact_matches_regenerated_json() -> None:
    artifact_path = Path("docs/sims/sim_werner_v1_blast_chamber_00_v0.1.json")
    committed = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert committed == sim.build_artifact()


def test_generated_files_are_reproducible(tmp_path: Path) -> None:
    json_out = tmp_path / "sim.json"
    md_out = tmp_path / "sim.md"
    assert sim.main(["--json-out", str(json_out), "--md-out", str(md_out)]) == 0
    assert json.loads(json_out.read_text(encoding="utf-8")) == sim.build_artifact()
    assert "pool conservation difference" in md_out.read_text(encoding="utf-8")
