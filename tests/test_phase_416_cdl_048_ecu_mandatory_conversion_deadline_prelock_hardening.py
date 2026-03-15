from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md")
HARDENING_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md")
CDL_048_STUB_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md")
CDL_047_HARDENING_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md")
EXPECTED_CDL_048_ROW = (
    "| CDL-048 | ADR-0017 / CDL-V1 / CDL-035 / SIM-008 | ECU mandatory conversion deadline and circulation "
    "enforcement | open | indefinite ECU retention, governed conversion deadline with anti-hoarding forced "
    "circulation, discretionary operator conversion windows | governed conversion deadline with anti-hoarding "
    "forced circulation (proposed) | SIM-008 deadline calibration anchor, CDL-V1 temporal-decay complement "
    "clause, CDL-035 lifecycle attachment clause, no-reputation-carry-forward clause |"
)
PHASE_416_SUBJECT_TOKEN = "phase 416 cdl-048 ecu mandatory conversion deadline prelock hardening"
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. CDL-048 open-state evidence anchor",
    "## 3. Candidate discrimination and winning candidate confirmation",
    "## 4. Section-7 ratification readiness evidence checklist satisfaction",
    "## 5. SIM-008 conversion-deadline calibration anchor",
    "## 6. Anti-hoarding and forced-circulation rationale",
    "## 7. Relationship to CDL-V1 temporal decay and CDL-035 lifecycle",
    "## 8. No-reputation-carry-forward clause and dependency chain",
    "## 9. Non-goals",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-048 prelock hardening confirms the proposed candidate: governed conversion deadline with anti-hoarding forced circulation.",
    "No CDL row mutation occurs in Phase 416.",
    "Phase 419 is the targeted CDL-048 ratification lane; this hardening artifact constitutes the primary prelock evidence.",
    "Indefinite ECU retention is rejected because it permits hoarding pressure and defeats the constitutional circulation objective of the ECU layer in the late economy.",
    "Discretionary operator conversion windows is rejected because operator-level timing discretion would undermine uniform economic lifecycle rules and constitutional comparability across agents.",
    "ecu_conversion_deadline = 4 issuance epochs",
    "ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.",
    "CDL-048 complements CDL-V1 temporal decay and CDL-035 lifecycle governance rather than replacing them.",
    "ECU-to-ILC conversion is a lifecycle transition and does not carry forward reputation or attribution automatically.",
    "This SIM-008 deadline anchor is a prelock input and does not become a constitutional constant until CDL-048 ratification in Phase 419.",
)
REQUIRED_SECTION_4_ITEMS = (
    "1. The governed conversion deadline with anti-hoarding forced circulation is confirmed as the proposed candidate and both rejected candidates remain excluded.",
    "2. SIM-008 deadline calibration anchor is locked: ecu_conversion_deadline = 4 issuance epochs, as the conversion-deadline prelock input.",
    "3. Anti-hoarding intent is locked: ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.",
    "4. CDL-V1 temporal decay and CDL-035 lifecycle continuity is satisfied: CDL-048 complements the existing validation and circulation governance layers rather than replacing them.",
    "5. No-reputation-carry-forward is locked: ECU-to-ILC conversion is a lifecycle transition and not an achievement or attribution event.",
)
REQUIRED_DEPENDENCY_ANCHORS = (
    "docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md",
    "CDL-V1",
    "CDL-035",
    "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}")
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_416_commit_ref() -> str:
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
        if PHASE_416_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(HARDENING_PATH),
        "tests/test_phase_416_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_416_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_416_commit_not_present_in_local_history")


def _extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading):]
    match = re.search(r"\n## \d+\. ", rest)
    if match:
        return rest[: match.start()]
    return rest


def test_hardening_artifact_exists_and_contains_required_headings_tokens_checklist_and_dependencies() -> None:
    assert HARDENING_PATH.exists()
    text = _read(HARDENING_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for item in REQUIRED_SECTION_4_ITEMS:
        assert item in text
    for anchor in REQUIRED_DEPENDENCY_ANCHORS:
        assert anchor in text
    section_4 = _extract_section(text, "## 4. Section-7 ratification readiness evidence checklist satisfaction")
    assert len(re.findall(r"^\d+\. ", section_4, flags=re.MULTILINE)) == 5


def test_phase_414_cdl_048_opening_stub_is_preserved() -> None:
    assert CDL_048_STUB_PATH.exists()
    text = _read(CDL_048_STUB_PATH)
    assert "Phase-416 is the targeted prelock hardening lane for CDL-048." in text
    assert "status: open" in text
    assert "CDL-048 complements CDL-V1 temporal decay and CDL-035 lifecycle governance rather than replacing them." in text


def test_cdl_047_and_cdl_048_register_order_preserved() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_046_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-046 "))
    cdl_047_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-047 "))
    cdl_048_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-048 "))
    assert cdl_047_index == cdl_046_index + 1
    assert cdl_048_index == cdl_047_index + 1


def test_cdl_048_row_is_open() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    assert rows["CDL-048"]["status"] == "open"
    assert EXPECTED_CDL_048_ROW in text


def test_cdl_048_has_no_premature_ratification_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-048"]["status"] != "ratified"
    assert "ratified_date" not in rows["CDL-048"]
    assert "ratified_phase" not in rows["CDL-048"]


def test_phase_416_commit_no_cdl_row_mutation_stub_immutable_and_phase_415_immutable() -> None:
    commit_ref = _resolve_phase_416_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_416_commit_unlawfully_added_or_removed_cdl_rows"
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_416"
    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_048_STUB_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_048_STUB_PATH))
    assert old_stub == new_stub, "phase_416_commit_modified_phase_414_opening_stub_unlawfully"
    old_415 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_047_HARDENING_PATH))
    new_415 = _read_file_at_ref(commit_ref, str(CDL_047_HARDENING_PATH))
    assert old_415 == new_415, "phase_416_commit_modified_phase_415_cdl_047_hardening_unlawfully"


def test_phase_416_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_416_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
