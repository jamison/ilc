from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

from ilc_core.validator import staking_liveness_runtime
from ilc_core.validator import re_admission_runtime

MODULE_PATH = Path("ilc_core/validator/re_admission_runtime.py")
TEST_PATH = Path("tests/test_phase_521_re_admission_runtime.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_521_SUBJECT_TOKEN = "phase 521 cdl-058 re_admission runtime"
EXACT_REQUIRED_MAIN_PATHS = {
    str(MODULE_PATH),
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


def _resolve_phase_521_commit_ref() -> str:
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
        if PHASE_521_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_521_commit_subject_present_but_no_qualifying_runtime_commit")
    raise AssertionError("phase_521_commit_not_present_in_local_history")


def test_module_imports() -> None:
    module = importlib.import_module("ilc_core.validator.re_admission_runtime")
    assert module.RE_ADMISSION_RUNTIME_VERSION == "re_admission_runtime_521.v0.1"


def test_runtime_version_constant_value() -> None:
    assert re_admission_runtime.RE_ADMISSION_RUNTIME_VERSION == "re_admission_runtime_521.v0.1"


def test_cdl_058_dependency_constant_value() -> None:
    assert re_admission_runtime.CDL_058_DEPENDENCY == "cdl_058_ratified_520.v0.1"


def test_cdl_055_staking_dependency_chain() -> None:
    assert (
        re_admission_runtime.CDL_055_STAKING_DEPENDENCY
        == staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
    )


def test_exit_reasons_contains_exact_required_members() -> None:
    assert re_admission_runtime.EXIT_REASONS == frozenset(
        ("liveness_miss", "equivocation", "voluntary_exit")
    )


def test_cooldown_constants_match_sim_011_and_preserve_ordering() -> None:
    assert re_admission_runtime.COOLDOWN_EPOCHS_LIVENESS_MISS == 2
    assert re_admission_runtime.COOLDOWN_EPOCHS_EQUIVOCATION == 12
    assert re_admission_runtime.COOLDOWN_EPOCHS_VOLUNTARY_EXIT == 1
    assert (
        re_admission_runtime.COOLDOWN_EPOCHS_EQUIVOCATION
        > re_admission_runtime.COOLDOWN_EPOCHS_LIVENESS_MISS
    )


def test_evaluate_re_admission_eligibility_returns_true_after_liveness_cooldown() -> None:
    assert re_admission_runtime.evaluate_re_admission_eligibility("liveness_miss", 2) == {
        "eligible": True,
        "cooldown_remaining": 0,
    }


def test_evaluate_re_admission_eligibility_returns_false_below_equivocation_cooldown() -> None:
    assert re_admission_runtime.evaluate_re_admission_eligibility("equivocation", 11) == {
        "eligible": False,
        "cooldown_remaining": 1,
    }


def test_evaluate_re_admission_eligibility_raises_for_unrecognized_exit_reason() -> None:
    try:
        re_admission_runtime.evaluate_re_admission_eligibility("governance_vote", 0)
    except ValueError as exc:
        assert str(exc) == "unrecognized_exit_reason"
    else:
        raise AssertionError("expected ValueError for unrecognized exit reason")


def test_evaluate_re_admission_eligibility_rejects_negative_epoch_count() -> None:
    try:
        re_admission_runtime.evaluate_re_admission_eligibility("voluntary_exit", -1)
    except ValueError as exc:
        assert str(exc) == "epochs_since_exit_must_be_non_negative_int"
    else:
        raise AssertionError("expected ValueError for negative epochs_since_exit")


def test_phase_521_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_521_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_521_main_commit_does_not_touch_cdl_or_quorum_paths() -> None:
    commit_ref = _resolve_phase_521_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/consensus/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/epoch/") for path in changed_paths)
