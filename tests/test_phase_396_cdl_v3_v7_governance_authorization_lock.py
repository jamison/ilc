from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)


ARTIFACT_PATH = Path("docs/specs/ilc_cdl_v3_v7_governance_authorization_lock_396_v0.1.md")
TEST_PATH = Path("tests/test_phase_396_cdl_v3_v7_governance_authorization_lock.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_396_COMMIT_SUBJECT = "docs(g8): phase 396 cdl-v3-v7 governance authorization lock"


REQUIRED_HEADINGS = (
    "## 1. Scope and authority boundary",
    "## 2. Inputs and constitutional carry-forward",
    "## 3. Branch resolution and governance stance",
    "## 4. Authorized runtime target paths for phases 397/398",
    "## 5. Dependency token and version lock",
    "## 6. Mutation scope restrictions for runtime phases",
    "## 7. Placeholder-vocabulary limitation and guardrails",
    "## 8. Conflict resolution and forward boundary",
    "## 9. Non-goals and immutable boundaries",
)


REQUIRED_TOKENS = (
    "This is the single source of truth for CDL-V3/V7 runtime implementation authorization for phases 397/398.",
    "SIM-006 favorable branch is locked: recommended_panel_assignment_policy: diversity_weighted.",
    "No unfavorable SIM-006 fallback branch is authorized in this artifact.",
    "SIM-006 capability-vector tiers are directionally valid but were commissioned with placeholder vocabulary; this limitation is acknowledged and bounded to governance authorization framing in Phase 396.",
    "Phases 397/398 implement ratified CDL-V3/V7 constitutional text; SIM-006 placeholder capability-vector tiers are not runtime specification inputs.",
    'CDL_V3_DEPENDENCY = "cdl_v3_diversity_floor_397.v0.1"',
    'CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"',
    "Phase 396 is authorization-only and non-ratifying.",
    "No decision-log mutation occurred. No ilc_core runtime files were changed.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_396_commit_ref() -> str:
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
        if subject.strip() == PHASE_396_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(ARTIFACT_PATH),
        str(TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_396_commit_subject_present_but_no_qualifying_authorization_lock_commit")
    raise AssertionError("phase_396_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_artifact_contains_required_authority_and_branch_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_authorized_runtime_target_paths_are_explicit_and_creation_authorized() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "ilc_core/consensus/__init__.py",
        "ilc_core/consensus/diversity_floor_runtime.py",
        "ilc_core/consensus/popperian_gate_runtime.py",
        "ilc_core/consensus/` does not exist in Phase 396 and is explicitly authorized as a creation target package for phases 397/398.",
    ):
        assert token in text


def test_dependency_token_values_are_exact() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'CDL_V3_DEPENDENCY = "cdl_v3_diversity_floor_397.v0.1"' in text
    assert 'CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"' in text


def test_placeholder_limitation_is_bounded_and_source_distinction_is_explicit() -> None:
    text = _read(ARTIFACT_PATH)
    assert (
        "SIM-006 capability-vector tiers are directionally valid but were commissioned with placeholder vocabulary; this limitation is acknowledged and bounded to governance authorization framing in Phase 396."
        in text
    )
    assert (
        "Phases 397/398 implement ratified CDL-V3/V7 constitutional text; SIM-006 placeholder capability-vector tiers are not runtime specification inputs."
        in text
    )


def test_phase_396_commit_touched_no_decision_log_files() -> None:
    commit_ref = _resolve_phase_396_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed


def test_phase_396_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_396_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
