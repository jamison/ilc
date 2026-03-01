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


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v2_sybil_resistance_ratification_evidence_331_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_324_TEST_PATH = Path("tests/test_cdl_v_batch_a_open_and_evidence_prelock_324.py")
PHASE_331_COMMIT_SUBJECT = "docs(g8): phase 331 cdl-v2 ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_331_CDL_V2_ROW = (
    "| CDL-V2 | CDL-001 / CDL-033 / Vulnerability Plan v0.1 | Sybil resistance mechanism for participant identity and reuse validation | "
    "open | proof-of-personhood gate, stake-based participation cost, hybrid heuristic resistance | "
    "hybrid heuristic resistance (proposed) | sybil threat model, synthetic graph simulations, operator response thresholds |"
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


def _resolve_phase_331_commit_ref() -> str:
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
        if subject.strip() == PHASE_331_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        str(PHASE_324_TEST_PATH),
        "tests/test_cdl_v2_ratification_331.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_331_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_331_commit_not_present_in_local_history")


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
        "## 3. CDL-V2 option inventory and selection statement",
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
        "`hybrid heuristic resistance`",
        "`proof-of-personhood gate`",
        "`stake-based participation cost`",
        "Section 3 of `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md` is authoritative",
        "`a sybil threat model covering reuse-event inflation and coordinated cluster gaming`",
        "`synthetic graph simulation demonstrating expected containment effectiveness`",
        "`monitoring/operator threshold proposal for suspicious reuse velocity, burst patterns, or isolated cluster anomalies`",
        "`clear identity-surface integration notes describing how the chosen mechanism interacts with participant identity validation`",
        "leading step in the `CDL-V2 -> CDL-V3 -> CDL-V4` sequence",
        "docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md",
        "docs/specs/ilc_d2e_04_identity_subsystem_contract_293_v0.1.md",
        "identity-surface anchor for `CDL-V2`, not by itself full anti-sybil enforcement",
    ):
        assert token in text


def test_phase_324_historical_prelock_hardening_patch_is_active() -> None:
    text = _read(PHASE_324_TEST_PATH)
    assert "assert EXPECTED_V2_ROW in historical_text" in text
    assert "assert EXPECTED_V3_ROW in historical_text" in text
    assert 'assert rows["CDL-V2"]["status"] == "open"' not in text
    assert 'assert rows["CDL-V3"]["status"] == "open"' not in text
    assert "historical_rows = parse_decision_register_rows(historical_text)" in text
    assert 'for cdl_id in ("CDL-V1", "CDL-V2", "CDL-V3")' in text
    assert "historical prelock reference" in text


def test_decision_log_cdl_v2_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-V2"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "331"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_v2_sybil_resistance_ratification_evidence_331_v0.1.md"
    )


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_v2() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_331_CDL_V2_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-V2"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-V2")


def test_non_target_rows_not_ratified_in_phase_331() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="331",
        target_cdls={"CDL-V2"},
    )


def test_full_non_target_row_mutation_guard_for_phase_331() -> None:
    commit_ref = _resolve_phase_331_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-V2"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-V2"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-V2")

    for cdl_id in old_rows:
        if cdl_id == "CDL-V2":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_331"


def test_phase_331_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_331_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
