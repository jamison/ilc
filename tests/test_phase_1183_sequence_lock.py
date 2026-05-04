from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1183_1190_sequence_lock_v0.1.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_sequence_lock_exists() -> None:
    assert SEQUENCE_LOCK.exists()


def test_sequence_lock_token() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1183_1190_sequence_lock_committed" in content


def test_sequence_lock_preserves_sensitive_gates() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "GO Phase 1185" in content
    assert "v0_2_signing_ceremony_authorized_phase_1186" in content
    assert "GO Phase 1190" in content


def test_planning_index_points_to_active_window_and_lock() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1183-1190 in progress through Phase 1183" in content
    assert "ilc_window_1183_1190_candidate_phase_grouping_v0.1.md" in content
    assert "ilc_phase_1183_1190_sequence_lock_v0.1.md" in content
