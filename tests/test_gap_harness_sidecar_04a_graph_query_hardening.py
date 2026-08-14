# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only graph sidecar query hardening tests for GAP-HARNESS-SIDECAR-04a."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ilc_core.graph.sidecar_query_runtime import (
    compute_local_novelty_score,
    lookup_submission_receipt,
    rank_nodes_by_reuse_centrality,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/graph/sidecar_query_runtime.py"
CLI = ROOT / "ilc_core/cli/main.py"
QUERY_SCHEMA_VERSION = "299.v0.1"


def _canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _graph_state() -> dict[str, Any]:
    fields = {"body": "existing node", "claim_id": "claim-1", "topic": "sidecar"}
    return {
        "edges": [
            {"source": "node-a", "target": "node-b", "edge_type": "supports"},
            {"source": "node-c", "target": "node-b", "edge_type": "reuses"},
            {"source": "node-b", "target": "node-c", "edge_type": "revises"},
        ],
        "nodes": [
            {
                "fields": fields,
                "node_id": "node-a",
                "node_type": "claim",
                "receipt_token": "receipt-node-a",
                "status": "persisted",
            },
            {
                "content_hash": _canonical_hash(fields),
                "node_id": "node-b",
                "node_type": "evidence",
                "status": "persisted",
            },
            {
                "fields": {"body": "different", "claim_id": "claim-1", "topic": "sidecar"},
                "node_id": "node-c",
                "node_type": "revision",
            },
        ],
        "receipts": [
            {
                "node_id": "node-r",
                "receipt": {"receipt_token": "receipt-nested"},
                "status": "accepted",
            }
        ],
    }


def test_compute_local_novelty_score_exact_duplicate_by_declared_hash() -> None:
    result = compute_local_novelty_score(
        {"body": "existing node", "claim_id": "claim-1", "topic": "sidecar"},
        _graph_state(),
    )

    assert result == {
        "advisory": True,
        "exact_duplicate_found": True,
        "near_duplicate_count": 0,
        "novelty_score": 0.0,
    }


def test_compute_local_novelty_score_near_duplicate_is_partial() -> None:
    result = compute_local_novelty_score(
        {"body": "different enough", "claim_id": "claim-1", "topic": "sidecar"},
        _graph_state(),
    )

    assert result["advisory"] is True
    assert result["exact_duplicate_found"] is False
    assert result["near_duplicate_count"] == 2
    assert result["novelty_score"] == pytest.approx(1 / 3)


def test_compute_local_novelty_score_empty_graph_is_fully_novel() -> None:
    result = compute_local_novelty_score({"claim_id": "new"}, {"nodes": []})

    assert result["advisory"] is True
    assert result["exact_duplicate_found"] is False
    assert result["near_duplicate_count"] == 0
    assert result["novelty_score"] == 1.0


def test_compute_local_novelty_score_malformed_candidate_returns_unknown() -> None:
    result = compute_local_novelty_score({"bad": object()}, _graph_state())

    assert result["advisory"] is True
    assert result["advisory_note"] == "novelty_candidate_fields_not_canonical_json"
    assert result["exact_duplicate_found"] is False
    assert result["near_duplicate_count"] == 0
    assert result["novelty_score"] == 0.5


def test_compute_local_novelty_score_non_string_key_returns_unknown() -> None:
    result = compute_local_novelty_score({1: "bad-key"}, _graph_state())

    assert result["advisory"] is True
    assert result["advisory_note"] == "novelty_candidate_fields_not_canonical_json"
    assert result["novelty_score"] == 0.5


def test_compute_local_novelty_score_malformed_graph_state_is_empty_projection() -> None:
    result = compute_local_novelty_score({"claim_id": "new"}, "not-a-graph")  # type: ignore[arg-type]

    assert result["advisory"] is True
    assert result["exact_duplicate_found"] is False
    assert result["near_duplicate_count"] == 0
    assert result["novelty_score"] == 1.0


