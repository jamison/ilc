#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS-003 envelope encryption — X25519 + ChaCha20-Poly1305.

Envelope structure (60 bytes overhead per layer):
    [32 bytes] ephemeral X25519 public key
    [12 bytes] ChaCha20-Poly1305 nonce
    [N  bytes] plaintext (encrypted in place)
    [16 bytes] Poly1305 authentication tag

Inner envelope (2108 bytes):
    Plaintext = 2048 bytes:
        [1]    version byte (0x01)
        [2]    message length LE (uint16, max 2000)
        [2000] message UTF-8, zero-padded to 2000 bytes
        [45]   reserved zeros
    Sealed = 2048 + 60 = 2108 bytes

Outer envelope (4156 bytes):
    Plaintext = 4096 bytes:
        [1]    version byte (0x01)
        [2]    inner envelope length LE = 2108
        [2108] inner envelope bytes
        [1985] zero padding
    Sealed = 4096 + 60 = 4156 bytes

Recipient public key: 32-byte X25519 public key, hex-encoded.
Published at: docs/contact/genesis_identity.json ("ccss_recipient_pubkey")
"""

from __future__ import annotations

import os
import struct
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

_VERSION = 0x01
_INNER_PLAINTEXT = 2048
_INNER_ENVELOPE  = 2108   # 2048 + 60 overhead
_OUTER_PLAINTEXT = 4096
_OUTER_ENVELOPE  = 4156   # 4096 + 60 overhead
_OVERHEAD        = 60     # 32 ephem_pubkey + 12 nonce + 16 tag
_MAX_MESSAGE_BYTES = 2000
_NONCE_LEN = 12
_TAG_LEN   = 16
_EPHEM_KEY_LEN = 32

_HKDF_INFO_INNER = b"ccss-003-inner-v1"
_HKDF_INFO_OUTER = b"ccss-003-outer-v1"


class CCSSEncryptError(ValueError):
    pass


def _ecdh_derive(ephemeral_private: X25519PrivateKey, recipient_pub: X25519PublicKey, info: bytes) -> bytes:
    """X25519 ECDH + HKDF-SHA256 → 32-byte ChaCha20-Poly1305 key."""
    shared = ephemeral_private.exchange(recipient_pub)
    return HKDF(algorithm=SHA256(), length=32, salt=None, info=info).derive(shared)


def _seal(plaintext: bytes, recipient_pub: X25519PublicKey, info: bytes) -> bytes:
    """Encrypt plaintext → [ephem_pubkey(32) | nonce(12) | ciphertext | tag(16)]."""
    ephem_priv = X25519PrivateKey.generate()
    ephem_pub_bytes = ephem_priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    key = _ecdh_derive(ephem_priv, recipient_pub, info)
    nonce = os.urandom(_NONCE_LEN)
    ciphertext_with_tag = ChaCha20Poly1305(key).encrypt(nonce, plaintext, associated_data=None)
    return ephem_pub_bytes + nonce + ciphertext_with_tag


def seal_message(message: str, recipient_pubkey_hex: str) -> bytes:
    """Seal a plaintext message into a 4156-byte CCSS-003 outer envelope.

    Args:
        message:               UTF-8 text, max 2000 bytes encoded.
        recipient_pubkey_hex:  Hex-encoded 32-byte X25519 public key.

    Returns:
        4156-byte outer envelope.
    """
    msg_bytes = message.encode("utf-8")
    if len(msg_bytes) > _MAX_MESSAGE_BYTES:
        raise CCSSEncryptError(
            f"message too long: {len(msg_bytes)} bytes (max {_MAX_MESSAGE_BYTES})"
        )

    try:
        raw_key = bytes.fromhex(recipient_pubkey_hex)
    except ValueError as exc:
        raise CCSSEncryptError(f"invalid recipient pubkey hex: {exc}") from exc
    if len(raw_key) != _EPHEM_KEY_LEN:
        raise CCSSEncryptError(
            f"recipient pubkey must be 32 bytes, got {len(raw_key)}"
        )
    recipient_pub = X25519PublicKey.from_public_bytes(raw_key)

    # ── Build inner plaintext (2048 bytes) ──
    inner_plain = bytearray(_INNER_PLAINTEXT)
    inner_plain[0] = _VERSION
    struct.pack_into("<H", inner_plain, 1, len(msg_bytes))
    inner_plain[3 : 3 + len(msg_bytes)] = msg_bytes
    # bytes 3+len … 2047 remain zero (padding)

    inner_envelope = _seal(bytes(inner_plain), recipient_pub, _HKDF_INFO_INNER)
    if len(inner_envelope) != _INNER_ENVELOPE:
        raise CCSSEncryptError(
            f"inner envelope size mismatch: {len(inner_envelope)} != {_INNER_ENVELOPE}"
        )

    # ── Build outer plaintext (4096 bytes) ──
    outer_plain = bytearray(_OUTER_PLAINTEXT)
    outer_plain[0] = _VERSION
    struct.pack_into("<H", outer_plain, 1, _INNER_ENVELOPE)
    outer_plain[3 : 3 + _INNER_ENVELOPE] = inner_envelope
    # bytes 3+2108 … 4095 remain zero (padding)

    outer_envelope = _seal(bytes(outer_plain), recipient_pub, _HKDF_INFO_OUTER)
    if len(outer_envelope) != _OUTER_ENVELOPE:
        raise CCSSEncryptError(
            f"outer envelope size mismatch: {len(outer_envelope)} != {_OUTER_ENVELOPE}"
        )

    return outer_envelope


def load_recipient_pubkey(genesis_identity_path: str) -> str:
    """Read ccss_recipient_pubkey from genesis_identity.json."""
    import json
    from pathlib import Path
    data = json.loads(Path(genesis_identity_path).read_text())
    key = data.get("ccss_recipient_pubkey", "")
    if not key or "PLACEHOLDER" in key.upper():
        raise CCSSEncryptError(
            "genesis_identity.json has not been configured: "
            "ccss_recipient_pubkey is still a placeholder"
        )
    return key


def load_onion_address(genesis_identity_path: str) -> str:
    """Read ccss_contact_onion from genesis_identity.json."""
    import json
    from pathlib import Path
    data = json.loads(Path(genesis_identity_path).read_text())
    onion = data.get("ccss_contact_onion", "")
    if not onion or "PLACEHOLDER" in onion.upper():
        raise CCSSEncryptError(
            "genesis_identity.json has not been configured: "
            "ccss_contact_onion is still a placeholder"
        )
    return onion


__all__ = [
    "CCSSEncryptError",
    "seal_message",
    "load_recipient_pubkey",
    "load_onion_address",
]
