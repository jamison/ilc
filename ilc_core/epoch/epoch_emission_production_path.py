# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1532p default-off emission production path.

PRODUCTION_EMISSION_NOT_ACTIVATED was cleared by Phase 1575g economic guard
clearance. This path computes production emission records but still performs no
ledger, wallet, treasury, minting, settlement, or epoch-transition writes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from ilc_core.analysis.genesis_accrual_governor import (
    GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN,
    evaluate_genesis_accrual_governor,
)
from ilc_core.epoch.allocation_distributor_runtime import (
    CDL_029_DEPENDENCY,
    EpochAllocationDistributionQuote,
    build_allocation_distribution_quote,
)
from ilc_core.epoch.epoch_emission_runtime import (
    CDL_025_DEPENDENCY,
    CDL_025_EMISSION_SCHEDULE_RUNTIME_TOKEN,
    CDL_026_DEPENDENCY,
    CDL_026_CMAX_CAP_RUNTIME_TOKEN,
    CDL_027_DEPENDENCY,
    CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
    C_MAX_ILC,
    EpochEmissionQuote,
    build_epoch_emission_quote,
)
from ilc_core.epoch.fee_burn_split_runtime import (
    CDL_028_DEPENDENCY,
    EpochFeeBurnSplitQuote,
    build_fee_burn_split_quote,
)
from ilc_core.epoch.issuance_economics_integration_gate import (
    ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS,
    IssuanceEconomicsIntegrationGateReport,
    verify_issuance_economics_integration_gate,
)

PRODUCTION_EMISSION_NOT_ACTIVATED = False  # cleared by Phase 1575g economic guard clearance
PRODUCTION_EMISSION_NOT_ACTIVATED_TOKEN = "PRODUCTION_EMISSION_NOT_ACTIVATED"
GENESIS_GOVERNOR_WIRING_TOKEN = (
    "genesis_governor_wired_into_production_path_1575c_fix3d.v0.1"
)
GENESIS_GOVERNOR_WIRING_DEPENDENCY = GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN
CANONICAL_ECONOMIC_EVENT_RECORD_SCHEMA_VERSION = "canonical_economic_event_record_1537p_fix1.v0.2"
SCHEDULED_EMISSION_POOL_ROLE = "scheduled_emission_pool"
PERFORMER_POOL_ROLE = "performer_pool"
AUDITOR_POOL_ROLE = "auditor_pool"
GENESIS_OVERHEAD_POOL_ROLE = "genesis_overhead_pool"
GENESIS_BURN_POOL_ROLE = "genesis_burn_pool"
CANONICAL_ECONOMIC_EVENT_ROLES = [
    SCHEDULED_EMISSION_POOL_ROLE,
    PERFORMER_POOL_ROLE,
    AUDITOR_POOL_ROLE,
    GENESIS_OVERHEAD_POOL_ROLE,
    GENESIS_BURN_POOL_ROLE,
]
GENESIS_FIXED_TRANCHE_FRACTION = Decimal("0.05")
GENESIS_FIXED_TRANCHE_ILC = C_MAX_ILC * GENESIS_FIXED_TRANCHE_FRACTION
CDL_EMISSION_AUTHORITY_TOKENS = [
    CDL_025_EMISSION_SCHEDULE_RUNTIME_TOKEN,
    CDL_026_CMAX_CAP_RUNTIME_TOKEN,
    CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
    CDL_028_DEPENDENCY,
    CDL_029_DEPENDENCY,
]
CDL_ECONOMIC_EVENT_AUTHORITY_TOKENS = [
    CDL_025_DEPENDENCY,
    CDL_026_DEPENDENCY,
    CDL_027_DEPENDENCY,
    CDL_028_DEPENDENCY,
    CDL_029_DEPENDENCY,
]
SETTLEMENT_ROOT_SCHEMA_VERSION = "epoch_emission_event_batch_root_1537p_fix1.v0.2"


