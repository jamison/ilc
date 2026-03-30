from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

ARTIFACT_PATH = Path("docs/specs/ilc_epoch_boundary_witness_opening_stub_509_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_509_epoch_boundary_cdl_opening_stub.py")
PHASE_509_SUBJECT_TOKEN = "phase 509 epoch boundary cdl opening stub"
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Lane identity",
    "## 2. Evidence gate",
    "## 3. Non-goals",
    "## 4. Opening-state boundary",
    "## 5. Ratification readiness evidence checklist",
)
REQUIRED_TOKENS = (
    "CDL-057 opens in Phase 509.",
    "epoch_boundary_provenance_scope",
    "cdl_053_reserved",
    "No ilc_core/ mutation occurs in Phase 509.",
    "Phase 510 is the next authorized phase.",
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


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_509_commit_ref() -> str:
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
        if PHASE_509_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_509_commit_subject_present_but_no_qualifying_opening_commit")
    raise AssertionError("phase_509_commit_not_present_in_local_history")


def _baseline_decision_log_text() -> str:
    try:
        commit_ref = _resolve_phase_509_commit_ref()
    except AssertionError:
        return _commit_text(str(DECISION_LOG_PATH), "HEAD")
    return _commit_text(str(DECISION_LOG_PATH), f"{commit_ref}^")


def test_opening_stub_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_opening_stub_contains_required_governance_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert (
        "epoch_boundary_blocking_authority_deferred" in text
        or "epoch_boundary_blocking_authority_in_scope" in text
    )


def test_opening_stub_cites_phase_508_vehicle_selection_and_phase_498_scoping() -> None:
    text = _read(ARTIFACT_PATH)
    assert "docs/specs/ilc_epoch_boundary_cdl_vehicle_selection_508_v0.1.md" in text
    assert "docs/specs/ilc_epoch_boundary_enforcement_architectural_scoping_498_v0.1.md" in text


def test_live_decision_log_contains_open_cdl_057_row() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-057"]["status"] in {"open", "ratified"}
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert "CDL-053" not in rows


def test_pre_existing_decision_rows_remain_unchanged() -> None:
    baseline_rows = parse_decision_register_rows(_baseline_decision_log_text())
    live_rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id, baseline_row in baseline_rows.items():
        assert live_rows[cdl_id] == baseline_row


def test_phase_509_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_509_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_509_main_commit_opens_cdl_057_and_preserves_pre_existing_rows() -> None:
    commit_ref = _resolve_phase_509_commit_ref()
    committed_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    baseline_rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), f"{commit_ref}^"))
    assert committed_rows["CDL-057"]["status"] == "open"
    assert committed_rows["CDL-055"]["status"] == "ratified"
    assert committed_rows["CDL-056"]["status"] == "ratified"
    assert "CDL-053" not in committed_rows
    for cdl_id, baseline_row in baseline_rows.items():
        assert committed_rows[cdl_id] == baseline_row
