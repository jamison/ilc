from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)

BRIEF_PATH = Path("docs/specs/ilc_treasury_sim_t_commission_brief_453_v0.1.md")
TEST_PATH = Path("tests/test_phase_453_sim_t_commission_brief.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_453_SUBJECT = "docs(g8): phase 453 sim-t commission brief and measurement contract"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
MAIN_COMMIT_PATHS = {
    str(BRIEF_PATH),
    str(TEST_PATH),
}


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


def _resolve_phase_453_commit_ref() -> str:
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
        if subject.strip() == PHASE_453_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS:
            return commit_ref

    if matches:
        raise AssertionError("phase_453_commit_subject_present_but_no_qualifying_commission_brief_commit")
    raise AssertionError("phase_453_commit_not_present_in_local_history")


def test_commission_brief_exists_and_contains_required_headings() -> None:
    assert BRIEF_PATH.exists()
    text = _read(BRIEF_PATH)
    for heading in (
        "## 1. Scenario matrix",
        "## 2. Parameter families",
        "## 3. Seed and manifest policy",
        "## 4. Success criteria",
        "## 5. Discriminating thresholds",
        "## 6. Tie-break logic",
        "## 7. Ambiguous-outcome policy",
    ):
        assert heading in text


def test_commission_brief_contains_required_tokens() -> None:
    text = _read(BRIEF_PATH)
    for token in (
        "Blocker 1",
        "Blocker 2",
        "Blocker 3",
        "Scenario 1 - Escrow multiplier discrimination",
        "Scenario 2 - Vesting lock duration discrimination",
        "Scenario 3 - L1/L2 contagion isolation test",
        "Scenario 4 - Long-tail zero-issuance stress test",
        "Scenario 5 - Recovery criterion exit validation",
        "SIM-T",
        "No retroactive rewriting of success criteria after Phase 453.",
        "Ambiguous simulation outcomes preserve the blocker rather than forcing closure.",
        "No CDL-050 opening or ratification occurs in Phase 453.",
    ):
        assert token in text


def test_commission_brief_references_phase_451_observables_contract() -> None:
    text = _read(BRIEF_PATH)
    assert "docs/specs/ilc_treasury_objective_function_and_observables_contract_451_v0.1.md" in text


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    for path in (BRIEF_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_453_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_453_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS


def test_phase_453_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_453_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
