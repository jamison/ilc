from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_020_d2_schema_baseline_ratification_evidence_319_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_319_COMMIT_SUBJECT = "docs(g8): phase 319 cdl-020 ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_319_CDL_020_ROW = (
    "| CDL-020 | ADM-001 / Roadmap v0.3 | Protocol-native bundle schema and complete type system | "
    "open | full schema catalog, minimal schema catalog, phased schema catalog | "
    "full schema catalog (proposed) | D2 schema artifact set, bundle generator/verifier tooling, test vectors |"
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


def _resolve_phase_319_commit_ref() -> str:
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
        if subject.strip() == PHASE_319_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_319_commit_not_present_in_local_history")


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
        "## 3. CDL-020 option inventory and selection statement",
        "## 4. Ratification record",
        "## 5. Mutation protocol confirmation",
        "## 6. Non-goals",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    for token in (
        "`full schema catalog`",
        "`minimal schema catalog`",
        "`phased schema catalog`",
        "d2_schema_baseline_310.v0.1",
        "docs/specs/ilc_d2_schema_baseline_contract_and_cdl_020_evidence_prelock_309_v0.1.md",
        "docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md",
    ):
        assert token in text


def test_decision_log_cdl_020_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-020"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "319"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_020_d2_schema_baseline_ratification_evidence_319_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_020() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_319_CDL_020_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-020"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-020")


def test_non_target_rows_not_ratified_in_phase_319() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="319",
        target_cdls={"CDL-020"},
    )


def test_full_non_target_row_mutation_guard_for_phase_319() -> None:
    commit_ref = _resolve_phase_319_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-020"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-020"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-020")

    for cdl_id in old_rows:
        if cdl_id == "CDL-020":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_319"


def test_phase_319_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_319_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
