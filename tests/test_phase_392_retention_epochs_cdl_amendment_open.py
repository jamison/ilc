from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_392_401_sequence_lock_v0.1.md")
PRELOCK_PATH = Path("docs/specs/ilc_cdl_044_retention_epochs_amendment_open_prelock_392_v0.1.md")
PHASE_392_SUBJECT_TOKEN = "phase 392 seq lock and retention epochs amendment open"
EXPECTED_ROW = (
    "| CDL-044 | CDL-039 / SIM-003 / Phase-391 Handoff 391 v0.1 | retention_epochs operational amendment for "
    "CDL-039 deployment boundary | open | retain deferred obligation without amendment row, open dedicated "
    "amendment row with bounded-range prelock, open dedicated amendment row with fixed constant prelock | open "
    "dedicated amendment row with bounded-range prelock (proposed) | Phase-379 retention obligation token, "
    "SIM-003 retention calibration anchor, Phase-391 handoff carry-forward token |"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_392_commit_ref() -> str:
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
        if PHASE_392_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(SEQUENCE_LOCK_PATH),
        str(PRELOCK_PATH),
        "tests/test_phase_392_retention_epochs_cdl_amendment_open.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_392_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_392_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def test_sequence_lock_exists_and_contains_required_headings_and_tokens() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)

    for heading in (
        "## 1. Window identity and scope",
        "## 2. Inputs and closure inheritance",
        "## 3. SIM-006/007 branch resolution",
        "## 4. Locked phase table (392-401)",
        "## 5. Constitutional first-action requirement",
        "## 6. Sequencing constraints and dependency ordering",
        "## 7. Deferred tracks and SIM-008 gate",
        "## 8. Canonical anchors and non-goals",
    ):
        assert heading in text

    for token in (
        "Window 392-401 is the Ratification Settlement and V-series Resolution Block.",
        "The first constitutional action of Window 392+ is opening the retention_epochs amendment required by CDL-039 ratification evidence and carried through Phase 391 handoff.",
        "SIM-006 favorable branch is locked: recommended_panel_assignment_policy: diversity_weighted.",
        "SIM-007 carry-forward to CDL-035 amendment lane is locked: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.",
        "CDL-040/041/043 ratifications must complete before CDL-042 opening.",
        "D2e implementation remains deferred to Window 402+ pending CDL-042 opening.",
        "Treasury governance CDL cluster and mandatory ECU conversion deadline CDL are explicitly deferred to Window 402+ and gated on SIM-008.",
    ):
        assert token in text


def test_prelock_exists_and_contains_required_headings_and_tokens() -> None:
    assert PRELOCK_PATH.exists()
    text = _read(PRELOCK_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-044 opening state",
        "## 3. Constitutional obligation anchors",
        "## 4. Calibration anchor and bounded-range rationale",
        "## 5. Evidence-assembly plan (393-398)",
        "## 6. Sequencing and dependency constraints",
        "## 7. Out-of-scope and deferred tracks",
        "## 8. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-044 opens as the retention_epochs constitutional amendment lane required by CDL-039 ratification carry-forward obligations.",
        "SIM-003 retention_epochs=1 is the floor anchor for calibration; this opening does not ratify a fixed operational value.",
        "Phase-399 is the targeted ratification lane for CDL-044 pending evidence assembly through Phases 393-398.",
        "No runtime implementation occurs in Phase 392.",
        "Treasury governance CDL cluster and mandatory ECU conversion deadline CDL remain out-of-scope in this phase and SIM-008 gated.",
    ):
        assert token in text


def test_decision_log_contains_exact_cdl_044_opening_row_and_token() -> None:
    text = _read(DECISION_LOG_PATH)
    assert EXPECTED_ROW in text
    rows = parse_decision_register_rows(text)
    assert rows["CDL-044"]["status"] == "open"
    assert "Phase-379 retention obligation token" in rows["CDL-044"]["required_artifacts"]


def test_cdl_044_row_is_appended_after_cdl_043_in_raw_order() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    row_043_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-043 "))
    row_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    assert row_044_index == row_043_index + 1


def test_cdl_043_row_remains_open_in_live_decision_log() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-043"]["status"] == "open"


def test_phase_392_commit_additive_only_non_target_shield_and_new_row_guard() -> None:
    commit_ref = _resolve_phase_392_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-044"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_392"


def test_phase_392_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_392_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
