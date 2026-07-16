# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1568-Fix2q Genesis tranche quote/read-model reconciliation.

This module separates three Genesis-related value surfaces without activating
any wallet, treasury, minting, settlement, or production-emission path.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ilc_core.epoch.allocation_distributor_runtime import (
    GENESIS_OVERHEAD_ALLOCATION_FRACTION,
    GENESIS_OVERHEAD_POOL_LABEL,
    SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN,
)
from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC
from ilc_core.epoch.fee_burn_split_runtime import FEE_BURN_RATIO, GENESIS_BURN_POOL_LABEL
from ilc_core.epoch.genesis_settlement_destination import (
    CDL048_TREATMENT_APPLIED_TOKEN,
    CDL_048_GENESIS_TRANCHE_TREATMENT,
    GENESIS_DESTINATION_BINDING_TOKEN,
)
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, parse_non_negative_decimal


GENESIS_TRANCHE_RECONCILIATION_RUNTIME_VERSION = (
    "genesis_tranche_reconciliation_runtime_1568_fix2q.v0.1"
)
FIXED_GENESIS_TRANCHE_FRACTION = Decimal("0.05")
FIXED_GENESIS_TRANCHE_ILC = C_MAX_ILC * FIXED_GENESIS_TRANCHE_FRACTION

GENESIS_BURN_POOL_NOT_FIXED_TRANCHE_TOKEN = (
    "genesis_burn_pool_not_fixed_genesis_tranche_phase_1568_fix2q"
)
CDL029_OVERHEAD_NOT_FULL_TRANCHE_TOKEN = (
    "cdl029_genesis_overhead_not_full_tranche_phase_1568_fix2q"
)
CDL048_TRANCHE_TREATMENT_ABSENT_TOKEN = (
    "cdl048_conversion_quote_genesis_tranche_treatment_absent_phase_1568_fix2q"
)
GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN = (
    "genesis_tranche_realization_controller_deferred_phase_1568_fix2q"
)
GENESIS_TRANCHE_RECONCILIATION_QUOTE_ONLY_TOKEN = (
    "genesis_tranche_reconciliation_quote_read_model_only_phase_1568_fix2q"
)
FIX2Q_SURFACES_RECONCILED_TOKEN = "phase_1568_fix2q_genesis_tranche_surfaces_reconciled"

_FORBIDDEN_TRUE_FIELDS = (
    "conversion_activation_authorized",
    "ledger_write_authorized",
    "wallet_write_authorized",
    "treasury_write_authorized",
    "production_minting_authorized",
    "ilc_settlement_authorized",
    "wallet_withdrawal_enabled",
    "wallet_transfer_enabled",
    "wallet_spend_enabled",
    "ecu_mint_authorized",
)


