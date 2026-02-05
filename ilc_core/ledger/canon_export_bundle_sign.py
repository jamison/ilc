
import base64
import hashlib
import hmac
from pathlib import Path
from typing import Optional


def load_key_from_file(path: Path) -> bytes:
    """Load a base64-encoded key from a file."""
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("Key file is empty")
    return base64.b64decode(raw)

def sign_manifest(bundle_dir: Path, key: bytes, overwrite: bool = False) -> Path:
    """
    Sign the manifest.json file in a bundle using HMAC-SHA256.
    
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
        
    # Read manifest bytes as-is
    data = manifest_path.read_bytes()
    
    # Compute HMAC
    sig = hmac.new(key, data, hashlib.sha256).digest()
    sig_b64 = base64.b64encode(sig)
    
    # Write detached signature, single-line
    sig_path.write_bytes(sig_b64 + b"\n")
    
    return sig_path
