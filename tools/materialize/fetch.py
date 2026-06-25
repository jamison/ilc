# SPDX-License-Identifier: AGPL-3.0-only
"""Fetch one ILC materialization file entry and verify its SHA-256."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

from ilc_core.distribution.materialization import (
    DEFAULT_MAX_TOTAL_BYTES,
    FetchSources,
    fetch_file_bytes,
)


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--size-bytes", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--tarball", default="")
    parser.add_argument("--http-base-url", default="")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    args = parser.parse_args()
    data = fetch_file_bytes(
        {
            "source_path": args.source_path,
            "source_sha256": args.source_sha256,
            "size_bytes": int(args.size_bytes),
        },
        sources=FetchSources(
            cache_dir=Path(args.cache_dir) if args.cache_dir else None,
            repo_root=Path(args.repo_root) if args.repo_root else None,
            tarball=Path(args.tarball) if args.tarball else None,
            http_base_url=str(args.http_base_url or ""),
        ),
        max_file_bytes=int(args.max_file_bytes),
    )
    _write_bytes_atomic(Path(args.out), data)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI wrapper
    raise SystemExit(main())
