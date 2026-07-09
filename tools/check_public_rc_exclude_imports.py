#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""AST scanner for PUBLIC_RC_EXCLUDE import closure.

Phase 1573al packaging gate: a non-excluded ilc_core module must not import an
excluded ilc_core module at module scope. Lazy imports are reported so release
review can pin deliberate local-only command paths, but they do not fail this
gate.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SCANNER_VERSION = "public_rc_exclude_import_scanner_1573al.v0.1"
PUBLIC_RC_EXCLUDE_IMPORT_CLOSURE_TOKEN = (
    "public_rc_exclude_import_closure_clean_phase_1573al"
)
_EXCLUDE_MARKER = "PUBLIC_RC_EXCLUDE:"
_MAX_FILE_BYTES = 3_000_000


@dataclass(frozen=True)
class ImportViolation:
    importer: str
    imported_module: str
    imported_path: str
    lineno: int
    col_offset: int
    severity: str
    import_kind: str
    disposition_required: bool


def _repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _is_excluded(path: Path) -> bool:
    header = "".join(path.read_text(encoding="utf-8", errors="ignore").splitlines(True)[:10])
    return _EXCLUDE_MARKER in header


def _module_for_path(path: Path, repo_root: Path) -> str:
    rel = path.resolve().relative_to(repo_root.resolve())
    parts = rel.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _path_for_module(module: str, module_to_path: dict[str, Path]) -> Path | None:
    if module in module_to_path:
        return module_to_path[module]
    return None


def _package_for_path(path: Path, repo_root: Path) -> tuple[str, ...]:
    rel = path.resolve().relative_to(repo_root.resolve()).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        return parts[:-1]
    return parts[:-1]


def _resolve_import_from(path: Path, repo_root: Path, node: ast.ImportFrom) -> str:
    module_parts = tuple(part for part in (node.module or "").split(".") if part)
    if node.level == 0:
        return ".".join(module_parts)
    package_parts = _package_for_path(path, repo_root)
    if node.level > len(package_parts):
        return ".".join(module_parts)
    base_parts = package_parts[: len(package_parts) - node.level + 1]
    return ".".join((*base_parts, *module_parts))


def _is_lazy(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> bool:
    current = parents.get(node)
    while current is not None:
        if isinstance(
            current,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.Lambda,
                ast.ClassDef,
                ast.Try,
                ast.TryStar,
            ),
        ):
            return True
        current = parents.get(current)
    return False


def _module_candidates_for_import(
    path: Path,
    repo_root: Path,
    node: ast.AST,
) -> list[tuple[str, str]]:
    if isinstance(node, ast.Import):
        return [(alias.name, "import") for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        base = _resolve_import_from(path, repo_root, node)
        candidates: list[tuple[str, str]] = []
        if base:
            candidates.append((base, "from"))
        for alias in node.names:
            if alias.name == "*":
                continue
            candidate = f"{base}.{alias.name}" if base else alias.name
            candidates.append((candidate, "from-name"))
        return candidates
    return []


def _collect_modules(root: Path, repo_root: Path) -> tuple[dict[str, Path], set[Path]]:
    module_to_path: dict[str, Path] = {}
    excluded_paths: set[Path] = set()
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if path.stat().st_size > _MAX_FILE_BYTES:
            raise ValueError(f"public_rc_exclude_scanner_file_too_large:{path}")
        module_to_path[_module_for_path(path, repo_root)] = path
        if _is_excluded(path):
            excluded_paths.add(path.resolve())
    return module_to_path, excluded_paths


def scan_import_closure(root: Path | str = "ilc_core") -> dict[str, object]:
    repo_root = Path.cwd()
    scan_root = (repo_root / root).resolve()
    module_to_path, excluded_paths = _collect_modules(scan_root, repo_root)
    violations: list[ImportViolation] = []

    for path in sorted(scan_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if path.resolve() in excluded_paths:
            continue
        display_path = _repo_relative(path, repo_root)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=display_path)
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        seen_for_node: set[tuple[int, str]] = set()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            for module, import_kind in _module_candidates_for_import(path, repo_root, node):
                imported_path = _path_for_module(module, module_to_path)
                if imported_path is None or imported_path.resolve() not in excluded_paths:
                    continue
                key = (id(node), _repo_relative(imported_path, repo_root))
                if key in seen_for_node:
                    continue
                seen_for_node.add(key)
                severity = "lazy" if _is_lazy(node, parents) else "top_level"
                violations.append(
                    ImportViolation(
                        importer=display_path,
                        imported_module=module,
                        imported_path=_repo_relative(imported_path, repo_root),
                        lineno=getattr(node, "lineno", 0),
                        col_offset=getattr(node, "col_offset", 0),
                        severity=severity,
                        import_kind=import_kind,
                        disposition_required=severity == "top_level",
                    )
                )

    top_level = [violation for violation in violations if violation.severity == "top_level"]
    lazy = [violation for violation in violations if violation.severity == "lazy"]
    return {
        "ok": not top_level,
        "scanner_version": SCANNER_VERSION,
        "token": PUBLIC_RC_EXCLUDE_IMPORT_CLOSURE_TOKEN if not top_level else "",
        "excluded_file_count": len(excluded_paths),
        "top_level_violation_count": len(top_level),
        "lazy_violation_count": len(lazy),
        "violations": [asdict(violation) for violation in violations],
    }


def _emit_text(result: dict[str, object]) -> None:
    print(f"scanner_version={result['scanner_version']}")
    print(f"excluded_file_count={result['excluded_file_count']}")
    print(f"top_level_violation_count={result['top_level_violation_count']}")
    print(f"lazy_violation_count={result['lazy_violation_count']}")
    for row in result["violations"]:
        assert isinstance(row, dict)
        print(
            "{severity}\t{importer}:{lineno}:{col_offset}\t{imported_module}\t{imported_path}".format(
                **row
            )
        )
    if result["ok"]:
        print(PUBLIC_RC_EXCLUDE_IMPORT_CLOSURE_TOKEN)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default="ilc_core")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    result = scan_import_closure(args.root)
    if args.as_json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        _emit_text(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
