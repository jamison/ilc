from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1200_1208_sequence_lock_v0.1.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH = Path("docs/phases/phase_1200_window_sequence_lock_walkthrough.md")


def test_sequence_lock_exists() -> None:
    assert SEQUENCE_LOCK.exists()


def test_sequence_lock_token() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1200_1208_sequence_lock_committed" in content


def test_sequence_lock_records_current_frontier() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "window_1191_1199_closed_phase_1199" in content
    assert "cdl_086_public_launch_packaging_blocker_opened_phase_1194" in content
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in content
    assert "persistent_rate_limiter_scope_committed_phase_1196" in content


def test_sequence_lock_preserves_sensitive_gates() -> None:
    content = SEQUENCE_LOCK.read_text(encoding="utf-8")
    assert "GO Phase 1204" in content
    assert "v0_2_signing_ceremony_authorized_phase_1205" in content
    assert "GO Phase 1205" in content
    assert "GO Phase 1208" in content


def test_planning_index_points_to_active_window_and_lock() -> None:
    content = PLANNING_INDEX.read_text(encoding="utf-8")
    assert (
        "Window 1200-1208 is IN PROGRESS through Phase 1200" in content
        or "Window 1200-1208 is IN PROGRESS through Phase 1203" in content
    )
    assert "ilc_window_1200_1208_candidate_phase_grouping_v0.1.md" in content
    assert "ilc_phase_1200_1208_sequence_lock_v0.1.md" in content


def test_walkthrough_marked_complete() -> None:
    content = WALKTHROUGH.read_text(encoding="utf-8")
    assert "**Status:** complete" in content
    assert "window_1200_1208_sequence_lock_committed" in content
