from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch import (
    ALLOCATION_80_15_5_ROUTING_TOKEN,
    ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION,
    ALLOCATION_FRACTION_TOTAL,
    AUDITOR_ALLOCATION_FRACTION,
    AUDITOR_REWARD_POOL_LABEL,
    CDL_029_AMENDMENT_PHASE_1351A_TOKEN,
    CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN,
    CDL_029_DEPENDENCY,
    CDL_029_POST_THETA_HARD_ROUTING_AMENDMENT_TOKEN,
    CDL_029_POST_THETA_HARD_ROUTING_IMPLEMENTATION_DEFERRED_TOKEN,
    CDL_083_UPHELD_REFUTATION_RECIPIENTS_PRIMARY_DUST_ROUTE_TOKEN,
    GENESIS_OVERHEAD_ALLOCATION_FRACTION,
    GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN,
    GENESIS_OVERHEAD_CAP_BLOCKED_DUST_ROUTING_DEFERRED_TOKEN,
    GENESIS_OVERHEAD_CAP_BLOCKED_GUARD_TOKEN,
    GENESIS_OVERHEAD_POOL_LABEL,
    GENESIS_RESIDUAL_ROUTE,
    NO_DIRECT_ALLOCATION_STUB_FOUND_TOKEN,
    PERFORMER_ALLOCATION_FRACTION,
    PERFORMER_POOL_FALLBACK_DUST_ROUTE_TOKEN,
    PERFORMER_POOL_RESIDUAL_ROUTE,
    PERFORMER_REWARD_POOL_LABEL,
    POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN,
    PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN,
    PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN,
    PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN,
    PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN,
    THETA_HARD_CONTINUITY_FRACTION,
    THETA_HARD_ILC,
    UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE,
    build_allocation_distribution_quote,
    require_cdl_029_allocation_fractions,
    require_production_allocation_distribution_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/epoch/allocation_distributor_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1347_g8_cdl_029_80_15_5_allocation_distributor.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1347_cdl_029_80_15_5_allocation_distributor_walkthrough.md"
)
CDL_029_EVIDENCE = (
    ROOT / "docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1347_constants_bind_cdl_029_and_default_off_state() -> None:
    assert ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION == "allocation_distributor_runtime_1347.v0.1"
    assert CDL_029_DEPENDENCY == "cdl_029_allocation_split_ratified_phase_272.v0.1"
    assert CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN == (
        "cdl_029_allocation_distributor_runtime_phase_1347.v0.1"
    )
    assert ALLOCATION_80_15_5_ROUTING_TOKEN == "allocation_80_15_5_routing_phase_1347"
    assert PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN == (
        "production_distribution_not_activated_phase_1347"
    )
    assert PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN == (
        "phase_1366_soft_rc_eligible_true_value_path_activation_required"
    )
    assert NO_DIRECT_ALLOCATION_STUB_FOUND_TOKEN == "no_direct_allocation_stub_found_phase_1347"
    assert GENESIS_OVERHEAD_CAP_BLOCKED_GUARD_TOKEN == (
        "genesis_overhead_cap_blocked_guard_phase_1347_fix1"
    )
    assert GENESIS_OVERHEAD_CAP_BLOCKED_DUST_ROUTING_DEFERRED_TOKEN == (
        "genesis_overhead_cap_blocked_dust_routing_deferred"
    )
    assert CDL_029_POST_THETA_HARD_ROUTING_IMPLEMENTATION_DEFERRED_TOKEN == (
        "cdl_029_post_theta_hard_routing_implementation_deferred_pending_decimal_governor"
    )
    assert CDL_029_POST_THETA_HARD_ROUTING_AMENDMENT_TOKEN == (
        "cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1"
    )
    assert CDL_029_AMENDMENT_PHASE_1351A_TOKEN == "cdl_029_amendment_phase_1351a"
    assert CDL_083_UPHELD_REFUTATION_RECIPIENTS_PRIMARY_DUST_ROUTE_TOKEN == (
        "cdl_083_upheld_refutation_recipients_primary_dust_route_phase_1351a"
    )
    assert PERFORMER_POOL_FALLBACK_DUST_ROUTE_TOKEN == (
        "performer_pool_fallback_dust_route_phase_1351a"
    )
    assert POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN == (
        "post_theta_hard_routing_implemented_phase_1351a"
    )
    assert PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN == (
        "pre_theta_hard_routing_unchanged_phase_1351a"
    )
    assert PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN == (
        "production_distribution_not_activated_phase_1351a"
    )
    assert GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN == (
        "genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a"
    )
    assert GENESIS_RESIDUAL_ROUTE == "genesis"
    assert UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE == "upheld_refutation_recipients"
    assert PERFORMER_POOL_RESIDUAL_ROUTE == "performer_pool"
    assert SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN == (
        "split_quote_clarified_not_full_genesis_tranche_phase_1347_fix1"
    )
    assert PERFORMER_ALLOCATION_FRACTION == Decimal("0.80")
    assert AUDITOR_ALLOCATION_FRACTION == Decimal("0.15")
    assert GENESIS_OVERHEAD_ALLOCATION_FRACTION == Decimal("0.05")
    assert ALLOCATION_FRACTION_TOTAL == Decimal("1.00")
    assert THETA_HARD_ILC == Decimal("0.05")
    assert THETA_HARD_CONTINUITY_FRACTION == Decimal("0.05")


def test_allocation_distributor_routes_80_15_5() -> None:
    quote = build_allocation_distribution_quote(issuance_epoch=11, total_epoch_allocation_ilc="100")

    assert quote.issuance_epoch == 11
    assert quote.total_epoch_allocation_ilc == Decimal("100.000000000")
    assert quote.performer_fraction == Decimal("0.80")
    assert quote.auditor_fraction == Decimal("0.15")
    assert quote.genesis_overhead_fraction == Decimal("0.05")
    assert quote.performer_reward_pool_ilc == Decimal("80.000000000")
    assert quote.auditor_reward_pool_ilc == Decimal("15.000000000")
    assert quote.genesis_overhead_pool_ilc == Decimal("5.000000000")
    assert quote.rounding_residual_to_genesis_overhead_ilc == Decimal("0E-9")
    assert quote.genesis_overhead_cap_blocked is False
    assert quote.rounding_residual_to_upheld_refutation_recipients_ilc == Decimal("0")
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0")
    assert quote.residual_route == GENESIS_RESIDUAL_ROUTE
    assert quote.upheld_refutation_recipients == ()
    assert quote.post_theta_hard_routing_token == PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN
    assert quote.split_quote_boundary_token == SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN
    assert quote.performer_reward_pool_label == PERFORMER_REWARD_POOL_LABEL
    assert quote.auditor_reward_pool_label == AUDITOR_REWARD_POOL_LABEL
    assert quote.genesis_overhead_pool_label == GENESIS_OVERHEAD_POOL_LABEL
    assert quote.production_allocation_distribution_activated is False
    assert quote.decision_token == PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN


def test_allocation_distributor_quantizes_down_and_preserves_total() -> None:
    quote = build_allocation_distribution_quote(0, "1.2345678999")

    assert quote.total_epoch_allocation_ilc == Decimal("1.234567899")
    assert quote.performer_reward_pool_ilc == Decimal("0.987654319")
    assert quote.auditor_reward_pool_ilc == Decimal("0.185185184")
    assert quote.genesis_overhead_pool_ilc == Decimal("0.061728396")
    assert quote.rounding_residual_to_genesis_overhead_ilc == Decimal("0.000000002")
    assert (
        quote.performer_reward_pool_ilc
        + quote.auditor_reward_pool_ilc
        + quote.genesis_overhead_pool_ilc
    ) == quote.total_epoch_allocation_ilc


def test_allocation_distributor_fails_closed_on_nonzero_genesis_base_when_cap_blocked() -> None:
    with pytest.raises(
        ValueError,
        match=GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN,
    ):
        build_allocation_distribution_quote(
            issuance_epoch=0,
            total_epoch_allocation_ilc="1.2345678999",
            genesis_overhead_cap_blocked=True,
        )

    with pytest.raises(
        ValueError,
        match=GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN,
    ):
        build_allocation_distribution_quote(
            issuance_epoch=0,
            total_epoch_allocation_ilc="100",
            genesis_overhead_cap_blocked=True,
        )

    zero_quote = build_allocation_distribution_quote(
        issuance_epoch=0,
        total_epoch_allocation_ilc="0",
        genesis_overhead_cap_blocked=True,
    )

    assert zero_quote.genesis_overhead_cap_blocked is True
    assert zero_quote.genesis_overhead_pool_ilc == Decimal("0E-9")
    assert zero_quote.residual_route == PERFORMER_POOL_RESIDUAL_ROUTE
    assert zero_quote.post_theta_hard_routing_token == POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN


def test_post_theta_hard_residual_routes_to_upheld_refutation_recipients() -> None:
    quote = build_allocation_distribution_quote(
        issuance_epoch=9,
        total_epoch_allocation_ilc="0.000000009",
        genesis_overhead_cap_blocked=True,
        upheld_refutation_recipients=["agent:z", "agent:a"],
    )

    assert quote.total_epoch_allocation_ilc == Decimal("0.000000009")
    assert quote.performer_reward_pool_ilc == Decimal("0.000000007")
    assert quote.auditor_reward_pool_ilc == Decimal("0.000000001")
    assert quote.genesis_overhead_pool_ilc == Decimal("0E-9")
    assert quote.rounding_residual_to_genesis_overhead_ilc == Decimal("0")
    assert quote.rounding_residual_to_upheld_refutation_recipients_ilc == Decimal("0.000000001")
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0")
    assert quote.residual_route == UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE
    assert quote.upheld_refutation_recipients == ("agent:a", "agent:z")
    assert quote.post_theta_hard_routing_token == POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN
    assert quote.decision_token == PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN
    assert (
        quote.performer_reward_pool_ilc
        + quote.auditor_reward_pool_ilc
        + quote.genesis_overhead_pool_ilc
        + quote.rounding_residual_to_upheld_refutation_recipients_ilc
    ) == quote.total_epoch_allocation_ilc


def test_post_theta_hard_residual_falls_back_to_performer_pool() -> None:
    quote = build_allocation_distribution_quote(
        issuance_epoch=9,
        total_epoch_allocation_ilc="0.000000009",
        genesis_overhead_cap_blocked=True,
        upheld_refutation_recipients=[],
    )

    assert quote.performer_reward_pool_ilc == Decimal("0.000000008")
    assert quote.auditor_reward_pool_ilc == Decimal("0.000000001")
    assert quote.genesis_overhead_pool_ilc == Decimal("0E-9")
    assert quote.rounding_residual_to_genesis_overhead_ilc == Decimal("0")
    assert quote.rounding_residual_to_upheld_refutation_recipients_ilc == Decimal("0")
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0.000000001")
    assert quote.residual_route == PERFORMER_POOL_RESIDUAL_ROUTE
    assert quote.upheld_refutation_recipients == ()
    assert (
        quote.performer_reward_pool_ilc
        + quote.auditor_reward_pool_ilc
        + quote.genesis_overhead_pool_ilc
    ) == quote.total_epoch_allocation_ilc


def test_allocation_fraction_guards_enforce_sum_and_exact_cdl_029_values() -> None:
    assert require_cdl_029_allocation_fractions() == (
        Decimal("0.80"),
        Decimal("0.15"),
        Decimal("0.05"),
    )
    with pytest.raises(ValueError, match="allocation_fractions_must_sum_to_one"):
        require_cdl_029_allocation_fractions("0.80", "0.15", "0.04")
    with pytest.raises(ValueError, match="allocation_fractions_must_equal_cdl_029_80_15_5"):
        require_cdl_029_allocation_fractions("0.79", "0.16", "0.05")


def test_exact_numeric_guards_reject_float_bool_negative_and_non_finite() -> None:
    with pytest.raises(ValueError, match="allocation_issuance_epoch_must_be_non_negative_int"):
        build_allocation_distribution_quote(True, Decimal("0"))
    with pytest.raises(ValueError, match="allocation_issuance_epoch_must_be_non_negative_int"):
        build_allocation_distribution_quote(-1, Decimal("0"))
    with pytest.raises(ValueError, match="total_epoch_allocation_ilc_must_be_exact_decimal"):
        build_allocation_distribution_quote(0, 0.1)
    with pytest.raises(ValueError, match="total_epoch_allocation_ilc_must_be_finite"):
        build_allocation_distribution_quote(0, Decimal("NaN"))
    with pytest.raises(ValueError, match="total_epoch_allocation_ilc_must_be_non_negative"):
        build_allocation_distribution_quote(0, Decimal("-0.000000001"))
    with pytest.raises(ValueError, match="performer_fraction_must_be_exact_decimal"):
        build_allocation_distribution_quote(0, "10", performer_fraction=0.8)
    with pytest.raises(ValueError, match="genesis_overhead_cap_blocked_must_be_bool"):
        build_allocation_distribution_quote(0, "10", genesis_overhead_cap_blocked=1)
    with pytest.raises(ValueError, match="upheld_refutation_recipients_must_be_list_or_none"):
        build_allocation_distribution_quote(
            0,
            "0.000000009",
            genesis_overhead_cap_blocked=True,
            upheld_refutation_recipients=("agent:a",),  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="upheld_refutation_recipient_must_be_non_empty_string"):
        build_allocation_distribution_quote(
            0,
            "0.000000009",
            genesis_overhead_cap_blocked=True,
            upheld_refutation_recipients=[""],
        )
    with pytest.raises(ValueError, match="upheld_refutation_recipients_must_be_unique"):
        build_allocation_distribution_quote(
            0,
            "0.000000009",
            genesis_overhead_cap_blocked=True,
            upheld_refutation_recipients=["agent:a", "agent:a"],
        )


def test_production_allocation_distribution_guard_remains_closed() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN):
        require_production_allocation_distribution_activation(None)
    with pytest.raises(
        ValueError,
        match="production_allocation_distribution_activation_not_implemented_phase_1347",
    ):
        require_production_allocation_distribution_activation(
            PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN
        )


