from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    diff_row_fields,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_050_constitutional_consensus_and_treasury_ecu_governor_prelock_hardening_458_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_458_cdl_050_prelock_hardening.py")
PHASE_458_SUBJECT_TOKEN = "phase 458 cdl-050 prelock hardening and adversarial review"
FORBIDDEN_TREASURY_TOKEN = "ILC_CDL_MUTATION_" + "AUTHORIZED"
EXACT_REQUIRED_MAIN_PATHS = {
    str(DECISION_LOG_PATH),
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
EXPECTED_PRELOCK_ROW = (
    "| CDL-050 | Phase-450 / Phase-451 / Phase-452 / Phase-456-Fix-14 | constitutional Treasury "
    "ECU-governor lane for decoupled recovery criterion, ECU-side lever ceilings, and bounded ordinary-to-stressed "
    "intervention governance | prelock | leave Treasury lane unopened indefinitely, retain narrow P_e trigger-only "
    "framing, broaden Treasury scope into Jubilee or long-horizon macro redesign | bounded Treasury ECU-governor "
    "lane with decoupled recovery criterion and explicit ECU-side lever ceilings (proposed) | Phase 450 lane-identity "
    "freeze, Phase 451 objective-function and observables contract, Phase 452 L1/L2 prerequisite disposition, "
    "docs/specs/ilc_cdl_050_constitutional_treasury_ecu_governor_opening_stub_457_v0.1.md |"
)
EXPECTED_OPEN_ROW = EXPECTED_PRELOCK_ROW.replace("| prelock |", "| open |", 1)
REQUIRED_HEADINGS = (
    "## 1. Hardened constitutional language",
    "## 2. Selected recovery criterion",
    "## 3. Risk ceilings (all ECU-side levers)",
    "## 4. Categorical prohibitions",
    "## 5. Adversarial review findings",
    "## 6. Scope-creep check",
    "## 7. Prelock authorization",
)
REQUIRED_TOKENS = (
    "CDL-050 prelock hardening is complete as of Phase 458.",
    "CDL-050 prelock remains authorized by phase_456_fix_14_overall_verdict=pass.",
    "The controlling Blocker-1 evidence basis remains the oscillator-cleared rerun chain.",
    "All ECU-side levers have explicit ceilings.",
    "No uncapped lever remains.",
    "Categorical prohibitions are explicit.",
    "Worst-case intervention cost is bounded from simulation evidence.",
    "No Jubilee or long-horizon hardness-rotation language was introduced in Phase 458.",
    "Ratification proceeds in Phase 459 if and only if this prelock artifact remains clean.",
    "CDL-050's operating envelope covers ordinary-to-stressed ECU-side operational scenarios.",
    "Catastrophic cross-layer scenarios are governed by CDL-V6, not by CDL-050 normal operation.",
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


def _resolve_phase_458_commit_ref() -> str:
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
        if PHASE_458_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref

    if matching:
        raise AssertionError("phase_458_commit_subject_present_but_no_qualifying_prelock_commit")
    raise AssertionError("phase_458_commit_not_present_in_local_history")


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


def test_prelock_artifact_exists_and_contains_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_prelock_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_decision_log_contains_exact_required_prelock_row() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    assert EXPECTED_PRELOCK_ROW in text
    assert rows["CDL-050"]["status"] == "prelock"


def test_cdl_050_has_no_premature_ratification_metadata_and_candidate_is_unchanged() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-050"]["status"] == "prelock"
    assert rows["CDL-050"]["current_candidate"] == (
        "bounded Treasury ECU-governor lane with decoupled recovery criterion and explicit ECU-side lever ceilings (proposed)"
    )
    assert "ratified_phase" not in rows["CDL-050"]
    assert "ratified_date" not in rows["CDL-050"]
    assert "evidence_document" not in rows["CDL-050"]


def test_cdl_051_remains_ratified() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-051"]["status"] == "ratified"


def test_no_forbidden_token_in_artifact_or_test_and_cdl_v6_boundary_is_explicit() -> None:
    assert FORBIDDEN_TREASURY_TOKEN not in _read(ARTIFACT_PATH)
    assert FORBIDDEN_TREASURY_TOKEN not in _read(TEST_PATH)
    assert "Catastrophic cross-layer scenarios are governed by CDL-V6, not by CDL-050 normal operation." in _read(
        ARTIFACT_PATH
    )


def test_phase_458_commit_touches_exact_required_paths_and_no_runtime() -> None:
    commit_ref = _resolve_phase_458_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith("simulations/") for path in changed_paths)
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_458_commit_mutates_only_cdl_050_status_and_no_non_target_rows() -> None:
    commit_ref = _resolve_phase_458_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    assert set(old_rows.keys()) == set(new_rows.keys())
    assert EXPECTED_OPEN_ROW in _decision_log_text_at_ref(f"{commit_ref}^1")
    assert EXPECTED_PRELOCK_ROW in _decision_log_text_at_ref(commit_ref)
    assert diff_row_fields(old_rows["CDL-050"], new_rows["CDL-050"]) == {"status"}
    assert old_rows["CDL-050"]["status"] == "open"
    assert new_rows["CDL-050"]["status"] == "prelock"
    for cdl_id in old_rows:
        if cdl_id == "CDL-050":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_458"
