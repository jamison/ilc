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


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v5_schema_epoch_translation_ratification_evidence_333_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_325_TEST_PATH = Path("tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py")
PHASE_333_COMMIT_SUBJECT = "docs(g8): phase 333 cdl-v5 ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_333_CDL_V5_ROW = (
    "| CDL-V5 | CDL-020 / CDL-023 / Vulnerability Plan v0.1 | Schema epoch markers and cross-version translation protocol for centrality comparability | "
    "open | no epoch markers, schema epoch markers only, schema epoch markers plus explicit cross-version translation | "
    "schema epoch markers plus explicit cross-version translation (proposed) | translation invariance test vectors, epoch-marker serialization contract, backward-compatibility thresholds |"
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


def _resolve_phase_333_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_333_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        str(PHASE_325_TEST_PATH),
        "tests/test_cdl_v5_ratification_333.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_333_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_333_commit_not_present_in_local_history")


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
        "## 3. CDL-V5 option inventory and selection statement",
        "## 4. Section-3 authoritative evidence checklist satisfaction",
        "## 5. Ratification record",
        "## 6. Mutation protocol confirmation",
        "## 7. Historical-prelock preservation note",
        "## 8. Non-goals",
        "## 9. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    for token in (
        "`schema epoch markers plus explicit cross-version translation`",
        "`no epoch markers`",
        "`schema epoch markers only`",
        "Section 3 of `docs/specs/ilc_cdl_v5_schema_epoch_translation_evidence_prelock_325_v0.1.md` is authoritative",
        "`translation invariance test vectors covering representative schema-epoch transitions`",
        "`epoch-marker serialization contract specifying how schema epoch identifiers enter canonical artifacts`",
        "`backward-compatibility thresholds defining when translation is acceptable versus incommensurable`",
        "`explicit tie-back to schema and snapshot runtime surfaces already ratified in the current window`",
        "leading step in the `CDL-V5 -> CDL-V7` sequence",
        "non-comparable by design",
        "docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md",
        "docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md",
        "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md",
    ):
        assert token in text


def test_phase_325_historical_prelock_hardening_patch_is_active() -> None:
    text = _read(PHASE_325_TEST_PATH)
    assert "assert EXPECTED_V4_ROW in historical_text" in text
    assert "assert EXPECTED_V5_ROW in historical_text" in text
    assert "assert EXPECTED_V6_ROW in historical_text" in text
    assert 'assert rows["CDL-V4"]["status"] == "open"' not in text
    assert 'assert rows["CDL-V5"]["status"] == "open"' not in text
    assert 'assert rows["CDL-V6"]["status"] == "open"' not in text
    assert 'for cdl_id in ("CDL-V7",)' in text
    assert 'for cdl_id in ("CDL-V4", "CDL-V6", "CDL-V7")' not in text
    assert "# The Phase-325 `CDL-V4` row is a historical prelock reference" in text
    assert "# The Phase-325 `CDL-V6` row is a historical prelock reference" in text


def test_decision_log_cdl_v5_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-V5"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "333"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_v5_schema_epoch_translation_ratification_evidence_333_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_v5() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_333_CDL_V5_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-V5"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-V5")


def test_non_target_rows_not_ratified_in_phase_333() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="333",
        target_cdls={"CDL-V5"},
    )


def test_full_non_target_row_mutation_guard_for_phase_333() -> None:
    commit_ref = _resolve_phase_333_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-V5"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-V5"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-V5")

    for cdl_id in old_rows:
        if cdl_id == "CDL-V5":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_333"


def test_phase_333_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_333_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
