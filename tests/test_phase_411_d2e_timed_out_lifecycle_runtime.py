from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.node.timed_out_lifecycle_runtime_411 import (
    CDL_046_DEPENDENCY,
    LIFECYCLE_BASE_DEPENDENCY,
    ORPHAN_TIMEOUT_EPOCHS,
    RECOVERY_POLICY,
    TIMED_OUT_LIFECYCLE_RUNTIME_VERSION,
    TimedOutLifecycleError,
    get_recovery_policy,
    is_claim_timed_out,
)


RUNTIME_PATH = Path("ilc_core/node/timed_out_lifecycle_runtime_411.py")
NODE_INIT_PATH = Path("ilc_core/node/__init__.py")
HANDOFF_PATH = Path("docs/specs/ilc_d2e_timed_out_lifecycle_runtime_handoff_411_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_411_COMMIT_SUBJECT = "feat(g8): phase 411 d2e timed-out lifecycle runtime"
AUTHORIZED_RUNTIME_PATHS = {
    "ilc_core/node/timed_out_lifecycle_runtime_411.py",
    "ilc_core/node/__init__.py",
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_411_commit_ref() -> str:
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
        if subject.strip().lower() == PHASE_411_COMMIT_SUBJECT.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "ilc_core/node/timed_out_lifecycle_runtime_411.py",
        "ilc_core/node/__init__.py",
        "tests/test_phase_411_d2e_timed_out_lifecycle_runtime.py",
        "docs/specs/ilc_d2e_timed_out_lifecycle_runtime_handoff_411_v0.1.md",
    }

    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_411_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_411_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed
    assert any(path.startswith("ilc_core/node/") for path in changed), (
        "phase_411_node_runtime_mutation_missing"
    )

    non_node_ilc_core = [
        path for path in changed if path.startswith("ilc_core/") and not path.startswith("ilc_core/node/")
    ]
    assert not non_node_ilc_core, (
        f"phase_411_ilc_core_scope_violation:{non_node_ilc_core}"
    )

    unexpected_node_paths = [
        path for path in changed
        if path.startswith("ilc_core/node/") and path not in AUTHORIZED_RUNTIME_PATHS
    ]
    assert not unexpected_node_paths, (
        f"phase_411_node_scope_violation:{unexpected_node_paths}"
    )


def test_runtime_paths_and_version_constant() -> None:
    assert RUNTIME_PATH.exists()
    assert NODE_INIT_PATH.exists()
    assert TIMED_OUT_LIFECYCLE_RUNTIME_VERSION == "timed_out_lifecycle_runtime_411.v0.1"


def test_cdl_046_dependency_token_correct() -> None:
    assert CDL_046_DEPENDENCY == "cdl_046_ratified_409.v0.1"


def test_lifecycle_base_dependency_links_to_cdl_035() -> None:
    assert LIFECYCLE_BASE_DEPENDENCY == "cdl_035_ratified_350.v0.1"


def test_orphan_timeout_epochs_constitutional_constant() -> None:
    # CDL-046 Phase-409 ratified constant - any change is unconstitutional.
    assert ORPHAN_TIMEOUT_EPOCHS == 4


def test_recovery_policy_constitutional_constant() -> None:
    # CDL-046 Phase-409 ratified constant - any change is unconstitutional.
    assert RECOVERY_POLICY == "stake_full_release"
    assert get_recovery_policy() == "stake_full_release"


def test_is_claim_timed_out_exactly_at_boundary() -> None:
    assert is_claim_timed_out(current_epoch=4, orphaned_since_epoch=0) is True
    assert is_claim_timed_out(current_epoch=104, orphaned_since_epoch=100) is True


def test_is_claim_timed_out_below_boundary() -> None:
    assert is_claim_timed_out(current_epoch=3, orphaned_since_epoch=0) is False
    assert is_claim_timed_out(current_epoch=103, orphaned_since_epoch=100) is False


def test_is_claim_timed_out_well_above_boundary() -> None:
    assert is_claim_timed_out(current_epoch=10, orphaned_since_epoch=0) is True
    assert is_claim_timed_out(current_epoch=0, orphaned_since_epoch=0) is False


def test_is_claim_timed_out_rejects_invalid_inputs() -> None:
    with pytest.raises(TimedOutLifecycleError) as exc:
        is_claim_timed_out(-1, 0)
    assert exc.value.token == "cdl_046_current_epoch_invalid"

    with pytest.raises(TimedOutLifecycleError) as exc:
        is_claim_timed_out(5, -1)
    assert exc.value.token == "cdl_046_orphaned_since_epoch_invalid"

    with pytest.raises(TimedOutLifecycleError) as exc:
        is_claim_timed_out("five", 0)  # type: ignore[arg-type]
    assert exc.value.token == "cdl_046_current_epoch_invalid"


def test_handoff_artifact_has_required_headings_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. CDL-046 ratified constants specification",
        "## 4. Deterministic failure-token catalog",
        "## 5. CDL-035 amendment boundary statement",
        "## 6. Mutation-scope boundary statement",
        "## 7. Non-goals and carry-forward to Phase 412",
    ):
        assert heading in text

    for token in (
        'TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"',
        'CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"',
        'ORPHAN_TIMEOUT_EPOCHS = 4 and RECOVERY_POLICY = "stake_full_release" are constitutionally locked by CDL-046 ratified in Phase 409.',
        "No decision-log mutation occurred in Phase 411.",
        "timed_out transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.",
        "D2e Agent SDK CLI integration and Window-414+ runtime work are the authorized next implementation slots.",
    ):
        assert token in text


def test_phase_411_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_411_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)


def test_phase_411_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_411_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
