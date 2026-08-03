# SPDX-License-Identifier: AGPL-3.0-only
"""Local Ed25519/COSE Sign1 provider for value-action envelopes."""
from __future__ import annotations

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


class UnsupportedKeyProviderError(ValueError):
    """Raised when a key URI scheme is outside this provider's RC scope."""


class LocalEd25519SigningProvider:
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
        except (InvalidSignature, ValueError, TypeError):
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
            "memo": env.memo,
            "nonce": env.nonce,
            "recipient_agent_id": env.recipient_agent_id,
            "sender_agent_id": env.sender_agent_id,
            "version": "agent_action_envelope.ilc_transfer.v0.1",
        }
        if env.graph_context_anchor is not None:
            payload["graph_context_anchor"] = env.graph_context_anchor
        return payload

    def canonical_payload_dag_cbor(self, env: AgentActionEnvelope) -> bytes:
        """Return canonical ILC DAG-CBOR bytes for the signable payload."""
        payload = encode_dag_cbor(self.canonical_payload_dict(env))
        validate_canonical_ilc_dag_cbor(payload)
        return payload

    def _load_private_key(self, key_uri: str) -> ed25519.Ed25519PrivateKey:
        key_path = self._parse_file_uri(key_uri)
        key = load_pem_private_key(key_path.read_bytes(), password=None)
        if not isinstance(key, ed25519.Ed25519PrivateKey):
            raise ValueError("invalid_key_type_not_ed25519")
        return key

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
        return Path(unquote(parsed.path))


__all__ = [
    "LOCAL_SIGNING_PROVIDER_VERSION",
    "LocalEd25519SigningProvider",
    "UnsupportedKeyProviderError",
]
