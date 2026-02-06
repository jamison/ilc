"""
CLI for validating and signing canon bundle key registry files.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json --strict
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json --sign --key-file key.txt
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry registry.json --sig registry.sig --key-file key.txt
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry-dir ./config --key-file key.txt
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry registry.json --prod --key-file key.txt
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry import (
    validate_registry_file,
    sign_registry_file,
    verify_registry_file_signature,
)


def _load_key_bytes(key_path: Path) -> bytes:
    """Load key bytes from file, decoding base64 if applicable."""
    content = key_path.read_bytes().strip()
    # Try base64 decode (consistent with bundle signing)
    try:
        decoded = base64.b64decode(content, validate=True)
        # If successfully decoded and looks like raw bytes, use it
        if len(decoded) >= 16:
            return decoded
    except Exception:
        pass
    # Otherwise use raw bytes
    return content


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and sign canon bundle key registry files"
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
    
    args = parser.parse_args()
    
    # Detect production mode: CLI flag overrides env
    prod = args.prod or os.environ.get("ILC_ENV") == "prod"
    
    # Resolve registry path
    if args.registry_dir:
        registry_dir = Path(args.registry_dir).resolve()
        registry_path = registry_dir / "canon_key_registry_v0.1.json"
        # Default sig path in registry-dir mode
        default_sig_path = registry_dir / "canon_key_registry_v0.1.json.sig"
    else:
        registry_path = Path(args.registry).resolve()
        default_sig_path = None
    
    # Handle IO errors
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
    
    # Production mode requires signature verification
    if prod and not args.key_file and not args.sign:
        output = {
            "ok": False,
            "errors": ["prod_signature_required"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 1
    
    # Check if --sig provided without --key-file (verification requires key)
    if args.sig and not args.key_file and not args.sign:
        output = {
            "ok": False,
            "errors": ["key_missing_for_verify"],
            "warnings": [],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 1
    
    # Signing mode
    if args.sign:
        if not args.key_file:
            output = {
                "ok": False,
                "errors": ["key_missing_for_sign"],
                "warnings": [],
                "registry_path": str(registry_path),
                "prod": prod,
            }
            print(json.dumps(output, separators=(",", ":")))
            return 1
        
        key_path = Path(args.key_file)
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
        
        key = _load_key_bytes(key_path)
        sig_path = Path(args.sig) if args.sig else (default_sig_path if default_sig_path else None)
        
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
    
    # Determine strict mode (prod implies strict, but --allow-empty is ignored in prod)
    strict = args.strict and not args.allow_empty
    
    # Validate registry structure first
    result = validate_registry_file(registry_path, strict=strict, prod=prod)

    # IO error handling: treat as exit code 2
    if any(err in result["errors"] for err in ("file_not_found", "file_read_error")):
        output = {
            "ok": False,
            "errors": result["errors"],
            "warnings": result["warnings"],
            "registry_path": str(registry_path),
            "prod": prod,
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    # If allow-empty (and not prod), remove empty_current_keys from errors
    if args.allow_empty and not prod and "empty_current_keys" in result["errors"]:
        result["errors"].remove("empty_current_keys")
        if "empty_current_keys" not in result["warnings"]:
            result["warnings"].append("empty_current_keys")
        result["ok"] = len(result["errors"]) == 0
    
    # Signature verification if --key-file provided (without --sign)
    signature_ok = None
    sig_path_str = None
    registry_hash = None
    sig_key_id = None
    
    if args.key_file and not args.sign:
        key_path = Path(args.key_file)
        if not key_path.exists():
            result["errors"].append("key_file_not_found")
            result["ok"] = False
        else:
            key = _load_key_bytes(key_path)
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
    
    # Get key counts if valid JSON
    key_counts = {"current": 0, "previous": 0, "deprecated": 0}
    registry_version = None
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            key_counts["current"] = len(data.get("current_keys", []))
            key_counts["previous"] = len(data.get("previous_keys", []))
            key_counts["deprecated"] = len(data.get("deprecated_keys", []))
            registry_version = data.get("registry_version")
    except Exception:
        pass
    
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
