from __future__ import annotations

import inspect
from pathlib import Path

from ilc_core.epoch import (
    TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN,
    build_validator_reward_pool_routing_quote,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/epoch/validator_reward_pool_routing_runtime.py"
INTEGRATION_GATE = ROOT / "ilc_core/epoch/issuance_economics_integration_gate.py"
WALKTHROUGH = ROOT / "docs/phases/phase_1367_pre_gate_fix_pass_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1367_validator_quote_signature_removes_budget_override() -> None:
    signature = inspect.signature(build_validator_reward_pool_routing_quote)
    runtime = _read(RUNTIME)

    assert "treasury_epoch_budget_ilc" not in signature.parameters
    assert "cumulative_issued_before_epoch_ilc" in signature.parameters
    assert "build_epoch_emission_quote" in runtime
    assert "capped_epoch_budget_ilc" in runtime
    assert TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN in runtime


def test_phase_1367_integration_gate_uses_emission_bound_budget() -> None:
    integration_gate = _read(INTEGRATION_GATE)

    assert "validator_treasury_budget" not in integration_gate
    assert "TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN" in integration_gate
    assert "emission_quote.capped_epoch_budget_ilc * BURN_FLOOR_FRACTION" in integration_gate


def test_phase_1367_docs_record_blocker_resolution_without_true_soft_rc_claim() -> None:
    required_tokens = (
        "pre_gate_fix_pass_phase_1367.v0.1",
        "phase_1366_blockers_addressed_or_clean_pass_phase_1367",
        "no_new_scope_introduced_phase_1367",
        "phase_1366_treasury_epoch_budget_binding_verified",
    )
    for path in (WALKTHROUGH, STATUS, INDEX, FORWARD_PLAN, SEQUENCE_LOCK, ROADMAP):
        text = _read(path)
        for token in required_tokens:
            assert token in text, f"{path} missing {token}"

    walkthrough = _read(WALKTHROUGH)
    assert "02c2eb0c" in walkthrough
    assert "did not re-run the full Phase 1366 soft RC gate" in walkthrough
    assert "soft_rc_eligible=true" in walkthrough
    assert "did not record `soft_rc_eligible=true`" in walkthrough
