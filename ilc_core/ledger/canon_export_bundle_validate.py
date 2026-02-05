
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Set

REQUIRED_MANIFEST_KEYS = {
    "bundle_format", "created_at", "export_hash", "validate_hash",
    "canon_hash", "export_path", "validate_path", "hash_alg"
}
OPTIONAL_MANIFEST_KEYS = {
    "export_format",
}

def _hash_file_content(path: Path) -> str:
    """Read bytes, strip one trailing newline if present, and return sha256 hex digest."""
    data = path.read_bytes()
    if data.endswith(b"\n"):
        data = data[:-1]
    return hashlib.sha256(data).hexdigest()

def validate_canon_export_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """
    Validate the integrity and structure of a canon export bundle.
    
    Args:
        bundle_dir: Path to the bundle directory.
        
    Returns:
        Dict with keys: ok (bool), errors (List[str]), warnings (List[str]).
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # 1. Directory Existence
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        return {"ok": False, "errors": [f"Bundle directory not found or not a directory: {bundle_dir}"], "warnings": []}
        
    # 2. File Extistence Check
    manifest_path = bundle_dir / "manifest.json"
    export_path = bundle_dir / "export.json"
    validate_path = bundle_dir / "validate.json"
    
    for p in [manifest_path, export_path, validate_path]:
        if not p.exists():
            errors.append(f"Missing required file: {p.name}")
            
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}
        
    # 3. Load Manifest
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "errors": ["manifest.json is not valid JSON"], "warnings": warnings}
        
    # 4. Check Manifest Keys
    manifest_keys = set(manifest.keys())
    missing_keys = REQUIRED_MANIFEST_KEYS - manifest_keys
    if missing_keys:
        errors.append(f"Manifest missing keys: {sorted(list(missing_keys))}")
        
    unknown_keys = manifest_keys - REQUIRED_MANIFEST_KEYS - OPTIONAL_MANIFEST_KEYS
    if unknown_keys:
        warnings.append(f"Manifest contains unknown keys: {sorted(list(unknown_keys))}")
        
    if errors:
         return {"ok": False, "errors": errors, "warnings": warnings}
         
    # 5. Check Fixed Values
    if manifest["bundle_format"] != "v0.1":
        errors.append(f"Unsupported bundle_format: {manifest['bundle_format']}")
    
    if manifest["hash_alg"] != "sha256":
        errors.append(f"Unsupported hash_alg: {manifest['hash_alg']}")
        
    if manifest["export_path"] != "export.json":
        errors.append(f"Invalid export_path: {manifest['export_path']} (must be 'export.json')")
        
    if manifest["validate_path"] != "validate.json":
        errors.append(f"Invalid validate_path: {manifest['validate_path']} (must be 'validate.json')")

    # 6. Check Timestamp Format (Warning only)
    ts = manifest.get("created_at", "")
    if not (ts.endswith("Z") or "+00:00" in ts):
        warnings.append("created_at does not appear to be ISO-8601 UTC (missing 'Z' or '+00:00')")

    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    # 7. Integrity Checks (Recompute Hashes)
    try:
        computed_export_hash = _hash_file_content(export_path)
        if computed_export_hash != manifest["export_hash"]:
            errors.append("Integrity check failed: export.json hash mismatch")
            
        computed_validate_hash = _hash_file_content(validate_path)
        if computed_validate_hash != manifest["validate_hash"]:
            errors.append("Integrity check failed: validate.json hash mismatch")
    except Exception as e:
        errors.append(f"Failed to compute file hashes: {e}")

    # 8. Content Consistency Checks (Lightweight)
    export_format_val = manifest.get("export_format")
    if export_format_val is None:
        warnings.append("Missing optional field 'export_format'")
    elif export_format_val != "v0.1":
        warnings.append(f"Unexpected export_format: {export_format_val}")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
