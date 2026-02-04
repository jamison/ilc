import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
    duplicates: dict[str, list[str]] = {}
    for path in _iter_py_files(ROOT):
        source = path.read_text(encoding="utf-8")
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
