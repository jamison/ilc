from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.popperian_gate_runtime import (
    CDL_V3_DEPENDENCY,
    CDL_V7_DEPENDENCY,
    CDL_V7_RUNTIME_VERSION,
    PopperianGateValidationError,
    evaluate_decomposition_admissibility,
    is_claim_form_admissible,
    meets_reproducibility_threshold,
    passes_falsifiability_gate,
    reject_inadmissible_counterexample,
)


RUNTIME_INIT_PATH = Path("ilc_core/consensus/__init__.py")
RUNTIME_PATH = Path("ilc_core/consensus/popperian_gate_runtime.py")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_v7_popperian_gate_runtime_handoff_398_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "feat(g8): phase 398 cdl-v7 popperian gate runtime"

AUTHORIZED_RUNTIME_PATHS = {
    "ilc_core/consensus/__init__.py",
    "ilc_core/consensus/popperian_gate_runtime.py",
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_398_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() == SUBJECT_TOKEN.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "ilc_core/consensus/__init__.py",
        "ilc_core/consensus/popperian_gate_runtime.py",
        "docs/specs/ilc_cdl_v7_popperian_gate_runtime_handoff_398_v0.1.md",
        "tests/test_cdl_v7_popperian_gate_runtime_398.py",
    }

    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_398_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_398_commit_not_present_in_local_history")


def _assert_v_series_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed

    # Positive check: at least one consensus runtime path changed.
    assert any(path.startswith("ilc_core/consensus/") for path in changed), (
        "phase_398_consensus_mutation_missing"
    )

    # Negative check: no ilc_core path outside ilc_core/consensus/ changed.
    non_consensus_ilc_core = [
        path for path in changed if path.startswith("ilc_core/") and not path.startswith("ilc_core/consensus/")
    ]
    assert not non_consensus_ilc_core, (
        f"phase_398_ilc_core_scope_violation:{non_consensus_ilc_core}"
    )

    assert any(path in changed for path in AUTHORIZED_RUNTIME_PATHS), "phase_398_authorized_runtime_missing"

    unexpected_consensus = [
        path
        for path in changed
        if path.startswith("ilc_core/consensus/") and path not in AUTHORIZED_RUNTIME_PATHS
    ]
    assert not unexpected_consensus, f"phase_398_consensus_scope_violation:{unexpected_consensus}"


def test_runtime_paths_exist() -> None:
    assert RUNTIME_INIT_PATH.exists()
    assert RUNTIME_PATH.exists()


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert CDL_V7_RUNTIME_VERSION == "cdl_v7_popperian_gate_runtime_398.v0.1"
    assert CDL_V7_DEPENDENCY == "cdl_v7_popperian_gate_398.v0.1"
    assert CDL_V3_DEPENDENCY == "cdl_v3_diversity_floor_397.v0.1"


def test_claim_form_admissibility_for_ratified_forms() -> None:
    assert is_claim_form_admissible(claim_form="singular")
    assert is_claim_form_admissible(claim_form="existential")
    assert is_claim_form_admissible(claim_form="falsifiable_positive")
    assert not is_claim_form_admissible(claim_form="inadmissible_counterexample")


def test_falsifiability_gate_requires_boolean_true() -> None:
    assert passes_falsifiability_gate(has_falsifiable_test=True)
    assert not passes_falsifiability_gate(has_falsifiable_test=False)


def test_inadmissible_counterexample_rejection_is_deterministic() -> None:
    assert reject_inadmissible_counterexample(is_inadmissible_counterexample=False)
    assert not reject_inadmissible_counterexample(is_inadmissible_counterexample=True)


def test_reproducibility_threshold_helper_bounds_and_threshold_compare() -> None:
    assert meets_reproducibility_threshold(agreement_score=0.90, reproducibility_threshold=0.85)
    assert not meets_reproducibility_threshold(agreement_score=0.80, reproducibility_threshold=0.85)


def test_top_level_admissibility_verdict_combines_all_constraints() -> None:
    assert evaluate_decomposition_admissibility(
        claim_form="singular",
        has_falsifiable_test=True,
        is_inadmissible_counterexample=False,
        agreement_score=0.90,
        reproducibility_threshold=0.85,
    )
    assert not evaluate_decomposition_admissibility(
        claim_form="singular",
        has_falsifiable_test=False,
        is_inadmissible_counterexample=False,
        agreement_score=0.90,
        reproducibility_threshold=0.85,
    )


def test_invalid_claim_form_type_raises_tokenized_error() -> None:
    with pytest.raises(PopperianGateValidationError) as exc:
        is_claim_form_admissible(claim_form=123)  # type: ignore[arg-type]
    assert exc.value.token == "cdl_v7_popperian_invalid_string"


def test_invalid_bool_and_out_of_range_numeric_raise_tokenized_errors() -> None:
    with pytest.raises(PopperianGateValidationError) as exc_bool:
        passes_falsifiability_gate(has_falsifiable_test="yes")  # type: ignore[arg-type]
    assert exc_bool.value.token == "cdl_v7_popperian_invalid_bool"

    with pytest.raises(PopperianGateValidationError) as exc_num:
        meets_reproducibility_threshold(agreement_score=1.2, reproducibility_threshold=0.85)
    assert exc_num.value.token == "cdl_v7_popperian_out_of_range"

    with pytest.raises(PopperianGateValidationError) as exc_nan:
        meets_reproducibility_threshold(
            agreement_score=float("nan"),
            reproducibility_threshold=0.85,
        )
    assert exc_nan.value.token == "cdl_v7_popperian_invalid_numeric"

    with pytest.raises(PopperianGateValidationError) as exc_inf:
        meets_reproducibility_threshold(
            agreement_score=0.9,
            reproducibility_threshold=float("inf"),
        )
    assert exc_inf.value.token == "cdl_v7_popperian_invalid_numeric"


def test_handoff_artifact_has_required_headings_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. Popperian-gate computational model statement",
        "## 4. Deterministic failure-token catalog",
        "## 5. Mutation-scope boundary statement",
        "## 6. Carry-forward constraints for Phase 399",
        "## 7. Non-goals",
    ):
        assert heading in text

    for token in (
        'CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"',
        "CDL-V7 Popperian-gate enforcement is computational and deterministic.",
        "Phase 398 uses Phase-396 authorization targets as binding scope.",
        "Phase 398 implements ratified CDL-V7 constitutional text and does not treat SIM-006 placeholder capability tiers as runtime policy terms.",
        "No decision-log mutation occurred in Phase 398.",
    ):
        assert token in text


def test_phase_398_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_398_commit_ref_or_fail()
    _assert_v_series_mutation_scope(commit_ref)


def test_phase_398_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_398_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
