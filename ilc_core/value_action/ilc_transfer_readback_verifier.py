# SPDX-License-Identifier: AGPL-3.0-only
"""Readback verifier for Python LMDB settled-ILC value actions."""
from __future__ import annotations

from decimal import Decimal

from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger

ILC_TRANSFER_READBACK_VERSION = "ilc_transfer_readback_verifier_06.v0.1"
READBACK_PATH = "PYTHON_LMDB_AUTHORITATIVE"


class ILCTransferReadbackVerifier:
    """Verify post-transfer state through the authoritative Python LMDB ledger."""

    def verify_post_transfer_balance(
        self,
        ledger: ILCTransferLedger,
        agent_id: str,
        expected_balance: Decimal,
    ) -> bool:
        """Return true when LMDB balance readback exactly matches expected."""
        if not isinstance(expected_balance, Decimal) or not expected_balance.is_finite():
            raise ValueError("invalid_expected_readback_balance")
        return ledger.get_balance(agent_id) == expected_balance

    def verify_transfer_record_retrievable(
        self,
        ledger: ILCTransferLedger,
        transfer_id: str,
    ) -> bool:
        """Return true when a transfer record is present and integrity-valid.

        Corrupt or tampered records raise the ledger's stable ValueError token
        rather than being coerced into a missing-record false negative.
        """
        return ledger.get_transfer_record(transfer_id) is not None


__all__ = [
    "ILC_TRANSFER_READBACK_VERSION",
    "ILCTransferReadbackVerifier",
    "READBACK_PATH",
]
