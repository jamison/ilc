"""Phase 1564 Window 1556-1564 closure-gate checks.

PUBLIC_RC_EXCLUDE: phase_1564_private_closure_gate_test
PUBLIC_RC_EXCLUDE_REASON: Internal private closure-gate test for pre-RC completion artifacts; not part of public RC exports.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest


GATE_ENV_VAR = "ILC_PHASE_1564_GATE_SELFTEST"


def _phase_1564_selftest_guard_message() -> str | None:
    if os.environ.get(GATE_ENV_VAR) == "1":
        return "selftest guard: ILC_PHASE_1564_GATE_SELFTEST=1"
    return None


if (guard_message := _phase_1564_selftest_guard_message()) is not None:
    pytest.skip(guard_message, allow_module_level=True)


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CLOSURE_TOKENS = [
    "hb_001_genesis_authority_assertion_builder_wired_phase_1557",
    "hb_003_layer_0_bundle_truth_primitive_schema_embedded_phase_1558",
    "hb_002_minimal_serving_receipt_implemented_phase_1559",
    "agent_init_ceremony_live_executed_phase_1560",
    "ecu_live_smoke_test_executed_phase_1561",
    "production_emission_not_activated_confirmed_phase_1561",
    "invitation_provenance_chain_runtime_implemented_phase_1562",
    "pre_rc_completion_coherence_complete_phase_1563",
    "context_capsule_v5_70_pre_block6_committed",
]

PHASE_1564_OUTPUT_TOKENS = [
    "window_1556_closed_phase_1564",
    "window_1556_closure_gate_verdict=pass",
    "homoiconic_bootstrap_hb001_hb002_hb003_complete_phase_1564",
    "ecu_live_smoke_confirmed_phase_1564",
    "agent_init_live_confirmed_phase_1564",
    "invitation_provenance_chain_confirmed_phase_1564",
    "block6_entry_conditions_satisfied_phase_1564",
    "go_window_1565_block6_required_next",
    "public_path_remains_blocked_phase_1564",
]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _require_tokens(text: str, tokens: list[str]) -> None:
    for token in tokens:
        if token not in text:
            pytest.fail(f"missing: {token}")


def test_phase_1564_required_closure_tokens_present_in_status() -> None:
    status = _read("docs/phases/STATUS.md")
    _require_tokens(status, REQUIRED_CLOSURE_TOKENS)


def test_phase_1564_handoff_and_routing_tokens() -> None:
    handoff_path = ROOT / "docs/specs/ilc_window_1556_1564_handoff_1564_v0.1.md"
    if not handoff_path.exists():
        pytest.fail("missing: docs/specs/ilc_window_1556_1564_handoff_1564_v0.1.md")

    handoff = handoff_path.read_text(encoding="utf-8")
    status = _read("docs/phases/STATUS.md")

    if "Block 6" not in handoff and "Window 1565" not in handoff:
        pytest.fail("missing: Block 6 or Window 1565 routing in handoff")
    _require_tokens(handoff, ["go_window_1565_block6_required_next"])
    _require_tokens(status, ["window_1556_closure_gate_verdict=pass", "go_window_1565_block6_required_next"])


def test_phase_1564_selftest_guard_function(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(GATE_ENV_VAR, "1")
    assert _phase_1564_selftest_guard_message() == "selftest guard: ILC_PHASE_1564_GATE_SELFTEST=1"

    source = _read("tests/test_phase_1564_window_1556_1564_closure_gate.py")
    assert 'GATE_ENV_VAR = "ILC_PHASE_1564_GATE_SELFTEST"' in source
    assert "pytest.skip(" in source
    assert "allow_module_level=True" in source


def test_phase_1564_non_authorizations_preserved() -> None:
    status = _read("docs/phases/STATUS.md")
    phase_1564_status = status.split("## Phase 1563 -", maxsplit=1)[0]
    handoff = _read("docs/specs/ilc_window_1556_1564_handoff_1564_v0.1.md")

    assert "public_rc_authorized" not in phase_1564_status
    assert "guard_cleared" not in phase_1564_status
    assert re.search(r"NOT_ACTIVATED.*False", phase_1564_status) is None
    assert "Phase 1448b is authorized" not in handoff
    assert "Phase 1448b is not authorized" in handoff
    assert re.search(r"public_path.*open", handoff, re.IGNORECASE) is None


def test_phase_1564_sequence_lock_closed_pass() -> None:
    sequence_lock = _read("docs/specs/ilc_phase_1556_1564_sequence_lock_v0.1.md")
    assert "**Status:** CLOSED PASS - Phase 1564 closure gate committed" in sequence_lock
    assert "| 1564 | Window closure gate | SENSITIVE | COMPLETE |" in sequence_lock
    _require_tokens(sequence_lock, PHASE_1564_OUTPUT_TOKENS)


def test_phase_1564_planning_index_frontier() -> None:
    planning_index = _read("docs/PLANNING_INDEX.md")
    assert planning_index.count("⬅ CURRENT") == 1
    assert "Phase 1564 Window 1556-1564 closure gate" in planning_index
    assert "Window 1556-1564 CLOSED PASS" in planning_index
    assert "Block 6 guidance - Window 1565-1575" in planning_index
    assert "go_window_1565_block6_required_next" in planning_index


def test_phase_1564_agents_records_closed_window_and_block6_gate() -> None:
    agents = _read("AGENTS.md")
    assert "phase_1564: complete_sensitive_window_closure_gate" in agents
    assert "window_1556_1564: CLOSED_PASS" in agents
    assert "next_phase: go_window_1565_block6_required_next" in agents
    assert "sensitive_gate: phase_1565_requires_exact_GO_Phase_1565" in agents
    assert "public_path: blocked_public_path_remains_blocked_phase_1564" in agents


def test_phase_1564_handoff_mem_palace_disposition() -> None:
    handoff = _read("docs/specs/ilc_window_1556_1564_handoff_1564_v0.1.md")
    assert "## 6. MemPalace refresh disposition" in handoff
    assert "Disposition: required" in handoff
    assert "Active working set impacted: yes" in handoff
    assert "Working-set descriptor: docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json" in handoff
    assert "Manifest: docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json" in handoff
    assert "Rebuild command: bash tools/mempalace/build_active_working_set.sh" in handoff


def test_phase_1564_status_records_output_tokens() -> None:
    status = _read("docs/phases/STATUS.md")
    _require_tokens(status, PHASE_1564_OUTPUT_TOKENS)
