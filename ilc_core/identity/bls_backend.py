# SPDX-License-Identifier: AGPL-3.0-only
"""Packageable BLS12-381 backend for onboarding AgentID and invite PoP.

Rust ``blst`` helper binaries remain useful for validator/operator parity
tests, but public wheels need a backend that works without a source checkout or
``cargo``. This module implements the same IETF BLS key derivation and the ILC
invite-PoP DST using ``py_ecc``.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
from typing import Final

from py_ecc.bls import G2Basic
from py_ecc.optimized_bls12_381 import curve_order

ILC_INVITE_POP_DST: Final[bytes] = (
    b"ILC_INVITE_POP_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_"
)
ILC_RELAY_ADMISSION_DST: Final[bytes] = (
    b"ILC_RELAY_ADMISSION_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_"
)
ILC_RELAY_LIFECYCLE_DST: Final[bytes] = (
    b"ILC_RELAY_LIFECYCLE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_"
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
_BLS_BACKEND_ENV_VAR: Final[str] = "ILC_BLS_BACKEND"
_BLS_VERIFY_COMMAND_ENV_VAR: Final[str] = "ILC_BLS_VERIFY_COMMAND"
_BLS_BACKEND_PYTHON: Final[str] = "python"
_BLS_BACKEND_RUST: Final[str] = "rust"
_BLS_BACKEND_AUTO: Final[str] = "auto"
_BLS_VERIFY_TIMEOUT_SECONDS: Final[float] = 5.0
_RUST_SUITE_INVITE_POP: Final[str] = "invite_pop"
_RUST_SUITE_RELAY_ADMISSION: Final[str] = "relay_admission"
_RUST_SUITE_RELAY_LIFECYCLE: Final[str] = "relay_lifecycle"
_RUST_SUITE_RELAY_BOOTSTRAP_RECORD: Final[str] = "relay_bootstrap_record"
_RUST_SUITE_RELAY_BOOTSTRAP_CAPSULE: Final[str] = "relay_bootstrap_capsule"
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]


class _ILCInvitePoP(G2Basic):
    DST = ILC_INVITE_POP_DST


class _ILCRelayAdmission(G2Basic):
    DST = ILC_RELAY_ADMISSION_DST


class _ILCRelayLifecycle(G2Basic):
    DST = ILC_RELAY_LIFECYCLE_DST


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


def sign_relay_admission_digest(secret_key_hex: str, digest_hex: str) -> str:
    """Sign a SHA-384 relay admission digest with relay-admission DST."""

    return _sign_digest_with_ciphersuite(
        secret_key_hex=secret_key_hex,
        digest_hex=digest_hex,
        ciphersuite=_ILCRelayAdmission,
        private_key_token="relay_admission_private_key_invalid",
        digest_token="relay_admission_payload_ref_invalid",
        signature_token="relay_admission_signature_invalid",
    )


def sign_relay_lifecycle_digest(secret_key_hex: str, digest_hex: str) -> str:
    """Sign a SHA-384 relay lifecycle digest with relay-lifecycle DST."""

    return _sign_digest_with_ciphersuite(
        secret_key_hex=secret_key_hex,
        digest_hex=digest_hex,
        ciphersuite=_ILCRelayLifecycle,
        private_key_token="relay_lifecycle_private_key_invalid",
        digest_token="relay_lifecycle_payload_ref_invalid",
        signature_token="relay_lifecycle_signature_invalid",
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

    return _verify_digest_with_ciphersuite(
        public_key_hex=public_key_hex,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
        ciphersuite=_ILCInvitePoP,
        rust_suite=_RUST_SUITE_INVITE_POP,
        public_key_token="identity_agent_id_invalid",
        digest_token="invite_pop_digest_invalid",
        signature_token="invite_pop_signature_invalid",
    )


def verify_relay_admission_digest(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
) -> bool:
    """Verify a relay-admission signature against a compressed G1 public key."""

    return _verify_digest_with_ciphersuite(
        public_key_hex=public_key_hex,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
        ciphersuite=_ILCRelayAdmission,
        rust_suite=_RUST_SUITE_RELAY_ADMISSION,
        public_key_token="relay_agent_id_invalid",
        digest_token="relay_admission_payload_ref_invalid",
        signature_token="relay_admission_signature_invalid",
    )


def verify_relay_lifecycle_digest(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
) -> bool:
    """Verify a relay lifecycle signature against a compressed G1 public key."""

    return _verify_digest_with_ciphersuite(
        public_key_hex=public_key_hex,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
        ciphersuite=_ILCRelayLifecycle,
        rust_suite=_RUST_SUITE_RELAY_LIFECYCLE,
        public_key_token="relay_lifecycle_agent_id_invalid",
        digest_token="relay_lifecycle_payload_ref_invalid",
        signature_token="relay_lifecycle_signature_invalid",
    )


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
        rust_suite=_RUST_SUITE_RELAY_BOOTSTRAP_RECORD,
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
        rust_suite=_RUST_SUITE_RELAY_BOOTSTRAP_CAPSULE,
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
    rust_suite: str,
    public_key_token: str,
    digest_token: str,
    signature_token: str,
) -> bool:
    clean_public_key_hex = _require_hex(public_key_hex, _BLS_PUBLIC_KEY_RE, public_key_token)
    clean_digest_hex = _require_hex(digest_hex, _SHA384_RE, digest_token)
    clean_signature_hex = _require_hex(signature_hex, _BLS_SIGNATURE_RE, signature_token)
    backend = os.environ.get(_BLS_BACKEND_ENV_VAR, _BLS_BACKEND_PYTHON).strip().lower()
    if backend not in {_BLS_BACKEND_PYTHON, _BLS_BACKEND_RUST, _BLS_BACKEND_AUTO}:
        raise ValueError("bls_backend_invalid")
    if backend in {_BLS_BACKEND_RUST, _BLS_BACKEND_AUTO}:
        rust_result = _try_verify_bls_signature_rust(
            public_key_hex=clean_public_key_hex,
            digest_hex=clean_digest_hex,
            signature_hex=clean_signature_hex,
            suite=rust_suite,
        )
        if rust_result is not None:
            return rust_result
    public_key = bytes.fromhex(clean_public_key_hex)
    digest = bytes.fromhex(clean_digest_hex)
    signature = bytes.fromhex(clean_signature_hex)
    try:
        if not ciphersuite.KeyValidate(public_key):
            return False
        return bool(ciphersuite.Verify(public_key, digest, signature))
    except (AssertionError, ValueError):
        return False


def verify_bls_signature_rust(
    pubkey_hex: str,
    message_hex: str,
    sig_hex: str,
    *,
    suite: str,
) -> bool:
    """Verify a BLS digest signature with the optional Rust ``blst`` helper."""

    result = _try_verify_bls_signature_rust(
        public_key_hex=_require_hex(
            pubkey_hex,
            _BLS_PUBLIC_KEY_RE,
            "bls_rust_public_key_invalid",
        ),
        digest_hex=_require_hex(
            message_hex,
            _SHA384_RE,
            "bls_rust_digest_invalid",
        ),
        signature_hex=_require_hex(
            sig_hex,
            _BLS_SIGNATURE_RE,
            "bls_rust_signature_invalid",
        ),
        suite=_require_rust_suite(suite),
    )
    return bool(result)


def _try_verify_bls_signature_rust(
    *,
    public_key_hex: str,
    digest_hex: str,
    signature_hex: str,
    suite: str,
) -> bool | None:
    """Return None when the optional Rust helper is unavailable or unusable."""

    command = _resolve_bls_verify_command()
    if command is None:
        return None
    timeout = _BLS_VERIFY_TIMEOUT_SECONDS
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("bls_rust_timeout_invalid")
    try:
        result = subprocess.run(
            [
                *command,
                "--public-key-hex",
                public_key_hex,
                "--signature-hex",
                signature_hex,
                "--suite",
                _require_rust_suite(suite),
            ],
            input=f"{digest_hex}\n",
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    if output == "true":
        return True
    if output == "false":
        return False
    return False


def _resolve_bls_verify_command() -> list[str] | None:
    """Return a prebuilt Rust verifier command, never ``cargo run``.

    Runtime BLS verification must not turn a missing optional helper into
    repeated compile attempts or subprocess timeouts. Operator and test flows
    may build the helper explicitly; auto mode falls back to Python when no
    prebuilt binary is discoverable.
    """

    env_command = os.environ.get(_BLS_VERIFY_COMMAND_ENV_VAR)
    if env_command is not None and env_command.strip():
        command = shlex.split(env_command)
        return command or None
    path_binary = shutil.which("bls_verify_digest")
    if path_binary is not None:
        return [path_binary]
    debug_binary = _REPO_ROOT / "ilc_consensus" / "target" / "debug" / "bls_verify_digest"
    if debug_binary.exists():
        return [str(debug_binary)]
    return None


def _require_rust_suite(value: str) -> str:
    if value not in {
        _RUST_SUITE_INVITE_POP,
        _RUST_SUITE_RELAY_ADMISSION,
        _RUST_SUITE_RELAY_LIFECYCLE,
        _RUST_SUITE_RELAY_BOOTSTRAP_RECORD,
        _RUST_SUITE_RELAY_BOOTSTRAP_CAPSULE,
    }:
        raise ValueError("bls_rust_suite_invalid")
    return value


def _require_hex(value: str, pattern: re.Pattern[str], token: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _is_valid_secret_key_int(value: int) -> bool:
    return isinstance(value, int) and 0 < value < curve_order


__all__ = [
    "ILC_INVITE_POP_DST",
    "ILC_RELAY_ADMISSION_DST",
    "ILC_RELAY_BOOTSTRAP_CAPSULE_DST",
    "ILC_RELAY_BOOTSTRAP_RECORD_DST",
    "ILC_RELAY_LIFECYCLE_DST",
    "keypair_from_ikm_hex",
    "sign_invite_pop_digest",
    "sign_relay_admission_digest",
    "sign_relay_bootstrap_capsule_digest",
    "sign_relay_bootstrap_record_digest",
    "sign_relay_lifecycle_digest",
    "verify_bls_signature_rust",
    "verify_invite_pop_digest",
    "verify_relay_admission_digest",
    "verify_relay_bootstrap_capsule_digest",
    "verify_relay_bootstrap_record_digest",
    "verify_relay_lifecycle_digest",
]
