# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic transfer receipts for settled ILC value actions."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedgerEntry

ILC_TRANSFER_RECEIPT_VERSION = "ilc_transfer_receipt_05.v0.1"


@dataclass(frozen=True)
class ILCTransferReceipt:
    receipt_id: str
    transfer_id: str
    sender_agent_id: str
    recipient_agent_id: str
    amount_ilc: Decimal
    nonce: str
    epoch: int
    sender_balance_before_ilc: Decimal
    sender_balance_after_ilc: Decimal
    recipient_balance_before_ilc: Decimal
    recipient_balance_after_ilc: Decimal
    record_sha256: str
    receipt_sha256: str
    memo: str | None = None
    graph_context_anchor: str | None = None


@dataclass(frozen=True)
class ILCTransferBatchRoot:
    epoch: int
    transfer_count: int
    root_sha256: str


def build_transfer_receipt(entry: ILCTransferLedgerEntry) -> ILCTransferReceipt:
    """Build a deterministic receipt commitment for a ledger entry."""
    payload = _receipt_payload(entry)
    receipt_sha256 = _sha256_hex(payload)
    return ILCTransferReceipt(
        receipt_id=f"ilc-transfer-receipt:{receipt_sha256}",
        transfer_id=entry.transfer_id,
        sender_agent_id=entry.sender_agent_id,
        recipient_agent_id=entry.recipient_agent_id,
        amount_ilc=entry.amount_ilc,
        nonce=entry.nonce,
        epoch=entry.epoch,
        sender_balance_before_ilc=entry.sender_balance_before_ilc,
        sender_balance_after_ilc=entry.sender_balance_after_ilc,
        recipient_balance_before_ilc=entry.recipient_balance_before_ilc,
        recipient_balance_after_ilc=entry.recipient_balance_after_ilc,
        record_sha256=entry.record_sha256,
        receipt_sha256=receipt_sha256,
        memo=entry.memo,
        graph_context_anchor=entry.graph_context_anchor,
    )


def compute_transfer_batch_root(
    receipts: list[ILCTransferReceipt],
) -> ILCTransferBatchRoot:
    """Compute an order-independent SHA-256 batch root over receipts."""
    if not receipts:
        return ILCTransferBatchRoot(
            epoch=0,
            transfer_count=0,
            root_sha256=hashlib.sha256(b"").hexdigest(),
        )

    epochs = {receipt.epoch for receipt in receipts}
    if len(epochs) != 1:
        raise ValueError("mixed_transfer_receipt_epochs")

    receipt_hashes = [_require_sha256_hex(receipt.receipt_sha256) for receipt in receipts]
    if len(set(receipt_hashes)) != len(receipt_hashes):
        raise ValueError("duplicate_transfer_receipt")

    payload = {
        "receipt_sha256_values": sorted(receipt_hashes),
        "schema_version": ILC_TRANSFER_RECEIPT_VERSION,
        "transfer_count": len(receipts),
    }
    return ILCTransferBatchRoot(
        epoch=receipts[0].epoch,
        transfer_count=len(receipts),
        root_sha256=_sha256_hex(payload),
    )


def verify_receipt(receipt: ILCTransferReceipt, entry: ILCTransferLedgerEntry) -> bool:
    """Return true only when receipt fully matches a rebuilt entry receipt."""
    return receipt == build_transfer_receipt(entry)


def _receipt_payload(entry: ILCTransferLedgerEntry) -> dict[str, Any]:
    return {
        "amount_ilc": decimal_to_canonical_string(entry.amount_ilc),
        "epoch": entry.epoch,
        "graph_context_anchor": entry.graph_context_anchor,
        "memo": entry.memo,
        "nonce": entry.nonce,
        "receipt_schema_version": ILC_TRANSFER_RECEIPT_VERSION,
        "recipient_agent_id": entry.recipient_agent_id,
        "recipient_balance_after_ilc": decimal_to_canonical_string(
            entry.recipient_balance_after_ilc
        ),
        "recipient_balance_before_ilc": decimal_to_canonical_string(
            entry.recipient_balance_before_ilc
        ),
        "record_sha256": entry.record_sha256,
        "sender_agent_id": entry.sender_agent_id,
        "sender_balance_after_ilc": decimal_to_canonical_string(
            entry.sender_balance_after_ilc
        ),
        "sender_balance_before_ilc": decimal_to_canonical_string(
            entry.sender_balance_before_ilc
        ),
        "transfer_id": entry.transfer_id,
    }


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def _sha256_hex(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_json_bytes(payload)).hexdigest()


def _require_sha256_hex(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("invalid_transfer_receipt_sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("invalid_transfer_receipt_sha256") from exc
    if value.lower() != value:
        raise ValueError("invalid_transfer_receipt_sha256")
    return value


__all__ = [
    "ILC_TRANSFER_RECEIPT_VERSION",
    "ILCTransferBatchRoot",
    "ILCTransferReceipt",
    "build_transfer_receipt",
    "compute_transfer_batch_root",
    "verify_receipt",
]
