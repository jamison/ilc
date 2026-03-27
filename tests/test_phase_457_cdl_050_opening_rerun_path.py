from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_050_constitutional_treasury_ecu_governor_opening_stub_457_v0.1.md")
TEST_PATH = Path("tests/test_phase_457_cdl_050_opening_rerun_path.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_457_g8_cdl_050_opening_rerun_path_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_457_SUBJECT_TOKEN = "phase 457 cdl-050 opening under rerun path"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(OPENING_STUB_PATH),
    str(TEST_PATH),
}
EXPECTED_CDL_050_ROW = (
    "| CDL-050 | Phase-450 / Phase-451 / Phase-452 / Phase-456-Fix-14 | constitutional Treasury "
    "ECU-governor lane for decoupled recovery criterion, ECU-side lever ceilings, and bounded ordinary-to-stressed "
    "intervention governance | open | leave Treasury lane unopened indefinitely, retain narrow P_e trigger-only "
    "framing, broaden Treasury scope into Jubilee or long-horizon macro redesign | bounded Treasury ECU-governor "
    "lane with decoupled recovery criterion and explicit ECU-side lever ceilings (proposed) | Phase 450 lane-identity "
    "freeze, Phase 451 objective-function and observables contract, Phase 452 L1/L2 prerequisite disposition, "
    "docs/specs/ilc_cdl_050_constitutional_treasury_ecu_governor_opening_stub_457_v0.1.md |"
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


def _resolve_phase_457_commit_ref() -> str:
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
        if PHASE_457_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError("phase_457_rerun_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_457_rerun_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}:{result.stderr.strip()}")
    return result.stdout


def _decision_log_text_for_opening_assertions() -> str:
    try:
        commit_ref = _resolve_phase_457_commit_ref()
    except AssertionError as exc:
        if str(exc) != "phase_457_rerun_commit_not_present_in_local_history":
            raise
        return _read(DECISION_LOG_PATH)
    return _decision_log_text_at_ref(commit_ref)


def test_opening_stub_exists_and_contains_required_headings() -> None:
    assert OPENING_STUB_PATH.exists()
    text = _read(OPENING_STUB_PATH)
    for heading in (
        "## 1. Opening declaration",
        "## 2. Scope of CDL-050",
        "## 3. Rerun authorization basis",
        "## 4. Non-goals preserved from Phase 450",
        "## 5. Prelock target",
        "## 6. Ratification evidence program",
    ):
        assert heading in text


def test_opening_stub_contains_required_tokens() -> None:
    text = _read(OPENING_STUB_PATH)
    for token in (
        "CDL-050 is opened in Phase 457 following the clean Phase 456 Fix 14 rerun pass.",
        "CDL-050 governs the Treasury ECU-governor lane.",
        "CDL-050 does not govern Jubilee, long-horizon hardness-rotation, or node-rent lifecycle.",
        "The opening is authorized by phase_456_fix_14_overall_verdict=pass.",
        "Prelock hardening occurs in Phase 458.",
        "Ratification occurs in Phase 459 if and only if the prelock phase remains clean.",
        "This Phase 457 opening is additive only and does not itself prelock or ratify CDL-050.",
    ):
        assert token in text


def test_decision_log_contains_exact_cdl_050_opening_row() -> None:
    text = _decision_log_text_for_opening_assertions()
    rows = parse_decision_register_rows(text)
    assert EXPECTED_CDL_050_ROW in text
    assert rows["CDL-050"]["status"] == "open"


def test_cdl_050_row_is_inserted_between_cdl_049_and_cdl_051() -> None:
    lines = _decision_log_text_for_opening_assertions().splitlines()
    cdl_049_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-049 "))
    cdl_050_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-050 "))
    cdl_051_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-051 "))
    assert cdl_050_index == cdl_049_index + 1
    assert cdl_051_index == cdl_050_index + 1


def test_cdl_051_remains_ratified_and_unchanged() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-051"]["status"] == "ratified"
    assert rows["CDL-050"]["status"] == "open"


def test_no_forbidden_treasury_mutation_token_in_deliverables() -> None:
    for path in (OPENING_STUB_PATH, TEST_PATH):
        assert FORBIDDEN_TREASURY_TOKEN not in _read(path)

    assert WALKTHROUGH_PATH.exists()
    assert STATUS_PATH.exists()


def test_phase_457_rerun_commit_touches_exact_required_paths_and_no_runtime() -> None:
    commit_ref = _resolve_phase_457_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith("simulations/") for path in changed_paths)
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_457_rerun_commit_additive_only_non_target_shield() -> None:
    commit_ref = _resolve_phase_457_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-050"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_457"
