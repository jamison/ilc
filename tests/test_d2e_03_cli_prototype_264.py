from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path


MODULE_PATH = Path("ilc_core/cli/main.py")
LOCKED_COMMANDS = [
    "assert",
    "validate",
    "contradict",
    "refute",
    "revise",
    "link",
    "epoch",
    "query",
    "verify",
    "balance",
    "identity",
    "bundle",
    "shard",
    "capproof",
    "config",
]


def _run_cli(*args: str, graph_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", "-m", "ilc_core.cli.main", *args]
    env = None
    if graph_path is not None:
        env = dict(os.environ)
        env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    return subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)


def test_entrypoint_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_help_lists_all_locked_commands() -> None:
    result = _run_cli("--help")
    assert result.returncode == 0
    output = result.stdout
    for command in LOCKED_COMMANDS:
        assert command in output


def test_each_command_emits_success_envelope() -> None:
    # query, verify, and bundle became subcommand routers in Phases 300-304
    # and require additional arguments; they are excluded from the bare-command check.
    bare_commands = [c for c in LOCKED_COMMANDS if c not in ("query", "verify", "bundle")]
    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        for command in bare_commands:
            result = _run_cli(command, graph_path=graph_path)
            assert result.returncode == 0, (command, result.stderr)
            payload = json.loads(result.stdout)
            assert payload["schema_version"] == "254.v0.1"
            assert payload["command"] == command
            assert payload["ok"] is True
            assert "ts_utc" in payload
            assert "data" in payload


def test_unknown_command_exits_two() -> None:
    result = _run_cli("assert_truth")
    assert result.returncode == 2


def test_local_graph_state_file_created() -> None:
    # query became a subcommand router in Phase 300; epoch is used as the probe command.
    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "nested" / "graph_state.json"
        result = _run_cli("epoch", graph_path=graph_path)
        assert result.returncode == 0
        assert graph_path.exists()
        data = json.loads(graph_path.read_text(encoding="utf-8"))
        assert data["schema_version"] == "d2e03.v0.1"
        assert data["last_command"] == "epoch"


def test_help_does_not_expose_non_locked_commands() -> None:
    result = _run_cli("--help")
    assert result.returncode == 0
    output = result.stdout
    assert "assert_truth" not in output
    assert "star.map" not in output
