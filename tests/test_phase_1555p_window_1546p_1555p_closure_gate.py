"""Phase 1555p Window 1546p-1555p closure-gate checks.

PUBLIC_RC_EXCLUDE: phase_1555p_private_closure_gate_test
PUBLIC_RC_EXCLUDE_REASON: Internal private closure-gate test for Block 5 planning artifacts; not part of public RC exports.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


GATE_ENV_VAR = "ILC_PHASE_1555P_GATE_SELFTEST"

if os.environ.get(GATE_ENV_VAR) == "1":
    pytest.skip("selftest guard: skipping gate when running as part of full regression", allow_module_level=True)


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _obl_row(obligation_id: str) -> str:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")
    prefix = f"| {obligation_id} |"
    for line in register.splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f"{obligation_id} row not found")


def _cdl_row(cdl_id: str) -> str:
    register = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    prefix = f"| {cdl_id} |"
    for line in register.splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f"{cdl_id} row not found")


def test_phase_1555p_handoff_contains_required_closure_tokens() -> None:
    handoff = _read("docs/specs/ilc_window_1546p_1555p_handoff_1555p_v0.1.md")
    for token in [
        "window_1546p_closed_phase_1555p",
        "window_1546p_closure_gate_committed_phase_1555p",
        "window_1546p_closure_gate_verdict=pass",
        "obl_023_closure_confirmed_phase_1555p",
        "obl_024_closure_confirmed_phase_1555p",
        "obl_028_closure_confirmed_phase_1555p",
        "obl_029_closure_confirmed_phase_1555p",
        "cdl_096_ratified_phase_1553p",
        "block_5_all_obligations_closed_phase_1555p",
        "block6_private_rehearsal_required_next_phase_1555p",
        "public_path_remains_blocked_phase_1555p",
        "go_window_1556p_block6_required_next",
    ]:
        assert token in handoff


def test_closure_gate_confirms_obls_without_reclosing_rows() -> None:
    handoff = _read("docs/specs/ilc_window_1546p_1555p_handoff_1555p_v0.1.md")
    for obligation_id, owning_token, confirmation_token in [
        ("OBL-023", "obl_023_closed_phase_1547p", "obl_023_closure_confirmed_phase_1555p"),
        ("OBL-024", "obl_024_closed_phase_1548p", "obl_024_closure_confirmed_phase_1555p"),
        ("OBL-028", "obl_028_closed_phase_1549p", "obl_028_closure_confirmed_phase_1555p"),
        ("OBL-029", "obl_029_closed_phase_1550p", "obl_029_closure_confirmed_phase_1555p"),
    ]:
        row = _obl_row(obligation_id)
        assert "| closed |" in row
        assert owning_token in row
        assert confirmation_token in handoff

    for forbidden_token in [
        "obl_023_closed_phase_1555p",
        "obl_024_closed_phase_1555p",
        "obl_028_closed_phase_1555p",
        "obl_029_closed_phase_1555p",
    ]:
        assert forbidden_token not in handoff


def test_cdl096_is_ratified_with_runtime_and_public_path_still_blocked() -> None:
    row = _cdl_row("CDL-096")
    assert "| ratified |" in row
    assert "cdl_096_ratified_phase_1553p" in row
    assert "cdl_096_scope_ratified_phase_1553p" in row
    assert "werner_value_path_status: not_ecu_not_ilc_not_claimability" in row
    assert "werner_flow_governor_runtime_status: not_authorized" in row
    assert "global_tier_activation_status: not_authorized" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "public_path_status: blocked" in row


@pytest.mark.parametrize(
    ("relative_path", "guard_assignment"),
    [
        ("ilc_core/epoch/epoch_emission_production_path.py", "PRODUCTION_EMISSION_NOT_ACTIVATED = True"),
        ("ilc_core/validator/validator_admission_ejection_production_path.py", "VALIDATOR_ADMISSION_NOT_ACTIVATED = True"),
        ("ilc_core/epoch/treasury_validator_reward_production_path.py", "TREASURY_DISTRIBUTION_NOT_ACTIVATED = True"),
        (
            "ilc_core/epoch/ejected_stake_distribution_production_path.py",
            "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED = True",
        ),
        ("ilc_core/economics/productive_ecu_expansion_bounty_runtime.py", "PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED = True"),
        ("ilc_core/bundle/type_registry.py", "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True"),
        ("ilc_core/network/rust_p2p_bridge.py", "RUST_P2P_BRIDGE_NOT_ACTIVATED: Final[bool] = True"),
        ("ilc_core/epistemic/jury_finality_evaluator.py", "JURY_FINALITY_EVALUATOR_NOT_PRODUCTION: Final[bool] = True"),
    ],
)
def test_runtime_and_public_path_guards_remain_set(relative_path: str, guard_assignment: str) -> None:
    source = _read(relative_path)
    assert guard_assignment in source


def test_sequence_lock_records_window_closed_pass_and_block6_next() -> None:
    sequence_lock = _read("docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md")
    assert "**Status:** CLOSED PASS - Phase 1555p closure gate committed" in sequence_lock
    assert "| 1555p | Window closure gate | SENSITIVE | COMPLETE |" in sequence_lock
    assert "window_1546p_closed_phase_1555p" in sequence_lock
    assert "block_5_all_obligations_closed_phase_1555p" in sequence_lock
    assert "go_window_1556p_block6_required_next" in sequence_lock


def test_planning_index_marks_phase_1555p_as_only_current_frontier() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    assert planning_index.count("⬅ CURRENT") == 1
    assert "Phase 1555p Window 1546p-1555p closure gate" in planning_index
    assert "window_1546p_closed_phase_1555p" in planning_index
    assert "go_window_1556p_block6_required_next" in planning_index


def test_agents_records_closed_window_and_next_block6_gate() -> None:
    agents = _read("AGENTS.md")
    assert "phase_1555p: complete_sensitive_window_closure_gate" in agents
    assert "window_1546p_1555p: CLOSED_PASS" in agents
    assert "block_5_governance_edge_specs: complete_closed_phase_1555p" in agents
    assert "next_phase: go_window_1556p_block6_required_next" in agents
    assert "public_path: blocked_public_path_remains_blocked_phase_1555p" in agents


def test_status_records_phase_1555p_closure() -> None:
    status = _read("docs/phases/STATUS.md")
    assert "## Phase 1555p - Window 1546p-1555p Closure Gate" in status
    assert "window_1546p_closed_phase_1555p" in status
    assert "block_5_all_obligations_closed_phase_1555p" in status
    assert "go_window_1556p_block6_required_next" in status


def test_closure_gate_selftest_guard_is_declared() -> None:
    source = _read("tests/test_phase_1555p_window_1546p_1555p_closure_gate.py")
    assert 'GATE_ENV_VAR = "ILC_PHASE_1555P_GATE_SELFTEST"' in source
    assert "pytest.skip(" in source
    assert "allow_module_level=True" in source
