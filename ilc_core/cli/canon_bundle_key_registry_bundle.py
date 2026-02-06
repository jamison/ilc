"""
CLI for building and verifying canon bundle key registry bundles.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_bundle --build --registry /path/registry.json --key-file key.txt --out-dir ./bundles
    python3 -m ilc_core.cli.canon_bundle_key_registry_bundle --verify --bundle ./bundles/canon_key_registry_bundle_v0.1 --key-file key.txt
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_bundle import (
    build_registry_bundle,
    verify_registry_bundle,
)


def _load_key_bytes(key_path: Path) -> bytes:
    """Load key bytes from file, decoding base64 if applicable."""
    content = key_path.read_bytes().strip()
    # Try base64 decode (consistent with bundle signing)
    try:
        decoded = base64.b64decode(content, validate=True)
        if len(decoded) >= 16:
            return decoded
    except Exception:
        pass
    return content


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and verify canon bundle key registry bundles"
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--build",
        action="store_true",
        help="Build a registry bundle"
    )
    mode_group.add_argument(
        "--verify",
        action="store_true",
        help="Verify a registry bundle"
    )
    
    parser.add_argument(
        "--registry",
        type=str,
        help="Path to registry JSON file (for --build)"
    )
    parser.add_argument(
        "--bundle",
        type=str,
        help="Path to bundle directory (for --verify)"
    )
    parser.add_argument(
        "--key-file",
        type=str,
        required=True,
        help="Path to key file"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        help="Output directory for bundle (for --build)"
    )
    parser.add_argument(
        "--sig",
        type=str,
        help="Optional existing signature file to include in bundle"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing bundle"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict registry validation"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Force JSON output"
    )
    
    args = parser.parse_args()
    
    # Load key
    key_path = Path(args.key_file)
    if not key_path.exists():
        output = {
            "ok": False,
            "errors": ["key_file_not_found"],
            "warnings": [],
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    key = _load_key_bytes(key_path)
    
    # Build mode
    if args.build:
        if not args.registry:
            output = {
                "ok": False,
                "errors": ["registry_path_required"],
                "warnings": [],
            }
            print(json.dumps(output, separators=(",", ":")))
            return 1
        
        if not args.out_dir:
            output = {
                "ok": False,
                "errors": ["out_dir_required"],
                "warnings": [],
            }
            print(json.dumps(output, separators=(",", ":")))
            return 1
        
        registry_path = Path(args.registry).resolve()
        out_dir = Path(args.out_dir).resolve()
        sig_path = Path(args.sig).resolve() if args.sig else None
        
        if not registry_path.exists():
            output = {
                "ok": False,
                "errors": ["registry_not_found"],
                "warnings": [],
                "registry_path": str(registry_path),
            }
            print(json.dumps(output, separators=(",", ":")))
            return 2
        
        result = build_registry_bundle(
            registry_path, key, out_dir,
            force=args.force,
            sig_path=sig_path,
        )
        
        output = {
            "ok": result.get("ok", False),
            "errors": [result.get("error")] if result.get("error") else [],
            "warnings": [],
            "registry_path": str(registry_path),
            "bundle_dir": result.get("bundle_dir"),
        }
        if result.get("manifest"):
            output["manifest"] = result["manifest"]
        if result.get("validation_errors"):
            output["validation_errors"] = result["validation_errors"]
        
        print(json.dumps(output, separators=(",", ":")))
        return 0 if result.get("ok") else (2 if "not_found" in result.get("error", "") else 1)
    
    # Verify mode
    if args.verify:
        if not args.bundle:
            output = {
                "ok": False,
                "errors": ["bundle_path_required"],
                "warnings": [],
            }
            print(json.dumps(output, separators=(",", ":")))
            return 1
        
        bundle_dir = Path(args.bundle).resolve()
        
        result = verify_registry_bundle(bundle_dir, key, strict=args.strict)
        
        output = {
            "ok": result.get("ok", False),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "bundle_dir": str(bundle_dir),
            "registry_hash": result.get("registry_hash"),
            "key_id": result.get("key_id"),
        }
        
        print(json.dumps(output, separators=(",", ":")))
        io_errors = {
            "bundle_missing",
            "bundle_not_directory",
            "manifest_missing",
            "registry_missing",
            "sig_missing",
        }
        if result.get("ok"):
            return 0
        if any(err in io_errors for err in output["errors"]):
            return 2
        return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
