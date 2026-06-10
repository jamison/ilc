from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1546p_sequence_lock_tokens_and_public_boundary() -> None:
    text = read("docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md")

    required = [
        "window_1546p_1555p_opened",
        "window_1538p_1545p_closed_pass_inherits_to_window_1546p",
        "window_1546p_sequence_lock_committed_phase_1546p",
        "gap_refresh_1546p_pre_block5_committed",
        "mempalace_rebuild_complete_phase_1546p",
        "cdl_096_scope_reconciliation_recorded_phase_1546p",
        "obl_023_routed_to_window_1546p_phase_1546p",
        "obl_024_routed_to_window_1546p_phase_1546p",
        "obl_028_routed_to_window_1546p_phase_1546p",
        "obl_029_routed_to_window_1546p_phase_1546p",
        "block6_required_after_window_1546p_phase_1546p",
        "public_rc_gate_not_reached_phase_1546p",
    ]
    for token in required:
        assert token in text

    assert "This window is not the public RC gate" in text
    assert "cdl_096_scope_selection_option_a_phase_1551p" in text
    assert "| 1551p | CDL-096 opening after human scope selection | SENSITIVE | COMPLETE - Option A |" in text
    assert "| 1552p | CDL-096 deliberation and prelock | NON-SENSITIVE | COMPLETE |" in text
    assert "Phase 1553p is the next phase and is SENSITIVE" in text


def test_phase_1546p_gap_refresh_records_cdl096_three_options() -> None:
    text = read("docs/specs/ilc_gap_refresh_1546p_pre_block5_v0.1.md")

    assert "| A | Combined Werner plus global-tier jury finality |" in text
    assert "| B | Werner-only |" in text
    assert "| C | Global-tier-only |" in text
    assert "No option is selected in Phase 1546p" in text
    assert "Guidance-only false positive" in text


def test_obligation_register_records_block5_routes_without_phase_1546p_closure() -> None:
    text = read("docs/specs/ilc_open_obligation_register_v0.1.md")

    assert "**Status:** ACTIVE - WINDOW 1546P OPEN" in text
    assert "docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md" in text

    for obl, phase in {
        "OBL-023": "Phase 1547p",
        "OBL-024": "Phase 1548p",
        "OBL-028": "Phase 1549p",
        "OBL-029": "Phase 1550p",
    }.items():
        row = next(line for line in text.splitlines() if line.startswith(f"| {obl} |"))
        assert f"Window 1546p-1555p {phase}" in row
        assert "closed_phase_1546p" not in row


def test_frontier_docs_point_to_window_1546p() -> None:
    planning = read("docs/PLANNING_INDEX.md")
    status = read("docs/phases/STATUS.md")
    agents = read("AGENTS.md")

    assert "Phase 1546p Block 5 sequence lock and gap refresh" in planning
    assert "Phase 1552p CDL-096 deliberation and prelock" in planning
    assert "Phase 1551p CDL-096 opening with Option A" in planning
    assert "Phase 1550p OBL-029 peer-funded bounty spec" in planning
    assert "Window 1546p-1555p is OPEN" in planning
    assert "## Phase 1552p - CDL-096 Deliberation and Prelock" in status
    assert "## Phase 1551p - CDL-096 Opening With Option A" in status
    assert "## Phase 1546p - Block 5 Sequence Lock and Gap Refresh" in status
    assert "window: 1546p-1555p" in agents
    assert "next_phase: phase_1553p_sensitive_cdl096_ratification" in agents
