"""
CLI for promoting registry bundles between channels.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_promotion \
        --src /path/to/test --dest /path/to/main \
        --channel-file channel.json --from test --to main --key-file key.txt
"""

import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_promotion import promote_bundle
from ilc_core.cli._key_utils import load_key_bytes_with_b64_fallback


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote registry bundles between channels"
    )
    
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="Source directory containing bundle"
    )
    parser.add_argument(
        "--dest",
        type=str,
        required=True,
        help="Destination directory for promoted bundle"
    )
    parser.add_argument(
        "--channel-file",
        type=str,
        required=True,
        help="Path to channel file"
    )
    parser.add_argument(
        "--from",
        type=str,
        dest="from_channel",
        required=True,
        help="Source channel name"
    )
    parser.add_argument(
        "--to",
        type=str,
        dest="to_channel",
        required=True,
        help="Destination channel name"
    )
    parser.add_argument(
        "--key-file",
        type=str,
        required=True,
        help="Path to verification key file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force promotion (allow same-channel, add missing channel)"
    )
    parser.add_argument(
        "--switch",
        action="store_true",
        help="Update current_channel to destination after promotion"
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
    
    key = load_key_bytes_with_b64_fallback(key_path)
    
    result = promote_bundle(
        src_dir=Path(args.src).resolve(),
        dest_dir=Path(args.dest).resolve(),
        channel_file=Path(args.channel_file).resolve(),
        src_channel=args.from_channel,
        dest_channel=args.to_channel,
        key=key,
        force=args.force,
        dry_run=args.dry_run,
        switch=args.switch,
    )
    
    output = {
        "ok": result.get("ok", False),
        "errors": result.get("errors", []),
        "warnings": result.get("warnings", []),
    }
    if result.get("dry_run"):
        output["dry_run"] = True
    if result.get("actions"):
        output["actions"] = result["actions"]
    if result.get("last_promotion"):
        output["last_promotion"] = result["last_promotion"]
    if "promoted" in result:
        output["promoted"] = result["promoted"]
    if result.get("dest_bundle"):
        output["dest_bundle"] = result["dest_bundle"]
    
    print(json.dumps(output, separators=(",", ":")))
    
    if result.get("ok"):
        return 0
    
    # Determine exit code
    io_errors = {"src_not_readable", "dest_not_writable", "promotion_failed", "channel_update_failed"}
    for err in result.get("errors", []):
        if any(io_err in err for io_err in io_errors):
            return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
