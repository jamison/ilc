"""Phase 874 — CDL-074 truth primitive submit CLI tests.

Covers all hard pass conditions from the Window 873-876 sequence lock:
  - All six agent-issuable primitives via handle_submit
  - commit.epoch rejection
  - Malformed envelope rejection
  - Dependency token presence
  - main.py submit wiring and graph-state exemption
  - No graph-state mutation via subprocess
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli.d2e_submit_cli import (
    CDL_074_DEPENDENCY,
    D2E_SUBMIT_CLI_VERSION,
    SubmitCommandError,
    handle_submit,
)

PHASE_874_COMMIT_SUBJECT = "feat(g8): phase 873-874 submit cli wiring"
MAIN_PY_PATH = Path("ilc_core/cli/main.py")
CLI_MODULE_PATH = Path("ilc_core/cli/d2e_submit_cli.py")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ns(**kwargs: object) -> argparse.Namespace:
    """Build a minimal argparse.Namespace for handle_submit."""
    defaults = {
        "primitive": None,
        "payload_json": None,
        "payload_file": None,
        "agent_id": None,
        "epoch": None,
        "sig": "UNSIGNED",
        "signing_key": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


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


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_874_commit_ref() -> str:
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
        if subject.strip() == PHASE_874_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        "ilc_core/cli/d2e_submit_cli.py",
        "ilc_core/cli/main.py",
        "tests/test_phase_874_d2e_submit_cli.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_874_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_874_commit_not_present_in_local_history")


# ---------------------------------------------------------------------------
# Standard payloads for each primitive
# ---------------------------------------------------------------------------

_ASSERT_TRUTH_PAYLOAD = json.dumps({
    "content": {"body": "the sky is blue"},
    "primitive_type": "observation",
    "epistemic_type": "objective",
    "parent_node_ids": [],
})

_VALIDATE_CLAIM_PAYLOAD = json.dumps({
    "target_node_id": "bafy-node-abc",
    "confidence": "0.85",
    "evidence_summary": "direct measurement confirms claim",
})

_CONTRADICT_ASSERT_PAYLOAD = json.dumps({
    "node_a_id": "bafy-node-1",
    "node_b_id": "bafy-node-2",
    "contradiction_scope": "empirical",
    "rationale": "both cannot hold under identical conditions",
})

_LINK_CLAIM_PAYLOAD = json.dumps({
    "source_node_id": "bafy-src-1",
    "target_node_id": "bafy-tgt-1",
    "link_type": "cites",
    "link_rationale": "source cites target as prior work",
})

_REFUTATION_CRITERION = {
    "claim": "the proposed hypothesis is falsifiable",
    "evidence_type": "empirical",
    "scope_boundary": "within peer-reviewed dataset",
    "claim_form": "falsifiable_positive",
    "has_falsifiable_test": True,
}

_REFUTE_CLAIM_PAYLOAD = json.dumps({
    "target_node_id": "bafy-target-claim",
    "refutation_criterion": _REFUTATION_CRITERION,
    "evidence_node_ids": ["bafy-evidence-1"],
})

_REVISE_ASSERT_PAYLOAD = json.dumps({
    "source_node_id": "bafy-original-node",
    "revised_content": {
        "primitive_type": "observation",
        "body": "revised body content",
    },
    "revision_rationale": "correcting measurement error",
})


# ---------------------------------------------------------------------------
# 1. Module existence and version token
# ---------------------------------------------------------------------------


def test_d2e_submit_cli_module_exists_and_version_constant_correct() -> None:
    assert CLI_MODULE_PATH.exists()
    assert D2E_SUBMIT_CLI_VERSION == "d2e_submit_cli_874_GAP_GRAPH_SIGN_00.v0.1"


# ---------------------------------------------------------------------------
# 2. Dependency token
# ---------------------------------------------------------------------------


def test_cdl_074_dependency_token_correct() -> None:
    assert CDL_074_DEPENDENCY == "cdl_074_truth_primitive_runtime_ratified.v0.1"


# ---------------------------------------------------------------------------
# 3–8. All six valid primitives via handle_submit
# ---------------------------------------------------------------------------


def test_handle_submit_assert_truth_returns_contract() -> None:
    ns = _ns(primitive="assert.truth", payload_json=_ASSERT_TRUTH_PAYLOAD, agent_id="agent-abc", epoch=1)
    result = handle_submit(ns)
    assert result["subcommand"] == "submit"
    assert result["primitive"] == "assert.truth"
    assert result["creates_node"] is True
    assert result["node_primitive_type"] == "observation"
    assert isinstance(result["edges"], list)
    edge_types = {e["edge_type"] for e in result["edges"]}
    assert "asserted_by" in edge_types
    assert "graph_persistence" in result
    assert result["version"] == D2E_SUBMIT_CLI_VERSION


def test_handle_submit_validate_claim_returns_contract() -> None:
    ns = _ns(primitive="validate.claim", payload_json=_VALIDATE_CLAIM_PAYLOAD, agent_id="agent-abc", epoch=1)
    result = handle_submit(ns)
    assert result["primitive"] == "validate.claim"
    assert result["creates_node"] is False
    assert result["node_primitive_type"] is None
    edge_types = {e["edge_type"] for e in result["edges"]}
    assert "validated_by" in edge_types


def test_handle_submit_contradict_assert_returns_contract() -> None:
    ns = _ns(primitive="contradict.assert", payload_json=_CONTRADICT_ASSERT_PAYLOAD, agent_id="agent-abc", epoch=1)
    result = handle_submit(ns)
    assert result["primitive"] == "contradict.assert"
    assert result["creates_node"] is False
    edge_types = {e["edge_type"] for e in result["edges"]}
    assert "contradicts" in edge_types


def test_handle_submit_link_claim_returns_contract() -> None:
    ns = _ns(primitive="link.claim", payload_json=_LINK_CLAIM_PAYLOAD, agent_id="agent-abc", epoch=1)
    result = handle_submit(ns)
    assert result["primitive"] == "link.claim"
    assert result["creates_node"] is False
    edge_types = {e["edge_type"] for e in result["edges"]}
    assert "cites" in edge_types


def test_handle_submit_refute_claim_returns_contract() -> None:
    ns = _ns(primitive="refute.claim", payload_json=_REFUTE_CLAIM_PAYLOAD, agent_id="agent-abc", epoch=1)
    result = handle_submit(ns)
    assert result["primitive"] == "refute.claim"
    assert result["creates_node"] is False
    edge_types = {e["edge_type"] for e in result["edges"]}
    assert "refuted_by" in edge_types
    assert "supported_by" in edge_types


def test_handle_submit_revise_assert_returns_contract() -> None:
    ns = _ns(primitive="revise.assert", payload_json=_REVISE_ASSERT_PAYLOAD, agent_id="agent-abc", epoch=1)
    result = handle_submit(ns)
    assert result["primitive"] == "revise.assert"
    assert result["creates_node"] is True
    assert result["node_primitive_type"] == "observation"
    edge_types = {e["edge_type"] for e in result["edges"]}
    assert "asserted_by" in edge_types
    assert "revision_of" in edge_types
    assert "revised_by" in edge_types


# ---------------------------------------------------------------------------
# 9. commit.epoch rejection
# ---------------------------------------------------------------------------


def test_handle_submit_commit_epoch_rejected() -> None:
    ns = _ns(
        primitive="commit.epoch",
        payload_json=json.dumps({"epoch_id": "epoch-1"}),
        agent_id="agent-abc",
        epoch=1,
    )
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "commit_epoch_agent_submission_rejected"


# ---------------------------------------------------------------------------
# 10. Malformed envelope rejection
# ---------------------------------------------------------------------------


def test_handle_submit_unknown_primitive_rejected() -> None:
    ns = _ns(
        primitive="nonexistent.primitive",
        payload_json=json.dumps({}),
        agent_id="agent-abc",
        epoch=1,
    )
    with pytest.raises(SubmitCommandError):
        handle_submit(ns)


def test_handle_submit_missing_primitive_raises() -> None:
    ns = _ns(primitive=None, payload_json=json.dumps({}), agent_id="agent-abc", epoch=1)
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_primitive_missing"


def test_handle_submit_missing_agent_id_raises() -> None:
    ns = _ns(primitive="assert.truth", payload_json=_ASSERT_TRUTH_PAYLOAD, agent_id=None, epoch=1)
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_agent_id_missing"


def test_handle_submit_invalid_epoch_raises() -> None:
    ns = _ns(primitive="assert.truth", payload_json=_ASSERT_TRUTH_PAYLOAD, agent_id="agent-abc", epoch=-1)
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_epoch_invalid"


def test_handle_submit_payload_ambiguous_raises(tmp_path: Path) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(_ASSERT_TRUTH_PAYLOAD, encoding="utf-8")
    ns = _ns(
        primitive="assert.truth",
        payload_json=_ASSERT_TRUTH_PAYLOAD,
        payload_file=str(payload_file),
        agent_id="agent-abc",
        epoch=1,
    )
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_payload_ambiguous"


def test_handle_submit_payload_file_not_found_raises() -> None:
    ns = _ns(
        primitive="assert.truth",
        payload_file="/tmp/nonexistent_ilc_payload_file_874.json",
        agent_id="agent-abc",
        epoch=1,
    )
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_payload_file_not_found"


def test_handle_submit_payload_file_valid_path(tmp_path: Path) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(_VALIDATE_CLAIM_PAYLOAD, encoding="utf-8")
    ns = _ns(
        primitive="validate.claim",
        payload_file=str(payload_file),
        agent_id="agent-abc",
        epoch=2,
    )
    result = handle_submit(ns)
    assert result["primitive"] == "validate.claim"
    assert result["creates_node"] is False


# ---------------------------------------------------------------------------
# 11. main.py structural checks
# ---------------------------------------------------------------------------


def test_main_py_submit_command_in_operational_commands() -> None:
    from ilc_core.cli.main import OPERATIONAL_COMMANDS

    assert "submit" in OPERATIONAL_COMMANDS


def test_main_py_submit_wired_correctly() -> None:
    text = _read(MAIN_PY_PATH)
    assert 'command == "submit"' in text
    assert '"submit"' in text and "submit_parser" in text
    assert "--primitive" in text
    assert "--payload-json" in text
    assert "--payload-file" in text
    assert "--agent-id" in text
    assert "handle_submit" in text
    assert "SubmitCommandError" in text
    # graph-state exempt set must include "submit" or submit must not mutate graph
    # The exempt set check — submit is in OPERATIONAL_COMMANDS and skips graph state
    assert '"submit"' not in text.split('"query", "verify", "bundle", "agent", "node"')[0].rsplit("not in", 1)[-1]


# ---------------------------------------------------------------------------
# 12. Subprocess integration — no graph-state mutation
# ---------------------------------------------------------------------------


def test_submit_assert_truth_via_subprocess_does_not_mutate_graph_state(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    result = _run_cli(
        "submit",
        "--primitive", "assert.truth",
        "--payload-json", _ASSERT_TRUTH_PAYLOAD,
        "--agent-id", "agent-test-874",
        "--epoch", "1",
        graph_path=graph_path,
    )
    # submit should return exit code 0
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["command"] == "submit"
    assert payload["data"]["primitive"] == "assert.truth"
    assert payload["data"]["creates_node"] is True
    # submit command DOES call _ensure_local_graph_state (it's not in the exempt set)
    # so graph.json WILL be created — verify it is not polluted with node data
    if graph_path.exists():
        state = json.loads(graph_path.read_text())
        assert isinstance(state, dict)
        # graph persistence is deferred — no nodes added
        assert state.get("nodes") in ([], None, []) or "nodes" not in state or state["nodes"] == []


def test_submit_commit_epoch_via_subprocess_returns_error(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    result = _run_cli(
        "submit",
        "--primitive", "commit.epoch",
        "--payload-json", json.dumps({"epoch_id": "epoch-1"}),
        "--agent-id", "agent-test-874",
        "--epoch", "1",
        graph_path=graph_path,
    )
    assert result.returncode == 1
    err = json.loads(result.stderr)
    assert err["ok"] is False


# ---------------------------------------------------------------------------
# 13. Phase 874 commit scope guard (post-commit)
# ---------------------------------------------------------------------------


def test_phase_874_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_874_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
    for path in changed:
        if path.startswith("ilc_core/"):
            assert path.startswith("ilc_core/cli/"), f"phase_874_ilc_core_scope_violation:{path}"
    assert "ilc_core/cli/main.py" in changed, "phase_874_main_py_wiring_missing"
    assert "ilc_core/cli/d2e_submit_cli.py" in changed, "phase_874_d2e_submit_cli_module_missing"


def test_phase_874_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_874_commit_ref()
    assert DECISION_LOG_PATH not in _changed_paths_for_commit(commit_ref)
