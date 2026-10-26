from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from tools.sufficiency_benchmark.run_benchmark import (
    MAX_OUTPUT_BYTES,
    MIN_SAMPLES,
    PATHS,
    PHASES,
    RETRIEVAL_STRATEGIES,
    REUSE_MODES,
    WORKLOADS,
    BenchmarkError,
    FixtureStore,
    ResourceLimitError,
    _record,
    _atomic_write,
    _find_run,
    acquire_objects,
    build_fixture,
    build_results,
    exact_cache_key,
    execute_target,
    expected_behavior,
    independent_expected_output,
    semantic_cache_key,
    write_outputs,
)


@pytest.fixture(scope="module")
def results() -> dict:
    return build_results(warmups=2, samples=9, kernel_rounds=8)


def run_at(results: dict, workload: str, mode: str, strategy: str, path: str) -> dict:
    return dict(_find_run(results, workload, mode, strategy, path))


def test_complete_matrix_and_required_workloads(results: dict) -> None:
    assert [item["workload_id"] for item in results["workloads"]] == [
        item.workload_id for item in WORKLOADS
    ]
    assert results["matrix"]["logical_cells"] == 84
    assert results["matrix"]["run_records"] == 168
    assert sum(len(item["runs"]) for item in results["workloads"]) == 168
    coordinates = {
        (workload["workload_id"], run["reuse_mode"], run["retrieval_strategy"], run["path"])
        for workload in results["workloads"]
        for run in workload["runs"]
    }
    assert len(coordinates) == 168


def test_independent_oracle_is_exact() -> None:
    expected = {
        (0, 0, 0): 0,
        (1, 2, 0): 3,
        (1, 2, 2): 3,
        (2, 1, 2): 3,
    }
    assert {value: independent_expected_output(value) for value in expected} == expected
    with pytest.raises(BenchmarkError, match="oracle_input_invalid"):
        independent_expected_output((True, 2, 0))


@pytest.mark.parametrize("strategy", RETRIEVAL_STRATEGIES)
def test_different_equivalent_exact_misses_semantic_hits(results: dict, strategy: str) -> None:
    exact = run_at(
        results,
        "different_inputs_equivalent_operation",
        "ordinary_exact_input_cache",
        strategy,
        "warm",
    )
    semantic = run_at(
        results,
        "different_inputs_equivalent_operation",
        "sufficiency_semantic_reuse",
        strategy,
        "warm",
    )
    assert (exact["cache_hits"], exact["operation_calls"], exact["output"]) == (0, 1, 3)
    assert (semantic["cache_hits"], semantic["operation_calls"], semantic["output"]) == (1, 0, 3)


@pytest.mark.parametrize("strategy", RETRIEVAL_STRATEGIES)
def test_identical_input_exact_cache_hits(results: dict, strategy: str) -> None:
    run = run_at(
        results,
        "identical_inputs",
        "ordinary_exact_input_cache",
        strategy,
        "warm",
    )
    assert run["verdict"] == "authorized_reuse"
    assert run["cache_hits"] == 1
    assert run["operation_calls"] == 0


@pytest.mark.parametrize("workload_id", ["low_reuse", "changed_dependencies", "changed_operation_scope"])
def test_semantic_cache_misses_when_equivalence_namespace_changes(
    results: dict, workload_id: str
) -> None:
    run = run_at(
        results,
        workload_id,
        "sufficiency_semantic_reuse",
        "typed_mandatory_evidence_closure",
        "warm",
    )
    assert run["cache_hits"] == 0
    assert run["operation_calls"] == 1
    if workload_id != "low_reuse":
        assert run["invalidations"] == 1


def test_cache_keys_bind_operation_contract_checker_scope_and_dependency() -> None:
    workload = next(item for item in WORKLOADS if item.workload_id == "changed_operation_scope")
    assert exact_cache_key(workload, workload.prime_input, prime=True) != exact_cache_key(
        workload, workload.target_input, prime=False
    )
    assert semantic_cache_key(workload, workload.prime_input, prime=True) != semantic_cache_key(
        workload, workload.target_input, prime=False
    )


@pytest.mark.parametrize("mode", REUSE_MODES)
@pytest.mark.parametrize("strategy", RETRIEVAL_STRATEGIES)
def test_invalid_substitution_claim_does_not_block_authorized_direct_computation(
    results: dict, mode: str, strategy: str
) -> None:
    run = run_at(results, "invalid_sufficiency_claim", mode, strategy, "warm")
    assert run["verdict"] == "authorized_direct_computation"
    assert run["output"] == 3
    assert run["operation_calls"] == 1
    assert run["cache_hits"] == 0
    assert run["object_reads"] > 0


