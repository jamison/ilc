"""Phase 1505p sequence-lock checks.

PUBLIC_RC_EXCLUDE: phase_1505p_private_sequence_lock_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window opening assertion. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1505p_sequence_lock_records_required_tokens() -> None:
    lock = _read("docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md")

    required_tokens = [
        "window_1505p_sequence_lock_committed",
        "mempalace_rebuild_complete_phase_1505p",
        "window_1505p_1514p_opened",
        "public_path_blocked_private_continuation_in_force_phase_1505p",
        "no_cdl_mutation_phase_1505p",
        "no_adr_status_mutation_phase_1505p",
        "no_runtime_activation_phase_1505p",
    ]

    for token in required_tokens:
        assert token in lock


def test_phase_1505p_locks_window_order_and_sensitive_closure_gate() -> None:
    lock = _read("docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md")

    expected_phase_rows = [
        "| 1 | 1505p | Window sequence lock and MemPalace rebuild",
        "| 2 | 1506p | Werner topology data capture schema",
        "| 3 | 1507p | Werner multi-node capture run",
        "| 4 | 1508p | Werner SIM-FETCH re-run",
        "| 5 | 1509p | CDL-096 eligibility checkpoint only",
        "| 6 | 1510p | Spec-only OBL batch",
        "| 7 | 1511p | SIM batch",
        "| 8 | 1512p | Genesis governance node frameworks",
        "| 9 | 1513p | Window coherence",
        "| 10 | 1514p | Window closure gate and handoff",
    ]
    for row in expected_phase_rows:
        assert row in lock

    assert "Phase 1514p requires exact human authorization: `GO Phase 1514p`" in lock
    assert "This lock does not authorize Phase 1514p" in lock


def test_phase_1505p_preserves_non_authorization_floor() -> None:
    lock = _read("docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md")

    forbidden_authorities = [
        "public repository publication",
        "public package publication",
        "public RC claim",
        "public source export",
        "epoch 0-to-1 transition",
        "CDL opening or mutation",
        "ADR status mutation",
        "opening CDL-096",
        "Werner flow-governor runtime activation",
        "clearing `DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED`",
    ]

    for authority in forbidden_authorities:
        assert authority in lock


def test_phase_1505p_obligation_routing_matches_register_state() -> None:
    lock = _read("docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md")
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    for obligation in ["OBL-004", "OBL-026", "OBL-035", "OBL-036", "OBL-037", "OBL-038"]:
        assert f"| {obligation} |" in register
        assert f"| {obligation} | open" in lock or f"| {obligation} | open |" in lock

    for token in [
        "obl_013_closed_phase_1502p",
        "obl_031_closed_phase_1499p",
        "obl_032_closed_phase_1500p",
        "obl_033_closed_phase_1501p",
        "obl_034_closed_phase_1502p",
    ]:
        assert token in register


def test_phase_1505p_frontier_updates_are_present() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")

    assert "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md" in planning_index
    assert "Window 1505p-1514p is OPEN" in planning_index
    assert "Phase 1505p - Window 1505p-1514p Sequence Lock" in status
    assert "window_1505p_sequence_lock_committed" in status
    assert "window: 1505p-1514p" in agents
    assert "phase_1505p: complete_window_sequence_lock_mempalace" in agents
