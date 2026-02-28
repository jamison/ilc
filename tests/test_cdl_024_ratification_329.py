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


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_024_wire_transport_ratification_evidence_329_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_322_TEST_PATH = Path("tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py")
PHASE_329_COMMIT_SUBJECT = "docs(g8): phase 329 cdl-024 ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_329_CDL_024_ROW = (
    "| CDL-024 | ADM-001 / Roadmap v0.3 | Wire protocol specification and transport bindings | "
    "open | single transport binding, transport-agnostic + reference bindings, framework-specific bindings | "
    "transport-agnostic + reference bindings (proposed) | D2d message schema set, transport requirements, conformance tests |"
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


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_329_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "	" not in line:
            continue
        commit_hash, subject = line.split("	", 1)
        if subject.strip() == PHASE_329_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_024_ratification_329.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_329_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_329_commit_not_present_in_local_history")


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
        "## 3. CDL-024 option inventory and selection statement",
        "## 4. Ratification record",
        "## 5. Mutation protocol confirmation",
        "## 6. Historical-prelock preservation note",
        "## 7. Non-goals",
        "## 8. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    for token in (
        "`transport-agnostic + reference bindings`",
        "`single transport binding`",
        "`framework-specific bindings`",
        "wire_transport_runtime_323.v0.1",
        "d2_schema_baseline_310.v0.1",
        "genesis_state_bundle_312.v0.1",
        "epoch_snapshot_runtime_314.v0.1",
        "docs/specs/ilc_wire_transport_contract_and_cdl_024_evidence_prelock_322_v0.1.md",
        "docs/specs/ilc_wire_transport_runtime_handoff_323_v0.1.md",
    ):
        assert token in text


def test_historical_prelock_hardening_patch_is_active() -> None:
    text = _read(PHASE_322_TEST_PATH)
    assert 'assert "status: open" in text' in text
    assert 'historical prelock artifact' in text


def test_decision_log_cdl_024_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-024"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "329"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_024_wire_transport_ratification_evidence_329_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_024() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_329_CDL_024_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-024"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-024")


def test_non_target_rows_not_ratified_in_phase_329() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="329",
        target_cdls={"CDL-024"},
    )


def test_full_non_target_row_mutation_guard_for_phase_329() -> None:
    commit_ref = _resolve_phase_329_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-024"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-024"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-024")

    for cdl_id in old_rows:
        if cdl_id == "CDL-024":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_329"


def test_phase_329_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_329_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
