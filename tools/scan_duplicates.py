#!/usr/bin/env python3
"""Scan for duplicate definitions and imports in the codebase.

CI-friendly: exits with code 2 when duplicates found, 1 for errors, 0 for clean.

Usage:
    python3 tools/scan_duplicates.py [--root PATH] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Directories to always exclude.
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "dist",
    "build",
    ".tox",
    "node_modules",
    "out",
}

DIRS_TO_SCAN = ["ilc_core", "simulations", "tests"]


@dataclass
class DuplicateFinding:
    """A duplicate finding in a file."""
    filepath: str
    line: int
    kind: str  # "import" or "consecutive"
    content: str
    first_seen_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "filepath": self.filepath,
            "line": self.line,
            "kind": self.kind,
            "content": self.content,
            "first_seen_line": self.first_seen_line,
        }


def _is_import_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("import ") or stripped.startswith("from ")


def scan_file(filepath: Path) -> list[DuplicateFinding]:
    """Scan a single file for duplicate imports and consecutive duplicate lines."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return []

    findings: list[DuplicateFinding] = []
    seen_imports: dict[str, int] = {}

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        lineno = i + 1

        # Check duplicate imports.
        if _is_import_line(line):
            if stripped in seen_imports:
                findings.append(DuplicateFinding(
                    filepath=str(filepath),
                    line=lineno,
                    kind="import",
                    content=stripped,
                    first_seen_line=seen_imports[stripped],
                ))
            else:
                seen_imports[stripped] = lineno

        # Check consecutive duplicate lines.
        if i > 0:
            prev_idx = i - 1
            while prev_idx >= 0 and not lines[prev_idx].strip():
                prev_idx -= 1
            
            if prev_idx >= 0:
                prev_line = lines[prev_idx].strip()
                # Require 20+ chars to avoid short common patterns like "return value".
                if (
                    prev_line == stripped
                    and len(stripped) > 20
                    and not stripped.startswith("#")
                ):
                    findings.append(DuplicateFinding(
                        filepath=str(filepath),
                        line=lineno,
                        kind="consecutive",
                        content=stripped,
                        first_seen_line=prev_idx + 1,
                    ))

    return findings


def _iter_py_files(root: Path) -> list[Path]:
    """Iterate over Python files, excluding common build/cache dirs."""
    files: list[Path] = []
    for d in DIRS_TO_SCAN:
        dir_path = root / d
        if not dir_path.exists():
            continue
        for path in dir_path.rglob("*.py"):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            files.append(path)
    return files


def scan_for_duplicates(root: Path) -> list[DuplicateFinding]:
    """Scan the repository for duplicate definitions.
    
    Returns:
        List of DuplicateFinding objects.
    """
    findings: list[DuplicateFinding] = []
    for path in _iter_py_files(root):
        findings.extend(scan_file(path))
    return findings


def main() -> int:
    """Main entry point. Returns exit code."""
    parser = argparse.ArgumentParser(description="Scan for duplicate definitions")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (default: parent of tools/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output findings as JSON",
    )
    args = parser.parse_args()

    try:
        findings = scan_for_duplicates(args.root)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        if findings:
            # Group by file for readable output.
            by_file: dict[str, list[DuplicateFinding]] = {}
            for f in findings:
                by_file.setdefault(f.filepath, []).append(f)
            
            for filepath, file_findings in sorted(by_file.items()):
                print(f"\nFile: {filepath}")
                for finding in file_findings:
                    if finding.kind == "import":
                        print(f"  Line {finding.line}: Duplicate import '{finding.content}' (first seen at line {finding.first_seen_line})")
                    else:
                        print(f"  Line {finding.line}: Consecutive duplicate line '{finding.content}'")
        else:
            print("No duplicates found.")

    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
