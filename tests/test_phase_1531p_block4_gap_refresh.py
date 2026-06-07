"""Phase 1531p Block 4 window-opening checks.

PUBLIC_RC_EXCLUDE: phase_1531p_private_gap_refresh_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window opening assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1531p_sequence_lock_records_window_and_guard_floor() -> None:
    lock = _read("docs/specs/ilc_phase_1531p_1537p_sequence_lock_v0.1.md")

    required = [
        "window_1531p_sequence_lock_committed",
        "gap_refresh_1531p_pre_block4_committed",
        "mempalace_rebuild_complete_phase_1531p",
        "window_1531p_1537p_opened",
        "obl_020_routed_to_window_1531p_phase_1531p",
        "public_path_blocked_private_continuation_in_force_phase_1531p",
        "`PRODUCTION_EMISSION_NOT_ACTIVATED = True` must remain set",
    ]

    for token in required:
        assert token in lock

    for phase in ["1531p", "1532p", "1533p", "1534p", "1535p", "1536p", "1537p"]:
        assert f"| {phase} |" in lock

    assert "requires exact `GO Phase 1537p`" in lock
    assert "no CDL opening or mutation scope" in lock


def test_phase_1531p_gap_refresh_classifies_relevant_runtime_surfaces() -> None:
    refresh = _read("docs/specs/ilc_gap_refresh_1531p_pre_block4_v0.1.md")

    required = [
        "gap_refresh_1531p_pre_block4_committed",
        "ilc_core/epoch/epoch_emission_runtime.py",
        "ilc_core/epoch/fee_burn_split_runtime.py",
        "ilc_core/epoch/allocation_distributor_runtime.py",
        "ilc_core/epoch/issuance_economics_integration_gate.py",
        "ilc_core/protocol/commit_epoch_emission_runtime.py",
        "`activation_missing`",
        "`implemented_guarded`",
        "production_minting_activation_not_implemented_phase_1345",
        "production_fee_burn_activation_not_implemented_phase_1346",
        "production_allocation_distribution_activation_not_implemented_phase_1347",
        "Phase 1532p must build on top of this gate, not duplicate it",
    ]

    for token in required:
        assert token in refresh


def test_phase_1531p_obl_register_routes_obl_020_only_to_window_a() -> None:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    assert "| OBL-020 |" in register
    assert "Window 1531p-1537p Block 4 Window A" in register
    assert "obl_020_routed_to_window_1531p_phase_1531p" in register
    assert "| OBL-021 |" in register
    assert "| OBL-022 |" in register
    assert "| OBL-027 |" in register
    assert "Block 4 Window B, phase/window TBD by later sequence lock" in register


def test_phase_1531p_frontier_updates_are_present() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")

    assert "docs/specs/ilc_phase_1531p_1537p_sequence_lock_v0.1.md" in planning_index
    assert "Phase 1531p - Block 4 Sequence Lock and Runtime Surface Audit" in status
    assert "gap_refresh_1531p_pre_block4_committed" in status
    assert "window: 1531p-1537p" in agents
    assert "phase_1531p: complete_sequence_lock_gap_refresh_mempalace" in agents
