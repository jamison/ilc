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

IMPORT_BOUNDARY_INVENTORY_VERSION = "package_boundary_inventory_1250.v0.1"
GAP14_ADAPTER_EXTRACTION_VERSION = "gap14_adapter_extraction_phase_1250.v0.1"
ILC_LOGIC_IMPORT_BOUNDARY_REDUCTION_TOKEN = (
    "ilc_logic_import_boundary_migration_debt_reduced_phase_1250"
)
PHASE_1250_GAP14_ADAPTER_EXTRACTION_COMPLETE_TOKEN = (
    "phase_1250_gap14_adapter_extraction_complete"
)
MAX_IMPORT_INVENTORY_FILES = 5_000
MAX_IMPORT_INVENTORY_FILE_BYTES = 3_000_000
_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ImportBoundarySpec:
    surface_id: str
    root_paths: tuple[str, ...]
    forbidden_import_roots: tuple[str, ...] = ()
    forbidden_module_prefixes: tuple[str, ...] = ()
    anchor_to_repo_root: bool = False


DEFAULT_IMPORT_BOUNDARY_SPECS = {
    "ilc_logic": ImportBoundarySpec(
        surface_id="ilc_logic",
        root_paths=(
            "ilc_core/graph",
            "ilc_core/protocol",
            "ilc_core/epistemic",
            "ilc_core/reputation",
        ),
        anchor_to_repo_root=True,
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
        forbidden_module_prefixes=(
            "ilc_core.cli",
            "ilc_core.network",
            "ilc_core.node",
            "ilc_core.server",
            "ilc_core.sim",
            "ilc_core.storage",
        ),
    ),
    "ilc_cli": ImportBoundarySpec(
        surface_id="ilc_cli",
        root_paths=("ilc_core/cli",),
        anchor_to_repo_root=True,
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
        anchor_to_repo_root=True,
        forbidden_import_roots=(),
    ),
    "ilc_harness_adapters": ImportBoundarySpec(
        surface_id="ilc_harness_adapters",
        root_paths=("ilc_core/rc",),
        anchor_to_repo_root=True,
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
        if "\x00" in root or "\n" in root or "\r" in root:
            raise ValueError("package_boundary_inventory_invalid_root")
        if Path(root).is_absolute() or ".." in Path(root).parts:
            raise ValueError("package_boundary_inventory_root_must_be_repo_relative")
    for import_root in spec.forbidden_import_roots:
        if not isinstance(import_root, str) or not import_root:
            raise ValueError("package_boundary_inventory_invalid_forbidden_import")
    for module_prefix in spec.forbidden_module_prefixes:
        if not isinstance(module_prefix, str) or not module_prefix:
            raise ValueError("package_boundary_inventory_invalid_forbidden_module_prefix")
    if type(spec.anchor_to_repo_root) is not bool:
        raise ValueError("package_boundary_inventory_anchor_to_repo_root_must_be_bool")


def _display_path(path: Path, *, base: Path | None) -> str:
    if base is not None:
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def _iter_python_files(spec: ImportBoundarySpec) -> list[Path]:
    files: list[Path] = []
    base = _REPO_ROOT if spec.anchor_to_repo_root else None
    for root_path in spec.root_paths:
        root = (base / root_path) if base is not None else Path(root_path)
        if not root.exists():
            if spec.anchor_to_repo_root:
                raise ValueError("package_boundary_inventory_root_missing")
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
    if spec.anchor_to_repo_root and not unique:
        raise ValueError("package_boundary_inventory_root_empty")
    return unique


def _module_package_for_path(path: Path) -> tuple[str, ...]:
    if path.name == "__init__.py":
        return path.parent.parts
    return path.parent.parts


def _resolve_import_from_module(path: Path, node: ast.ImportFrom) -> str:
    module_parts = tuple(part for part in (node.module or "").split(".") if part)
    if node.level == 0:
        return ".".join(module_parts)

    package_parts = _module_package_for_path(path)
    if node.level > len(package_parts):
        return ".".join(module_parts)
    base_parts = package_parts[: len(package_parts) - node.level + 1]
    return ".".join((*base_parts, *module_parts))


def _dynamic_import_module(node: ast.Call) -> str | None:
    function = node.func
    if isinstance(function, ast.Attribute):
        is_importlib_call = (
            function.attr == "import_module"
            and isinstance(function.value, ast.Name)
            and function.value.id == "importlib"
        )
    else:
        is_importlib_call = False
    is_named_import_module = isinstance(function, ast.Name) and function.id == "import_module"
    is_dunder_import = isinstance(function, ast.Name) and function.id == "__import__"
    if not is_importlib_call and not is_named_import_module and not is_dunder_import:
        return None
    if not node.args:
        return None
    first_arg = node.args[0]
    if isinstance(first_arg, ast.Constant) and type(first_arg.value) is str and first_arg.value:
        return first_arg.value
    return None


def _import_records(path: Path, *, display_path: str) -> list[dict[str, str]]:
    if path.stat().st_size > MAX_IMPORT_INVENTORY_FILE_BYTES:
        raise ValueError("package_boundary_inventory_file_bytes_limit_exceeded")
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=display_path)
    records: list[dict[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                records.append(
                    {
                        "file": display_path,
                        "import_root": module.split(".")[0],
                        "module": module,
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            module = _resolve_import_from_module(Path(display_path), node)
            if module:
                records.append(
                    {
                        "file": display_path,
                        "import_root": module.split(".")[0],
                        "module": module,
                    }
                )
        elif isinstance(node, ast.Call):
            module = _dynamic_import_module(node)
            if module:
                records.append(
                    {
                        "file": display_path,
                        "import_root": module.split(".")[0],
                        "module": module,
                    }
                )
    return records


def _module_matches_prefix(module: str, prefix: str) -> bool:
    return module == prefix or module.startswith(f"{prefix}.")


def build_import_boundary_inventory(spec: ImportBoundarySpec) -> dict[str, Any]:
    _validate_spec(spec)
    forbidden = set(spec.forbidden_import_roots)
    forbidden_prefixes = set(spec.forbidden_module_prefixes)
    files = _iter_python_files(spec)
    base = _REPO_ROOT if spec.anchor_to_repo_root else None
    imports: list[dict[str, str]] = []
    for path in files:
        imports.extend(_import_records(path, display_path=_display_path(path, base=base)))

    violations: list[dict[str, str]] = []
    for record in imports:
        if record["import_root"] in forbidden:
            violations.append(
                {
                    **record,
                    "matched_rule": record["import_root"],
                    "violation_type": "forbidden_import_root",
                }
            )
        for module_prefix in forbidden_prefixes:
            if _module_matches_prefix(record["module"], module_prefix):
                violations.append(
                    {
                        **record,
                        "matched_rule": module_prefix,
                        "violation_type": "forbidden_module_prefix",
                    }
                )
    return {
        "file_count": len(files),
        "forbidden_import_roots": sorted(forbidden),
        "forbidden_module_prefixes": sorted(forbidden_prefixes),
        "import_roots": sorted({record["import_root"] for record in imports}),
        "max_files": MAX_IMPORT_INVENTORY_FILES,
        "max_file_bytes": MAX_IMPORT_INVENTORY_FILE_BYTES,
        "root_paths": list(spec.root_paths),
        "status": "pass" if not violations else "violations_present",
        "surface_id": spec.surface_id,
        "version": IMPORT_BOUNDARY_INVENTORY_VERSION,
        "violations": sorted(
            violations,
            key=lambda record: (
                record["file"],
                record["import_root"],
                record["matched_rule"],
                record["module"],
                record["violation_type"],
            ),
        ),
    }


def validate_import_boundary(spec: ImportBoundarySpec) -> dict[str, Any]:
    inventory = build_import_boundary_inventory(spec)
    if inventory["status"] != "pass":
        raise ValueError("package_boundary_inventory_forbidden_imports_present")
    return inventory


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
    "GAP14_ADAPTER_EXTRACTION_VERSION",
    "ILC_LOGIC_IMPORT_BOUNDARY_REDUCTION_TOKEN",
    "IMPORT_BOUNDARY_INVENTORY_VERSION",
    "ImportBoundarySpec",
    "PHASE_1250_GAP14_ADAPTER_EXTRACTION_COMPLETE_TOKEN",
    "build_default_import_boundary_inventory",
    "build_import_boundary_inventory",
    "export_import_boundary_inventory_json",
    "validate_import_boundary",
]
