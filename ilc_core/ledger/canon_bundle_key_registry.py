"""
Key registry for canon bundle signing key rotation.

Tracks current, previous, and deprecated keys to support key lifecycle management.
"""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import hashlib
import hmac
from datetime import datetime, timezone


@dataclass
class KeyRegistry:
    """Registry of signing keys with lifecycle status."""
    current_keys: List[str] = field(default_factory=list)
    previous_keys: List[str] = field(default_factory=list)
    deprecated_keys: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True if registry has no keys configured."""
        return not self.current_keys and not self.previous_keys and not self.deprecated_keys

    def status(self, key_id: str) -> str:
        """Return the lifecycle status of a key_id."""
        # If registry is empty, only allow all keys when explicitly enabled.
        if self.is_empty():
            if os.environ.get("ILC_ALLOW_EMPTY_KEY_REGISTRY") == "1":
                return "current"
            return "unknown"
        if key_id in self.current_keys:
            return "current"
        if key_id in self.previous_keys:
            return "previous"
        if key_id in self.deprecated_keys:
            return "deprecated"
        return "unknown"



# Default registry for MVP (placeholder key_ids)
DEFAULT_REGISTRY = KeyRegistry(
    current_keys=[],
    previous_keys=[],
    deprecated_keys=[],
)


def load_registry(path: Optional[Path] = None) -> KeyRegistry:
    """
    Load key registry from JSON file or return defaults.
    
    Args:
        path: Optional path to registry JSON file.
              Falls back to ILC_KEY_REGISTRY_PATH env var if not provided.
    
    Returns:
        KeyRegistry instance.
    """
    if path is None:
        env_path = os.environ.get("ILC_KEY_REGISTRY_PATH")
        if env_path:
            path = Path(env_path)
        else:
            default_path = Path("config") / "canon_key_registry_v0.1.json"
            if default_path.exists():
                path = default_path
    
    if path and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return KeyRegistry(
                current_keys=data.get("current_keys", []),
                previous_keys=data.get("previous_keys", []),
                deprecated_keys=data.get("deprecated_keys", []),
            )
        except (json.JSONDecodeError, OSError):
            pass
    
    return DEFAULT_REGISTRY


# Module-level registry instance (lazy loaded on first use)
_registry: Optional[KeyRegistry] = None


def get_registry() -> KeyRegistry:
    """Get the global key registry instance."""
    global _registry
    if _registry is None:
        _registry = load_registry()
    return _registry


def set_registry(registry: KeyRegistry) -> None:
    """Set the global key registry (for testing)."""
    global _registry
    _registry = registry


def reset_registry() -> None:
    """Reset the global registry to force reload."""
    global _registry
    _registry = None


# Key ID pattern: lowercase hex, exactly 16 characters
KEY_ID_PATTERN = r'^[0-9a-f]{16}$'
MAX_LIST_SIZE = 10000
STRICT_ISO8601_TZ_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"


def _is_strict_iso8601_tz(value: str) -> bool:
    return re.match(STRICT_ISO8601_TZ_PATTERN, value) is not None


def validate_registry_file(path: Path, strict: bool = False, prod: bool = False) -> dict:
    """
    Validate a key registry file.
    
    Args:
        path: Path to the registry JSON file.
        strict: If True, empty current_keys is an error instead of warning.
        prod: If True, enforce production mode (empty current_keys is hard error).
    
    Returns:
        Dict with {ok: bool, errors: list, warnings: list}.
    """
    errors = []
    warnings = []
    
    # Check file exists
    if not path.exists():
        return {"ok": False, "errors": ["file_not_found"], "warnings": []}
    
    # Try to read and parse JSON
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {"ok": False, "errors": ["file_read_error"], "warnings": []}
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"ok": False, "errors": ["invalid_json"], "warnings": []}
    
    if not isinstance(data, dict):
        return {"ok": False, "errors": ["schema_violation:root_not_object"], "warnings": []}
    
    # Check required fields
    required = ["registry_version", "updated_at", "current_keys", "previous_keys", "deprecated_keys"]
    for field in required:
        if field not in data:
            errors.append(f"schema_violation:missing_{field}")
    
    # Check registry_version
    if data.get("registry_version") != "v0.1":
        errors.append("schema_violation:invalid_registry_version")
    
    # Check updated_at strict ISO-8601 with timezone
    updated_at = data.get("updated_at")
    if updated_at is not None:
        if not isinstance(updated_at, str):
            errors.append("invalid_updated_at")
        else:
            if not _is_strict_iso8601_tz(updated_at):
                errors.append("invalid_updated_at")
    
    # Check additional properties
    allowed_keys = {"registry_version", "updated_at", "current_keys", "previous_keys", "deprecated_keys", "notes"}
    extra_keys = set(data.keys()) - allowed_keys
    if extra_keys:
        errors.append(f"schema_violation:unknown_fields:{','.join(sorted(extra_keys))}")
    
    # Validate key lists
    key_pattern = re.compile(KEY_ID_PATTERN)
    all_keys = []
    
    for list_name in ["current_keys", "previous_keys", "deprecated_keys"]:
        key_list = data.get(list_name, [])
        
        if not isinstance(key_list, list):
            errors.append(f"schema_violation:{list_name}_not_array")
            continue
        
        # Check size guardrail
        if len(key_list) > MAX_LIST_SIZE:
            warnings.append(f"key_list_too_large:{list_name}")
        
        # Check for duplicates within list
        seen = set()
        for key_id in key_list:
            if not isinstance(key_id, str):
                errors.append(f"schema_violation:{list_name}_invalid_type")
                continue
            if not key_pattern.match(key_id):
                errors.append(f"schema_violation:{list_name}_invalid_pattern:{key_id}")
            if key_id in seen:
                errors.append(f"duplicate_keys:{list_name}:{key_id}")
            seen.add(key_id)
            all_keys.append(key_id)
        
        # Check if sorted (only if all elements are strings)
        if all(isinstance(key_id, str) for key_id in key_list):
            sorted_list = sorted(key_list)
            if key_list != sorted_list:
                warnings.append(f"unsorted_keys:{list_name}")
    
    # Check for overlaps between lists
    current = set(data.get("current_keys", []))
    previous = set(data.get("previous_keys", []))
    deprecated = set(data.get("deprecated_keys", []))
    
    overlaps = (current & previous) | (current & deprecated) | (previous & deprecated)
    if overlaps:
        errors.append(f"overlapping_keys:{','.join(sorted(overlaps))}")
    
    # Check empty current_keys
    if not data.get("current_keys"):
        if prod:
            errors.append("prod_empty_registry")
        elif strict:
            errors.append("empty_current_keys")
        else:
            warnings.append("empty_current_keys")
    
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }



def canonical_registry_bytes(registry_path: Path) -> bytes:
    """
    Return canonical bytes of registry JSON for signing/verification.
    
    Canonical form: sorted keys, compact separators, no trailing newline.
    """
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _derive_key_id(key: bytes) -> str:
    """Derive key_id from key bytes (first 16 hex chars of SHA-256)."""
    return hashlib.sha256(key).hexdigest()[:16]


def sign_registry_file(
    registry_path: Path,
    key: bytes,
    sig_path: Optional[Path] = None
) -> dict:
    """
    Sign a registry file and write detached signature.
    
    Args:
        registry_path: Path to registry JSON file.
        key: Signing key bytes.
        sig_path: Optional signature file path. Defaults to registry_path + .sig.
    
    Returns:
        Dict with {ok: bool, key_id: str, sig_alg: str, sig_path: str, registry_hash: str}.
    """

    
    if sig_path is None:
        sig_path = registry_path.with_suffix(registry_path.suffix + ".sig")
    
    try:
        canonical = canonical_registry_bytes(registry_path)
    except (json.JSONDecodeError, OSError) as e:
        return {"ok": False, "error": f"failed_to_read_registry:{e}"}
    
    # Compute hash and signature
    registry_hash = hashlib.sha256(canonical).hexdigest()
    signature = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    key_id = _derive_key_id(key)
    signed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    sig_data = {
        "sig_alg": "hmac-sha256",
        "key_id": key_id,
        "signed_at": signed_at,
        "registry_hash": registry_hash,
        "signature_hex": signature,
    }
    
    try:
        sig_path.write_text(json.dumps(sig_data, indent=2), encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"failed_to_write_sig:{e}"}
    
    return {
        "ok": True,
        "key_id": key_id,
        "sig_alg": "hmac-sha256",
        "sig_path": str(sig_path),
        "registry_hash": registry_hash,
    }


def verify_registry_file_signature(
    registry_path: Path,
    key: bytes,
    sig_path: Optional[Path] = None
) -> dict:
    """
    Verify a registry file signature.
    
    Args:
        registry_path: Path to registry JSON file.
        key: Signing key bytes.
        sig_path: Optional signature file path. Defaults to registry_path + .sig.
    
    Returns:
        Dict with {ok: bool, errors: list, warnings: list, registry_hash: str, key_id: str}.
    """

    
    if sig_path is None:
        sig_path = registry_path.with_suffix(registry_path.suffix + ".sig")
    
    errors = []
    warnings = []
    
    # Check sig file exists
    if not sig_path.exists():
        return {"ok": False, "errors": ["signature_missing"], "warnings": []}
    
    # Read signature file
    try:
        sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"ok": False, "errors": ["signature_invalid"], "warnings": []}
    
    # Validate signature file structure
    required_fields = ["sig_alg", "key_id", "signed_at", "registry_hash", "signature_hex"]
    for f in required_fields:
        if f not in sig_data:
            errors.append(f"signature_invalid:missing_{f}")
    
    if errors:
        return {"ok": False, "errors": errors, "warnings": []}
    
    # Validate signed_at format
    signed_at = sig_data.get("signed_at", "")
    if not _is_strict_iso8601_tz(signed_at):
        errors.append("signature_invalid:invalid_signed_at")
    
    # Validate sig_alg
    if sig_data.get("sig_alg") != "hmac-sha256":
        errors.append("signature_invalid:unsupported_sig_alg")
    
    # Read registry and compute canonical form
    try:
        canonical = canonical_registry_bytes(registry_path)
    except (json.JSONDecodeError, OSError):
        return {"ok": False, "errors": ["file_read_error"], "warnings": []}
    
    # Verify hash
    computed_hash = hashlib.sha256(canonical).hexdigest()
    if computed_hash != sig_data.get("registry_hash"):
        errors.append("signature_mismatch:hash_mismatch")
    
    # Verify HMAC signature
    expected_sig = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig_data.get("signature_hex", "")):
        errors.append("signature_mismatch")
    
    # Check key_id matches
    computed_key_id = _derive_key_id(key)
    if computed_key_id != sig_data.get("key_id"):
        errors.append("signature_key_unknown")
    
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "registry_hash": computed_hash,
        "key_id": sig_data.get("key_id"),
    }


def _atomic_write(path: Path, data: str) -> None:
    """Write data to path atomically using temp file + rename."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    tmp.replace(path)


