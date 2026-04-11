from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

ARTIFACT_PATH = Path("docs/specs/ilc_epoch_boundary_witness_prelock_hardening_510_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_510_epoch_boundary_cdl_prelock_hardening.py")
PHASE_510_SUBJECT_TOKEN = "phase 510 epoch boundary cdl prelock hardening"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Scope lock",
    "## 2. Rejected alternatives",
    "## 3. Compatibility guards",
    "## 4. Opening-state preservation",
    "## 5. Prelock summary",
)
REQUIRED_TOKENS = (
    "epoch_boundary_witness_scope_locked",
    "cdl_030_p_e_clamp_unchanged",
    "cdl_v3_diversity_floor_unchanged",
    "No decision-log mutation occurs in Phase 510.",
    "Phase 511 is the next authorized phase.",
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


def _resolve_phase_510_commit_ref() -> str:
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
        if PHASE_510_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_510_commit_subject_present_but_no_qualifying_prelock_commit")
    raise AssertionError("phase_510_commit_not_present_in_local_history")


def test_prelock_document_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_document_contains_required_governance_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_prelock_document_records_rejected_alternatives() -> None:
    text = _read(ARTIFACT_PATH)
    assert "validator witness veto" in text
    assert "settlement-block authority" in text
    assert "reinterpretation of epoch-finality attestations as conversion authorization" in text


def test_live_decision_log_preserves_epoch_boundary_lane_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-057"]["status"] in {"open", "ratified"}
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert "CDL-053" not in rows


def test_head_commit_touches_no_runtime_files() -> None:
    assert_head_commit_touched_no_runtime_files(commit_ref=_resolve_phase_510_commit_ref())


def test_phase_510_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_510_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_510_main_commit_does_not_touch_cdl_log() -> None:
    commit_ref = _resolve_phase_510_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
