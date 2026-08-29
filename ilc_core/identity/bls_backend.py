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
ILC_RELAY_BOOTSTRAP_RECORD_DST: Final[bytes] = (
    b"ILC_RELAY_BOOTSTRAP_RECORD_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_"
)
ILC_RELAY_BOOTSTRAP_CAPSULE_DST: Final[bytes] = (
    b"ILC_RELAY_BOOTSTRAP_CAPSULE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_"
)

_IKM_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_BLS_PUBLIC_KEY_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{96}$")
_BLS_SECRET_KEY_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_BLS_SIGNATURE_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{192}$")
_SHA384_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{96}$")


class _ILCInvitePoP(G2Basic):
    DST = ILC_INVITE_POP_DST


class _ILCRelayBootstrapRecord(G2Basic):
    DST = ILC_RELAY_BOOTSTRAP_RECORD_DST


class _ILCRelayBootstrapCapsule(G2Basic):
    DST = ILC_RELAY_BOOTSTRAP_CAPSULE_DST


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

    return _sign_digest_with_ciphersuite(
        secret_key_hex=secret_key_hex,
        digest_hex=digest_hex,
        ciphersuite=_ILCInvitePoP,
        private_key_token="onboarding_bls_private_key_invalid",
        digest_token="invite_pop_digest_invalid",
        signature_token="invite_pop_signature_invalid",
    )


def sign_relay_bootstrap_record_digest(secret_key_hex: str, digest_hex: str) -> str:
    """Sign a SHA-384 relay bootstrap-record digest with relay-record DST."""

    return _sign_digest_with_ciphersuite(
        secret_key_hex=secret_key_hex,
        digest_hex=digest_hex,
        ciphersuite=_ILCRelayBootstrapRecord,
        private_key_token="relay_bootstrap_private_key_invalid",
        digest_token="relay_bootstrap_payload_ref_invalid",
        signature_token="relay_bootstrap_signature_invalid",
    )


def sign_relay_bootstrap_capsule_digest(secret_key_hex: str, digest_hex: str) -> str:
    """Sign a SHA-384 relay bootstrap-capsule digest with Genesis-capsule DST."""

    return _sign_digest_with_ciphersuite(
        secret_key_hex=secret_key_hex,
        digest_hex=digest_hex,
        ciphersuite=_ILCRelayBootstrapCapsule,
        private_key_token="relay_bootstrap_capsule_private_key_invalid",
        digest_token="relay_bootstrap_capsule_payload_ref_invalid",
        signature_token="relay_bootstrap_capsule_signature_invalid",
    )


def _sign_digest_with_ciphersuite(
    *,
    secret_key_hex: str,
    digest_hex: str,
    ciphersuite: type[G2Basic],
    private_key_token: str,
    digest_token: str,
    signature_token: str,
) -> str:
    secret_key_int = int(
        _require_hex(secret_key_hex, _BLS_SECRET_KEY_RE, private_key_token),
        16,
    )
    if not _is_valid_secret_key_int(secret_key_int):
        raise ValueError(private_key_token)
    digest = bytes.fromhex(_require_hex(digest_hex, _SHA384_RE, digest_token))
    signature_hex = bytes(ciphersuite.Sign(secret_key_int, digest)).hex()
    return _require_hex(signature_hex, _BLS_SIGNATURE_RE, signature_token)


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


def verify_relay_bootstrap_record_digest(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
) -> bool:
    """Verify a relay bootstrap-record signature against a compressed G1 key."""

    return _verify_digest_with_ciphersuite(
        public_key_hex=public_key_hex,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
        ciphersuite=_ILCRelayBootstrapRecord,
        public_key_token="relay_bootstrap_signing_key_invalid",
        digest_token="relay_bootstrap_payload_ref_invalid",
        signature_token="relay_bootstrap_signature_invalid",
    )


def verify_relay_bootstrap_capsule_digest(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
) -> bool:
    """Verify a Genesis relay bootstrap-capsule signature."""

    return _verify_digest_with_ciphersuite(
        public_key_hex=public_key_hex,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
        ciphersuite=_ILCRelayBootstrapCapsule,
        public_key_token="relay_bootstrap_capsule_signing_key_invalid",
        digest_token="relay_bootstrap_capsule_payload_ref_invalid",
        signature_token="relay_bootstrap_capsule_signature_invalid",
    )


def _verify_digest_with_ciphersuite(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
    ciphersuite: type[G2Basic],
    public_key_token: str,
    digest_token: str,
    signature_token: str,
) -> bool:
    public_key = bytes.fromhex(_require_hex(public_key_hex, _BLS_PUBLIC_KEY_RE, public_key_token))
    digest = bytes.fromhex(_require_hex(digest_hex, _SHA384_RE, digest_token))
    signature = bytes.fromhex(_require_hex(signature_hex, _BLS_SIGNATURE_RE, signature_token))
    try:
        if not ciphersuite.KeyValidate(public_key):
            return False
        return bool(ciphersuite.Verify(public_key, digest, signature))
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
    "ILC_RELAY_BOOTSTRAP_CAPSULE_DST",
    "ILC_RELAY_BOOTSTRAP_RECORD_DST",
    "keypair_from_ikm_hex",
    "sign_invite_pop_digest",
    "sign_relay_bootstrap_capsule_digest",
    "sign_relay_bootstrap_record_digest",
    "verify_invite_pop_digest",
    "verify_relay_bootstrap_capsule_digest",
    "verify_relay_bootstrap_record_digest",
]
