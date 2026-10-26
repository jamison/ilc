from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from tools.sim import sim_sufficiency_hyperedge_01 as sim


EXPECTED = {
    "useful_reduction": ("authorized_reuse", "0.20"),
    "costly_little_reuse": ("no_eligible_attribution_event", "0"),
    "stale_dependency": ("rejected_use", "0"),
    "valid_counterexample": ("rejected_claim_refutation_credited", "0.20"),
    "misleading_verification": ("rejected_use", "0"),
    "repeated_submissions": ("authorized_reuse", "0.20"),
    "genesis_ordinary_direct": ("authorized_direct_attribution", "0.20"),
    "genesis_backward": ("authorized_backward_attribution", "0.0150"),
    "genesis_invite_fee_zero": ("no_special_referral_fee", "0"),
    "node0_authority_only": ("no_eligible_attribution_event", "0"),
    "genesis_governance_vs_productive": ("authorized_direct_attribution", "0.20"),
    "no_duplicate_payment": (
        "authorized_distinct_contributions_deduplicated",
        "0.2150",
    ),
}


def _inputs() -> list[dict[str, object]]:
    return sim.build_fixture_inputs()


def _by_id(results: dict[str, object]) -> dict[str, dict[str, object]]:
    return {item["scenario_id"]: item for item in results["scenarios"]}


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def test_all_twelve_expected_scenarios_match_independent_matrix() -> None:
    records = _by_id(sim.build_results())
    assert set(records) == set(EXPECTED)
    for scenario_id, (decision, total) in EXPECTED.items():
        assert records[scenario_id]["decision"] == decision
        assert records[scenario_id]["total_quote_ecu"] == total


def test_authority_constants_and_lane_boundaries_are_exact() -> None:
    parameters = sim.build_results()["authority_parameters"]
    assert parameters == {
        "cdl081_direct_rate": "0.20",
        "cdl084_provenance_decay_alpha": "0.45",
        "cdl084_provenance_max_depth": 3,
        "cdl085_phi_bound": "0.60",
        "cdl108_backward_pool_share": "0.10",
        "cdl108_per_node_cap_share": "0.05",
        "cdl108_per_agent_cap_share": "0.10",
        "cdl108_per_cluster_cap_share": "0.25",
        "explicit_provenance_hop_1_quote": "0.0900",
    }
    assert sim.explicit_provenance_quote(1) == Decimal("0.0900")
    assert sim.explicit_provenance_quote(3) == Decimal("0.0182250")


def test_phi_bound_does_not_cap_direct_reuse() -> None:
    useful = _by_id(sim.build_results())["useful_reduction"]
    assert Decimal(useful["total_quote_ecu"]) == Decimal("0.20")
    assert sim.EDGE_MINT_PHI_BOUND == Decimal("0.60")
    assert useful["quote_records"][0]["channel"] == "CDL081_DIRECT"


def test_refutation_is_separate_from_rejected_claim_reuse() -> None:
    item = _by_id(sim.build_results())["valid_counterexample"]
    assert item["decision"] == "rejected_claim_refutation_credited"
    assert item["quote_records"][0]["channel"] == "CDL083_REFUTATION"
    assert "claim_reuse_rejected" in item["reason_codes"]


def test_refutation_credit_requires_exact_upheld_refutation_assessments() -> None:
    item = next(value for value in _inputs() if value["scenario_id"] == "valid_counterexample")
    item["assessments"].update(
        {
            "structural_closure": "missing",
            "current_observer_permission": "negative",
            "use_time_readiness": "not_ready",
        }
    )
    result = sim.evaluate_scenario(item)
    assert result["decision"] == "unresolved_pending_evidence"
    assert result["quote_records"] == []
    assert result["total_quote_ecu"] == "0"


def test_backward_caps_derive_from_backward_pool() -> None:
    item = _by_id(sim.build_results())["genesis_backward"]
    details = item["details"]
    assert details["event_budget_ecu"] == "1"
    assert details["backward_pool_ecu"] == "0.10"
    assert details["node_cap_amount_ecu"] == "0.0050"
    assert details["agent_cap_amount_ecu"] == "0.0100"
    assert details["cluster_cap_amount_ecu"] == "0.0250"
    assert details["unissued_backward_pool_ecu"] == "0.0850"
    assert len(item["quote_records"]) == 3
    assert all(q["amount_ecu"] == "0.0050" for q in item["quote_records"])
    assert item["details"]["sybil_diversity_status"] == (
        "cdl_114_sybil_diversity_guard_passed"
    )
    assert item["details"]["distinct_source_ref_creator_count"] == "3"


