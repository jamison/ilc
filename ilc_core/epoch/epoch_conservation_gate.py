# SPDX-License-Identifier: AGPL-3.0-only
"""Epoch distribution conservation gate.

The gate verifies both the explicit difference field and the full double-entry
conservation equation. ``commit_epoch_distribution`` invokes this function
before any lifecycle write, so callers cannot bypass the phase-token gate by
using the commit helper directly.
"""

from __future__ import annotations

from decimal import Decimal

from ilc_core.epoch.epoch_distribution_writer import EpochDistributionOutput
from ilc_core.epoch.epoch_maturity_gate import require_monthly_issuance_maturity_proof


EPOCH_CONSERVATION_GATE_VERSION = (
    "epoch_conservation_gate_GAP_PUBLIC_RC_EPOCH_FIX1_00C.v0.1"
)
EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN = (
    "epoch_gate_conservation_check_added_GAP_PUBLIC_RC_EPOCH_FIX1_00C"
)
NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN = (
    "no_unsettled_ilc_issuance_gate_hard_check_GAP_PUBLIC_RC_EPOCH_FIX1_00C"
)
EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN = (
    "epoch_0_to_1_transition_conservation_enforced_GAP_PUBLIC_RC_EPOCH_FIX1_00C"
)

_ZERO = Decimal("0")
_RECORD_DECIMAL_FIELDS = (
    "gross_epoch_value_ilc",
    "current_emission_ilc",
    "remaining_fee_pool_ilc",
    "genesis_burn_pool_ilc",
    "agent_settled_balance_deltas_ilc",
    "genesis_settled_delta_ilc",
    "protocol_reserve_delta_ilc",
    "validator_reward_deltas_ilc",
    "treasury_settled_delta_ilc",
    "distribution_carry_forward_out_ilc",
    "distribution_carry_forward_in_ilc",
    "explicit_rounding_sinks_ilc",
    "total_debit_ilc",
    "total_credit_ilc",
    "difference_ilc",
)


def verify_epoch_conservation_before_commit(output: EpochDistributionOutput) -> None:
    """Raise unless an epoch distribution output is exactly conserved."""
    if not isinstance(output, EpochDistributionOutput):
        raise ValueError("conservation_gate_requires_epoch_distribution_output")
    if output.conservation_verified is not True:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    record = output.conservation_record
    values = {
        field_name: _require_finite_decimal(getattr(record, field_name, None))
        for field_name in _RECORD_DECIMAL_FIELDS
    }

    expected_total_debit = (
        values["current_emission_ilc"]
        + values["remaining_fee_pool_ilc"]
        + values["genesis_burn_pool_ilc"]
    )
    expected_total_credit = (
        values["agent_settled_balance_deltas_ilc"]
        + values["genesis_settled_delta_ilc"]
        + values["protocol_reserve_delta_ilc"]
        + values["validator_reward_deltas_ilc"]
        + values["treasury_settled_delta_ilc"]
        + values["distribution_carry_forward_out_ilc"]
        - values["distribution_carry_forward_in_ilc"]
        + values["explicit_rounding_sinks_ilc"]
    )
    if values["gross_epoch_value_ilc"] != expected_total_debit:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["total_debit_ilc"] != expected_total_debit:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["total_credit_ilc"] != expected_total_credit:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["difference_ilc"] != values["total_debit_ilc"] - values["total_credit_ilc"]:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if values["difference_ilc"] != _ZERO:
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    if output.issuance_epoch > 0 and values["current_emission_ilc"] > _ZERO:
        require_monthly_issuance_maturity_proof(
            output.monthly_maturity_proof,
            distribution_issuance_epoch=output.issuance_epoch,
            source_settlement_root_hex=output.source_settlement_root_hex,
        )
    return None


def _require_finite_decimal(value: object) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN)
    return value


__all__ = [
    "EPOCH_0_TO_1_CONSERVATION_ENFORCED_TOKEN",
    "EPOCH_CONSERVATION_GATE_VERSION",
    "EPOCH_GATE_CONSERVATION_CHECK_ADDED_TOKEN",
    "NO_UNSETTLED_ILC_ISSUANCE_GATE_TOKEN",
    "verify_epoch_conservation_before_commit",
]
