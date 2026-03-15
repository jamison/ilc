from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli.d2e_lifecycle_cli import (
    CDL_046_DEPENDENCY,
    D2D_GOSSIP_DEPENDENCY,
    D2E_LIFECYCLE_CLI_VERSION,
    handle_node_constants,
    handle_node_timed_out_d2d,
    handle_node_timed_out_inspect,
)

PHASE_421_COMMIT_SUBJECT = "feat(g8): phase 421 d2e lifecycle cli part 2"
MAIN_PY_PATH = Path("ilc_core/cli/main.py")
CLI_MODULE_PATH = Path("ilc_core/cli/d2e_lifecycle_cli.py")
HANDOFF_PATH = Path("docs/specs/ilc_d2e_lifecycle_cli_handoff_421_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_421_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_421_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        "ilc_core/cli/d2e_lifecycle_cli.py",
        "ilc_core/cli/main.py",
        "tests/test_phase_421_d2e_lifecycle_cli.py",
        str(HANDOFF_PATH),
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_421_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_421_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
    for path in changed:
        if path.startswith("ilc_core/"):
            assert path.startswith("ilc_core/cli/"), f"phase_421_ilc_core_scope_violation:{path}"
    assert "ilc_core/cli/main.py" in changed, "phase_421_main_py_wiring_missing"
    cli_paths = {
        path
        for path in changed
        if path.startswith("ilc_core/cli/") and path != "ilc_core/cli/main.py"
    }
    assert cli_paths, "phase_421_d2e_lifecycle_cli_module_missing"


def _write_record(path: Path, record: dict[str, object]) -> None:
    path.write_text(json.dumps(record), encoding="utf-8")


def _run_cli(*args: str, graph_path: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    return subprocess.run(
        ["python3", "-m", "ilc_core.cli.main", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_d2e_lifecycle_cli_module_exists_and_version_constant_correct() -> None:
    assert CLI_MODULE_PATH.exists()
    assert D2E_LIFECYCLE_CLI_VERSION == "d2e_lifecycle_cli_421.v0.1"


def test_cdl_046_and_d2d_dependency_tokens_correct() -> None:
    assert CDL_046_DEPENDENCY == "cdl_046_ratified_409.v0.1"
    assert D2D_GOSSIP_DEPENDENCY == "d2d_gossip_382.v0.1"


def test_node_constants_returns_locked_runtime_values() -> None:
    result = handle_node_constants()
    assert result == {
        "subcommand": "constants",
        "orphan_timeout_epochs": 4,
        "recovery_policy": "stake_full_release",
        "timed_out_runtime_version": "timed_out_lifecycle_runtime_411.v0.1",
        "version": "d2e_lifecycle_cli_421.v0.1",
    }


def test_timed_out_inspect_returns_expected_lifecycle_path(tmp_path: Path) -> None:
    record_path = tmp_path / "timed-out.json"
    _write_record(
        record_path,
        {"claim_id": "claim-1", "orphaned_since_epoch": 10, "payload_cid": "bafy-claim-1"},
    )
    result = handle_node_timed_out_inspect(str(record_path), current_epoch=14)
    assert result["timed_out"] is True
    assert result["lifecycle_path"] == "timed_out_recovery"
    assert result["recovery_policy"] == "stake_full_release"


def test_timed_out_inspect_returns_pending_path_below_boundary(tmp_path: Path) -> None:
    record_path = tmp_path / "pending.json"
    _write_record(record_path, {"claim_id": "claim-2", "orphaned_since_epoch": 10})
    result = handle_node_timed_out_inspect(str(record_path), current_epoch=13)
    assert result["timed_out"] is False
    assert result["lifecycle_path"] == "pending_orphan_grace"


def test_timed_out_d2d_returns_transport_envelope_for_timed_out_claim(tmp_path: Path) -> None:
    record_path = tmp_path / "d2d.json"
    _write_record(
        record_path,
        {"claim_id": "claim-3", "orphaned_since_epoch": 5, "payload_cid": "bafy-claim-3"},
    )
    result = handle_node_timed_out_d2d(
        str(record_path),
        current_epoch=9,
        channel_id="cid:11223344556677889900aabbccddeeff",
        sender_peer_id="peer:node-1",
    )
    envelope = result["envelope"]
    assert result["timed_out"] is True
    assert result["recovery_policy"] == "stake_full_release"
    assert envelope["message_id"] == "timed-out:claim-3:9"
    assert envelope["payload_cid"] == "bafy-claim-3"
    assert envelope["transport_headers"]["event"] == "claim_timed_out"


def test_timed_out_d2d_rejects_preboundary_claim(tmp_path: Path) -> None:
    record_path = tmp_path / "not-timed-out.json"
    _write_record(
        record_path,
        {"claim_id": "claim-4", "orphaned_since_epoch": 5, "payload_cid": "bafy-claim-4"},
    )
    with pytest.raises(ValueError, match="node_d2d_not_timed_out"):
        handle_node_timed_out_d2d(
            str(record_path),
            current_epoch=8,
            channel_id="cid:11223344556677889900aabbccddeeff",
            sender_peer_id="peer:node-2",
        )


def test_main_py_node_command_in_operational_commands() -> None:
    from ilc_core.cli.main import OPERATIONAL_COMMANDS

    assert "node" in OPERATIONAL_COMMANDS


def test_main_py_node_command_wired_and_graph_state_exempt() -> None:
    text = _read(MAIN_PY_PATH)
    assert 'command == "node"' in text
    assert 'add_parser("node"' in text
    assert 'add_parser("constants"' in text
    assert 'add_parser("timed-out-inspect"' in text
    assert 'add_parser("timed-out-d2d"' in text
    assert '"query", "verify", "bundle", "agent", "node"' in text


def test_main_node_constants_cli_does_not_mutate_graph_state(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    result = _run_cli("--graph-state", str(graph_path), "node", "constants", graph_path=graph_path)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["command"] == "node"
    assert payload["data"]["subcommand"] == "constants"
    assert not graph_path.exists()


def test_phase_421_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_421_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)


def test_phase_421_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_421_commit_ref()
    assert DECISION_LOG_PATH not in _changed_paths_for_commit(commit_ref)
