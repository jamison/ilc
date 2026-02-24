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


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md")
PRELOCK_PATH = Path("docs/specs/ilc_cdl_033_openclaw_skill_publication_evidence_prelock_290_v0.1.md")
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

_PRE_291_CDL_033_ROW = (
    "| CDL-033 | ADM-002 / CDL-032 | OpenClaw skill specification and ClawHub publication contract | open | "
    "skill-only, skill + dedicated agent, full fleet config | "
    "skill-only initial (proposed) — dedicated agent config deferred to Phase B | "
    "SKILL.md spec, ClawHub PR, working CLI binary (CDL-032 prerequisite) |"
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


def _resolve_phase_291_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_291")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Evidence chain summary",
        "## 3. CDL-033 policy selection statement",
        "## 4. Ratified policy table and guardrail trace",
        "## 5. Mutation protocol confirmation",
        "## 6. Non-goals",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    assert "ratified_phase | `291`" in text


def test_prelock_anchor_present() -> None:
    assert PRELOCK_PATH.exists()
    text = _read(PRELOCK_PATH).lower()
    assert "phase-291 entry criteria" in text


def test_decision_log_cdl_033_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-033"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "291"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_033() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_291_CDL_033_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-033"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-033")


def test_previously_ratified_rows_remain_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in [
        "CDL-001",
        "CDL-002",
        "CDL-007",
        "CDL-019",
        "CDL-025",
        "CDL-026",
        "CDL-027",
        "CDL-028",
        "CDL-029",
        "CDL-030",
        "CDL-031",
        "CDL-032",
    ]:
        assert rows[cdl_id]["status"] == "ratified", cdl_id


def test_non_target_rows_not_ratified_in_phase_291() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="291",
        target_cdls={"CDL-033"},
    )


def test_full_non_target_row_mutation_guard_for_phase_291() -> None:
    commit_ref = _resolve_phase_291_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-033"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-033"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-033")

    for cdl_id in old_rows:
        if cdl_id == "CDL-033":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"Row {cdl_id} unlawfully mutated in Phase 291"


def test_phase_291_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_291_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
