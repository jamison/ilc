from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path("docs/specs/ilc_adr_0023_cdl_scoping_analysis_522_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_522_adr_0023_cdl_scoping_analysis.py")
PHASE_522_SUBJECT_TOKEN = "phase 522 adr-0023 cdl scoping analysis"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. ADR-0023 summary",
    "## 2. Protocol-layer constitutional necessity test",
    "## 3. Research-guidance sufficiency assessment",
    "## 4. Recommendation",
    "## 5. Window 525+ prerequisites (if CDL-059 opening recommended)",
    "## 6. Governance boundary",
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


def _resolve_phase_522_commit_ref() -> str:
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
        if PHASE_522_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_522_commit_subject_present_but_no_qualifying_scoping_commit")
    raise AssertionError("phase_522_commit_not_present_in_local_history")


def test_scoping_document_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_scoping_document_contains_required_tokens_and_exactly_one_recommendation() -> None:
    text = _read(ARTIFACT_PATH)
    assert "adr_0023_quality_signal_architecture" in text
    assert "No decision-log mutation occurs in Phase 522." in text
    recommendation_tokens = ("cdl_059_opening_recommended", "adr_0023_remains_research_guidance")
    assert sum(token in text for token in recommendation_tokens) == 1


def test_scoping_document_states_adr_0023_is_not_a_ratified_cdl() -> None:
    text = _read(ARTIFACT_PATH)
    assert "ADR-0023 is not a ratified CDL." in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert rows["CDL-057"]["status"] == "ratified"
    assert rows["CDL-058"]["status"] == "ratified"
    assert "CDL-053" not in rows
    assert "CDL-059" not in rows


def test_head_commit_touches_no_ilc_core_files() -> None:
    changed_paths = {
        path.strip()
        for path in subprocess.run(
            ["git", "diff", "HEAD", "--name-only", "--", "ilc_core/"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
        if path.strip()
    }
    assert changed_paths == set()


def test_phase_522_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_522_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_522_main_commit_does_not_touch_cdl_log_and_cdl_059_remains_absent() -> None:
    commit_ref = _resolve_phase_522_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert "CDL-059" not in rows
