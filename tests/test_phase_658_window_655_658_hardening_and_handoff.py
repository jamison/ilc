from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


REPORT_PATH = Path("docs/specs/ilc_window_655_658_signing_export_hardening_report_658_v0.1.md")
GATE_SCRIPT_PATH = Path("tools/run_window_655_658_signing_export_gate_phase_658.sh")
TEST_PATH = Path("tests/test_phase_658_window_655_658_hardening_and_handoff.py")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v3.9.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_655_658_handoff_658_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_658_g8_window_655_658_hardening_and_handoff_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_658_SUBJECT_TOKENS = ("phase 658", "window 655-658 hardening and handoff")
PHASE_658_BACKFILL_SUBJECT_TOKENS = ("phase 658", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(REPORT_PATH),
    str(GATE_SCRIPT_PATH),
    str(TEST_PATH),
    str(CAPSULE_PATH),
    str(HANDOFF_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Signing/export reproducibility closure summary",
    "## 3. What this window fixed",
    "## 4. What this window did not claim",
    "## 5. Routing after closure",
    "## 6. MemPalace refresh disposition",
)
REQUIRED_HANDOFF_TOKENS = (
    "window_655_658_handoff_658_closed",
    "window_655_658_signing_export_lane_status_pass",
    "signed_manifest_and_registry_signature_reproducibility_closed_after_658",
    "helper_level_registry_channel_sync_reproducibility_closed_after_658",
    "coupling_invariants_lock_remains_next_constitutional_target_after_658",
    "option_d_posture_still_active_after_658",
    "no_option_b_or_cdl_062_selection_in_658",
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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
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
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
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
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_tokens}")


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f"commit_not_yet_present:{subject_tokens}")


def test_hardening_report_exists_and_records_lane_pass() -> None:
    text = _read(REPORT_PATH)
    assert "window_655_658_signing_export_lane_status_pass" in text
    assert "Window 655-658 passes on the basis of" in text


def test_handoff_exists_with_all_required_headings() -> None:
    text = _read(HANDOFF_PATH)
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text


def test_handoff_contains_all_required_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text


def test_handoff_states_what_the_lane_fixed() -> None:
    text = _read(HANDOFF_PATH)
    assert "signed canon-export manifest metadata no longer depends on implicit local wall" in text
    assert "detached registry signature sidecars no longer depend on implicit local wall" in text
    assert "sync bookkeeping remains clearly separated from channel signed identity" in text


def test_handoff_states_what_the_lane_did_not_claim() -> None:
    text = _read(HANDOFF_PATH)
    assert "did not claim" in text
    assert "closure of Phase 611 rows 5-9" in text
    assert "Option-B selection" in text
    assert "CDL-062" in text


def test_handoff_preserves_the_next_constitutional_target_correctly() -> None:
    text = _read(HANDOFF_PATH)
    assert "coupling-invariants governance lock remains the next constitutional" in text
    assert "Option D" in text


def test_capsule_v3_9_exists_and_records_bounded_maintenance_closure_honestly() -> None:
    text = _read(CAPSULE_PATH)
    assert "ILC Antigravity Context Capsule v3.9" in text
    assert "Window 655-658 is now closed as a bounded post-654 signing/export maintenance" in text
    assert "rows 1-4 of the Phase 611 Option-B graduation checklist remain" in text
    assert "rows 5-9 remain open" in text
    assert "coupling-invariants governance lock remains the next constitutional target" in text


def test_gate_script_exists_is_executable_and_wires_required_tests() -> None:
    script_text = _read(GATE_SCRIPT_PATH)
    assert GATE_SCRIPT_PATH.is_file()
    assert os.access(GATE_SCRIPT_PATH, os.X_OK)
    assert "tests/test_phase_656_canon_export_and_registry_signature_reproducibility.py" in script_text
    assert "tests/test_phase_657_registry_channel_promotion_sync_reproducibility.py" in script_text
    assert "tests/test_phase_658_window_655_658_hardening_and_handoff.py" in script_text
    assert "tests/test_canon_bundle_key_registry_channel_signing.py" in script_text
    assert "tests/test_canon_bundle_key_registry_sync.py" in script_text
    assert "tests/test_canon_bundle_key_registry_channel_rollback.py" in script_text
    assert "run_window_655_658_signing_export_gate_phase_658.sh" not in script_text


def test_decision_log_unchanged() -> None:
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_phase_658_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_658_SUBJECT_TOKENS)
    main_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_658_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS
    if _find_commit_ref(subject_tokens=PHASE_658_BACKFILL_SUBJECT_TOKENS) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_658_BACKFILL_SUBJECT_TOKENS}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_658_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(backfill_commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
