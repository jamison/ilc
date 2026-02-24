"""Phase 294 implementation tests for D2e-04 identity subsystem."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.testing.phase_commit_manifest import resolve_phase_commit_ref_or_skip


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        CLI_CMD + args,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _json_payload(result: subprocess.CompletedProcess[str]) -> dict:
    blob = result.stdout.strip() or result.stderr.strip()
    assert blob, "expected_json_payload"
    return json.loads(blob)


def test_identity_commands_return_json_envelopes(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    init_res = _run_cli(["identity", "init", "--lineage-id", "lineage-a", "--key-ref", "key-a"], env)
    assert init_res.returncode == 0
    init_payload = _json_payload(init_res)
    assert init_payload["ok"] is True
    assert init_payload["command"] == "identity"
    assert init_payload["data"]["action"] == "init"

    show_res = _run_cli(["identity", "show"], env)
    assert show_res.returncode == 0
    show_payload = _json_payload(show_res)
    assert show_payload["ok"] is True
    assert show_payload["data"]["action"] == "show"

    rotate_res = _run_cli(["identity", "rotate", "--new-key-ref", "key-b"], env)
    assert rotate_res.returncode == 0
    rotate_payload = _json_payload(rotate_res)
    assert rotate_payload["ok"] is True
    assert rotate_payload["data"]["action"] == "rotate"
    assert rotate_payload["data"]["state"]["key_ref"] == "key-b"

    export_res = _run_cli(["identity", "export"], env)
    assert export_res.returncode == 0
    export_payload = _json_payload(export_res)
    assert export_payload["ok"] is True
    assert export_payload["data"]["action"] == "export"


def test_error_conditions_return_contract_exit_codes(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    # Operational failure: show before init.
    show_res = _run_cli(["identity", "show"], env)
    assert show_res.returncode == 1
    show_payload = _json_payload(show_res)
    assert show_payload["ok"] is False
    assert show_payload["code"] == "1"
    assert "identity_not_initialized" in show_payload["message"]

    # Usage failure: unknown subcommand.
    bad_res = _run_cli(["identity", "bogus"], env)
    assert bad_res.returncode == 2
    bad_payload = _json_payload(bad_res)
    assert bad_payload["ok"] is False
    assert bad_payload["code"] == "2"


def test_behavior_is_deterministic_for_repeated_export(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    init_res = _run_cli(["identity", "init", "--lineage-id", "lineage-d", "--key-ref", "key-d"], env)
    assert init_res.returncode == 0

    export_one = _json_payload(_run_cli(["identity", "export"], env))
    export_two = _json_payload(_run_cli(["identity", "export"], env))

    assert export_one["ok"] is True
    assert export_two["ok"] is True
    assert export_one["data"] == export_two["data"]


def test_bare_identity_command_preserves_d2e03_compatibility(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    result = _run_cli(["identity"], env)
    assert result.returncode == 0
    payload = _json_payload(result)
    assert payload["ok"] is True
    assert payload["command"] == "identity"
    assert payload["data"]["mode"] == "prototype_compat"
    assert payload["data"]["lineage_id"] == "lineage-local"
    assert payload["data"]["export_ref"] == "identity-local"


def _resolve_phase_294_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_294")


def test_no_decision_log_file_changed_in_phase_commit() -> None:
    commit_ref = _resolve_phase_294_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed
