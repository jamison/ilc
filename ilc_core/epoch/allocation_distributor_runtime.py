# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1347 default-off CDL-029 split quote runtime.

This module computes allocation quotes only. It does not implement full
Genesis-tranche realization. Phase 1351a adds settlement-bound sub-quantum
residual routing after theta_hard. Phase 1575c-Fix3d wires the Decimal Genesis
accrual governor in the production emission path; this allocator still accepts
the resulting cap-blocked signal as an input and performs split-quote routing.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any

from .epoch_emission_runtime import (
    EPOCH_EMISSION_RUNTIME_VERSION,
    ILC_QUANTUM,
    ISSUANCE_EPOCH_DURATION,
    VALIDATION_EPOCH_SECONDS,
)
from .fee_burn_split_runtime import FEE_BURN_SPLIT_RUNTIME_VERSION


ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION = "allocation_distributor_runtime_1347.v0.1"
CDL_029_DEPENDENCY = "cdl_029_allocation_split_ratified_phase_272.v0.1"
PHASE_1345_EMISSION_RUNTIME_DEPENDENCY = EPOCH_EMISSION_RUNTIME_VERSION
PHASE_1346_FEE_BURN_RUNTIME_DEPENDENCY = FEE_BURN_SPLIT_RUNTIME_VERSION
CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN = (
    "cdl_029_allocation_distributor_runtime_phase_1347.v0.1"
)
ALLOCATION_80_15_5_ROUTING_TOKEN = "allocation_80_15_5_routing_phase_1347"
PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN = (
    "production_distribution_not_activated_phase_1347"
)
PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)
NO_DIRECT_ALLOCATION_STUB_FOUND_TOKEN = "no_direct_allocation_stub_found_phase_1347"
GENESIS_OVERHEAD_CAP_BLOCKED_GUARD_TOKEN = "genesis_overhead_cap_blocked_guard_phase_1347_fix1"
GENESIS_OVERHEAD_CAP_BLOCKED_DUST_ROUTING_DEFERRED_TOKEN = (
    "genesis_overhead_cap_blocked_dust_routing_deferred"
)
CDL_029_POST_THETA_HARD_ROUTING_IMPLEMENTATION_DEFERRED_TOKEN = (
    "cdl_029_post_theta_hard_routing_implementation_deferred_pending_decimal_governor"
)
CDL_029_POST_THETA_HARD_ROUTING_GOVERNOR_WIRED_TOKEN = (
    "cdl_029_post_theta_hard_routing_governor_wired_phase_1575c_fix3d"
)
CDL_029_POST_THETA_HARD_ROUTING_AMENDMENT_TOKEN = (
    "cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1"
)
CDL_029_AMENDMENT_PHASE_1351A_TOKEN = "cdl_029_amendment_phase_1351a"
CDL_083_UPHELD_REFUTATION_RECIPIENTS_PRIMARY_DUST_ROUTE_TOKEN = (
    "cdl_083_upheld_refutation_recipients_primary_dust_route_phase_1351a"
)
PERFORMER_POOL_FALLBACK_DUST_ROUTE_TOKEN = "performer_pool_fallback_dust_route_phase_1351a"
POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN = "post_theta_hard_routing_implemented_phase_1351a"
PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN = "pre_theta_hard_routing_unchanged_phase_1351a"
PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN = (
    "production_distribution_not_activated_phase_1351a"
)
GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN = (
    "genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a"
)
SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN = (
    "split_quote_clarified_not_full_genesis_tranche_phase_1347_fix1"
)
FINDING_1_ROUNDING_RESIDUAL_CAP_BLOCKED_RESOLVED_TOKEN = (
    "finding_1_rounding_residual_cap_blocked_resolved_phase_1440"
)

PERFORMER_ALLOCATION_FRACTION = Decimal("0.80")
AUDITOR_ALLOCATION_FRACTION = Decimal("0.15")
GENESIS_OVERHEAD_ALLOCATION_FRACTION = Decimal("0.05")
THETA_HARD_ILC = Decimal("0.05")
THETA_HARD_CONTINUITY_FRACTION = THETA_HARD_ILC
ALLOCATION_FRACTION_TOTAL = Decimal("1.00")