def test_genesis_has_no_special_invite_fee_or_multiplier() -> None:
    records = _by_id(sim.build_results())
    assert records["genesis_invite_fee_zero"]["total_quote_ecu"] == "0"
    assert records["genesis_ordinary_direct"]["total_quote_ecu"] == "0.20"
    assert records["useful_reduction"]["total_quote_ecu"] == "0.20"


def test_governance_authority_alone_has_no_quote() -> None:
    records = _by_id(sim.build_results())
    assert records["node0_authority_only"]["total_quote_ecu"] == "0"
    mixed = records["genesis_governance_vs_productive"]
    assert mixed["total_quote_ecu"] == "0.20"
    assert "governance_control_quote_zero" in mixed["reason_codes"]


def test_repeated_submission_deduplicates_exact_economic_event() -> None:
    repeated = _by_id(sim.build_results())["repeated_submissions"]
    assert repeated["raw_quote_count"] == 5
    assert repeated["deduplicated_quote_count"] == 1
    assert repeated["total_quote_ecu"] == "0.20"


def test_distinct_contributions_survive_exact_duplicate_collapse() -> None:
    item = _by_id(sim.build_results())["no_duplicate_payment"]
    assert item["raw_quote_count"] == 8
    assert item["deduplicated_quote_count"] == 4
    assert item["total_quote_ecu"] == "0.2150"
    assert item["details"]["separate_non_ecu_mechanism"].startswith("CDL-029")


def test_stale_and_misleading_claims_cannot_authorize_reuse() -> None:
    records = _by_id(sim.build_results())
    for scenario_id in ("stale_dependency", "misleading_verification"):
        assert records[scenario_id]["decision"] == "rejected_use"
        assert records[scenario_id]["quote_records"] == []


@pytest.mark.parametrize(
    ("field", "value", "expected_decision"),
    [
        ("historical_production_authority", "unresolved", "unresolved_pending_evidence"),
        ("present_artifact_eligibility", "negative", "rejected_use"),
        ("current_observer_permission", "negative", "rejected_use"),
        ("use_time_readiness", "not_ready", "unresolved_pending_evidence"),
        ("structural_closure", "missing", "unresolved_pending_evidence"),
        ("structural_closure", "resource_exhausted", "unresolved_pending_evidence"),
    ],
)
def test_positive_scenario_requires_all_six_assessments(
    field: str,
    value: str,
    expected_decision: str,
) -> None:
    item = _inputs()[0]
    item["assessments"][field] = value
    result = sim.evaluate_scenario(item)
    assert result["decision"] == expected_decision
    assert result["quote_records"] == []
    assert result["total_quote_ecu"] == "0"


def test_lineage_materialization_and_economic_scope_stay_local() -> None:
    results = sim.build_results()
    assert results["scope"] == "bounded_local_fixture_only"
    assert results["economic_effect"] == "simulated_quote_only"
    for item in results["scenarios"]:
        assert item["materialization_status"] == "unresolved"
        assert item["canonical_genesis_lineage"] == "local_only_not_applicable"


def test_output_is_deterministic_and_contains_no_float() -> None:
    left = sim.build_results()
    right = sim.build_results()
    assert sim.canonical_json_bytes(left) == sim.canonical_json_bytes(right)
    assert not _contains_float(left)


def test_decimal_quote_is_independent_of_ambient_context() -> None:
    with localcontext() as context:
        context.prec = 4
        low_precision = sim.explicit_provenance_quote(3)
    with localcontext() as context:
        context.prec = 28
        normal_precision = sim.explicit_provenance_quote(3)
    assert low_precision == normal_precision == Decimal("0.0182250")


