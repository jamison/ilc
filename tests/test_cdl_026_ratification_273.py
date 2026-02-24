from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_273_COMMIT_SUBJECT = "docs(g8): phase 273 cdl-026 cmax lock ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_273_CDL_026_ROW = (
    "| CDL-026 | CDL-005 / CDL-025 | Total supply cap (`C_max`) lock | open | explicit finite cap, cap-with-tolerance | "
    "depends on CDL-025 closure | cap lock spec, regression tests |"
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


def _resolve_phase_273_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_273_COMMIT_SUBJECT:
            return commit_hash
    pytest.skip("phase_commit_subject_not_found: commit-scoped assertions skipped")


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Evidence chain summary",
        "## 3. CDL-026 option selection statement",
        "## 4. Mutation protocol confirmation",
        "## 5. Non-goals",
        "## 6. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    assert "explicit finite cap" in text
    assert "not `cap-with-tolerance`" in text
    assert "Selected `C_max` lock candidate" in text


def test_decision_log_cdl_026_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-026"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "273"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_026() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_273_CDL_026_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-026"]))

    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-026")


def test_previously_ratified_rows_remain_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-001", "CDL-002", "CDL-007", "CDL-019", "CDL-025", "CDL-029", "CDL-032"]:
        assert rows[cdl_id]["status"] == "ratified", cdl_id


def test_non_target_issuance_rows_not_ratified_in_phase_273() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-027", "CDL-028", "CDL-030", "CDL-031"]:
        assert rows[cdl_id].get("ratified_phase") != "273", cdl_id


def test_phase_273_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_273_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
