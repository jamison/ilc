"""Phase 1515p sequence-lock checks.

PUBLIC_RC_EXCLUDE: phase_1515p_private_sequence_lock_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window opening assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1515p_gap_refresh_records_required_verdicts() -> None:
    refresh = _read("docs/specs/ilc_gap_refresh_1515p_pre_block2_v0.1.md")

    required = [
        "gap_refresh_1515p_pre_block2_committed",
        "| Total ADR files | 43 |",
        "| Proposed ADR files | 9 |",
        "| Proposed ADRs with no OBL routing or documented non-RC reason | 0 |",
        "| Active CDL rows currently open | 1 (`CDL-021`) |",
        "| CDL-096 status | Eligible to open, no row exists, unopened |",
        "| Stale OBL register rows patched | 10 (`OBL-020` through `OBL-029`) |",
        "`docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md`",
    ]

    for token in required:
        assert token in refresh


def test_phase_1515p_gap_refresh_classifies_runtime_obligations() -> None:
    refresh = _read("docs/specs/ilc_gap_refresh_1515p_pre_block2_v0.1.md")

    expected_classifications = {
        "OBL-020": "`activation_missing`",
        "OBL-021": "`activation_missing`",
        "OBL-022": "`partial_integration_missing`",
        "OBL-024": "`implemented_guarded`",
        "OBL-026": "`partial_integration_missing`",
    }

    for obligation, classification in expected_classifications.items():
        assert obligation in refresh
        assert classification in refresh


def test_phase_1515p_obl_register_patch_routes_all_ten_rows() -> None:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    expected_routes = {
        "OBL-020": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-021": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-022": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-023": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
        "OBL-024": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
        "OBL-025": "Block 3 ADR-0035 homoiconic type-system lane, phase/window TBD by later sequence lock",
        "OBL-026": "Block 2 Window 1515p-1522p (this window)",
        "OBL-027": "Block 4 Economic Finality, phase/window TBD by later sequence lock",
        "OBL-028": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
        "OBL-029": "Block 5 Governance/economic edge specs, phase/window TBD by later sequence lock",
    }

    for obligation, route in expected_routes.items():
        assert f"| {obligation} |" in register
        assert route in register

    for classification in ["activation_missing", "partial_integration_missing", "implemented_guarded"]:
        assert classification in register


def test_phase_1515p_sequence_lock_records_window_and_sensitive_gates() -> None:
    lock = _read("docs/specs/ilc_phase_1515p_1522p_sequence_lock_v0.1.md")

    required_tokens = [
        "window_1515p_sequence_lock_committed",
        "mempalace_rebuild_complete_phase_1515p",
        "gap_refresh_1515p_pre_block2_committed",
        "obl_register_stale_routing_patched_phase_1515p",
        "window_1515p_1522p_opened",
        "public_path_blocked_private_continuation_in_force_phase_1515p",
    ]
    for token in required_tokens:
        assert token in lock

    for phase in ["1515p", "1516p", "1517p", "1518p", "1519p", "1520p", "1521p", "1522p"]:
        assert f"| {phase} |" in lock

    assert "exact `GO Phase 1520p`" in lock
    assert "exact `GO Phase 1522p`" in lock
    assert "must not execute source export" in lock


def test_phase_1515p_frontier_updates_are_present() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")

    assert "docs/specs/ilc_phase_1515p_1522p_sequence_lock_v0.1.md" in planning_index
    assert "Window 1515p-1522p is OPEN" in planning_index
    assert "Phase 1515p - Window 1515p-1522p Sequence Lock" in status
    assert "gap_refresh_1515p_pre_block2_committed" in status
    assert "window: 1515p-1522p" in agents
    assert "phase_1515p: complete_gap_refresh_sequence_lock_mempalace_obl_patch" in agents


def test_phase_1515p_guidance_uses_actual_adr_0009_path() -> None:
    checked_paths = [
        "docs/specs/ilc_window_1515p_1522p_candidate_phase_grouping_v0.1.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1516p_g9_adr_0009_layer0_layer1_encoding_integration.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1517p_g9_adr_0009_layer2_layer3_encoding_integration.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1519p_g9_adr_0009_source_export_rehearsal_integration.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1520p_g9_adr_0009_promotion_sensitive.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1521p_g9_window_1515p_coherence_capsule.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1522p_g9_window_1515p_closure_gate.md",
    ]

    for relative_path in checked_paths:
        text = _read(relative_path)
        assert "ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md" in text
        assert "ADR_0009_Protocol_Native_Bundle_Distribution.md" not in text
