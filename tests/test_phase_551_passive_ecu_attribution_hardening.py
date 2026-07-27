from __future__ import annotations

import subprocess
from decimal import Decimal
from pathlib import Path

from ilc_core.economics import passive_ecu_attribution_runtime as runtime

RUNTIME_PATH = Path("ilc_core/economics/passive_ecu_attribution_runtime.py")
PHASE_550_TEST_PATH = Path("tests/test_phase_550_passive_ecu_attribution_runtime.py")
TEST_PATH_551 = Path("tests/test_phase_551_passive_ecu_attribution_hardening.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_551_SUBJECT_TOKEN = "phase 551 passive ecu attribution hardening"
EXACT_REQUIRED_MAIN_PATHS = {
    str(RUNTIME_PATH),
    str(TEST_PATH_551),
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_551_commit_ref() -> str:
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
        if PHASE_551_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError("phase_551_commit_not_present_in_local_history")


def _assert_phase_551_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert str(PHASE_550_TEST_PATH) not in changed_paths
    assert all(
        not path.startswith("ilc_core/") or path.startswith("ilc_core/economics/")
        for path in changed_paths
    )


def test_cap_binding_proof_scales_with_base_reward() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("10"), Decimal("1"), Decimal("1")
    ) == Decimal("1.500000000000")


def test_quality_factor_extremes_produce_expected_passive_ecu_values() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("1"), Decimal("0.5"), Decimal("0")
    ) == Decimal("0.085000000000")
    assert runtime.compute_passive_ecu(
        Decimal("1"), Decimal("0.5"), Decimal("1")
    ) == Decimal("0.115000000000")


def test_decay_floor_boundary_is_inclusive_for_quality_extremes() -> None:
    assert runtime.compute_passive_ecu(
        Decimal("1"), runtime.DECAY_FLOOR, Decimal("0")
    ) > Decimal("0")
    assert runtime.compute_passive_ecu(
        Decimal("1"), runtime.DECAY_FLOOR, Decimal("1")
    ) > Decimal("0")


def test_authorship_primacy_holds_for_full_grid() -> None:
    for centrality_score in (Decimal("0.05"), Decimal("0.5"), Decimal("1")):
        for q_i in (Decimal("0"), Decimal("0.5"), Decimal("1")):
            assert runtime.compute_passive_ecu(Decimal("1"), centrality_score, q_i) < Decimal("1")


def test_negative_base_reward_raises_value_error() -> None:
    try:
        runtime.compute_passive_ecu(Decimal("-1"), Decimal("0.5"), Decimal("0.5"))
    except ValueError as exc:
        assert str(exc) == "base_reward_must_be_non_negative_decimal"
    else:
        raise AssertionError("expected ValueError for negative base_reward")


def test_phase_551_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_551_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(PHASE_550_TEST_PATH) not in changed_paths


def test_phase_551_main_commit_scope_is_limited_to_passive_ecu_runtime() -> None:
    commit_ref = _resolve_phase_551_commit_ref()
    _assert_phase_551_runtime_mutation_scope(commit_ref)