@dataclass(frozen=True)
class GenesisTrancheReconciliationQuote:
    cmax_ilc: Decimal
    fixed_genesis_tranche_fraction: Decimal
    fixed_genesis_tranche_ilc: Decimal
    cdl028_fee_burn_ratio: Decimal
    cdl028_genesis_burn_pool_ilc: Decimal
    cdl029_genesis_overhead_fraction: Decimal
    cdl029_genesis_overhead_pool_ilc: Decimal
    cdl048_conversion_credit_ilc: Decimal
    cdl048_genesis_tranche_treatment: str
    genesis_burn_pool_is_fixed_tranche: bool
    cdl029_overhead_is_full_tranche: bool
    cdl048_applies_fixed_tranche: bool
    fixed_tranche_realized_by_current_value_path_ilc: Decimal
    fixed_tranche_unrealized_in_current_value_path_ilc: Decimal
    quote_read_model_only: bool
    wallet_write_authorized: bool
    treasury_write_authorized: bool
    production_minting_authorized: bool
    ilc_settlement_authorized: bool
    public_rc_activated: bool
    tokens: tuple[str, ...]

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cdl028_fee_burn_ratio": _decimal_to_string(self.cdl028_fee_burn_ratio),
            "cdl028_genesis_burn_pool_ilc": _decimal_to_string(
                self.cdl028_genesis_burn_pool_ilc
            ),
            "cdl028_genesis_burn_pool_is_fixed_tranche": (
                self.genesis_burn_pool_is_fixed_tranche
            ),
            "cdl028_genesis_burn_pool_label": GENESIS_BURN_POOL_LABEL,
            "cdl029_genesis_overhead_fraction": _decimal_to_string(
                self.cdl029_genesis_overhead_fraction
            ),
            "cdl029_genesis_overhead_is_full_tranche": self.cdl029_overhead_is_full_tranche,
            "cdl029_genesis_overhead_pool_ilc": _decimal_to_string(
                self.cdl029_genesis_overhead_pool_ilc
            ),
            "cdl029_genesis_overhead_pool_label": GENESIS_OVERHEAD_POOL_LABEL,
            "cdl029_split_quote_boundary_token": (
                SPLIT_QUOTE_CLARIFIED_NOT_FULL_GENESIS_TRANCHE_TOKEN
            ),
            "cdl048_applies_fixed_tranche": self.cdl048_applies_fixed_tranche,
            "cdl048_conversion_credit_ilc": _decimal_to_string(
                self.cdl048_conversion_credit_ilc
            ),
            "cdl048_genesis_tranche_treatment": self.cdl048_genesis_tranche_treatment,
            "cmax_ilc": _decimal_to_string(self.cmax_ilc),
            "fixed_genesis_tranche_fraction": _decimal_to_string(
                self.fixed_genesis_tranche_fraction
            ),
            "fixed_genesis_tranche_ilc": _decimal_to_string(
                self.fixed_genesis_tranche_ilc
            ),
            "fixed_tranche_realized_by_current_value_path_ilc": _decimal_to_string(
                self.fixed_tranche_realized_by_current_value_path_ilc
            ),
            "fixed_tranche_unrealized_in_current_value_path_ilc": _decimal_to_string(
                self.fixed_tranche_unrealized_in_current_value_path_ilc
            ),
            "ilc_settlement_authorized": self.ilc_settlement_authorized,
            "production_minting_authorized": self.production_minting_authorized,
            "public_rc_activated": self.public_rc_activated,
            "quote_read_model_only": self.quote_read_model_only,
            "runtime_version": GENESIS_TRANCHE_RECONCILIATION_RUNTIME_VERSION,
            "tokens": list(self.tokens),
            "treasury_write_authorized": self.treasury_write_authorized,
            "wallet_write_authorized": self.wallet_write_authorized,
        }


def _decimal_to_string(value: Decimal) -> str:
    return decimal_to_canonical_string(value)


