"""
CLI for validating, signing, and managing canon bundle key registry files.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json --strict
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json --sign --key-file key.txt
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry registry.json --rotate --new-key-id a1b2c3d4e5f6a7b8
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry registry.json --backup-dir ./backups
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry registry.json --restore ./backups/registry.bak
"""

import argparse
import json
import os
import sys
from pathlib import Path
import logging

from ilc_core.ledger.canon_bundle_key_registry import (
    validate_registry_file,
    sign_registry_file,
    verify_registry_file_signature,
    rotate_registry,
    backup_registry,
    restore_registry,
)
from ilc_core.cli._key_utils import load_key_bytes_with_b64_fallback

logger = logging.getLogger(__name__)


def _setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate, sign, and manage canon bundle key registry files"
    )
    registry_group = parser.add_mutually_exclusive_group(required=True)
    registry_group.add_argument(
        "--registry",
        type=str,
        help="Path to the registry JSON file"
    )
    registry_group.add_argument(
        "--registry-dir",
        type=str,
        help="Directory containing canon_key_registry_v0.1.json"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat empty current_keys as an error"
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow empty current_keys even in strict mode"
    )
    parser.add_argument(
        "--sign",
        action="store_true",
        help="Sign the registry file"
    )
    parser.add_argument(
        "--sig",
        type=str,
        help="Path to signature file (for signing or verification)"
    )
    parser.add_argument(
        "--key-file",
        type=str,
        help="Path to key file (required for signing or signature verification)"
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Production mode: require signature, disallow empty registry"
    )
    # Ops commands
    parser.add_argument(
        "--rotate",
        action="store_true",
        help="Rotate keys: add new current, move old keys"
    )
    parser.add_argument(
        "--new-key-id",
        type=str,
        help="New key ID for rotation (required with --rotate)"
    )
    parser.add_argument(
        "--backup-dir",
        type=str,
        help="Create a timestamped backup in this directory"
    )
    parser.add_argument(
        "--restore",
        type=str,
        help="Restore registry from backup file"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operation (override validation failures or prod restrictions)"
    )
    return parser


def _handle_restore(backup_path: Path, registry_path: Path, force: bool, prod: bool) -> int:
    result = restore_registry(backup_path, registry_path, force=force, prod=prod)
    output = {
        "ok": result.get("ok", False),
        "errors": [result.get("error")] if result.get("error") else [],
        "warnings": result.get("warnings", []),
        "registry_path": str(registry_path),
        "restored_from": result.get("restored_from"),
        "prod": prod,
    }
    if result.get("validation_errors"):
        output["validation_errors"] = result["validation_errors"]
    print(json.dumps(output, separators=(",", ":")))
    return 0 if result.get("ok") else (2 if "not_found" in result.get("error", "") else 1)


def _handle_backup(registry_path: Path, backup_dir: Path, prod: bool) -> int:
    result = backup_registry(registry_path, backup_dir)
    output = {
        "ok": result.get("ok", False),
        "errors": [result.get("error")] if result.get("error") else [],
        "warnings": [],
        "registry_path": str(registry_path),
        "backup_path": result.get("backup_path"),
        "prod": prod,
    }
    print(json.dumps(output, separators=(",", ":")))
    return 0 if result.get("ok") else 2


