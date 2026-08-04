# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import lmdb
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from ilc_core.value_action import ilc_transfer_intent
from ilc_core.value_action.action_nonce_store import ActionNonceStore, NonceReplayError
from ilc_core.value_action.local_signing_provider import LocalEd25519SigningProvider
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.ilc_transfer_ledger import (
    ILC_TRANSFER_LEDGER_VERSION,
    ILCTransferLedger,
    InsufficientBalanceError,
)

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
MODULE_PATH = Path("ilc_core/value_action/ilc_transfer_ledger.py")


class _SignerAuthority:
    def __init__(self, agent_id: str, public_key_bytes: bytes) -> None:
        self._agent_id = agent_id
        self._public_key_bytes = public_key_bytes

    def is_signer_authorized(
        self,
        agent_id: str,
        public_key_bytes: bytes,
        *,
        action_scope: str,
    ) -> bool:
        return (
            agent_id == self._agent_id
            and public_key_bytes == self._public_key_bytes
            and action_scope == "ILC_TRANSFER"
        )


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
    monkeypatch.setenv("ILC_TEST_BALANCE_SEED_AUTHORIZED", "1")


@pytest.fixture
def private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


@pytest.fixture
def key_uri(tmp_path: Path, private_key: ed25519.Ed25519PrivateKey) -> str:
    key_path = tmp_path / "sender-ed25519.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            NoEncryption(),
        )
    )
    key_path.chmod(0o600)
    return key_path.as_uri()


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


def _signed_intent(
    key_uri: str,
    amount: Decimal = Decimal("3.5"),
    *,
    nonce: str | None = None,
):
    return LocalEd25519SigningProvider().sign_envelope(_intent(amount, nonce=nonce), key_uri)


def _execute(
    ledger: ILCTransferLedger,
    nonce_store: ActionNonceStore,
    env,
    private_key: ed25519.Ed25519PrivateKey,
):
    provider = LocalEd25519SigningProvider()
    public_key_bytes = private_key.public_key().public_bytes_raw()
    return ledger.execute_transfer(
        env,
        nonce_store,
        signature_verifier=provider,
        signer_authority=_SignerAuthority(env.sender_agent_id, public_key_bytes),
        sender_public_key_bytes=public_key_bytes,
    )


def _seed_balance(ledger: ILCTransferLedger, agent_id: str, amount: Decimal) -> None:
    ledger.seed_balance_for_test(agent_id, amount)


