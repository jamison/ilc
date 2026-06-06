"""Phase 1523p sequence-lock checks.

PUBLIC_RC_EXCLUDE: phase_1523p_private_sequence_lock_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window opening assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1523p_gap_refresh_records_adr_0035_intake() -> None:
    refresh = _read("docs/specs/ilc_gap_refresh_1523p_pre_block3_v0.1.md")

    required = [
        "gap_refresh_1523p_pre_block3_committed",
        "adr_0035_homoiconic_type_definition_system_direction_accepted",
        "adr_0035_implementation_deferred_pending_cdl",
        "OBL-025 remains open",
        "ADR-0030 is accepted but does not list `content_type=\"type_definition\"`",
        "CDL-096 has no register row and remains unopened",
        "`ilc_core/types.py`",
    ]

    for token in required:
        assert token in refresh


def test_phase_1523p_sequence_lock_records_window_and_sensitive_gates() -> None:
    lock = _read("docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md")

    required_tokens = [
        "window_1523p_sequence_lock_committed",
        "gap_refresh_1523p_pre_block3_committed",
        "mempalace_rebuild_complete_phase_1523p",
        "window_1523p_1530p_opened",
        "obl_025_routed_to_window_1523p_phase_1523p",
        "public_path_blocked_private_continuation_in_force_phase_1523p",
    ]
    for token in required_tokens:
        assert token in lock

    for phase in ["1523p", "1524p", "1525p", "1526p", "1527p", "1528p", "1529p", "1530p"]:
        assert f"| {phase} |" in lock

    assert (
        "requires exact `GO Phase 1526p`" in lock
        or "| 1526p | Type-system CDL opening | SENSITIVE | COMPLETE |" in lock
    )
    assert "requires exact `GO Phase 1528p`" in lock
    assert "requires exact `GO Phase 1530p`" in lock
    assert "must not consume CDL-096" in lock


def test_phase_1523p_obl_025_remains_open_and_routed_to_window() -> None:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    assert "| OBL-025 |" in register
    assert "ADR-0035 homoiconic type definition CDL" in register
    assert "open" in register
    assert "Window 1523p-1530p Block 3 ADR-0035 homoiconic type-system lane" in register
    assert "obl_025_routed_to_window_1523p_phase_1523p" in register
    assert (
        "Does not open or ratify type-system CDL" in register
        or "Does not ratify type-system CDL" in register
    )


def test_phase_1523p_does_not_mutate_adr_or_cdl_authority() -> None:
    adr = _read("docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md")
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")

    assert "**Status:** Accepted — direction accepted; implementation deferred to CDL phase" in adr
    assert "adr_0035_implementation_deferred_pending_cdl" in adr
    assert "| CDL-096 |" not in cdl
    if "| CDL-097 |" in cdl:
        assert "cdl_097_type_definition_node_authority_opened_phase_1526p" in cdl
        assert "ratification_token: cdl_097_ratified_phase_1528p" not in cdl
    else:
        assert "type-definition node authority for ADR-0035" not in cdl


def test_phase_1523p_frontier_updates_are_present() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")

    assert "docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md" in planning_index
    assert "Phase 1523p - Window 1523p-1530p Sequence Lock" in status
    assert "gap_refresh_1523p_pre_block3_committed" in status
    assert "window: 1523p-1530p" in agents
    assert "phase_1523p: complete_sequence_lock_gap_refresh_mempalace" in agents
