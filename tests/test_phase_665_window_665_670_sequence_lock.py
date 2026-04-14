from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_665_670_sequence_lock_v0.1.md")
RECOVERY_PATH = Path("docs/specs/ilc_transport_open_questions_and_historical_recovery_665_v0.1.md")
TEST_PATH = Path("tests/test_phase_665_window_665_670_sequence_lock.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_665_g8_window_665_670_sequence_lock_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_665_SUBJECT_TOKENS = ("phase 665", "window 665-670 sequence lock")
PHASE_665_BACKFILL_SUBJECT_TOKENS = ("phase 665", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQUENCE_LOCK_PATH),
    str(RECOVERY_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_SEQUENCE_HEADINGS = (
    "## 1. Window identity and row-9 target",
    "## 2. Inherited canon and non-goals",
    "## 3. Closure tier versus stretch tier",
    "## 4. Live-infra and VPN discipline",
    "## 5. OpenClaw overlay-harness boundary",
    "## 6. What this window may and may not close",
)
REQUIRED_SEQUENCE_TOKENS = (
    "row_9_lane_locked_to_operational_maturity_not_dynamic_discovery",
    "row_9_target_bounded_public_participant_maturity",
    "closure_tier_vs_stretch_tier_threshold_split",
    "vpn_firewall_posture_must_be_verified_first",
    "openclaw_overlay_harness_not_transport_base_layer",
    "participant_lateness_cost_is_participant_side_not_network_rescue_duty",
    "dynamic_peer_discovery_deferred_beyond_665_670",
)
REQUIRED_RECOVERY_HEADINGS = (
    "## 1. Purpose and authority order",
    "## 2. Questions already settled by canon",
    "## 3. Questions directionally settled but not operationalized",
    "## 4. Questions that require sim or live drills",
    "## 5. Questions that require human decision",
    "## 6. Immediate easy wins for later lanes",
)
REQUIRED_RECOVERY_TOKENS = (
    "row_9_open_questions_classified_by_authority_not_by_memory",
    "static_peer_registry_v1_remains_row_9_baseline",
    "github_bootstrap_and_explicit_promotion_preserved",
    "vpn_port_matrix_needed_before_live_claims",
    "openclaw_sidecar_investigation_allowed_not_required",
    "transport_evidence_infrastructure_should_be_reusable_beyond_row_9",
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


def test_sequence_lock_artifact_exists_and_contains_all_required_headings() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for heading in REQUIRED_SEQUENCE_HEADINGS:
        assert heading in text


def test_sequence_lock_artifact_contains_all_required_tokens() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in REQUIRED_SEQUENCE_TOKENS:
        assert token in text


def test_recovery_artifact_exists_and_contains_all_required_headings() -> None:
    text = _read(RECOVERY_PATH)
    for heading in REQUIRED_RECOVERY_HEADINGS:
        assert heading in text


def test_recovery_artifact_contains_all_required_tokens() -> None:
    text = _read(RECOVERY_PATH)
    for token in REQUIRED_RECOVERY_TOKENS:
        assert token in text


def test_sequence_lock_preserves_static_peer_registry_v1_and_defers_dynamic_discovery() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "static peer registry v1 remains the active discovery posture" in text
    assert "dynamic peer discovery" in text
    assert "does not authorize:" in text


def test_sequence_lock_explicitly_records_closure_tier_versus_stretch_tier() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    assert "Closure-tier evidence means:" in text
    assert "Stretch-tier evidence means:" in text


def test_recovery_artifact_classifies_questions_across_all_four_authority_open_states() -> None:
    text = _read(RECOVERY_PATH)
    assert "already settled by canon" in text
    assert "directionally settled but not yet operationalized" in text
    assert "require sim or live drills" in text
    assert "require human decision" in text


def test_recovery_artifact_records_vpn_posture_question_and_openclaw_overlay_boundary() -> None:
    text = _read(RECOVERY_PATH)
    assert "their firewall/port posture is an early gating question" in text
    assert "OpenClaw remains an overlay harness" in text


def test_decision_log_and_ilc_core_remain_unchanged() -> None:
    _require_commit_or_skip(PHASE_665_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_665_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_665_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_665_SUBJECT_TOKENS)
    main_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_665_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS

    if _find_commit_ref(subject_tokens=PHASE_665_BACKFILL_SUBJECT_TOKENS) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_665_BACKFILL_SUBJECT_TOKENS}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_665_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(backfill_commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
