# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedgerEntry
from ilc_core.value_action.ilc_transfer_receipt import (
    ILC_TRANSFER_RECEIPT_VERSION,
    build_transfer_receipt,
    compute_transfer_batch_root,
    verify_receipt,
)

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
THIRD_AGENT_ID = "c" * 96
MODULE_PATH = Path("ilc_core/value_action/ilc_transfer_receipt.py")


def _entry(
    *,
    transfer_id: str = "1" * 64,
    sender: str = SENDER_AGENT_ID,
    recipient: str = RECIPIENT_AGENT_ID,
    amount: Decimal = Decimal("3.5"),
    nonce: str | None = None,
    epoch: int = 0,
) -> ILCTransferLedgerEntry:
    return ILCTransferLedgerEntry(
        transfer_id=transfer_id,
        sender_agent_id=sender,
        recipient_agent_id=recipient,
        amount_ilc=amount,
        nonce=nonce or f"{sender}:nonce:{1:020d}",
        epoch=epoch,
        sender_balance_before_ilc=Decimal("10"),
        sender_balance_after_ilc=Decimal("6.5"),
        recipient_balance_before_ilc=Decimal("0"),
        recipient_balance_after_ilc=amount,
        record_sha256="2" * 64,
        memo="receipt test",
        graph_context_anchor="graph:receipt-test",
    )


def test_receipt_hash_is_deterministic() -> None:
    entry = _entry()

    first = build_transfer_receipt(entry)
    second = build_transfer_receipt(entry)

    assert first == second
    assert first.receipt_id == f"ilc-transfer-receipt:{first.receipt_sha256}"


def test_tampered_amount_changes_hash() -> None:
    entry = _entry()
    tampered = replace(entry, amount_ilc=Decimal("3.6"))

    assert build_transfer_receipt(entry).receipt_sha256 != build_transfer_receipt(
        tampered
    ).receipt_sha256


def test_batch_root_same_regardless_of_input_order() -> None:
    first = build_transfer_receipt(_entry())
    second = build_transfer_receipt(
        _entry(
            transfer_id="3" * 64,
            sender=RECIPIENT_AGENT_ID,
            recipient=THIRD_AGENT_ID,
            nonce=f"{RECIPIENT_AGENT_ID}:nonce:{1:020d}",
        )
    )

    assert compute_transfer_batch_root([first, second]) == compute_transfer_batch_root(
        [second, first]
    )


def test_verify_receipt_passes_on_valid_entry() -> None:
    entry = _entry()

    assert verify_receipt(build_transfer_receipt(entry), entry) is True


def test_verify_receipt_fails_on_tampered_entry() -> None:
    entry = _entry()
    receipt = build_transfer_receipt(entry)
    tampered = replace(entry, amount_ilc=Decimal("4.5"))

    assert verify_receipt(receipt, tampered) is False


def test_empty_batch_root_does_not_crash() -> None:
    root = compute_transfer_batch_root([])

    assert root.epoch == 0
    assert root.transfer_count == 0
    assert len(root.root_sha256) == 64


def test_verify_receipt_rejects_metadata_tamper() -> None:
    entry = _entry()
    receipt = build_transfer_receipt(entry)
    tampered_receipt = replace(receipt, recipient_agent_id=THIRD_AGENT_ID)

    assert verify_receipt(tampered_receipt, entry) is False


def test_batch_root_rejects_mixed_epochs() -> None:
    first = build_transfer_receipt(_entry(epoch=1))
    second = build_transfer_receipt(_entry(transfer_id="4" * 64, epoch=2))

    with pytest.raises(ValueError, match="mixed_transfer_receipt_epochs"):
        compute_transfer_batch_root([first, second])


def test_batch_root_rejects_duplicate_receipts() -> None:
    receipt = build_transfer_receipt(_entry())

    with pytest.raises(ValueError, match="duplicate_transfer_receipt"):
        compute_transfer_batch_root([receipt, receipt])


def test_batch_root_rejects_malformed_receipt_hash() -> None:
    receipt = replace(build_transfer_receipt(_entry()), receipt_sha256="A" * 64)

    with pytest.raises(ValueError, match="invalid_transfer_receipt_sha256"):
        compute_transfer_batch_root([receipt])


def test_decimal_payload_uses_canonical_string_without_exponent() -> None:
    normal = build_transfer_receipt(_entry(amount=Decimal("0.000000001")))
    exponent = build_transfer_receipt(_entry(amount=Decimal("1E-9")))

    assert normal.receipt_sha256 == exponent.receipt_sha256


def test_module_has_no_disallowed_runtime_patterns() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "uuid" not in source
    assert "time" not in source
    assert "random" not in source
    assert "float" not in source
    assert "\nassert " not in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source
    assert ILC_TRANSFER_RECEIPT_VERSION == "ilc_transfer_receipt_05.v0.1"
