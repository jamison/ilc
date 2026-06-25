# SPDX-License-Identifier: AGPL-3.0-only
"""
Registry bundle creation and verification for canon bundle key registry.

A registry bundle is a directory containing:
- canon_key_registry_v0.1.json (registry copy)
- canon_key_registry_v0.1.json.sig (detached signature)
- registry_manifest.json (metadata: hash, size, created_at, sig info)
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Optional

from ilc_core.ledger.canon_bundle_key_registry import (
    _is_strict_iso8601_tz,
    canonical_registry_bytes,
    sign_registry_file,
    verify_registry_file_signature,
    validate_registry_file,
    _atomic_write,
)


BUNDLE_VERSION = "v0.1"
BUNDLE_DIR_NAME = "canon_key_registry_bundle_v0.1"
REGISTRY_FILENAME = "canon_key_registry_v0.1.json"
SIG_FILENAME = "canon_key_registry_v0.1.json.sig"
MANIFEST_FILENAME = "registry_manifest.json"
MAX_BUNDLE_BYTES = 5 * 1024 * 1024  # 5 MB

STRICT_ISO8601_TZ_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"


def _compute_file_hash(path: Path) -> str:
    """Compute SHA-256 hash of file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_bundle_created_at(
    *,
    created_at: str | None,
    sig_data: dict,
    registry_data: dict,
) -> str:
    if created_at is not None:
        if not _is_strict_iso8601_tz(created_at):
            raise ValueError("invalid_created_at")
        return created_at

    signed_at = sig_data.get("signed_at")
    if isinstance(signed_at, str):
        if not _is_strict_iso8601_tz(signed_at):
            raise ValueError("invalid_signed_at")
        return signed_at

    updated_at = registry_data.get("updated_at")
    if isinstance(updated_at, str):
        if not _is_strict_iso8601_tz(updated_at):
            raise ValueError("invalid_updated_at")
        return updated_at

    return "1970-01-01T00:00:00Z"


def build_registry_bundle(
    registry_path: Path,
    key: bytes,
    out_dir: Path,
    force: bool = False,
    sig_path: Optional[Path] = None,
    created_at: Optional[str] = None,
) -> dict:
    """
    Build a registry bundle.
    
    Args:
        registry_path: Path to registry JSON file.
        key: Signing key bytes.
        out_dir: Output directory (bundle will be created inside).
        force: If True, overwrite existing bundle.
        sig_path: Optional existing signature file to use.
    
    Returns:
        Dict with {ok, bundle_dir, manifest}.
    """
    if not registry_path.exists():
        return {"ok": False, "error": "registry_not_found"}
    
    # Validate registry
    validation = validate_registry_file(registry_path)
    if not validation["ok"]:
        return {"ok": False, "error": "registry_invalid", "validation_errors": validation["errors"]}
    
    # Create bundle directory
    bundle_dir = out_dir / BUNDLE_DIR_NAME
    if bundle_dir.exists():
        if not force:
            return {"ok": False, "error": "bundle_exists"}
        shutil.rmtree(bundle_dir)
    
    try:
        bundle_dir.mkdir(parents=True)
    except OSError as e:
        return {"ok": False, "error": f"mkdir_failed:{e}"}
    
    # Copy registry
    dest_registry = bundle_dir / REGISTRY_FILENAME
    try:
        shutil.copy2(registry_path, dest_registry)
    except OSError as e:
        return {"ok": False, "error": f"copy_registry_failed:{e}"}
    
    # Sign or copy signature
    dest_sig = bundle_dir / SIG_FILENAME
    if sig_path and sig_path.exists():
        # Use existing signature
        try:
            shutil.copy2(sig_path, dest_sig)
        except OSError as e:
            return {"ok": False, "error": f"copy_sig_failed:{e}"}
        # Load sig data for manifest
        sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    else:
        # Sign registry
        sign_result = sign_registry_file(
            dest_registry,
            key,
            dest_sig,
            signed_at=created_at,
        )
        if not sign_result.get("ok"):
            return {"ok": False, "error": f"sign_failed:{sign_result.get('error')}"}
        sig_data = json.loads(dest_sig.read_text(encoding="utf-8"))
    
    # Compute hashes
    registry_hash = hashlib.sha256(canonical_registry_bytes(dest_registry)).hexdigest()
    sig_hash = _compute_file_hash(dest_sig)
    registry_size = dest_registry.stat().st_size
    
    # Load registry version
    registry_data = json.loads(dest_registry.read_text(encoding="utf-8"))
    registry_version = registry_data.get("registry_version", "unknown")
    
    # Build manifest
    try:
        manifest_created_at = _resolve_bundle_created_at(
            created_at=created_at,
            sig_data=sig_data,
            registry_data=registry_data,
        )
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    manifest = {
        "bundle_version": BUNDLE_VERSION,
        "created_at": manifest_created_at,
        "registry_path": REGISTRY_FILENAME,
        "registry_hash": registry_hash,
        "registry_size_bytes": registry_size,
        "sig_path": SIG_FILENAME,
        "sig_alg": sig_data.get("sig_alg", "hmac-sha256"),
        "key_id": sig_data.get("key_id"),
        "registry_version": registry_version,
        "signed": False,
        "sig_hash": sig_hash,
    }
    
    # Write manifest atomically
    manifest_json = json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    try:
        _atomic_write(bundle_dir / MANIFEST_FILENAME, manifest_json)
    except OSError as e:
        return {"ok": False, "error": f"manifest_write_failed:{e}"}
    
    return {
        "ok": True,
        "bundle_dir": str(bundle_dir),
        "manifest": manifest,
    }