@dataclass(frozen=True)
class EpochEmissionProductionResult:
    issuance_epoch: int
    gate_report: IssuanceEconomicsIntegrationGateReport
    emission_quote: EpochEmissionQuote
    fee_burn_quote: EpochFeeBurnSplitQuote
    allocation_quote: EpochAllocationDistributionQuote
    production_emission_activated: bool
    guard_token: str
    governor_report: dict[str, str | bool] | None

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "allocation_quote": self.allocation_quote.to_canonical_record(),
            "authority_tokens": list(CDL_EMISSION_AUTHORITY_TOKENS),
            "emission_quote": self.emission_quote.to_canonical_record(),
            "fee_burn_quote": self.fee_burn_quote.to_canonical_record(),
            "gate_report": self.gate_report.to_canonical_record(),
            "guard_token": self.guard_token,
            "governor_report": self.governor_report,
            "issuance_epoch": self.issuance_epoch,
            "production_emission_activated": self.production_emission_activated,
        }


@dataclass(frozen=True)
class EpochSettlementRoot:
    """SHA-256 over compact canonical JSON for an epoch economic event batch.

    The hash input is UTF-8 encoded JSON rendered with ``sort_keys=True``,
    ``separators=(",", ":")``, ``allow_nan=False``, and ``ensure_ascii=True``.
    The input commits to canonical economic event payloads excluding any
    ``settlement_root_hex`` field to avoid circularity.
    """

    issuance_epoch: int
    canonical_record_json: str
    root_hex: str
    root_algorithm: str = "sha256_over_canonical_json"

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "canonical_record_json": self.canonical_record_json,
            "issuance_epoch": self.issuance_epoch,
            "root_algorithm": self.root_algorithm,
            "root_hex": self.root_hex,
        }


def _require_epoch_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("issuance_epoch_must_be_non_negative_int")
    return value


