
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle

REQUIRED_AUDIT_KEYS = {
    "audit_version", "bundle_path", "manifest_hash", "pipeline_json",
    "steps", "errors", "warnings", "pipeline_ok"
}

SUPPORTED_AUDIT_VERSIONS = {"v0.1"}

def file_sha256(path: Path) -> Optional[str]:
    """Compute SHA-256 hexdigest of a file's bytes, or None if file doesn't exist."""
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

def replay_verify(bundle_path: Path, audit: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replay-verify a bundle against an audit artifact.
    
    Args:
        bundle_path: Path to the bundle directory.
        audit: The audit artifact dictionary.
        
    Returns:
        A dictionary with: ok, errors, warnings, replay_matches, mismatch.
    """
    errors = []
    warnings = []
    mismatch = {}
    
    def check(field: str, expected: Any, actual: Any):
        if expected != actual:
            mismatch[field] = {"expected": expected, "actual": actual}
    
    # Check required audit keys
    missing_keys = REQUIRED_AUDIT_KEYS - set(audit.keys())
    if missing_keys:
        return {
            "ok": False,
            "errors": ["audit_missing_fields"],
            "warnings": [],
            "replay_matches": False,
            "mismatch": {}
        }
    
    # Check audit version
    audit_version = audit.get("audit_version")
    if audit_version not in SUPPORTED_AUDIT_VERSIONS:
        return {
            "ok": False,
            "errors": ["unsupported_audit_version"],
            "warnings": [],
            "replay_matches": False,
            "mismatch": {}
        }
    
    # Warn if bundle path differs
    audit_bundle_path = audit.get("bundle_path", "")
    if str(bundle_path.resolve()) != audit_bundle_path:
        warnings.append("bundle_path_mismatch")
    
    # Check bundle exists
    if not bundle_path.exists() or not bundle_path.is_dir():
        return {
            "ok": False,
            "errors": ["bundle_missing"],
            "warnings": warnings,
            "replay_matches": False,
            "mismatch": {}
        }
    
    manifest_path = bundle_path / "manifest.json"
    sig_path = bundle_path / "manifest.sig"
    
    # Compute current hashes
    current_manifest_hash = file_sha256(manifest_path)
    current_sig_hash = file_sha256(sig_path)
    
    # Compare manifest hash
    check("manifest_hash", audit.get("manifest_hash"), current_manifest_hash)
    
    # Compare signature hash (if audit had one)
    audit_sig_hash = audit.get("signature_hash")
    if audit_sig_hash is not None or current_sig_hash is not None:
        check("signature_hash", audit_sig_hash, current_sig_hash)
    
    # Run validation
    if manifest_path.exists():
        validation_result = validate_canon_export_bundle(bundle_path)
        current_validate_step = validation_result.get("ok", False)
        current_errors = validation_result.get("errors", [])
        current_warnings = validation_result.get("warnings", [])
    else:
        current_validate_step = False
        current_errors = []
        current_warnings = []
    
    # Compare steps (validate + verify)
    audit_steps = audit.get("steps", {})
    check("steps.validate", audit_steps.get("validate"), current_validate_step)
    if audit_sig_hash is None:
        current_verify_step = current_sig_hash is None
    else:
        current_verify_step = current_sig_hash == audit_sig_hash
    check("steps.verify", audit_steps.get("verify"), current_verify_step)
    
    # Compare pipeline_ok based on current replay state
    audit_pipeline_ok = audit.get("pipeline_ok", False)
    audit_errors = audit.get("errors", [])
    audit_warnings = audit.get("warnings", [])
    
    # Check recorded errors/warnings (exact match)
    check("errors", audit_errors, current_errors)
    check("warnings", audit_warnings, current_warnings)
    current_pipeline_ok = current_validate_step and current_verify_step
    check("pipeline_ok", audit_pipeline_ok, current_pipeline_ok)
    
    # Determine if replay matches
    replay_matches = len(mismatch) == 0
    
    return {
        "ok": replay_matches and len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "replay_matches": replay_matches,
        "mismatch": mismatch
    }
