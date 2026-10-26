from __future__ import annotations

import json

import pytest

from tools.sim.sim_sufficiency_reuse_refinement_00 import (
    ASSESSMENT_KEYS,
    ObserverStore,
    ScenarioSpec,
    SimInvariantError,
    aggregate_decision,
    build_evidence_bundle,
    canonical_json,
    evaluate_request,
    execute_spec,
    finite_oracle,
    run_reuse_cycle,
    run_simulation,
    run_stateful_transition_checks,
    write_results,
    _record,
)


@pytest.fixture(scope="module")
def results():
    return run_simulation()


def _by_id(results):
    return {item["scenario_id"]: item for item in results["use_decision_scenarios"]}


def test_finite_oracle_recomputes_exact_pair_counts_and_witness():
    oracle = finite_oracle()
    assert oracle["domain_size"] == 27
    assert oracle["original_equal_representation_ordered_pairs"] == 81
    assert oracle["refined_equal_representation_ordered_pairs"] == 45
    assert oracle["original_claim_valid"] is True
    assert oracle["refined_parent_claim_valid"] is True
    assert oracle["separating_witness"] == {
        "s": [1, 2, 0],
        "t": [1, 2, 1],
        "same_original_representation": True,
        "different_parent_behavior": True,
        "separated_by_refinement": True,
    }


def test_eight_step_cycle_preserves_original_claim_and_separates_caches():
    cycle = run_reuse_cycle()
    assert len(cycle["events"]) == 8
    assert cycle["original_claim_id"] == cycle["original_claim_id_after_refinement"]
    assert cycle["refined_claim_id"] != cycle["original_claim_id"]
    assert cycle["exact_input_cache_hit"] is False
    assert cycle["operation_relative_cache_hit"] is True
    assert cycle["reused_output"] == 3
    assert len(set(cycle["cache_namespaces"].values())) == 4


def test_all_38_use_decisions_have_six_typed_assessments(results):
    scenarios = results["use_decision_scenarios"]
    assert len(scenarios) == 38
    for scenario in scenarios:
        assert tuple(scenario["assessments"]) == ASSESSMENT_KEYS
        assert scenario["assessments"]["structural_closure"] in {
            "complete", "missing", "contradictory", "resource_exhausted"
        }
        assert scenario["assessments"]["use_time_readiness"] in {
            "ready", "not_ready", "unresolved"
        }
        assert scenario["final_decision"] == scenario["expected_final_decision"]
        assert scenario["reason_codes"]
        assert scenario["evidence_refs"]


def test_aggregate_precedence_rejects_conclusive_computational_negative():
    assessments = {
        "structural_closure": "complete",
        "computational_contract": "negative",
        "historical_production_authority": "unresolved",
        "present_artifact_eligibility": "unresolved",
        "current_observer_permission": "unresolved",
        "use_time_readiness": "unresolved",
    }
    decision, reasons = aggregate_decision(assessments)
    assert decision == "rejected_use"
    assert "conclusive_negative:computational_contract" in reasons


@pytest.mark.parametrize("structural", ["missing", "contradictory", "resource_exhausted"])
def test_structural_failure_is_unresolved_not_mathematical_refutation(structural):
    assessments = {
        "structural_closure": structural,
        "computational_contract": "negative",
        "historical_production_authority": "negative",
        "present_artifact_eligibility": "negative",
        "current_observer_permission": "negative",
        "use_time_readiness": "not_ready",
    }
    assert aggregate_decision(assessments)[0] == "unresolved_pending_evidence"


def test_r9_has_events_zero_through_ten_and_replay_is_suppressed(results):
    r9 = [
        item for item in results["use_decision_scenarios"]
        if item["scenario_id"].startswith("R9_event_")
    ]
    assert len(r9) == 11
    assert {item["scenario_id"].split("_")[2] for item in r9} == {
        f"{index:02d}" for index in range(11)
    }
    event10 = next(item for item in r9 if "event_10" in item["scenario_id"])
    assert event10["delivery_applied"] is False
    assert event10["final_decision"] == "authorized_reuse"


def test_r9_variants_pin_exact_outcomes(results):
    scenarios = _by_id(results)
    expected = {
        "R9_variant_missing_output_bytes": "unresolved_pending_evidence",
        "R9_variant_corrupted_evidence": "unresolved_pending_evidence",
        "R9_variant_denied_access": "rejected_use",
        "R9_variant_exhausted_budget": "unresolved_pending_evidence",
        "R9_variant_checkpoint_policy_mismatch": "unresolved_pending_evidence",
        "R9_variant_incomplete_reverse_dependency_index": "unresolved_pending_evidence",
    }
    assert {key: scenarios[key]["final_decision"] for key in expected} == expected


def test_all_14_stateful_requirements_are_covered(results):
    scenarios = results["use_decision_scenarios"]
    assert {
        item["stateful_requirement"]
        for item in scenarios
        if item["stateful_requirement"] is not None
    } == set(range(1, 15))


