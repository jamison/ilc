from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path("docs/specs/ilc_cdl_058_re_admission_boundary_prelock_hardening_519_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_518_TEST_PATH = Path("tests/test_phase_518_cdl_058_opening_stub.py")
TEST_PATH = Path("tests/test_phase_519_cdl_058_prelock_hardening.py")
PHASE_519_SUBJECT_TOKEN = "phase 519 cdl-058 prelock hardening"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(PHASE_518_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Prelock scope",
    "## 2. Exit-reason enumeration lock",
    "## 3. CDL-046 timed_out orthogonality lock",
    "## 4. CDL-055 dep chain integrity",
    "## 5. Rejected scope expansions",
    "## 6. Ratification readiness",
)
REQUIRED_TOKENS = (
    "exit_reasons_locked: liveness_miss, equivocation, voluntary_exit",
    "cdl_046_timed_out_orthogonal",
    "cdl_058_dep_chain_requires_cdl_055_staking",
    "CDL-058 remains status: open in Phase 519.",
)
PHASE_518_COMMENT = "# The Phase-518 CDL-058 open-state check is a historical prelock reference."


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


def _resolve_phase_519_commit_ref() -> str:
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
        if PHASE_519_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_519_commit_subject_present_but_no_qualifying_prelock_commit")
    raise AssertionError("phase_519_commit_not_present_in_local_history")


def test_prelock_document_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_document_contains_required_governance_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_prelock_document_rejects_out_of_scope_expansions() -> None:
    text = _read(ARTIFACT_PATH)
    assert "blocking authority overlap with `CDL-057`" in text
    assert "`timed_out` amalgamation with `CDL-046`" in text
    assert "automatic reputation carry-forward on re-admission" in text


def test_live_cdl_log_preserves_open_state_and_required_statuses() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert rows["CDL-057"]["status"] == "ratified"
    assert rows["CDL-058"]["status"] == "open"
    assert "CDL-053" not in rows


def test_phase_518_test_historical_prelock_patch_is_active() -> None:
    phase_518_text = _read(PHASE_518_TEST_PATH)
    assert PHASE_518_COMMENT in phase_518_text
    assert "_commit_text(str(DECISION_LOG_PATH), commit_ref)" in phase_518_text


def test_phase_519_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_519_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_519_main_commit_does_not_touch_cdl_log() -> None:
    commit_ref = _resolve_phase_519_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-058"]["status"] == "open"
