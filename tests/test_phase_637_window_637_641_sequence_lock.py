from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path("docs/specs/ilc_phase_637_641_sequence_lock_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_637_window_637_641_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_637_g8_window_637_641_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_637_SUBJECT_TOKEN = "phase 637 window 637-641 sequence lock"
PHASE_637_BACKFILL_SUBJECT_TOKEN = "phase 637 walkthrough and status backfill"
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
    "## 2. Residual target surface and hard pass conditions",
    "## 3. AG-gate design basis",
    "## 4. CDL-064 consumption boundary",
    "## 5. Inherited boundary state",
    "## 6. Per-phase scope constraints",
    "## 7. Window-level routing and exclusions",
)
REQUIRED_TOKENS = (
    "window_637_641_sequence_lock_primary_gate",
    "window_637_641_targets_residual_r2_r3_surfaces_only",
    "cdl_064_consumed_not_reopened_in_window_637_641",
    "types_py_and_protocol_mapper_named_as_primary_r2_targets",
    "window_623_plus_priority_preserved_in_window_637_641",
    "window_637_641_does_not_reopen_constitutional_vehicle",
    "window_637_641_does_not_select_option_b",
    "cdl_062_remains_not_authorized_in_window_637_641",
    "wallet_boundary_576_581_unchanged_in_window_637_641",
    "ecu_ilc_separation_preserved_in_window_637_641",
    "residual_numeric_hardening_gate_required_in_phase_641",
)
REQUIRED_SECTION_ONE_SNIPPETS = (
    "Human direction 2026-04-13: residual `R2/R3` float leakage is treated as a",
    "Window 631-636 closed the Tier-0 blocker and produced a clean exact-numeric",
    "`CDL-064` is already ratified, so this lane consumes an existing",
    "Window 623+ remains the broader runtime/interface continuation",
)
REQUIRED_TARGET_PATHS = (
    "`ilc_core/types.py`",
    "`ilc_core/protocol/mapper.py`",
    "`ilc_core/protocol/event_log.py`",
    "`ilc_core/ledger/settlement_metrics.py`",
    "`ilc_core/ledger/ecu_active_layer_runtime.py`",
    "`ilc_core/ledger/canon_export_validate.py`",
    "`ilc_core/ledger/canon_export_bundle_validate.py`",
    "`ilc_core/ledger/canon_export_bundle.py`",
    "`ilc_core/ledger/canon_export_format.py`",
    "`ilc_core/ledger/canon_bundle_audit_artifact.py`",
)
REQUIRED_HARD_PASS_SNIPPETS = (
    "shared contract float leakage in `types.py` / `mapper.py` is closed",
    "runtime-adjacent numeric helpers no longer reintroduce float semantics",
    "canon-export companion validators and scalar contracts align with exact",
    "Phase 641 residual numeric hardening gate passes before closure",
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
REQUIRED_SECTION_FOUR_SNIPPETS = (
    "`CDL-064` is already ratified and is only being consumed in Window 637-641.",
    "No new CDL or ADR opening is authorized in this window.",
    "This lane is implementation and hardening only.",
)
REQUIRED_SECTION_SEVEN_SNIPPETS = (
    "No decision-log mutation.",
    "No ADR mutation.",
    "No new constitutional vehicle opening.",
    "No `CDL-062` opening; `cdl_062_remains_not_authorized_in_window_637_641`.",
    "No `Option B` selection claim; `window_637_641_does_not_select_option_b`.",
    "No wallet-write widening or ILC transferability.",
    "Window 623+ remains the broader runtime/interface continuation:",
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


def test_section_one_states_residual_cleanup_basis_and_cdl_064_consumption_posture() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_ONE_SNIPPETS:
        assert item in text


def test_section_two_defines_full_residual_target_surface_and_all_hard_pass_conditions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_TARGET_PATHS:
        assert item in text
    for item in REQUIRED_HARD_PASS_SNIPPETS:
        assert item in text


def test_section_three_contains_ag_gate_table_all_rows_and_no_fail() -> None:
    text = _read(SEQ_LOCK_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    ag_rows = [line for line in text.splitlines() if line.startswith("| AG-")]
    assert ag_rows
    assert not any("| FAIL |" in line or " FAIL " in line for line in ag_rows)


def test_section_four_states_cdl_064_is_consumed_not_reopened() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_FOUR_SNIPPETS:
        assert item in text


def test_section_seven_preserves_window_623_plus_priority_and_bounded_residual_lane() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_SEVEN_SNIPPETS:
        assert item in text


def test_phase_637_main_commit_touches_expected_paths_only_and_no_prohibited_paths() -> None:
    _require_commit_or_skip(PHASE_637_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_637_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_637_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_637_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_637_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
