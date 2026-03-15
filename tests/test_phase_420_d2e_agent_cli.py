from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli.d2e_agent_cli import (
    CDL_042_DEPENDENCY,
    D2E_AGENT_CLI_VERSION,
    handle_agent_derive,
    handle_agent_inspect,
)
from ilc_core.identity.agent_id_runtime import derive_agent_id

PHASE_420_COMMIT_SUBJECT = "feat(g8): phase 420 d2e agent cli part 1"
MAIN_PY_PATH = Path("ilc_core/cli/main.py")
CLI_MODULE_PATH = Path("ilc_core/cli/d2e_agent_cli.py")
HANDOFF_PATH = Path("docs/specs/ilc_d2e_agent_cli_handoff_420_v0.1.md")
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


def _resolve_phase_420_commit_ref() -> str:
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
        if subject.strip() == PHASE_420_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        "ilc_core/cli/d2e_agent_cli.py",
        "ilc_core/cli/main.py",
        "tests/test_phase_420_d2e_agent_cli.py",
        str(HANDOFF_PATH),
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_420_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_420_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
    for path in changed:
        if path.startswith("ilc_core/"):
            assert path.startswith("ilc_core/cli/"), f"phase_420_ilc_core_scope_violation:{path}"
    assert "ilc_core/cli/main.py" in changed, "phase_420_main_py_wiring_missing"
    cli_paths = {
        path
        for path in changed
        if path.startswith("ilc_core/cli/") and path != "ilc_core/cli/main.py"
    }
    assert cli_paths, "phase_420_d2e_agent_cli_module_missing"


def test_d2e_agent_cli_module_exists_and_version_constant_correct() -> None:
    assert CLI_MODULE_PATH.exists()
    assert D2E_AGENT_CLI_VERSION == "d2e_agent_cli_420.v0.1"


def test_cdl_042_dependency_token_correct() -> None:
    assert CDL_042_DEPENDENCY == "cdl_042_ratified_407.v0.1"


def test_agent_derive_produces_correct_agent_id_from_hex() -> None:
    known_bytes = b"canonical-root-key-test-bytes"
    known_hex = known_bytes.hex()
    result = handle_agent_derive(known_hex)
    expected_agent_id = derive_agent_id(known_bytes)
    assert result["subcommand"] == "derive"
    assert result["agent_id"].startswith("agent-")
    assert result["agent_id"] == expected_agent_id
    assert result["version"] == D2E_AGENT_CLI_VERSION


def test_agent_derive_rejects_invalid_hex() -> None:
    with pytest.raises(ValueError, match="agent_derive_invalid_hex"):
        handle_agent_derive("not-hex")


def test_agent_inspect_returns_record_fields(tmp_path: Path) -> None:
    record_path = tmp_path / "agent-record.json"
    record = {"agent_id": "agent-123", "cluster": "a"}
    record_path.write_text(json.dumps(record), encoding="utf-8")

    result = handle_agent_inspect(str(record_path))
    assert result["subcommand"] == "inspect"
    assert result["record_path"] == str(record_path)
    assert result["fields"] == ["agent_id", "cluster"]
    assert result["record"] == record
    assert result["version"] == D2E_AGENT_CLI_VERSION


def test_agent_inspect_rejects_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="agent_inspect_record_not_found"):
        handle_agent_inspect(str(missing_path))


def test_main_py_agent_command_in_operational_commands() -> None:
    from ilc_core.cli.main import OPERATIONAL_COMMANDS

    assert "agent" in OPERATIONAL_COMMANDS


def test_main_py_agent_command_wired_in_dispatch_and_parser() -> None:
    text = _read(MAIN_PY_PATH)
    assert 'command == "agent"' in text
    assert 'add_parser("agent"' in text
    assert 'add_parser("derive"' in text
    assert 'add_parser("inspect"' in text
    assert '"query", "verify", "bundle", "agent"' in text


def test_agent_inspect_rejects_invalid_json(tmp_path: Path) -> None:
    record_path = tmp_path / "invalid.json"
    record_path.write_text("{invalid", encoding="utf-8")
    with pytest.raises(ValueError, match="agent_inspect_record_invalid_json"):
        handle_agent_inspect(str(record_path))


def test_agent_inspect_rejects_non_object_root(tmp_path: Path) -> None:
    record_path = tmp_path / "list.json"
    record_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="agent_inspect_record_not_object"):
        handle_agent_inspect(str(record_path))


def test_phase_420_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_420_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)


def test_phase_420_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_420_commit_ref()
    assert DECISION_LOG_PATH not in _changed_paths_for_commit(commit_ref)
