from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.epoch.allocation_distributor_runtime import (
    GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN,
    build_allocation_distribution_quote,
)
from ilc_core.epoch.epoch_emission_production_path import (
    GENESIS_FIXED_TRANCHE_ILC,
    compute_epoch_emission_production_path,
)
from ilc_core.epoch.epoch_emission_runtime import ILC_QUANTUM


def test_fix3h_partial_cap_excess_token_is_pinned() -> None:
    assert GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN == (
        "genesis_partial_cap_excess_to_performer_pool_phase_1575c_fix3h.v0.1"
    )


def test_fix3h_allocator_routes_partial_cap_excess_to_performer_pool() -> None:
    quote = build_allocation_distribution_quote(
        1,
        Decimal("900"),
        genesis_overhead_remaining_allowance_ilc=Decimal("10"),
    )

    assert quote.genesis_overhead_pool_ilc == Decimal("10")
    assert quote.genesis_partial_cap_excess_ilc == Decimal("35")
    assert quote.genesis_partial_cap_excess_route == "performer_pool"
    assert quote.genesis_partial_cap_excess_token == GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN
    assert quote.performer_reward_pool_ilc == Decimal("755")

    record = quote.to_canonical_record()
    assert record["genesis_partial_cap_excess_ilc"] == "35"
    assert record["genesis_partial_cap_excess_route"] == "performer_pool"
    assert record["genesis_partial_cap_excess_token"] == (
        GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN
    )


def test_fix3h_allocator_exact_remaining_allowance_has_no_excess() -> None:
    quote = build_allocation_distribution_quote(
        1,
        Decimal("900"),
        genesis_overhead_remaining_allowance_ilc=Decimal("45"),
    )

    assert quote.genesis_overhead_pool_ilc == Decimal("45")
    assert quote.genesis_partial_cap_excess_ilc == Decimal("0")
    assert quote.genesis_partial_cap_excess_route == "none"
    assert quote.genesis_partial_cap_excess_token == ""
    assert quote.performer_reward_pool_ilc == Decimal("720")


def test_fix3h_partial_cap_routes_caught_rounding_residual_to_performer_metadata() -> None:
    quote = build_allocation_distribution_quote(
        1,
        Decimal("1.000000001"),
        genesis_overhead_remaining_allowance_ilc=Decimal("0"),
    )

    assert quote.genesis_overhead_pool_ilc == Decimal("0")
    assert quote.genesis_partial_cap_excess_ilc == Decimal("0.050000001")
    assert quote.performer_reward_pool_ilc == Decimal("0.850000001")
    assert quote.rounding_residual_to_genesis_overhead_ilc == Decimal("0")
    assert quote.rounding_residual_to_performer_pool_ilc == ILC_QUANTUM


def test_fix3h_partial_cap_with_one_quantum_allowance_keeps_residual_metadata_orthogonal() -> None:
    quote = build_allocation_distribution_quote(
        1,
        Decimal("1.000000001"),
        genesis_overhead_remaining_allowance_ilc=ILC_QUANTUM,
    )

    assert quote.genesis_overhead_pool_ilc == ILC_QUANTUM
    assert quote.genesis_partial_cap_excess_ilc == Decimal("0.050000000")
    assert quote.genesis_partial_cap_excess_route == "performer_pool"
    assert quote.genesis_partial_cap_excess_token == GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN
    assert quote.performer_reward_pool_ilc == Decimal("0.850000000")
    assert quote.rounding_residual_to_genesis_overhead_ilc == ILC_QUANTUM
    assert quote.rounding_residual_to_performer_pool_ilc == Decimal("0")


def test_fix3h_production_path_caps_final_epoch_genesis_credit() -> None:
    remaining = Decimal("13500")
    result = compute_epoch_emission_production_path(
        20,
        Decimal("2000000"),
        Decimal("1500000"),
        genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC - remaining,
    )

    assert result.governor_report is not None
    assert result.governor_report["cap_blocked"] is False
    assert result.allocation_quote.genesis_overhead_pool_ilc == remaining
    assert result.allocation_quote.genesis_partial_cap_excess_ilc == Decimal("54000")
    assert result.allocation_quote.genesis_partial_cap_excess_route == "performer_pool"
    assert result.allocation_quote.genesis_partial_cap_excess_token == (
        GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN
    )


def test_fix3h_one_quantum_below_cap_receives_only_one_quantum() -> None:
    result = compute_epoch_emission_production_path(
        3,
        Decimal("25920000"),
        Decimal("1000"),
        genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC - ILC_QUANTUM,
    )

    assert result.governor_report is not None
    assert result.governor_report["cap_blocked"] is False
    assert result.allocation_quote.genesis_overhead_pool_ilc == ILC_QUANTUM
    assert result.allocation_quote.genesis_partial_cap_excess_ilc > Decimal("0")
    assert result.allocation_quote.performer_reward_pool_ilc > Decimal("720")


def test_fix3h_post_cap_nonzero_base_still_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a",
    ):
        compute_epoch_emission_production_path(
            3,
            Decimal("20000000"),
            Decimal("1000"),
            genesis_cumulative_accrual_ilc=GENESIS_FIXED_TRANCHE_ILC,
        )
