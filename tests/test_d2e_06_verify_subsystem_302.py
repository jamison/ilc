"""Phase 302 runtime tests for D2e-06 verify subsystem implementation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_302_COMMIT_SUBJECT = "feat(g8): phase 302 d2e-06 verify subsystem initial implementation tranche"


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
            {"id": "node-1", "claim_id": "claim-a", "payload": {"text": "alpha"}},
            {"node_id": "node-2", "claim_id": "claim-b", "payload": {"text": "beta"}},
        ],
        "edges": [],
        "epochs": [{"epoch": 8}],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(payload))
    meta = normalized.get("meta", {})
    if isinstance(meta, dict):
        meta.pop("generated_at", None)
    return normalized


def _assert_min_check_schema(checks: list[dict[str, Any]]) -> None:
    assert checks, "checks_empty"
    for item in checks:
        assert "check_type" in item
        assert isinstance(item["check_type"], str)
        assert "passed" in item
        assert isinstance(item["passed"], bool)


def test_verify_subcommands_return_nested_envelopes(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    identity_path = tmp_path / "identity.json"
    _write_graph_state(graph_path)
    identity_path.write_text(
        json.dumps(
            {
                "lineage_id": "lineage-a",
                "status": "active",
                "key_ref": "key-a",
                "rotation_count": 0,
                "updated_at": "2026-02-25T00:00:00Z",
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    for args, command_token in (
        (["verify", "claim", "--claim-id", "claim-a"], "verify claim"),
        (["verify", "node", "--node-id", "node-1"], "verify node"),
        (["verify", "lineage", "--lineage-id", "lineage-a"], "verify lineage"),
    ):
        result = _run_cli(args, env)
        assert result.returncode == 0
        payload = _payload(result)
        assert set(payload.keys()) == {"ok", "data", "meta"}
        assert payload["ok"] is True
        assert payload["meta"]["schema_version"] == "301.v0.1"
        assert payload["meta"]["command"] == command_token
        assert payload["meta"]["generated_at"].endswith("Z")
        assert set(payload["data"].keys()) == {"subject", "verdict", "checks"}
        _assert_min_check_schema(payload["data"]["checks"])


def test_verify_error_paths_return_nested_errors(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _write_graph_state(graph_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    not_found = _run_cli(["verify", "claim", "--claim-id", "missing"], env)
    assert not_found.returncode == 1
    not_found_payload = _payload(not_found)
    assert not_found_payload["ok"] is False
    assert not_found_payload["error"]["code"] == "verify_not_found"
    assert not_found_payload["meta"]["command"] == "verify claim"

    invalid_input = _run_cli(["verify", "claim"], env)
    assert invalid_input.returncode == 2
    invalid_payload = _payload(invalid_input)
    assert invalid_payload["ok"] is False
    assert invalid_payload["error"]["code"] == "verify_invalid_input"
    assert invalid_payload["meta"]["command"] == "verify claim"


def test_verify_determinism_for_repeated_claim_requests(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _write_graph_state(graph_path)
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    one = _payload(_run_cli(["verify", "claim", "--claim-id", "claim-a"], env))
    two = _payload(_run_cli(["verify", "claim", "--claim-id", "claim-a"], env))
    assert _normalize(one) == _normalize(two)


def test_verify_addition_does_not_regress_query_or_identity_envelopes(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    identity_path = tmp_path / "identity.json"
    _write_graph_state(graph_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    query_result = _run_cli(["query", "node", "--node-id", "node-1"], env)
    assert query_result.returncode == 0
    query_payload = _payload(query_result)
    assert set(query_payload.keys()) == {"ok", "data", "meta"}
    assert query_payload["meta"]["schema_version"] == "299.v0.1"
    assert query_payload["meta"]["command"] == "query node"

    identity_init = _run_cli(["identity", "init"], env)
    assert identity_init.returncode == 0
    identity_payload = _payload(identity_init)
    assert identity_payload["schema_version"] == "254.v0.1"
    assert identity_payload["command"] == "identity"
    assert "meta" not in identity_payload


def test_verify_lineage_uses_local_identity_state_only(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    identity_path = tmp_path / "identity.json"
    _write_graph_state(graph_path)

    identity_path.write_text(
        json.dumps({"lineage_id": "lineage-local", "status": "active"}, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    result = _run_cli(["verify", "lineage", "--lineage-id", "lineage-local"], env)
    assert result.returncode == 0
    payload = _payload(result)
    checks = payload["data"]["checks"]
    assert any(item["check_type"] == "identity_state_present" for item in checks)
    assert any(item["check_type"] == "lineage_id_match" for item in checks)


def _resolve_phase_302_commit_ref() -> str:
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
        if subject.strip() == PHASE_302_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_302_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_302_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_consensus_or_security_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_302_commit_ref()
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
    assert not forbidden, f"phase_302_forbidden_runtime_mutations:{forbidden}"
