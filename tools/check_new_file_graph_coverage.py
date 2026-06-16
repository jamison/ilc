#!/usr/bin/env python3
"""Check new files have graph-intake records.

PUBLIC_RC_EXCLUDE: graph_intake_lint_tool
PUBLIC_RC_EXCLUDE_REASON: Internal repo hygiene checker for candidate graph
intake coverage. It does not mutate graph state, sign nodes, activate runtime,
or authorize public RC.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


COVERED_PREFIXES = (
    "docs/specs/",
    "docs/antigravity_tasks/",
    "ilc_core/",
    "tools/",
    "tests/",
)
DEFAULT_LEDGER = Path("docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json")
DEFAULT_OVERLAY_LEDGER = Path("docs/specs/ilc_fix39_graph_intake_overlay_v0.1.json")
DEFAULT_OVERLAY_GLOB = "ilc_fix*_graph_intake_overlay_v0.1.json"


def _candidate_stub(path: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    return f"graph_intake_{slug[:96]}"


def _is_covered(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in COVERED_PREFIXES)


def _staged_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git_diff_cached_failed:{result.stderr.strip()}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _walk_paths(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"repo_path", "path"} and isinstance(item, str):
                paths.add(item)
            paths.update(_walk_paths(item))
    elif isinstance(value, list):
        for item in value:
            paths.update(_walk_paths(item))
    return paths


def _ledger_paths(path: Path) -> set[str]:
    if not path.exists():
        raise FileNotFoundError(f"graph_intake_ledger_not_found:{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _walk_paths(payload)


def _default_ledgers(repo_root: Path) -> list[Path]:
    ledgers = [repo_root / DEFAULT_LEDGER]
    overlay_dir = repo_root / DEFAULT_OVERLAY_LEDGER.parent
    for overlay in sorted(overlay_dir.glob(DEFAULT_OVERLAY_GLOB)):
        if overlay != repo_root / DEFAULT_LEDGER:
            ledgers.append(overlay)
    return ledgers


def _resolve_ledgers(repo_root: Path, ledgers: list[Path] | None) -> list[Path]:
    if ledgers is None:
        return _default_ledgers(repo_root)
    return [path if path.is_absolute() else repo_root / path for path in ledgers]


def _combined_ledger_paths(ledgers: list[Path]) -> set[str]:
    registered: set[str] = set()
    for ledger in ledgers:
        registered.update(_ledger_paths(ledger))
    return registered


def check_files(
    files: list[str],
    ledgers: list[Path],
) -> tuple[list[str], list[dict[str, str]]]:
    covered = sorted({path.replace("\\", "/") for path in files if _is_covered(path)})
    registered = _combined_ledger_paths(ledgers)
    missing = [
        {"path": path, "suggested_candidate_id": _candidate_stub(path)}
        for path in covered
        if path not in registered
    ]
    return covered, missing


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        action="append",
        default=None,
        help=(
            "Graph-intake ledger to check. May be repeated. If omitted, the "
            "Fix38 manual ledger is loaded and the Fix39 overlay ledger is "
            "loaded when present."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Repo-relative file paths. If omitted, staged git files are checked.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    files = args.files if args.files is not None else _staged_files(repo_root)
    ledgers = _resolve_ledgers(repo_root, args.ledger)

    try:
        covered, missing = check_files(files, ledgers)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (json.JSONDecodeError, RuntimeError) as exc:
        print(f"graph_intake_check_error:{exc}", file=sys.stderr)
        return 2

    payload = {
        "covered_file_count": len(covered),
        "ledgers": [str(ledger) for ledger in ledgers],
        "missing": missing,
        "missing_count": len(missing),
        "status": "pass" if not missing else "fail",
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
    elif missing:
        print("graph_intake_missing_records")
        for item in missing:
            print(f"- {item['path']} -> {item['suggested_candidate_id']}")
    else:
        print("graph_intake_all_covered_files_registered")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
