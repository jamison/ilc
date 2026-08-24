# SPDX-License-Identifier: AGPL-3.0-only
"""Packageable BLS12-381 backend for onboarding AgentID and invite PoP.

Rust ``blst`` helper binaries remain useful for validator/operator parity
tests, but public wheels need a backend that works without a source checkout or
``cargo``. This module implements the same IETF BLS key derivation and the ILC
invite-PoP DST using ``py_ecc``.
"""

from __future__ import annotations

import re
from typing import Final

from py_ecc.bls import G2Basic
from py_ecc.optimized_bls12_381 import curve_order

ILC_INVITE_POP_DST: Final[bytes] = (
    b"ILC_INVITE_POP_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_"
)

_IKM_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_BLS_PUBLIC_KEY_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{96}$")
_BLS_SECRET_KEY_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_BLS_SIGNATURE_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{192}$")
_SHA384_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{96}$")


class _ILCInvitePoP(G2Basic):
    DST = ILC_INVITE_POP_DST


def keypair_from_ikm_hex(ikm_hex: str) -> tuple[str, str]:
    """Return ``(secret_key_hex, public_key_hex)`` from a 32-byte IKM hex string."""

    ikm = _require_hex(ikm_hex, _IKM_RE, "onboarding_bls_ikm_invalid")
    if ikm == "0" * 64:
        raise ValueError("onboarding_bls_ikm_must_not_be_all_zero")
    secret_key_int = G2Basic.KeyGen(bytes.fromhex(ikm), b"")
    if not _is_valid_secret_key_int(secret_key_int):
        raise ValueError("onboarding_bls_private_key_invalid")
    secret_key_hex = secret_key_int.to_bytes(32, "big").hex()
    public_key_hex = bytes(G2Basic.SkToPk(secret_key_int)).hex()
    _require_hex(public_key_hex, _BLS_PUBLIC_KEY_RE, "identity_agent_id_invalid")
    return secret_key_hex, public_key_hex


def sign_invite_pop_digest(secret_key_hex: str, digest_hex: str) -> str:
    """Sign a SHA-384 invite-PoP digest with an ILC AgentID BLS secret key."""

    secret_key_int = int(
        _require_hex(secret_key_hex, _BLS_SECRET_KEY_RE, "onboarding_bls_private_key_invalid"),
        16,
    )
    if not _is_valid_secret_key_int(secret_key_int):
        raise ValueError("onboarding_bls_private_key_invalid")
    digest = bytes.fromhex(_require_hex(digest_hex, _SHA384_RE, "invite_pop_digest_invalid"))
    signature_hex = bytes(_ILCInvitePoP.Sign(secret_key_int, digest)).hex()
    return _require_hex(signature_hex, _BLS_SIGNATURE_RE, "invite_pop_signature_invalid")


def verify_invite_pop_digest(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
) -> bool:
    """Verify an ILC invite-PoP signature against a compressed G1 public key."""

    public_key = bytes.fromhex(
        _require_hex(public_key_hex, _BLS_PUBLIC_KEY_RE, "identity_agent_id_invalid")
    )
    digest = bytes.fromhex(_require_hex(digest_hex, _SHA384_RE, "invite_pop_digest_invalid"))
    signature = bytes.fromhex(
        _require_hex(signature_hex, _BLS_SIGNATURE_RE, "invite_pop_signature_invalid")
    )
    try:
        if not _ILCInvitePoP.KeyValidate(public_key):
            return False
        return bool(_ILCInvitePoP.Verify(public_key, digest, signature))
    except (AssertionError, ValueError):
        return False


def _require_hex(value: str, pattern: re.Pattern[str], token: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _is_valid_secret_key_int(value: int) -> bool:
    return isinstance(value, int) and 0 < value < curve_order


__all__ = [
    "ILC_INVITE_POP_DST",
    "keypair_from_ikm_hex",
    "sign_invite_pop_digest",
    "verify_invite_pop_digest",
]
