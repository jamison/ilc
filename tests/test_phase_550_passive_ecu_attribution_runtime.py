from __future__ import annotations

import importlib
import subprocess
from decimal import Decimal
from pathlib import Path

from ilc_core.economics import passive_ecu_attribution_runtime as runtime

RUNTIME_PATH = Path("ilc_core/economics/passive_ecu_attribution_runtime.py")
TEST_PATH = Path("tests/test_phase_550_passive_ecu_attribution_runtime.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_550_SUBJECT_TOKEN = "phase 550 passive ecu attribution runtime"
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(TEST_PATH),
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _name_status_for_commit(commit_ref: str) -> dict[str, str]:
    result = subprocess.run(
        ["git", "show", "--name-status", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    statuses: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        status, path = parts
        statuses[path] = status
    return statuses


def _resolve_phase_550_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_550_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError("phase_550_commit_not_present_in_local_history")


def _assert_phase_550_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    name_status = _name_status_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert all(
        not path.startswith("ilc_core/") or path.startswith("ilc_core/economics/")
        for path in changed_paths
    )
    assert name_status[str(RUNTIME_PATH)] == "A"
    assert name_status[str(TEST_PATH)] == "A"


def test_module_imports_without_error() -> None:
    module = importlib.import_module("ilc_core.economics.passive_ecu_attribution_runtime")
    assert module.PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION == "passive_ecu_attribution_runtime_550.v0.1"


def test_all_constants_have_exact_expected_values() -> None:
    assert runtime.PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION == "passive_ecu_attribution_runtime_550.v0.1"
    assert runtime.CDL_060_DEPENDENCY == "cdl_060_ratified_541.v0.1"
    assert runtime.CDL_060_GOSSIP_RUNTIME_DEPENDENCY == "centrality_delta_gossip_runtime_GAP_CDL060.v0.2"
    assert runtime.PASSIVE_ATTRIBUTION_RATE == Decimal("0.20")
    assert runtime.DECAY_FLOOR == Decimal("0.05")
    assert runtime.ATTRIBUTION_CAP == Decimal("0.15")
    assert runtime.GAMMA == Decimal("0.15")


def test_authorship_primacy_contract_validation_is_present_in_source() -> None:
    text = RUNTIME_PATH.read_text(encoding="utf-8")
    assert "def _validate_runtime_contract()" in text
    assert "PassiveECUAttributionContractError" in text
    assert 'PASSIVE_ATTRIBUTION_RATE * (Decimal("1") + GAMMA) >= Decimal("1")' in text
    assert 'ATTRIBUTION_CAP >= Decimal("1")' in text


def test_quality_factor_matches_expected_bounds_and_neutral_midpoint() -> None:
    assert runtime.quality_factor(Decimal("0")) == Decimal("0.850000000000")
    assert runtime.quality_factor(Decimal("1")) == Decimal("1.150000000000")
    assert runtime.quality_factor(Decimal("0.5")) == Decimal("1.000000000000")


def test_compute_passive_ecu_returns_zero_below_decay_floor() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("1"), Decimal("0.04"), Decimal("0.5")
    ) == Decimal("0")


def test_compute_passive_ecu_returns_zero_for_zero_base_reward() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("0"), Decimal("1"), Decimal("0.5")
    ) == Decimal("0")


def test_compute_passive_ecu_applies_output_layer_cap() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("1"), Decimal("1"), Decimal("1")
    ) == Decimal("0.150000000000")


def test_compute_passive_ecu_returns_uncapped_value_when_below_cap() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("1"), Decimal("0.5"), Decimal("0.5")
    ) == Decimal("0.100000000000")


def test_quality_factor_rejects_scores_outside_unit_interval() -> None:
    for invalid in (Decimal("-0.01"), Decimal("1.01")):
        try:
            runtime.quality_factor(invalid)
        except ValueError as exc:
            assert str(exc) == "q_i_must_be_float_in_unit_interval"
        else:
            raise AssertionError("expected ValueError for invalid quality score")


def test_source_contains_gossip_runtime_dependency_validation() -> None:
    text = RUNTIME_PATH.read_text(encoding="utf-8")
    assert "_CDL_060_GOSSIP_RUNTIME_CHECK != CDL_060_GOSSIP_RUNTIME_DEPENDENCY" in text
    assert "passive_ecu_dependency_mismatch" in text


def test_phase_550_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_550_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_550_main_commit_scope_is_limited_to_new_economics_runtime() -> None:
    commit_ref = _resolve_phase_550_commit_ref()
    _assert_phase_550_runtime_mutation_scope(commit_ref)