def test_all_14_stateful_transitions_execute_and_pass(results):
    checks = results["stateful_transition_checks"]
    assert checks == run_stateful_transition_checks()
    assert set(checks) == {str(index) for index in range(1, 15)}
    assert all(item["passed"] is True for item in checks.values())
    assert checks["1"]["transitions"] == ["accepted", "stale_ignored"]
    assert checks["2"]["transition"] == "idempotent_replay"
    assert checks["3"]["transitions"] == ["equivocation", "accepted_recovery"]
    assert checks["6"]["before"] == "unresolved_pending_evidence"
    assert checks["6"]["after"] == "authorized_reuse"
    assert checks["9"]["corruption_rejected"] is True


def test_direct_binding_attacks_never_authorize(results):
    attacks = [
        item for item in results["use_decision_scenarios"]
        if item["scenario_id"].startswith("state_12")
    ]
    assert len(attacks) == 7
    assert {item["final_decision"] for item in attacks} == {
        "unresolved_pending_evidence"
    }
    assert all(
        item["assessments"]["current_observer_permission"] == "unresolved"
        for item in attacks
    )


def test_withdrawal_does_not_rewrite_historical_authority(results):
    item = _by_id(results)["state_11_withdrawal_after_cached_verification"]
    assert item["assessments"]["computational_contract"] == "affirmative"
    assert item["assessments"]["historical_production_authority"] == "affirmative"
    assert item["assessments"]["present_artifact_eligibility"] == "negative"
    assert item["final_decision"] == "rejected_use"


def test_failed_reuse_does_not_authorize_fallback(results):
    item = _by_id(results)["state_14_failed_reuse_does_not_authorize_fallback"]
    assert item["assessments"]["computational_contract"] == "unresolved"
    assert item["assessments"]["current_observer_permission"] == "unresolved"
    assert item["final_decision"] == "unresolved_pending_evidence"


def test_negative_mathematical_result_is_cached_as_negative_not_missing(results):
    item = _by_id(results)["state_07_negative_math_cached_as_negative"]
    assert item["assessments"]["structural_closure"] == "complete"
    assert item["assessments"]["computational_contract"] == "negative"
    assert item["final_decision"] == "rejected_use"


def test_operation_version_change_invalidates_computational_cache(results):
    item = _by_id(results)["state_08_operation_version_invalidates_cache"]
    assert item["request"]["operation"].endswith("@2")
    assert item["assessments"]["computational_contract"] == "unresolved"
    assert item["final_decision"] == "unresolved_pending_evidence"


def test_observer_decision_reads_only_its_local_store():
    spec = ScenarioSpec("isolation_probe", "A")
    refs, records = build_evidence_bundle(spec)
    store_a = ObserverStore("A")
    store_b = ObserverStore("B")
    store_a.deliver("event:a", records)
    result_a = evaluate_request(store_a, {
        "observer": "A", "network": "fixture:network:row35c",
        "scope": "fixture:scope:sufficiency-reuse",
        "operation": "fixture:operation:f@1",
        "invocation": "fixture:invocation:isolation_probe",
    }, refs)
    result_b = evaluate_request(store_b, {
        "observer": "A", "network": "fixture:network:row35c",
        "scope": "fixture:scope:sufficiency-reuse",
        "operation": "fixture:operation:f@1",
        "invocation": "fixture:invocation:isolation_probe",
    }, refs)
    assert result_a["final_decision"] == "authorized_reuse"
    assert result_b["assessments"]["structural_closure"] == "missing"
    assert result_b["final_decision"] == "unresolved_pending_evidence"


def test_same_event_delivery_is_idempotent_and_conflict_free():
    spec = ScenarioSpec("delivery_probe", "A")
    _, records = build_evidence_bundle(spec)
    store = ObserverStore("A")
    assert store.deliver("event:1", records) is True
    count = len(store.records)
    assert store.deliver("event:1", records) is False
    assert len(store.records) == count
    assert not store.conflicting_record_ids


def test_same_event_with_different_records_is_equivocation():
    store = ObserverStore("A")
    first = _record("policy", {"value": 1})
    second = _record("policy", {"value": 2})
    assert store.deliver("event:equivocation", [first]) is True
    with pytest.raises(SimInvariantError, match="delivery_event_equivocation"):
        store.deliver("event:equivocation", [second])
    assert second["record_id"] not in store.records


def test_delivery_record_cap_stops_bounded_generator():
    produced = 0

    def records():
        nonlocal produced
        while True:
            produced += 1
            yield _record("policy", {"value": produced})

    with pytest.raises(SimInvariantError, match="delivery_record_cap_exceeded"):
        ObserverStore("A").deliver("event:bounded", records())
    assert produced == 17


def test_delivery_recomputes_content_identity_before_storage():
    spec = ScenarioSpec("tamper_probe", "A")
    _, records = build_evidence_bundle(spec)
    records[-1]["data"]["sequence"] = 999
    store = ObserverStore("A")
    with pytest.raises(SimInvariantError, match="record_content_id_mismatch"):
        store.deliver("event:tampered", records)
    assert store.records == {}


