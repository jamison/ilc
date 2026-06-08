"""Phase 1545p Window 1538p-1545p closure-gate checks.

PUBLIC_RC_EXCLUDE: phase_1545p_private_closure_gate_test
PUBLIC_RC_EXCLUDE_REASON: Internal private closure-gate test for Block 4B planning artifacts; not part of public RC exports.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


GATE_ENV_VAR = "ILC_PHASE_1545P_GATE_SELFTEST"

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


def test_phase_1538p_window_opening_tokens_present() -> None:
    sequence_lock = _read("docs/specs/ilc_phase_1538p_1545p_sequence_lock_v0.1.md")
    assert "window_1538p_1545p_opened" in sequence_lock
    assert "window_1538p_sequence_lock_committed_phase_1538p" in sequence_lock
    assert "gap_refresh_1538p_pre_block4b_committed" in sequence_lock
    assert "mempalace_rebuild_complete_phase_1538p" in sequence_lock


def test_phase_1539p_validator_path_tokens_present() -> None:
    text = _read("docs/phases/phase_1539p_obl021_validator_admission_ejection_walkthrough.md")
    status = _read("docs/phases/STATUS.md")
    assert "obl_021_validator_integration_path_committed_phase_1539p" in text
    assert "VALIDATOR_ADMISSION_NOT_ACTIVATED=True" in text
    assert "public_path_still_blocked_phase_1539p" in status


def test_phase_1540p_treasury_validator_reward_tokens_present() -> None:
    text = _read("docs/phases/phase_1540p_obl022_treasury_validator_reward_walkthrough.md")
    status = _read("docs/phases/STATUS.md")
    assert "obl_022_treasury_validator_reward_path_committed_phase_1540p" in text
    assert "TREASURY_DISTRIBUTION_NOT_ACTIVATED=True" in text
    assert "public_path_still_blocked_phase_1540p" in status


def test_phase_1541p_ejected_stake_tokens_present() -> None:
    text = _read("docs/phases/phase_1541p_obl022_ejected_stake_walkthrough.md")
    status = _read("docs/phases/STATUS.md")
    assert "ejected_stake_distribution_production_path_committed_phase_1541p" in text
    assert "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED=True" in text
    assert "public_path_still_blocked_phase_1541p" in status


def test_phase_1542p_expansion_bounty_tokens_present() -> None:
    text = _read("docs/phases/phase_1542p_obl027_expansion_bounty_walkthrough.md")
    status = _read("docs/phases/STATUS.md")
    assert "productive_ecu_expansion_bounty_runtime_committed_phase_1542p" in text
    assert "PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED=True" in text
    assert "ADR-0016 Proposed retained" in text
    assert "public_path_still_blocked_phase_1542p" in status


def test_phase_1543p_round_trip_tokens_present() -> None:
    text = _read("docs/phases/phase_1543p_block4b_round_trip_walkthrough.md")
    status = _read("docs/phases/STATUS.md")
    assert "block4b_round_trip_committed_phase_1543p" in text
    assert "block4b_replay_invariant_confirmed_phase_1543p" in text
    assert "public_path_still_blocked_phase_1543p" in status


def test_phase_1544p_coherence_tokens_present() -> None:
    text = _read("docs/phases/phase_1544p_block4b_coherence_walkthrough.md")
    assert "block4b_coherence_complete_phase_1544p" in text
    assert "context_capsule_block4b_committed_phase_1544p" in text
    assert "public_path_still_blocked_phase_1544p" in text


def test_obl_020_remains_closed() -> None:
    row = _obl_row("OBL-020")
    assert "| closed |" in row
    assert "obl_020_closed_phase_1537p" in row
    assert "production_emission_not_activated_guard_retained_phase_1537p_fix1" in row


def test_obl_021_closed_by_phase_1545p() -> None:
    row = _obl_row("OBL-021")
    assert "| closed |" in row
    assert "obl_021_validator_integration_path_committed_phase_1539p" in row
    assert "obl_021_closed_phase_1545p" in row


def test_obl_022_closed_by_phase_1545p() -> None:
    row = _obl_row("OBL-022")
    assert "| closed |" in row
    assert "obl_022_treasury_validator_reward_path_committed_phase_1540p" in row
    assert "ejected_stake_distribution_production_path_committed_phase_1541p" in row
    assert "obl_022_closed_phase_1545p" in row


def test_obl_027_closed_by_phase_1545p() -> None:
    row = _obl_row("OBL-027")
    assert "| closed |" in row
    assert "productive_ecu_expansion_bounty_runtime_committed_phase_1542p" in row
    assert "obl_027_closed_phase_1545p" in row


def test_obl_023_remains_open_for_block_5() -> None:
    row = _obl_row("OBL-023")
    assert "| open |" in row
    assert "Block 5 Governance/economic edge specs" in row


def test_obl_024_remains_open_for_block_5() -> None:
    row = _obl_row("OBL-024")
    assert "| open |" in row
    assert "Block 5 Governance/economic edge specs" in row


def test_obl_028_remains_open_for_block_5() -> None:
    row = _obl_row("OBL-028")
    assert "| open |" in row
    assert "Block 5 Governance/economic edge specs" in row


def test_obl_029_remains_open_for_block_5() -> None:
    row = _obl_row("OBL-029")
    assert "| open |" in row
    assert "Block 5 Governance/economic edge specs" in row


@pytest.mark.parametrize(
    ("relative_path", "guard_name"),
    [
        ("ilc_core/epoch/epoch_emission_production_path.py", "PRODUCTION_EMISSION_NOT_ACTIVATED"),
        ("ilc_core/validator/validator_admission_ejection_production_path.py", "VALIDATOR_ADMISSION_NOT_ACTIVATED"),
        ("ilc_core/epoch/treasury_validator_reward_production_path.py", "TREASURY_DISTRIBUTION_NOT_ACTIVATED"),
        (
            "ilc_core/epoch/ejected_stake_distribution_production_path.py",
            "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED",
        ),
        ("ilc_core/economics/productive_ecu_expansion_bounty_runtime.py", "PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED"),
        ("ilc_core/bundle/type_registry.py", "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED"),
    ],
)
def test_default_off_guards_remain_true(relative_path: str, guard_name: str) -> None:
    source = _read(relative_path)
    assert f"{guard_name} = True" in source
    assert f"{guard_name} = False" not in source


def test_handoff_contains_required_closure_tokens() -> None:
    handoff = _read("docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md")
    for token in [
        "window_1538p_closed_phase_1545p",
        "window_1538p_closure_gate_committed_phase_1545p",
        "window_1538p_closure_gate_verdict=pass",
        "obl_021_closed_phase_1545p",
        "obl_022_closed_phase_1545p",
        "obl_027_closed_phase_1545p",
        "block_4_all_obligations_closed_phase_1545p",
        "production_emission_not_activated_guard_retained_phase_1545p",
        "public_path_remains_blocked_phase_1545p",
        "go_window_1546p_required_next",
    ]:
        assert token in handoff


def test_sequence_lock_records_closed_pass() -> None:
    sequence_lock = _read("docs/specs/ilc_phase_1538p_1545p_sequence_lock_v0.1.md")
    assert "**Status:** CLOSED PASS - Phase 1545p closure gate committed" in sequence_lock
    assert "window_1538p_closed_phase_1545p" in sequence_lock
    assert "block_4_all_obligations_closed_phase_1545p" in sequence_lock


def test_planning_index_marks_phase_1545p_current() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    assert "Phase 1545p Window 1538p-1545p closure gate" in planning_index
    assert "window_1538p_closed_phase_1545p" in planning_index
    assert "go_window_1546p_required_next" in planning_index


def test_agents_records_closed_window_and_next_go() -> None:
    agents = _read("AGENTS.md")
    assert "window_1538p_1545p: CLOSED_PASS" in agents
    assert "block_4_all_obligations: complete_closed_phase_1545p" in agents
    assert "next_phase: window_1546p_not_open_go_window_1546p_required_next" in agents


def test_status_records_phase_1545p_closure() -> None:
    status = _read("docs/phases/STATUS.md")
    assert "## Phase 1545p - Window 1538p-1545p Closure Gate" in status
    assert "window_1538p_closed_phase_1545p" in status
    assert "block_4_all_obligations_closed_phase_1545p" in status


def test_closure_gate_selftest_guard_is_declared() -> None:
    source = _read("tests/test_phase_1545p_window_1538p_1545p_closure_gate.py")
    assert 'GATE_ENV_VAR = "ILC_PHASE_1545P_GATE_SELFTEST"' in source
    assert "pytest.skip(" in source
    assert "allow_module_level=True" in source
