"""Phase 1537p Window 1531p-1537p closure-gate checks.

PUBLIC_RC_EXCLUDE: phase_1537p_private_closure_gate_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window closure assertion. Not a public RC artifact.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


GATE_ENV_VAR = "ILC_PHASE_1537P_GATE_SELFTEST"
if os.environ.get(GATE_ENV_VAR) == "1":
    pytest.skip("selftest guard: skipping gate when running as part of full regression")

ROOT = Path(__file__).resolve().parents[1]

PHASE_TEST_FILES = [
    "tests/test_phase_1531p_block4_gap_refresh.py",
    "tests/test_phase_1532p_obl020_emission_production_path.py",
    "tests/test_phase_1533p_obl020_settlement_roots.py",
    "tests/test_phase_1534p_obl020_canonical_economic_events.py",
    "tests/test_phase_1535p_obl020_economic_round_trip.py",
]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1537p_input_phase_test_files_are_bound() -> None:
    for relative_path in PHASE_TEST_FILES:
        assert (ROOT / relative_path).exists(), relative_path

    assert GATE_ENV_VAR == "ILC_PHASE_1537P_GATE_SELFTEST"


def test_phase_1537p_handoff_records_required_tokens_and_verdict() -> None:
    handoff = _read("docs/specs/ilc_window_1531p_1537p_handoff_1537p_v0.1.md")

    required = [
        "window_1531p_closed_phase_1537p",
        "window_1531p_closure_gate_committed_phase_1537p",
        "window_1531p_closure_gate_verdict=pass",
        "obl_020_closed_phase_1537p",
        "production_emission_not_activated_guard_set_phase_1537p",
        "public_path_remains_blocked_phase_1537p",
        "go_window_1538p_required_next",
    ]
    for token in required:
        assert token in handoff

    for phase in ["1531p", "1532p", "1533p", "1534p", "1535p", "1536p", "1537p"]:
        assert f"| {phase} |" in handoff


def test_phase_1537p_gate_checks_are_recorded_as_pass() -> None:
    walkthrough = _read(
        "docs/phases/phase_1537p_window_1531p_1537p_closure_gate_walkthrough.md"
    )

    expected_checks = [
        "Phase 1531p sequence lock and audit committed",
        "Phase 1532p production emission path committed",
        "Phase 1533p settlement roots committed",
        "Phase 1534p canonical economic event emitter committed",
        "Phase 1535p round-trip integration test committed",
        "Phase 1536p coherence complete",
        "`PRODUCTION_EMISSION_NOT_ACTIVATED = True`",
        "`ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True`",
        "OBL-020 closed",
        "OBL-021/022/027 still open",
        "No CDL mutation",
        "No production emission activation",
        "Public path still blocked",
        "All focused tests pass",
        "`issuance_economics_integration_gate.py` unchanged",
    ]
    for check in expected_checks:
        assert check in walkthrough
    assert walkthrough.count("| pass |") >= 15


def test_phase_1537p_production_emission_guard_remains_true() -> None:
    source = _read("ilc_core/epoch/epoch_emission_production_path.py")

    assert "PRODUCTION_EMISSION_NOT_ACTIVATED = True" in source
    assert "PRODUCTION_EMISSION_NOT_ACTIVATED = False" not in source


def test_phase_1537p_type_registry_guard_remains_true() -> None:
    source = _read("ilc_core/bundle/type_registry.py")

    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in source
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = False" not in source


def test_phase_1537p_obligation_register_closes_only_obl020_window_a() -> None:
    register = _read("docs/specs/ilc_open_obligation_register_v0.1.md")

    obl020_row = next(line for line in register.splitlines() if line.startswith("| OBL-020 |"))
    assert "| closed |" in obl020_row
    assert "obl_020_closed_phase_1537p" in obl020_row
    for obl in ["OBL-021", "OBL-022", "OBL-027"]:
        row = next(line for line in register.splitlines() if line.startswith(f"| {obl} |"))
        assert "| open |" in row
        assert "Block 4 Window B, phase/window TBD by later sequence lock" in row


def test_phase_1537p_cdl_register_frontier_contains_later_cdl_rows() -> None:
    cdl = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    cdl_rows = [line for line in cdl.splitlines() if line.startswith("| CDL-")]

    assert len(cdl_rows) >= 113
    assert "| CDL-097 |" in cdl
    assert "| CDL-096 |" in cdl
    assert "| CDL-098 |" in cdl


def test_phase_1537p_public_path_and_guard_non_authorizations_are_recorded() -> None:
    handoff = _read("docs/specs/ilc_window_1531p_1537p_handoff_1537p_v0.1.md")
    status = _read("docs/phases/STATUS.md")
    normalized_status = " ".join(status.split())

    required_non_claims = [
        "No public repository publication",
        "No public package publication",
        "No public source export",
        "No public RC",
        "No production emission activation",
        "No actual ECU minting",
        "No ILC settlement",
        "No wallet write",
        "No treasury write",
        "No ledger write",
        "No CDL opening",
        "No CDL mutation",
        "No ADR mutation",
        "No CDL-096 opening",
    ]
    for phrase in required_non_claims:
        assert phrase in handoff
        assert phrase in normalized_status


def test_phase_1537p_sequence_lock_and_frontier_are_closed() -> None:
    sequence_lock = _read("docs/specs/ilc_phase_1531p_1537p_sequence_lock_v0.1.md")
    planning_index = _read("docs/PLANNING_INDEX.md")
    agents = _read("AGENTS.md")

    assert "**Status:** CLOSED PASS" in sequence_lock
    assert "| 1537p | Window closure gate | SENSITIVE | COMPLETE |" in sequence_lock
    assert "window_1531p_closed_phase_1537p" in sequence_lock
    assert "Phase 1537p Window 1531p-1537p closure" in planning_index
    assert "⬅ CURRENT" in planning_index.splitlines()[3]
    assert "window_1531p_1537p: CLOSED_PASS" in agents
    assert "phase_1537p: complete_sensitive_window_closure_gate" in agents


def test_phase_1537p_issuance_integration_gate_baseline_remains_present() -> None:
    gate = _read("ilc_core/epoch/issuance_economics_integration_gate.py")

    assert (
        'ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS = "issuance_economics_integration_gate_pass"'
        in gate
    )
    assert "ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERSION" in gate
