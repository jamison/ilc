# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from ilc_core.crypto.cose_sign1 import cose_sign1_verify
from ilc_core.encoding.dag_cbor import validate_canonical_ilc_dag_cbor
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.local_signing_provider import (
    LOCAL_SIGNING_PROVIDER_VERSION,
    LocalEd25519SigningProvider,
    UnsupportedKeyProviderError,
)

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
MODULE_PATH = Path("ilc_core/value_action/local_signing_provider.py")


@pytest.fixture
def private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


@pytest.fixture
def key_uri(tmp_path: Path, private_key: ed25519.Ed25519PrivateKey) -> str:
    key_path = tmp_path / "agent-ed25519.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            NoEncryption(),
        )
    )
    return key_path.as_uri()


def _intent():
    return ILCTransferIntent.create(
        sender_agent_id=SENDER_AGENT_ID,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=Decimal("1.25"),
        nonce="agent-a:1",
        epoch=0,
        memo="settled transfer intent",
        graph_context_anchor="graph:context-root",
    )


def test_sign_and_verify_roundtrip(key_uri: str, private_key: ed25519.Ed25519PrivateKey) -> None:
    provider = LocalEd25519SigningProvider()
    signed = provider.sign_envelope(_intent(), key_uri)
    public_bytes = private_key.public_key().public_bytes_raw()

    assert provider.verify_envelope_signature(signed, public_bytes) is True


def test_non_file_uri_raises() -> None:
    provider = LocalEd25519SigningProvider()

    with pytest.raises(UnsupportedKeyProviderError, match="unsupported_key_provider_scheme"):
        provider.sign_envelope(_intent(), "coinbase://agent-key")


def test_canonical_payload_is_deterministic() -> None:
    provider = LocalEd25519SigningProvider()
    env = _intent()

    assert provider.canonical_payload_dag_cbor(env) == provider.canonical_payload_dag_cbor(env)


def test_signature_bytes_nonempty(key_uri: str) -> None:
    signed = LocalEd25519SigningProvider().sign_envelope(_intent(), key_uri)

    assert signed.cose_signature is not None
    assert len(signed.cose_signature) > 0


def test_tampered_envelope_fails_verify(
    key_uri: str,
    private_key: ed25519.Ed25519PrivateKey,
) -> None:
    provider = LocalEd25519SigningProvider()
    signed = provider.sign_envelope(_intent(), key_uri)
    tampered = replace(signed, amount_ilc=Decimal("2.25"))
    public_bytes = private_key.public_key().public_bytes_raw()

    assert provider.verify_envelope_signature(tampered, public_bytes) is False


def test_no_signature_verify_raises(private_key: ed25519.Ed25519PrivateKey) -> None:
    public_bytes = private_key.public_key().public_bytes_raw()

    with pytest.raises(ValueError, match="invalid_envelope_no_signature"):
        LocalEd25519SigningProvider().verify_envelope_signature(_intent(), public_bytes)


def test_cose_payload_is_canonical_dag_cbor(
    key_uri: str,
    private_key: ed25519.Ed25519PrivateKey,
) -> None:
    provider = LocalEd25519SigningProvider()
    signed = provider.sign_envelope(_intent(), key_uri)
    verified = cose_sign1_verify(
        signed.cose_signature or b"",
        private_key.public_key(),
    )

    validate_canonical_ilc_dag_cbor(verified["payload"])
    assert verified["payload"] == provider.canonical_payload_dag_cbor(signed)


def test_amount_uses_canonical_decimal_string() -> None:
    env = ILCTransferIntent.create(
        sender_agent_id=SENDER_AGENT_ID,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=Decimal("1.2300"),
        nonce="agent-a:2",
        epoch=0,
    )

    payload = LocalEd25519SigningProvider().canonical_payload_dict(env)
    assert payload["amount_ilc"] == "1.23"


def test_resolve_public_key_returns_raw_ed25519_bytes(
    key_uri: str,
    private_key: ed25519.Ed25519PrivateKey,
) -> None:
    provider = LocalEd25519SigningProvider()

    assert provider.resolve_public_key(key_uri) == private_key.public_key().public_bytes_raw()


def test_provider_capabilities_are_local_and_non_exporting() -> None:
    caps = LocalEd25519SigningProvider().provider_capabilities()

    assert caps == {
        "attestation": False,
        "detached_signing": False,
        "key_exportable": False,
        "scheme": "file",
    }
    assert LOCAL_SIGNING_PROVIDER_VERSION == "local_signing_provider_02.v0.1"


def test_schema_module_does_not_advertise_deferred_algorithms() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "secp256k1" not in source
    assert "EIP-712" not in source
