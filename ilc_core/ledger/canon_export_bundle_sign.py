
import base64
import binascii
import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ilc_core.exceptions import LedgerExportContractError
from ilc_core.ledger.canon_bundle_utils import derive_key_fingerprint, derive_key_id


def _reject_non_finite_constant(constant: str) -> None:
    raise LedgerExportContractError("invalid_manifest_non_finite")


def _canonical_manifest_json(manifest: dict) -> str:
    return json.dumps(
        manifest,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def _is_strict_iso8601_with_timezone(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _resolve_manifest_signed_at(manifest: dict, signed_at: str | None) -> str:
    if signed_at is not None:
        if not _is_strict_iso8601_with_timezone(signed_at):
            raise LedgerExportContractError("invalid_signed_at")
        return signed_at

    existing_signed_at = manifest.get("signed_at")
    if isinstance(existing_signed_at, str):
        if not _is_strict_iso8601_with_timezone(existing_signed_at):
            raise LedgerExportContractError("invalid_signed_at")
        return existing_signed_at

    created_at = manifest.get("created_at")
    if isinstance(created_at, str):
        if not _is_strict_iso8601_with_timezone(created_at):
            raise LedgerExportContractError("invalid_created_at")
        return created_at

    return "1970-01-01T00:00:00Z"


def load_key_from_file(path: Path) -> bytes:
    """Load a base64-encoded key from a file."""
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise LedgerExportContractError("Key file is empty")
    try:
        return base64.b64decode(raw)
    except binascii.Error as exc:
        raise LedgerExportContractError("invalid_key_file") from exc


def sign_manifest(
    bundle_dir: Path,
    key: bytes,
    overwrite: bool = False,
    signed_at: str | None = None,
) -> Path:
    """
    Sign the manifest.json file in a bundle using HMAC-SHA256.
    
    Adds key metadata (key_id, sig_alg, signed_at) to the manifest before signing.
    
    Args:
        bundle_dir: Path to the bundle directory.
        key: The byte string secret key for HMAC.
        overwrite: If True, overwrite existing manifest.sig.
        
    Returns:
        Path to the created signature file.
        
    Raises:
        FileNotFoundError: If manifest.json does not exist.
        FileExistsError: If manifest.sig exists and overwrite is False.
    """
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")
        
    sig_path = bundle_dir / "manifest.sig"
    if sig_path.exists() and not overwrite:
        raise FileExistsError(f"Signature already exists at {sig_path}")
    
    # Load manifest, add key metadata, and rewrite
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8"),
        parse_constant=_reject_non_finite_constant,
    )
    if not isinstance(manifest, dict):
        raise LedgerExportContractError("invalid_manifest_shape")
    manifest["key_id"] = derive_key_id(key)
    manifest["key_fingerprint"] = derive_key_fingerprint(key)
    manifest["sig_alg"] = "hmac-sha256"
    manifest["signed_at"] = _resolve_manifest_signed_at(manifest, signed_at)
    
    # Write updated manifest
    manifest_path.write_text(_canonical_manifest_json(manifest), encoding="utf-8")
        
    # Read manifest bytes as-is for signing
    data = manifest_path.read_bytes()
    
    # Compute HMAC
    sig = hmac.new(key, data, hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig)
    
    # Write detached signature, single-line
    sig_path.write_bytes(sig_b64 + b"\n")
    
    return sig_path
