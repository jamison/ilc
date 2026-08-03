# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
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
from ilc_core.value_action.action_nonce_store import ActionNonceStore
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger, _encode_balance
from ilc_core.value_action.local_signing_provider import LocalEd25519SigningProvider
from ilc_core.value_action.ilc_transfer_readback_verifier import (
    ILC_TRANSFER_READBACK_VERSION,
    READBACK_PATH,
    ILCTransferReadbackVerifier,
)

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
MODULE_PATH = Path("ilc_core/value_action/ilc_transfer_readback_verifier.py")


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
    env = lmdb.open(str(tmp_path / "ilc-transfer-readback.lmdb"), max_dbs=8, map_size=8 * 1024 * 1024)
    try:
        yield env
    finally:
        env.close()


@pytest.fixture(autouse=True)
def transfer_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(ilc_transfer_intent, "ILC_TRANSFER_ENABLED", True)


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
    return key_path.as_uri()


def _nonce(agent_id: str, counter: int) -> str:
    return f"{agent_id}:nonce:{counter:020d}"


def _intent():
    return ILCTransferIntent.create(
        sender_agent_id=SENDER_AGENT_ID,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=Decimal("3.5"),
        nonce=_nonce(SENDER_AGENT_ID, 1),
        epoch=0,
        memo="readback test",
    )


def _seed_balance(ledger: ILCTransferLedger, agent_id: str, amount: Decimal) -> None:
    with ledger._env.begin(write=True, db=ledger._balances_db) as txn:
        txn.put(agent_id.encode("ascii"), _encode_balance(amount))


def _execute_transfer(lmdb_env, key_uri: str, private_key: ed25519.Ed25519PrivateKey):
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    provider = LocalEd25519SigningProvider()
    public_key_bytes = private_key.public_key().public_bytes_raw()
    _seed_balance(ledger, SENDER_AGENT_ID, Decimal("10"))
    entry = ledger.execute_transfer(
        provider.sign_envelope(_intent(), key_uri),
        nonce_store,
        signature_verifier=provider,
        signer_authority=_SignerAuthority(SENDER_AGENT_ID, public_key_bytes),
        sender_public_key_bytes=public_key_bytes,
    )
    return ledger, entry


def test_post_transfer_balance_matches(lmdb_env, key_uri: str, private_key) -> None:
    ledger, _entry = _execute_transfer(lmdb_env, key_uri, private_key)
    verifier = ILCTransferReadbackVerifier()

    assert verifier.verify_post_transfer_balance(
        ledger,
        SENDER_AGENT_ID,
        Decimal("6.5"),
    )


def test_receipt_retrievable_after_commit(lmdb_env, key_uri: str, private_key) -> None:
    ledger, entry = _execute_transfer(lmdb_env, key_uri, private_key)
    verifier = ILCTransferReadbackVerifier()

    assert verifier.verify_transfer_record_retrievable(ledger, entry.transfer_id)


def test_readback_path_is_python_lmdb() -> None:
    assert READBACK_PATH == "PYTHON_LMDB_AUTHORITATIVE"


def test_verify_fails_if_balance_wrong(lmdb_env, key_uri: str, private_key) -> None:
    ledger, _entry = _execute_transfer(lmdb_env, key_uri, private_key)
    verifier = ILCTransferReadbackVerifier()

    assert not verifier.verify_post_transfer_balance(
        ledger,
        SENDER_AGENT_ID,
        Decimal("6.4"),
    )


def test_verify_fails_if_receipt_absent(lmdb_env) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    verifier = ILCTransferReadbackVerifier()

    assert not verifier.verify_transfer_record_retrievable(ledger, "f" * 64)


def test_invalid_expected_balance_rejected(lmdb_env, key_uri: str, private_key) -> None:
    ledger, _entry = _execute_transfer(lmdb_env, key_uri, private_key)
    verifier = ILCTransferReadbackVerifier()

    with pytest.raises(ValueError, match="invalid_expected_readback_balance"):
        verifier.verify_post_transfer_balance(ledger, SENDER_AGENT_ID, "6.5")  # type: ignore[arg-type]


def test_tampered_transfer_record_fails_closed(lmdb_env, key_uri: str, private_key) -> None:
    ledger, entry = _execute_transfer(lmdb_env, key_uri, private_key)
    with ledger._env.begin(write=True, db=ledger._transfers_db) as txn:
        raw = txn.get(entry.transfer_id.encode("ascii"))
        assert raw is not None
        payload = json.loads(raw.decode("utf-8"))
        payload["amount_ilc"] = "3.6"
        txn.put(
            entry.transfer_id.encode("ascii"),
            json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
                "utf-8"
            ),
        )

    with pytest.raises(ValueError, match="transfer_record_sha256_mismatch"):
        ledger.get_transfer_record(entry.transfer_id)


def test_module_has_no_disallowed_runtime_patterns() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "EpochSettlementRecord" not in source
    assert "gRPC" not in source
    assert "grpc" not in source
    assert "float" not in source
    assert "\nassert " not in source
    assert ILC_TRANSFER_READBACK_VERSION == "ilc_transfer_readback_verifier_06.v0.1"
