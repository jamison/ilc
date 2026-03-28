"""Phase 300 runtime tests for D2e-05 query subsystem implementation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_300_COMMIT_SUBJECT = "feat(g8): phase 300 d2e-05 query subsystem initial implementation tranche"


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CLI_CMD + args, capture_output=True, text=True, env=env, check=False)


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    blob = result.stdout.strip() or result.stderr.strip()
    assert blob, "expected_json_payload"
    return json.loads(blob)


def _write_graph_state(path: Path) -> None:
    state = {
        "schema_version": "d2e03.v0.1",
        "nodes": [
            {
                "id": "node-1",
                "claim_id": "claim-a",
                "objective_score": 0.8,
                "payload": {"text": "alpha"},
                "reputation_score": 0.92,
                "reuse_count": 14,
                "sybil_risk": 0.03,
            },
            {
                "id": "node-2",
                "claim_id": "claim-a",
                "objective_score": 0.6,
                "payload": {"text": "beta"},
            },
        ],
        "edges": [],
        "epochs": [{"epoch": 7, "issued_ilc": 123.45}],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _normalize_query_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(payload))
    meta = normalized.get("meta", {})
    if isinstance(meta, dict):
        meta.pop("generated_at", None)
    return normalized


def test_query_subcommands_use_phase299_nested_envelope(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _write_graph_state(graph_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)

    for args, command_token in (
        (["query", "node", "--node-id", "node-1"], "query node"),
        (["query", "epoch", "--epoch", "7"], "query epoch"),
        (["query", "claim", "--claim-id", "claim-a"], "query claim"),
    ):
        result = _run_cli(args, env)
        assert result.returncode == 0
        payload = _payload(result)
        assert set(payload.keys()) == {"ok", "data", "meta"}
        assert payload["ok"] is True
        assert payload["meta"]["command"] == command_token
        assert payload["meta"]["schema_version"] == "299.v0.1"
        assert payload["meta"]["generated_at"].endswith("Z")


def test_query_error_paths_use_nested_error_object(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _write_graph_state(graph_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)

    not_found = _run_cli(["query", "node", "--node-id", "missing"], env)
    assert not_found.returncode == 1
    not_found_payload = _payload(not_found)
    assert not_found_payload["ok"] is False
    assert not_found_payload["error"]["code"] == "query_not_found"
    assert not_found_payload["meta"]["command"] == "query node"
    assert "code" not in not_found_payload

    invalid_input = _run_cli(["query", "node"], env)
    assert invalid_input.returncode == 2
    invalid_payload = _payload(invalid_input)
    assert invalid_payload["ok"] is False
    assert invalid_payload["error"]["code"] == "query_invalid_input"
    assert invalid_payload["meta"]["command"] == "query node"


def test_query_output_is_deterministic_for_identical_input(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _write_graph_state(graph_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)

    one = _payload(_run_cli(["query", "claim", "--claim-id", "claim-a"], env))
    two = _payload(_run_cli(["query", "claim", "--claim-id", "claim-a"], env))
    assert _normalize_query_payload(one) == _normalize_query_payload(two)


def test_identity_envelope_remains_legacy_shape(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    init_result = _run_cli(["identity", "init"], env)
    assert init_result.returncode == 0
    init_payload = _payload(init_result)
    assert init_payload["ok"] is True
    assert init_payload["command"] == "identity"
    assert init_payload["schema_version"] == "254.v0.1"
    assert "meta" not in init_payload

    uninitialized_env = os.environ.copy()
    uninitialized_env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph2.json")
    uninitialized_env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity2.json")
    show_result = _run_cli(["identity", "show"], uninitialized_env)
    assert show_result.returncode == 1
    show_payload = _payload(show_result)
    assert show_payload["ok"] is False
    assert show_payload["error"] is True
    assert show_payload["code"] == "1"
    assert "meta" not in show_payload


def test_query_does_not_introduce_new_reputation_mappings(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _write_graph_state(graph_path)
    source_state = json.loads(graph_path.read_text(encoding="utf-8"))
    source_node = source_state["nodes"][0]

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)

    result = _run_cli(["query", "node", "--node-id", "node-1"], env)
    assert result.returncode == 0
    payload = _payload(result)
    returned_node = payload["data"]["node"]

    assert set(returned_node.keys()) == set(source_node.keys())
    for key in source_node:
        assert returned_node[key] == source_node[key]


def _resolve_phase_300_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_300_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_300_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_300_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_consensus_or_security_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_300_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [
        path
        for path in changed
        if path.startswith("ilc_core/consensus/") or path.startswith("ilc_core/security/")
    ]
    assert not forbidden, f"phase_300_forbidden_runtime_mutations:{forbidden}"
