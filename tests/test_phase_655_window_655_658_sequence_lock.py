from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


SEQ_LOCK_PATH = Path("docs/specs/ilc_phase_655_658_sequence_lock_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_655_window_655_658_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_655_g8_window_655_658_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_655_SUBJECT_TOKEN = "phase 655 window 655-658 sequence lock"
PHASE_655_BACKFILL_SUBJECT_TOKEN = "phase 655 walkthrough and status backfill"
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
    "## 2. Bug-class map and target surfaces",
    "## 3. Inherited boundary state",
    "## 4. Per-phase scope constraints",
    "## 5. Deterministic signing/export rules",
    "## 6. Routing and exclusions",
)
REQUIRED_TOKENS = (
    "window_655_658_sequence_lock_primary_gate",
    "window_655_658_signing_export_reproducibility_lane_locked",
    "window_655_658_non_constitutional_maintenance_lane",
    "signed_payload_timestamps_must_be_explicit_or_deterministic",
    "diagnostic_timestamps_must_not_pollute_signed_identity",
    "backup_filename_uniqueness_must_not_change_signed_payload_identity",
    "coupling_invariants_lock_remains_next_constitutional_target_after_655",
    "no_decision_log_or_adr_scope_in_window_655_658",
    "no_cdl_062_or_option_b_selection_in_655_658",
)
REQUIRED_SECTION_ONE_SNIPPETS = (
    "Window 655-658 is a bounded post-654 maintenance lane for signing/export",
    "Window 655-658 is not a constitutional lane",
    "No decision-log opening, ADR opening, `CDL-062` opening, or `Option B`",
)
REQUIRED_SECTION_TWO_SNIPPETS = (
    "implicit local wall clock inside signed manifests",
    "implicit local wall clock inside detached registry signature sidecars",
    "`ilc_core/ledger/canon_export_bundle_sign.py`",
    "`ilc_core/ledger/canon_bundle_key_registry.py`",
)
REQUIRED_SECTION_THREE_SNIPPETS = (
    "Rows 1-4 are `runtime_closed`.",
    "Rows 5-9 remain open.",
    "`Option D` remains active.",
    "This window is maintenance only.",
)
REQUIRED_SECTION_FIVE_SNIPPETS = (
    "signed payload timestamps must be explicit caller inputs or deterministic",
    "diagnostic timestamps may remain local only when they are excluded from signed",
    "sorted-key, compact-separator, `allow_nan=False` JSON",
    "No phase in this window may silently rely on `datetime.now(...)`, `time.time()`",
)
REQUIRED_SECTION_SIX_SNIPPETS = (
    "the coupling-invariants governance lock still remains the next constitutional",
    "`Option D` remains active",
    "no `CDL-062` opening is authorized",
    "no `Option B` selection is authorized",
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


def test_section_two_maps_bug_class_and_target_surfaces() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_TWO_SNIPPETS:
        assert item in text


def test_section_three_preserves_post_654_boundary_state() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_THREE_SNIPPETS:
        assert item in text


def test_section_five_states_deterministic_signing_export_rules() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_FIVE_SNIPPETS:
        assert item in text


def test_section_six_preserves_routing_and_exclusions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_SIX_SNIPPETS:
        assert item in text


def test_phase_655_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_655_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_655_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_655_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_655_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_655_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
