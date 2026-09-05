# SPDX-License-Identifier: AGPL-3.0-only
"""ML-DSA-65 signature verification utility for CDL-101 signed gossip."""

from __future__ import annotations

CDL_101_PQ_VERIFY_DEPENDENCY = "cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1"
CDL_101_SIGNED_ENVELOPE_DEPENDENCY = CDL_101_PQ_VERIFY_DEPENDENCY

_MLDSA_SIG_BYTES = 3309
_MLDSA_SIG_HEX_LENGTH = _MLDSA_SIG_BYTES * 2
_MLDSA_PK_BYTES = 1952
_MLDSA_PK_HEX_LENGTH = _MLDSA_PK_BYTES * 2
_HEX_CHARS = frozenset("0123456789abcdefABCDEF")


def _is_hex_string(value: object, expected_length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == expected_length
        and all(char in _HEX_CHARS for char in value)
    )


def verify_mldsa65_signature(
    message_bytes: bytes,
    signature_hex: str,
    pubkey_hex: str,
) -> bool:
    """Verify an ML-DSA-65 signature. Return False on any error.

    Security contract: this helper never raises. Import failure, malformed
    inputs, liboqs runtime failure, and invalid signatures all fail closed.
    """

    if not isinstance(message_bytes, bytes):
        return False
    if not _is_hex_string(signature_hex, _MLDSA_SIG_HEX_LENGTH):
        return False
    if not _is_hex_string(pubkey_hex, _MLDSA_PK_HEX_LENGTH):
        return False

    sig_bytes = bytes.fromhex(signature_hex)
    pubkey_bytes = bytes.fromhex(pubkey_hex)

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PublicKey
    except (ImportError, RuntimeError, SystemExit):
        pass
    else:
        try:
            public_key = MLDSA65PublicKey.from_public_bytes(pubkey_bytes)
            public_key.verify(sig_bytes, message_bytes)
            return True
        except InvalidSignature:
            return False
        except (AttributeError, TypeError, ValueError, RuntimeError):
            return False

    try:
        import oqs  # type: ignore[import]
    except (ImportError, RuntimeError, SystemExit):
        return False

    try:
        verifier = oqs.Signature("ML-DSA-65")
        return bool(verifier.verify(message_bytes, sig_bytes, pubkey_bytes))
    except (RuntimeError, ValueError):
        return False


__all__ = [
    "CDL_101_PQ_VERIFY_DEPENDENCY",
    "CDL_101_SIGNED_ENVELOPE_DEPENDENCY",
    "verify_mldsa65_signature",
]
