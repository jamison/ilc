# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-028 protocol reserve destination binding.

The protocol reserve is a concrete settled destination for the CDL-028
``genesis_burn_pool``. It is distinct from Genesis Agent 1 and treasury, and it
has no transfer, withdrawal, or governance-deployment authority at public RC.
"""

from __future__ import annotations

from typing import Any


PROTOCOL_RESERVE_DESTINATION_RUNTIME_VERSION = (
    "protocol_reserve_destination_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00.v0.1"
)
CDL_028_AMENDMENT_DEPENDENCY = (
    "cdl028_protocol_reserve_amendment_committed_GAP_PUBLIC_RC_CDL028_AMENDMENT_00"
)

PROTOCOL_RESERVE_ACCOUNT_ID = "reserve:cdl028:genesis_burn_pool"

PROTOCOL_RESERVE_TRANSFER_ENABLED = False
PROTOCOL_RESERVE_WITHDRAWAL_ENABLED = False
PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_ENABLED = False

PROTOCOL_RESERVE_DESTINATION_MODULE_CREATED_TOKEN = (
    "protocol_reserve_destination_module_created_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00"
)
PROTOCOL_RESERVE_TRANSFER_BLOCKED_TOKEN = (
    "protocol_reserve_transfer_blocked_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00"
)
PROTOCOL_RESERVE_WITHDRAWAL_BLOCKED_TOKEN = (
    "protocol_reserve_withdrawal_blocked_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00"
)
PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_BLOCKED_TOKEN = (
    "protocol_reserve_governance_deployment_blocked_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00"
)
PROTOCOL_RESERVE_DISTINCT_FROM_GENESIS_AGENT_TOKEN = (
    "protocol_reserve_distinct_from_genesis_agent_confirmed_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00"
)
PROTOCOL_RESERVE_DISTINCT_FROM_TREASURY_TOKEN = (
    "protocol_reserve_distinct_from_treasury_confirmed_GAP_PUBLIC_RC_PROTOCOL_RESERVE_00"
)

_EXPECTED_RECORD_KEYS = frozenset(
    {
        "account_id",
        "cdl_028_amendment_dependency",
        "distinct_from_genesis_agent",
        "distinct_from_treasury",
        "governance_deployment_enabled",
        "module_created_token",
        "runtime_version",
        "transfer_enabled",
        "withdrawal_enabled",
    }
)

_FORBIDDEN_TRUE_FIELDS = frozenset(
    {
        "transfer_enabled",
        "withdrawal_enabled",
        "governance_deployment_enabled",
    }
)


def require_protocol_reserve_transfer_blocked() -> None:
    """Fail closed for any attempted reserve transfer."""

    raise ValueError(PROTOCOL_RESERVE_TRANSFER_BLOCKED_TOKEN)


def require_protocol_reserve_withdrawal_blocked() -> None:
    """Fail closed for any attempted reserve withdrawal."""

    raise ValueError(PROTOCOL_RESERVE_WITHDRAWAL_BLOCKED_TOKEN)


def require_protocol_reserve_governance_deployment_blocked() -> None:
    """Fail closed until CDL-047 governance explicitly authorizes deployment."""

    raise ValueError(PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_BLOCKED_TOKEN)


def get_protocol_reserve_destination_record() -> dict[str, Any]:
    """Return the canonical protocol reserve destination record."""

    return {
        "account_id": PROTOCOL_RESERVE_ACCOUNT_ID,
        "cdl_028_amendment_dependency": CDL_028_AMENDMENT_DEPENDENCY,
        "distinct_from_genesis_agent": True,
        "distinct_from_treasury": True,
        "governance_deployment_enabled": PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_ENABLED,
        "module_created_token": PROTOCOL_RESERVE_DESTINATION_MODULE_CREATED_TOKEN,
        "runtime_version": PROTOCOL_RESERVE_DESTINATION_RUNTIME_VERSION,
        "transfer_enabled": PROTOCOL_RESERVE_TRANSFER_ENABLED,
        "withdrawal_enabled": PROTOCOL_RESERVE_WITHDRAWAL_ENABLED,
    }


def verify_protocol_reserve_destination_record(record: dict[str, Any]) -> None:
    """Verify protocol reserve account and public-RC nonspendability invariants."""

    if not isinstance(record, dict):
        raise ValueError("protocol_reserve_destination_record_must_be_dict")
    if frozenset(record.keys()) != _EXPECTED_RECORD_KEYS:
        raise ValueError("protocol_reserve_destination_record_keys_mismatch")
    if record.get("account_id") != PROTOCOL_RESERVE_ACCOUNT_ID:
        raise ValueError("protocol_reserve_account_id_mismatch")
    if record.get("cdl_028_amendment_dependency") != CDL_028_AMENDMENT_DEPENDENCY:
        raise ValueError("protocol_reserve_cdl028_dependency_mismatch")
    if record.get("runtime_version") != PROTOCOL_RESERVE_DESTINATION_RUNTIME_VERSION:
        raise ValueError("protocol_reserve_runtime_version_mismatch")
    if record.get("module_created_token") != PROTOCOL_RESERVE_DESTINATION_MODULE_CREATED_TOKEN:
        raise ValueError("protocol_reserve_module_created_token_mismatch")
    for field in _FORBIDDEN_TRUE_FIELDS:
        if record.get(field) is not False:
            raise ValueError(f"protocol_reserve_{field}_must_be_false")
    if record.get("distinct_from_genesis_agent") is not True:
        raise ValueError(PROTOCOL_RESERVE_DISTINCT_FROM_GENESIS_AGENT_TOKEN)
    if record.get("distinct_from_treasury") is not True:
        raise ValueError(PROTOCOL_RESERVE_DISTINCT_FROM_TREASURY_TOKEN)


__all__ = [
    "CDL_028_AMENDMENT_DEPENDENCY",
    "PROTOCOL_RESERVE_ACCOUNT_ID",
    "PROTOCOL_RESERVE_DESTINATION_MODULE_CREATED_TOKEN",
    "PROTOCOL_RESERVE_DESTINATION_RUNTIME_VERSION",
    "PROTOCOL_RESERVE_DISTINCT_FROM_GENESIS_AGENT_TOKEN",
    "PROTOCOL_RESERVE_DISTINCT_FROM_TREASURY_TOKEN",
    "PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_BLOCKED_TOKEN",
    "PROTOCOL_RESERVE_GOVERNANCE_DEPLOYMENT_ENABLED",
    "PROTOCOL_RESERVE_TRANSFER_BLOCKED_TOKEN",
    "PROTOCOL_RESERVE_TRANSFER_ENABLED",
    "PROTOCOL_RESERVE_WITHDRAWAL_BLOCKED_TOKEN",
    "PROTOCOL_RESERVE_WITHDRAWAL_ENABLED",
    "get_protocol_reserve_destination_record",
    "require_protocol_reserve_governance_deployment_blocked",
    "require_protocol_reserve_transfer_blocked",
    "require_protocol_reserve_withdrawal_blocked",
    "verify_protocol_reserve_destination_record",
]
