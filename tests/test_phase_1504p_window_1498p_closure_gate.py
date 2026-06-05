"""Phase 1504p closure-gate self-test.

PUBLIC_RC_EXCLUDE: phase_1504p_private_closure_gate_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window closure assertion. Not a public RC artifact.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _phase_1504p_enabled() -> bool:
    return os.environ.get("ILC_PHASE_1504P_GATE_SELFTEST") == "1"


def test_phase_1504p_selftest_requires_explicit_environment_gate() -> None:
    assert _phase_1504p_enabled(), (
        "phase_1504p_selftest_requires_ILC_PHASE_1504P_GATE_SELFTEST_1"
    )


def test_handoff_records_window_closure_and_public_path_block() -> None:
    if not _phase_1504p_enabled():
        return

    handoff = _read("docs/specs/ilc_window_1498p_1504p_handoff_1504p_v0.1.md")

    required_tokens = [
        "window_1498p_closure_gate_committed_phase_1504p",
        "window_1498p_closed_phase_1504p",
        "window_1498p_closure_gate_verdict=pass",
        "window_1498p_closure_verdict_cdl031_track_completed_public_path_still_blocked",
        "public_path_remains_blocked_phase_1504p",
        "public_rc_not_published_phase_1504p",
        "epoch_transition_not_triggered_phase_1504p",
        "cdl_019_amendment_ratified_phase_1501p",
        "window_1505p_not_open_phase_1504p",
        "go_window_1505p_required_next",
    ]

    for token in required_tokens:
        assert token in handoff


def test_closure_preserves_runtime_and_distribution_guards() -> None:
    if not _phase_1504p_enabled():
        return

    handoff = _read("docs/specs/ilc_window_1498p_1504p_handoff_1504p_v0.1.md")
    runtime = _read("ilc_core/economics/dynamic_ranking_multiplier_runtime.py")
    issuance_gate = _read("ilc_core/epoch/issuance_economics_integration_gate.py")
    rust_bridge = _read("ilc_core/network/rust_p2p_bridge.py")
    jury = _read("ilc_core/epistemic/jury_finality_evaluator.py")
    local_store = _read("ilc_core/harness/local_immutable_store.py")

    assert "DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED: bool = True" in runtime
    assert "cdl_031_runtime_deferred_to_governance_weight_lane_phase_1344" in issuance_gate
    assert "RUST_P2P_BRIDGE_NOT_ACTIVATED: Final[bool] = True" in rust_bridge
    assert "CDL_094_ADMISSION_WIRE_NOT_ACTIVATED: Final[bool] = True" in rust_bridge
    assert "JURY_FINALITY_EVALUATOR_NOT_PRODUCTION: Final[bool] = True" in jury
    assert "LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION = True" in local_store

    non_authorized_terms = [
        "public repository publication",
        "public RC claim",
        "public source export",
        "production minting",
        "CDL-096 opening",
        "dynamic-ranking activation",
        "issuance-gate mutation",
        "removing `CDL_031_RUNTIME_DEFERRED_TOKEN`",
    ]
    for term in non_authorized_terms:
        assert term in handoff


def test_planning_frontier_points_to_closed_window_and_requires_next_go() -> None:
    if not _phase_1504p_enabled():
        return

    planning_index = _read("docs/PLANNING_INDEX.md")
    status = _read("docs/phases/STATUS.md")
    agents = _read("AGENTS.md")
    sequence_lock = _read("docs/specs/ilc_phase_1498p_1504p_sequence_lock_v0.1.md")

    assert "docs/specs/ilc_window_1498p_1504p_handoff_1504p_v0.1.md" in planning_index
    assert "Window 1498p-1504p CLOSED" in planning_index
    assert "GO Window 1505p" in planning_index
    assert "Phase 1504p - Window 1498p-1504p Closure Gate" in status
    assert "window_1498p_closed_phase_1504p" in status
    assert "window: 1498p-1504p" in agents
    assert "window_1498p_1504p: CLOSED" in agents
    assert "go_window_1505p_required_next" in agents
    assert "**Status:** CLOSED - Phase 1504p closure gate complete" in sequence_lock
