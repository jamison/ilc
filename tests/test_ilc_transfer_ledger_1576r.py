# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import lmdb
import pytest

from ilc_core.value_action import ilc_transfer_intent
from ilc_core.value_action.action_nonce_store import ActionNonceStore, NonceReplayError
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.ilc_transfer_ledger import (
    ILC_TRANSFER_LEDGER_VERSION,
    ILCTransferLedger,
    InsufficientBalanceError,
    _encode_balance,
)

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
MODULE_PATH = Path("ilc_core/value_action/ilc_transfer_ledger.py")


@pytest.fixture
def lmdb_env(tmp_path: Path):
    env = lmdb.open(str(tmp_path / "ilc-transfer-ledger.lmdb"), max_dbs=8, map_size=8 * 1024 * 1024)
    try:
        yield env
    finally:
        env.close()


@pytest.fixture(autouse=True)
def transfer_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ilc_transfer_intent, "ILC_TRANSFER_ENABLED", True)


def _nonce(agent_id: str, counter: int) -> str:
    return f"{agent_id}:nonce:{counter:020d}"


def _intent(amount: Decimal = Decimal("3.5"), *, nonce: str | None = None):
    return ILCTransferIntent.create(
        sender_agent_id=SENDER_AGENT_ID,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=amount,
        nonce=nonce or _nonce(SENDER_AGENT_ID, 1),
        epoch=0,
        memo="settled ILC transfer",
        graph_context_anchor="graph:transfer-context",
    )


def _seed_balance(ledger: ILCTransferLedger, agent_id: str, amount: Decimal) -> None:
    with ledger._env.begin(write=True, db=ledger._balances_db) as txn:
        txn.put(agent_id.encode("ascii"), _encode_balance(amount))


def test_happy_path_debit_credit_record(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    entry = ledger.execute_transfer(_intent(), nonce_store)

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("6.5")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("3.5")
    assert len(entry.transfer_id) == 64
    assert ledger.get_transfer_record(entry.transfer_id) == entry


def test_insufficient_balance_raises_and_nonce_not_consumed(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    with pytest.raises(InsufficientBalanceError, match="insufficient_balance"):
        ledger.execute_transfer(_intent(Decimal("11")), nonce_store)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0


def test_activation_guard_blocks(lmdb_env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ilc_transfer_intent, "ILC_TRANSFER_ENABLED", False)
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)

    with pytest.raises(ValueError, match="transfer_not_enabled"):
        ledger.execute_transfer(_intent(), nonce_store)


def test_nonce_replay_raises(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    env = _intent()
    ledger.execute_transfer(env, nonce_store)

    with pytest.raises(NonceReplayError, match="nonce_replay_rejected"):
        ledger.execute_transfer(env, nonce_store)


def test_decimal_precision_lmdb_roundtrip(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1.000000001"))

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("1.000000001")


def test_sender_balance_zero_after_full_transfer(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("3.5"))

    ledger.execute_transfer(_intent(), nonce_store)

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("0")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("3.5")


def test_transfer_record_retrievable(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    entry = ledger.execute_transfer(_intent(), nonce_store)
    readback = ledger.get_transfer_record(entry.transfer_id)

    assert readback is not None
    assert readback.amount_ilc == Decimal("3.5")
    assert readback.sender_balance_before_ilc == Decimal("10")
    assert readback.sender_balance_after_ilc == Decimal("6.5")
    assert readback.recipient_balance_after_ilc == Decimal("3.5")
    assert len(readback.record_sha256) == 64


def test_zero_amount_transfer_raises(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)

    with pytest.raises(ValueError, match="invalid_envelope_amount_not_positive"):
        ledger.execute_transfer(_intent(Decimal("0")), nonce_store)


def test_transaction_is_atomic_on_balance_corruption(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    with ledger._env.begin(write=True, db=ledger._balances_db) as txn:
        txn.put(SENDER_AGENT_ID.encode("ascii"), b"NaN")

    with pytest.raises(ValueError, match="invalid_ilc_balance"):
        ledger.execute_transfer(_intent(), nonce_store)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0


def test_nonce_store_must_share_lmdb_env(tmp_path: Path, lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    other_env = lmdb.open(str(tmp_path / "other.lmdb"), max_dbs=4, map_size=8 * 1024 * 1024)
    try:
        with pytest.raises(ValueError, match="transfer_nonce_store_env_mismatch"):
            ledger.execute_transfer(_intent(), ActionNonceStore(other_env))
    finally:
        other_env.close()


def test_deterministic_transfer_id_for_same_payload_different_store(tmp_path: Path) -> None:
    ids: list[str] = []
    for index in range(2):
        env = lmdb.open(str(tmp_path / f"ledger-{index}.lmdb"), max_dbs=8, map_size=8 * 1024 * 1024)
        try:
            ledger = ILCTransferLedger(env)
            nonce_store = ActionNonceStore(env)
            _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
            ids.append(ledger.execute_transfer(_intent(), nonce_store).transfer_id)
        finally:
            env.close()

    assert ids[0] == ids[1]


def test_module_has_no_disallowed_runtime_patterns() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "EpochSettlementRecord" not in source
    assert "epoch_settlement_record" not in source
    assert "float" not in source
    assert "\nassert " not in source
    assert "uuid" not in source
    assert "monotonic" not in source
    assert ILC_TRANSFER_LEDGER_VERSION == "ilc_transfer_ledger_04.v0.1"