def _now_iso8601() -> str:
    """Return current UTC time as strict ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rotate_registry(
    registry_path: Path,
    new_key_id: str,
    force: bool = False
) -> dict:
    """
    Rotate registry: move current→previous→deprecated, insert new key.
    
    Args:
        registry_path: Path to registry JSON file.
        new_key_id: New key ID to become sole current key.
        force: If True, override validation failures.
    
    Returns:
        Dict with {ok, old_current_keys, new_current_key, updated_at, warnings}.
    """
    warnings = []
    
    # Validate new_key_id format
    if not re.match(KEY_ID_PATTERN, new_key_id):
        return {"ok": False, "error": "invalid_new_key_id"}
    
    # Check file exists
    if not registry_path.exists():
        return {"ok": False, "error": "file_not_found"}
    
    # Load and validate current registry
    try:
        content = registry_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (json.JSONDecodeError, OSError):
        return {"ok": False, "error": "file_read_error"}
    
    # Validate before rotation unless force
    if not force:
        validation = validate_registry_file(registry_path)
        if not validation["ok"]:
            return {"ok": False, "error": "validation_failed", "validation_errors": validation["errors"]}
    
    # Check if new key already exists
    all_keys = (
        set(data.get("current_keys", [])) |
        set(data.get("previous_keys", [])) |
        set(data.get("deprecated_keys", []))
    )
    if new_key_id in all_keys:
        return {"ok": False, "error": "key_already_exists"}
    
    # Perform rotation
    old_current = sorted(set(data.get("current_keys", [])))
    old_previous = sorted(set(data.get("previous_keys", [])))
    old_deprecated = sorted(set(data.get("deprecated_keys", [])))
    
    new_data = {
        **data,
        "current_keys": [new_key_id],
        "previous_keys": old_current,
        "deprecated_keys": sorted(set(old_deprecated) | set(old_previous)),
        "updated_at": _now_iso8601(),
    }
    
    # Invalidate existing .sig file
    sig_path = registry_path.with_suffix(registry_path.suffix + ".sig")
    if sig_path.exists():
        try:
            sig_path.unlink()
            warnings.append("signature_invalidated")
        except OSError:
            warnings.append("signature_invalidation_failed")
    
    # Atomic write
    try:
        _atomic_write(registry_path, json.dumps(new_data, indent=2))
    except OSError as e:
        return {"ok": False, "error": f"write_failed:{e}"}
    
    return {
        "ok": True,
        "old_current_keys": old_current,
        "new_current_key": new_key_id,
        "updated_at": new_data["updated_at"],
        "warnings": warnings,
    }


def backup_registry(registry_path: Path, backup_dir: Path) -> dict:
    """
    Create timestamped backup of registry file.
    
    Args:
        registry_path: Path to registry JSON file.
        backup_dir: Directory for backup files.
    
    Returns:
        Dict with {ok, backup_path}.
    """

    
    if not registry_path.exists():
        return {"ok": False, "error": "file_not_found"}
    
    # Create backup directory if needed
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return {"ok": False, "error": f"backup_dir_create_failed:{e}"}
    
    # Generate backup filename
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup_name = f"{registry_path.name}.{stamp}.bak"
    backup_path = backup_dir / backup_name
    
    # Copy file
    try:
        content = registry_path.read_text(encoding="utf-8")
        backup_path.write_text(content, encoding="utf-8")
    except OSError as e:
        return {"ok": False, "error": f"backup_failed:{e}"}
    
    return {"ok": True, "backup_path": str(backup_path)}


def restore_registry(
    backup_path: Path,
    registry_path: Path,
    force: bool = False,
    prod: bool = False
) -> dict:
    """
    Restore registry from backup.
    
    Args:
        backup_path: Path to backup file.
        registry_path: Path to registry file to restore to.
    
    Returns:
        Dict with {ok, restored_from}.
    """
    if not backup_path.exists():
        return {"ok": False, "error": "backup_not_found"}
    
    # Read and validate backup
    try:
        content = backup_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (json.JSONDecodeError, OSError):
        return {"ok": False, "error": "backup_invalid"}
    
    # Validate backup content is valid registry format
    # Write to temp file and validate
    tmp_path = registry_path.with_suffix(registry_path.suffix + ".restore_tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        validation = validate_registry_file(tmp_path, prod=prod)
        if not validation["ok"] and not force:
            tmp_path.unlink()
            return {"ok": False, "error": "backup_validation_failed", "validation_errors": validation["errors"]}
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    
    # Atomic restore
    try:
        _atomic_write(registry_path, content)
    except OSError as e:
        return {"ok": False, "error": f"restore_failed:{e}"}
    
    # Invalidate existing .sig file
    sig_path = registry_path.with_suffix(registry_path.suffix + ".sig")
    if sig_path.exists():
        try:
            sig_path.unlink()
        except OSError:
            pass
    
    return {
        "ok": True,
        "restored_from": str(backup_path),
        "warnings": ["validation_bypassed"] if (force and not validation["ok"]) else [],
    }