def _handle_rotate(registry_path: Path, new_key_id: str, force: bool, prod: bool) -> int:
    if not new_key_id:
        output = {
            "ok": False,
            "errors": ["new_key_id_required"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 1
    
    if prod and not force:
        output = {
            "ok": False,
            "errors": ["prod_rotation_requires_force"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 1
    
    result = rotate_registry(registry_path, new_key_id, force=force)
    output = {
        "ok": result.get("ok", False),
        "errors": [result.get("error")] if result.get("error") else [],
        "warnings": result.get("warnings", []),
        "registry_path": str(registry_path),
        "rotation": True,
        "old_current_keys": result.get("old_current_keys"),
        "new_current_key": result.get("new_current_key"),
        "updated_at": result.get("updated_at"),
        "prod": prod,
    }
    if result.get("validation_errors"):
        output["validation_errors"] = result["validation_errors"]
    print(json.dumps(output, separators=(",", ":")))
    return 0 if result.get("ok") else 1


def _handle_sign(registry_path: Path, key_file: str, sig_file: str, default_sig_path: Path, prod: bool) -> int:
    if not key_file:
        output = {
            "ok": False,
            "errors": ["key_missing_for_sign"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 1
    
    key_path = Path(key_file)
    if not key_path.exists():
        output = {
            "ok": False,
            "errors": ["key_file_not_found"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    key = load_key_bytes_with_b64_fallback(key_path)
    sig_path = Path(sig_file) if sig_file else (default_sig_path if default_sig_path else None)
    
    result = sign_registry_file(registry_path, key, sig_path)
    output = {
        "ok": result.get("ok", False),
        "errors": [result.get("error")] if result.get("error") else [],
        "warnings": [],
        "registry_path": str(registry_path),
        "sig_path": result.get("sig_path"),
        "key_id": result.get("key_id"),
        "sig_alg": result.get("sig_alg"),
        "registry_hash": result.get("registry_hash"),
        "prod": prod,
    }
    print(json.dumps(output, separators=(",", ":")))
    return 0 if result.get("ok") else 1


def main() -> int:
    parser = _setup_parser()
    args = parser.parse_args()
    
    # Detect production mode: CLI flag overrides env
    prod = args.prod or os.environ.get("ILC_ENV") == "prod"
    
    # Resolve registry path
    if args.registry_dir:
        registry_dir = Path(args.registry_dir).resolve()
        registry_path = registry_dir / "canon_key_registry_v0.1.json"
        default_sig_path = registry_dir / "canon_key_registry_v0.1.json.sig"
    else:
        registry_path = Path(args.registry).resolve()
        default_sig_path = None
    
    # Restore mode (check first since registry may not exist yet)
    if args.restore:
        return _handle_restore(Path(args.restore).resolve(), registry_path, args.force, prod)
    
    # Check if registry exists for other ops
    if not registry_path.exists():
        output = {
            "ok": False,
            "errors": ["file_not_found"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    if args.backup_dir:
        return _handle_backup(registry_path, Path(args.backup_dir).resolve(), prod)
        
    if args.rotate:
        return _handle_rotate(registry_path, args.new_key_id, args.force, prod)
    
    # Production policy checks
    if prod and not args.key_file and not args.sign:
        print(json.dumps({"ok": False, "errors": ["prod_signature_required"], "warnings": [], "registry_path": str(registry_path), "prod": prod}, separators=(",", ":")))
        return 1
    
    if args.sig and not args.key_file and not args.sign:
        print(json.dumps({"ok": False, "errors": ["key_missing_for_verify"], "warnings": [], "registry_path": str(registry_path), "prod": prod}, separators=(",", ":")))
        return 1
    
    if args.sign:
        return _handle_sign(registry_path, args.key_file, args.sig, default_sig_path, prod)
    
    # Validate and optional verify
    strict = args.strict and not args.allow_empty
    result = validate_registry_file(registry_path, strict=strict, prod=prod)

    if any(err in result["errors"] for err in ("file_not_found", "file_read_error")):
        output = {
            "ok": False, "errors": result["errors"], "warnings": result["warnings"],
            "registry_path": str(registry_path), "prod": prod
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    if args.allow_empty and not prod and "empty_current_keys" in result["errors"]:
        result["errors"].remove("empty_current_keys")
        if "empty_current_keys" not in result["warnings"]:
           result["warnings"].append("empty_current_keys")
        result["ok"] = len(result["errors"]) == 0
    
    signature_ok = None
    sig_path_str = None
    registry_hash = None
    sig_key_id = None
    
    if args.key_file:
        key_path = Path(args.key_file)
        if not key_path.exists():
            result["errors"].append("key_file_not_found")
            result["ok"] = False
        else:
            key = load_key_bytes_with_b64_fallback(key_path)
            sig_path = Path(args.sig) if args.sig else (default_sig_path if default_sig_path else None)
            
            sig_result = verify_registry_file_signature(registry_path, key, sig_path)
            signature_ok = sig_result.get("ok")
            sig_path_str = str(sig_path) if sig_path else str(registry_path) + ".sig"
            registry_hash = sig_result.get("registry_hash")
            sig_key_id = sig_result.get("key_id")
            
            if not sig_result.get("ok"):
                result["errors"].extend(sig_result.get("errors", []))
                result["ok"] = False
            result["warnings"].extend(sig_result.get("warnings", []))
    
    # Get key counts
    key_counts = {"current": 0, "previous": 0, "deprecated": 0}
    registry_version = None
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            key_counts["current"] = len(data.get("current_keys", []))
            key_counts["previous"] = len(data.get("previous_keys", []))
            key_counts["deprecated"] = len(data.get("deprecated_keys", []))
            registry_version = data.get("registry_version")
    except Exception as exc:
        logger.debug("registry_summary_parse_skipped path=%s error=%s", registry_path, exc)
    
    output = {
        "ok": result["ok"],
        "errors": result["errors"],
        "warnings": result["warnings"],
        "registry_path": str(registry_path),
        "registry_version": registry_version,
        "key_counts": key_counts,
        "prod": prod,
    }
    
    if signature_ok is not None:
        output["signature_ok"] = signature_ok
        output["sig_path"] = sig_path_str
        output["registry_hash"] = registry_hash
        output["sig_key_id"] = sig_key_id
    
    print(json.dumps(output, separators=(",", ":")))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