PERFORMER_REWARD_POOL_LABEL = "performer_reward_pool"
AUDITOR_REWARD_POOL_LABEL = "auditor_reward_pool"
GENESIS_OVERHEAD_POOL_LABEL = "genesis_overhead_pool"
UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE = "upheld_refutation_recipients"
PERFORMER_POOL_RESIDUAL_ROUTE = "performer_pool"
GENESIS_RESIDUAL_ROUTE = "genesis"
MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT = 18
INVALID_AMOUNT_MAGNITUDE_TOKEN = "invalid_amount_magnitude"
MAX_UPHELD_REFUTATION_RECIPIENTS = 128
MAX_UPHELD_REFUTATION_RECIPIENT_ID_BYTES = 256


@dataclass(frozen=True)
class EpochAllocationDistributionQuote:
    runtime_version: str
    cdl_029_dependency: str
    issuance_epoch: int
    issuance_epoch_duration: str
    validation_epoch_seconds: int
    total_epoch_allocation_ilc: Decimal
    performer_fraction: Decimal
    auditor_fraction: Decimal
    genesis_overhead_fraction: Decimal
    theta_hard_continuity_fraction: Decimal
    performer_reward_pool_ilc: Decimal
    auditor_reward_pool_ilc: Decimal
    genesis_overhead_pool_ilc: Decimal
    rounding_residual_to_genesis_overhead_ilc: Decimal
    rounding_residual_to_upheld_refutation_recipients_ilc: Decimal
    rounding_residual_to_performer_pool_ilc: Decimal
    rounding_residual_refutation_recipient_allocations_ilc: tuple[tuple[str, Decimal], ...]
    genesis_overhead_cap_blocked: bool
    residual_route: str
    upheld_refutation_recipients: tuple[str, ...]
    performer_reward_pool_label: str
    auditor_reward_pool_label: str
    genesis_overhead_pool_label: str
    post_theta_hard_routing_token: str
    split_quote_boundary_token: str
    production_allocation_distribution_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "auditor_fraction": _decimal_to_string(self.auditor_fraction),
            "auditor_reward_pool_ilc": _decimal_to_string(self.auditor_reward_pool_ilc),
            "auditor_reward_pool_label": self.auditor_reward_pool_label,
            "cdl_029_dependency": self.cdl_029_dependency,
            "decision_token": self.decision_token,
            "genesis_overhead_fraction": _decimal_to_string(self.genesis_overhead_fraction),
            "genesis_overhead_cap_blocked": self.genesis_overhead_cap_blocked,
            "genesis_overhead_pool_ilc": _decimal_to_string(self.genesis_overhead_pool_ilc),
            "genesis_overhead_pool_label": self.genesis_overhead_pool_label,
            "issuance_epoch": self.issuance_epoch,
            "issuance_epoch_duration": self.issuance_epoch_duration,
            "performer_fraction": _decimal_to_string(self.performer_fraction),
            "performer_reward_pool_ilc": _decimal_to_string(self.performer_reward_pool_ilc),
            "performer_reward_pool_label": self.performer_reward_pool_label,
            "post_theta_hard_routing_token": self.post_theta_hard_routing_token,
            "production_allocation_distribution_activated": (
                self.production_allocation_distribution_activated
            ),
            "rounding_residual_to_genesis_overhead_ilc": _decimal_to_string(
                self.rounding_residual_to_genesis_overhead_ilc
            ),
            "rounding_residual_to_performer_pool_ilc": _decimal_to_string(
                self.rounding_residual_to_performer_pool_ilc
            ),
            "rounding_residual_to_upheld_refutation_recipients_ilc": _decimal_to_string(
                self.rounding_residual_to_upheld_refutation_recipients_ilc
            ),
            "rounding_residual_refutation_recipient_allocations_ilc": [
                {"recipient": recipient, "amount_ilc": _decimal_to_string(amount)}
                for recipient, amount in self.rounding_residual_refutation_recipient_allocations_ilc
            ],
            "runtime_version": self.runtime_version,
            "residual_route": self.residual_route,
            "split_quote_boundary_token": self.split_quote_boundary_token,
            "theta_hard_continuity_fraction": _decimal_to_string(
                self.theta_hard_continuity_fraction
            ),
            "total_epoch_allocation_ilc": _decimal_to_string(self.total_epoch_allocation_ilc),
            "upheld_refutation_recipients": list(self.upheld_refutation_recipients),
            "validation_epoch_seconds": self.validation_epoch_seconds,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("allocation_issuance_epoch_must_be_non_negative_int")
    return value


