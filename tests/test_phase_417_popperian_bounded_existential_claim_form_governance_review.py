from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REVIEW_PATH = Path("docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md")
PHASE_414_SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md")
CDL_047_OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_opening_stub_414_v0.1.md")
CDL_048_OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_opening_stub_414_v0.1.md")
CDL_047_HARDENING_PATH = Path("docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md")
CDL_048_HARDENING_PATH = Path("docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md")
PHASE_417_SUBJECT_TOKEN = "phase 417 popperian bounded-existential claim form governance review"
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. Review corpus and methodology",
    "## 3. Window-414 blocking-rule application summary",
    "## 4. CDL-047 bounded-existential review result",
    "## 5. CDL-048 bounded-existential review result",
    "## 6. Cross-window Popperian finding outside CDL-047 and CDL-048",
    "## 7. Window-424+ disposition and CDL-049 forward pointer",
    "## 8. Non-goals and canonical anchors",
)
REQUIRED_TOKENS = (
    "Phase 417 is a non-ratifying governance review and does not open, amend, or ratify any CDL row.",
    "CDL-047 review verdict: CLEAN.",
    "CDL-048 review verdict: CLEAN.",
    "No CDL-047-specific or CDL-048-specific CRITICAL findings were identified; Phase 418 and Phase 419 are not blocked by Phase 417.",
    "MODERATE finding: CDL-V7 runtime and supporting governance text admit existential claim forms without an explicit bounded-existential qualifier.",
    "Recommended disposition: designate CDL-049 as the first constitutional planning lane of Window 424+ to resolve bounded-existential claim-form wording and runtime tokenization.",
    "This finding is outside CDL-047 and CDL-048 and therefore does not block Window 414-423 execution under the Phase-417 blocking rule.",
    "ilc_core/consensus/popperian_gate_runtime.py",
    "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md",
    "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
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


def _resolve_phase_417_commit_ref() -> str:
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
        if PHASE_417_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(REVIEW_PATH),
        "tests/test_phase_417_popperian_bounded_existential_claim_form_governance_review.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_417_commit_subject_present_but_no_review_artifact_commit")
    raise AssertionError("phase_417_commit_not_present_in_local_history")


def test_review_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    assert REVIEW_PATH.exists()
    text = _read(REVIEW_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_cdl_047_and_cdl_048_are_still_open_and_cdl_049_absent() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-047"]["status"] == "open"
    assert rows["CDL-048"]["status"] == "open"
    assert "CDL-049" not in rows


def test_phase_414_phase_415_and_phase_416_artifacts_remain_present() -> None:
    assert PHASE_414_SEQUENCE_LOCK_PATH.exists()
    assert CDL_047_OPENING_STUB_PATH.exists()
    assert CDL_048_OPENING_STUB_PATH.exists()
    assert CDL_047_HARDENING_PATH.exists()
    assert CDL_048_HARDENING_PATH.exists()


def test_review_records_clean_verdict_for_cdl_047_and_cdl_048() -> None:
    text = _read(REVIEW_PATH)
    assert "CDL-047 review verdict: CLEAN." in text
    assert "CDL-048 review verdict: CLEAN." in text
    assert "bounded governance-parameter lane" in text
    assert "bounded lifecycle-deadline lane" in text


def test_review_records_moderate_cross_window_finding_and_non_blocking_disposition() -> None:
    text = _read(REVIEW_PATH)
    assert "MODERATE finding: CDL-V7 runtime and supporting governance text admit existential claim forms without an explicit bounded-existential qualifier." in text
    assert '`_ADMISSIBLE_CLAIM_FORMS = {"singular", "existential", "falsifiable_positive"}`' in text
    assert "CDL-049 is not opened in Phase 417 and remains a Window 424+ planning obligation only." in text


def test_phase_417_commit_touched_no_decision_log_runtime_or_prelock_files() -> None:
    commit_ref = _resolve_phase_417_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert old_rows == new_rows, "phase_417_commit_modified_decision_log_unlawfully"

    path_and_token_pairs = (
        (PHASE_414_SEQUENCE_LOCK_PATH, "phase_417_commit_modified_phase_414_sequence_lock_unlawfully"),
        (CDL_047_OPENING_STUB_PATH, "phase_417_commit_modified_phase_414_cdl_047_opening_stub_unlawfully"),
        (CDL_048_OPENING_STUB_PATH, "phase_417_commit_modified_phase_414_cdl_048_opening_stub_unlawfully"),
        (CDL_047_HARDENING_PATH, "phase_417_commit_modified_phase_415_cdl_047_hardening_unlawfully"),
        (CDL_048_HARDENING_PATH, "phase_417_commit_modified_phase_416_cdl_048_hardening_unlawfully"),
    )
    for path, token in path_and_token_pairs:
        old_text = _read_file_at_ref(f"{commit_ref}^1", str(path))
        new_text = _read_file_at_ref(commit_ref, str(path))
        assert old_text == new_text, token


def test_phase_417_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_417_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
