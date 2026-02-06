"""
CLI for validating canon bundle key registry files.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json --strict
    python3 -m ilc_core.cli.canon_bundle_key_registry --registry /path/registry.json --allow-empty
"""

import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry import validate_registry_file, load_registry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a canon bundle key registry file"
    )
    parser.add_argument(
        "--registry",
        type=str,
        required=True,
        help="Path to the registry JSON file"
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
    
    args = parser.parse_args()
    registry_path = Path(args.registry).resolve()
    
    # Handle IO errors
    if not registry_path.exists():
        output = {
            "ok": False,
            "errors": ["file_not_found"],
            "warnings": [],
            "registry_path": str(registry_path),
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    # Determine strict mode
    strict = args.strict and not args.allow_empty
    
    # Validate
    result = validate_registry_file(registry_path, strict=strict)

    # IO error handling: treat as exit code 2
    if any(err in result["errors"] for err in ("file_not_found", "file_read_error")):
        output = {
            "ok": False,
            "errors": result["errors"],
            "warnings": result["warnings"],
            "registry_path": str(registry_path),
        }
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    # If allow-empty, remove empty_current_keys from errors
    if args.allow_empty and "empty_current_keys" in result["errors"]:
        result["errors"].remove("empty_current_keys")
        if "empty_current_keys" not in result["warnings"]:
            result["warnings"].append("empty_current_keys")
        result["ok"] = len(result["errors"]) == 0
    
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
    }
    
    print(json.dumps(output, separators=(",", ":")))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
