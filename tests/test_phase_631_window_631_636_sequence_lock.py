from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path("docs/specs/ilc_phase_631_636_sequence_lock_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_631_window_631_636_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_631_g8_window_631_636_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_631_SUBJECT_TOKEN = "phase 631 window 631-636 sequence lock"
PHASE_631_BACKFILL_SUBJECT_TOKEN = "phase 631 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Window identity and authorization basis",
    "## 2. Tier-0 target surface and hard pass conditions",
    "## 3. AG-gate design basis",
    "## 4. CDL-064 vehicle declaration",
    "## 5. Inherited boundary state",
    "## 6. Per-phase scope constraints",
    "## 7. Window-level exclusions and routing",
)
REQUIRED_TOKENS = (
    "window_631_636_sequence_lock_primary_gate",
    "cdl_064_named_as_vehicle_for_exact_numeric_representation",
    "window_631_636_targets_tier0_runtime_surfaces_only",
    "window_631_636_reprioritization_requires_human_lock",
    "float_retention_not_acceptable_tier0_window_631_636",
    "window_631_636_does_not_select_option_b",
    "cdl_062_remains_not_authorized_in_window_631_636",
    "wallet_boundary_576_581_unchanged_in_window_631_636",
    "ecu_ilc_separation_preserved_in_window_631_636",
    "window_623_plus_priority_recorded_but_bracketed_by_numeric_strike_force",
    "cdl_064_stub_required_in_phase_632",
    "numeric_hardening_gate_required_in_phase_636",
)
REQUIRED_AUTHORIZATION_SNIPPETS = (
    "Human direction 2026-04-13: Tier-0 float-based economic runtime is treated as",
    "Window 624-630 proved bounded internal economic agency but left broader",
    "Existing canon still records Window 623+ as the highest-priority continuation",
    "Human activation is required to reprioritize this corrective lane",
)
REQUIRED_HARD_PASS_SNIPPETS = (
    "`CDL-064` is opened as a stub row in Phase 632 and ratified in Phase 634.",
    "A complete Tier-0 numeric inventory exists and classifies all target",
    "A ratified exact-numeric contract exists for Tier-0 economic runtime.",
    "Tier-0 runtime migration lands in Phase 635.",
    "Phase 636 hardening gate passes before closure.",
)
AG_GATE_ROWS = (
    "| AG-1 Co-flourishing mission |",
    "| AG-2 W_e increase |",
    "| AG-3 Epistemic integrity |",
    "| AG-4 ECU-ILC separation |",
    "| AG-5 Harness-agnostic |",
    "| AG-6 Near-infinite scale |",
    "| AG-7 Machine-legible first |",
    "| AG-8 Outbound economic loop |",
)
REQUIRED_VEHICLE_SNIPPETS = (
    "`CDL-064` title: *Canonical Economic Numeric Representation and Exact",
    "option A: retain float with rounding and tolerance,",
    "option B: exact decimal runtime contract,",
    "option C: fixed-point minor-unit contract.",
    "This vehicle does not open sovereign substrate selection, `CDL-062`, wallet",
)
REQUIRED_ROUTING_SNIPPETS = (
    "No decision-log mutation except the `CDL-064` row in Phase 632 and Phase 634.",
    "No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_631_636`.",
    "No `Option B` selection claim; `window_631_636_does_not_select_option_b`.",
    "No ILC transferability or wallet-write widening.",
    "Existing canon still records Window 623+ as the highest-priority continuation.",
    "If activated by human lock, Window 631-636 should run before or immediately",
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


def _find_commit_ref(*, subject_token: str) -> str | None:
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
        if subject_token in subject.lower():
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_sequence_lock_exists_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_contains_all_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_one_states_authorization_basis_and_corrective_reprioritization() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_AUTHORIZATION_SNIPPETS:
        assert item in text


def test_section_two_defines_tier0_surface_and_all_hard_pass_conditions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for required_path in (
        "`ilc_core/ledger/`",
        "`ilc_core/rc/economic_cycle_runtime.py`",
        "`ilc_core/validator/staking_liveness_runtime.py`",
        "`ilc_core/types.py`",
    ):
        assert required_path in text
    for item in REQUIRED_HARD_PASS_SNIPPETS:
        assert item in text


def test_section_three_contains_ag_gate_table_all_rows_and_no_fail() -> None:
    text = _read(SEQ_LOCK_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    ag_rows = [line for line in text.splitlines() if line.startswith("| AG-")]
    assert ag_rows
    assert not any("| FAIL |" in line or " FAIL " in line for line in ag_rows)


def test_section_four_names_cdl_064_and_defers_representation_choice() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_VEHICLE_SNIPPETS:
        assert item in text


def test_section_seven_records_window_623_plus_priority_and_corrective_routing() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_ROUTING_SNIPPETS:
        assert item in text


def test_phase_631_main_commit_touches_expected_paths_only_and_no_prohibited_paths() -> None:
    _require_commit_or_skip(PHASE_631_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_631_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_631_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_631_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_631_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
