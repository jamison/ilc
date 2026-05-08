from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/specs/ilc_window_1241_1248_handoff_1248_v0.1.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1248_handoff_records_window_closed_pass_without_public_rc_claim() -> None:
    text = _text(HANDOFF)
    assert "**Status:** CLOSED" in text
    assert "**Closure verdict:** PASS" in text
    assert "`window_1241_1248_closed_phase_1248`" in text
    assert "`window_1241_1248_closure_gate_verdict=pass`" in text
    assert "This is a window-coherence pass. It is not a public-RC claim" in text
    assert "Public RC itself remains\nblocked" in text


def test_phase_1248_handoff_maps_all_window_phases_and_required_topics() -> None:
    text = _text(HANDOFF)
    for token in (
        "roadmap_v1_1_controlling_public_rc_roadmap_phase_1242",
        "phase_1243_gap14_package_profile_contracts_complete",
        "phase_1244_import_boundary_lint_protocol_stubs_complete",
        "phase_1245_openclaw_nemoclaw_skill_preview_complete",
        "cdl_087_governance_review_complete_phase_1246",
        "phase_1247_atlas_g_graph_discipline_first_slice_complete",
    ):
        assert token in text
    assert "Gap 14 moved from declaration to executable enforcement | PASS, first slice only" in text
    assert "CDL-087 governance disposition packet present | PASS, ratification deferred" in text
    assert "ATLAS-G-001..003 status present | PASS" in text


def test_phase_1248_handoff_carries_forward_remaining_public_rc_blockers() -> None:
    text = _text(HANDOFF)
    for token in (
        "ilc_logic_import_boundary_migration_debt_recorded_phase_1244",
        "gap_14_adapter_extraction_and_package_ci_gate_should_continue_before_public_rc_claim",
        "cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence",
        "transport_principal_identity_required_before_public_p2p",
        "ilc_public_claimability_substrate_required_pre_public_launch",
        "atlas_g_006_public_rc_graph_reachability_gate_required",
        "tla_refinement_notes_pre_rc_window_1241_plus_candidate",
        "allowlist_export_procedure_window_1241_plus_candidate",
        "v0_2_signing_ceremony_deferred_pending_signing_authorization",
    ):
        assert token in text
    assert "window_1249_plus_sequence_lock_required_before_next_phase_assignment" in text


def test_phase_1248_roadmap_has_closure_addendum_and_no_public_p2p_claim() -> None:
    text = _text(ROADMAP)
    assert "## 9. Phase 1248 Closure Addendum" in text
    assert "window_1241_1248_closed_phase_1248" in text
    assert "Gap 14 first slice is complete, but package split/CI remains open" in text
    assert "No public ILC-owned P2P claim is introduced by this closure" in text
    assert "Final public RC still requires public claimability" in text


def test_phase_1248_status_and_planning_index_point_to_closed_window() -> None:
    status = _text(STATUS)
    planning = _text(PLANNING_INDEX)
    assert "## Phase 1248" in status
    assert "window_1241_1248_closed_phase_1248" in status
    assert "Window 1241-1248 CLOSED through Phase 1248" in planning
    assert "docs/specs/ilc_window_1241_1248_handoff_1248_v0.1.md" in planning
    assert "GO Phase 1248" in planning
