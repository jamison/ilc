"""Phase 435 runtime-tranche peer fanout integration tests."""

from __future__ import annotations

import ast
import logging
import subprocess
import sys
import types
from pathlib import Path

import ilc_core.network.peer as peer_runtime
import requests

from ilc_core.network.peer import PeerManager
from ilc_core.node.node_dissemination_runtime_362 import (
    canonical_node_dissemination_vectors,
    generate_node_dissemination_record,
    verify_node_dissemination_record,
)

SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_434_440_sequence_lock_v0.1.md")
HANDOFF_PATH = Path("docs/specs/ilc_runtime_tranche_peer_fanout_handoff_435_v0.1.md")
PEER_PATH = Path("ilc_core/network/peer.py")
CLI_PATH = Path("ilc_core/cli/main.py")
NODE_RUNTIME_PATH = Path("ilc_core/node/node_dissemination_runtime_362.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_435_COMMIT_SUBJECT = "runtime(g8): phase 435 peer fanout integration and hotspot cleanup"
MAX_FUNC_LINES = 150
MAX_NESTING_DEPTH = 4


class _Response:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.ok = 200 <= status_code < 300


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_435_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(PEER_PATH),
        str(CLI_PATH),
        str(NODE_RUNTIME_PATH),
        "tests/test_phase_435_runtime_tranche_peer_fanout_integration.py",
        str(HANDOFF_PATH),
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_435_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_435_commit_subject_present_but_no_qualifying_runtime_commit")
    raise AssertionError("phase_435_commit_not_present_in_local_history")


def _assert_phase_435_runtime_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    required_paths = {
        str(PEER_PATH),
        str(CLI_PATH),
        str(NODE_RUNTIME_PATH),
        "tests/test_phase_435_runtime_tranche_peer_fanout_integration.py",
        str(HANDOFF_PATH),
    }
    assert changed_paths == required_paths, f"phase_435_runtime_scope_mismatch:{sorted(changed_paths)}"
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert "tools/runtime_baseline.py" not in changed_paths


def _max_nesting_depth(node: ast.AST) -> int:
    max_depth = 0

    def _walk(current: ast.AST, depth: int) -> None:
        nonlocal max_depth
        if isinstance(
            current,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.Try,
                ast.With,
                ast.AsyncFor,
                ast.AsyncWith,
                ast.Match,
            ),
        ):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(current):
            _walk(child, depth)

    _walk(node, 0)
    return max_depth


def _function_node(path: Path, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"function_not_found:{path}:{name}")


def test_peer_broadcast_returns_zero_result_with_no_peers() -> None:
    manager = PeerManager(local_port=8000)
    result = manager.broadcast("/gossip/receive", {"id": "claim-0"})
    assert result == {
        "attempted": 0,
        "succeeded": 0,
        "failed": 0,
        "targets": [],
    }


def test_peer_broadcast_records_success_and_failure_logs(monkeypatch, caplog) -> None:
    monkeypatch.setattr(peer_runtime.random, "sample", lambda population, k: sorted(population)[:k])
    caplog.set_level(logging.INFO)

    manager = PeerManager(
        local_port=8000,
        fanout_limit=2,
        sender=lambda url, payload, timeout_s: _Response(202 if url.endswith("8100/gossip/receive") else 503),
    )
    manager.add_peer("10.0.0.1", 8100)
    manager.add_peer("10.0.0.2", 8101)

    result = manager.broadcast("/gossip/receive", {"id": "claim-1"})
    assert result["attempted"] == 2
    assert result["succeeded"] == 1
    assert result["failed"] == 1
    assert result["targets"] == ["10.0.0.1:8100", "10.0.0.2:8101"]

    messages = [record.getMessage() for record in caplog.records]
    assert any("network_gossip_delivery_succeeded" in message for message in messages)
    assert any("network_gossip_delivery_failed" in message for message in messages)


