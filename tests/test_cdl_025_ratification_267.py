from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_267_COMMIT_SUBJECT = "docs(g8): phase 267 cdl-025 terminal issuance model ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_267_CDL_025_ROW = (
    "| CDL-025 | CDL-005 | Terminal issuance model (hard cap vs. tail emission reconciliation) | "
    "open | asymptotic cap (Model A), fee-funded tail (Model B), burn-offset tail (Model C) | "
    "fee-funded tail / Model B (planning recommendation — not ratified) | "
    "terminal model spec, issuance simulation |"
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


def _resolve_phase_267_commit_ref() -> str:
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
        if subject.strip() == PHASE_267_COMMIT_SUBJECT:
            return commit_hash
    return "HEAD"


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Evidence chain summary",
        "## 3. CDL-025 option selection statement",
        "## 4. Mutation protocol confirmation",
        "## 5. Non-goals",
        "## 6. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    assert any(model in text for model in ("Model A", "Model B", "Model C"))
    assert (
        "ilc_issuance_governance_activation_survey_247_v0.1.md" in text
        or "Phase-247" in text
    )


def test_decision_log_cdl_025_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-025"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "267"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_025() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_267_CDL_025_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-025"]))

    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-025")


def test_non_target_rows_not_ratified_in_phase_267() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    # CDL-019 was open during Phase 267 and ratified later in Phase 268.
    assert rows["CDL-019"].get("ratified_phase") != "267", "CDL-019"
    for cdl_id in ["CDL-026", "CDL-027", "CDL-028", "CDL-029", "CDL-030", "CDL-031"]:
        # Phase-scoped invariant: these rows must not be ratified by Phase 267.
        assert rows[cdl_id].get("ratified_phase") != "267", cdl_id


def test_previously_ratified_cdls_unchanged() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-001", "CDL-002", "CDL-007", "CDL-025", "CDL-032"]:
        assert rows[cdl_id]["status"] == "ratified", cdl_id


def test_phase_267_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_267_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
