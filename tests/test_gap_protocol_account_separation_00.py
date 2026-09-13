from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import lmdb
import pytest
from fastapi.testclient import TestClient

import ilc_core.epoch as epoch
from ilc_core.epoch.protocol_account_boundary import (
    CARRY_FORWARD_PROTOCOL_ACCOUNT_IDS,
    PROTOCOL_ACCOUNT_BOUNDARY_VERSION,
    RESERVED_PROTOCOL_ACCOUNT_IDS,
    RESERVED_PROTOCOL_ACCOUNT_PREFIXES,
    is_reserved_protocol_account,
    require_known_protocol_account_id,
    require_not_reserved_protocol_account,
)
from ilc_core.epoch.pool_carry_forward_runtime import (
    AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
)
from ilc_core.epoch.protocol_reserve_destination import PROTOCOL_RESERVE_ACCOUNT_ID
from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntimeError
from ilc_core.server import create_app
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger


SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
PROTOCOL_ACCOUNTS = (
    PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
    AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    PROTOCOL_RESERVE_ACCOUNT_ID,
)
PROMPT_PATH = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_gap_protocol_account_separation_00_g10_reserved_pool_wallet_boundary.md"
)


@pytest.fixture
def lmdb_env(tmp_path: Path):
    env = lmdb.open(str(tmp_path / "transfer-ledger.lmdb"), max_dbs=8, map_size=8 * 1024 * 1024)
    try:
        yield env
    finally:
        env.close()


@pytest.fixture(autouse=True)
def seed_authorized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_TEST_BALANCE_SEED_AUTHORIZED", "1")


def _transfer(**overrides: object):
    fields = {
        "sender_agent_id": SENDER_AGENT_ID,
        "recipient_agent_id": RECIPIENT_AGENT_ID,
        "amount_ilc": Decimal("1"),
        "nonce": f"{SENDER_AGENT_ID}:nonce:00000000000000000001",
        "epoch": 1,
    }
    fields.update(overrides)
    return ILCTransferIntent.create(**fields)


def test_protocol_account_boundary_exports_registered_pool_and_reserve_ids() -> None:
    assert PROTOCOL_ACCOUNT_BOUNDARY_VERSION.endswith("GAP_PROTOCOL_ACCOUNT_SEPARATION_00.v0.1")
    assert RESERVED_PROTOCOL_ACCOUNT_PREFIXES == ("pool:", "reserve:")
    assert set(PROTOCOL_ACCOUNTS) == RESERVED_PROTOCOL_ACCOUNT_IDS
    assert CARRY_FORWARD_PROTOCOL_ACCOUNT_IDS == {
        PERFORMER_CARRY_FORWARD_ACCOUNT_ID,
        AUDITOR_CARRY_FORWARD_ACCOUNT_ID,
    }
    assert epoch.RESERVED_PROTOCOL_ACCOUNT_IDS == RESERVED_PROTOCOL_ACCOUNT_IDS
    assert epoch.PROTOCOL_ACCOUNT_BOUNDARY_VERSION == PROTOCOL_ACCOUNT_BOUNDARY_VERSION


@pytest.mark.parametrize("account_id", PROTOCOL_ACCOUNTS)
def test_registered_protocol_accounts_are_detected_and_not_user_principals(account_id: str) -> None:
    assert is_reserved_protocol_account(account_id) is True
    assert require_known_protocol_account_id(account_id) == account_id

    with pytest.raises(ValueError, match="reserved_protocol_account_not_agent_principal"):
        require_not_reserved_protocol_account(
            account_id,
            "reserved_protocol_account_not_agent_principal",
        )


@pytest.mark.parametrize(
    "account_id",
    [
        "pool:cdl029:future_unregistered_account",
        "reserve:cdl028:future_unregistered_account",
    ],
)
def test_unknown_protocol_accounts_are_rejected_as_unregistered(account_id: str) -> None:
    assert is_reserved_protocol_account(account_id) is True
    with pytest.raises(ValueError, match="unknown_protocol_account_id"):
        require_known_protocol_account_id(account_id)


@pytest.mark.parametrize("account_id", PROTOCOL_ACCOUNTS)
def test_public_wallet_runtime_rejects_protocol_accounts(account_id: str) -> None:
    with TestClient(create_app()) as client:
        with pytest.raises(PublicWalletRuntimeError) as exc_info:
            client.app.state.public_wallet_runtime.wallet_status(agent_id=account_id)

    assert exc_info.value.token == "wallet_protocol_account_not_user_wallet"


def test_transfer_intent_rejects_protocol_account_sender() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_sender_protocol_account"):
        _transfer(sender_agent_id=PERFORMER_CARRY_FORWARD_ACCOUNT_ID)


def test_transfer_intent_rejects_protocol_account_recipient() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_recipient_protocol_account"):
        _transfer(recipient_agent_id=PROTOCOL_RESERVE_ACCOUNT_ID)


@pytest.mark.parametrize("account_id", PROTOCOL_ACCOUNTS)
def test_transfer_ledger_get_balance_rejects_protocol_accounts(lmdb_env, account_id: str) -> None:
    ledger = ILCTransferLedger(lmdb_env)

    with pytest.raises(ValueError, match="invalid_ilc_transfer_protocol_account"):
        ledger.get_balance(account_id)


def test_transfer_ledger_seed_balance_rejects_protocol_accounts(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)

    with pytest.raises(ValueError, match="invalid_ilc_transfer_protocol_account"):
        ledger.seed_balance_for_test(PROTOCOL_RESERVE_ACCOUNT_ID, Decimal("1"))


def test_prompt_names_transfer_sender_and_recipient_boundary() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")

    assert "Ensure reserved protocol accounts cannot be transfer senders or recipients." in text
