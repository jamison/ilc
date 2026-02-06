
import base64
import hashlib
import hmac
from datetime import datetime
from pathlib import Path

from ilc_core.ledger.canon_bundle_utils import derive_key_id
from ilc_core.ledger.canon_bundle_key_registry import get_registry


def verify_manifest_signature(bundle_dir: Path, key: bytes) -> bool:
    """
    Verify the HMAC-SHA256 signature of a bundle's manifest.
    
    Args:
        bundle_dir: Path to the bundle directory.
        key: The byte string shared secret key.
        
    Returns:
        True if signature is valid, False otherwise.
        
    Raises:
        FileNotFoundError: If manifest.json or manifest.sig are missing.
    """
    manifest_path = bundle_dir / "manifest.json"
    sig_path = bundle_dir / "manifest.sig"
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")
    if not sig_path.exists():
        raise FileNotFoundError(f"Signature not found at {sig_path}")
        
    raw_sig_content = sig_path.read_text(encoding="utf-8")
    lines = [line for line in raw_sig_content.splitlines() if line.strip()]
    if len(lines) != 1:
        return False
    sig_b64 = lines[0].strip()
    if any(ch.isspace() for ch in sig_b64):
        return False
        
    # Load manifest JSON for metadata validation
    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError:
        return False

    try:
        manifest_text = manifest_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return False

    try:
        import json
        manifest_json = json.loads(manifest_text)
    except Exception:
        return False

    key_id = manifest_json.get("key_id")
    sig_alg = manifest_json.get("sig_alg")
    signed_at = manifest_json.get("signed_at")

    if key_id is None or sig_alg is None or signed_at is None:
        return False

    if sig_alg != "hmac-sha256":
        return False

    if key_id != derive_key_id(key):
        return False

    try:
        datetime.fromisoformat(str(signed_at).replace("Z", "+00:00"))
    except ValueError:
        return False

    # Check key_id against registry - reject deprecated/unknown
    registry = get_registry()
    key_status = registry.status(key_id)
    if key_status in ("deprecated", "unknown"):
        return False

    # Read manifest bytes as-is for signing
    manifest_data = manifest_bytes
    
    # Compute Expected HMAC
    expected = hmac.new(key, manifest_data, hashlib.sha256).digest()
    
    # Decode signature
    try:
        actual = base64.b64decode(sig_b64)
    except Exception:
        return False
        
    return hmac.compare_digest(actual, expected)

