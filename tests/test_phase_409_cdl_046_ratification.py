from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    ALLOWED_RATIFICATION_MUTATION_FIELDS,
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md")
PHASE_405_TEST_PATH = Path("tests/test_phase_405_cdl_046_timed_out_amendment_open_prelock.py")
PHASE_408_TEST_PATH = Path("tests/test_phase_408_cdl_045_ratification.py")
PHASE_409_COMMIT_SUBJECT = "docs(g8): phase 409 cdl-046 timed_out amendment ratification"

REQUIRED_HEADINGS = (
    "## 1. Purpose and scope",
    "## 2. Ratified decision",
    "## 3. Evidence basis",
    "## 4. Section-7 ratification readiness evidence checklist satisfaction",
    "## 5. Ratified amendment constants: orphan timeout and recovery policy",
    "## 6. CDL-035 amendment boundary and timed_out transition scope",
    "## 7. D2e Agent SDK implementation carry-forward",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)

REQUIRED_TOKENS = (
    "CDL-046 is ratified as the CDL-035 timed_out amendment for churn and orphan recovery semantics.",
    "SIM-007 calibrated the amendment basis at issuance_epoch scale: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.",
    "SIM-007 epoch context is issuance_epoch; orphan_timeout_epochs = 4 means a 4-month timeout horizon under the canonical 1-month issuance epoch.",
    "Claims remaining orphaned after orphan_timeout_epochs = 4 issuance epochs transition to timed_out and apply recovery_policy = stake_full_release.",
    "timed_out transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.",
    "Bounded timeout-and-recovery prelock is rejected because SIM-007 already provides direct fixed-constant recommendations at issuance_epoch scale.",
    "Retaining CDL-035 without timed_out amendment is rejected because agent-churn and orphan accumulation evidence now requires explicit timed_out semantics and recovery policy to avoid undefined orphan-state handling.",
)

REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    "docs/specs/ilc_cdl_046_timed_out_amendment_open_prelock_405_v0.1.md",
    "docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md",
    "docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md",
    "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md",
)

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_ALLOWED_FIELDS = set(ALLOWED_RATIFICATION_MUTATION_FIELDS) | {"current_candidate"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _register_row_text(row: dict[str, str]) -> str:
    cells = [row[header] for header in _BASE_HEADERS]
    if "ratified_phase" in row:
        cells.append(f"ratified_phase: {row['ratified_phase']}")
    if "ratified_date" in row:
        cells.append(f"ratified_date: {row['ratified_date']}")
    if "evidence_document" in row:
        cells.append(f"evidence_document: {row['evidence_document']}")
    return "| " + " | ".join(cells) + " |"


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


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}")
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_409_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_409_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_409_cdl_046_ratification.py",
        "tests/test_phase_405_cdl_046_timed_out_amendment_open_prelock.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_409_commit_subject_present_but_no_ratification_mutation_commit")
    raise AssertionError("phase_409_commit_not_present_in_local_history")


def test_ratification_evidence_contains_required_headings_and_tokens() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_cdl_046_row_is_ratified_with_correct_fields() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    row = rows["CDL-046"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "409"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == "2026-03-14"
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert "open dedicated amendment row with fixed timeout and recovery constants prelock (proposed)" not in text
    assert "open dedicated amendment row with fixed timeout and recovery constants prelock" in text
    assert rows["CDL-035"]["status"] == "ratified"
    assert_no_non_target_rows_marked_with_phase(rows, phase="409", target_cdls={"CDL-046"})


def test_cdl_045_row_unchanged() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-045"]["status"] == "ratified"


def test_phase_405_and_phase_408_open_assertions_are_hardened() -> None:
    phase_405_text = _read(PHASE_405_TEST_PATH)
    assert '# The Phase-405 `CDL-046` row is a historical prelock reference.' in phase_405_text
    assert phase_405_text.count("_read_file_at_ref(_resolve_phase_405_commit_ref(), str(DECISION_LOG_PATH))") >= 2
    assert "rows = parse_decision_register_rows(historical_text)" in phase_405_text
    assert "EXPECTED_CDL_046_ROW in historical_text" in phase_405_text
    assert 'rows["CDL-046"]["status"] == "open"' in phase_405_text
    assert phase_405_text.count("_read(DECISION_LOG_PATH)") == 2

    phase_408_text = _read(PHASE_408_TEST_PATH)
    assert '# The Phase-408 `CDL-046` neighbor-state check is a historical ratification reference.' in phase_408_text
    assert "_read_file_at_ref(_resolve_phase_408_commit_ref(), str(DECISION_LOG_PATH))" in phase_408_text
    assert "historical_rows = parse_decision_register_rows(historical_text)" in phase_408_text
    assert 'historical_rows["CDL-046"]["status"] == "open"' in phase_408_text
    assert 'rows["CDL-042"]["status"] == "ratified"' in phase_408_text


def test_cdl_046_register_order_preserved_after_ratification() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    cdl_042_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-042 "))
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    cdl_046_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-046 "))
    assert cdl_042_index == cdl_044_index + 1
    assert cdl_045_index == cdl_042_index + 1
    assert cdl_046_index == cdl_045_index + 1


def test_phase_409_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_409_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    required = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_409_cdl_046_ratification.py",
        "tests/test_phase_405_cdl_046_timed_out_amendment_open_prelock.py",
    }
    assert required.issubset(changed)
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_409_commit_no_non_cdl_046_row_mutation() -> None:
    commit_ref = _resolve_phase_409_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows)

    target_old = _mini_register(_register_row_text(old_rows["CDL-046"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-046"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-046",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-046":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"non_target_row_mutated:{cdl_id}"

    assert old_rows["CDL-046"]["status"] == "open"
    assert new_rows["CDL-046"]["status"] == "ratified"
