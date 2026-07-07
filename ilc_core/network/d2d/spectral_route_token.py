# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS-SPECTRAL-01 SpectralRouteToken primitive boundary.

Phase 1573f creates this module as a non-activated cryptographic primitive
surface. The current local ``cryptography`` library is 46.0.7. ML-KEM-768
remains the primary target, but the bounded dependency probe for this phase
could not produce a vetted, importable, KAT-checked ML-KEM-768 dependency.
Therefore the committed implementation uses the explicit X25519 contingency
path and exposes that fact as a machine-readable constant.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
import math
from numbers import Real
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


CCSS_SPECTRAL_01_NOT_ACTIVATED = True
CCSS_SPECTRAL_ROUTE_TOKEN_VERSION = "ccss_spectral_route_token_1573f.v0.1"
CCSS_SPECTRAL_ROUTE_TOKEN_HKDF_INFO_V1 = b"ccss-spectral-route-token-v1"
CCSS_SPECTRAL_HIDING_COMMIT_PREFIX = b"ccss-spectral-lambda-commit-v1"
CCSS_SPECTRAL_CAP_CONTEXT_PREFIX = b"ccss-spectral-cap-context-v1"
CCSS_SPECTRAL_QUANTIZATION_SCALE = 1000
CCSS_SPECTRAL_01_KEM_ALGORITHM = "x25519_ecdh_contingency"
CCSS_SPECTRAL_01_KEM_SELECTION_TOKEN = "kem_x25519_contingency_selected_phase_1573f"
CCSS_SPECTRAL_01_KEM_NON_PQ_DISCLAIMER = (
    "X25519 ECDH contingency selected: ML-KEM-768 dependency evaluation failed. "
    "X25519 provides no post-quantum security. ML-KEM-768 upgrade remains the "
    "primary target after a vetted dependency and deterministic KAT evidence are "
    "available. Token: kem_x25519_contingency_selected_phase_1573f"
)

CCSS_SPECTRAL_FORBIDDEN_WIRE_FIELDS: frozenset[str] = frozenset(
    {
        "lambda_local",
        "lambda_vector",
        "eigenvalue",
        "eigenvalues",
        "spectral_fingerprint",
        "noise_sigma",
        "sigma",
        "agent_id",
        "sender_agent_id",
        "recipient_agent_id",
        "recipient_public_key",
        "raw_contact_capability_id",
        "commitment_salt",
    }
)

CCSS_SPECTRAL_ALLOWED_CLEARTEXT_FIELDS: frozenset[str] = frozenset(
    {
        "ccss_spectral_version",
        "epoch",
        "route_token",
        "sender_ephemeral_pubkey",
        "kem_ciphertext",
        "message_nonce",
        "route_purpose",
        "hiding_commitment",
        "capability_context_commitment",
        "sealed_payload_ciphertext",
        "size_class",
    }
)

# Fix2z defines these only as "coarse enum" placeholders; Phase 1573f does not
# invent runtime values before a later activation/specification phase.
CCSS_SPECTRAL_ROUTE_PURPOSE_VALUES: frozenset[str] = frozenset()
CCSS_SPECTRAL_SIZE_CLASS_VALUES: frozenset[str] = frozenset()
CCSS_SPECTRAL_COARSE_ENUM_VALUES_SPECIFIED = False

CCSS_SPECTRAL_MAX_ENVELOPE_DEPTH = 20


