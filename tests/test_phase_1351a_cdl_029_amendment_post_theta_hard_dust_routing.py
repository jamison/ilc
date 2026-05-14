from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch import (
    CDL_029_AMENDMENT_PHASE_1351A_TOKEN,
    CDL_029_POST_THETA_HARD_ROUTING_AMENDMENT_TOKEN,
    CDL_083_UPHELD_REFUTATION_RECIPIENTS_PRIMARY_DUST_ROUTE_TOKEN,
    GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN,
    PERFORMER_POOL_FALLBACK_DUST_ROUTE_TOKEN,
    PERFORMER_POOL_RESIDUAL_ROUTE,
    POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN,
    PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN,
    PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN,
    UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE,
    build_allocation_distribution_quote,
)


ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
EVIDENCE = (
    ROOT / "docs/specs/ilc_cdl_029_post_theta_hard_dust_routing_amendment_1351a_v0.1.md"
)
RUNTIME = ROOT / "ilc_core/epoch/allocation_distributor_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1351a_cdl_029_amendment_post_theta_hard_dust_routing_walkthrough.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1351a_tokens_and_register_amendment_are_recorded() -> None:
    cdl_register = _read(CDL_REGISTER)
    evidence = _read(EVIDENCE)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    sequence_lock = _read(SEQUENCE_LOCK)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)

    for token in (
        "cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1",
        "cdl_029_amendment_phase_1351a",
        "cdl_083_upheld_refutation_recipients_primary_dust_route_phase_1351a",
        "performer_pool_fallback_dust_route_phase_1351a",
        "post_theta_hard_routing_implemented_phase_1351a",
        "pre_theta_hard_routing_unchanged_phase_1351a",
        "production_distribution_not_activated_phase_1351a",
        "genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a",
    ):
        assert token in cdl_register or token in runtime
        assert token in evidence
        assert token in prompt
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough

    assert "amendment_phase: 1351a" in cdl_register
    assert "amendment_token: cdl_029_post_theta_hard_dust_routing_1351a" in cdl_register
    assert "local ECU attribution" in cdl_register
    assert "CDL-083 Q4 caller-filtered upheld-refutation recipients" in cdl_register
    assert "CDL-V7 is admissibility-only" in sequence_lock


def test_phase_1351a_pre_theta_hard_residual_path_is_unchanged() -> None:
    quote = build_allocation_distribution_quote(issuance_epoch=1, total_epoch_allocation_ilc="1.2345678999")

    assert quote.rounding_residual_to_genesis_overhead_ilc == Decimal("0.000000002")
    assert quote.rounding_residual_to_upheld_refutation_recipients_ilc == Decimal("0")
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0")
    assert quote.genesis_overhead_pool_ilc == Decimal("0.061728396")
    assert quote.post_theta_hard_routing_token == PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN
    assert quote.decision_token == PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN


def test_phase_1351a_post_theta_hard_residual_routes_to_upheld_refutation_recipient_pool() -> None:
    quote = build_allocation_distribution_quote(
        issuance_epoch=2,
        total_epoch_allocation_ilc="0.000000009",
        genesis_overhead_cap_blocked=True,
        upheld_refutation_recipients=["agent:refuter-2", "agent:refuter-1"],
    )

    assert CDL_029_POST_THETA_HARD_ROUTING_AMENDMENT_TOKEN == (
        "cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1"
    )
    assert CDL_029_AMENDMENT_PHASE_1351A_TOKEN == "cdl_029_amendment_phase_1351a"
    assert CDL_083_UPHELD_REFUTATION_RECIPIENTS_PRIMARY_DUST_ROUTE_TOKEN == (
        "cdl_083_upheld_refutation_recipients_primary_dust_route_phase_1351a"
    )
    assert quote.genesis_overhead_cap_blocked is True
    assert quote.genesis_overhead_pool_ilc == Decimal("0E-9")
    assert quote.rounding_residual_to_upheld_refutation_recipients_ilc == Decimal("0.000000001")
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0")
    assert quote.residual_route == UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE
    assert quote.upheld_refutation_recipients == ("agent:refuter-1", "agent:refuter-2")
    assert quote.post_theta_hard_routing_token == POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN


def test_phase_1351a_post_theta_hard_residual_falls_back_to_performer_pool() -> None:
    quote = build_allocation_distribution_quote(
        issuance_epoch=3,
        total_epoch_allocation_ilc="0.000000009",
        genesis_overhead_cap_blocked=True,
    )

    assert PERFORMER_POOL_FALLBACK_DUST_ROUTE_TOKEN == "performer_pool_fallback_dust_route_phase_1351a"
    assert quote.performer_reward_pool_ilc == Decimal("0.000000008")
    assert quote.auditor_reward_pool_ilc == Decimal("0.000000001")
    assert quote.genesis_overhead_pool_ilc == Decimal("0E-9")
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0.000000001")
    assert quote.residual_route == PERFORMER_POOL_RESIDUAL_ROUTE
    assert quote.post_theta_hard_routing_token == POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN


def test_phase_1351a_full_genesis_base_tranche_routing_remains_fail_closed() -> None:
    with pytest.raises(
        ValueError,
        match=GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN,
    ):
        build_allocation_distribution_quote(
            issuance_epoch=4,
            total_epoch_allocation_ilc="100",
            genesis_overhead_cap_blocked=True,
            upheld_refutation_recipients=["agent:refuter-1"],
        )