def test_happy_path_debit_credit_record(lmdb_env, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    entry = _execute(ledger, nonce_store, _signed_intent(key_uri), private_key)

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("6.5")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("3.5")
    assert len(entry.transfer_id) == 64
    assert ledger.get_transfer_record(entry.transfer_id) == entry


def test_insufficient_balance_raises_and_nonce_not_consumed(
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    with pytest.raises(InsufficientBalanceError, match="insufficient_balance"):
        _execute(ledger, nonce_store, _signed_intent(key_uri, Decimal("11")), private_key)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0


def test_activation_guard_blocks(
    lmdb_env,
    monkeypatch: pytest.MonkeyPatch,
    key_uri: str,
    private_key,
) -> None:
    monkeypatch.setattr(ilc_transfer_intent, "ILC_TRANSFER_ENABLED", False)
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)

    with pytest.raises(ValueError, match="transfer_not_enabled"):
        _execute(ledger, nonce_store, _signed_intent(key_uri), private_key)


def test_nonce_replay_raises(lmdb_env, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    env = _signed_intent(key_uri)
    _execute(ledger, nonce_store, env, private_key)

    with pytest.raises(NonceReplayError, match="nonce_replay_rejected"):
        _execute(ledger, nonce_store, env, private_key)


def test_decimal_precision_lmdb_roundtrip(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1.000000001"))

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("1.000000001")


def test_sender_balance_zero_after_full_transfer(lmdb_env, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("3.5"))

    _execute(ledger, nonce_store, _signed_intent(key_uri), private_key)

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("0")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("3.5")


def test_transfer_record_retrievable(lmdb_env, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    entry = _execute(ledger, nonce_store, _signed_intent(key_uri), private_key)
    readback = ledger.get_transfer_record(entry.transfer_id)

    assert readback is not None
    assert readback.amount_ilc == Decimal("3.5")
    assert readback.sender_balance_before_ilc == Decimal("10")
    assert readback.sender_balance_after_ilc == Decimal("6.5")
    assert readback.recipient_balance_after_ilc == Decimal("3.5")
    assert len(readback.record_sha256) == 64


def test_zero_amount_transfer_raises(lmdb_env, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)

    with pytest.raises(ValueError, match="invalid_envelope_amount_not_positive"):
        _execute(ledger, nonce_store, _signed_intent(key_uri, Decimal("0")), private_key)


def test_transaction_is_atomic_on_balance_corruption(lmdb_env, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    with ledger._env.begin(write=True, db=ledger._balances_db) as txn:
        txn.put(SENDER_AGENT_ID.encode("ascii"), b"NaN")

    with pytest.raises(ValueError, match="invalid_ilc_balance"):
        _execute(ledger, nonce_store, _signed_intent(key_uri), private_key)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0


def test_seed_balance_for_test_requires_explicit_authorization(
    lmdb_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ILC_TEST_BALANCE_SEED_AUTHORIZED", raising=False)
    ledger = ILCTransferLedger(lmdb_env)

    with pytest.raises(ValueError, match="test_balance_seed_not_authorized"):
        ledger.seed_balance_for_test(SENDER_AGENT_ID, Decimal("1"))


def test_nonce_store_must_share_lmdb_env(
    tmp_path: Path,
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    other_env = lmdb.open(str(tmp_path / "other.lmdb"), max_dbs=4, map_size=8 * 1024 * 1024)
    try:
        with pytest.raises(ValueError, match="transfer_nonce_store_env_mismatch"):
            _execute(ledger, ActionNonceStore(other_env), _signed_intent(key_uri), private_key)
    finally:
        other_env.close()


def test_deterministic_transfer_id_for_same_payload_different_store(
    tmp_path: Path,
    key_uri: str,
    private_key,
) -> None:
    ids: list[str] = []
    for index in range(2):
        env = lmdb.open(str(tmp_path / f"ledger-{index}.lmdb"), max_dbs=8, map_size=8 * 1024 * 1024)
        try:
            ledger = ILCTransferLedger(env)
            nonce_store = ActionNonceStore(env)
            _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
            ids.append(
                _execute(ledger, nonce_store, _signed_intent(key_uri), private_key).transfer_id
            )
        finally:
            env.close()

    assert ids[0] == ids[1]


def test_duplicate_transfer_id_collision_rolls_back_state(
    lmdb_env,
    key_uri: str,
    private_key,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    forced_transfer_id = "1" * 64
    forced_record_hash = "2" * 64
    hash_calls: list[dict[str, object]] = []

    def _forced_hash(_payload: dict[str, object]) -> str:
        hash_calls.append(_payload)
        return forced_transfer_id if len(hash_calls) in {1, 3} else forced_record_hash

    monkeypatch.setattr("ilc_core.value_action.ilc_transfer_ledger._sha256_hex", _forced_hash)
    _execute(ledger, nonce_store, _signed_intent(key_uri, nonce=_nonce(SENDER_AGENT_ID, 1)), private_key)

    with pytest.raises(ValueError, match="transfer_record_duplicate"):
        _execute(
            ledger,
            nonce_store,
            _signed_intent(key_uri, nonce=_nonce(SENDER_AGENT_ID, 2)),
            private_key,
        )

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 1
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("6.5")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("3.5")


def test_unsigned_transfer_rejected_before_nonce_or_balance_mutation(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))

    with pytest.raises(ValueError, match="transfer_signature_verifier_required"):
        ledger.execute_transfer(_intent(), nonce_store)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("10")


def test_signature_failure_rejected_before_nonce_or_balance_mutation(
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    signed = _signed_intent(key_uri)
    signature = signed.cose_signature or b""
    tampered = replace(signed, cose_signature=signature[:-1] + bytes([signature[-1] ^ 0x01]))
    public_key_bytes = private_key.public_key().public_bytes_raw()

    with pytest.raises(ValueError, match="transfer_signature_invalid"):
        ledger.execute_transfer(
            tampered,
            nonce_store,
            signature_verifier=LocalEd25519SigningProvider(),
            signer_authority=_SignerAuthority(SENDER_AGENT_ID, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("10")


def test_unbound_signer_rejected_before_nonce_or_balance_mutation(
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    signed = _signed_intent(key_uri)
    public_key_bytes = private_key.public_key().public_bytes_raw()

    with pytest.raises(ValueError, match="transfer_signer_not_authorized"):
        ledger.execute_transfer(
            signed,
            nonce_store,
            signature_verifier=LocalEd25519SigningProvider(),
            signer_authority=_SignerAuthority("c" * 96, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("10")


def test_module_has_no_disallowed_runtime_patterns() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "EpochSettlementRecord" not in source
    assert "epoch_settlement_record" not in source
    assert "float" not in source
    assert "\nassert " not in source
    assert "uuid" not in source
    assert "monotonic" not in source
    assert ILC_TRANSFER_LEDGER_VERSION == "ilc_transfer_ledger_04.v0.1"
