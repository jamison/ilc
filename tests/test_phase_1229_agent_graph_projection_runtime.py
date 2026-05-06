from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.graph import EpistemicGraph
from ilc_core.graph.agent_graph_projection_runtime import (
    AGENT_GRAPH_PROJECTION_RUNTIME_VERSION,
    FETCH_INCENTIVE_PROJECTION_TOKEN,
    ProjectionBounds,
    build_fetch_incentive_hypergraph_slice,
    export_projection_json,
    export_projection_ndjson,
    path_to_genesis,
    project_graph,
)


RUNTIME_PATH = Path("ilc_core/graph/agent_graph_projection_runtime.py")


def _sample_projection():
    return project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "node:b", "node_class": "claim", "phase": 2},
            {"canonical_id": "genesis:root", "node_class": "genesis", "phase": 1},
            {"canonical_id": "node:a", "node_class": "claim", "phase": 1},
        ],
        edges=[
            {"source": "node:a", "target": "node:b", "edge_type": "derives_from"},
            {"source": "genesis:root", "target": "node:a", "edge_type": "derives_from"},
        ],
        hyperedges=[
            {
                "canonical_id": "hyperedge:ab",
                "members": ["node:b", "node:a"],
                "hyperedge_type": "cohort",
            }
        ],
    )


def test_phase_1229_runtime_version_token():
    assert AGENT_GRAPH_PROJECTION_RUNTIME_VERSION == "agent_graph_projection_runtime_1229.v0.1"


def test_existing_graph_import_contract_preserved():
    graph = EpistemicGraph()
    assert graph.edge_count() == 0


def test_projection_outputs_are_sorted_and_canonical_json_is_stable():
    projection = _sample_projection()
    assert [node["canonical_id"] for node in projection["nodes"]] == [
        "genesis:root",
        "node:a",
        "node:b",
    ]
    first = export_projection_json(projection)
    second = export_projection_json(projection)
    assert first == second
    assert '"runtime_version":"agent_graph_projection_runtime_1229.v0.1"' in first


def test_projection_rejects_float_values():
    with pytest.raises(ValueError, match="graph_projection_float_values_forbidden"):
        project_graph(
            projection_type="economic_flow_graph",
            nodes=[{"canonical_id": "node:a", "weight": 0.1}],
        )


def test_projection_decimal_values_are_finite_and_serialized_as_strings():
    projection = project_graph(
        projection_type="economic_flow_graph",
        nodes=[{"canonical_id": "node:a", "ecu": Decimal("1.25")}],
    )
    assert projection["nodes"][0]["ecu"] == "1.25"
    with pytest.raises(ValueError, match="graph_projection_decimal_must_be_finite"):
        project_graph(
            projection_type="economic_flow_graph",
            nodes=[{"canonical_id": "node:a", "ecu": Decimal("NaN")}],
        )


def test_projection_enforces_hard_count_bounds_before_export():
    with pytest.raises(ValueError, match="graph_projection_node_count_exceeded"):
        project_graph(
            projection_type="repo_hypergraph",
            nodes=[{"canonical_id": "node:a"}, {"canonical_id": "node:b"}],
            bounds=ProjectionBounds(max_nodes=1),
        )


def test_projection_filters_nodes_and_edges_deterministically():
    projection = project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "node:a", "node_class": "claim"},
            {"canonical_id": "node:b", "node_class": "claim"},
            {"canonical_id": "node:c", "node_class": "task"},
        ],
        edges=[
            {"source": "node:a", "target": "node:b", "edge_type": "depends_on"},
            {"source": "node:b", "target": "node:c", "edge_type": "depends_on"},
        ],
        filters={"node_class": "claim"},
    )
    assert [node["canonical_id"] for node in projection["nodes"]] == ["node:a", "node:b"]
    assert len(projection["edges"]) == 1
    assert projection["edges"][0]["source"] == "node:a"


def test_projection_ndjson_is_deterministic_and_bounded():
    projection = _sample_projection()
    ndjson = export_projection_ndjson(projection)
    assert ndjson == export_projection_ndjson(projection)
    assert ndjson.splitlines()[0].startswith('{"kind":"metadata"')
    with pytest.raises(ValueError, match="graph_projection_export_size_exceeded"):
        export_projection_ndjson(projection, max_bytes=10)


def test_path_to_genesis_uses_projection_edges():
    projection = _sample_projection()
    assert path_to_genesis(projection, "node:b", max_depth=4) == [
        "node:b",
        "node:a",
        "genesis:root",
    ]


def test_fetch_incentive_hypergraph_slice_resolves_phase_1228_token():
    projection = build_fetch_incentive_hypergraph_slice()
    ids = {node["canonical_id"] for node in projection["nodes"]}
    assert {"cdl:060", "cdl:077", "cdl:078", "cdl:087"}.issubset(ids)
    assert projection["metadata"]["phase_1228_token_resolved"] == FETCH_INCENTIVE_PROJECTION_TOKEN
    assert projection["metadata"]["serving_peer_vs_served_graph_node_distinguished"] is True
    assert "edge:serving_peer_identity" in ids
    assert "edge:served_graph_node_centrality" in ids


def test_unsupported_projection_type_rejected():
    with pytest.raises(ValueError, match="projection_type_unsupported"):
        project_graph(projection_type="star_map_visualization", nodes=[])


def test_runtime_source_has_no_random_assert_or_wall_clock_protocol_calls():
    tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        assert not isinstance(node, ast.Assert)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imported = [alias.name for alias in node.names]
            assert "random" not in imported
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"now", "time"}


def test_runtime_source_json_dumps_calls_are_canonical():
    tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
    dumps_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "dumps"
    ]
    assert dumps_calls
    for call in dumps_calls:
        kwargs = {kw.arg: kw.value for kw in call.keywords}
        assert "sort_keys" in kwargs
        assert isinstance(kwargs["sort_keys"], ast.Constant)
        assert kwargs["sort_keys"].value is True
        assert "allow_nan" in kwargs
        assert isinstance(kwargs["allow_nan"], ast.Constant)
        assert kwargs["allow_nan"].value is False
