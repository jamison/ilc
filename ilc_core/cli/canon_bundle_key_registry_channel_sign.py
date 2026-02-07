"""
CLI for signing registry channel files.

Usage:
    python3 -m ilc_core.cli.canon_bundle_key_registry_channel_sign \
        --channel-file channel.json --key-file key.txt
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_channel_signing import sign_channel_file


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
        description="Sign registry channel file creating detached signature"
    )
    
    parser.add_argument(
        "--channel-file",
        type=str,
        required=True,
        help="Path to channel file to sign"
    )
    parser.add_argument(
        "--key-file",
        type=str,
        required=True,
        help="Path to signing key file"
    )
    parser.add_argument(
        "--sig-file",
        type=str,
        default=None,
        help="Output path for signature (default: <channel>.sig)"
    )
    
    args = parser.parse_args()
    
    # Load key
    key_path = Path(args.key_file)
    if not key_path.exists():
        output = {"ok": False, "errors": ["key_file_not_found"], "warnings": []}
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    try:
        key = _load_key_bytes(key_path)
    except Exception as e:
        output = {"ok": False, "errors": [f"key_read_failed:{e}"], "warnings": []}
        print(json.dumps(output, separators=(",", ":")))
        return 2
    
    channel_path = Path(args.channel_file)
    sig_path = Path(args.sig_file) if args.sig_file else None
    
    result = sign_channel_file(
        channel_path=channel_path,
        key=key,
        sig_path=sig_path,
    )
    
    print(json.dumps(result, separators=(",", ":")))
    
    if result.get("ok"):
        return 0
    
    # IO vs Validation errors
    io_errors = {"channel_read_error", "channel_signature_write_error"}
    for err in result.get("errors", []):
        if any(io_e in err for io_e in io_errors):
            return 2
            
    return 1


if __name__ == "__main__":
    sys.exit(main())