def test_canonical_record_uses_strings_for_decimal_amounts() -> None:
    record = build_allocation_distribution_quote(5, "100").to_canonical_record()

    assert record["runtime_version"] == ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION
    assert record["performer_fraction"] == "0.8"
    assert record["auditor_fraction"] == "0.15"
    assert record["genesis_overhead_fraction"] == "0.05"
    assert record["genesis_overhead_cap_blocked"] is False
    assert record["theta_hard_continuity_fraction"] == "0.05"
    assert record["total_epoch_allocation_ilc"] == "100"
    assert record["performer_reward_pool_ilc"] == "80"
    assert record["auditor_reward_pool_ilc"] == "15"
    assert record["genesis_overhead_pool_ilc"] == "5"
    assert record["rounding_residual_to_upheld_refutation_recipients_ilc"] == "0"
    assert record["rounding_residual_to_performer_pool_ilc"] == "0"
    assert record["residual_route"] == GENESIS_RESIDUAL_ROUTE
    assert record["upheld_refutation_recipients"] == []
    assert record["post_theta_hard_routing_token"] == PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN
    assert record["split_quote_boundary_token"] == (
        SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN
    )
    assert record["production_allocation_distribution_activated"] is False
    assert record["decision_token"] == PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN


def test_evidence_prompt_frontier_and_walkthrough_record_tokens() -> None:
    evidence = _read(CDL_029_EVIDENCE)
    prompt = _read(PROMPT)
    status = _read(STATUS)
    index = _read(INDEX)
    forward_plan = _read(FORWARD_PLAN)
    walkthrough = _read(WALKTHROUGH)
    runtime = _read(RUNTIME)

    assert "performer / auditor / genesis split = `80 / 15 / 5`" in evidence
    assert 'PERFORMER_ALLOCATION_FRACTION = Decimal("0.80")' in runtime
    assert 'AUDITOR_ALLOCATION_FRACTION = Decimal("0.15")' in runtime
    assert 'GENESIS_OVERHEAD_ALLOCATION_FRACTION = Decimal("0.05")' in runtime
    assert 'THETA_HARD_ILC = Decimal("0.05")' in runtime
    assert "genesis_overhead_cap_blocked_dust_routing_deferred" in runtime
    for token in (
        "cdl_029_allocation_distributor_runtime_phase_1347.v0.1",
        "allocation_80_15_5_routing_phase_1347",
        "production_distribution_not_activated_phase_1347",
        "phase_1366_soft_rc_eligible_true_value_path_activation_required",
        "no_direct_allocation_stub_found_phase_1347",
        "genesis_overhead_cap_blocked_guard_phase_1347_fix1",
        "cdl_029_post_theta_hard_routing_implementation_deferred_pending_decimal_governor",
        "split_quote_clarified_not_full_genesis_tranche_phase_1347_fix1",
    ):
        assert token in status
        assert token in index
        assert token in forward_plan
        assert token in walkthrough