def test_rank_nodes_by_reuse_centrality_sorts_by_in_degree_then_node_id() -> None:
    result = rank_nodes_by_reuse_centrality(_graph_state(), top_n=3)

    assert result == [
        {"in_degree": 2, "node_id": "node-b", "node_type": "evidence"},
        {"in_degree": 1, "node_id": "node-c", "node_type": "revision"},
        {"in_degree": 0, "node_id": "node-a", "node_type": "claim"},
    ]


def test_rank_nodes_by_reuse_centrality_empty_graph_returns_empty() -> None:
    assert rank_nodes_by_reuse_centrality({"nodes": [], "edges": []}) == []


def test_rank_nodes_by_reuse_centrality_malformed_graph_state_returns_empty() -> None:
    assert rank_nodes_by_reuse_centrality("not-a-graph") == []  # type: ignore[arg-type]


def test_rank_nodes_by_reuse_centrality_invalid_top_n_fails_closed() -> None:
    with pytest.raises(ValueError, match="reuse_centrality_top_n_invalid"):
        rank_nodes_by_reuse_centrality(_graph_state(), top_n=0)


def test_lookup_submission_receipt_found_in_node_record() -> None:
    result = lookup_submission_receipt("receipt-node-a", _graph_state())

    assert result["found"] is True
    assert result["node_id"] == "node-a"
    assert result["status"] == "persisted"
    assert result["fields"]["receipt_token"] == "receipt-node-a"


def test_lookup_submission_receipt_found_in_nested_receipt_record() -> None:
    result = lookup_submission_receipt("receipt-nested", _graph_state())

    assert result["found"] is True
    assert result["node_id"] == "node-r"
    assert result["status"] == "accepted"


def test_lookup_submission_receipt_not_found_is_deterministic() -> None:
    assert lookup_submission_receipt("missing-token", _graph_state()) == {
        "found": False,
        "receipt_token": "missing-token",
    }


def test_lookup_submission_receipt_malformed_graph_state_is_not_found() -> None:
    assert lookup_submission_receipt("receipt-node-a", "not-a-graph") == {  # type: ignore[arg-type]
        "found": False,
        "receipt_token": "receipt-node-a",
    }


def test_lookup_submission_receipt_empty_token_fails_closed() -> None:
    with pytest.raises(ValueError, match="invalid_receipt_token_empty"):
        lookup_submission_receipt("", _graph_state())


def test_cli_query_receipt_returns_json_envelope(tmp_path: Path) -> None:
    graph_state = tmp_path / "graph.json"
    graph_state.write_text(json.dumps(_graph_state(), sort_keys=True), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli",
            "--graph-state",
            str(graph_state),
            "query",
            "receipt",
            "receipt-node-a",
        ],
        cwd=ROOT,
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["meta"]["command"] == "query receipt"
    assert payload["meta"]["schema_version"] == QUERY_SCHEMA_VERSION
    assert payload["data"]["query"] == "receipt"
    assert payload["data"]["receipt"]["found"] is True
    assert payload["data"]["receipt"]["node_id"] == "node-a"


def test_sidecar_04a_runtime_has_no_mutation_or_network_surface() -> None:
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    forbidden_import_roots = {
        "aiohttp",
        "fastapi",
        "httpx",
        "lmdb",
        "requests",
        "socket",
        "starlette",
        "urllib",
    }
    forbidden_call_names = {
        "delete",
        "open",
        "patch",
        "post",
        "put",
        "remove",
        "replace",
        "rmdir",
        "unlink",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_call_names
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_call_names
        if isinstance(node, ast.FunctionDef):
            assert not node.name.startswith(("delete_", "mutate_", "serve_", "set_", "write_"))


def test_cli_query_receipt_parser_registered_without_write_surface() -> None:
    source = CLI.read_text(encoding="utf-8")

    assert "query_subparsers.add_parser" in source
    assert '"receipt"' in source
    assert "lookup_submission_receipt" in source
    assert "write=True" not in source[source.index("def _query_receipt") : source.index("def _query_command_token")]
