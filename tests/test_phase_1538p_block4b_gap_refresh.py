"""Phase 1538p Block 4B window-opening checks.

PUBLIC_RC_EXCLUDE: phase_1538p_private_gap_refresh_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window opening assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1538p_sequence_lock_records_window_and_guard_floor() -> None:
    lock = _read("docs/specs/ilc_phase_1538p_1545p_sequence_lock_v0.1.md")

    required = [
        "window_1538p_1545p_opened",
        "window_1531p_1537p_closed_pass_inherits_to_window_1538p",
        "window_1538p_sequence_lock_committed_phase_1538p",
        "gap_refresh_1538p_pre_block4b_committed",
        "mempalace_rebuild_complete_phase_1538p",
        "obl_021_routed_to_window_1538p_phase_1538p",
        "obl_022_routed_to_window_1538p_phase_1538p",
        "obl_027_routed_to_window_1538p_phase_1538p",
        "public_path_blocked_private_continuation_in_force_phase_1538p",
        "requires exact `GO Phase 1545p`",
    ]

    for token in required:
        assert token in lock

    for phase in ["1538p", "1539p", "1540p", "1541p", "1542p", "1543p", "1544p", "1545p"]:
        assert f"| {phase} |" in lock

    assert "no authority for public repository publication" in lock
    assert "All Block 4B runtime work must remain default-off" in lock


def test_phase_1538p_gap_refresh_classifies_block4b_surfaces() -> None:
    refresh = _read("docs/specs/ilc_gap_refresh_1538p_pre_block4b_v0.1.md")

    required = [
        "gap_refresh_1538p_pre_block4b_committed",
        "ilc_core/validator/admission_ejection_runtime.py",
        "ilc_core/epoch/treasury_governance_runtime.py",
        "ilc_core/epoch/validator_reward_pool_routing_runtime.py",
        "ilc_core/economics/epoch_attribution_settle_runtime.py",
        "ilc_core/epoch/issuance_economics_integration_gate.py",
        "`activation_missing`",
        "`implemented_guarded`",
        "production_validator_admission_activation_not_implemented_phase_1353",
        "production_treasury_activation_not_implemented_phase_1348",
        "production_ejected_stake_distribution_activation_not_implemented_phase_1350",
        "build_issuance_economics_integration_gate_report()",
    ]

    for token in required:
        assert token in refresh


def test_phase_1538p_stale_1486p_reconciliation_is_evidence_based() -> None:
    refresh = _read("docs/specs/ilc_gap_refresh_1538p_pre_block4b_v0.1.md")

    required = [
        "stale_1486p_gap_analysis_reconciled_phase_1538p",
        "cdl_030_cdl_068_adr_0008_confirmed_activation_boundary_not_implementation_gap",
        "ilc_core/epoch/ecu_price_clamp_runtime.py",
        "cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1",
        "ilc_core/validator/topology_shuffle_runtime.py",
        "cdl_068_topology_shuffle_vrf_runtime_phase_1354.v0.1",
        "ilc_core/protocol/governance_weighted_decision.py",
        "cdl_013_governance_weight_live_integration_phase_1356.v0.1",
        "governance_weight_vote_share_precision_gap_closed_phase_1357",
    ]

    for token in required:
        assert token in refresh

    assert "activation-boundary findings, not missing-implementation gaps" in refresh


def test_phase_1538p_frontier_updates_are_present() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    assert "docs/specs/ilc_phase_1538p_1545p_sequence_lock_v0.1.md" in planning_index
    assert "Phase 1538p - Block 4B Sequence Lock and Gap Refresh" in status
    assert "gap_refresh_1538p_pre_block4b_committed" in status
    assert "window: 1538p-1545p" in agents
    assert "phase_1538p: complete_sequence_lock_gap_refresh_mempalace" in agents
    assert "Window 1538p-1545p Block 4 Window B" in register
    assert "obl_021_routed_to_window_1538p_phase_1538p" in register
    assert "obl_022_routed_to_window_1538p_phase_1538p" in register
    assert "obl_027_routed_to_window_1538p_phase_1538p" in register
