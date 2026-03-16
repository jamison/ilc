from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    ALLOWED_RATIFICATION_MUTATION_FIELDS,
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_ratification_evidence_419_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md")
CDL_047_OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md")
CDL_048_OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md")
CDL_047_HARDENING_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md")
CDL_048_HARDENING_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md")
CDL_047_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md")
PHASE_417_REVIEW_PATH = Path("docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md")
PHASE_414_TEST_PATH = Path("tests/test_phase_414_cdl_047_and_cdl_048_opening.py")
PHASE_416_TEST_PATH = Path("tests/test_phase_416_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening.py")
PHASE_417_TEST_PATH = Path("tests/test_phase_417_popperian_bounded_existential_claim_form_governance_review.py")
PHASE_418_TEST_PATH = Path("tests/test_phase_418_cdl_047_treasury_governance_ratification.py")
PHASE_419_COMMIT_SUBJECT = "docs(g8): phase 419 cdl-048 ecu mandatory conversion deadline ratification"

REQUIRED_HEADINGS = (
    "## 1. Scope and ratification boundary",
    "## 2. CDL-048 open-state anchor",
    "## 3. Constitutional evidence for ECU mandatory conversion deadline",
    "## 4. Phase-416 prelock hardening anchor",
    "## 5. SIM-008 deadline calibration evidence satisfaction",
    "## 6. Section-7 ratification readiness evidence checklist satisfaction",
    "## 7. Ratified governance tokens and constitutional effect",
    "## 8. Non-goals and boundary",
    "## 9. Canonical anchors",
)

REQUIRED_TOKENS = (
    "CDL-048 is ratified as the ECU mandatory conversion deadline framework for forced circulation and anti-hoarding policy.",
    "ecu_conversion_deadline = 4 issuance epochs",
    "ECU mandatory conversion eliminates ECU hoarding and forces ECU into economic circulation.",
    "CDL-048 complements CDL-V1 temporal decay and CDL-035 lifecycle governance rather than replacing them.",
    "ECU-to-ILC conversion is a lifecycle transition and does not carry forward reputation or attribution automatically.",
    "Indefinite ECU retention is rejected because it permits hoarding pressure and defeats the constitutional circulation objective of the ECU layer in the late economy.",
    "Discretionary operator conversion windows is rejected because operator-level timing discretion would undermine uniform economic lifecycle rules and constitutional comparability across agents.",
    "Phase 417 recorded no CDL-047-specific or CDL-048-specific CRITICAL findings; Phase 419 proceeds unblocked.",
)

REQUIRED_SECTION_6_ITEMS = (
    "1. The Phase-414 opening row and opening stub remain the authoritative historical open-state anchor for `CDL-048`.",
    "2. The Phase-416 prelock artifact confirms the selected conversion deadline candidate and preserves exclusion of both rejected candidates.",
    "3. The SIM-008 deadline calibration anchor is accepted as a ratified governance constant: `ecu_conversion_deadline = 4 issuance epochs`.",
    "4. The CDL-V1 temporal decay and CDL-035 lifecycle continuity clause is satisfied: CDL-048 complements rather than replaces the existing validation and circulation governance layers.",
    "5. The Phase-417 governance review recorded no `CDL-048`-specific blocking defect and therefore does not block ratification.",
)

REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    "docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md",
    "docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md",
    "docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md",
    "docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md",
    "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md",
    "docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md",
)

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_ALLOWED_FIELDS = set(ALLOWED_RATIFICATION_MUTATION_FIELDS) | {"current_candidate"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _register_row_text(row: dict[str, str]) -> str:
    cells = [row[header] for header in _BASE_HEADERS]
    if "ratified_phase" in row:
        cells.append(f"ratified_phase: {row['ratified_phase']}")
    if "ratified_date" in row:
        cells.append(f"ratified_date: {row['ratified_date']}")
    if "evidence_document" in row:
        cells.append(f"evidence_document: {row['evidence_document']}")
    return "| " + " | ".join(cells) + " |"


def _mini_register(row: str) -> str:
    return "\n".join(
        [
            "## Decision Register",
            "",
            "| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |",
            "|---|---|---|---|---|---|---|",
            row,
            "",
            "## Scoped Ratification Record",
        ]
    )


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


def _resolve_phase_419_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "	" not in line:
            continue
        commit_hash, subject = line.split("	", 1)
        if subject.strip() == PHASE_419_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        str(PHASE_414_TEST_PATH),
        str(PHASE_416_TEST_PATH),
        str(PHASE_417_TEST_PATH),
        str(PHASE_418_TEST_PATH),
        "tests/test_phase_419_cdl_048_ecu_mandatory_conversion_deadline_ratification.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching:
        raise AssertionError("phase_419_commit_subject_present_but_no_ratification_commit")
    raise AssertionError("phase_419_commit_not_present_in_local_history")


def _extract_function_block(text: str, function_name: str) -> str:
    needle = f"def {function_name}("
    start = text.find(needle)
    if start == -1:
        raise AssertionError(f"unable_to_locate_function_block:{function_name}")
    next_start = text.find("\ndef ", start + 1)
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def test_ratification_evidence_exists_and_contains_required_headings_tokens_and_checklist() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for item in REQUIRED_SECTION_6_ITEMS:
        assert item in text
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_cdl_048_row_is_ratified_with_correct_fields() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    row = rows["CDL-048"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "governed conversion deadline with anti-hoarding forced circulation"
    assert row["ratified_phase"] == "419"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == "2026-03-15"
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert "governed conversion deadline with anti-hoarding forced circulation (proposed)" not in text


def test_cdl_047_remains_ratified_and_cdl_049_absent() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-047"]["status"] == "ratified"
    assert rows["CDL-047"]["ratified_phase"] == "418"

    # The Phase-419 `CDL-049` absence check is a historical pre-Window-424 reference.
    historical_rows = parse_decision_register_rows(
        _read_file_at_ref(_resolve_phase_419_commit_ref(), str(DECISION_LOG_PATH))
    )
    assert "CDL-049" not in historical_rows
    assert_no_non_target_rows_marked_with_phase(rows, phase="419", target_cdls={"CDL-048"})


def test_phase_414_and_phase_416_tests_are_historicalized_for_cdl_048_open_state() -> None:
    phase_414_text = _read(PHASE_414_TEST_PATH)
    assert '# The Phase-414 `CDL-048` row is a historical opening reference.' in phase_414_text
    assert 'EXPECTED_CDL_048_ROW in historical_text' in phase_414_text
    assert 'rows["CDL-048"]["status"] == "open"' in phase_414_text
    assert 'live_rows["CDL-048"]["status"] == "open"' not in phase_414_text
    phase_414_block = _extract_function_block(phase_414_text, 'test_decision_log_contains_exact_cdl_047_and_cdl_048_opening_rows')
    assert 'live_text = _read(DECISION_LOG_PATH)' not in phase_414_block
    assert 'live_rows = parse_decision_register_rows(live_text)' not in phase_414_block

    phase_416_text = _read(PHASE_416_TEST_PATH)
    assert phase_416_text.count('_read_file_at_ref(_resolve_phase_416_commit_ref(), str(DECISION_LOG_PATH))') >= 2
    assert '# The Phase-416 `CDL-048` row is a historical prelock reference.' in phase_416_text
    assert 'EXPECTED_CDL_048_ROW in historical_text' in phase_416_text


def test_phase_417_and_phase_418_tests_are_historicalized_for_cdl_048_open_state() -> None:
    phase_417_text = _read(PHASE_417_TEST_PATH)
    assert '# The Phase-417 `CDL-048` open-state check is a historical governance-review reference.' in phase_417_text
    assert 'historical_rows["CDL-048"]["status"] == "open"' in phase_417_text
    assert 'live_rows["CDL-048"]["status"] == "open"' not in phase_417_text
    assert '# The Phase-417 `CDL-049` absence check is a historical pre-Window-424 reference.' in phase_417_text
    assert 'assert "CDL-049" not in historical_rows' in phase_417_text

    phase_418_text = _read(PHASE_418_TEST_PATH)
    assert '# The Phase-418 `CDL-048` non-ratification boundary check is a historical Phase-418-commit reference.' in phase_418_text
    phase_418_block = _extract_function_block(phase_418_text, 'test_cdl_048_remains_open_without_ratification_metadata')
    assert '_read_file_at_ref(_resolve_phase_418_commit_ref(), str(DECISION_LOG_PATH))' in phase_418_block
    assert 'rows["CDL-048"]["status"] == "open"' in phase_418_block
    assert '_read(DECISION_LOG_PATH)' not in phase_418_block
    assert '# Phase-419 removed the live CDL-048 check from the Phase-414 test; verify the historical form.' in phase_418_text
    assert 'assert \'live_rows["CDL-048"]["status"] == "open"\' not in phase_414_text' in phase_418_text


def test_phase_419_commit_mutated_only_cdl_048_and_left_prior_artifacts_unchanged() -> None:
    commit_ref = _resolve_phase_419_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    required = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        str(PHASE_414_TEST_PATH),
        str(PHASE_416_TEST_PATH),
        str(PHASE_417_TEST_PATH),
        str(PHASE_418_TEST_PATH),
        "tests/test_phase_419_cdl_048_ecu_mandatory_conversion_deadline_ratification.py",
    }
    assert changed == required, "phase_419_commit_touched_unexpected_paths"

    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_419_commit_unlawfully_added_or_removed_cdl_rows"

    target_old = _mini_register(_register_row_text(old_rows["CDL-048"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-048"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-048",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-048":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"non_target_row_mutated:{cdl_id}"

    for path, token in (
        (SEQUENCE_LOCK_PATH, "phase_419_commit_modified_phase_414_sequence_lock_unlawfully"),
        (CDL_047_OPENING_STUB_PATH, "phase_419_commit_modified_phase_414_cdl_047_opening_stub_unlawfully"),
        (CDL_048_OPENING_STUB_PATH, "phase_419_commit_modified_phase_414_cdl_048_opening_stub_unlawfully"),
        (CDL_047_HARDENING_PATH, "phase_419_commit_modified_phase_415_cdl_047_hardening_unlawfully"),
        (CDL_048_HARDENING_PATH, "phase_419_commit_modified_phase_416_cdl_048_hardening_unlawfully"),
        (PHASE_417_REVIEW_PATH, "phase_419_commit_modified_phase_417_review_artifact_unlawfully"),
        (CDL_047_EVIDENCE_PATH, "phase_419_commit_modified_phase_418_evidence_artifact_unlawfully"),
    ):
        old_text = _read_file_at_ref(f"{commit_ref}^1", str(path))
        new_text = _read_file_at_ref(commit_ref, str(path))
        assert old_text == new_text, token


def test_phase_419_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_419_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
