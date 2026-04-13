from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    parse_decision_register_rows,
)

EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_064_exact_numeric_representation_ratification_evidence_634_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_634_cdl_064_exact_numeric_representation_ratification.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_634_g8_cdl_064_ratification_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_634_EVIDENCE_SUBJECT = (
    "phase 634 cdl-064 exact numeric representation ratification evidence"
)
PHASE_634_RATIFIED_SUBJECT = "phase 634 cdl-064 ratified"
PHASE_634_BACKFILL_SUBJECT = "phase 634 walkthrough and status backfill"
EXACT_REQUIRED_EVIDENCE_PATHS = {str(EVIDENCE_PATH), str(TEST_PATH)}
EXACT_REQUIRED_CDL_PATHS = {str(DECISION_LOG_PATH)}
EXACT_REQUIRED_BACKFILL_PATHS = {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
REQUIRED_HEADINGS = (
    "## 1. Ratification identity and prelock lineage",
    "## 2. Final constitutional clause text",
    "## 3. Representation decision and canonical serialization rule",
    "## 4. Ratification readiness evidence checklist satisfaction",
    "## 5. Mutation scope and invariants",
)
REQUIRED_TOKENS = (
    "cdl_064_ratified_634",
    "cdl_064_exact_numeric_boundary_ratified",
    "cdl_064_exact_arithmetic_rule_ratified",
    "cdl_064_canonical_serialization_rule_ratified",
    "cdl_064_tier0_scope_boundary_ratified",
    "cdl_064_selected_representation_locked",
    "float_retention_rejected_by_cdl_064",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
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
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def test_evidence_document_exists_and_contains_required_headings() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_evidence_document_contains_required_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_contains_all_four_constitutional_clause_classes() -> None:
    text = _read(EVIDENCE_PATH)
    assert "**Clause A — Exact numeric representation requirement**" in text
    assert "**Clause B — Exact arithmetic requirement**" in text
    assert "**Clause C — Canonical machine serialization rule**" in text
    assert "**Clause D — Tier-0 scope boundary and non-goals**" in text


def test_section_three_records_selected_representation_and_canonical_serialization_rule() -> None:
    text = _read(EVIDENCE_PATH)
    assert "`exact-decimal-runtime-contract`" in text
    assert "Tier-0 exact numeric values serialize as normalized decimal strings" in text
    assert "canonical examples: `0`, `0.05`, `1`, `1.25`, `400`" in text
    assert "non-canonical examples: `0.0`, `01.25`, `1.2500`, `1e-3`, `-0`" in text
    assert "does not ratify a universal minor-unit scale" in text


def test_section_four_satisfies_all_five_readiness_checklist_items() -> None:
    text = _read(EVIDENCE_PATH)
    assert "tier0_numeric_inventory_632_locked" in text
    assert "cdl_064_prelock_633_locked" in text
    assert "retain-float-rounding-and-tolerance" in text
    assert "exact-decimal-runtime-contract" in text
    assert "fixed-point-minor-unit-contract" in text
    assert "float_retention_rejected_for_tier0" in text
    assert "does not widen Option-B, wallet, or" in text
    assert "ILC-transfer scope" in text


def test_cdl_064_row_is_ratified_after_commit_2() -> None:
    _require_commit_or_skip(PHASE_634_RATIFIED_SUBJECT)
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-064"]["status"] == "ratified"
    assert rows["CDL-064"]["ratified_phase"] == "634"
    assert rows["CDL-064"]["ratified_date"] == "2026-04-13"
    assert rows["CDL-064"]["evidence_document"] == str(EVIDENCE_PATH)


def test_commit_1_evidence_touches_expected_paths_only_and_no_cdl_mutation() -> None:
    _require_commit_or_skip(PHASE_634_EVIDENCE_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_634_EVIDENCE_SUBJECT,
        expected_paths=EXACT_REQUIRED_EVIDENCE_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_EVIDENCE_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_commit_2_cdl_update_touches_decision_log_only() -> None:
    _require_commit_or_skip(PHASE_634_RATIFIED_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_634_RATIFIED_SUBJECT,
        expected_paths=EXACT_REQUIRED_CDL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_CDL_PATHS
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows["CDL-064"]["status"] == "ratified"
    assert rows["CDL-064"]["ratified_phase"] == "634"


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_634_BACKFILL_SUBJECT)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_634_BACKFILL_SUBJECT,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
