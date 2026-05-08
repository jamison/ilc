"""Package import-boundary inventory for public-RC profile work.

This module is an inventory tool, not a package splitter. It gives Window
1241-1248 phases a deterministic way to measure which candidate package
surfaces still import server, storage, CLI, or transport dependencies.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

IMPORT_BOUNDARY_INVENTORY_VERSION = "package_boundary_inventory_1243.v0.1"
MAX_IMPORT_INVENTORY_FILES = 5_000


@dataclass(frozen=True)
class ImportBoundarySpec:
    surface_id: str
    root_paths: tuple[str, ...]
    forbidden_import_roots: tuple[str, ...]


DEFAULT_IMPORT_BOUNDARY_SPECS = {
    "ilc_logic": ImportBoundarySpec(
        surface_id="ilc_logic",
        root_paths=(
            "ilc_core/graph",
            "ilc_core/protocol",
            "ilc_core/epistemic",
            "ilc_core/reputation",
        ),
        forbidden_import_roots=(
            "aiohttp",
            "argparse",
            "fastapi",
            "http",
            "lmdb",
            "requests",
            "socket",
            "urllib",
            "uvicorn",
        ),
    ),
    "ilc_cli": ImportBoundarySpec(
        surface_id="ilc_cli",
        root_paths=("ilc_core/cli",),
        forbidden_import_roots=(
            "aiohttp",
            "fastapi",
            "lmdb",
            "uvicorn",
        ),
    ),
    "ilc_node_runtime": ImportBoundarySpec(
        surface_id="ilc_node_runtime",
        root_paths=(
            "ilc_core/network",
            "ilc_core/node",
            "ilc_core/storage",
        ),
        forbidden_import_roots=(),
    ),
    "ilc_harness_adapters": ImportBoundarySpec(
        surface_id="ilc_harness_adapters",
        root_paths=("ilc_core/rc",),
        forbidden_import_roots=(
            "aiohttp",
            "fastapi",
            "http",
            "requests",
            "socket",
            "urllib",
            "uvicorn",
        ),
    ),
}


def _validate_spec(spec: ImportBoundarySpec) -> None:
    if not spec.surface_id or not isinstance(spec.surface_id, str):
        raise ValueError("package_boundary_inventory_invalid_surface_id")
    if not spec.root_paths or not isinstance(spec.root_paths, tuple):
        raise ValueError("package_boundary_inventory_invalid_roots")
    for root in spec.root_paths:
        if not isinstance(root, str) or not root:
            raise ValueError("package_boundary_inventory_invalid_root")
        if Path(root).is_absolute() or ".." in Path(root).parts:
            raise ValueError("package_boundary_inventory_root_must_be_repo_relative")
    for import_root in spec.forbidden_import_roots:
        if not isinstance(import_root, str) or not import_root:
            raise ValueError("package_boundary_inventory_invalid_forbidden_import")


def _iter_python_files(root_paths: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for root_path in root_paths:
        root = Path(root_path)
        if not root.exists():
            continue
        if root.is_file() and root.suffix == ".py":
            files.append(root)
            continue
        if root.is_dir():
            files.extend(
                path
                for path in root.rglob("*.py")
                if "__pycache__" not in path.parts
            )
    unique = sorted(set(files), key=lambda path: path.as_posix())
    if len(unique) > MAX_IMPORT_INVENTORY_FILES:
        raise ValueError("package_boundary_inventory_file_limit_exceeded")
    return unique


def _import_records(path: Path) -> list[dict[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    records: list[dict[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                records.append(
                    {
                        "file": path.as_posix(),
                        "import_root": module.split(".")[0],
                        "module": module,
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                records.append(
                    {
                        "file": path.as_posix(),
                        "import_root": module.split(".")[0],
                        "module": module,
                    }
                )
    return records


def build_import_boundary_inventory(spec: ImportBoundarySpec) -> dict[str, Any]:
    _validate_spec(spec)
    forbidden = set(spec.forbidden_import_roots)
    files = _iter_python_files(spec.root_paths)
    imports: list[dict[str, str]] = []
    for path in files:
        imports.extend(_import_records(path))

    violations = [
        record
        for record in imports
        if record["import_root"] in forbidden
    ]
    return {
        "file_count": len(files),
        "forbidden_import_roots": sorted(forbidden),
        "import_roots": sorted({record["import_root"] for record in imports}),
        "max_files": MAX_IMPORT_INVENTORY_FILES,
        "root_paths": list(spec.root_paths),
        "status": "pass" if not violations else "violations_present",
        "surface_id": spec.surface_id,
        "version": IMPORT_BOUNDARY_INVENTORY_VERSION,
        "violations": sorted(
            violations,
            key=lambda record: (
                record["file"],
                record["import_root"],
                record["module"],
            ),
        ),
    }


def build_default_import_boundary_inventory() -> dict[str, Any]:
    return {
        "surfaces": {
            surface_id: build_import_boundary_inventory(spec)
            for surface_id, spec in sorted(DEFAULT_IMPORT_BOUNDARY_SPECS.items())
        },
        "version": IMPORT_BOUNDARY_INVENTORY_VERSION,
    }


def export_import_boundary_inventory_json(inventory: dict[str, Any] | None = None) -> str:
    active = build_default_import_boundary_inventory() if inventory is None else inventory
    return json.dumps(
        active,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


__all__ = [
    "DEFAULT_IMPORT_BOUNDARY_SPECS",
    "IMPORT_BOUNDARY_INVENTORY_VERSION",
    "ImportBoundarySpec",
    "build_default_import_boundary_inventory",
    "build_import_boundary_inventory",
    "export_import_boundary_inventory_json",
]
