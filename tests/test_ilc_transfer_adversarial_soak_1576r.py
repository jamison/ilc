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
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.ilc_transfer_ledger import (
    ILCTransferLedger,
    ILCTransferLedgerEntry,
    InsufficientBalanceError,
)
from ilc_core.value_action.ilc_transfer_receipt import (
    build_transfer_receipt,
    compute_transfer_batch_root,
    verify_receipt,
)
from ilc_core.value_action.local_signing_provider import LocalEd25519SigningProvider

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
THIRD_AGENT_ID = "c" * 96
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
    env = lmdb.open(
        str(tmp_path / "ilc-transfer-adversarial.lmdb"),
        max_dbs=8,
        map_size=8 * 1024 * 1024,
    )
    try:
        yield env
    finally:
        env.close()


@pytest.fixture
def provider() -> LocalEd25519SigningProvider:
    return LocalEd25519SigningProvider()


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


@pytest.fixture(autouse=True)
def transfer_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ilc_transfer_intent, "ILC_TRANSFER_ENABLED", True)
    monkeypatch.setenv("ILC_TEST_BALANCE_SEED_AUTHORIZED", "1")


def _nonce(agent_id: str, counter: int) -> str:
    return f"{agent_id}:nonce:{counter:020d}"


def _intent(
    amount: Decimal = Decimal("100"),
    *,
    nonce_counter: int = 1,
    sender_agent_id: str = SENDER_AGENT_ID,
    recipient_agent_id: str = RECIPIENT_AGENT_ID,
    memo: str | None = "adversarial transfer",
):
    return ILCTransferIntent.create(
        sender_agent_id=sender_agent_id,
        recipient_agent_id=recipient_agent_id,
        amount_ilc=amount,
        nonce=_nonce(sender_agent_id, nonce_counter),
        epoch=0,
        memo=memo,
        graph_context_anchor="graph:transfer-context",
    )


def _seed_balance(ledger: ILCTransferLedger, agent_id: str, amount: Decimal) -> None:
    ledger.seed_balance_for_test(agent_id, amount)


def _execute(
    ledger: ILCTransferLedger,
    nonce_store: ActionNonceStore,
    env,
    *,
    provider: LocalEd25519SigningProvider,
    private_key: ed25519.Ed25519PrivateKey,
) -> ILCTransferLedgerEntry:
    public_key_bytes = private_key.public_key().public_bytes_raw()
    return ledger.execute_transfer(
        env,
        nonce_store,
        signature_verifier=provider,
        signer_authority=_SignerAuthority(env.sender_agent_id, public_key_bytes),
        sender_public_key_bytes=public_key_bytes,
    )


def _signed(
    env,
    *,
    provider: LocalEd25519SigningProvider,
    key_uri: str,
):
    return provider.sign_envelope(env, key_uri)


def test_replay_same_nonce_rejected(lmdb_env, provider, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)

    _execute(ledger, nonce_store, signed, provider=provider, private_key=private_key)
    with pytest.raises(NonceReplayError, match="nonce_replay_rejected"):
        _execute(ledger, nonce_store, signed, provider=provider, private_key=private_key)


def test_double_spend_insufficient_balance(lmdb_env, provider, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("100"))
    first = _signed(_intent(nonce_counter=1), provider=provider, key_uri=key_uri)
    second = _signed(_intent(nonce_counter=2), provider=provider, key_uri=key_uri)

    _execute(ledger, nonce_store, first, provider=provider, private_key=private_key)
    with pytest.raises(InsufficientBalanceError, match="insufficient_balance"):
        _execute(ledger, nonce_store, second, provider=provider, private_key=private_key)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 1
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("0")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("100")


def test_non_finite_decimal_nan_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _intent(Decimal("NaN"))


def test_non_finite_decimal_inf_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _intent(Decimal("Infinity"))


def test_self_transfer_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_self_transfer"):
        _intent(sender_agent_id=SENDER_AGENT_ID, recipient_agent_id=SENDER_AGENT_ID)


def test_negative_amount_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_amount_not_positive"):
        _intent(Decimal("-1"))


def test_zero_amount_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_amount_not_positive"):
        _intent(Decimal("0"))


def test_activation_guard_blocks_execute_transfer(
    lmdb_env,
    provider,
    key_uri: str,
    private_key,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)
    monkeypatch.setattr(ilc_transfer_intent, "ILC_TRANSFER_ENABLED", False)

    with pytest.raises(ValueError, match="transfer_not_enabled"):
        _execute(ledger, nonce_store, signed, provider=provider, private_key=private_key)


