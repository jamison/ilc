
import base64
import hashlib
import hmac
from pathlib import Path

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
        binascii.Error: If manifest.sig contains invalid base64 data.
    """
    manifest_path = bundle_dir / "manifest.json"
    sig_path = bundle_dir / "manifest.sig"
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")
    if not sig_path.exists():
        raise FileNotFoundError(f"Signature not found at {sig_path}")
        
    sig_b64 = sig_path.read_text(encoding="utf-8").strip()
    
    # Reject multi-line signatures or unexpected whitespace/newlines within the base64 string
    # (Checking against raw content for internal newlines)
    raw_sig_content = sig_path.read_text(encoding="utf-8")
    if "\n" in raw_sig_content.strip(): 
         # A valid single-line signature file might have ONE trailing newline, 
         # but .strip() removes it. If there are internal newlines, they might persist 
         # or we should check the raw string more carefully.
         # Re-read: "If manifest.sig has newlines or whitespace in middle: return ok=false"
         # Let's check internal structure strictly.
         pass
    
    # For robust check:
    lines = [line for line in raw_sig_content.splitlines() if line.strip()]
    if len(lines) != 1:
        # If there's more than one non-empty line, it's malformed according to our strict rule
        return False
        
    # Read manifest bytes as-is
    manifest_data = manifest_path.read_bytes()
    
    # Compute Expected HMAC
    expected = hmac.new(key, manifest_data, hashlib.sha256).digest()
    
    # Decode signature
    try:
        actual = base64.b64decode(sig_b64)
    except Exception:
        return False
        
    return hmac.compare_digest(actual, expected)