def test_peer_broadcast_normalizes_paths_and_keeps_http_boundary_local(monkeypatch, caplog) -> None:
    observed: list[tuple[str, float]] = []

    def _raising_sender(url: str, payload: dict[str, object], timeout_s: float) -> _Response:
        observed.append((url, timeout_s))
        raise requests.RequestException("boom")

    monkeypatch.setattr(peer_runtime.random, "sample", lambda population, k: sorted(population)[:k])
    caplog.set_level(logging.INFO)

    manager = PeerManager(local_port=8000, sender=_raising_sender)
    manager.add_peer("10.0.0.3", 8102)
    result = manager.broadcast("gossip/receive", {"id": "claim-2"})

    assert result == {
        "attempted": 1,
        "succeeded": 0,
        "failed": 1,
        "targets": ["10.0.0.3:8102"],
    }
    assert observed == [("http://10.0.0.3:8102/gossip/receive", 1.0)]
    assert any("network_gossip_delivery_failed" in record.getMessage() for record in caplog.records)

    text = PEER_PATH.read_text(encoding="utf-8")
    assert "def _default_sender" in text
    assert text.count("requests.post") == 1
    assert "self._sender" in text


def test_cli_refactor_preserves_exemption_set_and_node_payload_shape(monkeypatch) -> None:
    import ilc_core.cli.main as cli_main

    text = CLI_PATH.read_text(encoding="utf-8")
    assert 'if command not in {"query", "verify", "bundle", "agent", "node"}:' in text

    fake_module = types.ModuleType("ilc_core.cli.d2e_lifecycle_cli")
    fake_module.run_node_command = lambda args: {"status": "ok", "subcommand": "constants"}
    monkeypatch.setitem(sys.modules, "ilc_core.cli.d2e_lifecycle_cli", fake_module)
    monkeypatch.setattr(
        cli_main,
        "_ensure_local_graph_state",
        lambda graph_state_path, command: (_ for _ in ()).throw(AssertionError("ensure_local_graph_state_called")),
    )

    payload = cli_main._run_top_level_command("node", types.SimpleNamespace(), Path(".ilc_test.json"))
    assert payload["command"] == "node"
    assert payload["ok"] is True
    assert payload["data"] == {"status": "ok", "subcommand": "constants"}

    code, error_payload = cli_main._value_error_result("node", ValueError("boom"))
    assert code == 1
    assert error_payload["command"] == "node"
    assert error_payload["ok"] is False
    assert error_payload["message"] == "boom"


def test_code_health_hotspots_resolved_and_node_dissemination_vectors_still_validate() -> None:
    main_node = _function_node(CLI_PATH, "main")
    assert _max_nesting_depth(main_node) <= MAX_NESTING_DEPTH

    verify_node = _function_node(NODE_RUNTIME_PATH, "verify_node_dissemination_record")
    length = (verify_node.end_lineno or verify_node.lineno) - verify_node.lineno + 1
    assert length <= MAX_FUNC_LINES

    for vector in canonical_node_dissemination_vectors():
        record = generate_node_dissemination_record(vector)
        verified = verify_node_dissemination_record(record)
        assert verified["valid"] is True


def test_runtime_handoff_exists_with_required_contract_tokens() -> None:
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Phase 435 runtime scope summary",
        "## 2. Imported runtime surfaces",
        "## 3. Peer fanout delivery contract",
        "## 4. Code-health hotspot resolution",
        "## 5. Preserved runtime invariants",
        "## 6. Test evidence and remaining tranche work",
        "## 7. Non-goals and Phase 436 pointer",
    ):
        assert heading in text
    for token in (
        "Phase 435 imported only the Phase-434-authorized peer fanout runtime subset.",
        "Release-track source anchor: ../ILC_release_track/docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md",
        "Release-track source snapshot sha256: 4e16ccb979d555329158753499b9dbbf38180460dd5db969a987999fc08a3113",
        "Real HTTP peer fanout attempts are now performed by ilc_core/network/peer.py.",
        "Delivery success and failure outcomes are observable in runtime logs.",
        "HTTP fanout remains a bridge implementation and does not foreclose native P2P replacement.",
        "Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.",
        "Runtime tranche imports landed on main with an identifiable runtime commit message and not as a bulk packaging merge.",
        "tools/runtime_baseline.py remains deferred to Phase 436.",
        "CDL-050 remains unopened and unaffected by Phase 435.",
        "Public packaging/bootstrap work remains outside the numbered window.",
        "Phase 436 is the next authorized runtime-tranche phase.",
    ):
        assert token in text


def test_phase_435_commit_did_not_mutate_decision_log() -> None:
    commit_ref = _resolve_phase_435_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_435_runtime_scope_is_exact() -> None:
    commit_ref = _resolve_phase_435_commit_ref()
    _assert_phase_435_runtime_scope(commit_ref)
