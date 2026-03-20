from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)

CONTRACT_PATH = Path("docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md")
TEST_PATH = Path("tests/test_phase_451_treasury_objective_function_and_observables_contract.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_451_SUBJECT = "docs(g8): phase 451 treasury objective-function and observables contract"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
MAIN_COMMIT_PATHS = {
    str(CONTRACT_PATH),
    str(TEST_PATH),
}
RELEASE_ENGINEERING_PREFIXES = (
    "release/",
    "bootstrap/",
    "packaging/",
    "docs/release",
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


def _resolve_phase_451_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_451_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS:
            return commit_ref

    if matches:
        raise AssertionError("phase_451_commit_subject_present_but_no_qualifying_objective_contract_commit")
    raise AssertionError("phase_451_commit_not_present_in_local_history")


def test_contract_exists_and_contains_required_headings() -> None:
    assert CONTRACT_PATH.exists()
    text = _read(CONTRACT_PATH)
    for heading in (
        "## 1. Treasury optimization target",
        "## 2. Candidate observables",
        "## 3. Observable definitions",
        "## 4. Evidence-source ladder",
        "## 5. Anti-goals",
        "## 6. Non-authorization statement",
    ):
        assert heading in text


def test_contract_contains_all_required_observable_tokens() -> None:
    text = _read(CONTRACT_PATH)
    for token in (
        "P_e clamp-respect rate",
        "organic ECU production rate",
        "productive backlog / queue-clearance behavior",
        "release-shock amplitude after time-lock expiry",
        "intervention duration and intervention cost",
    ):
        assert token in text


def test_contract_contains_required_anti_goal_and_non_authorization_tokens() -> None:
    text = _read(CONTRACT_PATH)
    for token in (
        "No blocker closes on prose alone.",
        "No parameter locks without pre-registered discriminating metrics.",
        "No CDL-050 opening or ratification occurs in Phase 451.",
    ):
        assert token in text


def test_no_forbidden_treasury_mutation_token_in_deliverable_or_test() -> None:
    for path in (CONTRACT_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_451_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_451_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS


def test_phase_451_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_451_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
    assert not any(
        path.startswith(prefix)
        for path in changed
        for prefix in RELEASE_ENGINEERING_PREFIXES
    )
