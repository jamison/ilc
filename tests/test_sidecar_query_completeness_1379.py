from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ilc_core.graph.sidecar_query_runtime import (
    QUERY_TYPES,
    SIDECAR_QUERY_COMPLETENESS_TOKEN,
    SidecarQuery,
    execute_sidecar_query,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/graph/sidecar_query_runtime.py"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1379_g8_adr_0031_sidecar_query_completeness.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1379_adr_0031_sidecar_query_completeness_walkthrough.md"

REQUIRED_TOKENS = (
    "adr_0031_sidecar_query_runtime_completeness_phase_1379",
    "sidecar_query_no_mutation_authority_confirmed_phase_1379",
)


def _projection() -> dict[str, object]:
    return {
        "nodes": [
            {"canonical_id": "root"},
            {"canonical_id": "a"},
            {"canonical_id": "b"},
            {"canonical_id": "outside"},
        ],
        "edges": [
            {
                "canonical_id": "edge:root-a",
                "edge_type": "derives_from",
                "source": "root",
                "target": "a",
            },
            {
                "canonical_id": "edge:a-b",
                "edge_type": "supports",
                "source": "a",
                "target": "b",
            },
            {
                "canonical_id": "edge:b-outside",
                "edge_type": "supports",
                "source": "b",
                "target": "outside",
            },
        ],
        "hyperedges": [
            {
                "canonical_id": "hyperedge:root-a-b",
                "hyperedge_type": "triad",
                "members": ["root", "a", "b"],
            },
            {
                "canonical_id": "hyperedge:outside",
                "hyperedge_type": "external",
                "members": ["root", "outside"],
            },
        ],
        "metrics": {
            "degree_by_node": {"root": 1, "a": 2, "b": 2, "outside": 1},
            "edge_count": 3,
            "hyperedge_count": 2,
            "hyperedge_order_by_id": {
                "hyperedge:outside": 2,
                "hyperedge:root-a-b": 3,
            },
            "node_count": 4,
        },
    }


def _query_kwargs(query_type: str) -> dict[str, object]:
    if query_type == "ego_graph":
        return {"root_id": "a", "hops": 1}
    if query_type == "centrality_metrics":
        return {"top_k": 2}
    if query_type == "convergence_trace":
        return {"node_ids": ("a", "b")}
    raise AssertionError(f"unexpected query type in test fixture: {query_type}")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1379_tokens_are_recorded_in_prompt_runtime_and_frontier_docs() -> None:
    combined = "\n".join(
        _read(path)
        for path in (
            PROMPT,
            RUNTIME,
            STATUS,
            PLANNING,
            WALKTHROUGH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in combined
    assert SIDECAR_QUERY_COMPLETENESS_TOKEN == REQUIRED_TOKENS[0]


def test_phase_1379_runtime_source_has_no_not_implemented_error_stub() -> None:
    source = _read(RUNTIME)

    assert "NotImplementedError" not in source
    assert "not_yet_implemented" not in source
    assert "sidecar_query_dispatch_incomplete" in source


@pytest.mark.parametrize("query_type", sorted(QUERY_TYPES))
def test_phase_1379_all_locked_query_types_execute_without_stub(query_type: str) -> None:
    result = execute_sidecar_query(
        query_type=query_type,
        projection=_projection(),
        **_query_kwargs(query_type),
    )

    assert result["query_type"] == query_type


@pytest.mark.parametrize("query_type", sorted(QUERY_TYPES))
def test_phase_1379_sidecar_query_object_dispatch_executes_without_stub(query_type: str) -> None:
    kwargs = _query_kwargs(query_type)
    query = SidecarQuery(
        query_type=query_type,
        root_id=kwargs.get("root_id"),
        hops=kwargs.get("hops", 1),
        node_ids=tuple(kwargs.get("node_ids", ())),
        top_k=kwargs.get("top_k"),
    )

    result = execute_sidecar_query(
        projection=_projection(),
        query=query,
    )

    assert result["query_type"] == query_type


def test_phase_1379_unsupported_query_types_still_fail_closed() -> None:
    with pytest.raises(ValueError, match="sidecar_query_type_unsupported"):
        execute_sidecar_query(
            query_type="subgraph_homomorphism_public_serving",
            projection=_projection(),
        )


def test_phase_1379_ego_graph_preserves_adr0031_intra_response_edges() -> None:
    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=_projection(),
        root_id="a",
        hops=1,
    )

    returned_node_ids = {node["canonical_id"] for node in result["nodes"]}
    returned_edge_ids = {edge["canonical_id"] for edge in result["edges"]}
    returned_hyperedge_ids = {hyperedge["canonical_id"] for hyperedge in result["hyperedges"]}

    assert returned_node_ids == {"root", "a", "b"}
    assert returned_edge_ids == {"edge:root-a", "edge:a-b"}
    assert "edge:b-outside" not in returned_edge_ids
    assert returned_hyperedge_ids == {"hyperedge:root-a-b"}
    assert "hyperedge:outside" not in returned_hyperedge_ids


def test_phase_1379_no_sidecar_mutation_or_serving_authority_added() -> None:
    source = _read(RUNTIME)
    tree = ast.parse(source)
    forbidden_import_roots = {
        "aiohttp",
        "fastapi",
        "httpx",
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
