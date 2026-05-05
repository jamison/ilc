from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1209_1217_sequence_lock_v0.1.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH = Path("docs/phases/phase_1209_window_sequence_lock_walkthrough.md")


def test_sequence_lock_file_exists() -> None:
    assert SEQUENCE_LOCK.exists()


def test_sequence_lock_contains_window_token() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1209_1217_sequence_lock_committed" in content


def test_sequence_lock_references_baseline_commit() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "7d545106" in content
    assert "window_1200_1208_closed_phase_1208" in content


def test_sequence_lock_records_guidance_commits() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "40f4cadc" in content
    assert "b69a1e0b" in content
    assert "755d7243" in content
    assert "d9eb7cf1" in content


def test_sequence_lock_records_reciprocal_fetch_boundary() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in content
    assert "reciprocal_fetch_admission_model_required" in content


def test_planning_index_points_to_active_window_and_lock() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1209-1217 is IN PROGRESS through Phase 1209" in content
    assert "ilc_window_1209_1217_candidate_phase_grouping_v0.1.md" in content
    assert "ilc_phase_1209_1217_sequence_lock_v0.1.md" in content
    assert "Window 1200-1208 sequence lock** (closed reference)" in content


def test_walkthrough_marked_complete() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "window_1209_1217_sequence_lock_committed" in content