def _require_record(value: Any, *, token: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(token)
    _reject_float_tree(value)
    return value


def _reject_float_tree(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("genesis_tranche_reconciliation_float_rejected")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float_tree(key)
            _reject_float_tree(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float_tree(item)


def _record_amount(record: dict[str, Any], key: str, *, token: str) -> Decimal:
    try:
        return parse_non_negative_decimal(record.get(key, "0"), token=token)
    except ValueError as exc:
        raise ValueError(token) from exc


def _assert_no_forbidden_authorization(record: dict[str, Any], *, surface: str) -> None:
    for field in _FORBIDDEN_TRUE_FIELDS:
        if record.get(field) is True:
            raise ValueError(f"{surface}_{field}_forbidden_phase_1568_fix2q")


def _assert_default_off_flag(record: dict[str, Any], field: str, *, surface: str) -> None:
    value = record.get(field)
    if value is not False:
        raise ValueError(f"{surface}_{field}_must_be_false_phase_1568_fix2q")


def _assert_label(record: dict[str, Any], field: str, expected: str, *, surface: str) -> None:
    value = record.get(field)
    if value != expected:
        raise ValueError(f"{surface}_{field}_mismatch_phase_1568_fix2q")


def _cdl048_tranche_treatment(cdl048_quote: dict[str, Any]) -> tuple[str, bool]:
    treatment = cdl048_quote.get("genesis_tranche_treatment")
    if treatment is None:
        return "absent", False
    if treatment == "explicitly_deferred":
        return "explicitly_deferred", False
    if treatment == "applied":
        raise ValueError("cdl048_legacy_applied_treatment_rejected_phase_1575c_fix3e")
    if treatment == CDL_048_GENESIS_TRANCHE_TREATMENT:
        return CDL_048_GENESIS_TRANCHE_TREATMENT, True
    raise ValueError("cdl048_genesis_tranche_treatment_invalid_phase_1568_fix2q")


def build_genesis_tranche_reconciliation_quote(
    *,
    fee_burn_quote: dict[str, Any],
    allocation_quote: dict[str, Any],
    cdl048_conversion_quote: dict[str, Any],
) -> GenesisTrancheReconciliationQuote:
    fee_record = _require_record(
        fee_burn_quote,
        token="fee_burn_quote_must_be_object_phase_1568_fix2q",
    )
    allocation_record = _require_record(
        allocation_quote,
        token="allocation_quote_must_be_object_phase_1568_fix2q",
    )
    cdl048_record = _require_record(
        cdl048_conversion_quote,
        token="cdl048_conversion_quote_must_be_object_phase_1568_fix2q",
    )

    _assert_no_forbidden_authorization(fee_record, surface="fee_burn")
    _assert_no_forbidden_authorization(allocation_record, surface="cdl029_allocation")
    _assert_no_forbidden_authorization(cdl048_record, surface="cdl048_conversion")
    _assert_default_off_flag(
        fee_record,
        "production_fee_burn_activated",
        surface="fee_burn",
    )
    _assert_default_off_flag(
        allocation_record,
        "production_allocation_distribution_activated",
        surface="cdl029_allocation",
    )
    _assert_default_off_flag(
        cdl048_record,
        "conversion_activation_authorized",
        surface="cdl048_conversion",
    )
    _assert_default_off_flag(
        cdl048_record,
        "ledger_write_authorized",
        surface="cdl048_conversion",
    )
    _assert_default_off_flag(
        cdl048_record,
        "wallet_write_authorized",
        surface="cdl048_conversion",
    )
    _assert_label(
        fee_record,
        "genesis_burn_pool_label",
        GENESIS_BURN_POOL_LABEL,
        surface="fee_burn",
    )
    _assert_label(
        allocation_record,
        "genesis_overhead_pool_label",
        GENESIS_OVERHEAD_POOL_LABEL,
        surface="cdl029_allocation",
    )

    treatment, applies_fixed_tranche = _cdl048_tranche_treatment(cdl048_record)
    realized = FIXED_GENESIS_TRANCHE_ILC if applies_fixed_tranche else Decimal("0")
    unresolved = FIXED_GENESIS_TRANCHE_ILC - realized
    if unresolved < Decimal("0"):
        raise ValueError("genesis_tranche_realization_exceeds_fixed_tranche_phase_1568_fix2q")

    tokens = [
        FIX2Q_SURFACES_RECONCILED_TOKEN,
        GENESIS_BURN_POOL_NOT_FIXED_TRANCHE_TOKEN,
        CDL029_OVERHEAD_NOT_FULL_TRANCHE_TOKEN,
        GENESIS_TRANCHE_RECONCILIATION_QUOTE_ONLY_TOKEN,
        GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN,
    ]
    if treatment == "absent":
        tokens.append(CDL048_TRANCHE_TREATMENT_ABSENT_TOKEN)
    if treatment == CDL_048_GENESIS_TRANCHE_TREATMENT:
        tokens.append(CDL048_TREATMENT_APPLIED_TOKEN)
        tokens.append(GENESIS_DESTINATION_BINDING_TOKEN)

    fee_burn_ratio = _record_amount(
        fee_record,
        "fee_burn_ratio",
        token="fee_burn_ratio_invalid_phase_1568_fix2q",
    )
    if fee_burn_ratio != FEE_BURN_RATIO:
        raise ValueError("fee_burn_ratio_mismatch_phase_1568_fix2q")
    genesis_overhead_fraction = _record_amount(
        allocation_record,
        "genesis_overhead_fraction",
        token="genesis_overhead_fraction_invalid_phase_1568_fix2q",
    )
    if genesis_overhead_fraction != GENESIS_OVERHEAD_ALLOCATION_FRACTION:
        raise ValueError("cdl029_genesis_overhead_fraction_mismatch_phase_1568_fix2q")

    return GenesisTrancheReconciliationQuote(
        cmax_ilc=C_MAX_ILC,
        fixed_genesis_tranche_fraction=FIXED_GENESIS_TRANCHE_FRACTION,
        fixed_genesis_tranche_ilc=FIXED_GENESIS_TRANCHE_ILC,
        cdl028_fee_burn_ratio=fee_burn_ratio,
        cdl028_genesis_burn_pool_ilc=_record_amount(
            fee_record,
            "genesis_burn_pool_ilc",
            token="genesis_burn_pool_ilc_invalid_phase_1568_fix2q",
        ),
        cdl029_genesis_overhead_fraction=genesis_overhead_fraction,
        cdl029_genesis_overhead_pool_ilc=_record_amount(
            allocation_record,
            "genesis_overhead_pool_ilc",
            token="genesis_overhead_pool_ilc_invalid_phase_1568_fix2q",
        ),
        cdl048_conversion_credit_ilc=_record_amount(
            cdl048_record,
            "amount_ilc_credit",
            token="cdl048_amount_ilc_credit_invalid_phase_1568_fix2q",
        ),
        cdl048_genesis_tranche_treatment=treatment,
        genesis_burn_pool_is_fixed_tranche=False,
        cdl029_overhead_is_full_tranche=False,
        cdl048_applies_fixed_tranche=applies_fixed_tranche,
        fixed_tranche_realized_by_current_value_path_ilc=realized,
        fixed_tranche_unrealized_in_current_value_path_ilc=unresolved,
        quote_read_model_only=True,
        wallet_write_authorized=False,
        treasury_write_authorized=False,
        production_minting_authorized=False,
        ilc_settlement_authorized=False,
        public_rc_activated=False,
        tokens=tuple(tokens),
    )


def build_genesis_tranche_reconciliation_from_rehearsal_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    rehearsal_record = _require_record(
        record,
        token="rehearsal_economics_record_must_be_object_phase_1568_fix2q",
    )
    epoch_emission_result = _require_record(
        rehearsal_record.get("epoch_emission_result"),
        token="epoch_emission_result_must_be_object_phase_1568_fix2q",
    )
    quote = build_genesis_tranche_reconciliation_quote(
        fee_burn_quote=_require_record(
            epoch_emission_result.get("fee_burn_quote"),
            token="fee_burn_quote_must_be_object_phase_1568_fix2q",
        ),
        allocation_quote=_require_record(
            rehearsal_record.get("allocation_quote"),
            token="allocation_quote_must_be_object_phase_1568_fix2q",
        ),
        cdl048_conversion_quote=_require_record(
            rehearsal_record.get("cdl048_conversion_quote"),
            token="cdl048_conversion_quote_must_be_object_phase_1568_fix2q",
        ),
    )
    return quote.to_canonical_record()


def verify_genesis_tranche_reconciliation_record(record: dict[str, Any]) -> dict[str, Any]:
    quote = _require_record(
        record,
        token="genesis_tranche_reconciliation_must_be_object_phase_1568_fix2q",
    )
    _assert_no_forbidden_authorization(quote, surface="genesis_tranche_reconciliation")
    if quote.get("quote_read_model_only") is not True:
        raise ValueError("quote_read_model_only_must_be_true_phase_1568_fix2q")
    for field in (
        "cdl028_genesis_burn_pool_is_fixed_tranche",
        "cdl029_genesis_overhead_is_full_tranche",
    ):
        if quote.get(field) is not False:
            raise ValueError(f"{field}_must_be_false_phase_1568_fix2q")
    if not isinstance(quote.get("cdl048_applies_fixed_tranche"), bool):
        raise ValueError("cdl048_applies_fixed_tranche_must_be_bool_phase_1568_fix2q")
    for field in (
        "wallet_write_authorized",
        "treasury_write_authorized",
        "production_minting_authorized",
        "ilc_settlement_authorized",
        "public_rc_activated",
    ):
        if quote.get(field) is not False:
            raise ValueError(f"{field}_must_be_false_phase_1568_fix2q")

    if quote.get("cmax_ilc") != _decimal_to_string(C_MAX_ILC):
        raise ValueError("genesis_tranche_cmax_mismatch_phase_1568_fix2q")
    if quote.get("fixed_genesis_tranche_fraction") != _decimal_to_string(
        FIXED_GENESIS_TRANCHE_FRACTION
    ):
        raise ValueError("genesis_tranche_fraction_mismatch_phase_1568_fix2q")
    if quote.get("fixed_genesis_tranche_ilc") != _decimal_to_string(
        FIXED_GENESIS_TRANCHE_ILC
    ):
        raise ValueError("genesis_tranche_amount_mismatch_phase_1568_fix2q")
    if quote.get("cdl028_fee_burn_ratio") != _decimal_to_string(FEE_BURN_RATIO):
        raise ValueError("fee_burn_ratio_mismatch_phase_1568_fix2q")
    if quote.get("cdl029_genesis_overhead_fraction") != _decimal_to_string(
        GENESIS_OVERHEAD_ALLOCATION_FRACTION
    ):
        raise ValueError("cdl029_genesis_overhead_fraction_mismatch_phase_1568_fix2q")

    tokens = quote.get("tokens")
    if not isinstance(tokens, list):
        raise ValueError("genesis_tranche_reconciliation_tokens_invalid_phase_1568_fix2q")
    required_tokens = {
        FIX2Q_SURFACES_RECONCILED_TOKEN,
        GENESIS_BURN_POOL_NOT_FIXED_TRANCHE_TOKEN,
        CDL029_OVERHEAD_NOT_FULL_TRANCHE_TOKEN,
        GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN,
        GENESIS_TRANCHE_RECONCILIATION_QUOTE_ONLY_TOKEN,
    }
    if not required_tokens.issubset(set(tokens)):
        raise ValueError("genesis_tranche_reconciliation_tokens_missing_phase_1568_fix2q")
    token_set = set(tokens)
    if quote.get("cdl048_applies_fixed_tranche") is True and quote.get(
        "cdl048_genesis_tranche_treatment"
    ) != CDL_048_GENESIS_TRANCHE_TREATMENT:
        raise ValueError("cdl048_fixed_tranche_requires_fix3e_treatment")
    if quote.get("cdl048_genesis_tranche_treatment") == CDL_048_GENESIS_TRANCHE_TREATMENT:
        if quote.get("cdl048_applies_fixed_tranche") is not True:
            raise ValueError("cdl048_applied_treatment_must_apply_fixed_tranche")
        if not {
            CDL048_TREATMENT_APPLIED_TOKEN,
            GENESIS_DESTINATION_BINDING_TOKEN,
        }.issubset(token_set):
            raise ValueError("genesis_destination_binding_tokens_missing_phase_1575c_fix3e")

    return {
        "cdl028_genesis_burn_pool_is_fixed_tranche": False,
        "cdl029_genesis_overhead_is_full_tranche": False,
        "cdl048_applies_fixed_tranche": quote["cdl048_applies_fixed_tranche"],
        "fixed_genesis_tranche_ilc": quote["fixed_genesis_tranche_ilc"],
        "marker": "phase_1568_fix2q_genesis_tranche_reconciliation_verified",
        "quote_read_model_only": True,
        "runtime_version": GENESIS_TRANCHE_RECONCILIATION_RUNTIME_VERSION,
        "verified": True,
        "wallet_write_authorized": False,
        "treasury_write_authorized": False,
    }


__all__ = [
    "CDL029_OVERHEAD_NOT_FULL_TRANCHE_TOKEN",
    "CDL048_TREATMENT_APPLIED_TOKEN",
    "CDL048_TRANCHE_TREATMENT_ABSENT_TOKEN",
    "CDL_048_GENESIS_TRANCHE_TREATMENT",
    "FIX2Q_SURFACES_RECONCILED_TOKEN",
    "FIXED_GENESIS_TRANCHE_FRACTION",
    "FIXED_GENESIS_TRANCHE_ILC",
    "GENESIS_BURN_POOL_NOT_FIXED_TRANCHE_TOKEN",
    "GENESIS_DESTINATION_BINDING_TOKEN",
    "GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN",
    "GENESIS_TRANCHE_RECONCILIATION_QUOTE_ONLY_TOKEN",
    "GENESIS_TRANCHE_RECONCILIATION_RUNTIME_VERSION",
    "GenesisTrancheReconciliationQuote",
    "build_genesis_tranche_reconciliation_from_rehearsal_record",
    "build_genesis_tranche_reconciliation_quote",
    "verify_genesis_tranche_reconciliation_record",
]
