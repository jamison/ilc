# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.ledger.exact_numeric import parse_non_negative_decimal
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger


RECEIPT_PATH = Path("out/gap_genesis_wallet_transfer_bridge_00/bridge_receipt.json")
WALLET_PATH = Path("out/public_runtime/wallet")

pytestmark = pytest.mark.skipif(
    not RECEIPT_PATH.exists() or not (WALLET_PATH / "data.mdb").exists(),
    reason="requires local EPOCH-SETTLEMENT-00 and TRANSFER-BRIDGE-00 LMDB artifacts",
)


def test_gap_genesis_wallet_transfer_bridge_receipt_matches_lmdb_readback() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    wallet_store = LmdbWalletStore(WALLET_PATH)
    try:
        wallet_row = wallet_store.get_wallet(GENESIS_AGENT1_AGENT_ID)
        assert isinstance(wallet_row, dict)
        settled = parse_non_negative_decimal(wallet_row["balance_ilc"])
        bridged = ILCTransferLedger(wallet_store.env).get_balance(GENESIS_AGENT1_AGENT_ID)
    finally:
        wallet_store.close()

    assert receipt["balances_match"] is True
    assert receipt["seed_balance_for_test_used"] is False
    assert receipt["ilc_test_balance_seed_authorized_env_present"] is False
    assert Decimal(receipt["settled_wallet_balance_ilc"]) == settled
    assert Decimal(receipt["bridged_transfer_balance_ilc"]) == bridged
    assert settled == bridged == Decimal("18580.494562318")


def test_gap_genesis_wallet_transfer_bridge_receipt_token_and_db_name() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    assert receipt["transfer_balances_db_name"] == "ilc_transfer_balances"
    assert (
        receipt["output_token"]
        == "genesis_wallet_transfer_bridge_committed_GAP_GENESIS_WALLET_TRANSFER_BRIDGE_00"
    )
    assert receipt["non_claims"]["no_ilc_transfer_executed"] is True
