"""Phase 304 runtime tests for D2e-07 bundle subsystem implementation."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_304_COMMIT_SUBJECT = "feat(g8): phase 304 d2e-07 bundle subsystem initial implementation tranche"


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CLI_CMD + args, capture_output=True, text=True, env=env, check=False)


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    blob = result.stdout.strip() or result.stderr.strip()
    assert blob, "expected_json_payload"
    return json.loads(blob)


def _manifest_hash(manifest: dict[str, Any]) -> str:
    stable = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _write_graph_state(path: Path, with_refs: bool = True) -> None:
    nodes = [{"id": "node-1", "claim_id": "claim-a", "payload": {"text": "alpha"}}] if with_refs else []
    state = {
        "schema_version": "d2e03.v0.1",
        "nodes": nodes,
        "edges": [],
        "epochs": [{"epoch": 9}],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_bundle_state(path: Path, *, blocked: bool = False) -> None:
    manifest = {
        "bundle_version": "v1",
        "entries": [{"cid": "node-1", "kind": "knowledge_node"}],
        "name": "demo-bundle",
    }
    state = {
        "schema_version": "d2e07.v0.1",
        "bundles": [
            {
                "bundle_cid": "bafy-bundle-1",
                "provider": "blocked" if blocked else "local",
                "manifest": manifest,
                "integrity": {"manifest_sha256": _manifest_hash(manifest)},
                "graph_refs": {"node_ids": ["node-1"], "claim_ids": ["claim-a"]},
            }
        ],
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


def test_bundle_subcommands_return_nested_envelopes(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "default_graph.json")
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    for args, token in (
        (["bundle", "inspect", "--bundle-cid", "bafy-bundle-1"], "bundle inspect"),
        (["bundle", "verify", "--bundle-cid", "bafy-bundle-1"], "bundle verify"),
        (
            ["bundle", "validate-local", "--bundle-cid", "bafy-bundle-1", "--graph-state", str(graph_path)],
            "bundle validate-local",
        ),
    ):
        result = _run_cli(args, env)
        assert result.returncode == 0
        payload = _payload(result)
        assert set(payload.keys()) == {"ok", "data", "meta"}
        assert payload["ok"] is True
        assert payload["meta"]["command"] == token
        assert payload["meta"]["schema_version"] == "303.v0.1"
        assert payload["meta"]["generated_at"].endswith("Z")
        assert set(payload["data"].keys()) == {"subject", "result", "checks"}
        _assert_min_check_schema(payload["data"]["checks"])


def test_bundle_error_paths_use_nested_error_object(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    not_found = _run_cli(["bundle", "inspect", "--bundle-cid", "missing"], env)
    assert not_found.returncode == 1
    not_found_payload = _payload(not_found)
    assert not_found_payload["ok"] is False
    assert not_found_payload["error"]["code"] == "bundle_not_found"
    assert not_found_payload["meta"]["command"] == "bundle inspect"

    invalid = _run_cli(["bundle", "inspect"], env)
    assert invalid.returncode == 2
    invalid_payload = _payload(invalid)
    assert invalid_payload["ok"] is False
    assert invalid_payload["error"]["code"] == "bundle_invalid_input"
    assert invalid_payload["meta"]["command"] == "bundle inspect"

    unknown_arg = _run_cli(["bundle", "verify", "--bundle-cid", "bafy-bundle-1", "--unknown-arg"], env)
    assert unknown_arg.returncode == 2
    unknown_payload = _payload(unknown_arg)
    assert unknown_payload["ok"] is False
    assert unknown_payload["error"]["code"] == "bundle_invalid_input"


def test_bundle_provider_blocked_fails_closed(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path, blocked=True)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    result = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-1"], env)
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "bundle_provider_blocked"


def test_bundle_backend_unavailable_returns_contract_token(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(graph_path)
    bundle_path.write_text("{invalid_json", encoding="utf-8")

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    result = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-1"], env)
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "bundle_backend_unavailable"


def test_bundle_determinism_for_repeated_requests(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    one = _payload(_run_cli(["bundle", "verify", "--bundle-cid", "bafy-bundle-1"], env))
    two = _payload(_run_cli(["bundle", "verify", "--bundle-cid", "bafy-bundle-1"], env))
    assert _normalize(one) == _normalize(two)


def test_validate_local_uses_subcommand_graph_state_path(tmp_path: Path) -> None:
    top_level_graph = tmp_path / "top_level_graph.json"
    subcommand_graph = tmp_path / "subcommand_graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(top_level_graph, with_refs=False)
    _write_graph_state(subcommand_graph, with_refs=True)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    result = _run_cli(
        [
            "--graph-state",
            str(top_level_graph),
            "bundle",
            "validate-local",
            "--bundle-cid",
            "bafy-bundle-1",
            "--graph-state",
            str(subcommand_graph),
        ],
        env,
    )
    assert result.returncode == 0
    payload = _payload(result)
    assert payload["ok"] is True
    assert payload["data"]["subject"]["graph_state_path"] == str(subcommand_graph)


def test_validate_local_fails_when_subcommand_graph_state_is_invalid(tmp_path: Path) -> None:
    top_level_graph = tmp_path / "top_level_graph.json"
    subcommand_graph = tmp_path / "subcommand_graph.json"
    bundle_path = tmp_path / "bundle.json"
    _write_graph_state(top_level_graph, with_refs=True)
    _write_graph_state(subcommand_graph, with_refs=False)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)

    result = _run_cli(
        [
            "--graph-state",
            str(top_level_graph),
            "bundle",
            "validate-local",
            "--bundle-cid",
            "bafy-bundle-1",
            "--graph-state",
            str(subcommand_graph),
        ],
        env,
    )
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "bundle_manifest_invalid"


def test_bundle_integration_does_not_regress_query_verify_or_identity_envelopes(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    identity_path = tmp_path / "identity.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    query = _run_cli(["query", "node", "--node-id", "node-1"], env)
    assert query.returncode == 0
    query_payload = _payload(query)
    assert set(query_payload.keys()) == {"ok", "data", "meta"}
    assert query_payload["meta"]["schema_version"] == "299.v0.1"

    verify = _run_cli(["verify", "claim", "--claim-id", "claim-a"], env)
    assert verify.returncode == 0
    verify_payload = _payload(verify)
    assert set(verify_payload.keys()) == {"ok", "data", "meta"}
    assert verify_payload["meta"]["schema_version"] == "301.v0.1"

    identity = _run_cli(["identity", "init"], env)
    assert identity.returncode == 0
    identity_payload = _payload(identity)
    assert identity_payload["schema_version"] == "254.v0.1"
    assert "meta" not in identity_payload


def _resolve_phase_304_commit_ref() -> str:
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
        if subject.strip() == PHASE_304_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_304_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_304_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_consensus_or_security_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_304_commit_ref()
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
    assert not forbidden, f"phase_304_forbidden_runtime_mutations:{forbidden}"
