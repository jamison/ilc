from __future__ import annotations

import datetime
import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md")
CARRY_FORWARD_PATH = Path("docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_276_COMMIT_SUBJECT = "docs(g8): phase 276 cdl-027 decay formulation ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_276_CDL_027_ROW = (
    "| CDL-027 | CDL-005 / CDL-026 | Decay formulation and schedule constants (`H` or `lambda`) | open | "
    "discrete halving period `H`, continuous decay rate `lambda` | depends on CDL-026 closure | "
    "decay schedule spec, schedule simulation |"
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


def _resolve_phase_276_commit_ref() -> str:
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
        if subject.strip() == PHASE_276_COMMIT_SUBJECT:
            return commit_hash
    return "HEAD"


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


def _extract(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"missing_{label}")
    return match.group(1).strip()


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Evidence chain summary",
        "## 3. CDL-027 formulation selection statement",
        "## 4. Ratified constants and schedule table",
        "## 5. Mutation protocol confirmation",
        "## 6. Non-goals",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    assert "selected formulation: `halving`" in text
    assert "selected schedule constant: `H = 48`" in text
    assert "selected epoch duration: `1 month`" in text


def test_phase_275_carry_forward_values_match_phase_276_ratified_values_exactly() -> None:
    assert CARRY_FORWARD_PATH.exists(), "phase 275 carry-forward artifact missing"
    carry_forward_text = _read(CARRY_FORWARD_PATH)
    ratified_text = _read(EVIDENCE_PATH)

    carry_family = _extract(
        r"schedule family:\s*`([^`]+)`",
        carry_forward_text,
        "carry_forward_schedule_family",
    )
    carry_constant = _extract(
        r"schedule constant:\s*`([^`]+)`",
        carry_forward_text,
        "carry_forward_schedule_constant",
    )
    carry_epoch = _extract(
        r"epoch duration candidate:\s*`([^`]+)`",
        carry_forward_text,
        "carry_forward_epoch_duration",
    )

    ratified_family = _extract(
        r"selected formulation:\s*`([^`]+)`",
        ratified_text,
        "ratified_schedule_family",
    )
    ratified_constant = _extract(
        r"selected schedule constant:\s*`([^`]+)`",
        ratified_text,
        "ratified_schedule_constant",
    )
    ratified_epoch = _extract(
        r"selected epoch duration:\s*`([^`]+)`",
        ratified_text,
        "ratified_epoch_duration",
    )

    assert ratified_family == carry_family
    assert ratified_constant == carry_constant
    assert ratified_epoch == carry_epoch


def test_decision_log_cdl_027_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-027"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "276"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_027() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_276_CDL_027_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-027"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-027")


def test_previously_ratified_rows_remain_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-001", "CDL-002", "CDL-007", "CDL-019", "CDL-025", "CDL-026", "CDL-028", "CDL-029", "CDL-032"]:
        assert rows[cdl_id]["status"] == "ratified", cdl_id


def test_non_target_issuance_rows_not_ratified_in_phase_276() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-030", "CDL-031"]:
        assert rows[cdl_id].get("ratified_phase") != "276", cdl_id


def test_full_non_target_row_mutation_guard_for_phase_276() -> None:
    commit_ref = _resolve_phase_276_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-027"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-027"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-027")

    for cdl_id in old_rows:
        if cdl_id == "CDL-027":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"Row {cdl_id} unlawfully mutated in Phase 276"


def test_phase_276_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_276_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