def test_structured_deduplication_key_cannot_collide_on_separator_text() -> None:
    left = sim._quote(
        event_id="event|channel",
        channel="basis",
        contribution_basis="recipient",
        recipient_id="agent",
        amount=Decimal("0.1"),
        authority_ref="fixture",
    )
    right = sim._quote(
        event_id="event",
        channel="channel|basis",
        contribution_basis="recipient",
        recipient_id="agent",
        amount=Decimal("0.1"),
        authority_ref="fixture",
    )
    assert left["deduplication_key"] != right["deduplication_key"]


def test_atomic_output_round_trip(tmp_path: Path) -> None:
    results = sim.write_outputs(tmp_path)
    loaded = json.loads((tmp_path / "sim_results.json").read_text(encoding="utf-8"))
    assert loaded == results
    assert "No ECU accrued" in (tmp_path / "sim_summary.md").read_text(encoding="utf-8")
    assert not list(tmp_path.glob(".*.sim_results.json.*"))


def test_unknown_field_rejected() -> None:
    item = _inputs()[0]
    item["unknown"] = True
    with pytest.raises(ValueError, match="sim_scenario_schema_invalid"):
        sim.evaluate_scenario(item)


def test_float_event_budget_rejected() -> None:
    item = _inputs()[0]
    item["event_budget_ecu"] = 1.0
    with pytest.raises(ValueError, match="sim_event_budget_invalid"):
        sim.evaluate_scenario(item)


def test_bool_repetition_rejected() -> None:
    item = _inputs()[0]
    item["repetitions"] = True
    with pytest.raises(ValueError, match="sim_repetitions_invalid"):
        sim.evaluate_scenario(item)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_budget_rejected(value: str) -> None:
    item = _inputs()[0]
    item["event_budget_ecu"] = value
    with pytest.raises(ValueError, match="sim_event_budget_invalid"):
        sim.evaluate_scenario(item)


def test_invalid_scenario_id_rejected() -> None:
    item = _inputs()[0]
    item["scenario_id"] = "not-a-scenario"
    with pytest.raises(ValueError, match="sim_scenario_id_invalid"):
        sim.evaluate_scenario(item)


def test_bad_event_id_rejected() -> None:
    item = _inputs()[0]
    item["event_id"] = " event "
    with pytest.raises(ValueError, match="sim_event_id_invalid"):
        sim.evaluate_scenario(item)


def test_oversized_event_id_and_decimal_text_reject_before_output() -> None:
    event_item = _inputs()[0]
    event_item["event_id"] = "x" * 257
    with pytest.raises(ValueError, match="sim_event_id_invalid"):
        sim.evaluate_scenario(event_item)

    decimal_item = _inputs()[0]
    decimal_item["event_budget_ecu"] = "1" * 129
    with pytest.raises(ValueError, match="sim_event_budget_invalid"):
        sim.evaluate_scenario(decimal_item)


def test_bad_assessment_schema_rejected() -> None:
    item = _inputs()[0]
    item["assessments"] = {"computational_contract": "affirmative"}
    with pytest.raises(ValueError, match="sim_assessments_schema_invalid"):
        sim.evaluate_scenario(item)


def test_bad_assessment_enum_rejected() -> None:
    item = _inputs()[0]
    item["assessments"]["current_observer_permission"] = "trusted_enough"
    with pytest.raises(ValueError, match="sim_assessment_value_invalid"):
        sim.evaluate_scenario(item)


def test_duplicate_or_missing_scenario_set_rejected() -> None:
    inputs = _inputs()
    inputs[-1] = dict(inputs[0])
    with pytest.raises(ValueError, match="sim_scenario_identity_set_invalid"):
        sim.build_results(inputs)
    with pytest.raises(ValueError, match="sim_scenario_count_invalid"):
        sim.build_results(_inputs()[:-1])


@pytest.mark.parametrize("hop", [0, 4, True])
def test_invalid_explicit_provenance_hop_rejected(hop: object) -> None:
    with pytest.raises(ValueError, match="explicit_provenance_hop_invalid"):
        sim.explicit_provenance_quote(hop)


def test_output_size_cap_fails_before_publish(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sim, "MAX_OUTPUT_BYTES", 16)
    with pytest.raises(ValueError, match="sim_output_exceeds_maximum_bytes"):
        sim.write_outputs(tmp_path)
    assert not (tmp_path / "sim_results.json").exists()
