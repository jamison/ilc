from __future__ import annotations

import ast
from pathlib import Path

from ilc_core.cli import _cli_error


def test_shared_cli_error_module_exports_expected_symbols() -> None:
    assert hasattr(_cli_error, "emit_cli_error")
    assert hasattr(_cli_error, "build_cli_error_payload")
    assert hasattr(_cli_error, "CliErrorPayload")
    assert hasattr(_cli_error, "EXIT_ERROR")


def test_build_cli_error_payload_shape() -> None:
    payload = _cli_error.build_cli_error_payload("test_error", file="test.json")
    assert payload == {"ok": False, "error": "test_error", "file": "test.json"}


def test_replay_proof_cli_imports_shared_error_module() -> None:
    replay_cli_path = Path("ilc_core/cli/canon_cluster_a_replay_proof.py")
    tree = ast.parse(replay_cli_path.read_text(encoding="utf-8"))

    has_shared_import = False
    has_local_emit_definition = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "ilc_core.cli._cli_error":
            imported = {alias.name for alias in node.names}
            if "emit_cli_error" in imported:
                has_shared_import = True
        if isinstance(node, ast.FunctionDef) and node.name == "_emit_cli_error":
            has_local_emit_definition = True

    assert has_shared_import
    assert not has_local_emit_definition
