# SPDX-License-Identifier: AGPL-3.0-only
"""Self-contained Ed25519 verification for signed truth primitive records."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

TRUTH_PRIMITIVE_SIG_VERIFIER_VERSION = "truth_primitive_sig_verifier_GAP_GRAPH_SIGN_00.v0.1"
TRUTH_PRIMITIVE_SIG_SCHEME = "ed25519_raw_hex_v1"

_CONTENT_FIELD_NAMES = ("agent_id", "epoch", "payload", "primitive", "v")


def truth_primitive_pubkey_fingerprint(public_key_bytes: bytes) -> str:
    """Return sha256(raw_ed25519_pubkey_bytes_32) as lowercase hex."""

    if not isinstance(public_key_bytes, bytes) or len(public_key_bytes) != 32:
        raise ValueError("invalid_truth_primitive_sig_pubkey_length")
    return hashlib.sha256(public_key_bytes).hexdigest()


def truth_primitive_signable_content(record: dict[str, Any]) -> dict[str, Any]:
    """Extract the canonical CDL-073 content fields signed by graph hotkeys."""

    if not isinstance(record, dict):
        raise ValueError("invalid_truth_primitive_sig_record")
    missing = [field for field in _CONTENT_FIELD_NAMES if field not in record]
    if missing:
        raise ValueError(f"invalid_truth_primitive_sig_missing_content_field:{missing[0]}")
    return {field: record[field] for field in _CONTENT_FIELD_NAMES}


def canonical_truth_primitive_sig_payload(record: dict[str, Any]) -> bytes:
    """Serialize signable content with deterministic JSON semantics."""

    content = truth_primitive_signable_content(record)
    return json.dumps(
        content,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def attach_truth_primitive_signature(
    envelope: dict[str, Any],
    private_key: ed25519.Ed25519PrivateKey,
) -> dict[str, Any]:
    """Return a signed envelope copy with self-contained verification material."""

    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("invalid_truth_primitive_sig_private_key_type")
    signed = deepcopy(envelope)
    payload = canonical_truth_primitive_sig_payload(signed)
    public_key_bytes = private_key.public_key().public_bytes_raw()
    sig_bytes = private_key.sign(payload)
    signed["sig"] = sig_bytes.hex()
    signed["sig_pubkey_hex"] = public_key_bytes.hex()
    signed["sig_pubkey_fingerprint"] = truth_primitive_pubkey_fingerprint(public_key_bytes)
    signed["sig_scheme"] = TRUTH_PRIMITIVE_SIG_SCHEME
    return signed


def verify_truth_primitive_sig(record: dict[str, Any]) -> bool | None:
    """Verify a truth primitive signature from fields in the record alone.

    Returns ``True`` for a valid signed record and ``None`` for unsigned records.
    Raises ``ValueError`` for malformed or invalid signed records. This proves
    hotkey authorship, not AgentID-to-hotkey authority.
    """

    if not isinstance(record, dict):
        raise ValueError("invalid_truth_primitive_sig_record")
    sig_hex = record.get("sig")
    if sig_hex in (None, "UNSIGNED"):
        return None
    if not isinstance(sig_hex, str):
        raise ValueError("invalid_truth_primitive_sig_hex")
    if record.get("sig_scheme") != TRUTH_PRIMITIVE_SIG_SCHEME:
        raise ValueError("invalid_truth_primitive_sig_scheme")

    try:
        sig_bytes = bytes.fromhex(sig_hex)
    except ValueError as exc:
        raise ValueError("invalid_truth_primitive_sig_hex") from exc
    if len(sig_bytes) != 64:
        raise ValueError("invalid_truth_primitive_sig_length")

    pubkey_hex = record.get("sig_pubkey_hex")
    if not isinstance(pubkey_hex, str):
        raise ValueError("invalid_truth_primitive_sig_pubkey_hex")
    try:
        pubkey_bytes = bytes.fromhex(pubkey_hex)
    except ValueError as exc:
        raise ValueError("invalid_truth_primitive_sig_pubkey_hex") from exc
    if len(pubkey_bytes) != 32:
        raise ValueError("invalid_truth_primitive_sig_pubkey_length")

    expected_fingerprint = truth_primitive_pubkey_fingerprint(pubkey_bytes)
    if record.get("sig_pubkey_fingerprint") != expected_fingerprint:
        raise ValueError("invalid_truth_primitive_sig_pubkey_fingerprint")

    public_key = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)
    try:
        public_key.verify(sig_bytes, canonical_truth_primitive_sig_payload(record))
    except (InvalidSignature, ValueError) as exc:
        raise ValueError("invalid_truth_primitive_signature") from exc
    return True


__all__ = [
    "TRUTH_PRIMITIVE_SIG_SCHEME",
    "TRUTH_PRIMITIVE_SIG_VERIFIER_VERSION",
    "attach_truth_primitive_signature",
    "canonical_truth_primitive_sig_payload",
    "truth_primitive_pubkey_fingerprint",
    "truth_primitive_signable_content",
    "verify_truth_primitive_sig",
]
