"""
CLI for fetching and verifying canon bundle key registry bundles.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_fetch --source /path/to/bundle --key-file key.txt --dest ./installed
    python3 -m ilc_core.cli.canon_bundle_key_registry_fetch --source file:///path/to/bundle --key-file key.txt --dest ./installed
    python3 -m ilc_core.cli.canon_bundle_key_registry_fetch --source https://example.com/bundle.tar.gz --key-file key.txt --dest ./installed --allow-network
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_fetch import fetch_registry_bundle


def _load_key_bytes(key_path: Path) -> bytes:
    """Load key bytes from file, decoding base64 if applicable."""
    content = key_path.read_bytes().strip()
    try:
        decoded = base64.b64decode(content, validate=True)
        if len(decoded) >= 16:
            return decoded
    except Exception:
        pass
    return content


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch and verify canon bundle key registry bundles"
    )
    
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Source: local path, file:// URL, or https:// URL"
    )
    parser.add_argument(
        "--key-file",
        type=str,
        required=True,
        help="Path to verification key file"
    )
    parser.add_argument(
        "--dest",
        type=str,
        required=True,
        help="Destination directory for installed bundle"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing bundle"
    )
    parser.add_argument(
        "--allow-network",
        action="store_true",
        help="Allow https:// URLs (required for network fetch)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Timeout for network requests in seconds (default: 20)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temp directory on failure (for debugging)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict registry validation (default)"
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Disable strict registry validation"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Force JSON output"
    )
    
    parser.set_defaults(strict=True)
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
    dest_dir = Path(args.dest).resolve()
    
    result = fetch_registry_bundle(
        source=args.source,
        key=key,
        dest_dir=dest_dir,
        force=args.force,
        allow_network=args.allow_network,
        timeout=args.timeout,
        keep_temp=args.keep_temp,
        strict=args.strict,
    )
    
    output = {
        "ok": result.get("ok", False),
        "errors": result.get("errors", []),
        "warnings": result.get("warnings", []),
        "source": args.source,
        "dest": str(dest_dir),
    }
    if result.get("bundle_dir"):
        output["bundle_dir"] = result["bundle_dir"]
    if result.get("installed_to"):
        output["installed_to"] = result["installed_to"]
    if result.get("registry_hash"):
        output["registry_hash"] = result["registry_hash"]
    if result.get("key_id"):
        output["key_id"] = result["key_id"]
    
    print(json.dumps(output, separators=(",", ":")))
    
    if result.get("ok"):
        return 0
    
    # Determine exit code
    io_errors = {
        "source_not_found",
        "source_download_failed",
        "key_file_not_found",
        "network_not_allowed",
    }
    for err in result.get("errors", []):
        if any(io_err in err for io_err in io_errors):
            return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
