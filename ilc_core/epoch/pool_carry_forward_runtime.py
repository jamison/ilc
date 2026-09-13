# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-029 performer/auditor unallocated pool carry-forward accounts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC, ILC_QUANTUM
from ilc_core.ledger.exact_numeric import ZERO, decimal_to_canonical_string


POOL_CARRY_FORWARD_RUNTIME_VERSION = (
    "pool_carry_forward_runtime_GAP_PUBLIC_RC_DISTRIBUTION_CARRYFORWARD_00.v0.1"
)
CDL_029_ALLOCATION_DEPENDENCY = "cdl_029_allocation_distributor_runtime_phase_1347.v0.1"

PERFORMER_CARRY_FORWARD_ACCOUNT_ID = "pool:cdl029:performer_unallocated_carry_forward"
AUDITOR_CARRY_FORWARD_ACCOUNT_ID = "pool:cdl029:auditor_unallocated_carry_forward"

CARRY_FORWARD_TRANSFER_ENABLED = False
CARRY_FORWARD_WITHDRAWAL_ENABLED = False
CARRY_FORWARD_CLAIM_ENABLED = False
CARRY_FORWARD_SPEND_ENABLED = False

POOL_CARRY_FORWARD_RUNTIME_CREATED_TOKEN = (
    "pool_carry_forward_runtime_created_GAP_PUBLIC_RC_DISTRIBUTION_CARRYFORWARD_00"
)
PERFORMER_CARRY_FORWARD_ACCOUNT_DEFINED_TOKEN = (
    "performer_carry_forward_account_defined_GAP_PUBLIC_RC_DISTRIBUTION_CARRYFORWARD_00"
)
AUDITOR_CARRY_FORWARD_ACCOUNT_DEFINED_TOKEN = (
    "auditor_carry_forward_account_defined_GAP_PUBLIC_RC_DISTRIBUTION_CARRYFORWARD_00"
)
CARRY_FORWARD_NONSPENDABLE_TOKEN = (
    "carry_forward_nonspendable_confirmed_GAP_PUBLIC_RC_DISTRIBUTION_CARRYFORWARD_00"
)
CARRY_FORWARD_CONSUME_EXACTLY_ONCE_TOKEN = (
    "carry_forward_consume_exactly_once_enforced_GAP_PUBLIC_RC_DISTRIBUTION_CARRYFORWARD_00"
)

PERFORMER_POOL_ROLE = "performer"
AUDITOR_POOL_ROLE = "auditor"
PENDING_CONSUMPTION_STATUS = "pending_consumption"
CONSUMED_STATUS = "consumed"
MAX_CARRY_FORWARD_REASON_BYTES = 256
MAX_CARRY_FORWARD_AMOUNT_ADJUSTED_EXPONENT = 18

_SOURCE_SETTLEMENT_ROOT_RE = re.compile(r"^(?:[0-9a-f]{64}|01711220[0-9a-f]{64})$")
_ROLE_TO_ACCOUNT_ID = {
    PERFORMER_POOL_ROLE: PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
    AUDITOR_POOL_ROLE: AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
}
_POOL_RECORD_KEYS = frozenset(
    {
        "account_id",
        "claim_enabled",
        "nonspendable_token",
        "pool_role",
        "runtime_version",
        "spend_enabled",
        "transfer_enabled",
        "withdrawal_enabled",
    }
)


@dataclass(frozen=True)
class PoolCarryForwardRecord:
    source_epoch: int
    target_epoch: int
    pool_role: str
    amount_ilc: Decimal
    account_id: str
    reason: str
    source_settlement_root: str
    status: str
    consumed_at_epoch: int | None

    def __post_init__(self) -> None:
        _validate_record(self)

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "amount_ilc": decimal_to_canonical_string(self.amount_ilc),
            "cdl_029_allocation_dependency": CDL_029_ALLOCATION_DEPENDENCY,
            "consumed_at_epoch": self.consumed_at_epoch,
            "pool_role": self.pool_role,
            "reason": self.reason,
            "runtime_version": POOL_CARRY_FORWARD_RUNTIME_VERSION,
            "source_epoch": self.source_epoch,
            "source_settlement_root": self.source_settlement_root,
            "status": self.status,
            "target_epoch": self.target_epoch,
        }


