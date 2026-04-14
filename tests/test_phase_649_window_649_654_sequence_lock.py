from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


SEQ_LOCK_PATH = Path("docs/specs/ilc_phase_649_654_sequence_lock_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_649_window_649_654_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_649_g8_window_649_654_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_649_SUBJECT_TOKEN = "phase 649 window 649-654 sequence lock"
PHASE_649_BACKFILL_SUBJECT_TOKEN = "phase 649 walkthrough and status backfill"
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
    "## 2. Touchpoint map and checklist target",
    "## 3. Inherited boundary state",
    "## 4. Runtime-wide numeric and security guardrails",
    "## 5. Per-phase scope constraints",
    "## 6. Routing and exclusions",
)
REQUIRED_TOKENS = (
    "window_649_654_sequence_lock_primary_gate",
    "window_649_654_is_concrete_window_623_plus_runtime_lane",
    "rows_1_through_4_target_runtime_closed_after_649_654",
    "rows_5_through_9_not_closed_by_649_654",
    "wallet_boundary_576_581_unchanged_in_window_649_654",
    "claimability_state_remains_deferred_in_649_654",
    "exact_numeric_and_non_finite_guard_applies_to_new_runtime_surfaces",
    "canonical_json_compact_and_allow_nan_false_required_for_machine_surfaces",
    "option_d_posture_active_after_649",
    "no_cdl_062_opening_in_649_654",
    "window_649_654_preserves_post_648_runtime_priority",
)
REQUIRED_SECTION_ONE_SNIPPETS = (
    "Window 649-654 is the concrete execution form of the long-carried `Window 623+`",
    "Window 613-619 closed rows 1-4 in spec form only and left them at",
    "Window 642-648 preserved Window 623+ as the broader runtime/interface priority",
    "No new CDL or ADR opening is authorized here.",
)
REQUIRED_SECTION_TWO_SNIPPETS = (
    "Phase 650: public init/admission runtime",
    "Phase 651: public receipt issuance and query runtime",
    "Phase 652: visible ECU runtime plus delayed visible ILC settlement runtime",
    "Phase 653: public wallet runtime integration",
    "rows 1-4 are the target checklist rows for runtime closure",
    "rows 5-9 remain later-lane items after this window",
)
REQUIRED_SECTION_THREE_SNIPPETS = (
    "Phase 576 and Phase 581 read-only wallet boundary",
    "Phase 587-589 public identity, receipt, and settlement-linked legitimacy",
    "Phase 609 ECU / ILC / bounded-runtime separation",
    "Phase 612 two-form MVP gate rule",
    "ADR-0028 `Option D` active posture",
)
REQUIRED_SECTION_FOUR_SNIPPETS = (
    "use the exact-numeric rule",
    "reject non-finite numeric ingress",
    "sorted keys",
    "compact separators",
    "`allow_nan=False`",
    "fail closed with machine tokens",
)
REQUIRED_SECTION_SIX_SNIPPETS = (
    "`Option D` remains active",
    "no wallet widening is authorized",
    "no ILC transferability is authorized",
    "no `CDL-062` opening is authorized",
    "Window 649-654 does not by itself authorize broader public RC claims",
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


def test_section_one_states_concrete_623_plus_authorization_basis() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_ONE_SNIPPETS:
        assert item in text


def test_section_two_maps_touchpoints_and_rows_1_through_4_target_correctly() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_TWO_SNIPPETS:
        assert item in text


def test_section_three_preserves_inherited_boundaries() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_THREE_SNIPPETS:
        assert item in text


def test_section_four_captures_runtime_wide_numeric_and_security_guardrails() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_FOUR_SNIPPETS:
        assert item in text


def test_section_six_preserves_option_d_and_exclusions() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_SECTION_SIX_SNIPPETS:
        assert item in text


def test_phase_649_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_649_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_649_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_649_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_649_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_649_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
