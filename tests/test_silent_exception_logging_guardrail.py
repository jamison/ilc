from __future__ import annotations

import ast
from pathlib import Path

import pytest


TARGET_FILES = [
    "ilc_core/protocol/ilc_cluster_a_replay_proof_ci_gate.py",
    "ilc_core/protocol/ilc_cluster_a_replay_proof_batch_compare.py",
    "ilc_core/protocol/ilc_cluster_a_replay_proof_batch.py",
    "ilc_core/protocol/ilc_cluster_a_replay_proof_package.py",
    "ilc_core/protocol/ilc_cluster_a_ingest.py",
]


def _is_broad_exception(handler: ast.ExceptHandler) -> bool:
    if handler.type is None:
        return True
    if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
        return True
    return False


def _has_logger_call(statements: list[ast.stmt]) -> bool:
    for node in ast.walk(ast.Module(body=statements, type_ignores=[])):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            obj = node.func.value
            if isinstance(obj, ast.Name) and obj.id == "logger":
                return True
    return False


def _has_raise(statements: list[ast.stmt]) -> bool:
    return any(isinstance(node, ast.Raise) for node in ast.walk(ast.Module(body=statements, type_ignores=[])))


@pytest.mark.parametrize("rel_path", TARGET_FILES)
def test_no_silent_exception_handlers(rel_path: str) -> None:
    source = Path(rel_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=rel_path)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if not _is_broad_exception(node):
            continue

        is_pass_only = len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
        assert not is_pass_only, f"{rel_path}:{node.lineno}: broad except handler is pass-only"

        has_logger = _has_logger_call(node.body)
        has_raise = _has_raise(node.body)
        assert has_logger or has_raise, (
            f"{rel_path}:{node.lineno}: broad except handler has no logger call and no raise"
        )


@pytest.mark.parametrize("rel_path", TARGET_FILES)
def test_module_has_logger(rel_path: str) -> None:
    source = Path(rel_path).read_text(encoding="utf-8")
    assert "logger = logging.getLogger(__name__)" in source, (
        f"{rel_path}: missing module-level logger"
    )
