#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS inbox reader — list and verify pending sealed envelopes for Genesis Agent.

Envelopes are stored by ccss_relay_server.py as <sha256>.envelope files.
This tool lists pending envelopes, verifies their integrity, and reports
their state. Decryption requires Genesis Agent's private key (not handled here).

Usage:
    python tools/ccss_relay/ccss_inbox_reader.py [--inbox <dir>] [--verify]

Options:
    --inbox DIR   Inbox directory (default: ~/.ccss_inbox/genesis)
    --verify      Re-verify sha256 of each envelope against filename (default: on)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

_DEFAULT_INBOX = Path.home() / ".ccss_inbox" / "genesis"
_OUTER_ENVELOPE_BYTES = 4156


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List pending CCSS sealed envelopes for Genesis Agent."
    )
    parser.add_argument(
        "--inbox",
        type=Path,
        default=_DEFAULT_INBOX,
        metavar="DIR",
        help="Inbox directory (default: ~/.ccss_inbox/genesis)",
    )
    parser.add_argument(
        "--no-verify",
        dest="verify",
        action="store_false",
        default=True,
        help="Skip sha256 re-verification of envelope contents",
    )
    args = parser.parse_args(argv)

    inbox = args.inbox.resolve()

    print(f"CCSS Inbox: {inbox}")

    if not inbox.exists():
        print("  (inbox directory not found — no envelopes received yet)")
        return 0

    envelopes = sorted(inbox.glob("*.envelope"))
    print(f"Pending envelopes: {len(envelopes)}")

    if not envelopes:
        print("  (none)")
        return 0

    print()
    errors = 0
    for path in envelopes:
        size = path.stat().st_size
        size_ok = size == _OUTER_ENVELOPE_BYTES

        if args.verify:
            data = path.read_bytes()
            computed = hashlib.sha256(data).hexdigest()
            integrity = "OK" if computed == path.stem else "MISMATCH"
            if computed != path.stem:
                errors += 1
        else:
            integrity = "skipped"

        size_tag = "OK" if size_ok else f"UNEXPECTED:{size}B"
        if not size_ok:
            errors += 1

        print(f"  {path.stem}")
        print(f"    size: {size}B ({size_tag})")
        print(f"    integrity: {integrity}")
        print()

    if errors:
        print(f"Warnings: {errors} envelope(s) with integrity or size issues.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
