"""Phase 888–891 — CDL-075 truth primitive read-path query CLI tests.

Covers all 9 hard pass conditions from the Window 887-891 sequence lock:
  1. d2e_query_truth_cli.py module exists
  2. D2E_QUERY_TRUTH_CLI_VERSION and CDL_075_DEPENDENCY tokens
  3. handle_query_truth_node hit/miss
  4. handle_query_truth_edges source/target matching
  5. main.py truth-node and truth-edges subcommands wired
  6. Existing JSON-backed query handlers untouched
  7. Absent store path returns typed error (not crash)
  8. Subprocess CLI integration
  9. No mutation of LMDB store via query path
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli.d2e_query_truth_cli import (
    CDL_075_DEPENDENCY,
    D2E_QUERY_TRUTH_CLI_VERSION,
    QueryTruthCommandError,
    handle_query_truth_edges,
    handle_query_truth_node,
)
from ilc_core.epistemic.truth_primitive_graph_store import (
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    validate_truth_primitive_submission,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore

PHASE_890_COMMIT_SUBJECT = "feat(g8): phase 887-890 truth primitive query cli"
MODULE_PATH = Path("ilc_core/cli/d2e_query_truth_cli.py")
MAIN_PY_PATH = Path("ilc_core/cli/main.py")


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _assert_truth_envelope(body: str = "test claim", epoch: int = 1) -> dict:
    return {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": "agent-q-test",
        "epoch": epoch,
        "payload": {
            "content": {"body": body},
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }


def _populate_store(store_dir: Path, n: int = 1) -> list[str]:
    """Write n distinct assert.truth nodes; return their CIDv1 node_ids."""
    node_ids = []
    store = TruthPrimitiveGraphStore(store_dir)
    try:
        for i in range(n):
            env = _assert_truth_envelope(body=f"claim {i}", epoch=i + 1)
            result = validate_truth_primitive_submission(env)
            receipt = write_truth_primitive_result(store, env, result)
            node_ids.append(receipt["node_id"])
    finally:
        store.close()
    return node_ids


def _run_cli(*args: str, graph_path: Path, store_path: str | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    if store_path:
        env["ILC_TRUTH_GRAPH_STORE_PATH"] = store_path
    else:
        env.pop("ILC_TRUTH_GRAPH_STORE_PATH", None)
    return subprocess.run(
        ["python3", "-m", "ilc_core.cli.main", *args],
        capture_output=True, text=True, check=False, env=env,
    )


# ---------------------------------------------------------------------------
# 1. Module exists
# ---------------------------------------------------------------------------


def test_query_truth_cli_module_exists() -> None:
    assert MODULE_PATH.exists()


# ---------------------------------------------------------------------------
# 2. Version and dependency tokens
# ---------------------------------------------------------------------------


def test_version_token_correct() -> None:
    assert D2E_QUERY_TRUTH_CLI_VERSION == "d2e_query_truth_cli_888.v0.1"


def test_cdl_075_dependency_token_correct() -> None:
    assert CDL_075_DEPENDENCY == "cdl_075_truth_primitive_graph_persistence.v0.1"


# ---------------------------------------------------------------------------
# 3. handle_query_truth_node hit/miss
# ---------------------------------------------------------------------------


def test_query_truth_node_returns_record_for_known_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    node_ids = _populate_store(store_dir)
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    result = handle_query_truth_node(node_ids[0])
    assert result["subcommand"] == "truth-node"
    assert result["node_id"] == node_ids[0]
    assert result["node_record"]["primitive"] == "assert.truth"
    assert result["version"] == D2E_QUERY_TRUTH_CLI_VERSION


def test_query_truth_node_raises_for_unknown_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    with pytest.raises(QueryTruthCommandError) as exc_info:
        handle_query_truth_node("bafyreiunknownnodeshouldnotexist12345")
    assert exc_info.value.token == "query_truth_node_not_found"


def test_query_truth_node_raises_for_empty_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    with pytest.raises(QueryTruthCommandError) as exc_info:
        handle_query_truth_node("")
    assert exc_info.value.token == "query_truth_node_id_missing"


# ---------------------------------------------------------------------------
# 4. handle_query_truth_edges source/target matching
# ---------------------------------------------------------------------------


def test_query_truth_edges_returns_edges_for_node(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    node_ids = _populate_store(store_dir)
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    result = handle_query_truth_edges(node_ids[0])
    assert result["subcommand"] == "truth-edges"
    assert result["node_id"] == node_ids[0]
    assert isinstance(result["edges"], list)
    assert result["count"] >= 1
    # All returned edges reference the queried node
    for edge in result["edges"]:
        assert edge.get("source") == node_ids[0] or edge.get("target") == node_ids[0]


def test_query_truth_edges_returns_empty_for_unknown_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    result = handle_query_truth_edges("bafy-unknown-node-id")
    assert result["count"] == 0
    assert result["edges"] == []


def test_query_truth_edges_by_agent_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    _populate_store(store_dir, n=2)
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    # agent_id appears as the target of asserted_by edges
    result = handle_query_truth_edges("agent-q-test")
    assert result["count"] >= 1
    for edge in result["edges"]:
        assert edge.get("source") == "agent-q-test" or edge.get("target") == "agent-q-test"


# ---------------------------------------------------------------------------
# 5. main.py wiring — truth-node and truth-edges subcommands
# ---------------------------------------------------------------------------


def test_main_py_truth_node_subcommand_registered() -> None:
    text = MAIN_PY_PATH.read_text(encoding="utf-8")
    assert '"truth-node"' in text
    assert '"truth-edges"' in text
    assert "p_truth_node" in text
    assert "p_truth_edges" in text


def test_main_py_truth_query_dispatch_wired() -> None:
    text = MAIN_PY_PATH.read_text(encoding="utf-8")
    assert '"truth-node"' in text
    assert '"truth-edges"' in text
    assert "handle_query_truth_node" in text
    assert "handle_query_truth_edges" in text


# ---------------------------------------------------------------------------
# 6. Existing JSON-backed query handlers untouched
# ---------------------------------------------------------------------------


def test_existing_query_node_handler_unchanged() -> None:
    text = MAIN_PY_PATH.read_text(encoding="utf-8")
    assert 'subcommand == "node"' in text
    assert "_query_node(" in text


def test_existing_query_epoch_handler_unchanged() -> None:
    text = MAIN_PY_PATH.read_text(encoding="utf-8")
    assert 'subcommand == "epoch"' in text
    assert "_query_epoch(" in text


def test_existing_query_claim_handler_unchanged() -> None:
    text = MAIN_PY_PATH.read_text(encoding="utf-8")
    assert 'subcommand == "claim"' in text
    assert "_query_claim(" in text


# ---------------------------------------------------------------------------
# 7. Absent store path returns typed error (not crash)
# ---------------------------------------------------------------------------


def test_query_truth_node_absent_store_path_raises_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    with pytest.raises(QueryTruthCommandError) as exc_info:
        handle_query_truth_node("bafy-any-id")
    assert exc_info.value.token == "query_truth_store_path_not_configured"


def test_query_truth_edges_absent_store_path_raises_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    with pytest.raises(QueryTruthCommandError) as exc_info:
        handle_query_truth_edges("bafy-any-id")
    assert exc_info.value.token == "query_truth_store_path_not_configured"


# ---------------------------------------------------------------------------
# 8. Subprocess CLI integration
# ---------------------------------------------------------------------------


def test_query_truth_node_via_subprocess(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    graph_path = tmp_path / "graph.json"
    node_ids = _populate_store(store_dir)

    result = _run_cli(
        "query", "truth-node", "--node-id", node_ids[0],
        graph_path=graph_path,
        store_path=str(store_dir),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["node_id"] == node_ids[0]
    assert payload["data"]["node_record"]["primitive"] == "assert.truth"


def test_query_truth_edges_via_subprocess(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    graph_path = tmp_path / "graph.json"
    node_ids = _populate_store(store_dir)

    result = _run_cli(
        "query", "truth-edges", "--node-id", node_ids[0],
        graph_path=graph_path,
        store_path=str(store_dir),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["count"] >= 1


def test_query_truth_node_not_found_via_subprocess(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    graph_path = tmp_path / "graph.json"

    result = _run_cli(
        "query", "truth-node", "--node-id", "bafyreiunknownnodexyz",
        graph_path=graph_path,
        store_path=str(store_dir),
    )
    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False


def test_query_truth_node_absent_store_via_subprocess(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    result = _run_cli(
        "query", "truth-node", "--node-id", "bafy-any-id",
        graph_path=graph_path,
        store_path=None,
    )
    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False


# ---------------------------------------------------------------------------
# 9. No mutation via query path
# ---------------------------------------------------------------------------


def test_query_truth_node_does_not_mutate_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    node_ids = _populate_store(store_dir)
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))

    # Record node count before
    store = TruthPrimitiveGraphStore(store_dir)
    before_count = len(store.iter_nodes())
    store.close()

    handle_query_truth_node(node_ids[0])

    # Verify count unchanged
    store = TruthPrimitiveGraphStore(store_dir)
    after_count = len(store.iter_nodes())
    store.close()

    assert before_count == after_count


# ---------------------------------------------------------------------------
# Phase 890 commit scope guard (post-commit)
# ---------------------------------------------------------------------------


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    r = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True, check=True, text=True,
    )
    return {line.strip() for line in r.stdout.splitlines() if line.strip()}


def _resolve_phase_890_commit_ref() -> str:
    r = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True, check=True, text=True,
    )
    for line in r.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_890_COMMIT_SUBJECT:
            changed = _changed_paths_for_commit(commit_hash)
            required = {
                "ilc_core/cli/d2e_query_truth_cli.py",
                "ilc_core/cli/main.py",
                "tests/test_phase_888_891_query_truth_cli.py",
            }
            if required.issubset(changed):
                return commit_hash
    raise AssertionError("phase_890_commit_not_present_in_local_history")


def test_phase_890_commit_scope_guard() -> None:
    commit_ref = _resolve_phase_890_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    for path in changed:
        if path.startswith("ilc_core/"):
            assert path.startswith("ilc_core/cli/"), \
                f"phase_890_ilc_core_scope_violation:{path}"
    assert "ilc_core/cli/main.py" in changed
    assert "ilc_core/cli/d2e_query_truth_cli.py" in changed


def test_phase_890_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_890_commit_ref()
    assert "docs/specs/ilc_constitutional_decision_log_v0.1.md" not in _changed_paths_for_commit(commit_ref)