def test_role_schema_malformation_is_typed_structural_failure():
    spec = ScenarioSpec("malformed_role_probe", "A")
    refs, records = build_evidence_bundle(spec)
    claim_index = next(i for i, record in enumerate(records) if record["kind"] == "sufficiency_claim")
    malformed_data = dict(records[claim_index]["data"])
    malformed_data["assessment"] = []
    malformed = _record("sufficiency_claim", malformed_data)
    refs["claim"] = malformed["record_id"]
    records[claim_index] = malformed
    store = ObserverStore("A")
    store.deliver("event:malformed-role", records)
    result = evaluate_request(store, {
        "observer": "A", "network": "fixture:network:row35c",
        "scope": "fixture:scope:sufficiency-reuse",
        "operation": "fixture:operation:f@1",
        "invocation": "fixture:invocation:malformed_role_probe",
    }, refs)
    assert result["assessments"]["structural_closure"] == "contradictory"
    assert result["final_decision"] == "unresolved_pending_evidence"


def test_evaluator_cannot_select_superseded_permissive_view():
    initial = ScenarioSpec("active_view_probe", "A")
    old_refs, old_records = build_evidence_bundle(initial)
    store = ObserverStore("A")
    store.deliver("event:view:13", old_records)

    withdrawn = ScenarioSpec("active_view_probe", "A", eligibility="negative")
    new_refs, new_records = build_evidence_bundle(withdrawn)
    view_index = next(i for i, record in enumerate(new_records) if record["kind"] == "active_authority_view")
    view_data = dict(new_records[view_index]["data"])
    view_data["sequence"] = 14
    new_view = _record("active_authority_view", view_data)
    new_records[view_index] = new_view
    new_refs["view"] = new_view["record_id"]
    store.deliver("event:view:14", new_records)

    request = {
        "observer": "A", "network": "fixture:network:row35c",
        "scope": "fixture:scope:sufficiency-reuse",
        "operation": "fixture:operation:f@1",
        "invocation": "fixture:invocation:active_view_probe",
    }
    stale = evaluate_request(store, request, old_refs)
    current = evaluate_request(store, request, new_refs)
    assert stale["final_decision"] != "authorized_reuse"
    assert current["final_decision"] == "rejected_use"


def test_evaluator_obeys_equivocation_stale_arrival_and_recovery():
    spec = ScenarioSpec("active_view_state_probe", "A")
    refs, records = build_evidence_bundle(spec)
    store = ObserverStore("A")
    store.deliver("event:view:initial", records)
    view_index = next(
        i for i, record in enumerate(records) if record["kind"] == "active_authority_view"
    )
    base_view = dict(records[view_index]["data"])

    conflict_data = dict(base_view)
    conflict_data["policy_ref"] = "sha256:" + "0" * 64
    conflict = _record("active_authority_view", conflict_data)
    store.deliver("event:view:conflict", (conflict,))
    request = {
        "observer": "A",
        "network": "fixture:network:row35c",
        "scope": "fixture:scope:sufficiency-reuse",
        "operation": "fixture:operation:f@1",
        "invocation": "fixture:invocation:active_view_state_probe",
    }
    assert evaluate_request(store, request, refs)["final_decision"] == (
        "unresolved_pending_evidence"
    )

    recovery_data = dict(base_view)
    recovery_data["sequence"] = 14
    recovery = _record("active_authority_view", recovery_data)
    store.deliver("event:view:recovery", (recovery,))
    assert evaluate_request(store, request, refs)["final_decision"] == "authorized_reuse"

    stale_data = dict(base_view)
    stale_data["sequence"] = 12
    stale = _record("active_authority_view", stale_data)
    store.deliver("event:view:stale", (stale,))
    assert evaluate_request(store, request, refs)["final_decision"] == "authorized_reuse"


def test_resource_cap_stops_before_semantic_evaluation():
    spec = ScenarioSpec(
        "resource_probe",
        "A",
        structural_mode="resource_exhausted",
        expected_final="unresolved_pending_evidence",
    )
    result = execute_spec(spec, ObserverStore("A"))
    assert result["assessments"] == {
        "structural_closure": "resource_exhausted",
        "computational_contract": "unresolved",
        "historical_production_authority": "unresolved",
        "present_artifact_eligibility": "unresolved",
        "current_observer_permission": "unresolved",
        "use_time_readiness": "unresolved",
    }


def test_receipts_use_local_only_lineage_envelope(results):
    for item in results["use_decision_scenarios"]:
        receipt = item["receipt"]
        assert receipt["canonical_genesis_lineage"] == "local_only_not_applicable"
        assert receipt["canonical_genesis_lineage"] != "not_evaluated"


def test_results_are_deterministic_and_atomic(tmp_path):
    first = write_results(tmp_path)
    first_bytes = (tmp_path / "reuse_refinement_results.json").read_bytes()
    second = write_results(tmp_path)
    second_bytes = (tmp_path / "reuse_refinement_results.json").read_bytes()
    assert first == second
    assert first_bytes == second_bytes
    assert canonical_json(json.loads(first_bytes)) == canonical_json(first)
    assert "graph_delta=none" in (
        tmp_path / "reuse_refinement_summary.md"
    ).read_text(encoding="utf-8")
