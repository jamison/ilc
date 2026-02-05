"""Basic code health checks (size thresholds)."""
from __future__ import annotations

import ast
from pathlib import Path

MAX_FUNC_LINES = 150
MAX_CLASS_LINES = 300
MAX_FILE_LINES = 1500
MAX_FUNC_ARGS = 10
MAX_NESTING_DEPTH = 4

ROOT = Path(__file__).resolve().parents[1]
CODE_DIRS = [ROOT / "ilc_core"]
EXCLUDE_FILES = {"__init__.py"}
# Targeted exclusions for legacy hotspots; revisit once refactors land.
EXCLUDE_DIRS = {
    ROOT / "ilc_core" / "analysis",
    ROOT / "ilc_core" / "encoding",
    ROOT / "ilc_core" / "protocol",
    ROOT / "ilc_core" / "consensus",
}
EXCLUDE_PATHS: set[Path] = set()


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for base in CODE_DIRS:
        for path in base.rglob("*.py"):
            if path.name in EXCLUDE_FILES:
                continue
            if any(path.is_relative_to(d) for d in EXCLUDE_DIRS):
                continue
            if path in EXCLUDE_PATHS:
                continue
            files.append(path)
    return files


def iter_functions(tree: ast.AST) -> list[ast.AST]:
    funcs: list[ast.AST] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            funcs.append(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            funcs.append(node)
            self.generic_visit(node)

    Visitor().visit(tree)
    return funcs


def iter_classes(tree: ast.AST) -> list[ast.AST]:
    classes: list[ast.AST] = []

    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            classes.append(node)
            self.generic_visit(node)

    Visitor().visit(tree)
    return classes


def max_nesting_depth(node: ast.AST) -> int:
    max_depth = 0

    def walk(n: ast.AST, depth: int) -> None:
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(n):
            walk(
                child,
                depth
                + (
                    1
                    if isinstance(
                        child,
                        (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncWith),
                    )
                    else 0
                ),
            )

    walk(node, 0)
    return max_depth


def test_file_size_thresholds() -> None:
    failures = []
    for path in iter_python_files():
        try:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
        if line_count > MAX_FILE_LINES:
            failures.append(f"{path}: {line_count} lines (max {MAX_FILE_LINES})")
    if failures:
        raise AssertionError("File size threshold exceeded:\n" + "\n".join(failures))


def test_function_size_thresholds() -> None:
    failures = []
    for path in iter_python_files():
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in iter_functions(tree):
            if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
                continue
            start = node.lineno
            end = node.end_lineno or node.lineno
            length = end - start + 1
            if length > MAX_FUNC_LINES:
                name = getattr(node, "name", "<lambda>")
                failures.append(
                    f"{path}:{start}-{end} {name}() is {length} lines (max {MAX_FUNC_LINES})"
                )
            arg_count = len(node.args.args) + len(node.args.kwonlyargs)
            if node.args.vararg is not None:
                arg_count += 1
            if node.args.kwarg is not None:
                arg_count += 1
            if arg_count > MAX_FUNC_ARGS:
                name = getattr(node, "name", "<lambda>")
                failures.append(
                    f"{path}:{start}-{end} {name}() has {arg_count} args (max {MAX_FUNC_ARGS})"
                )
            depth = max_nesting_depth(node)
            if depth > MAX_NESTING_DEPTH:
                name = getattr(node, "name", "<lambda>")
                failures.append(
                    f"{path}:{start}-{end} {name}() nesting depth {depth} (max {MAX_NESTING_DEPTH})"
                )
    if failures:
        raise AssertionError("Function size threshold exceeded:\n" + "\n".join(failures))


def test_class_size_thresholds() -> None:
    failures = []
    for path in iter_python_files():
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in iter_classes(tree):
            if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
                continue
            start = node.lineno
            end = node.end_lineno or node.lineno
            length = end - start + 1
            if length > MAX_CLASS_LINES:
                name = getattr(node, "name", "<class>")
                failures.append(
                    f"{path}:{start}-{end} class {name} is {length} lines (max {MAX_CLASS_LINES})"
                )
    if failures:
        raise AssertionError("Class size threshold exceeded:\n" + "\n".join(failures))


def test_no_todos_in_prod_code() -> None:
    failures = []
    for path in iter_python_files():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "tests" in path.parts or "docs" in path.parts:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if "TODO" in line or "FIXME" in line:
                failures.append(f"{path}:{i}: {line.strip()}")
    if failures:
        raise AssertionError("TODO/FIXME found in production code:\n" + "\n".join(failures))
