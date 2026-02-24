from __future__ import annotations

import datetime
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


EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_019_multiplier_governance_surface_ratification_evidence_268_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_268_CDL_019_ROW = (
    "| CDL-019 | ADR-0008 / NodeValueTrack | Multiplier-governance surface: resolve relationship between "
    "flat Genesis constant (1.2x), refutation-profitability invariant floor, and eventual dynamic ranking-based "
    "multiplier mechanism | open | flat Genesis constant only, governed constant + invariant floor, governed "
    "constant + dynamic ranking mechanism | governed constant + invariant floor (dynamic ranking deferred) | "
    "multiplier policy contract update, invariant regression coverage, governance migration plan |"
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


def _resolve_phase_268_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_268")


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Evidence chain summary",
        "## 3. CDL-019 option selection statement",
        "## 4. Invariant and migration closure statement",
        "## 5. Mutation protocol confirmation",
        "## 6. Non-goals",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    assert "governed constant + invariant floor" in text
    assert "CDL-031" in text
    assert "deferred" in text


def test_decision_log_cdl_019_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-019"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "268"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_019_multiplier_governance_surface_ratification_evidence_268_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_019() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_268_CDL_019_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-019"]))

    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-019")


def test_previously_ratified_rows_remain_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-001", "CDL-002", "CDL-007", "CDL-025", "CDL-032"]:
        assert rows[cdl_id]["status"] == "ratified", cdl_id


def test_non_target_issuance_rows_not_ratified_in_phase_268() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="268",
        target_cdls={"CDL-019"},
    )


def test_phase_268_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_268_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
