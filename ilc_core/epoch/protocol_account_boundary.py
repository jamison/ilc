# SPDX-License-Identifier: AGPL-3.0-only
"""Reserved protocol-account boundary helpers.

Protocol accounts are internal accounting destinations, not graph AgentIDs and
not transfer principals. Settlement code may write explicitly registered
accounts, but public wallet and transfer surfaces must reject them.
"""

from __future__ import annotations

from ilc_core.epoch.pool_carry_forward_runtime import (
    AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
)
from ilc_core.epoch.protocol_reserve_destination import PROTOCOL_RESERVE_ACCOUNT_ID


PROTOCOL_ACCOUNT_BOUNDARY_VERSION = (
    "protocol_account_boundary_GAP_PROTOCOL_ACCOUNT_SEPARATION_00.v0.1"
)
RESERVED_PROTOCOL_ACCOUNT_PREFIXES = ("pool:", "reserve:")
RESERVED_PROTOCOL_ACCOUNT_IDS = frozenset(
    {
        PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
        PROTOCOL_RESERVE_ACCOUNT_ID,
    }
)
CARRY_FORWARD_PROTOCOL_ACCOUNT_IDS = frozenset(
    {
        PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    }
)


def is_reserved_protocol_account(value: object) -> bool:
    return isinstance(value, str) and value.startswith(RESERVED_PROTOCOL_ACCOUNT_PREFIXES)


def require_not_reserved_protocol_account(value: object, token: str) -> None:
    if is_reserved_protocol_account(value):
        raise ValueError(token)


def require_known_protocol_account_id(value: object, token: str = "unknown_protocol_account_id") -> str:
    if not isinstance(value, str) or value not in RESERVED_PROTOCOL_ACCOUNT_IDS:
        raise ValueError(token)
    return value


__all__ = [
    "CARRY_FORWARD_PROTOCOL_ACCOUNT_IDS",
    "PROTOCOL_ACCOUNT_BOUNDARY_VERSION",
    "RESERVED_PROTOCOL_ACCOUNT_IDS",
    "RESERVED_PROTOCOL_ACCOUNT_PREFIXES",
    "is_reserved_protocol_account",
    "require_known_protocol_account_id",
    "require_not_reserved_protocol_account",
]
