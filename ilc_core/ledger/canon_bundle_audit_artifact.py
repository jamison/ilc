# SPDX-License-Identifier: AGPL-3.0-only

import hashlib
import json
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeAlias, TypedDict

from ilc_core.ledger.canon_bundle_utils import file_sha256


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class PipelineAuditReport(TypedDict, total=False):
    ok: bool
    errors: list[str]
    warnings: list[str]
    steps: JsonObject


class AuditArtifact(TypedDict):
    audit_version: str
    bundle_path: str
    timestamp: str
    pipeline_ok: bool
    errors: list[str]
    warnings: list[str]
    steps: JsonObject
    report_path: str | None
    audit_path: str
    bundle_exists: bool
    signature_present: bool
    manifest_hash: str | None
    signature_hash: str | None
    report_hash: str | None
    pipeline_json: str
    key_id: str | None
    sig_alg: str | None
    signed_at: str | None
    key_status: str | None


def _reject_non_finite_json_constant(value: str) -> JsonValue:
    raise ValueError(f"non_finite_json_numeric_literal:{value}")



def create_audit_artifact(
    bundle_path: Path,
    report: PipelineAuditReport,
    report_path: Path | None,
    audit_path: Path,
    json_output: str,
    report_content: str | None = None,
    timestamp: str | None = None,
) -> AuditArtifact:
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
    
    # Extract key metadata from manifest if available
    key_id = None
    sig_alg = None
    signed_at = None
    if manifest_path.exists():
        try:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8"),
                parse_float=Decimal,
                parse_constant=_reject_non_finite_json_constant,
            )
            key_id = manifest.get("key_id")
            sig_alg = manifest.get("sig_alg")
            signed_at = manifest.get("signed_at")
        except (json.JSONDecodeError, OSError, ValueError):
            pass
    
    # Determine key_status from registry
    key_status = None
    if key_id:
        from ilc_core.ledger.canon_bundle_key_registry import get_registry
        registry = get_registry()
        key_status = registry.status(key_id)
    
    audit: AuditArtifact = {
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
        "key_id": key_id,
        "sig_alg": sig_alg,
        "signed_at": signed_at,
        "key_status": key_status,
    }
    
    return audit


def write_audit_artifact(audit: AuditArtifact, audit_path: Path) -> bool:
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
        json_content = json.dumps(
            audit,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
        audit_path.write_text(json_content, encoding="utf-8")
        return True
    except (OSError, TypeError, ValueError):
        return False
