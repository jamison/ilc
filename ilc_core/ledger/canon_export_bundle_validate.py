import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import TypeAlias, TypedDict

from ilc_core.ledger.canon_bundle_key_registry import get_registry


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class BundleValidationResult(TypedDict):
    ok: bool
    errors: list[str]
    warnings: list[str]

REQUIRED_MANIFEST_KEYS = {
    "bundle_format", "created_at", "export_hash", "validate_hash",
    "canon_hash", "export_path", "validate_path", "hash_alg"
}
OPTIONAL_MANIFEST_KEYS = {
    "export_format", "key_id", "key_fingerprint", "sig_alg", "signed_at",
}


def _append_key_status_issues(
    manifest: JsonObject, errors: list[str], warnings: list[str]
) -> None:
    key_id = manifest.get("key_id")
    if not key_id:
        return
    registry = get_registry()
    key_status = registry.status(key_id)
    if key_status == "deprecated":
        errors.append("deprecated_key_id")
    elif key_status == "unknown":
        errors.append("unknown_key_id")
    elif key_status == "previous":
        warnings.append("previous_key_id")

def _hash_file_content(path: Path) -> str:
    """Read bytes, strip one trailing newline if present, and return sha256 hex digest."""
    data = path.read_bytes()
    if data.endswith(b"\n"):
        data = data[:-1]
    return hashlib.sha256(data).hexdigest()

def validate_canon_export_bundle(bundle_dir: Path) -> BundleValidationResult:
    """
    Validate the integrity and structure of a canon export bundle.
    
    Args:
        bundle_dir: Path to the bundle directory.
        
    Returns:
        Dict with keys: ok (bool), errors (List[str]), warnings (List[str]).
    """
    errors: list[str] = []
    warnings: list[str] = []
    
    # 1. Directory Existence
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        return {"ok": False, "errors": [f"Bundle directory not found or not a directory: {bundle_dir}"], "warnings": []}
        
    # 2. File Existence Check
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
        manifest_raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "errors": ["manifest.json is not valid JSON"], "warnings": warnings}
    if not isinstance(manifest_raw, dict):
        return {"ok": False, "errors": ["manifest.json is not valid JSON"], "warnings": warnings}
    manifest: JsonObject = manifest_raw
        
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

    # 6. Check Timestamp Format (Strict ISO-8601)
    ts = manifest.get("created_at", "")
    if not isinstance(ts, str):
        errors.append("created_at must be a string")
    else:
        ts_normalized = ts.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(ts_normalized)
        except ValueError:
            errors.append("invalid_created_at")

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
    
    # 9. Key Metadata Validation (only when signature present)
    sig_path = bundle_dir / "manifest.sig"
    if sig_path.exists():
        # Require key metadata when signature is present
        if "key_id" not in manifest:
            errors.append("missing_key_id")
        if "sig_alg" not in manifest:
            errors.append("missing_sig_alg")
        elif manifest.get("sig_alg") != "hmac-sha256":
            errors.append("unsupported_sig_alg")
        
        signed_at = manifest.get("signed_at")
        if signed_at is None:
            errors.append("missing_signed_at")
        elif not isinstance(signed_at, str):
            errors.append("invalid_signed_at")
        else:
            try:
                datetime.fromisoformat(signed_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append("invalid_signed_at")
        
        # 10. Key Registry Status Check
        _append_key_status_issues(manifest, errors, warnings)

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
