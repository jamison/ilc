"""Test for duplicate top-level definitions in Python files.

Uses the scan_duplicates tool for duplicate import/line detection,
and adds AST-based detection for duplicate top-level class/function names.
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCAN_DUPLICATES_PATH = ROOT / "tools" / "scan_duplicates.py"
_spec = importlib.util.spec_from_file_location("scan_duplicates", _SCAN_DUPLICATES_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load scan_duplicates from {_SCAN_DUPLICATES_PATH}")
_scan_duplicates = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _scan_duplicates
_spec.loader.exec_module(_scan_duplicates)

scan_for_duplicates = _scan_duplicates.scan_for_duplicates
DuplicateFinding = _scan_duplicates.DuplicateFinding

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "out",
}


def _iter_py_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        # Skip generated or cache dirs inside repo
        if path.name.startswith("."):
            continue
        files.append(path)
    return files


def _find_duplicate_top_level_defs(source: str) -> dict[str, int]:
    tree = ast.parse(source)
    counts: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            counts[node.name] = counts.get(node.name, 0) + 1
    return {name: count for name, count in counts.items() if count > 1}


def test_no_duplicate_top_level_definitions() -> None:
    """Check that no file has duplicate top-level function/class names."""
    duplicates: dict[str, list[str]] = {}
    for path in _iter_py_files(ROOT):
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        dups = _find_duplicate_top_level_defs(source)
        if dups:
            duplicates[str(path)] = [f"{name} x{count}" for name, count in dups.items()]

    if duplicates:
        details = "\n".join(
            f"{path}: {', '.join(names)}" for path, names in sorted(duplicates.items())
        )
        raise AssertionError(
            "Duplicate top-level definitions found:\n" + details
        )


def test_no_duplicate_imports_or_lines() -> None:
    """Check for duplicate imports and consecutive duplicate lines using scan_duplicates tool."""
    findings = scan_for_duplicates(ROOT)
    
    if findings:
        # Limit output to avoid huge test logs.
        max_findings = 10
        details = "\n".join(
            f"{f.filepath}:{f.line}: {f.kind} - {f.content}"
            for f in findings[:max_findings]
        )
        if len(findings) > max_findings:
            details += f"\n... and {len(findings) - max_findings} more findings"
        raise AssertionError(
            f"Found {len(findings)} duplicate imports or lines:\n" + details
        )
