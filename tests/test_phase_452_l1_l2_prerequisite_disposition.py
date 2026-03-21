from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)

DISPOSITION_PATH = Path("docs/specs/ilc_cdl_050_l1_l2_prerequisite_disposition_452_v0.1.md")
TEST_PATH = Path("tests/test_phase_452_l1_l2_prerequisite_disposition.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_452_SUBJECT = "docs(g8): phase 452 l1-l2 prerequisite disposition and interface boundary"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
OPTION_A = "L1/L2 separation is adopted as a CDL-050 prerequisite."
OPTION_B = "L1/L2 separation is rejected as a CDL-050 prerequisite; the Treasury risk model is enlarged accordingly."
MAIN_COMMIT_PATHS = {
    str(DISPOSITION_PATH),
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


def _resolve_phase_452_commit_ref() -> str:
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
        if subject.strip() == PHASE_452_SUBJECT:
            matches.append(commit_hash)

    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS:
            return commit_ref

    if matches:
        raise AssertionError("phase_452_commit_subject_present_but_no_qualifying_prerequisite_disposition_commit")
    raise AssertionError("phase_452_commit_not_present_in_local_history")


def test_disposition_artifact_exists_and_contains_required_headings() -> None:
    assert DISPOSITION_PATH.exists()
    text = _read(DISPOSITION_PATH)
    for heading in (
        "## 1. Disposition decision",
        "## 2. Rationale",
        "## 3. Interface boundary conditions",
        "## 4. Risk model implications",
        "## 5. Non-authorization statement",
    ):
        assert heading in text


def test_disposition_artifact_records_exactly_one_binary_decision() -> None:
    text = _read(DISPOSITION_PATH)
    present = [token for token in (OPTION_A, OPTION_B) if token in text]
    assert present == [OPTION_A]


def test_disposition_artifact_contains_required_non_decision_tokens() -> None:
    text = _read(DISPOSITION_PATH)
    for token in (
        "L1/L2 disposition is frozen as of Phase 452.",
        "No CDL-050 opening or ratification occurs in Phase 452.",
        "No hidden or assumed prerequisite is allowed.",
        "ADR-0018",
        "Genesis affordance",
        "post-launch optional",
    ):
        assert token in text


def test_no_forbidden_treasury_mutation_token_appears() -> None:
    for path in (DISPOSITION_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)


def test_phase_452_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_452_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == MAIN_COMMIT_PATHS


def test_phase_452_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_452_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
    assert not any(
        path.startswith(prefix)
        for path in changed
        for prefix in RELEASE_ENGINEERING_PREFIXES
    )
