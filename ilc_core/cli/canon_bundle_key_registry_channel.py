# SPDX-License-Identifier: AGPL-3.0-only
"""
CLI for managing canon bundle key registry channels.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --validate
    python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --list
    python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --set main
    python3 -m ilc_core.cli.canon_bundle_key_registry_channel --file channel.json --set main --create
"""

import argparse
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_channel import (
    validate_channel_file,
    list_channels,
    set_current_channel,
    create_channel_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage canon bundle key registry channels"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to channel file"
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--validate",
        action="store_true",
        help="Validate the channel file"
    )
    mode_group.add_argument(
        "--list",
        action="store_true",
        help="List available channels"
    )
    mode_group.add_argument(
        "--set",
        type=str,
        metavar="CHANNEL",
        help="Set current channel"
    )
    
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create channel file if missing (use with --set)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operation (add missing channel to list)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Force JSON output"
    )
    
    args = parser.parse_args()
    file_path = Path(args.file).resolve()
    
    # Validate mode
    if args.validate:
        result = validate_channel_file(file_path)
        output = {
            "ok": result["ok"],
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "file": str(file_path),
        }
        print(json.dumps(output, separators=(",", ":")))
        
        if not result["ok"]:
            io_errors = {"file_not_found", "file_read_error", "invalid_json"}
            if any(any(io_err in err for io_err in io_errors) for err in result.get("errors", [])):
                return 2
            return 1
        return 0
    
    # List mode
    if args.list:
        result = list_channels(file_path)
        output = {
            "ok": result["ok"],
            "errors": [result.get("error")] if result.get("error") else [],
            "warnings": [],
            "file": str(file_path),
        }
        if result["ok"]:
            output["current_channel"] = result["current_channel"]
            output["channels"] = result["channels"]
        
        print(json.dumps(output, separators=(",", ":")))
        
        if not result["ok"]:
            io_errors = {"file_not_found", "file_read_error", "invalid_json"}
            if any(io_err in result.get("error", "") for io_err in io_errors):
                return 2
            return 1
        return 0
    
    # Set mode
    if args.set:
        # Handle --create
        if args.create and not file_path.exists():
            result = create_channel_file(file_path, args.set)
            output = {
                "ok": result["ok"],
                "errors": [result.get("error")] if result.get("error") else [],
                "warnings": [],
                "file": str(file_path),
                "created": True,
            }
            if result["ok"]:
                output["current_channel"] = result["current_channel"]
            
            print(json.dumps(output, separators=(",", ":")))
            return 0 if result["ok"] else (2 if "file_" in result.get("error", "") else 1)
        
        result = set_current_channel(file_path, args.set, force=args.force)
        output = {
            "ok": result["ok"],
            "errors": [result.get("error")] if result.get("error") else [],
            "warnings": result.get("warnings", []),
            "file": str(file_path),
        }
        if result["ok"]:
            output["current_channel"] = result["current_channel"]
        
        print(json.dumps(output, separators=(",", ":")))
        
        if not result["ok"]:
            io_errors = {"file_not_found", "file_read_error", "invalid_json"}
            if any(io_err in result.get("error", "") for io_err in io_errors):
                return 2
            return 1
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
