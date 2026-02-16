
import base64
import binascii
import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ilc_core.exceptions import LedgerExportContractError
from ilc_core.ledger.canon_bundle_utils import derive_key_id


def load_key_from_file(path: Path) -> bytes:
    """Load a base64-encoded key from a file."""
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise LedgerExportContractError("Key file is empty")
    try:
        return base64.b64decode(raw)
    except binascii.Error as exc:
        raise LedgerExportContractError("invalid_key_file") from exc


def sign_manifest(bundle_dir: Path, key: bytes, overwrite: bool = False) -> Path:
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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["key_id"] = derive_key_id(key)
    manifest["sig_alg"] = "hmac-sha256"
    manifest["signed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Write updated manifest
    manifest_path.write_text(json.dumps(manifest, separators=(",", ":"), sort_keys=False), encoding="utf-8")
        
    # Read manifest bytes as-is for signing
    data = manifest_path.read_bytes()
    
    # Compute HMAC
    sig = hmac.new(key, data, hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig)
    
    # Write detached signature, single-line
    sig_path.write_bytes(sig_b64 + b"\n")
    
    return sig_path
