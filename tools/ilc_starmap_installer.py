#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Command wrapper for the local StarMap Installer Sidecar MVP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ilc_core.sidecars.starmap_installer import (
    StarMapInstallerError,
    build_install_receipt,
    load_manifest_payload,
    materialize_starmap_manifest,
    verify_starmap_manifest,
)


def _print(payload: object) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ilc-starmap-installer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("manifest", type=Path)

    materialize_parser = subparsers.add_parser("materialize")
    materialize_parser.add_argument("manifest", type=Path)
    materialize_parser.add_argument("--target", type=Path)
    materialize_parser.add_argument("--dry-run", action="store_true")

    receipt_parser = subparsers.add_parser("receipt")
    receipt_parser.add_argument("manifest", type=Path)

    args = parser.parse_args(argv)
    try:
        payload = load_manifest_payload(args.manifest)
        if args.command == "verify":
            _print(verify_starmap_manifest(payload))
        elif args.command == "materialize":
            _print(
                materialize_starmap_manifest(
                    payload,
                    target=args.target,
                    dry_run=args.dry_run,
                )
            )
        elif args.command == "receipt":
            _print(build_install_receipt(payload))
        else:  # pragma: no cover - argparse enforces command choices.
            raise StarMapInstallerError("starmap_unknown_command")
    except StarMapInstallerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
