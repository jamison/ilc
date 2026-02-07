"""
CLI for syncing registry bundles from channel sources.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_sync \
        --channel-file channel.json --key-file key.txt --dest /var/ilc/registry
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_sync import sync_channel_registry


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
        description="Sync registry bundles from channel sources"
    )
    
    parser.add_argument(
        "--channel-file",
        type=str,
        required=True,
        help="Path to channel file"
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
        "--channel",
        type=str,
        default=None,
        help="Channel to sync (default: current_channel)"
    )
    parser.add_argument(
        "--source-index",
        type=int,
        default=0,
        help="Index into sources list (default: 0)"
    )
    parser.add_argument(
        "--allow-network",
        action="store_true",
        help="Allow https:// sources"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Strict registry validation (default)"
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Disable strict registry validation"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing bundle"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without making changes"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temp directory on failure"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Network timeout in seconds (default: 20)"
    )
    parser.add_argument(
        "--no-failover",
        action="store_true",
        help="Disable failover to subsequent sources"
    )
    parser.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Max number of sources to attempt"
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
        output = {"ok": False, "errors": ["key_file_not_found"], "warnings": []}
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    key = _load_key_bytes(key_path)
    
    result = sync_channel_registry(
        channel_file=Path(args.channel_file).resolve(),
        key=key,
        dest_dir=Path(args.dest).resolve(),
        channel=args.channel,
        source_index=args.source_index,
        allow_network=args.allow_network,
        strict=args.strict,
        force=args.force,
        dry_run=args.dry_run,
        keep_temp=args.keep_temp,
        timeout=args.timeout,
        failover=not args.no_failover,
        max_sources=args.max_sources,
    )
    
    output = {
        "ok": result.get("ok", False),
        "errors": result.get("errors", []),
        "warnings": result.get("warnings", []),
    }
    
    # Copy all relevant fields
    for field in ["channel", "source", "source_index", "channel_version",
                  "bundle_hash", "key_id", "installed_path", "dry_run", 
                  "dest", "actions", "attempted_sources", "failed_sources",
                  "successful_source_index", "last_sync",
                  "sources_to_attempt", "failover_enabled"]:
        if field in result:
            output[field] = result[field]
    
    print(json.dumps(output, separators=(",", ":")))
    
    if result.get("ok"):
        return 0
    
    # Determine exit code: validation/policy -> 1, IO/transport -> 2
    validation_errors = {
        "invalid_json",
        "schema_violation",
        "channel_not_found",
        "sources_missing",
        "source_index_out_of_range",
        "max_sources_invalid",
        "network_disabled",
        "dest_exists",
        "bundle_verify_failed",
    }
    io_errors = {
        "file_not_found",
        "file_read_error",
        "file_write_error",
        "source_not_found",
        "source_download_failed",
        "archive_extract_failed",
        "archive_format_unknown",
        "fetch_failed",
        "dest_not_writable",
        "key_file_not_found",
        "channel_update_failed",
    }

    errors = result.get("errors", [])
    has_validation = any(
        any(token in err for token in validation_errors) for err in errors
    )
    has_io = any(any(token in err for token in io_errors) for err in errors)

    if has_validation:
        return 1
    if has_io:
        return 2
    if "sync_failed_all_sources" in errors:
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
