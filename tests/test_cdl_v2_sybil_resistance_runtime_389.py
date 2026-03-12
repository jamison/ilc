from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.identity.sybil_resistance_runtime import (
    CDL_V1_DEPENDENCY,
    CDL_V2_DEPENDENCY,
    CDL_V2_RUNTIME_VERSION,
    SybilResistanceValidationError,
    compute_burst_write_penalty,
    compute_diversity_floor_contribution,
    compute_identity_cluster_risk,
    compute_sybil_penalty,
)


RUNTIME_INIT_PATH = Path("ilc_core/identity/__init__.py")
RUNTIME_PATH = Path("ilc_core/identity/sybil_resistance_runtime.py")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_v2_sybil_resistance_runtime_handoff_389_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "feat(g8): phase 389 cdl-v2 sybil resistance runtime"

AUTHORIZED_RUNTIME_PATHS = {
    "ilc_core/identity/__init__.py",
    "ilc_core/identity/sybil_resistance_runtime.py",
}
FORBIDDEN_PREFIXES = (
    "ilc_core/consensus/",
    "ilc_core/security/",
    "ilc_core/ledger/",
    "ilc_core/issuance/",
    "ilc_core/schema/",
    "ilc_core/genesis/",
    "ilc_core/epoch/",
    "ilc_core/network/",
    "ilc_core/node/",
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_389_commit_ref_or_fail() -> str:
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
        "ilc_core/identity/__init__.py",
        "ilc_core/identity/sybil_resistance_runtime.py",
        "docs/specs/ilc_cdl_v2_sybil_resistance_runtime_handoff_389_v0.1.md",
        "tests/test_cdl_v2_sybil_resistance_runtime_389.py",
    }

    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_389_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_389_commit_not_present_in_local_history")


def _assert_v_series_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed
    assert any(path in changed for path in AUTHORIZED_RUNTIME_PATHS), "phase_389_authorized_runtime_missing"

    forbidden = [path for path in changed if path.startswith(FORBIDDEN_PREFIXES)]
    assert not forbidden, f"phase_389_forbidden_prefix_mutation:{forbidden}"

    unexpected_ilc_core = [
        path
        for path in changed
        if path.startswith("ilc_core/") and path not in AUTHORIZED_RUNTIME_PATHS
    ]
    assert not unexpected_ilc_core, f"phase_389_ilc_core_scope_violation:{unexpected_ilc_core}"


def test_runtime_paths_and_constants_exist() -> None:
    assert RUNTIME_INIT_PATH.exists()
    assert RUNTIME_PATH.exists()
    assert CDL_V2_RUNTIME_VERSION == "cdl_v2_sybil_resistance_runtime_389.v0.1"
    assert CDL_V2_DEPENDENCY == "cdl_v2_sybil_resistance_389.v0.1"


def test_dependency_chain_imports_v1_token() -> None:
    assert CDL_V1_DEPENDENCY == "cdl_v1_temporal_decay_388.v0.1"


def test_identity_cluster_risk_monotonicity() -> None:
    low = compute_identity_cluster_risk(
        shared_operator_fraction=0.1,
        shared_infrastructure_fraction=0.1,
        key_rotation_overlap_fraction=0.1,
    )
    high = compute_identity_cluster_risk(
        shared_operator_fraction=0.8,
        shared_infrastructure_fraction=0.8,
        key_rotation_overlap_fraction=0.8,
    )
    assert low < high


def test_burst_write_penalty_zero_below_baseline() -> None:
    assert compute_burst_write_penalty(
        writes_per_validation_epoch=4,
        baseline_writes_per_validation_epoch=5,
    ) == 0.0


def test_burst_write_penalty_increases_with_ratio() -> None:
    p1 = compute_burst_write_penalty(
        writes_per_validation_epoch=7,
        baseline_writes_per_validation_epoch=5,
        burst_sensitivity=0.2,
    )
    p2 = compute_burst_write_penalty(
        writes_per_validation_epoch=15,
        baseline_writes_per_validation_epoch=5,
        burst_sensitivity=0.2,
    )
    assert p1 < p2


def test_diversity_floor_contribution_is_bounded() -> None:
    contribution = compute_diversity_floor_contribution(
        distinct_cluster_refs=9,
        expected_diversity_floor=6,
    )
    assert contribution == 1.0


def test_sybil_penalty_is_bounded_and_decreases_with_diversity() -> None:
    low_div = compute_sybil_penalty(
        cluster_risk=0.6,
        burst_write_penalty=0.3,
        diversity_floor_contribution=0.1,
    )
    high_div = compute_sybil_penalty(
        cluster_risk=0.6,
        burst_write_penalty=0.3,
        diversity_floor_contribution=1.0,
    )
    assert 0.0 <= low_div <= 1.0
    assert 0.0 <= high_div <= 1.0
    assert high_div < low_div


def test_invalid_unit_interval_inputs_raise_tokenized_error() -> None:
    with pytest.raises(SybilResistanceValidationError) as exc:
        compute_identity_cluster_risk(
            shared_operator_fraction=-0.1,
            shared_infrastructure_fraction=0.2,
            key_rotation_overlap_fraction=0.3,
        )
    assert exc.value.token == "cdl_v2_sybil_out_of_range"

    with pytest.raises(SybilResistanceValidationError) as exc_nan:
        compute_sybil_penalty(
            cluster_risk=float("nan"),
            burst_write_penalty=0.3,
            diversity_floor_contribution=0.3,
        )
    assert exc_nan.value.token == "cdl_v2_sybil_invalid_numeric"


def test_invalid_rate_inputs_raise_tokenized_error() -> None:
    with pytest.raises(SybilResistanceValidationError) as exc:
        compute_burst_write_penalty(
            writes_per_validation_epoch=2,
            baseline_writes_per_validation_epoch=0,
        )
    assert exc.value.token == "cdl_v2_sybil_rate_non_positive"


def test_burst_penalty_rejects_non_validation_epoch() -> None:
    with pytest.raises(SybilResistanceValidationError) as exc:
        compute_burst_write_penalty(
            writes_per_validation_epoch=8,
            baseline_writes_per_validation_epoch=5,
            epoch_type="issuance_epoch",
        )
    assert exc.value.token == "cdl_v2_sybil_epoch_context_invalid"


def test_handoff_artifact_has_required_headings_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. Heuristic calibration and deterministic-boundary statement",
        "## 4. Deterministic failure-token catalog",
        "## 5. Mutation-scope boundary statement",
        "## 6. Carry-forward constraints for Phase 390",
        "## 7. Non-goals",
    ):
        assert heading in text

    for token in (
        'CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"',
        "CDL-V2 sybil-resistance enforcement is computational and deterministic.",
        "Phase 389 uses Phase-387 authorization targets as binding scope.",
        "No decision-log mutation occurred in Phase 389.",
        "compute_sybil_penalty` is intentionally bounded to a practical maximum of `0.90`",
        "`cdl_v2_sybil_epoch_context_invalid`",
    ):
        assert token in text


def test_phase_389_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_389_commit_ref_or_fail()
    _assert_v_series_mutation_scope(commit_ref)


def test_phase_389_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_389_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
