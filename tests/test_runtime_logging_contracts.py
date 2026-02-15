from __future__ import annotations

import ast
import re
from pathlib import Path

from fastapi.testclient import TestClient

from ilc_core.server import app
from ilc_core.types import Node


TARGET_FILES = [
    "ilc_core/agent.py",
    "ilc_core/consensus/engine.py",
    "ilc_core/network/peer.py",
    "ilc_core/server.py",
]


def _iter_logger_calls(tree: ast.AST):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        value = node.func.value
        if isinstance(value, ast.Name) and value.id == "logger":
            yield node


def test_scoped_runtime_loggers_do_not_use_f_strings() -> None:
    for rel_path in TARGET_FILES:
        source = Path(rel_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=rel_path)
        for call in _iter_logger_calls(tree):
            if not call.args:
                continue
            first_arg = call.args[0]
            assert not isinstance(first_arg, ast.JoinedStr), (
                f"{rel_path}:{call.lineno}: logger call uses f-string message; "
                "use parameterized logging."
            )


def test_scoped_runtime_loggers_do_not_use_bracket_prefixed_messages() -> None:
    pattern = re.compile(
        r"""logger\.(?:debug|info|warning|error|exception|critical)\(\s*["']\["""
    )
    for rel_path in TARGET_FILES:
        source = Path(rel_path).read_text(encoding="utf-8")
        assert pattern.search(source) is None, (
            f"{rel_path}: bracket-prefixed logger message detected; use tokenized events."
        )


def test_gossip_receive_invalid_payload_contract_stable() -> None:
    client = TestClient(app)

    node = Node(
        id="placeholder",
        type="claim",
        content="runtime_logging_contract_test",
        agent_id="agent:gossip:contract",
        signature="sig:gossip:contract",
        net_stake=1.0,
    )
    node.id = node.compute_id()
    payload = node.model_dump(mode="json")
    payload["id"] = "invalid_hash"

    response = client.post("/gossip/receive", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"
