"""Phase 879–886 — CDL-075 truth primitive graph store tests.

Covers all 10 CDL-075 evidence checklist items:
  1. Module exists and imports
  2. TRUTH_PRIMITIVE_GRAPH_STORE_VERSION token
  3. CDL_075_DEPENDENCY token
  4. node_record_from_submission deterministic schema
  5. node_id_from_submission CIDv1 derivation
  6. TruthPrimitiveGraphStore LMDB layout
  7. write_truth_primitive_result for all six primitives
  8. Idempotency
  9. CLI integration with ILC_TRUTH_GRAPH_STORE_PATH
 10. Edge-only path for non-creating primitives
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import argparse
from pathlib import Path

import pytest

from ilc_core.epistemic.truth_primitive_graph_store import (
    CDL_074_DEPENDENCY,
    CDL_075_DEPENDENCY,
    TRUTH_PRIMITIVE_GRAPH_STORE_VERSION,
    _edge_key,
    _resolve_edges,
    node_id_from_submission,
    node_record_from_submission,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    validate_truth_primitive_submission,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore

PHASE_882_COMMIT_SUBJECT = "feat(g8): phase 877-882 cdl-075 truth primitive graph store"
MODULE_PATH = Path("ilc_core/epistemic/truth_primitive_graph_store.py")
SUBMIT_CLI_PATH = Path("ilc_core/cli/d2e_submit_cli.py")
VALID_AGENT_ID = "a" * 96
CLI_AGENT_ID = "b" * 96
READBACK_AGENT_ID = "c" * 96


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _envelope(primitive: str, payload: dict) -> dict:
    return {
        "v": 1,
        "primitive": primitive,
        "agent_id": VALID_AGENT_ID,
        "epoch": 3,
        "payload": payload,
        "sig": "UNSIGNED",
    }


def _result(envelope: dict):
    return validate_truth_primitive_submission(envelope)


def _assert_truth_env():
    return _envelope("assert.truth", {
        "content": {"body": "sky is blue"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    })


def _validate_claim_env():
    return _envelope("validate.claim", {
        "target_node_id": "bafy-target-node",
        "confidence": "0.90",
        "evidence_summary": "direct observation confirms claim",
    })


def _contradict_assert_env():
    return _envelope("contradict.assert", {
        "node_a_id": "bafy-node-a",
        "node_b_id": "bafy-node-b",
        "contradiction_scope": "logical",
        "rationale": "cannot both be true simultaneously",
    })


def _link_claim_env():
    return _envelope("link.claim", {
        "source_node_id": "bafy-src",
        "target_node_id": "bafy-tgt",
        "link_type": "elaborates",
        "link_rationale": "source elaborates target with additional detail",
    })


_REFUTATION_CRITERION = {
    "claim": "hypothesis is falsifiable",
    "evidence_type": "empirical",
    "scope_boundary": "controlled experiment",
    "claim_form": "falsifiable_positive",
    "has_falsifiable_test": True,
}


def _refute_claim_env():
    return _envelope("refute.claim", {
        "target_node_id": "bafy-claim-to-refute",
        "refutation_criterion": _REFUTATION_CRITERION,
        "evidence_node_ids": ["bafy-ev-1", "bafy-ev-2"],
    })


def _revise_assert_env():
    return _envelope("revise.assert", {
        "source_node_id": "bafy-original",
        "revised_content": {"primitive_type": "observation", "body": "revised body"},
        "revision_rationale": "correcting measurement error from prior epoch",
    })


def _run_cli_submit(*args: str, graph_path: Path, store_path: str | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    if store_path:
        env["ILC_TRUTH_GRAPH_STORE_PATH"] = store_path
    else:
        env.pop("ILC_TRUTH_GRAPH_STORE_PATH", None)
    return subprocess.run(
        ["python3", "-m", "ilc_core.cli.main", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


# ---------------------------------------------------------------------------
# Evidence item 1: Module exists and imports
# ---------------------------------------------------------------------------


def test_graph_store_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_graph_store_module_imports_cleanly() -> None:
    # All symbols imported at top of this file without error — implicit test.
    assert TRUTH_PRIMITIVE_GRAPH_STORE_VERSION is not None


# ---------------------------------------------------------------------------
# Evidence item 2: TRUTH_PRIMITIVE_GRAPH_STORE_VERSION token
# ---------------------------------------------------------------------------


def test_graph_store_version_token_correct() -> None:
    assert TRUTH_PRIMITIVE_GRAPH_STORE_VERSION == "truth_primitive_graph_store_880.v0.1"


# ---------------------------------------------------------------------------
# Evidence item 3: CDL_075_DEPENDENCY and CDL_074_DEPENDENCY tokens
# ---------------------------------------------------------------------------


def test_cdl_075_dependency_token_correct() -> None:
    assert CDL_075_DEPENDENCY == "cdl_075_truth_primitive_graph_persistence.v0.1"


def test_cdl_074_dependency_token_correct() -> None:
    assert CDL_074_DEPENDENCY == "cdl_074_truth_primitive_runtime_ratified.v0.1"


# ---------------------------------------------------------------------------
# Evidence item 4: node_record_from_submission deterministic schema
# ---------------------------------------------------------------------------


def test_node_record_assert_truth_has_required_fields() -> None:
    env = _assert_truth_env()
    result = _result(env)
    record = node_record_from_submission(env, result)
    assert set(record.keys()) == {"agent_id", "cdl_version", "epoch", "payload", "primitive", "primitive_type"}
    assert record["cdl_version"] == "cdl_075.v0.1"
    assert record["primitive"] == "assert.truth"
    assert record["primitive_type"] == "observation"
    assert record["epoch"] == 3
    assert record["agent_id"] == VALID_AGENT_ID


def test_node_record_revise_assert_has_required_fields() -> None:
    env = _revise_assert_env()
    result = _result(env)
    record = node_record_from_submission(env, result)
    assert record["primitive"] == "revise.assert"
    assert record["primitive_type"] == "observation"


def test_node_record_rejects_edge_only_primitive() -> None:
    env = _validate_claim_env()
    result = _result(env)
    with pytest.raises(ValueError, match="node_record_from_submission_invalid_primitive"):
        node_record_from_submission(env, result)


def test_node_record_is_deterministic() -> None:
    env = _assert_truth_env()
    result = _result(env)
    r1 = node_record_from_submission(env, result)
    r2 = node_record_from_submission(env, result)
    assert r1 == r2
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


# ---------------------------------------------------------------------------
# Evidence item 5: node_id_from_submission CIDv1 derivation
# ---------------------------------------------------------------------------


def test_node_id_assert_truth_is_cidv1_string() -> None:
    env = _assert_truth_env()
    result = _result(env)
    nid = node_id_from_submission(env, result)
    assert isinstance(nid, str)
    assert nid.startswith("b")
    assert len(nid) > 10


def test_node_id_is_deterministic() -> None:
    env = _assert_truth_env()
    result = _result(env)
    assert node_id_from_submission(env, result) == node_id_from_submission(env, result)


def test_node_id_different_for_different_content() -> None:
    env1 = _assert_truth_env()
    env2 = _envelope("assert.truth", {
        "content": {"body": "a different claim"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    })
    r1 = _result(env1)
    r2 = _result(env2)
    assert node_id_from_submission(env1, r1) != node_id_from_submission(env2, r2)


def test_node_id_rejects_edge_only_primitive() -> None:
    env = _validate_claim_env()
    result = _result(env)
    with pytest.raises(ValueError, match="node_record_from_submission_invalid_primitive"):
        node_id_from_submission(env, result)


# ---------------------------------------------------------------------------
# Evidence item 6: TruthPrimitiveGraphStore LMDB layout
# ---------------------------------------------------------------------------


def test_graph_store_opens_and_closes(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    store.close()


def test_graph_store_put_and_get_node(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        record = {"primitive": "assert.truth", "cdl_version": "cdl_075.v0.1", "epoch": 1}
        store.put_node_if_absent("bafy-test-node", record)
        retrieved = store.get_node("bafy-test-node")
        assert retrieved == record
    finally:
        store.close()


def test_graph_store_put_and_get_edge(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        record = {"edge_type": "asserted_by", "source": "bafy-x", "target": "agent-y", "agent_id": "agent-y", "epoch": 1}
        store.put_edge_if_absent("bafy-x:asserted_by:agent-y", record)
        retrieved = store.get_edge("bafy-x:asserted_by:agent-y")
        assert retrieved == record
    finally:
        store.close()


# ---------------------------------------------------------------------------
# Evidence item 7: write_truth_primitive_result for all six primitives
# ---------------------------------------------------------------------------


def test_write_assert_truth_creates_node_and_edges(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _assert_truth_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["primitive"] == "assert.truth"
        assert receipt["node_id"] is not None
        assert receipt["nodes_written"] == 1
        assert receipt["edges_written"] >= 1
        # Verify node is readable back
        node = store.get_node(receipt["node_id"])
        assert node is not None
        assert node["primitive"] == "assert.truth"
    finally:
        store.close()


def test_write_validate_claim_edge_only(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _validate_claim_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["node_id"] is None
        assert receipt["nodes_written"] == 0
        assert receipt["edges_written"] >= 1
    finally:
        store.close()


def test_write_contradict_assert_edge_only(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _contradict_assert_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["node_id"] is None
        assert receipt["nodes_written"] == 0
        assert receipt["edges_written"] == 1
    finally:
        store.close()


def test_write_link_claim_edge_only(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _link_claim_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["node_id"] is None
        assert receipt["edges_written"] == 1
    finally:
        store.close()


def test_write_refute_claim_edge_only_with_evidence(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _refute_claim_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["node_id"] is None
        assert receipt["nodes_written"] == 0
        # refuted_by + 2 supported_by edges (2 evidence nodes)
        assert receipt["edges_written"] == 3
    finally:
        store.close()


def test_write_revise_assert_creates_node_and_edges(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _revise_assert_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["node_id"] is not None
        assert receipt["nodes_written"] == 1
        # asserted_by + revision_of + revised_by = 3 edges
        assert receipt["edges_written"] == 3
        node = store.get_node(receipt["node_id"])
        assert node["primitive"] == "revise.assert"
    finally:
        store.close()


# ---------------------------------------------------------------------------
# Evidence item 8: Idempotency
# ---------------------------------------------------------------------------


def test_write_twice_returns_same_node_id(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _assert_truth_env()
        result = _result(env)
        r1 = write_truth_primitive_result(store, env, result)
        r2 = write_truth_primitive_result(store, env, result)
        assert r1["node_id"] == r2["node_id"]
        assert r1["nodes_written"] == 1
        assert r2["nodes_written"] == 0  # already present
        assert r2["edges_written"] == 0  # edges already present
    finally:
        store.close()


def test_put_node_if_absent_idempotent(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        record = {"k": "v"}
        assert store.put_node_if_absent("key-1", record) is True
        assert store.put_node_if_absent("key-1", record) is False
        assert store.get_node("key-1") == record
    finally:
        store.close()


# ---------------------------------------------------------------------------
# Evidence item 9: CLI integration with ILC_TRUTH_GRAPH_STORE_PATH
# ---------------------------------------------------------------------------


def test_submit_cli_with_store_path_returns_node_id(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    payload = json.dumps({
        "content": {"body": "cli test claim"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    })
    result = _run_cli_submit(
        "submit",
        "--primitive", "assert.truth",
        "--payload-json", payload,
        "--agent-id", CLI_AGENT_ID,
        "--epoch", "5",
        graph_path=graph_path,
        store_path=str(store_dir),
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["data"]["node_id"] is not None
    assert data["data"]["node_id"].startswith("b")
    assert data["data"]["graph_persistence"] == "persisted"


def test_submit_cli_without_store_path_defers_persistence(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    payload = json.dumps({
        "content": {"body": "no-store test"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    })
    result = _run_cli_submit(
        "submit",
        "--primitive", "assert.truth",
        "--payload-json", payload,
        "--agent-id", CLI_AGENT_ID,
        "--epoch", "1",
        graph_path=graph_path,
        store_path=None,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["data"]["node_id"] is None
    assert "deferred" in data["data"]["graph_persistence"]


def test_submit_cli_store_path_persisted_node_readable(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    payload = json.dumps({
        "content": {"body": "persistence readback test"},
        "primitive_type": "knowledge_claim",
        "epistemic_type": "subjective",
        "parent_node_ids": [],
    })
    result = _run_cli_submit(
        "submit",
        "--primitive", "assert.truth",
        "--payload-json", payload,
        "--agent-id", READBACK_AGENT_ID,
        "--epoch", "7",
        graph_path=graph_path,
        store_path=str(store_dir),
    )
    assert result.returncode == 0, result.stderr
    node_id = json.loads(result.stdout)["data"]["node_id"]

    # Read back from the store directly
    store = TruthPrimitiveGraphStore(store_dir)
    try:
        node = store.get_node(node_id)
        assert node is not None
        assert node["primitive"] == "assert.truth"
        assert node["agent_id"] == READBACK_AGENT_ID
        assert node["epoch"] == 7
    finally:
        store.close()


# ---------------------------------------------------------------------------
# Evidence item 10: Edge-only path correctness
# ---------------------------------------------------------------------------


def test_edge_only_writes_no_node_db_entry(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "store")
    try:
        env = _validate_claim_env()
        result = _result(env)
        receipt = write_truth_primitive_result(store, env, result)
        assert receipt["node_id"] is None
        # nodes db should be empty
        assert store.iter_nodes() == []
        # edges db should have one entry
        edges = store.iter_edges()
        assert len(edges) == 1
        assert edges[0]["edge_type"] == "validated_by"
    finally:
        store.close()


def test_edge_key_format_correct() -> None:
    record = {"source": "bafy-abc", "edge_type": "asserted_by", "target": "agent-xyz", "agent_id": "a", "epoch": 1}
    assert _edge_key(record) == "bafy-abc:asserted_by:agent-xyz"


# ---------------------------------------------------------------------------
# Phase 882 commit scope guard (post-commit)
# ---------------------------------------------------------------------------


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    r = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True, check=True, text=True,
    )
    return {line.strip() for line in r.stdout.splitlines() if line.strip()}


def _resolve_phase_882_commit_ref() -> str:
    r = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True, check=True, text=True,
    )
    for line in r.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_882_COMMIT_SUBJECT:
            changed = _changed_paths_for_commit(commit_hash)
            required = {
                "ilc_core/epistemic/truth_primitive_graph_store.py",
                "ilc_core/cli/d2e_submit_cli.py",
                "tests/test_phase_879_886_truth_primitive_graph_store.py",
            }
            if required.issubset(changed):
                return commit_hash
    raise AssertionError("phase_882_commit_not_present_in_local_history")


def test_phase_882_commit_scope_guard() -> None:
    commit_ref = _resolve_phase_882_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    for path in changed:
        if path.startswith("ilc_core/"):
            assert path.startswith("ilc_core/epistemic/") or path.startswith("ilc_core/cli/"), \
                f"phase_882_ilc_core_scope_violation:{path}"


def test_phase_882_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_882_commit_ref()
    assert "docs/specs/ilc_constitutional_decision_log_v0.1.md" not in _changed_paths_for_commit(commit_ref)
