from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [ROOT / "ilc_core", ROOT / "tests"]

# After phase 976, no concrete `Edge` symbol usage is allowed in ilc_core/tests.
EDGE_USAGE_ALLOWLIST: set[str] = set()

# After phase 977, direct edge-list append compatibility is fully removed.
DIRECT_EDGE_APPEND_ALLOWLIST: set[str] = set()

DIRECT_APPEND_PATTERN = re.compile(r"\.edges\.append\(")


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for base in TARGET_DIRS:
        files.extend(sorted(base.rglob("*.py")))
    return files


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _line_at(lines: list[str], lineno: int) -> str:
    if lineno <= 0 or lineno > len(lines):
        return ""
    return lines[lineno - 1].strip()


def _edge_symbol_findings(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text, filename=str(path))
    findings: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == "Edge" for alias in node.names):
                findings.append((node.lineno, _line_at(lines, node.lineno)))
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "Edge":
                findings.append((node.lineno, _line_at(lines, node.lineno)))
            elif isinstance(func, ast.Attribute) and func.attr == "Edge":
                findings.append((node.lineno, _line_at(lines, node.lineno)))

    return sorted(set(findings))


def test_no_new_direct_edge_append_outside_allowlist() -> None:
    offenders: list[str] = []
    for path in _iter_python_files():
        rel = _rel(path)
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if DIRECT_APPEND_PATTERN.search(line) and rel not in DIRECT_EDGE_APPEND_ALLOWLIST:
                offenders.append(f"{rel}:{idx}: {line.strip()}")

    if offenders:
        raise AssertionError(
            "Track 1 phase-1 freeze violation: direct .edges.append usage detected after sunset:\n"
            + "\n".join(offenders)
        )


def test_no_new_edge_symbol_spread_outside_allowlist() -> None:
    offenders: list[str] = []
    for path in _iter_python_files():
        rel = _rel(path)
        findings = _edge_symbol_findings(path)
        if not findings:
            continue
        if rel not in EDGE_USAGE_ALLOWLIST:
            for lineno, line in findings:
                offenders.append(f"{rel}:{lineno}: {line}")

    if offenders:
        raise AssertionError(
            "Track 1 phase-1 freeze violation: Edge symbol usage detected after eviction:\n"
            + "\n".join(offenders)
        )
