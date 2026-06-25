# SPDX-License-Identifier: AGPL-3.0-only
"""Write a safe local staging tree from an ILC materialization manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ilc_core.distribution.materialization import (
    DEFAULT_MAX_TOTAL_BYTES,
    FetchSources,
    canonical_json,
    load_json_object,
    materialize_tree,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--tarball", default="")
    parser.add_argument("--http-base-url", default="")
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    manifest = load_json_object(Path(args.manifest))
    result = materialize_tree(
        manifest,
        out_dir=Path(args.out),
        sources=FetchSources(
            cache_dir=Path(args.cache_dir) if args.cache_dir else None,
            repo_root=Path(args.repo_root) if args.repo_root else None,
            tarball=Path(args.tarball) if args.tarball else None,
            http_base_url=str(args.http_base_url or ""),
        ),
        max_total_bytes=int(args.max_total_bytes),
        overwrite=bool(args.overwrite),
    )
    print(canonical_json(result))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI wrapper
    raise SystemExit(main())
