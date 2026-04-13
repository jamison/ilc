from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SEQ_LOCK_PATH = Path("docs/specs/ilc_phase_642_648_sequence_lock_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_642_window_642_648_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_642_g8_window_642_648_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_642_SUBJECT_TOKEN = "phase 642 window 642-648 sequence lock"
PHASE_642_BACKFILL_SUBJECT_TOKEN = "phase 642 walkthrough and status backfill"
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
    "## 2. Primary live target surface",
    "## 3. Remaining-float inventory basis",
    "## 4. Second-order security guardrails",
    "## 5. Inherited boundary state",
    "## 6. Per-phase scope constraints",
    "## 7. Routing and exclusions",
)
REQUIRED_TOKENS = (
    "window_642_648_sequence_lock_primary_gate",
    "window_642_648_is_non_constitutional_security_strike_force",
    "remaining_float_inventory_and_todo_required_in_phase_643",
    "canonical_json_guard_requires_sort_keys_and_compact_separators",
    "non_finite_json_and_decimal_rejection_required_in_touched_boundaries",
    "no_predictable_prng_in_touched_runtime_security_paths",
    "assert_replacement_must_not_introduce_broad_exception_swallowing",
    "bounded_stream_fix_must_not_shift_attack_to_temp_disk_exhaustion",
    "wallet_boundary_576_581_unchanged_in_window_642_648",
    "option_d_posture_active_after_642",
    "window_623_plus_priority_preserved_after_642_648",
)
REQUIRED_SECTION_ONE_SNIPPETS = (
    "Human direction 2026-04-14: remaining float carry-forward and live bounded",
    "Window 637-641 closed bounded residual numeric leakage and produced a clean",
    "Window 642-648 is therefore locked as a non-constitutional strike-force lane",
    "No new CDL or ADR opening is authorized here.",
)
REQUIRED_TARGET_PATHS = (
    "`ilc_core/ledger/canon_bundle_replay_report.py`",
    "`ilc_core/ledger/canon_export_bundle_sign.py`",
    "`ilc_core/network/peer.py`",
    "`ilc_core/epistemic/aesthetic_panel_runtime.py`",
    "`ilc_core/economics/passive_ecu_attribution_runtime.py`",
    "`ilc_core/protocol/ndjson_bundle.py`",
    "`ilc_core/cli/ep_task_cli.py`",
)
REQUIRED_SECTION_FOUR_SNIPPETS = (
    "Canonical JSON on touched machine-verifiable paths requires both sorted keys",
    "Non-finite numeric constants must be rejected at touched JSON/Decimal",
    "No predictable PRNG may remain in touched runtime/security paths",
    "Assert removal must not be replaced by broad exception swallowing",
    "Stream bounding must not simply move the attack from RAM to temp-disk",
)
REQUIRED_SECTION_SEVEN_SNIPPETS = (
    "Window 623+ remains the broader runtime/interface continuation after this",
    "no decision-log mutation",
    "no ADR mutation",
    "no `CDL-062` opening",
    "no `Option B` selection claim",
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


def test_section_one_states_non_constitutional_authorization_basis() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_ONE_SNIPPETS:
        assert item in text


def test_section_two_names_primary_live_target_surface() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_TARGET_PATHS:
        assert item in text


def test_section_three_requires_remaining_float_inventory_and_todo_carry_forward() -> None:
    text = _read(SEQ_LOCK_PATH)
    assert "runtime-critical exact-numeric work already closed" in text
    assert "runtime-adjacent or public-contract float surfaces still open" in text
    assert "lower-tier sim / analysis / devnet float surfaces still deferred" in text


def test_section_four_captures_second_order_guardrails() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_FOUR_SNIPPETS:
        assert item in text


def test_section_seven_preserves_window_623_plus_routing_and_option_d_posture() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_SEVEN_SNIPPETS:
        assert item in text


def test_ag_gate_table_present_with_no_fail_rows() -> None:
    text = _read(SEQ_LOCK_PATH)
    for row in AG_GATE_ROWS:
        assert row in text
    ag_rows = [line for line in text.splitlines() if line.startswith("| AG-")]
    assert ag_rows
    assert not any("| FAIL |" in line or " FAIL " in line for line in ag_rows)


def test_phase_642_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_642_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_642_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_642_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_642_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_642_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
