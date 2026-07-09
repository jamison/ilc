# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS-SPECTRAL-01 SpectralRouteToken primitive boundary.

Phase 1573f created this module as a non-activated cryptographic primitive
surface. Phase 1573f-Fix1 upgrades the KEM path to a hybrid X25519 +
ML-KEM-768 construction using ``cryptography>=48.0.0`` while keeping route-token
emission fail-closed behind ``CCSS_SPECTRAL_01_NOT_ACTIVATED``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import hmac
import json
import math
from numbers import Real
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


CCSS_SPECTRAL_01_NOT_ACTIVATED = True
CCSS_SPECTRAL_ROUTE_TOKEN_VERSION = "ccss_spectral_route_token_1573f.v0.1"
CCSS_SPECTRAL_ROUTE_TOKEN_HKDF_INFO_V1 = b"ccss-spectral-route-token-v1"
CCSS_SPECTRAL_HYBRID_KEM_COMBINE_INFO_V1 = (
    b"ccss-spectral-hybrid-x25519-mlkem768-combine-v1"
)
CCSS_SPECTRAL_HIDING_COMMIT_PREFIX = b"ccss-spectral-lambda-commit-v1"
CCSS_SPECTRAL_CAP_CONTEXT_PREFIX = b"ccss-spectral-cap-context-v1"
CCSS_SPECTRAL_QUANTIZATION_SCALE = 1000
CCSS_SPECTRAL_MAX_LAMBDA_COMPONENTS = 32
CCSS_SPECTRAL_MIN_LAMBDA_VALUE = 0.0
CCSS_SPECTRAL_MAX_LAMBDA_VALUE = 2.0
CCSS_SPECTRAL_01_KEM_ALGORITHM = "hybrid_x25519_ml_kem_768_fips203"
CCSS_SPECTRAL_01_KEM_SELECTION_TOKEN = (
    "kem_hybrid_x25519_ml_kem_768_selected_phase_1573f_fix1"
)
CCSS_SPECTRAL_01_KEM_SECURITY_NOTE = (
    "Hybrid X25519 + ML-KEM-768 selected in Phase 1573f-Fix1. X25519 provides "
    "mature classical security; ML-KEM-768 provides the FIPS 203 post-quantum "
    "KEM component. Token: kem_hybrid_x25519_ml_kem_768_selected_phase_1573f_fix1"
)

CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES = 32
CCSS_SPECTRAL_X25519_PRIVATE_KEY_BYTES = 32
CCSS_SPECTRAL_MLKEM768_PUBLIC_KEY_BYTES = 1184
CCSS_SPECTRAL_MLKEM768_PRIVATE_SEED_BYTES = 64
CCSS_SPECTRAL_MLKEM768_CIPHERTEXT_BYTES = 1088
CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES = (
    CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES + CCSS_SPECTRAL_MLKEM768_PUBLIC_KEY_BYTES
)
CCSS_SPECTRAL_HYBRID_PRIVATE_KEY_BYTES = (
    CCSS_SPECTRAL_X25519_PRIVATE_KEY_BYTES + CCSS_SPECTRAL_MLKEM768_PRIVATE_SEED_BYTES
)
CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES = (
    CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES + CCSS_SPECTRAL_MLKEM768_CIPHERTEXT_BYTES
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

ROUTE_PURPOSE_VALUES: frozenset[bytes] = frozenset(
    {
        b"bootstrap",
        b"direct-message",
        b"query",
        b"relay",
    }
)
CCSS_SPECTRAL_ROUTE_PURPOSE_VALUES: frozenset[str] = frozenset(
    value.decode("ascii") for value in ROUTE_PURPOSE_VALUES
)
CCSS_SPECTRAL_SIZE_CLASS_VALUES: frozenset[str] = frozenset()
CCSS_SPECTRAL_COARSE_ENUM_VALUES_SPECIFIED = True

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


def generate_hybrid_recipient_keypair() -> tuple[bytes, bytes]:
    """Generate a local hybrid recipient capability keypair for tests/wiring.

    Returns ``(public_key_bytes, private_key_seed_bytes)`` where:
    - public key bytes = X25519 public key || ML-KEM-768 public key
    - private key bytes = X25519 private seed || ML-KEM-768 private seed

    This helper does not activate route-token emission.
    """

    x25519_private_key = X25519PrivateKey.generate()
    x25519_public_key = x25519_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    x25519_private_seed = x25519_private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    mlkem_private_key = mlkem.MLKEM768PrivateKey.generate()
    mlkem_public_key = mlkem_private_key.public_key().public_bytes_raw()
    mlkem_private_seed = mlkem_private_key.private_bytes_raw()
    return x25519_public_key + mlkem_public_key, x25519_private_seed + mlkem_private_seed


def split_hybrid_public_key(pk_recipient_bytes: bytes) -> tuple[bytes, bytes]:
    """Split fixed-format hybrid recipient public key bytes."""

    public_key_bytes = _require_bytes(
        pk_recipient_bytes, field_name="recipient_public_key"
    )
    if len(public_key_bytes) != CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES:
        raise SpectralRouteTokenError(
            "ccss_spectral_hybrid_public_key_length_invalid",
            "hybrid_public_key_length_invalid",
        )
    return (
        public_key_bytes[:CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES],
        public_key_bytes[CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES:],
    )


def split_hybrid_private_key(sk_recipient_bytes: bytes) -> tuple[bytes, bytes]:
    """Split fixed-format hybrid recipient private seed bytes."""

    private_key_bytes = _require_bytes(
        sk_recipient_bytes, field_name="recipient_private_key"
    )
    if len(private_key_bytes) != CCSS_SPECTRAL_HYBRID_PRIVATE_KEY_BYTES:
        raise SpectralRouteTokenError(
            "ccss_spectral_hybrid_private_key_length_invalid",
            "hybrid_private_key_length_invalid",
        )
    return (
        private_key_bytes[:CCSS_SPECTRAL_X25519_PRIVATE_KEY_BYTES],
        private_key_bytes[CCSS_SPECTRAL_X25519_PRIVATE_KEY_BYTES:],
    )


def split_hybrid_kem_ciphertext(kem_ciphertext: bytes) -> tuple[bytes, bytes]:
    """Split fixed-format hybrid KEM ciphertext bytes."""

    ciphertext_bytes = _require_bytes(kem_ciphertext, field_name="kem_ciphertext")
    if len(ciphertext_bytes) != CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES:
        raise SpectralRouteTokenError(
            "ccss_spectral_hybrid_ciphertext_length_invalid",
            "hybrid_ciphertext_length_invalid",
        )
    return (
        ciphertext_bytes[:CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES],
        ciphertext_bytes[CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES:],
    )


def _load_x25519_public_key(public_key_bytes: bytes) -> X25519PublicKey:
    try:
        return X25519PublicKey.from_public_bytes(public_key_bytes)
    except ValueError as exc:
        raise SpectralRouteTokenError(
            "ccss_spectral_recipient_x25519_public_key_invalid",
            "recipient_x25519_public_key_invalid",
        ) from exc


def _load_x25519_private_key(private_key_bytes: bytes) -> X25519PrivateKey:
    try:
        return X25519PrivateKey.from_private_bytes(private_key_bytes)
    except ValueError as exc:
        raise SpectralRouteTokenError(
            "ccss_spectral_recipient_x25519_private_key_invalid",
            "recipient_x25519_private_key_invalid",
        ) from exc


def _load_mlkem768_public_key(public_key_bytes: bytes) -> mlkem.MLKEM768PublicKey:
    try:
        return mlkem.MLKEM768PublicKey.from_public_bytes(public_key_bytes)
    except ValueError as exc:
        raise SpectralRouteTokenError(
            "ccss_spectral_recipient_mlkem768_public_key_invalid",
            "recipient_mlkem768_public_key_invalid",
        ) from exc


def _load_mlkem768_private_key(seed_bytes: bytes) -> mlkem.MLKEM768PrivateKey:
    try:
        return mlkem.MLKEM768PrivateKey.from_seed_bytes(seed_bytes)
    except ValueError as exc:
        raise SpectralRouteTokenError(
            "ccss_spectral_recipient_mlkem768_private_key_invalid",
            "recipient_mlkem768_private_key_invalid",
        ) from exc


def _combine_hybrid_shared_secret(x25519_ss: bytes, mlkem_ss: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA512(),
        length=32,
        salt=None,
        info=CCSS_SPECTRAL_HYBRID_KEM_COMBINE_INFO_V1,
    ).derive(x25519_ss + mlkem_ss)


def kem_encap(pk_recipient_bytes: bytes) -> tuple[bytes, bytes]:
    """Encapsulate to the recipient capability public key.

    Phase 1573f keeps the entry point fail-closed behind
    ``CCSS_SPECTRAL_01_NOT_ACTIVATED``. If a later phase clears the guard under
    authority, the hybrid path returns ``(combined_shared_secret,
    hybrid_ciphertext)`` where ``hybrid_ciphertext`` is
    sender X25519 ephemeral public key || ML-KEM-768 ciphertext.
    """

    _raise_if_not_activated()
    x25519_recipient_public_bytes, mlkem_recipient_public_bytes = split_hybrid_public_key(
        pk_recipient_bytes
    )
    recipient_public_key = _load_x25519_public_key(x25519_recipient_public_bytes)
    mlkem_public_key = _load_mlkem768_public_key(mlkem_recipient_public_bytes)
    sender_public_key, sender_private_key = generate_ephemeral_x25519()
    x25519_shared_secret = sender_private_key.exchange(recipient_public_key)
    mlkem_shared_secret, mlkem_ciphertext = mlkem_public_key.encapsulate()
    return (
        _combine_hybrid_shared_secret(x25519_shared_secret, mlkem_shared_secret),
        sender_public_key + mlkem_ciphertext,
    )


def kem_decap(sk_recipient_bytes: bytes, kem_ciphertext: bytes) -> bytes:
    """Decapsulate the guarded hybrid KEM ciphertext for recipient tests/wiring."""

    _raise_if_not_activated()
    x25519_private_seed, mlkem_private_seed = split_hybrid_private_key(
        sk_recipient_bytes
    )
    sender_ephemeral_public_bytes, mlkem_ciphertext = split_hybrid_kem_ciphertext(
        kem_ciphertext
    )
    x25519_private_key = _load_x25519_private_key(x25519_private_seed)
    sender_public_key = _load_x25519_public_key(sender_ephemeral_public_bytes)
    x25519_shared_secret = x25519_private_key.exchange(sender_public_key)
    mlkem_private_key = _load_mlkem768_private_key(mlkem_private_seed)
    try:
        mlkem_shared_secret = mlkem_private_key.decapsulate(mlkem_ciphertext)
    except ValueError as exc:
        raise SpectralRouteTokenError(
            "ccss_spectral_mlkem768_ciphertext_invalid",
            "mlkem768_ciphertext_invalid",
        ) from exc
    return _combine_hybrid_shared_secret(x25519_shared_secret, mlkem_shared_secret)


def quantize_lambda(
    lambda_vector: list[float],
    scale: int = CCSS_SPECTRAL_QUANTIZATION_SCALE,
) -> list[int]:
    """Quantize bounded normalized-Laplacian coordinates.

    This primitive accepts the same spectral range as the H-013 beacon builder:
    non-empty, at most 32 components, and each value in ``[0, 2]``. Keeping the
    primitive bounded prevents callers from bypassing the builder-level input
    and memory safeguards before a future activation clears the route-token
    guard.
    """

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
    if not lambda_vector:
        raise SpectralRouteTokenError(
            "ccss_spectral_lambda_vector_empty",
            "lambda_vector_empty",
        )
    if len(lambda_vector) > CCSS_SPECTRAL_MAX_LAMBDA_COMPONENTS:
        raise SpectralRouteTokenError(
            "ccss_spectral_lambda_vector_too_large",
            "lambda_vector_too_large",
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
        if (
            normalized < CCSS_SPECTRAL_MIN_LAMBDA_VALUE
            or normalized > CCSS_SPECTRAL_MAX_LAMBDA_VALUE
        ):
            raise SpectralRouteTokenError(
                "ccss_spectral_lambda_component_out_of_range",
                f"lambda_component_out_of_range:{index}",
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
    if not quantized_lambda:
        raise SpectralRouteTokenError(
            "ccss_spectral_quantized_lambda_empty",
            "quantized_lambda_empty",
        )
    if len(quantized_lambda) > CCSS_SPECTRAL_MAX_LAMBDA_COMPONENTS:
        raise SpectralRouteTokenError(
            "ccss_spectral_quantized_lambda_too_large",
            "quantized_lambda_too_large",
        )
    max_quantized = CCSS_SPECTRAL_MAX_LAMBDA_VALUE * CCSS_SPECTRAL_QUANTIZATION_SCALE
    for index, value in enumerate(quantized_lambda):
        if not isinstance(value, int) or isinstance(value, bool):
            raise SpectralRouteTokenError(
                "ccss_spectral_quantized_lambda_component_invalid",
                f"quantized_lambda_component_invalid:{index}",
            )
        if value < 0 or value > max_quantized:
            raise SpectralRouteTokenError(
                "ccss_spectral_quantized_lambda_component_out_of_range",
                f"quantized_lambda_component_out_of_range:{index}",
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
    validate_route_purpose(route_purpose)
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


def authenticate_route_token(
    token: bytes,
    ss: bytes,
    epoch_root: bytes,
    message_nonce: bytes,
    capability_context_commitment: bytes,
    sender_ephemeral_pubkey: bytes,
    kem_ciphertext: bytes,
    hiding_commitment: bytes,
    route_purpose: bytes,
) -> bool:
    """Authenticate a recipient-visible route token in constant time."""

    _raise_if_not_activated()
    candidate = _require_bytes(token, field_name="route_token")
    expected = derive_route_token(
        ss,
        epoch_root,
        message_nonce,
        capability_context_commitment,
        sender_ephemeral_pubkey,
        kem_ciphertext,
        hiding_commitment,
        route_purpose,
    )
    return hmac.compare_digest(candidate, expected)


def validate_route_purpose(route_purpose: bytes) -> None:
    """Validate the coarse route-purpose enum."""

    purpose = _require_bytes(route_purpose, field_name="route_purpose")
    if purpose not in ROUTE_PURPOSE_VALUES:
        try:
            printable = purpose.decode("utf-8")
        except UnicodeDecodeError:
            printable = purpose.hex()
        token = f"ccss_spectral_01_invalid_route_purpose:{printable}"
        raise SpectralRouteTokenError(
            token,
            token,
        )


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
