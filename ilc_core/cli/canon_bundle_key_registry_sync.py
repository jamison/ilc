"""
CLI for syncing registry bundles from channel sources.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_sync \
        --channel-file channel.json --key-file key.txt --dest /var/ilc/registry
"""

import argparse
import json
import os
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_sync import sync_channel_registry, SyncContext
from ilc_core.cli._key_utils import load_key_bytes_with_b64_fallback


def resolve_require_signed_channel(args) -> bool:
    """Resolve signature requirement from CLI flags and environment."""
    if args.require_signed_channel:
        return True
    if args.no_require_signed_channel:
        return False
    
    env = os.environ.get("ILC_REQUIRE_SIGNED_CHANNEL")
    if env is not None:
        if env.lower() in ("1", "true", "yes"):
            return True
        if env.lower() in ("0", "false", "no"):
            return False
            
    return False


def _setup_parser() -> argparse.ArgumentParser:
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
        "--channel-key-file",
        type=str,
        default=None,
        help="Path to channel signature verification key"
    )
    parser.add_argument(
        "--channel-sig-file",
        type=str,
        default=None,
        help="Path to detached channel signature"
    )
    parser.add_argument(
        "--require-signed-channel",
        action="store_true",
        help="Enforce valid channel signature"
    )
    parser.add_argument(
        "--no-require-signed-channel",
        action="store_true",
        help="Do not enforce channel signature (overrides env)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Force JSON output"
    )
    parser.add_argument(
        "--allow-channel-rollback",
        action="store_true",
        help="Allow regression to older channel sequence (requires --force in prod)"
    )
    parser.add_argument(
        "--sync-state-file",
        type=str,
        default=None,
        help="Path to local sync state file (default: <channel-file>.sync_state.json)"
    )
    parser.add_argument(
        "--allow-legacy-channel-v03",
        action="store_true",
        help="Allow v0.3 channel files in compatibility mode (non-prod default path)."
    )
    parser.add_argument(
        "--allow-legacy-channel-v02-v01",
        action="store_true",
        help="Allow v0.2/v0.1 channel files in break-glass mode (non-prod only)."
    )
    parser.add_argument(
        "--non-prod",
        action="store_true",
        help="Run in non-production mode (relax version policy decision matrix)."
    )
    return parser


def main() -> int:
    parser = _setup_parser()
    args = parser.parse_args()
    
    if args.require_signed_channel and args.no_require_signed_channel:
        print(json.dumps({
            "ok": False,
            "errors": ["conflicting_arguments:require_signed_channel"],
            "warnings": []
        }, separators=(",", ":")))
        return 1

    # Load keys
    registry_key_path = Path(args.key_file)
    if not registry_key_path.exists():
        output = {"ok": False, "errors": ["key_file_not_found"], "warnings": []}
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    registry_key = load_key_bytes_with_b64_fallback(registry_key_path)
    
    channel_key = None
    if args.channel_key_file:
        c_key_path = Path(args.channel_key_file)
        if not c_key_path.exists():
            output = {"ok": False, "errors": ["channel_key_file_not_found"], "warnings": []}
            print(json.dumps(output, separators=(",", ":")))
            return 2
        channel_key = load_key_bytes_with_b64_fallback(c_key_path)
    
    # Resolve policy
    require_signed = resolve_require_signed_channel(args)
    
    # Resolve sig path from args or env
    channel_sig_path = None
    if args.channel_sig_file:
        channel_sig_path = Path(args.channel_sig_file)
    elif os.environ.get("ILC_CHANNEL_SIG_PATH"):
        channel_sig_path = Path(os.environ["ILC_CHANNEL_SIG_PATH"])
    
    ctx = SyncContext(
        channel_file=Path(args.channel_file).resolve(),
        key=registry_key,
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
        channel_key=channel_key,
        channel_sig_path=channel_sig_path,
        require_signed_channel=require_signed,
        allow_channel_rollback=args.allow_channel_rollback,
        sync_state_file=Path(args.sync_state_file).resolve() if args.sync_state_file else None,
        prod=not args.non_prod,
        allow_legacy_channel_v03=args.allow_legacy_channel_v03,
        allow_legacy_channel_v02_v01=args.allow_legacy_channel_v02_v01,
    )
    
    result = sync_channel_registry(ctx)
    
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
                  "sources_to_attempt", "failover_enabled",
                  "seen_seq", "seen_hash", "channel_seq", "channel_hash",
                  "freshness_decision", "rollback_override", "rollback_check_applied"]:
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
        # Channel signing errors
        "channel_signature_missing",
        "channel_signature_invalid",
        "channel_signature_mismatch",
        "channel_signature_key_unknown",
        "channel_signature_unsupported_sig_alg",
        "channel_signature_invalid_signed_at",
        "channel_signature_missing_field",
        "channel_key_missing_for_required_signature",
        "channel_rollback_detected",
        "channel_seq_hash_conflict",
        "rollback_override_requires_force_in_prod",
        "context_violation",
        "value_violation",
    }
    io_errors = {
        "file_not_found",
        "file_read_error",
        "file_write_error",
        "channel_read_error",
        "source_not_found",
        "source_download_failed",
        "archive_extract_failed",
        "archive_format_unknown",
        "fetch_failed",
        "dest_not_writable",
        "key_file_not_found",
        "key_read_failed",
        "channel_update_failed",
        "channel_key_file_not_found",
        "channel_signature_read_error",
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
