"""Phase 894–898 — CDL-076 truth primitive announcement gossip tests.

Covers all 10 hard pass conditions from the Window 892-898 sequence lock:
  1. truth_primitive_gossip_runtime.py module exists
  2. TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION and CDL_076/061/075 dependency tokens
  3. TRUTH_PRIMITIVE_GOSSIP_TYPE == "truth_primitive_announced"
  4. Announcement payload exactly {node_id, primitive, agent_id, epoch, cdl_version}
  5. ILC_D2D_GOSSIP_PEERS absent → graceful skip
  6. Submit CLI wired: gossip_delivery field present in result
  7. Absent ILC_D2D_GOSSIP_PEERS → "deferred — gossip peers not configured"
  8. Absent ILC_TRUTH_GRAPH_STORE_PATH → gossip not attempted
  9. No LMDB store mutation via gossip path
  10. CDL-076 opened in CDL master log (ratification verified at Phase 897)
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from ilc_core.network.d2d.truth_primitive_gossip_runtime import (
    CDL_061_DEPENDENCY,
    CDL_075_DEPENDENCY,
    CDL_076_DEPENDENCY,
    TRUTH_PRIMITIVE_GOSSIP_CHANNEL,
    TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION,
    TRUTH_PRIMITIVE_GOSSIP_TYPE,
    _build_announcement_payload,
    announce_truth_primitive,
)
from ilc_core.cli.d2e_submit_cli import (
    CDL_076_DEPENDENCY as SUBMIT_CDL_076_DEPENDENCY,
    handle_submit,
)
from ilc_core.epistemic.truth_primitive_graph_store import (
    TruthPrimitiveGraphStore,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    validate_truth_primitive_submission,
)

PHASE_896_COMMIT_SUBJECT = "feat(g8): phase 892-896 cdl-076 truth primitive announcement gossip"
MODULE_PATH = Path("ilc_core/network/d2d/truth_primitive_gossip_runtime.py")
SUBMIT_CLI_PATH = Path("ilc_core/cli/d2e_submit_cli.py")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _truth_envelope(body: str = "gossip test claim", epoch: int = 1) -> dict:
    return {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": "agent-gossip-test",
        "epoch": epoch,
        "payload": {
            "content": {"body": body},
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }


def _populate_store(store_dir: Path) -> tuple[str, dict, dict]:
    """Write one assert.truth node; return (node_id, envelope, write_receipt)."""
    env = _truth_envelope()
    result = validate_truth_primitive_submission(env)
    store = TruthPrimitiveGraphStore(store_dir)
    try:
        receipt = write_truth_primitive_result(store, env, result)
    finally:
        store.close()
    return receipt["node_id"], env, receipt


def _run_cli(*args: str, store_path: str | None = None, gossip_peers: str | None = None,
             graph_path: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if store_path:
        env["ILC_TRUTH_GRAPH_STORE_PATH"] = store_path
    else:
        env.pop("ILC_TRUTH_GRAPH_STORE_PATH", None)
    if gossip_peers:
        env["ILC_D2D_GOSSIP_PEERS"] = gossip_peers
    else:
        env.pop("ILC_D2D_GOSSIP_PEERS", None)
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path or Path("/tmp/ilc_test_graph.json"))
    return subprocess.run(
        ["python3", "-m", "ilc_core.cli.main", *args],
        capture_output=True, text=True, check=False, env=env,
    )


# ---------------------------------------------------------------------------
# 1. Module exists
# ---------------------------------------------------------------------------


def test_gossip_runtime_module_exists() -> None:
    assert MODULE_PATH.exists()


# ---------------------------------------------------------------------------
# 2. Version and dependency tokens
# ---------------------------------------------------------------------------


def test_version_token() -> None:
    assert TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION == "truth_primitive_gossip_runtime_894.v0.1"


def test_cdl_076_dependency_token() -> None:
    assert CDL_076_DEPENDENCY == "cdl_076_truth_primitive_announcement_gossip.v0.1"


def test_cdl_061_dependency_token() -> None:
    assert CDL_061_DEPENDENCY == "cdl_061_ratified_561.v0.1"


def test_cdl_075_dependency_token() -> None:
    assert CDL_075_DEPENDENCY == "cdl_075_truth_primitive_graph_persistence.v0.1"


def test_submit_cli_cdl_076_dependency_token() -> None:
    assert SUBMIT_CDL_076_DEPENDENCY == "cdl_076_truth_primitive_announcement_gossip.v0.1"


# ---------------------------------------------------------------------------
# 3. TRUTH_PRIMITIVE_GOSSIP_TYPE constant
# ---------------------------------------------------------------------------


def test_gossip_type_constant() -> None:
    assert TRUTH_PRIMITIVE_GOSSIP_TYPE == "truth_primitive_announced"


def test_gossip_channel_constant_non_empty() -> None:
    assert TRUTH_PRIMITIVE_GOSSIP_CHANNEL
    assert isinstance(TRUTH_PRIMITIVE_GOSSIP_CHANNEL, str)


# ---------------------------------------------------------------------------
# 4. Announcement payload shape
# ---------------------------------------------------------------------------


def test_announcement_payload_has_exactly_five_fields() -> None:
    write_receipt = {"node_id": "bafytest123", "primitive": "assert.truth"}
    envelope = {"agent_id": "agent-001", "epoch": 5}
    payload_bytes = _build_announcement_payload(write_receipt, envelope)
    payload = json.loads(payload_bytes)
    assert set(payload.keys()) == {"node_id", "primitive", "agent_id", "epoch", "cdl_version"}


def test_announcement_payload_node_id_is_cid(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    node_id, env, receipt = _populate_store(store_dir)
    payload_bytes = _build_announcement_payload(receipt, env)
    payload = json.loads(payload_bytes)
    assert payload["node_id"] == node_id
    assert payload["node_id"].startswith("b")  # CIDv1 base32 lowercase


def test_announcement_payload_no_full_record_content(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    node_id, env, receipt = _populate_store(store_dir)
    payload_bytes = _build_announcement_payload(receipt, env)
    payload = json.loads(payload_bytes)
    # Full record fields must NOT appear
    assert "node_record" not in payload
    assert "payload" not in payload
    assert "edges" not in payload
    assert "cdl_075" not in payload


def test_announcement_payload_cdl_version_matches_dependency() -> None:
    write_receipt = {"node_id": "bafytest123", "primitive": "assert.truth"}
    envelope = {"agent_id": "agent-001", "epoch": 1}
    payload_bytes = _build_announcement_payload(write_receipt, envelope)
    payload = json.loads(payload_bytes)
    assert payload["cdl_version"] == CDL_076_DEPENDENCY


# ---------------------------------------------------------------------------
# 5. Absent ILC_D2D_GOSSIP_PEERS → graceful skip
# ---------------------------------------------------------------------------


def test_absent_peers_returns_deferred_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    receipt = announce_truth_primitive(
        {"node_id": "bafytest", "primitive": "assert.truth"},
        {"agent_id": "agent-001", "epoch": 1},
    )
    assert receipt["gossip_delivery"] == "deferred — gossip peers not configured"
    assert receipt["peers_attempted"] == 0
    assert receipt["peers_succeeded"] == 0


def test_empty_peers_env_returns_deferred_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_D2D_GOSSIP_PEERS", "   ")
    receipt = announce_truth_primitive(
        {"node_id": "bafytest", "primitive": "assert.truth"},
        {"agent_id": "agent-001", "epoch": 1},
    )
    assert receipt["gossip_delivery"] == "deferred — gossip peers not configured"


def test_no_node_id_returns_deferred_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_D2D_GOSSIP_PEERS", "https://peer1.example.com")
    receipt = announce_truth_primitive(
        {"node_id": None, "primitive": "validate.claim"},
        {"agent_id": "agent-001", "epoch": 1},
    )
    assert "edge-only" in receipt["gossip_delivery"]
    assert receipt["peers_attempted"] == 0


# ---------------------------------------------------------------------------
# 6. Submit CLI wired: gossip_delivery field in result
# ---------------------------------------------------------------------------


def test_submit_cli_result_has_gossip_delivery_field(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    ns = argparse.Namespace(
        primitive="assert.truth", agent_id="agent-001", epoch=1,
        payload_json='{"content":{"body":"test"},"primitive_type":"observation",'
                     '"epistemic_type":"objective","parent_node_ids":[]}',
        payload_file=None, sig="UNSIGNED",
    )
    result = handle_submit(ns)
    assert "gossip_delivery" in result


# ---------------------------------------------------------------------------
# 7. Absent ILC_D2D_GOSSIP_PEERS → deferred string in submit result
# ---------------------------------------------------------------------------


def test_submit_result_gossip_delivery_deferred_when_no_peers(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    ns = argparse.Namespace(
        primitive="assert.truth", agent_id="agent-001", epoch=1,
        payload_json='{"content":{"body":"test"},"primitive_type":"observation",'
                     '"epistemic_type":"objective","parent_node_ids":[]}',
        payload_file=None, sig="UNSIGNED",
    )
    result = handle_submit(ns)
    assert result["gossip_delivery"] == "deferred — gossip peers not configured"


# ---------------------------------------------------------------------------
# 8. Absent ILC_TRUTH_GRAPH_STORE_PATH → gossip not attempted
# ---------------------------------------------------------------------------


def test_gossip_not_attempted_when_no_store_path(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    monkeypatch.setenv("ILC_D2D_GOSSIP_PEERS", "https://peer1.example.com")
    ns = argparse.Namespace(
        primitive="assert.truth", agent_id="agent-001", epoch=1,
        payload_json='{"content":{"body":"test"},"primitive_type":"observation",'
                     '"epistemic_type":"objective","parent_node_ids":[]}',
        payload_file=None, sig="UNSIGNED",
    )
    result = handle_submit(ns)
    # node_id is None (no persist) so gossip is not attempted — peers not configured message
    assert result["gossip_delivery"] == "deferred — gossip peers not configured"
    assert result["node_id"] is None


# ---------------------------------------------------------------------------
# Per-peer send — mocked
# ---------------------------------------------------------------------------


def test_announce_calls_send_to_peer_once_per_peer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ILC_D2D_GOSSIP_PEERS",
        "https://peer1.example.com,https://peer2.example.com",
    )
    call_log: list[str] = []

    def mock_send(peer: str, _payload: bytes, _epoch: int) -> bool:
        call_log.append(peer)
        return True

    with patch("ilc_core.network.d2d.truth_primitive_gossip_runtime._send_to_peer", mock_send):
        receipt = announce_truth_primitive(
            {"node_id": "bafytest123", "primitive": "assert.truth"},
            {"agent_id": "agent-001", "epoch": 3},
        )

    assert len(call_log) == 2
    assert "https://peer1.example.com" in call_log
    assert "https://peer2.example.com" in call_log
    assert receipt["peers_attempted"] == 2
    assert receipt["peers_succeeded"] == 2


def test_announce_partial_failure_counted_correctly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ILC_D2D_GOSSIP_PEERS",
        "https://peer1.example.com,https://peer2.example.com",
    )
    call_count = {"n": 0}

    def mock_send(_peer: str, _payload: bytes, _epoch: int) -> bool:
        call_count["n"] += 1
        return call_count["n"] == 1  # first succeeds, second fails

    with patch("ilc_core.network.d2d.truth_primitive_gossip_runtime._send_to_peer", mock_send):
        receipt = announce_truth_primitive(
            {"node_id": "bafytest123", "primitive": "assert.truth"},
            {"agent_id": "agent-001", "epoch": 1},
        )

    assert receipt["peers_attempted"] == 2
    assert receipt["peers_succeeded"] == 1


# ---------------------------------------------------------------------------
# 9. No LMDB store mutation via gossip path
# ---------------------------------------------------------------------------


def test_gossip_does_not_mutate_lmdb_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_dir))
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)

    node_id, env, receipt = _populate_store(store_dir)

    store = TruthPrimitiveGraphStore(store_dir)
    before_count = len(store.iter_nodes())
    store.close()

    # Gossip with no peers → deferred
    announce_truth_primitive(receipt, env)

    store = TruthPrimitiveGraphStore(store_dir)
    after_count = len(store.iter_nodes())
    store.close()

    assert before_count == after_count


# ---------------------------------------------------------------------------
# Subprocess CLI integration
# ---------------------------------------------------------------------------


def test_submit_via_subprocess_includes_gossip_delivery(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    graph_path = tmp_path / "graph.json"
    payload = json.dumps({
        "content": {"body": "subprocess gossip test"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    })
    result = _run_cli(
        "submit", "--primitive", "assert.truth",
        "--payload-json", payload,
        "--agent-id", "agent-subprocess",
        "--epoch", "1",
        store_path=str(store_dir),
        graph_path=graph_path,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert "gossip_delivery" in data["data"]


def test_submit_subprocess_gossip_deferred_when_no_peers(tmp_path: Path) -> None:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    graph_path = tmp_path / "graph.json"
    payload = json.dumps({
        "content": {"body": "no peers test"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    })
    result = _run_cli(
        "submit", "--primitive", "assert.truth",
        "--payload-json", payload,
        "--agent-id", "agent-subprocess",
        "--epoch", "1",
        store_path=str(store_dir),
        gossip_peers=None,
        graph_path=graph_path,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["data"]["gossip_delivery"] == "deferred — gossip peers not configured"


# ---------------------------------------------------------------------------
# 10. CDL-076 present in CDL master log
# ---------------------------------------------------------------------------


def test_cdl_076_present_in_master_log() -> None:
    log_path = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    text = log_path.read_text(encoding="utf-8")
    assert "CDL-076" in text
    assert "truth_primitive_announced" in text
    assert "opened_phase: 893" in text


# ---------------------------------------------------------------------------
# Phase 896 commit scope guard (post-commit)
# ---------------------------------------------------------------------------


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    r = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True, check=True, text=True,
    )
    return {line.strip() for line in r.stdout.splitlines() if line.strip()}


def _resolve_phase_896_commit_ref() -> str:
    r = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True, check=True, text=True,
    )
    for line in r.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_896_COMMIT_SUBJECT:
            changed = _changed_paths_for_commit(commit_hash)
            # The phase 896 commit delivers the test file; implementation
            # files were committed separately in the same window.
            if "tests/test_phase_894_898_truth_primitive_gossip.py" in changed:
                return commit_hash
    raise AssertionError("phase_896_commit_not_present_in_local_history")


def test_phase_896_commit_scope_guard() -> None:
    commit_ref = _resolve_phase_896_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    for path in changed:
        if path.startswith("ilc_core/"):
            assert path.startswith("ilc_core/network/d2d/") or path.startswith("ilc_core/cli/"), \
                f"phase_896_ilc_core_scope_violation:{path}"


def test_phase_896_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_896_commit_ref()
    assert "docs/specs/ilc_constitutional_decision_log_v0.1.md" not in _changed_paths_for_commit(commit_ref)