def verify_registry_bundle(
    bundle_dir: Path,
    key: bytes,
    strict: bool = False,
) -> dict:
    """
    Verify a registry bundle.
    
    Args:
        bundle_dir: Path to bundle directory.
        key: Verification key bytes.
        strict: If True, use strict validation on registry.
    
    Returns:
        Dict with {ok, errors, warnings, registry_hash, key_id}.
    """
    import re
    
    errors = []
    warnings = []
    
    # Check bundle exists
    if not bundle_dir.exists():
        return {"ok": False, "errors": ["bundle_missing"], "warnings": []}
    
    if not bundle_dir.is_dir():
        return {"ok": False, "errors": ["bundle_not_directory"], "warnings": []}
    
    # Check manifest
    manifest_path = bundle_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return {"ok": False, "errors": ["manifest_missing"], "warnings": []}
    
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"ok": False, "errors": ["manifest_invalid"], "warnings": []}
    
    # Validate manifest fields
    required_fields = [
        "bundle_version", "created_at", "registry_path", "registry_hash",
        "registry_size_bytes", "sig_path", "sig_alg", "key_id",
        "registry_version", "sig_hash"
    ]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"manifest_invalid:missing_{field}")
    
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}
    
    # Validate bundle_version
    if manifest["bundle_version"] != BUNDLE_VERSION:
        errors.append("bundle_version_mismatch")
    
    # Validate created_at
    if not re.match(STRICT_ISO8601_TZ_PATTERN, manifest.get("created_at", "")):
        errors.append("manifest_invalid:invalid_created_at")
    
    # Check path traversal
    registry_path_str = manifest.get("registry_path", "")
    sig_path_str = manifest.get("sig_path", "")
    if Path(registry_path_str).name != registry_path_str:
        errors.append("path_traversal:registry_path")
    if Path(sig_path_str).name != sig_path_str:
        errors.append("path_traversal:sig_path")
    
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    # Ensure bundle contains only expected files
    allowed_files = {REGISTRY_FILENAME, SIG_FILENAME, MANIFEST_FILENAME}
    extra_files = [
        p.name for p in bundle_dir.iterdir()
        if p.is_file() and p.name not in allowed_files
    ]
    if extra_files:
        errors.append("bundle_extra_files")

    # Check registry exists
    registry_path = bundle_dir / registry_path_str
    if not registry_path.exists():
        errors.append("registry_missing")
        return {"ok": False, "errors": errors, "warnings": warnings}
    
    # Check signature exists
    sig_path = bundle_dir / sig_path_str
    if not sig_path.exists():
        errors.append("sig_missing")
        return {"ok": False, "errors": errors, "warnings": warnings}
    
    # Validate registry
    validation = validate_registry_file(registry_path, strict=strict)
    if not validation["ok"]:
        errors.append("registry_invalid")
        errors.extend(validation["errors"])
    warnings.extend(validation.get("warnings", []))
    
    # Verify registry hash
    computed_registry_hash = hashlib.sha256(canonical_registry_bytes(registry_path)).hexdigest()
    if computed_registry_hash != manifest["registry_hash"]:
        errors.append("hash_mismatch")
    
    # Verify sig hash
    computed_sig_hash = _compute_file_hash(sig_path)
    if computed_sig_hash != manifest["sig_hash"]:
        errors.append("sig_hash_mismatch")
    
    # Verify signature
    sig_result = verify_registry_file_signature(registry_path, key, sig_path)
    if not sig_result.get("ok"):
        errors.append("signature_invalid")
        errors.extend(sig_result.get("errors", []))
    
    # Bundle size warning
    total_bytes = sum(p.stat().st_size for p in bundle_dir.iterdir() if p.is_file())
    if total_bytes > MAX_BUNDLE_BYTES:
        warnings.append("bundle_too_large")
    
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "registry_hash": manifest["registry_hash"],
        "key_id": manifest.get("key_id"),
    }