def _require_bool(value: bool, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_bool")
    return value


def _require_decimal_amount(value: Decimal | int | str, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not amount.is_finite():
        raise ValueError(f"{field_name}_must_be_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{field_name}_must_be_non_negative")
    if amount.adjusted() > MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return amount


def _normalize_upheld_refutation_recipients(
    upheld_refutation_recipients: list[str] | None,
) -> tuple[str, ...]:
    if upheld_refutation_recipients is None:
        return ()
    if not isinstance(upheld_refutation_recipients, list):
        raise ValueError("upheld_refutation_recipients_must_be_list_or_none")
    if len(upheld_refutation_recipients) > MAX_UPHELD_REFUTATION_RECIPIENTS:
        raise ValueError("upheld_refutation_recipients_exceeds_max_count")
    normalized: list[str] = []
    seen: set[str] = set()
    for recipient in upheld_refutation_recipients:
        if not isinstance(recipient, str) or not recipient:
            raise ValueError("upheld_refutation_recipient_must_be_non_empty_string")
        if len(recipient.encode("utf-8")) > MAX_UPHELD_REFUTATION_RECIPIENT_ID_BYTES:
            raise ValueError("upheld_refutation_recipient_id_exceeds_max_bytes")
        if recipient in seen:
            raise ValueError("upheld_refutation_recipients_must_be_unique")
        seen.add(recipient)
        normalized.append(recipient)
    return tuple(sorted(normalized))


def _quantize_ilc(value: Decimal) -> Decimal:
    if value.adjusted() > MAX_ILC_QUANTIZE_ADJUSTED_EXPONENT:
        raise ValueError(INVALID_AMOUNT_MAGNITUDE_TOKEN)
    return value.quantize(ILC_QUANTUM, rounding=ROUND_DOWN)


def _split_residual_among_refutation_recipients(
    residual: Decimal,
    recipients: tuple[str, ...],
) -> tuple[tuple[str, Decimal], ...]:
    if not recipients:
        return ()
    if residual == Decimal("0"):
        return tuple((recipient, Decimal("0")) for recipient in recipients)
    quantum_count = int(residual / ILC_QUANTUM)
    base_quanta, remainder_quanta = divmod(quantum_count, len(recipients))
    allocations: list[tuple[str, Decimal]] = []
    for index, recipient in enumerate(recipients):
        recipient_quanta = base_quanta + (1 if index < remainder_quanta else 0)
        allocations.append((recipient, ILC_QUANTUM * recipient_quanta))
    allocated = sum((amount for _, amount in allocations), Decimal("0"))
    if allocated != residual:
        raise ValueError("rounding_residual_refutation_allocation_mismatch_phase_1440")
    return tuple(allocations)


def _decimal_to_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def require_cdl_029_allocation_fractions(
    performer_fraction: Decimal | int | str = PERFORMER_ALLOCATION_FRACTION,
    auditor_fraction: Decimal | int | str = AUDITOR_ALLOCATION_FRACTION,
    genesis_overhead_fraction: Decimal | int | str = GENESIS_OVERHEAD_ALLOCATION_FRACTION,
) -> tuple[Decimal, Decimal, Decimal]:
    performer = _require_decimal_amount(performer_fraction, "performer_fraction")
    auditor = _require_decimal_amount(auditor_fraction, "auditor_fraction")
    genesis_overhead = _require_decimal_amount(
        genesis_overhead_fraction,
        "genesis_overhead_fraction",
    )
    if performer + auditor + genesis_overhead != ALLOCATION_FRACTION_TOTAL:
        raise ValueError("allocation_fractions_must_sum_to_one")
    if (
        performer != PERFORMER_ALLOCATION_FRACTION
        or auditor != AUDITOR_ALLOCATION_FRACTION
        or genesis_overhead != GENESIS_OVERHEAD_ALLOCATION_FRACTION
    ):
        raise ValueError("allocation_fractions_must_equal_cdl_029_80_15_5")
    return performer, auditor, genesis_overhead


def build_allocation_distribution_quote(
    issuance_epoch: int,
    total_epoch_allocation_ilc: Decimal | int | str,
    *,
    performer_fraction: Decimal | int | str = PERFORMER_ALLOCATION_FRACTION,
    auditor_fraction: Decimal | int | str = AUDITOR_ALLOCATION_FRACTION,
    genesis_overhead_fraction: Decimal | int | str = GENESIS_OVERHEAD_ALLOCATION_FRACTION,
    genesis_overhead_cap_blocked: bool = False,
    upheld_refutation_recipients: list[str] | None = None,
) -> EpochAllocationDistributionQuote:
    epoch = _require_epoch_sequence(issuance_epoch)
    cap_blocked = _require_bool(genesis_overhead_cap_blocked, "genesis_overhead_cap_blocked")
    refutation_recipients = _normalize_upheld_refutation_recipients(upheld_refutation_recipients)
    total_allocation = _quantize_ilc(
        _require_decimal_amount(total_epoch_allocation_ilc, "total_epoch_allocation_ilc")
    )
    performer, auditor, genesis_overhead = require_cdl_029_allocation_fractions(
        performer_fraction,
        auditor_fraction,
        genesis_overhead_fraction,
    )

    performer_pool = _quantize_ilc(total_allocation * performer)
    auditor_pool = _quantize_ilc(total_allocation * auditor)
    genesis_overhead_base = _quantize_ilc(total_allocation * genesis_overhead)
    rounding_residual = total_allocation - performer_pool - auditor_pool - genesis_overhead_base
    residual_to_genesis = Decimal("0")
    residual_to_refutation_recipients = Decimal("0")
    residual_to_performer = Decimal("0")
    residual_refutation_recipient_allocations: tuple[tuple[str, Decimal], ...] = ()
    residual_route = GENESIS_RESIDUAL_ROUTE
    if cap_blocked:
        if genesis_overhead_base != Decimal("0"):
            raise ValueError(GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN)
        genesis_overhead_pool = Decimal("0")
        if refutation_recipients:
            residual_to_refutation_recipients = rounding_residual
            residual_refutation_recipient_allocations = (
                _split_residual_among_refutation_recipients(
                    rounding_residual,
                    refutation_recipients,
                )
            )
            residual_route = UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE
        else:
            residual_to_performer = rounding_residual
            performer_pool += rounding_residual
            residual_route = PERFORMER_POOL_RESIDUAL_ROUTE
    else:
        residual_to_genesis = rounding_residual
        genesis_overhead_pool = genesis_overhead_base + rounding_residual

    return EpochAllocationDistributionQuote(
        runtime_version=ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION,
        cdl_029_dependency=CDL_029_DEPENDENCY,
        issuance_epoch=epoch,
        issuance_epoch_duration=ISSUANCE_EPOCH_DURATION,
        validation_epoch_seconds=VALIDATION_EPOCH_SECONDS,
        total_epoch_allocation_ilc=total_allocation,
        performer_fraction=performer,
        auditor_fraction=auditor,
        genesis_overhead_fraction=genesis_overhead,
        theta_hard_continuity_fraction=THETA_HARD_CONTINUITY_FRACTION,
        performer_reward_pool_ilc=performer_pool,
        auditor_reward_pool_ilc=auditor_pool,
        genesis_overhead_pool_ilc=genesis_overhead_pool,
        rounding_residual_to_genesis_overhead_ilc=residual_to_genesis,
        rounding_residual_to_upheld_refutation_recipients_ilc=residual_to_refutation_recipients,
        rounding_residual_to_performer_pool_ilc=residual_to_performer,
        rounding_residual_refutation_recipient_allocations_ilc=(
            residual_refutation_recipient_allocations
        ),
        genesis_overhead_cap_blocked=cap_blocked,
        residual_route=residual_route,
        upheld_refutation_recipients=refutation_recipients,
        performer_reward_pool_label=PERFORMER_REWARD_POOL_LABEL,
        auditor_reward_pool_label=AUDITOR_REWARD_POOL_LABEL,
        genesis_overhead_pool_label=GENESIS_OVERHEAD_POOL_LABEL,
        post_theta_hard_routing_token=(
            POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN
            if cap_blocked
            else PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN
        ),
        split_quote_boundary_token=SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN,
        production_allocation_distribution_activated=False,
        decision_token=PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN,
    )


def require_production_allocation_distribution_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token != PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_allocation_distribution_activation_not_implemented_phase_1347")


__all__ = [
    "ALLOCATION_80_15_5_ROUTING_TOKEN",
    "ALLOCATION_DISTRIBUTOR_RUNTIME_VERSION",
    "ALLOCATION_FRACTION_TOTAL",
    "AUDITOR_ALLOCATION_FRACTION",
    "AUDITOR_REWARD_POOL_LABEL",
    "CDL_029_AMENDMENT_PHASE_1351A_TOKEN",
    "CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN",
    "CDL_029_DEPENDENCY",
    "CDL_029_POST_THETA_HARD_ROUTING_AMENDMENT_TOKEN",
    "CDL_029_POST_THETA_HARD_ROUTING_GOVERNOR_WIRED_TOKEN",
    "CDL_029_POST_THETA_HARD_ROUTING_IMPLEMENTATION_DEFERRED_TOKEN",
    "CDL_083_UPHELD_REFUTATION_RECIPIENTS_PRIMARY_DUST_ROUTE_TOKEN",
    "FINDING_1_ROUNDING_RESIDUAL_CAP_BLOCKED_RESOLVED_TOKEN",
    "GENESIS_OVERHEAD_ALLOCATION_FRACTION",
    "GENESIS_OVERHEAD_BASE_CAP_BLOCKED_FULL_TRANCHE_DEFERRED_TOKEN",
    "GENESIS_OVERHEAD_CAP_BLOCKED_DUST_ROUTING_DEFERRED_TOKEN",
    "GENESIS_OVERHEAD_CAP_BLOCKED_GUARD_TOKEN",
    "GENESIS_OVERHEAD_POOL_LABEL",
    "GENESIS_RESIDUAL_ROUTE",
    "MAX_UPHELD_REFUTATION_RECIPIENT_ID_BYTES",
    "MAX_UPHELD_REFUTATION_RECIPIENTS",
    "NO_DIRECT_ALLOCATION_STUB_FOUND_TOKEN",
    "PERFORMER_ALLOCATION_FRACTION",
    "PERFORMER_POOL_FALLBACK_DUST_ROUTE_TOKEN",
    "PERFORMER_POOL_RESIDUAL_ROUTE",
    "PERFORMER_REWARD_POOL_LABEL",
    "PHASE_1345_EMISSION_RUNTIME_DEPENDENCY",
    "PHASE_1346_FEE_BURN_RUNTIME_DEPENDENCY",
    "POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN",
    "PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN",
    "PRODUCTION_ALLOCATION_DISTRIBUTION_ACTIVATION_TOKEN",
    "PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN",
    "PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_TOKEN",
    "SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN",
    "THETA_HARD_CONTINUITY_FRACTION",
    "THETA_HARD_ILC",
    "UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE",
    "EpochAllocationDistributionQuote",
    "build_allocation_distribution_quote",
    "require_cdl_029_allocation_fractions",
    "require_production_allocation_distribution_activation",
]
