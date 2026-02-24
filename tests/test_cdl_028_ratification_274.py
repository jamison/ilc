from __future__ import annotations

import datetime
import re
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.phase_commit_manifest import resolve_phase_commit_ref_or_skip

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
FIX1_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_028_fee_burn_split_candidate_lock_274_fix1_v0.1.md")

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_274_CDL_028_ROW = (
    "| CDL-028 | CDL-005 / CDL-025 | Fee-burn split ratio | open | 30% burn, 50% burn, other percentages | "
    "depends on CDL-025 terminal model closure | fee model spec, payout regression |"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _register_row_text(row: dict[str, str]) -> str:
    cells = [row[header] for header in _BASE_HEADERS]
    if "ratified_phase" in row:
        cells.append(f"ratified_phase: {row['ratified_phase']}")
    if "ratified_date" in row:
        cells.append(f"ratified_date: {row['ratified_date']}")
    if "evidence_document" in row:
        cells.append(f"evidence_document: {row['evidence_document']}")
    return "| " + " | ".join(cells) + " |"


def _resolve_phase_274_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_274")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}"
        )
    return result.stdout


def _extract_percent_token(*, text: str, pattern: str, label: str) -> str:
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"missing_{label}_percent_token")
    return match.group(1)


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Evidence chain summary",
        "## 3. CDL-028 option selection statement",
        "## 4. Mutation protocol confirmation",
        "## 5. Non-goals",
        "## 6. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    assert "selected option for ratification in Phase 274" in text
    assert "`other percentages`" in text
    assert "fee-burn ratio = `10%`" in text
    assert "deferred to Phase 275/276 (`CDL-027` lane)" in text


def test_decision_log_cdl_028_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-028"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "274"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_028() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_274_CDL_028_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-028"]))

    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-028")


def test_previously_ratified_rows_remain_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-001", "CDL-002", "CDL-007", "CDL-019", "CDL-025", "CDL-026", "CDL-029", "CDL-032"]:
        assert rows[cdl_id]["status"] == "ratified", cdl_id


def test_non_target_issuance_rows_not_ratified_in_phase_274() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="274",
        target_cdls={"CDL-028"},
    )


def test_phase_274_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_274_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_ratified_value_exactly_matches_fix1_simulation_selected_candidate() -> None:
    assert FIX1_EVIDENCE_PATH.exists(), "fix1 evidence missing"
    fix1_text = _read(FIX1_EVIDENCE_PATH)
    evidence_text = _read(EVIDENCE_PATH)

    fix1_percent = _extract_percent_token(
        text=fix1_text,
        pattern=r"percentage:\s*`([^`]+)`",
        label="fix1",
    )
    ratified_percent = _extract_percent_token(
        text=evidence_text,
        pattern=r"fee-burn ratio\s*=\s*`([^`]+)`",
        label="ratification",
    )
    assert ratified_percent == fix1_percent


def test_full_non_target_row_mutation_guard_for_phase_274() -> None:
    commit_ref = _resolve_phase_274_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-028"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-028"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-028")

    for cdl_id in old_rows:
        if cdl_id == "CDL-028":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"Row {cdl_id} unlawfully mutated in Phase 274"