def _require_epoch(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _require_pool_role(pool_role: str) -> str:
    if pool_role not in _ROLE_TO_ACCOUNT_ID:
        raise ValueError("invalid_carry_forward_pool_role")
    return pool_role


def _account_id_for_role(pool_role: str) -> str:
    return _ROLE_TO_ACCOUNT_ID[_require_pool_role(pool_role)]


def _require_account_matches_role(account_id: str, pool_role: str) -> str:
    if not isinstance(account_id, str) or not account_id:
        raise ValueError("carry_forward_account_id_required")
    expected = _account_id_for_role(pool_role)
    if account_id != expected:
        raise ValueError("carry_forward_account_id_role_mismatch")
    return account_id


def _require_amount(value: Decimal) -> Decimal:
    if not isinstance(value, Decimal):
        raise ValueError("carry_forward_amount_must_be_decimal")
    if not value.is_finite():
        raise ValueError("carry_forward_amount_must_be_finite")
    if value <= ZERO:
        raise ValueError("carry_forward_amount_must_be_nonzero_positive")
    if value.adjusted() > MAX_CARRY_FORWARD_AMOUNT_ADJUSTED_EXPONENT:
        raise ValueError("carry_forward_amount_exceeds_max_magnitude")
    if value > C_MAX_ILC:
        raise ValueError("carry_forward_amount_exceeds_c_max")
    if value % ILC_QUANTUM != ZERO:
        raise ValueError("carry_forward_amount_must_align_to_ilc_quantum")
    return value


def _require_reason(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("carry_forward_reason_required")
    if len(value.encode("utf-8")) > MAX_CARRY_FORWARD_REASON_BYTES:
        raise ValueError("carry_forward_reason_exceeds_max_bytes")
    return value


def _require_source_settlement_root(value: str) -> str:
    if not isinstance(value, str) or _SOURCE_SETTLEMENT_ROOT_RE.fullmatch(value) is None:
        raise ValueError("carry_forward_source_settlement_root_must_be_sha256_or_cidv1_hex")
    return value


def _validate_record(record: PoolCarryForwardRecord) -> None:
    source_epoch = _require_epoch(record.source_epoch, "source_epoch")
    target_epoch = _require_epoch(record.target_epoch, "target_epoch")
    if target_epoch != source_epoch + 1:
        raise ValueError("carry_forward_target_epoch_must_be_next_epoch")
    _require_pool_role(record.pool_role)
    _require_amount(record.amount_ilc)
    _require_account_matches_role(record.account_id, record.pool_role)
    _require_reason(record.reason)
    _require_source_settlement_root(record.source_settlement_root)
    if record.status == PENDING_CONSUMPTION_STATUS:
        if record.consumed_at_epoch is not None:
            raise ValueError("pending_carry_forward_consumed_epoch_must_be_none")
        return
    if record.status == CONSUMED_STATUS:
        consumed_at_epoch = _require_epoch(record.consumed_at_epoch, "consumed_at_epoch")
        if consumed_at_epoch <= source_epoch:
            raise ValueError("carry_forward_consumed_epoch_must_follow_source_epoch")
        if consumed_at_epoch < target_epoch:
            raise ValueError("carry_forward_consumed_epoch_must_reach_target_epoch")
        return
    raise ValueError("invalid_carry_forward_status")


def create_carry_forward_record(
    *,
    source_epoch: int,
    target_epoch: int,
    pool_role: str,
    amount_ilc: Decimal,
    account_id: str,
    reason: str,
    source_settlement_root: str,
) -> PoolCarryForwardRecord:
    return PoolCarryForwardRecord(
        source_epoch=source_epoch,
        target_epoch=target_epoch,
        pool_role=pool_role,
        amount_ilc=amount_ilc,
        account_id=account_id,
        reason=reason,
        source_settlement_root=source_settlement_root,
        status=PENDING_CONSUMPTION_STATUS,
        consumed_at_epoch=None,
    )


def mark_carry_forward_consumed(
    record: PoolCarryForwardRecord,
    consumed_at_epoch: int,
) -> PoolCarryForwardRecord:
    if not isinstance(record, PoolCarryForwardRecord):
        raise ValueError("carry_forward_record_required")
    _validate_record(record)
    if record.status == CONSUMED_STATUS:
        raise ValueError(CARRY_FORWARD_CONSUME_EXACTLY_ONCE_TOKEN)
    consumed_epoch = _require_epoch(consumed_at_epoch, "consumed_at_epoch")
    if consumed_epoch <= record.source_epoch:
        raise ValueError("carry_forward_consumed_epoch_must_follow_source_epoch")
    if consumed_epoch < record.target_epoch:
        raise ValueError("carry_forward_consumed_epoch_must_reach_target_epoch")
    return PoolCarryForwardRecord(
        source_epoch=record.source_epoch,
        target_epoch=record.target_epoch,
        pool_role=record.pool_role,
        amount_ilc=record.amount_ilc,
        account_id=record.account_id,
        reason=record.reason,
        source_settlement_root=record.source_settlement_root,
        status=CONSUMED_STATUS,
        consumed_at_epoch=consumed_epoch,
    )


def require_carry_forward_not_spendable() -> None:
    raise ValueError(CARRY_FORWARD_NONSPENDABLE_TOKEN)


def get_carry_forward_pool_record(pool_role: str) -> dict[str, Any]:
    role = _require_pool_role(pool_role)
    return {
        "account_id": _account_id_for_role(role),
        "claim_enabled": CARRY_FORWARD_CLAIM_ENABLED,
        "nonspendable_token": CARRY_FORWARD_NONSPENDABLE_TOKEN,
        "pool_role": role,
        "runtime_version": POOL_CARRY_FORWARD_RUNTIME_VERSION,
        "spend_enabled": CARRY_FORWARD_SPEND_ENABLED,
        "transfer_enabled": CARRY_FORWARD_TRANSFER_ENABLED,
        "withdrawal_enabled": CARRY_FORWARD_WITHDRAWAL_ENABLED,
    }


def verify_carry_forward_pool_record(record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise ValueError("carry_forward_pool_record_must_be_dict")
    if frozenset(record.keys()) != _POOL_RECORD_KEYS:
        raise ValueError("carry_forward_pool_record_keys_mismatch")
    role = _require_pool_role(record["pool_role"])
    if record.get("account_id") != _account_id_for_role(role):
        raise ValueError("carry_forward_pool_record_account_id_mismatch")
    if record.get("runtime_version") != POOL_CARRY_FORWARD_RUNTIME_VERSION:
        raise ValueError("carry_forward_pool_record_runtime_version_mismatch")
    if record.get("nonspendable_token") != CARRY_FORWARD_NONSPENDABLE_TOKEN:
        raise ValueError("carry_forward_pool_record_token_mismatch")
    for field in ("claim_enabled", "spend_enabled", "transfer_enabled", "withdrawal_enabled"):
        if record.get(field) is not False:
            raise ValueError(f"carry_forward_{field}_must_be_false")


__all__ = [
    "AUDITOR_CARRY_FORWARD_ACCOUNT_DEFINED_TOKEN",
    "AUDITOR_CARRY_FORWARD_ACCOUNT_ID",
    "AUDITOR_POOL_ROLE",
    "CARRY_FORWARD_CLAIM_ENABLED",
    "CARRY_FORWARD_CONSUME_EXACTLY_ONCE_TOKEN",
    "CARRY_FORWARD_NONSPENDABLE_TOKEN",
    "CARRY_FORWARD_SPEND_ENABLED",
    "CARRY_FORWARD_TRANSFER_ENABLED",
    "CARRY_FORWARD_WITHDRAWAL_ENABLED",
    "CDL_029_ALLOCATION_DEPENDENCY",
    "CONSUMED_STATUS",
    "PENDING_CONSUMPTION_STATUS",
    "PERFORMER_CARRY_FORWARD_ACCOUNT_DEFINED_TOKEN",
    "PERFORMER_CARRY_FORWARD_ACCOUNT_ID",
    "PERFORMER_POOL_ROLE",
    "POOL_CARRY_FORWARD_RUNTIME_CREATED_TOKEN",
    "POOL_CARRY_FORWARD_RUNTIME_VERSION",
    "PoolCarryForwardRecord",
    "create_carry_forward_record",
    "get_carry_forward_pool_record",
    "mark_carry_forward_consumed",
    "require_carry_forward_not_spendable",
    "verify_carry_forward_pool_record",
]