def _require_exact_decimal(value: Decimal | int | str, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    if isinstance(value, float):
        raise ValueError("float_input_rejected")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal") from exc
    if not amount.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{field_name}_must_be_non_negative")
    return amount


def _decimal_to_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _ratio_to_canonical_string(value: Decimal) -> str:
    if not isinstance(value, Decimal):
        raise ValueError("governor_ratio_must_be_decimal")
    if not value.is_finite():
        raise ValueError("governor_ratio_must_be_finite")
    return format(value.normalize(), "f")


def _canonical_governor_report(report: dict[str, object]) -> dict[str, str | bool]:
    return {
        "cap_blocked": bool(report["cap_blocked"]),
        "genesis_share_ratio": _ratio_to_canonical_string(report["genesis_share_ratio"]),
        "taper_multiplier": _ratio_to_canonical_string(report["taper_multiplier"]),
    }


def _require_event_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_economic_event_rejected")
    if not isinstance(value, Decimal):
        raise ValueError(f"{field_name}_must_be_decimal")
    if not value.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if value < Decimal("0"):
        raise ValueError(f"{field_name}_must_be_non_negative")
    return value


def _require_production_emission_activated(value: object) -> bool:
    if not isinstance(value, bool):
        raise ValueError("canonical_economic_event_activation_flag_invalid")
    return value


def _reject_non_json_exact_values(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_record_rejected")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("invalid_amount_non_finite")
        return
    if is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            _reject_non_json_exact_values(getattr(value, field.name))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_non_json_exact_values(key)
            _reject_non_json_exact_values(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_non_json_exact_values(item)


def _reject_settlement_root_key(value: Any) -> None:
    if isinstance(value, dict):
        if "settlement_root_hex" in value:
            raise ValueError("settlement_root_hex_must_be_excluded_from_root_payload")
        for item in value.values():
            _reject_settlement_root_key(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_settlement_root_key(item)


def _canonical_json(payload: dict[str, Any]) -> str:
    _reject_non_json_exact_values(payload)
    _reject_settlement_root_key(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    )


def build_canonical_economic_event_payloads(
    result: EpochEmissionProductionResult,
) -> list[dict[str, object]]:
    """Build event payloads that are committed by the settlement root.

    These payloads intentionally exclude ``settlement_root_hex``. The root is
    computed over this batch first; the hex root is injected into the final event
    records later by ``canonical_economic_event.emit_canonical_economic_event_records``.
    """

    if not isinstance(result, EpochEmissionProductionResult):
        raise ValueError("epoch_emission_production_result_required")

    allocation = result.allocation_quote
    fee_burn = result.fee_burn_quote
    emission = result.emission_quote
    issuance_epoch = _require_epoch_sequence(result.issuance_epoch)
    production_emission_activated = _require_production_emission_activated(
        result.production_emission_activated
    )
    event_specs = [
        (SCHEDULED_EMISSION_POOL_ROLE, emission.capped_epoch_budget_ilc),
        (PERFORMER_POOL_ROLE, allocation.performer_reward_pool_ilc),
        (AUDITOR_POOL_ROLE, allocation.auditor_reward_pool_ilc),
        (GENESIS_OVERHEAD_POOL_ROLE, allocation.genesis_overhead_pool_ilc),
        (GENESIS_BURN_POOL_ROLE, fee_burn.genesis_burn_pool_ilc),
    ]
    return [
        {
            "amount_ilc_str": _decimal_to_string(_require_event_decimal(amount, role)),
            "cdl_authority": sorted(CDL_ECONOMIC_EVENT_AUTHORITY_TOKENS),
            "issuance_epoch": issuance_epoch,
            "production_emission_activated": production_emission_activated,
            "role": role,
            "schema_version": CANONICAL_ECONOMIC_EVENT_RECORD_SCHEMA_VERSION,
        }
        for role, amount in event_specs
    ]


def _rounding_residual_metadata(result: EpochEmissionProductionResult) -> dict[str, object]:
    allocation = result.allocation_quote
    return {
        "recipient_allocations_ilc": [
            {
                "amount_ilc": _decimal_to_string(
                    _require_event_decimal(amount, "rounding_residual_recipient_amount")
                ),
                "recipient": recipient,
            }
            for recipient, amount in allocation.rounding_residual_refutation_recipient_allocations_ilc
        ],
        "residual_route": allocation.residual_route,
        "to_genesis_overhead_ilc": _decimal_to_string(
            _require_event_decimal(
                allocation.rounding_residual_to_genesis_overhead_ilc,
                "rounding_residual_to_genesis_overhead_ilc",
            )
        ),
        "to_performer_pool_ilc": _decimal_to_string(
            _require_event_decimal(
                allocation.rounding_residual_to_performer_pool_ilc,
                "rounding_residual_to_performer_pool_ilc",
            )
        ),
        "to_upheld_refutation_recipients_ilc": _decimal_to_string(
            _require_event_decimal(
                allocation.rounding_residual_to_upheld_refutation_recipients_ilc,
                "rounding_residual_to_upheld_refutation_recipients_ilc",
            )
        ),
    }


def compute_epoch_emission_production_path(
    issuance_epoch: int,
    cumulative_issued_before_epoch_ilc: Decimal | int | str,
    total_epoch_fees_ilc: Decimal | int | str,
    *,
    genesis_cumulative_accrual_ilc: Decimal | int | str | None = None,
    _test_only_genesis_cap_blocked_override: bool | None = None,
    upheld_refutation_recipients: list[str] | None = None,
) -> EpochEmissionProductionResult:
    """Compute the input-specific default-off emission quote bundle and ILC pool amounts.

    Calls ``verify_issuance_economics_integration_gate()`` from Phase 1352 as a
    preflight conservation check, then computes caller-specific emission,
    fee-burn, and allocation quotes from the supplied inputs. Phase 1575g
    cleared the computation-path guard, so the result now reports
    ``production_emission_activated=True``. This function still makes no ledger
    writes, wallet writes, or treasury writes. Outputs are ILC pool amounts, not
    per-node ECU credit amounts.
    """

    epoch = _require_epoch_sequence(issuance_epoch)
    cumulative = _require_exact_decimal(
        cumulative_issued_before_epoch_ilc,
        "cumulative_issued_before_epoch_ilc",
    )
    total_fees = _require_exact_decimal(total_epoch_fees_ilc, "total_epoch_fees_ilc")

    governor_report: dict[str, str | bool] | None = None
    genesis_overhead_remaining_allowance_ilc: Decimal | None = None
    if genesis_cumulative_accrual_ilc is not None:
        accrual = _require_exact_decimal(
            genesis_cumulative_accrual_ilc,
            "genesis_cumulative_accrual_ilc",
        )
        genesis_overhead_remaining_allowance_ilc = max(
            Decimal("0"),
            GENESIS_FIXED_TRANCHE_ILC - accrual,
        )
        raw_governor_report = evaluate_genesis_accrual_governor(
            {
                "genesis_cumulative_accrual": accrual,
                "total_cumulative_issuance": cumulative,
            }
        )
        governor_report = _canonical_governor_report(raw_governor_report)
        genesis_overhead_cap_blocked = bool(governor_report["cap_blocked"])
    elif _test_only_genesis_cap_blocked_override is not None:
        if not isinstance(_test_only_genesis_cap_blocked_override, bool):
            raise ValueError("_test_only_genesis_cap_blocked_override_must_be_bool")
        genesis_overhead_cap_blocked = _test_only_genesis_cap_blocked_override
    else:
        genesis_overhead_cap_blocked = False

    gate_report = verify_issuance_economics_integration_gate()
    if gate_report.verdict != ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS:
        raise ValueError("issuance_economics_integration_gate_not_passed")

    emission_quote = build_epoch_emission_quote(epoch, cumulative)
    fee_burn_quote = build_fee_burn_split_quote(epoch, total_fees)
    allocation_quote = build_allocation_distribution_quote(
        epoch,
        fee_burn_quote.remaining_fee_pool_ilc,
        genesis_overhead_cap_blocked=genesis_overhead_cap_blocked,
        genesis_overhead_remaining_allowance_ilc=genesis_overhead_remaining_allowance_ilc,
        upheld_refutation_recipients=upheld_refutation_recipients,
    )

    return EpochEmissionProductionResult(
        issuance_epoch=epoch,
        gate_report=gate_report,
        emission_quote=emission_quote,
        fee_burn_quote=fee_burn_quote,
        allocation_quote=allocation_quote,
        production_emission_activated=not PRODUCTION_EMISSION_NOT_ACTIVATED,
        guard_token=PRODUCTION_EMISSION_NOT_ACTIVATED_TOKEN,
        governor_report=governor_report,
    )


def compute_settlement_root(result: EpochEmissionProductionResult) -> EpochSettlementRoot:
    """Produce a deterministic settlement root for an epoch economic event batch.

    The settlement root is a pure hash commitment over canonical economic event
    payloads excluding ``settlement_root_hex``. It can feed later ``commit.epoch``
    infrastructure. It does not write ledger, wallet, treasury, graph, or
    external state.
    """

    if not isinstance(result, EpochEmissionProductionResult):
        raise ValueError("epoch_emission_production_result_required")
    _reject_non_json_exact_values(result)

    payload = {
        "authority_tokens": list(CDL_EMISSION_AUTHORITY_TOKENS),
        "economic_event_payloads": build_canonical_economic_event_payloads(result),
        "gate_report": {
            "gate_token": result.gate_report.gate_token,
            "invariant_token": result.gate_report.invariant_token,
            "quote_scope_token": result.gate_report.quote_scope_token,
            "stack_token": result.gate_report.stack_token,
            "verdict": result.gate_report.verdict,
            "verdict_token": result.gate_report.verdict_token,
        },
        "guard_token": result.guard_token,
        "issuance_epoch": result.issuance_epoch,
        "production_emission_activated": result.production_emission_activated,
        "rounding_residual_metadata": _rounding_residual_metadata(result),
        "schema_version": SETTLEMENT_ROOT_SCHEMA_VERSION,
    }
    canonical_record_json = _canonical_json(payload)
    root_hex = hashlib.sha256(canonical_record_json.encode("utf-8")).hexdigest()
    return EpochSettlementRoot(
        issuance_epoch=result.issuance_epoch,
        canonical_record_json=canonical_record_json,
        root_hex=root_hex,
    )


__all__ = [
    "CDL_EMISSION_AUTHORITY_TOKENS",
    "CDL_ECONOMIC_EVENT_AUTHORITY_TOKENS",
    "CANONICAL_ECONOMIC_EVENT_RECORD_SCHEMA_VERSION",
    "CANONICAL_ECONOMIC_EVENT_ROLES",
    "SCHEDULED_EMISSION_POOL_ROLE",
    "PRODUCTION_EMISSION_NOT_ACTIVATED",
    "PRODUCTION_EMISSION_NOT_ACTIVATED_TOKEN",
    "GENESIS_GOVERNOR_WIRING_DEPENDENCY",
    "GENESIS_GOVERNOR_WIRING_TOKEN",
    "GENESIS_FIXED_TRANCHE_ILC",
    "SETTLEMENT_ROOT_SCHEMA_VERSION",
    "EpochEmissionProductionResult",
    "EpochSettlementRoot",
    "build_canonical_economic_event_payloads",
    "compute_epoch_emission_production_path",
    "compute_settlement_root",
]
