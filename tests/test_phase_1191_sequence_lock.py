from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1191_1199_sequence_lock_v0.1.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH = Path("docs/phases/phase_1191_window_sequence_lock_walkthrough.md")


def test_sequence_lock_exists() -> None:
    assert SEQUENCE_LOCK.exists()


def test_sequence_lock_token() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1191_1199_sequence_lock_committed" in content


def test_sequence_lock_preserves_sensitive_gates() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "v0_2_signing_ceremony_authorized_phase_1193" in content
    assert "GO Phase 1193" in content
    assert "GO Phase 1194" in content
    assert "ILC_CDL_MUTATION_PHASE=1194" in content
    assert "GO Phase 1199" in content


def test_sequence_lock_records_current_frontier() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content
    assert "sim_spectral_05_three_slice_observer_framework_complete" in content
    assert "cdl_085_ratified_phase_1185" in content
    assert "CDL-086" in content


def test_planning_index_points_to_active_window_and_lock() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Window 1191-1199 in progress through Phase 1191" in content
    assert "ilc_window_1191_1199_candidate_phase_grouping_v0.1.md" in content
    assert "ilc_phase_1191_1199_sequence_lock_v0.1.md" in content


def test_walkthrough_marked_complete() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "window_1191_1199_sequence_lock_committed" in content