def test_tampered_signature_rejected(provider, key_uri: str, private_key) -> None:
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)
    signature = signed.cose_signature or b""
    tampered = replace(signed, cose_signature=signature[:-1] + bytes([signature[-1] ^ 0x01]))

    assert provider.verify_envelope_signature(
        tampered,
        private_key.public_key().public_bytes_raw(),
    ) is False


def test_tampered_amount_after_signing_rejected(provider, key_uri: str, private_key) -> None:
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)
    tampered = replace(signed, amount_ilc=Decimal("101"))

    assert provider.verify_envelope_signature(
        tampered,
        private_key.public_key().public_bytes_raw(),
    ) is False


def test_receipt_hash_changes_on_amount_tamper(lmdb_env, provider, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)
    entry = _execute(ledger, nonce_store, signed, provider=provider, private_key=private_key)
    receipt = build_transfer_receipt(entry)
    modified = replace(entry, amount_ilc=Decimal("101"))

    assert verify_receipt(receipt, modified) is False


def test_batch_root_deterministic_across_orderings(
    lmdb_env,
    provider,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))
    first = _execute(
        ledger,
        nonce_store,
        _signed(_intent(nonce_counter=1), provider=provider, key_uri=key_uri),
        provider=provider,
        private_key=private_key,
    )
    second = _execute(
        ledger,
        nonce_store,
        _signed(_intent(Decimal("50"), nonce_counter=2), provider=provider, key_uri=key_uri),
        provider=provider,
        private_key=private_key,
    )
    receipt_a = build_transfer_receipt(first)
    receipt_b = build_transfer_receipt(second)

    assert compute_transfer_batch_root([receipt_a, receipt_b]).root_sha256 == (
        compute_transfer_batch_root([receipt_b, receipt_a]).root_sha256
    )


def test_memo_too_long_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_memo_too_long"):
        _intent(memo="x" * 257)


def test_amount_type_not_accepted() -> None:
    with pytest.raises(TypeError, match="invalid_envelope_amount_not_decimal"):
        ILCTransferIntent.create(
            sender_agent_id=SENDER_AGENT_ID,
            recipient_agent_id=RECIPIENT_AGENT_ID,
            amount_ilc=1.5,  # type: ignore[arg-type]
            nonce=_nonce(SENDER_AGENT_ID, 1),
            epoch=0,
        )


def test_ledger_double_entry_conserved(lmdb_env, provider, key_uri: str, private_key) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))
    _seed_balance(ledger, RECIPIENT_AGENT_ID, Decimal("0"))
    before = ledger.get_balance(SENDER_AGENT_ID) + ledger.get_balance(RECIPIENT_AGENT_ID)
    signed = _signed(_intent(Decimal("300")), provider=provider, key_uri=key_uri)

    _execute(ledger, nonce_store, signed, provider=provider, private_key=private_key)

    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("700")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("300")
    assert ledger.get_balance(SENDER_AGENT_ID) + ledger.get_balance(RECIPIENT_AGENT_ID) == before


def test_ledger_rejects_unsigned_envelope_before_state_mutation(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))

    with pytest.raises(ValueError, match="transfer_signature_verifier_required"):
        ledger.execute_transfer(_intent(), nonce_store)

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("1000")


def test_ledger_rejects_unbound_signer_before_state_mutation(
    lmdb_env,
    provider,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)
    public_key_bytes = private_key.public_key().public_bytes_raw()

    with pytest.raises(ValueError, match="transfer_signer_not_authorized"):
        ledger.execute_transfer(
            signed,
            nonce_store,
            signature_verifier=provider,
            signer_authority=_SignerAuthority(THIRD_AGENT_ID, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("1000")


def test_ledger_rejects_tampered_signed_envelope_before_state_mutation(
    lmdb_env,
    provider,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("1000"))
    signed = _signed(_intent(), provider=provider, key_uri=key_uri)
    tampered = replace(signed, amount_ilc=Decimal("101"))
    public_key_bytes = private_key.public_key().public_bytes_raw()

    with pytest.raises(ValueError, match="transfer_signature_invalid"):
        ledger.execute_transfer(
            tampered,
            nonce_store,
            signature_verifier=provider,
            signer_authority=_SignerAuthority(SENDER_AGENT_ID, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )

    assert nonce_store.peek_counter(SENDER_AGENT_ID) == 0
    assert ledger.get_balance(SENDER_AGENT_ID) == Decimal("1000")


def test_value_moving_module_keeps_activation_and_custody_boundaries() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "ILC_TRANSFER_ENABLED = True" not in source
    assert "private_key" not in source
    assert "sender_key_material" not in source
    assert "EpochSettlementRecord" not in source
