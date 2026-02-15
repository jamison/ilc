from __future__ import annotations

import ast
from pathlib import Path


TARGET_FILES = [
    "ilc_core/protocol/schema.py",
    "ilc_core/protocol/mapper.py",
    "ilc_core/protocol/ilc_cluster_a_replay_proof_batch.py",
    "ilc_core/protocol/ilc_cluster_a_replay_proof_package.py",
    "ilc_core/protocol/ilc_cluster_a_replay_proof_ci_gate.py",
]


def _iter_raise_nodes(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            yield node


def test_no_raw_value_error_raise_in_scoped_modules() -> None:
    violations: list[str] = []

    for rel_path in TARGET_FILES:
        source = Path(rel_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=rel_path)
        for raise_node in _iter_raise_nodes(tree):
            exc = raise_node.exc
            if not isinstance(exc, ast.Call):
                continue
            func = exc.func
            if isinstance(func, ast.Name) and func.id == "ValueError":
                violations.append(f"{rel_path}:{raise_node.lineno}")

    assert not violations, "Raw ValueError raise(s) found in migrated modules: " + ", ".join(violations)
