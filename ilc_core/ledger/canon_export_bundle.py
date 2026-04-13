import json
import hashlib
import math
from decimal import Decimal
from pathlib import Path
from typing import TypeAlias, TypedDict

from ilc_core.exceptions import LedgerExportContractError
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, exact_to_canonical_string

def _sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hexdigest of bytes."""
    return hashlib.sha256(data).hexdigest()


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class CanonBundleManifest(TypedDict):
    bundle_format: str
    export_format: JsonValue
    hash_alg: str
    created_at: str
    export_hash: str
    validate_hash: str
    canon_hash: JsonValue
    export_path: str
    validate_path: str


def _normalize_bundle_value(value: object) -> JsonValue:
    if isinstance(value, bool) or value is None or isinstance(value, str) or isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        return decimal_to_canonical_string(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LedgerExportContractError("non_finite_numeric_scalar_in_bundle_payload")
        return exact_to_canonical_string(
            value,
            token="invalid_numeric_scalar_in_bundle_payload",
        )
    if isinstance(value, dict):
        return {
            str(key): _normalize_bundle_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_normalize_bundle_value(item) for item in value]
    raise LedgerExportContractError("unsupported_scalar_in_bundle_payload")


def _dump_bundle_json(payload: object) -> bytes:
    normalized_payload = _normalize_bundle_value(payload)
    return json.dumps(
        normalized_payload,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")


def write_canon_export_bundle(
    export: JsonObject, 
    validation: JsonObject, 
    bundle_dir: Path, 
    created_at: str | None = None, 
    overwrite: bool = False
) -> Path:
    """
    Write a canon export bundle directory containing export.json, validate.json, and manifest.json.
    
    Args:
        export: The canon export dictionary (v0.1). Must contain 'canon_hash'.
        validation: The validation report dictionary.
        bundle_dir: Destination directory path.
        created_at: Optional creation timestamp for manifest.
        overwrite: If True, allow writing to non-empty directory.
        
    Returns:
        The path to the created bundle directory.
        
    Raises:
        LedgerExportContractError: If export is missing required fields.
        FileExistsError: If bundle_dir is not empty and overwrite is False.
    """
    # 1. Validate Input
    if "canon_hash" not in export:
        raise LedgerExportContractError("export payload missing required 'canon_hash'")
        
    export_fmt = export.get("canon_export_format", "unknown")
    
    # 2. Prepare Directory
    if not bundle_dir.exists():
        bundle_dir.mkdir(parents=True, exist_ok=True)
    
    if any(bundle_dir.iterdir()) and not overwrite:
        raise FileExistsError(f"Bundle directory is not empty: {bundle_dir}")
        
    # 3. Serialize Content (Deterministic)
    # Use sort_keys=True and separators=(",", ":") for canonical JSON form
    export_bytes = _dump_bundle_json(export)
    validate_bytes = _dump_bundle_json(validation)
    
    # 4. Write Content Files
    # Append newline strictly
    (bundle_dir / "export.json").write_bytes(export_bytes + b"\n")
    (bundle_dir / "validate.json").write_bytes(validate_bytes + b"\n")
    
    # 5. Compute Hashes
    export_hash = _sha256_bytes(export_bytes)
    validate_hash = _sha256_bytes(validate_bytes)
    
    # 6. Create Manifest
    created_at = created_at or "2026-02-05T00:00:00+00:00" # Default, usually caller passes UTC now
    
    manifest: CanonBundleManifest = {
        "bundle_format": "v0.1",
        "export_format": export_fmt,
        "hash_alg": "sha256",
        "created_at": created_at,
        "export_hash": export_hash,
        "validate_hash": validate_hash,
        "canon_hash": export["canon_hash"],
        "export_path": "export.json",
        "validate_path": "validate.json"
    }
    
    manifest_bytes = _dump_bundle_json(manifest)
    (bundle_dir / "manifest.json").write_bytes(manifest_bytes + b"\n")
    
    return bundle_dir
