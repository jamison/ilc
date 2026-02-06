
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

def file_sha256(path: Path) -> Optional[str]:
    """Compute SHA-256 hexdigest of a file's bytes, or None if file doesn't exist."""
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

def create_audit_artifact(
    bundle_path: Path,
    report: Dict[str, Any],
    report_path: Optional[Path],
    audit_path: Path,
    json_output: str,
    report_content: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create an audit artifact dictionary for a bundle pipeline run.
    
    Args:
        bundle_path: Path to the bundle directory.
        report: The pipeline result dictionary.
        report_path: Path to the Markdown report (if created).
        audit_path: Path where audit artifact will be written.
        json_output: The exact JSON stdout payload as string.
        report_content: The Markdown report content (for hashing).
        timestamp: Optional override for generation timestamp.
        
    Returns:
        A dictionary containing the audit artifact data.
    """
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    manifest_path = bundle_path / "manifest.json"
    sig_path = bundle_path / "manifest.sig"
    
    manifest_hash = file_sha256(manifest_path)
    sig_hash = file_sha256(sig_path)
    
    report_hash = None
    if report_content:
        report_hash = hashlib.sha256(report_content.encode("utf-8")).hexdigest()
    
    audit = {
        "audit_version": "v0.1",
        "bundle_path": str(bundle_path.resolve()),
        "timestamp": ts,
        "pipeline_ok": report.get("ok", False),
        "errors": report.get("errors", []),
        "warnings": report.get("warnings", []),
        "steps": report.get("steps", {}),
        "report_path": str(report_path) if report_path else None,
        "audit_path": str(audit_path),
        "bundle_exists": bundle_path.exists() and bundle_path.is_dir(),
        "signature_present": sig_path.exists(),
        "manifest_hash": manifest_hash,
        "signature_hash": sig_hash,
        "report_hash": report_hash,
        "pipeline_json": json_output,
    }
    
    return audit

def write_audit_artifact(audit: Dict[str, Any], audit_path: Path) -> bool:
    """
    Write the audit artifact to a JSON file.
    
    Args:
        audit: The audit artifact dictionary.
        audit_path: Path where to write the audit file.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        json_content = json.dumps(audit, separators=(",", ":"), sort_keys=False)
        audit_path.write_text(json_content, encoding="utf-8")
        return True
    except Exception:
        return False
