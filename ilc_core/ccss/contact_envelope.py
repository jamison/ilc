# SPDX-License-Identifier: AGPL-3.0-only
"""Fixed-size CCSS contact envelope for Genesis D2D send alignment.

This module only seals outbound contact messages. It does not decapsulate,
receive, activate CCSS-SPECTRAL-01 route tokens, or implement D2D delivery.
"""

from __future__ import annotations

import secrets
import struct

from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from ilc_core.network.d2d.spectral_route_token import (
    CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES,
    CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES,
    CCSS_SPECTRAL_MLKEM768_CIPHERTEXT_BYTES,
    CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES,
    _combine_hybrid_shared_secret,
    _load_mlkem768_public_key,
    _load_x25519_public_key,
    generate_ephemeral_x25519,
    split_hybrid_public_key,
)


CONTACT_ENVELOPE_VERSION = "ccss_contact_envelope_phase_1576g.v0.1"
CONTACT_ENVELOPE_MESSAGE_VERSION = 0x01
CONTACT_ENVELOPE_NONCE_BYTES = 12
CONTACT_ENVELOPE_TAG_BYTES = 16
CONTACT_ENVELOPE_PLAINTEXT_BYTES = 3008
CONTACT_ENVELOPE_AEAD_BYTES = CONTACT_ENVELOPE_PLAINTEXT_BYTES + CONTACT_ENVELOPE_TAG_BYTES
CONTACT_ENVELOPE_BYTES = (
    CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES
    + CONTACT_ENVELOPE_NONCE_BYTES
    + CONTACT_ENVELOPE_AEAD_BYTES
)
CONTACT_ENVELOPE_MAX_MESSAGE_BYTES = 2000
CONTACT_ENVELOPE_AAD_V1 = b"ilc-ccss-contact-envelope-1576g-v1"


class ContactEnvelopeError(ValueError):
    """Stable CCSS contact-envelope failure."""


def _require_hybrid_public_key(public_key_bytes: bytes) -> bytes:
    if not isinstance(public_key_bytes, bytes):
        raise ContactEnvelopeError("contact_envelope_public_key_must_be_bytes")
    if len(public_key_bytes) != CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES:
        raise ContactEnvelopeError("contact_envelope_public_key_length_invalid")
    return public_key_bytes


def _require_message_bytes(message: bytes) -> bytes:
    if not isinstance(message, bytes):
        raise ContactEnvelopeError("contact_envelope_message_must_be_bytes")
    if len(message) > CONTACT_ENVELOPE_MAX_MESSAGE_BYTES:
        raise ContactEnvelopeError(
            f"message_too_long:{len(message)}:{CONTACT_ENVELOPE_MAX_MESSAGE_BYTES}"
        )
    return message


def _build_plaintext(message: bytes) -> bytes:
    message_bytes = _require_message_bytes(message)
    plaintext = bytearray(CONTACT_ENVELOPE_PLAINTEXT_BYTES)
    plaintext[0] = CONTACT_ENVELOPE_MESSAGE_VERSION
    struct.pack_into("<H", plaintext, 1, len(message_bytes))
    plaintext[3 : 3 + len(message_bytes)] = message_bytes
    return bytes(plaintext)


def seal_contact_envelope(message: bytes, recipient_public_key_bytes: bytes) -> bytes:
    """Seal ``message`` to a hybrid X25519 + ML-KEM-768 contact public key."""

    public_key_bytes = _require_hybrid_public_key(recipient_public_key_bytes)
    x25519_public_key_bytes, mlkem_public_key_bytes = split_hybrid_public_key(
        public_key_bytes
    )
    x25519_recipient = _load_x25519_public_key(x25519_public_key_bytes)
    mlkem_recipient = _load_mlkem768_public_key(mlkem_public_key_bytes)

    sender_public_key_bytes, sender_private_key = generate_ephemeral_x25519()
    x25519_shared_secret = sender_private_key.exchange(x25519_recipient)
    mlkem_shared_secret, mlkem_ciphertext = mlkem_recipient.encapsulate()
    if len(mlkem_ciphertext) != CCSS_SPECTRAL_MLKEM768_CIPHERTEXT_BYTES:
        raise ContactEnvelopeError("contact_envelope_mlkem_ciphertext_size_invalid")

    key = _combine_hybrid_shared_secret(x25519_shared_secret, mlkem_shared_secret)
    nonce = secrets.token_bytes(CONTACT_ENVELOPE_NONCE_BYTES)
    encrypted = ChaCha20Poly1305(key).encrypt(
        nonce,
        _build_plaintext(message),
        CONTACT_ENVELOPE_AAD_V1,
    )
    envelope = sender_public_key_bytes + mlkem_ciphertext + nonce + encrypted
    if len(sender_public_key_bytes) != CCSS_SPECTRAL_X25519_PUBLIC_KEY_BYTES:
        raise ContactEnvelopeError("contact_envelope_x25519_ephemeral_size_invalid")
    if len(envelope) != CONTACT_ENVELOPE_BYTES:
        raise ContactEnvelopeError("contact_envelope_size_mismatch")
    return envelope


__all__ = [
    "CONTACT_ENVELOPE_AEAD_BYTES",
    "CONTACT_ENVELOPE_BYTES",
    "CONTACT_ENVELOPE_MAX_MESSAGE_BYTES",
    "CONTACT_ENVELOPE_NONCE_BYTES",
    "CONTACT_ENVELOPE_PLAINTEXT_BYTES",
    "CONTACT_ENVELOPE_TAG_BYTES",
    "CONTACT_ENVELOPE_VERSION",
    "ContactEnvelopeError",
    "seal_contact_envelope",
]
