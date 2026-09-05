# SPDX-License-Identifier: AGPL-3.0-only
"""Local Ed25519/COSE Sign1 provider for value-action envelopes."""
from __future__ import annotations

import base64
import binascii
import os
import stat
from abc import ABC, abstractmethod
from dataclasses import replace
from pathlib import Path
from urllib.parse import unquote, urlparse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from ilc_core.crypto.cose_sign1 import cose_sign1_sign, cose_sign1_verify
from ilc_core.encoding.dag_cbor import encode_dag_cbor, validate_canonical_ilc_dag_cbor
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.value_action.ilc_transfer_intent import AgentActionEnvelope, validate_envelope

LOCAL_SIGNING_PROVIDER_VERSION = "local_signing_provider_02.v0.1"
_MAX_PRIVATE_KEY_PEM_BYTES = 16 * 1024
_MAX_PRIVATE_KEY_PEM_B64_BYTES = ((_MAX_PRIVATE_KEY_PEM_BYTES + 2) // 3) * 4 + 4
_MAX_SIGNING_PROVIDER_KID_BYTES = 256


class UnsupportedKeyProviderError(ValueError):
    """Raised when a key URI scheme is outside this provider's RC scope."""


class ILCSigningProvider(ABC):
    """Abstract signing provider interface for AgentActionEnvelope signatures."""

    @abstractmethod
    def sign_envelope(
        self,
        env: AgentActionEnvelope,
        *args: object,
        kid: bytes | None = None,
        external_aad: bytes = b"",
    ) -> AgentActionEnvelope:
        """Return a copy of env with a COSE_Sign1 signature over its payload."""

    @abstractmethod
    def verify_envelope_signature(
        self,
        env: AgentActionEnvelope,
        public_key_bytes: bytes,
        *,
        external_aad: bytes = b"",
    ) -> bool:
        """Return True only when env's signature verifies for public_key_bytes."""


def resolve_signing_key(kid: str, key_store_path: Path | None = None) -> bytes:
    """Resolve local signing key material by key ID without exposing secrets."""
    if not isinstance(kid, str):
        raise ValueError("signing_provider_kid_invalid_type")
    if not kid:
        raise ValueError("signing_provider_kid_empty")
    try:
        kid_bytes = kid.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("signing_provider_kid_invalid_characters") from exc
    if len(kid_bytes) > _MAX_SIGNING_PROVIDER_KID_BYTES:
        raise ValueError("signing_provider_kid_too_long")
    if kid.startswith("env://"):
        envvar = kid[len("env://") :]
        if not envvar or ".." in envvar or "/" in envvar or "\\" in envvar:
            raise ValueError("signing_provider_kid_invalid_characters")
        raw_value = os.environ.get(envvar)
        if raw_value is None:
            raise ValueError(f"signing_provider_env_var_not_set:{envvar}")
        try:
            encoded_value = raw_value.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError("signing_provider_env_var_invalid_base64") from exc
        if len(encoded_value) > _MAX_PRIVATE_KEY_PEM_B64_BYTES:
            raise ValueError("signing_provider_env_var_too_large")
        try:
            decoded = base64.b64decode(encoded_value, validate=True)
        except binascii.Error as exc:
            raise ValueError("signing_provider_env_var_invalid_base64") from exc
        if not decoded:
            raise ValueError("signing_provider_env_var_invalid_base64")
        if len(decoded) > _MAX_PRIVATE_KEY_PEM_BYTES:
            raise ValueError("signing_provider_env_var_too_large")
        return decoded
    if ".." in kid or "/" in kid or "\\" in kid:
        raise ValueError("signing_provider_kid_invalid_characters")
    if key_store_path is not None:
        root = Path(key_store_path)
        for suffix in (".pem", ".key"):
            candidate = root / f"{kid}{suffix}"
            try:
                return _read_private_key_file(candidate)
            except ValueError:
                raise
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise ValueError("signing_provider_key_file_unreadable") from exc
    raise ValueError(f"signing_provider_kid_not_found:{kid}")


def _load_ed25519_private_key_from_pem(
    key_bytes: bytes,
) -> ed25519.Ed25519PrivateKey:
    try:
        key = load_pem_private_key(key_bytes, password=None)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_private_key_pem") from exc
    if not isinstance(key, ed25519.Ed25519PrivateKey):
        raise ValueError("invalid_key_type_not_ed25519")
    return key


class LocalEd25519SigningProvider(ILCSigningProvider):
    """File-backed Ed25519 provider for AgentActionEnvelope COSE signatures."""

    def sign_envelope(
        self,
        env: AgentActionEnvelope,
        key_uri: str,
        *,
        kid: bytes | None = None,
        external_aad: bytes = b"",
    ) -> AgentActionEnvelope:
        """Return a copy of env with a COSE_Sign1 signature over its payload."""
        validate_envelope(env)
        if kid is not None and not isinstance(kid, bytes):
            raise ValueError("invalid_signing_provider_kid")
        if not isinstance(external_aad, bytes):
            raise ValueError("invalid_signing_provider_external_aad")
        private_key = self._load_private_key(key_uri)
        payload = self.canonical_payload_dag_cbor(env)
        cose_bytes = cose_sign1_sign(
            payload,
            private_key,
            kid=kid,
            external_aad=external_aad,
        )
        return replace(env, cose_signature=cose_bytes)

    def verify_envelope_signature(
        self,
        env: AgentActionEnvelope,
        public_key_bytes: bytes,
        *,
        external_aad: bytes = b"",
    ) -> bool:
        """Verify signature validity and payload equality for the current env."""
        validate_envelope(env)
        if env.cose_signature is None:
            raise ValueError("invalid_envelope_no_signature")
        if not isinstance(external_aad, bytes):
            raise ValueError("invalid_signing_provider_external_aad")
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        except ValueError:
            return False
        try:
            decoded = cose_sign1_verify(
                env.cose_signature,
                public_key,
                external_aad=external_aad,
            )
        except (InvalidSignature, ValueError):
            return False
        return decoded.get("payload") == self.canonical_payload_dag_cbor(env)

    def resolve_public_key(self, key_uri: str) -> bytes:
        """Return raw 32-byte public key bytes for a local private-key URI."""
        private_key = self._load_private_key(key_uri)
        return private_key.public_key().public_bytes_raw()

    def provider_capabilities(self) -> dict[str, bool | str]:
        """Expose ADM-003-style provider capabilities."""
        return {
            "attestation": False,
            "detached_signing": False,
            "key_exportable": False,
            "scheme": "file",
        }

    def canonical_payload_dict(self, env: AgentActionEnvelope) -> dict[str, object]:
        """Return the signable envelope payload without signature fields."""
        validate_envelope(env)
        payload: dict[str, object] = {
            "action_type": env.action_type.value,
            "amount_ilc": decimal_to_canonical_string(env.amount_ilc),
            "epoch": env.epoch,
            "nonce": env.nonce,
            "recipient_agent_id": env.recipient_agent_id,
            "sender_agent_id": env.sender_agent_id,
            "version": "agent_action_envelope.ilc_transfer.v0.1",
        }
        if env.memo is not None:
            payload["memo"] = env.memo
        if env.graph_context_anchor is not None:
            payload["graph_context_anchor"] = env.graph_context_anchor
        if env.signed_at_epoch is not None:
            payload["signed_at_epoch"] = env.signed_at_epoch
        return payload

    def canonical_payload_dag_cbor(self, env: AgentActionEnvelope) -> bytes:
        """Return canonical ILC DAG-CBOR bytes for the signable payload."""
        payload = encode_dag_cbor(self.canonical_payload_dict(env))
        validate_canonical_ilc_dag_cbor(payload)
        return payload

    def _load_private_key(self, key_uri: str) -> ed25519.Ed25519PrivateKey:
        key_path = self._parse_file_uri(key_uri)
        try:
            key_bytes = _read_private_key_file(key_path)
        except ValueError:
            raise
        except OSError as exc:
            raise ValueError("invalid_file_key_uri_unreadable") from exc
        return _load_ed25519_private_key_from_pem(key_bytes)

    def _parse_file_uri(self, key_uri: str) -> Path:
        if not isinstance(key_uri, str):
            raise UnsupportedKeyProviderError("unsupported_key_provider_scheme")
        parsed = urlparse(key_uri)
        if parsed.scheme != "file":
            raise UnsupportedKeyProviderError("unsupported_key_provider_scheme")
        if parsed.netloc not in {"", "localhost"}:
            raise UnsupportedKeyProviderError("unsupported_key_provider_authority")
        if not parsed.path:
            raise ValueError("invalid_file_key_uri")
        path = Path(unquote(parsed.path))
        if not path.is_absolute():
            raise ValueError("invalid_file_key_uri_not_absolute")
        return path


def _read_private_key_file(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        file_stat = os.fstat(fd)
        if not stat.S_ISREG(file_stat.st_mode):
            raise ValueError("invalid_file_key_uri_not_file")
        if file_stat.st_size > _MAX_PRIVATE_KEY_PEM_BYTES:
            raise ValueError("invalid_file_key_uri_too_large")
        if file_stat.st_mode & 0o077:
            raise ValueError("invalid_file_key_uri_permissions")
        with os.fdopen(fd, "rb") as handle:
            fd = -1
            return handle.read(_MAX_PRIVATE_KEY_PEM_BYTES + 1)
    finally:
        if fd >= 0:
            os.close(fd)


class GuardedLocalEd25519SigningProvider(LocalEd25519SigningProvider):
    """Kid-resolved local provider with an action-type allowlist."""

    def __init__(
        self,
        kid: str,
        key_store_path: Path | None = None,
        allowed_action_types: frozenset[str] = frozenset({"ILC_TRANSFER"}),
    ) -> None:
        if not isinstance(allowed_action_types, frozenset):
            raise ValueError("signing_provider_allowed_action_types_invalid")
        self.kid = kid
        self.allowed_action_types = allowed_action_types
        self._private_key = _load_ed25519_private_key_from_pem(
            resolve_signing_key(kid, key_store_path)
        )

    def sign_envelope(
        self,
        env: AgentActionEnvelope,
        *,
        kid: bytes | None = None,
        external_aad: bytes = b"",
    ) -> AgentActionEnvelope:
        """Sign env after checking the configured action-type allowlist."""
        validate_envelope(env)
        action_type = env.action_type.value
        if action_type not in self.allowed_action_types:
            raise ValueError(f"signing_provider_action_type_not_authorized:{action_type}")
        if kid is not None and not isinstance(kid, bytes):
            raise ValueError("invalid_signing_provider_kid")
        if not isinstance(external_aad, bytes):
            raise ValueError("invalid_signing_provider_external_aad")
        cose_kid = kid if kid is not None else self.kid.encode("utf-8")
        cose_bytes = cose_sign1_sign(
            self.canonical_payload_dag_cbor(env),
            self._private_key,
            kid=cose_kid,
            external_aad=external_aad,
        )
        return replace(env, cose_signature=cose_bytes)

    def resolve_public_key(self, key_uri: str | None = None) -> bytes:  # type: ignore[override]
        """Return raw 32-byte public key bytes for the resolved key."""
        if key_uri is not None:
            return super().resolve_public_key(key_uri)
        return self._private_key.public_key().public_bytes_raw()


__all__ = [
    "GuardedLocalEd25519SigningProvider",
    "ILCSigningProvider",
    "LOCAL_SIGNING_PROVIDER_VERSION",
    "LocalEd25519SigningProvider",
    "UnsupportedKeyProviderError",
    "resolve_signing_key",
]
