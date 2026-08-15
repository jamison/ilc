# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for GAP-AGENT-HARNESS-01b guarded signing provider runtime."""

from __future__ import annotations

import base64
from decimal import Decimal
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from ilc_core.crypto.cose_sign1 import cose_sign1_decode
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.local_signing_provider import (
    GuardedLocalEd25519SigningProvider,
    ILCSigningProvider,
    LocalEd25519SigningProvider,
    resolve_signing_key,
)


SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96


@pytest.fixture
def private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


@pytest.fixture
def private_key_pem(private_key: ed25519.Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        NoEncryption(),
    )


def _intent():
    return ILCTransferIntent.create(
        sender_agent_id=SENDER_AGENT_ID,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=Decimal("1.25"),
        nonce="agent-a:01b:1",
        epoch=0,
        memo="guarded provider test",
        graph_context_anchor="graph:guarded-provider",
    )


def test_ilc_signing_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        ILCSigningProvider()


def test_local_ed25519_provider_subclasses_abstract_interface() -> None:
    assert issubclass(LocalEd25519SigningProvider, ILCSigningProvider)
    assert isinstance(LocalEd25519SigningProvider(), ILCSigningProvider)


def test_resolve_signing_key_empty_kid_raises() -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_empty"):
        resolve_signing_key("")


def test_resolve_signing_key_rejects_parent_directory() -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_invalid_characters"):
        resolve_signing_key("../etc/passwd")


def test_resolve_signing_key_rejects_forward_slash() -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_invalid_characters"):
        resolve_signing_key("a/b")


def test_resolve_signing_key_rejects_backslash() -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_invalid_characters"):
        resolve_signing_key("a\\b")


def test_resolve_signing_key_rejects_oversized_kid() -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_too_long"):
        resolve_signing_key("k" * 257)


def test_resolve_signing_key_env_uri_returns_decoded_bytes(
    monkeypatch: pytest.MonkeyPatch,
    private_key_pem: bytes,
) -> None:
    monkeypatch.setenv("MY_KEY", base64.b64encode(private_key_pem).decode("ascii"))

    assert resolve_signing_key("env://MY_KEY") == private_key_pem


def test_resolve_signing_key_env_uri_absent_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MY_KEY", raising=False)

    with pytest.raises(ValueError, match="signing_provider_env_var_not_set:MY_KEY"):
        resolve_signing_key("env://MY_KEY")


def test_resolve_signing_key_env_uri_bad_base64_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MY_KEY", "not base64!!!")

    with pytest.raises(ValueError, match="signing_provider_env_var_invalid_base64"):
        resolve_signing_key("env://MY_KEY")


@pytest.mark.parametrize("kid", ["env://", "env://../SECRET", "env://A/B", "env://A\\B"])
def test_resolve_signing_key_env_uri_rejects_invalid_envvar_name(kid: str) -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_invalid_characters"):
        resolve_signing_key(kid)


def test_resolve_signing_key_env_uri_rejects_empty_decoded_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MY_KEY", "")

    with pytest.raises(ValueError, match="signing_provider_env_var_invalid_base64"):
        resolve_signing_key("env://MY_KEY")


def test_resolve_signing_key_env_uri_rejects_oversized_encoded_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MY_KEY", "A" * (22 * 1024))

    with pytest.raises(ValueError, match="signing_provider_env_var_too_large"):
        resolve_signing_key("env://MY_KEY")


def test_resolve_signing_key_unknown_kid_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="signing_provider_kid_not_found:unknown_kid"):
        resolve_signing_key("unknown_kid", tmp_path)


def test_resolve_signing_key_reads_pem_from_key_store(
    tmp_path: Path,
    private_key_pem: bytes,
) -> None:
    key_file = tmp_path / "agent-key.pem"
    key_file.write_bytes(private_key_pem)
    key_file.chmod(0o600)

    assert resolve_signing_key("agent-key", tmp_path) == private_key_pem


def test_resolve_signing_key_reads_key_suffix_from_key_store(
    tmp_path: Path,
    private_key_pem: bytes,
) -> None:
    key_file = tmp_path / "agent-key.key"
    key_file.write_bytes(private_key_pem)
    key_file.chmod(0o600)

    assert resolve_signing_key("agent-key", tmp_path) == private_key_pem


def test_resolve_signing_key_rejects_oversized_key_file(tmp_path: Path) -> None:
    key_file = tmp_path / "oversized.pem"
    key_file.write_bytes(b"x" * (16 * 1024 + 1))
    key_file.chmod(0o600)

    with pytest.raises(ValueError, match="signing_provider_key_file_too_large"):
        resolve_signing_key("oversized", tmp_path)


def test_resolve_signing_key_rejects_group_readable_key_file(
    tmp_path: Path,
    private_key_pem: bytes,
) -> None:
    key_file = tmp_path / "exposed.pem"
    key_file.write_bytes(private_key_pem)
    key_file.chmod(0o640)

    with pytest.raises(ValueError, match="signing_provider_key_file_permissions"):
        resolve_signing_key("exposed", tmp_path)


def test_resolve_signing_key_rejects_symlink(
    tmp_path: Path,
    private_key_pem: bytes,
) -> None:
    target = tmp_path / "target.pem"
    target.write_bytes(private_key_pem)
    target.chmod(0o600)
    link = tmp_path / "linked.pem"
    link.symlink_to(target)

    with pytest.raises(ValueError, match="signing_provider_key_file_symlink_rejected"):
        resolve_signing_key("linked", tmp_path)


def test_guarded_provider_rejects_unauthorized_action_type(
    tmp_path: Path,
    private_key_pem: bytes,
) -> None:
    key_file = tmp_path / "agent-key.pem"
    key_file.write_bytes(private_key_pem)
    key_file.chmod(0o600)
    provider = GuardedLocalEd25519SigningProvider(
        "agent-key",
        tmp_path,
        allowed_action_types=frozenset(),
    )

    with pytest.raises(
        ValueError,
        match="signing_provider_action_type_not_authorized:ILC_TRANSFER",
    ):
        provider.sign_envelope(_intent())


def test_guarded_provider_signs_default_ilc_transfer(
    tmp_path: Path,
    private_key_pem: bytes,
    private_key: ed25519.Ed25519PrivateKey,
) -> None:
    key_file = tmp_path / "agent-key.pem"
    key_file.write_bytes(private_key_pem)
    key_file.chmod(0o600)
    provider = GuardedLocalEd25519SigningProvider("agent-key", tmp_path)

    signed = provider.sign_envelope(_intent())

    assert signed.cose_signature is not None
    assert provider.verify_envelope_signature(
        signed,
        private_key.public_key().public_bytes_raw(),
    )
    assert cose_sign1_decode(signed.cose_signature)["kid"] == b"agent-key"


def test_guarded_provider_resolves_env_key_and_public_key(
    monkeypatch: pytest.MonkeyPatch,
    private_key_pem: bytes,
    private_key: ed25519.Ed25519PrivateKey,
) -> None:
    monkeypatch.setenv("MY_KEY", base64.b64encode(private_key_pem).decode("ascii"))
    provider = GuardedLocalEd25519SigningProvider("env://MY_KEY")

    signed = provider.sign_envelope(_intent())

    assert signed.cose_signature is not None
    assert provider.resolve_public_key() == private_key.public_key().public_bytes_raw()
    assert cose_sign1_decode(signed.cose_signature)["kid"] == b"env://MY_KEY"