def test_generic_and_typed_retrieval_are_distinct() -> None:
    workload = next(item for item in WORKLOADS if item.workload_id == "noninterference")
    store, root, _ = build_fixture(workload)
    generic = acquire_objects(store, root, "generic_dependency_aware")
    typed = acquire_objects(store, root, "typed_mandatory_evidence_closure")
    assert generic["typed_contract_used"] is False
    assert typed["typed_contract_used"] is True
    assert typed["object_reads"] < generic["object_reads"]
    assert typed["bytes_acquired"] < generic["bytes_acquired"]


def test_typed_traversal_validates_every_incoming_role_even_when_target_seen() -> None:
    workload = next(item for item in WORKLOADS if item.workload_id == "identical_inputs")
    store, root_id, named = build_fixture(workload)
    records = [copy.deepcopy(store._records[item]) for item in store.ids()]
    root = next(item for item in records if item["object_id"] == root_id)
    refs = [dict(item) for item in root["refs"]]
    next(item for item in refs if item["role"] == "claim")["target"] = named["view"]
    records.remove(root)
    replacement = _record(root["object_type"], root["data"], tuple(
        (item["role"], item["target"], item["required"]) for item in refs
    ))
    records.append(replacement)
    malformed = FixtureStore(records)
    with pytest.raises(BenchmarkError, match="typed_role_target_invalid"):
        acquire_objects(
            malformed,
            replacement["object_id"],
            "typed_mandatory_evidence_closure",
        )


def test_fixture_store_stops_unbounded_iterable_at_cap() -> None:
    produced = 0

    def records():
        nonlocal produced
        while True:
            produced += 1
            yield _record("fixture", {"value": produced})

    with pytest.raises(ResourceLimitError, match="store_object_limit_exceeded"):
        FixtureStore(records())
    assert produced == 65


def test_fixture_store_is_immutable_from_caller_mutation() -> None:
    record = _record("audit_note", {"nested": {"value": "original"}})
    store = FixtureStore((record,))
    record["data"]["nested"]["value"] = "mutated"

    loaded, _ = store.get(next(iter(store.ids())))

    assert loaded["data"]["nested"]["value"] == "original"


def test_retrieval_cost_order_and_same_substantive_output(results: dict) -> None:
    runs = {
        strategy: run_at(results, "noninterference", "direct_computation", strategy, "cold")
        for strategy in RETRIEVAL_STRATEGIES
    }
    assert {run["output"] for run in runs.values()} == {3}
    assert {run["verdict"] for run in runs.values()} == {"authorized_direct_computation"}
    assert runs["typed_mandatory_evidence_closure"]["object_reads"] < runs[
        "generic_dependency_aware"
    ]["object_reads"]
    assert runs["generic_dependency_aware"]["object_reads"] <= runs[
        "literal_all_reference_traversal"
    ]["object_reads"]
    assert runs["literal_all_reference_traversal"]["object_reads"] <= runs[
        "full_bounded_store"
    ]["object_reads"]


def test_noninterference_and_low_cap_are_separate(results: dict) -> None:
    workload = next(item for item in results["workloads"] if item["workload_id"] == "noninterference")
    assert workload["noninterference_invariant_holds"] is True
    assert results["resource_cap_probe"] == {
        "read_cap": 8,
        "full_bounded_store": "resource_exhausted",
        "typed_mandatory_evidence_closure": "authorized_direct_computation",
        "underlying_claim_refuted": False,
    }


def test_resource_exhaustion_reports_work_already_performed() -> None:
    workload = next(item for item in WORKLOADS if item.workload_id == "noninterference")
    run = execute_target(
        workload,
        "direct_computation",
        "full_bounded_store",
        path="cold",
        rounds=1,
        read_cap=2,
    )
    assert run["verdict"] == "resource_exhausted"
    assert run["counters"]["object_reads"] == 2
    assert run["counters"]["bytes_acquired"] > 0
    assert run["phase_ns"]["retrieval"] > 0


def test_noninterference_fixture_actually_adds_unrelated_objects() -> None:
    baseline = next(item for item in WORKLOADS if item.workload_id == "identical_inputs")
    noninterference = next(item for item in WORKLOADS if item.workload_id == "noninterference")
    baseline_store, baseline_root, _ = build_fixture(baseline)
    expanded_store, expanded_root, _ = build_fixture(noninterference)
    baseline_full = acquire_objects(baseline_store, baseline_root, "full_bounded_store")
    expanded_full = acquire_objects(expanded_store, expanded_root, "full_bounded_store")
    assert expanded_full["object_reads"] == baseline_full["object_reads"] + 2
    assert expanded_full["bytes_acquired"] > baseline_full["bytes_acquired"]


