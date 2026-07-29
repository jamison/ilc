from __future__ import annotations

import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.consensus.diversity_floor_runtime import (
    CDL_V2_DEPENDENCY,
    CDL_V3_DEPENDENCY,
    CDL_V3_RUNTIME_VERSION,
    DiversityFloorValidationError,
    compute_diversity_floor_penalty,
    compute_max_cluster_share,
    meets_distinct_cluster_floor,
    meets_max_cluster_share_ceiling,
)


RUNTIME_INIT_PATH = Path("ilc_core/consensus/__init__.py")
RUNTIME_PATH = Path("ilc_core/consensus/diversity_floor_runtime.py")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "feat(g8): phase 397 cdl-v3 diversity floor runtime"

AUTHORIZED_RUNTIME_PATHS = {
    "ilc_core/consensus/__init__.py",
    "ilc_core/consensus/diversity_floor_runtime.py",
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_397_commit_ref_or_fail() -> str:
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
        "ilc_core/consensus/diversity_floor_runtime.py",
        "docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md",
        "tests/test_cdl_v3_diversity_floor_runtime_397.py",
    }

    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_397_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_397_commit_not_present_in_local_history")


def _assert_v_series_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed

    # Positive check: at least one consensus runtime path changed.
    assert any(path.startswith("ilc_core/consensus/") for path in changed), (
        "phase_397_consensus_mutation_missing"
    )

    # Negative check: no ilc_core path outside ilc_core/consensus/ changed.
    non_consensus_ilc_core = [
        path for path in changed if path.startswith("ilc_core/") and not path.startswith("ilc_core/consensus/")
    ]
    assert not non_consensus_ilc_core, (
        f"phase_397_ilc_core_scope_violation:{non_consensus_ilc_core}"
    )

    assert any(path in changed for path in AUTHORIZED_RUNTIME_PATHS), "phase_397_authorized_runtime_missing"

    unexpected_consensus = [
        path
        for path in changed
        if path.startswith("ilc_core/consensus/") and path not in AUTHORIZED_RUNTIME_PATHS
    ]
    assert not unexpected_consensus, f"phase_397_consensus_scope_violation:{unexpected_consensus}"


def test_runtime_paths_and_constants_exist() -> None:
    assert RUNTIME_INIT_PATH.exists()
    assert RUNTIME_PATH.exists()
    assert CDL_V3_RUNTIME_VERSION == "cdl_v3_diversity_floor_runtime_397.v0.1"
    assert CDL_V3_DEPENDENCY == "cdl_v3_diversity_floor_397.v0.1"


def test_dependency_chain_imports_v2_token() -> None:
    assert CDL_V2_DEPENDENCY == "cdl_v2_sybil_resistance_389.v0.1"


def test_compute_max_cluster_share_nominal_case() -> None:
    share = compute_max_cluster_share(largest_cluster_slots=3, total_panel_slots=8)
    assert share == Decimal("0.375000000000")


def test_compute_max_cluster_share_accepts_exact_decimal_like_inputs() -> None:
    share = compute_max_cluster_share(
        largest_cluster_slots=Decimal("3"),
        total_panel_slots="8",
    )
    assert share == Decimal("0.375000000000")


def test_meets_distinct_cluster_floor_true_and_false_cases() -> None:
    assert meets_distinct_cluster_floor(distinct_clusters=4, distinct_cluster_floor=3)
    assert not meets_distinct_cluster_floor(distinct_clusters=2, distinct_cluster_floor=3)


def test_meets_max_cluster_share_ceiling_true_and_false_cases() -> None:
    assert meets_max_cluster_share_ceiling(
        max_cluster_share=Decimal("0.35"),
        max_cluster_share_ceiling=Decimal("0.40"),
    )
    assert not meets_max_cluster_share_ceiling(
        max_cluster_share=Decimal("0.45"),
        max_cluster_share_ceiling=Decimal("0.40"),
    )


def test_compute_diversity_floor_penalty_is_bounded_and_monotonic() -> None:
    better = compute_diversity_floor_penalty(
        distinct_clusters=4,
        distinct_cluster_floor=4,
        max_cluster_share=Decimal("0.40"),
        max_cluster_share_ceiling=Decimal("0.40"),
    )
    worse = compute_diversity_floor_penalty(
        distinct_clusters=1,
        distinct_cluster_floor=4,
        max_cluster_share=Decimal("0.90"),
        max_cluster_share_ceiling=Decimal("0.40"),
    )
    assert Decimal("0") <= better <= Decimal("1")
    assert Decimal("0") <= worse <= Decimal("1")
    assert better < worse


def test_compute_diversity_floor_penalty_documents_diagnostic_only_scope() -> None:
    doc = " ".join((compute_diversity_floor_penalty.__doc__ or "").split())
    assert "Diagnostic-only" in doc
    assert "before the penalty changes settlement, quorum, admission, or finality" in doc


def test_cluster_share_rejects_largest_exceeding_total() -> None:
    with pytest.raises(DiversityFloorValidationError) as exc:
        compute_max_cluster_share(largest_cluster_slots=9, total_panel_slots=8)
    assert exc.value.token == "cdl_v3_diversity_floor_cluster_exceeds_total"


def test_ceiling_rejects_out_of_range_values() -> None:
    with pytest.raises(DiversityFloorValidationError) as exc:
        meets_max_cluster_share_ceiling(
            max_cluster_share=Decimal("0.3"),
            max_cluster_share_ceiling=Decimal("1.2"),
        )
    assert exc.value.token == "cdl_v3_diversity_floor_ceiling_out_of_range"


def test_helpers_reject_non_numeric_inputs() -> None:
    with pytest.raises(DiversityFloorValidationError) as exc:
        meets_distinct_cluster_floor(distinct_clusters="three", distinct_cluster_floor=3)
    assert exc.value.token == "cdl_v3_diversity_floor_invalid_numeric"

    with pytest.raises(DiversityFloorValidationError) as exc_nan:
        compute_max_cluster_share(largest_cluster_slots=float("nan"), total_panel_slots=8)
    assert exc_nan.value.token == "cdl_v3_diversity_floor_invalid_numeric"


def test_handoff_artifact_has_required_headings_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. Diversity-floor computational model statement",
        "## 4. Deterministic failure-token catalog",
        "## 5. Mutation-scope boundary statement",
        "## 6. Carry-forward constraints for Phase 398",
        "## 7. Non-goals",
    ):
        assert heading in text

    for token in (
        'CDL_V3_DEPENDENCY = "cdl_v3_diversity_floor_397.v0.1"',
        "CDL-V3 diversity-floor enforcement is computational and deterministic.",
        "Phase 397 uses Phase-396 authorization targets as binding scope.",
        "Phase 397 implements ratified CDL-V3 constitutional text and does not treat SIM-006 placeholder capability tiers as runtime policy terms.",
        "No decision-log mutation occurred in Phase 397.",
    ):
        assert token in text


def test_phase_397_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_397_commit_ref_or_fail()
    _assert_v_series_mutation_scope(commit_ref)


def test_phase_397_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_397_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