class SpectralRouteTokenError(ValueError):
    """Deterministic CCSS-SPECTRAL-01 validation failure."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _raise_if_not_activated() -> None:
    if CCSS_SPECTRAL_01_NOT_ACTIVATED:
        raise SpectralRouteTokenError(
            "ccss_spectral_01_not_activated_phase_1573f",
            "ccss_spectral_01_not_activated",
        )


def _require_bytes(value: Any, *, field_name: str) -> bytes:
    if not isinstance(value, bytes):
        raise SpectralRouteTokenError(
            f"ccss_spectral_{field_name}_must_be_bytes",
            f"{field_name}_must_be_bytes",
        )
    if not value:
        raise SpectralRouteTokenError(
            f"ccss_spectral_{field_name}_empty",
            f"{field_name}_empty",
        )
    return value


def _require_uint64(value: Any, *, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise SpectralRouteTokenError(
            f"ccss_spectral_{field_name}_must_be_int",
            f"{field_name}_must_be_int",
        )
    if value < 0 or value >= 2**64:
        raise SpectralRouteTokenError(
            f"ccss_spectral_{field_name}_uint64_range",
            f"{field_name}_uint64_range",
        )
    return value


def generate_ephemeral_x25519() -> tuple[bytes, X25519PrivateKey]:
    """Generate an X25519 ephemeral public key and private key.

    This helper is available for local primitive tests. It does not emit a
    route token or activate a relay path.
    """

    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return public_key, private_key


def kem_encap(pk_recipient_bytes: bytes) -> tuple[bytes, bytes]:
    """Encapsulate to the recipient capability public key.

    Phase 1573f keeps the entry point fail-closed behind
    ``CCSS_SPECTRAL_01_NOT_ACTIVATED``. If a later phase clears the guard under
    authority, the X25519 contingency returns ``(shared_secret,
    sender_ephemeral_pubkey)``.
    """

    _raise_if_not_activated()
    recipient_bytes = _require_bytes(pk_recipient_bytes, field_name="recipient_public_key")
    try:
        recipient_public_key = X25519PublicKey.from_public_bytes(recipient_bytes)
    except ValueError as exc:
        raise SpectralRouteTokenError(
            "ccss_spectral_recipient_public_key_invalid",
            "recipient_public_key_invalid",
        ) from exc
    sender_public_key, sender_private_key = generate_ephemeral_x25519()
    shared_secret = sender_private_key.exchange(recipient_public_key)
    return shared_secret, sender_public_key


def quantize_lambda(
    lambda_vector: list[float],
    scale: int = CCSS_SPECTRAL_QUANTIZATION_SCALE,
) -> list[int]:
    """Quantize a local spectral vector with ``floor(scale * lambda_i)``."""

    if not isinstance(scale, int) or isinstance(scale, bool) or scale <= 0:
        raise SpectralRouteTokenError(
            "ccss_spectral_quantization_scale_invalid",
            "quantization_scale_invalid",
        )
    if not isinstance(lambda_vector, list):
        raise SpectralRouteTokenError(
            "ccss_spectral_lambda_vector_must_be_list",
            "lambda_vector_must_be_list",
        )
    quantized: list[int] = []
    for index, value in enumerate(lambda_vector):
        if not isinstance(value, Real) or isinstance(value, bool):
            raise SpectralRouteTokenError(
                "ccss_spectral_lambda_component_invalid",
                f"lambda_component_invalid:{index}",
            )
        normalized = float(value)
        if not math.isfinite(normalized):
            raise SpectralRouteTokenError(
                "ccss_spectral_lambda_component_non_finite",
                f"lambda_component_non_finite:{index}",
            )
        quantized.append(math.floor(scale * normalized))
    return quantized


def make_hiding_commitment(quantized_lambda: list[int], salt: bytes) -> bytes:
    """Commit to quantized spectral coordinates without exposing them."""

    if not isinstance(quantized_lambda, list):
        raise SpectralRouteTokenError(
            "ccss_spectral_quantized_lambda_must_be_list",
            "quantized_lambda_must_be_list",
        )
    for index, value in enumerate(quantized_lambda):
        if not isinstance(value, int) or isinstance(value, bool):
            raise SpectralRouteTokenError(
                "ccss_spectral_quantized_lambda_component_invalid",
                f"quantized_lambda_component_invalid:{index}",
            )
    salt_bytes = _require_bytes(salt, field_name="commitment_salt")
    payload = json.dumps(
        quantized_lambda,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(
        CCSS_SPECTRAL_HIDING_COMMIT_PREFIX + salt_bytes + payload
    ).digest()


def make_capability_context_commitment(raw_cap_id: str, epoch: int) -> bytes:
    """Create the one-way epoch-rotating capability context commitment."""

    if not isinstance(raw_cap_id, str) or not raw_cap_id:
        raise SpectralRouteTokenError(
            "ccss_spectral_raw_capability_id_invalid",
            "raw_capability_id_invalid",
        )
    epoch_int = _require_uint64(epoch, field_name="epoch")
    return hashlib.sha256(
        CCSS_SPECTRAL_CAP_CONTEXT_PREFIX
        + epoch_int.to_bytes(8, "big")
        + raw_cap_id.encode("utf-8")
    ).digest()


def derive_route_token(
    ss: bytes,
    epoch_root: bytes,
    message_nonce: bytes,
    capability_context_commitment: bytes,
    sender_ephemeral_pubkey: bytes,
    kem_ciphertext: bytes,
    hiding_commitment: bytes,
    route_purpose: bytes,
) -> bytes:
    """Derive the opaque route token from selected-KEM material and context."""

    _raise_if_not_activated()
    shared_secret = _require_bytes(ss, field_name="shared_secret")
    salt = _require_bytes(epoch_root, field_name="epoch_root") + _require_bytes(
        message_nonce, field_name="message_nonce"
    )
    info = (
        _require_bytes(
            capability_context_commitment,
            field_name="capability_context_commitment",
        )
        + _require_bytes(sender_ephemeral_pubkey, field_name="sender_ephemeral_pubkey")
        + _require_bytes(kem_ciphertext, field_name="kem_ciphertext")
        + _require_bytes(hiding_commitment, field_name="hiding_commitment")
        + _require_bytes(route_purpose, field_name="route_purpose")
        + CCSS_SPECTRAL_ROUTE_TOKEN_HKDF_INFO_V1
    )
    return HKDF(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        info=info,
    ).derive(shared_secret)


def validate_no_forbidden_fields(envelope: dict[str, Any], _depth: int = 0) -> None:
    """Reject forbidden CCSS-SPECTRAL-01 wire fields at any nested depth."""

    _validate_no_forbidden_fields(envelope, depth=_depth)


def _validate_no_forbidden_fields(value: Any, *, depth: int) -> None:
    if depth > CCSS_SPECTRAL_MAX_ENVELOPE_DEPTH:
        raise SpectralRouteTokenError(
            "ccss_spectral_envelope_depth_exceeded",
            "envelope_depth_exceeded",
        )
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise SpectralRouteTokenError(
                    "ccss_spectral_envelope_key_must_be_string",
                    "envelope_key_must_be_string",
                )
            if key in CCSS_SPECTRAL_FORBIDDEN_WIRE_FIELDS:
                raise SpectralRouteTokenError(
                    "ccss_spectral_forbidden_wire_field_present",
                    f"forbidden_wire_field_present:{key}",
                )
            _validate_no_forbidden_fields(nested, depth=depth + 1)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for nested in value:
            _validate_no_forbidden_fields(nested, depth=depth + 1)