def test_all_timing_samples_are_complete_and_nonnegative(results: dict) -> None:
    for workload in results["workloads"]:
        for run in workload["runs"]:
            assert len(run["duration_samples_ns"]) == MIN_SAMPLES
            assert all(type(item) is int and item >= 0 for item in run["duration_samples_ns"])
            assert set(run["phase_duration_samples_ns"]) == set(PHASES)
            for samples in run["phase_duration_samples_ns"].values():
                assert len(samples) == MIN_SAMPLES
                assert all(type(item) is int and item >= 0 for item in samples)
            assert run["duration_samples_ns"] == [
                sum(run["phase_duration_samples_ns"][phase][index] for phase in PHASES)
                for index in range(MIN_SAMPLES)
            ]


def test_interleaved_order_and_warm_priming_are_recorded(results: dict) -> None:
    run = run_at(
        results,
        "different_inputs_equivalent_operation",
        "sufficiency_semantic_reuse",
        "typed_mandatory_evidence_closure",
        "warm",
    )
    assert len(set(run["sample_order_indices"])) > 1
    assert run["priming_action"]["performed"] is True
    assert run["priming_action"]["kind"] == "semantic_cache_prime"
    assert len(run["priming_action"]["duration_samples_ns"]) == MIN_SAMPLES


def test_cold_paths_do_not_prime(results: dict) -> None:
    run = run_at(
        results,
        "identical_inputs",
        "ordinary_exact_input_cache",
        "typed_mandatory_evidence_closure",
        "cold",
    )
    assert run["priming_action"]["performed"] is False
    assert run["cache_hits"] == 0
    assert run["operation_calls"] == 1


def test_exact_counter_units_and_measurement_nonclaims(results: dict) -> None:
    assert results["instrumentation_boundaries"] == {
        "bytes_acquired": "canonical JSON bytes of locally acquired fixture objects",
        "retained_cache_bytes": "canonical JSON bytes of retained key/value cache entries",
        "process_memory_measured": False,
        "network_bytes_measured": False,
        "energy_measured": False,
        "priming_excluded_from_target_duration": True,
    }
    for workload in results["workloads"]:
        for run in workload["runs"]:
            assert run["counter_units"]["bytes_acquired"] == "canonical_local_fixture_bytes"
            assert run["bytes_acquired"] > 0
            assert run["object_reads"] > 0


def test_model_selector_accounting_is_separate(results: dict) -> None:
    fixture = results["model_selector_fixture"]
    assert fixture["included"] is True
    assert fixture["separate_from_matrix"] is True
    assert fixture["outcome"] == "selected"
    assert results["matrix"]["logical_cells"] == 84


def test_expected_behavior_table_is_independent_of_measured_timings() -> None:
    workload = next(
        item for item in WORKLOADS if item.workload_id == "different_inputs_equivalent_operation"
    )
    assert expected_behavior(workload, "ordinary_exact_input_cache", "warm") == {
        "verdict": "authorized_direct_computation",
        "output": 3,
        "cache_hits": 0,
        "operation_calls": 1,
    }
    assert expected_behavior(workload, "sufficiency_semantic_reuse", "warm") == {
        "verdict": "authorized_reuse",
        "output": 3,
        "cache_hits": 1,
        "operation_calls": 0,
    }


def test_atomic_output_is_parseable_and_bounded(results: dict, tmp_path: Path) -> None:
    results_path, summary_path = write_outputs(results, tmp_path)
    assert json.loads(results_path.read_text()) == results
    assert results_path.stat().st_size <= MAX_OUTPUT_BYTES
    assert "No transferable" in summary_path.read_text()
    assert not list(tmp_path.glob(".*.tmp"))


def test_atomic_output_rejects_oversize(tmp_path: Path) -> None:
    target = tmp_path / "too-large.bin"
    with pytest.raises(ResourceLimitError, match="output_bytes_limit_exceeded"):
        _atomic_write(target, b"x" * (MAX_OUTPUT_BYTES + 1))
    assert not target.exists()


def test_atomic_output_cleans_temporary_file_when_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "replace-failure.bin"

    def fail_replace(_source: str, _target: Path) -> None:
        raise OSError("fixture replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="fixture replace failure"):
        _atomic_write(target, b"payload")
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_measurement_contract_rejects_too_few_samples() -> None:
    with pytest.raises(BenchmarkError, match="measurement_repetition_contract_invalid"):
        build_results(warmups=2, samples=8, kernel_rounds=1)


def test_no_mode_uses_cache_as_authority(results: dict) -> None:
    for mode in REUSE_MODES:
        for strategy in RETRIEVAL_STRATEGIES:
            warm = run_at(results, "identical_inputs", mode, strategy, "warm")
            assert warm["authentication_checks"] == 2
            assert warm["freshness_checks"] == 1
            assert warm["authority_view_deliveries"] == 1
