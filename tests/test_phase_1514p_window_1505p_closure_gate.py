"""Phase 1514p closure-gate self-test.

PUBLIC_RC_EXCLUDE: phase_1514p_private_closure_gate_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window closure assertion. Not a public RC artifact.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _phase_1514p_enabled() -> bool:
    return os.environ.get("ILC_PHASE_1514P_GATE_SELFTEST") == "1"


def test_phase_1514p_selftest_requires_explicit_environment_gate() -> None:
    assert _phase_1514p_enabled(), (
        "phase_1514p_selftest_requires_ILC_PHASE_1514P_GATE_SELFTEST_1"
    )


def test_handoff_records_window_closure_and_non_opened_next_window() -> None:
    if not _phase_1514p_enabled():
        return

    handoff = _read("docs/specs/ilc_window_1505p_1514p_handoff_1514p_v0.1.md")

    required_tokens = [
        "window_1505p_closed_phase_1514p",
        "window_1505p_closure_gate_committed_phase_1514p",
        "window_1505p_closure_gate_verdict=pass",
        "public_path_remains_blocked_phase_1514p",
        "public_rc_not_published_phase_1514p",
        "epoch_transition_not_triggered_phase_1514p",
        "cdl_096_eligible_not_opened_window_1505p_closure",
        "window_1515p_not_open_phase_1514p",
        "go_window_1515p_required_next",
    ]

    for token in required_tokens:
        assert token in handoff

    assert "Block 1 of the pre-public-RC no-deferral strike-force plan is complete" in handoff
    assert "Window 1515p is not opened by this handoff" in handoff


def test_obligation_register_records_closed_and_carried_forward_rows() -> None:
    if not _phase_1514p_enabled():
        return

    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    closed_rows = [
        "OBL-004",
        "OBL-008",
        "OBL-011",
        "OBL-012",
        "OBL-015",
        "OBL-016",
        "OBL-017",
        "OBL-018",
        "OBL-019",
        "OBL-035",
        "OBL-036",
        "OBL-037",
        "OBL-038",
    ]
    for obligation_id in closed_rows:
        row_prefix = f"| {obligation_id} |"
        assert row_prefix in register
        row = next(line for line in register.splitlines() if line.startswith(row_prefix))
        assert "| closed |" in row

    open_rows = [
        "OBL-020",
        "OBL-021",
        "OBL-022",
        "OBL-023",
        "OBL-024",
        "OBL-025",
        "OBL-026",
        "OBL-027",
        "OBL-028",
        "OBL-029",
        "OBL-030",
    ]
    for obligation_id in open_rows:
        row_prefix = f"| {obligation_id} |"
        assert row_prefix in register
        row = next(line for line in register.splitlines() if line.startswith(row_prefix))
        assert "| open |" in row

    assert "| OBL-002 |" in register
    assert "| permanent-invariant |" in register
    assert "obligation_register_sweep_complete_phase_1514p" in register
    assert "cdl_096_eligible_not_opened_window_1505p_closure" in register


def test_cdl_096_is_eligible_but_not_opened() -> None:
    if not _phase_1514p_enabled():
        return

    handoff = _read("docs/specs/ilc_window_1505p_1514p_handoff_1514p_v0.1.md")
    cdl_register = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    checkpoint = _read("docs/specs/ilc_cdl096_eligibility_checkpoint_1509p_v0.1.md")

    assert "cdl_096_eligible_to_open_phase_1509p" in checkpoint
    assert "werner_conditions_1_and_4_jointly_covered_phase_1509p" in checkpoint
    assert "cdl_096_eligible_not_opened_window_1505p_closure" in handoff
    assert "| CDL-096 |" not in cdl_register


def test_planning_frontier_points_to_closed_window_and_requires_next_go() -> None:
    if not _phase_1514p_enabled():
        return

    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")
    sequence_lock = _read("docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md")

    assert "docs/specs/ilc_window_1505p_1514p_handoff_1514p_v0.1.md" in planning_index
    assert "Window 1505p-1514p CLOSED" in planning_index
    assert "GO Window 1515p" in planning_index
    assert planning_index.count("⬅ CURRENT") == 1

    assert "Phase 1514p - Window 1505p-1514p Closure Gate" in status
    assert "window_1505p_closed_phase_1514p" in status
    assert "window: 1505p-1514p" in agents
    assert "window_1505p_1514p: CLOSED" in agents
    assert "go_window_1515p_required_next" in agents
    assert "**Status:** CLOSED - Phase 1514p closure gate complete" in sequence_lock


def test_non_authorization_floor_is_preserved() -> None:
    if not _phase_1514p_enabled():
        return

    handoff = _read("docs/specs/ilc_window_1505p_1514p_handoff_1514p_v0.1.md")
    walkthrough = _read(
        "docs/phases/phase_1514p_window_1505p_1514p_closure_gate_walkthrough.md"
    )

    non_authorized_terms = [
        "public repository publication",
        "public package publication",
        "public RC",
        "public source export",
        "epoch 0-to-1 transition",
        "wallet write",
        "treasury write",
        "ECU minting",
        "ILC settlement",
        "CDL opening",
        "CDL mutation",
        "ADR status mutation",
        "CDL-096 opening",
        "Werner flow-governor runtime activation",
        "clearing any NOT_ACTIVATED guard",
        "raw repository publication",
    ]
    for term in non_authorized_terms:
        assert term in handoff

    assert "graph_delta=load_bearing_artifact_added:docs/specs/ilc_window_1505p_1514p_handoff_1514p_v0.1.md" in walkthrough
