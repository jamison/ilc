"""
Signing and verification for registry channel files (v0.3+).

Implements detached HMAC-SHA256 signatures for channel files to protect
routing and source selection policy.
"""

import hashlib
import hmac
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict

from ilc_core.ledger.canon_bundle_key_registry_channel import (
    _atomic_write,
    validate_channel_file,
)


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_strict_iso8601_tz(ts: str) -> bool:
    """Check for strict YYYY-MM-DDTHH:MM:SSZ format."""
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    return bool(re.match(pattern, ts))


def _derive_key_id(key: bytes) -> str:
    """Derive key ID from key bytes (first 16 chars of SHA256)."""
    return hashlib.sha256(key).hexdigest()[:16]


def _derive_key_fingerprint(key: bytes) -> str:
    """Derive canonical signer fingerprint from key bytes (full SHA-256)."""
    return hashlib.sha256(key).hexdigest()


def canonical_channel_bytes(channel_path: Path) -> bytes:
    """
    Return canonical bytes for a channel file.
    
    Format: JSON loaded and re-dumped with sort_keys=True, separators=(',', ':'), UTF-8.
    Raises: OSError, json.JSONDecodeError
    """
    data = json.loads(channel_path.read_text(encoding="utf-8"))
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_channel_file(
    channel_path: Path,
    key: bytes,
    sig_path: Optional[Path] = None,
) -> dict:
    """
    Sign a channel file creating a detached .sig sidecar.
    
    Args:
        channel_path: Path to channel file.
        key: Signing key bytes.
        sig_path: Optional path for .sig output (defaults to <channel_path>.sig).
    
    Returns:
        Dict with {ok, errors, warnings, sig_path, ...}.
    """
    warnings = []
    
    # Validate channel file first
    val_result = validate_channel_file(channel_path)
    if not val_result["ok"]:
        return {
            "ok": False,
            "errors": ["channel_file_invalid"] + val_result.get("errors", []),
            "warnings": warnings,
        }
    warnings.extend(val_result.get("warnings", []))
    
    try:
        canonical = canonical_channel_bytes(channel_path)
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "errors": ["channel_read_error"], "warnings": warnings}
    
    # Compute signature
    channel_hash = hashlib.sha256(canonical).hexdigest()
    signature_hex = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    key_id = _derive_key_id(key)
    key_fingerprint = _derive_key_fingerprint(key)
    
    sig_data = {
        "sig_alg": "hmac-sha256",
        "key_id": key_id,
        "key_fingerprint": key_fingerprint,
        "signed_at": _now_iso8601(),
        "channel_hash": channel_hash,
        "signature_hex": signature_hex,
    }
    
    # Determine sig path
    resolved_channel = channel_path.resolve()
    if sig_path:
        resolved_sig = sig_path.resolve()
    else:
        resolved_sig = Path(str(resolved_channel) + ".sig")
    
    # Write sidecar
    try:
        content = json.dumps(sig_data, indent=2, sort_keys=True)
        _atomic_write(resolved_sig, content)
    except OSError:
        return {"ok": False, "errors": ["channel_signature_write_error"], "warnings": warnings}
    
    return {
        "ok": True,
        "errors": [],
        "warnings": warnings,
        "sig_path": str(resolved_sig),
        "sig_alg": "hmac-sha256",
        "key_id": key_id,
        "key_fingerprint": key_fingerprint,
        "channel_hash": channel_hash,
    }


def verify_channel_file_signature(
    channel_path: Path,
    key: bytes,
    sig_path: Optional[Path] = None,
) -> dict:
    """
    Verify a detached channel file signature.
    
    Args:
        channel_path: Path to channel file.
        key: Verification key bytes.
        sig_path: Optional path to .sig file.
    
    Returns:
        Dict with {ok, errors, warnings, ...}.
    """
    errors = []
    warnings = []
    
    try:
        # 1. Channel file check
        if not channel_path.exists():
            return {"ok": False, "errors": ["channel_file_not_found"], "warnings": []}

        canonical = canonical_channel_bytes(channel_path)
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "errors": ["channel_read_error"], "warnings": []}
    
    # 2. Sig file check
    resolved_channel = channel_path.resolve()
    if sig_path:
        resolved_sig = sig_path.resolve()
    else:
        resolved_sig = Path(str(resolved_channel) + ".sig")
    
    if not resolved_sig.exists():
        return {"ok": False, "errors": ["channel_signature_missing"], "warnings": []}
    
    try:
        sig_data = json.loads(resolved_sig.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "errors": ["channel_signature_read_error"], "warnings": []}
    
    # 3. Required fields
    required = ["sig_alg", "key_id", "signed_at", "channel_hash", "signature_hex"]
    for field in required:
        if field not in sig_data:
            errors.append(f"channel_signature_missing_field:{field}")
    
    if errors:
        return {"ok": False, "errors": errors, "warnings": []}
    
    # 4. Alg check
    if sig_data["sig_alg"] != "hmac-sha256":
        errors.append("channel_signature_unsupported_sig_alg")
    
    # 5. Timestamp check
    if not _is_strict_iso8601_tz(sig_data["signed_at"]):
        errors.append("channel_signature_invalid_signed_at")
    
    # 6. Channel hash check
    expected_hash = hashlib.sha256(canonical).hexdigest()
    if sig_data["channel_hash"] != expected_hash:
        errors.append("channel_hash_mismatch")
    
    # 7. Signature check
    expected_sig = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig_data["signature_hex"], expected_sig):
        errors.append("channel_signature_mismatch")
    
    # 8. Key ID check
    expected_key_id = _derive_key_id(key)
    if sig_data["key_id"] != expected_key_id:
        # If key doesn't match, it's technically a failed verification against THIS key.
        # But if the sig is valid otherwise, it might be signed by another key.
        # Since we passed a specific key, we expect it to match.
        errors.append("channel_signature_key_unknown")

    # 9. Canonical fingerprint check (compatibility mode: optional for legacy sidecars)
    if "key_fingerprint" in sig_data:
        expected_fingerprint = _derive_key_fingerprint(key)
        if sig_data["key_fingerprint"] != expected_fingerprint:
            errors.append("channel_signature_fingerprint_mismatch")
    
    if errors:
        return {
            "ok": False,
            "errors": errors,
            "warnings": warnings,
            "sig_path": str(resolved_sig),
            "sig_alg": sig_data.get("sig_alg"),
            "key_id": sig_data.get("key_id"),
            "key_fingerprint": sig_data.get("key_fingerprint"),
            "channel_hash": sig_data.get("channel_hash"),
        }
    
    return {
        "ok": True,
        "errors": [],
        "warnings": warnings,
        "sig_path": str(resolved_sig),
        "sig_alg": sig_data["sig_alg"],
        "key_id": sig_data["key_id"],
        "key_fingerprint": sig_data.get("key_fingerprint"),
        "channel_hash": sig_data["channel_hash"],
    }
