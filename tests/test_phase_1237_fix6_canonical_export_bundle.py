from __future__ import annotations

import ast
import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.graph.agent_graph_projection_runtime import project_graph
from ilc_core.graph.sidecar_query_runtime import (
    SIDECAR_PROJECTION_DEPENDENCY,
    SIDECAR_QUERY_RUNTIME_VERSION,
    build_sidecar_query_bundle,
    execute_sidecar_query,
    export_sidecar_query_json,
    export_sidecar_query_ndjson,
)


RUNTIME_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")


def _centrality_result_with_decimal() -> dict[str, object]:
    return {
        "degree_centrality": {"a": Decimal("0.5")},
        "flag": True,
        "query_type": "centrality_metrics",
        "top_nodes_by_degree": [
            {"degree_centrality": Decimal("0.5"), "node_id": "a"},
        ],
    }


def _projection() -> dict[str, object]:
    projection = project_graph(
        projection_type="repo_hypergraph",
        nodes=[
            {"canonical_id": "genesis:root"},
            {"canonical_id": "a"},
            {"canonical_id": "b"},
        ],
        edges=[
            {
                "edge_type": "t",
                "source": "genesis:root",
                "target": "a",
            },
            {
                "edge_type": "t",
                "source": "a",
                "target": "b",
            },
        ],
    )
    projection["metadata"]["projection_id"] = "fixture"
    return projection


def test_phase_1237_fix6_json_export_is_deterministic_and_canonical() -> None:
    result = {"query_type": "ego_graph", "z": 1, "a": {"b": 2}}

    first = export_sidecar_query_json(result)
    second = export_sidecar_query_json(result)

    assert first == second
    assert first == '{"a":{"b":2},"query_type":"ego_graph","z":1}'


def test_phase_1237_fix6_decimal_metrics_serialize_as_strings() -> None:
    payload = export_sidecar_query_json(_centrality_result_with_decimal())
    decoded = json.loads(payload)

    assert decoded["degree_centrality"]["a"] == "0.5"
    assert decoded["top_nodes_by_degree"][0]["degree_centrality"] == "0.5"
    assert '"0.5"' in payload
    assert ':0.5' not in payload


def test_phase_1237_fix6_float_values_are_rejected_recursively() -> None:
    with pytest.raises(ValueError, match="sidecar_export_float_values_forbidden"):
        export_sidecar_query_json({"query_type": "x", "nested": [{"score": 0.5}]})


@pytest.mark.parametrize("value", (float("nan"), float("inf"), float("-inf")))
def test_phase_1237_fix6_non_finite_float_values_rejected_before_json(
    value: float,
) -> None:
    with pytest.raises(ValueError, match="sidecar_export_float_values_forbidden"):
        export_sidecar_query_json({"query_type": "x", "score": value})


@pytest.mark.parametrize("value", (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")))
def test_phase_1237_fix6_non_finite_decimal_values_are_rejected(
    value: Decimal,
) -> None:
    with pytest.raises(ValueError, match="sidecar_export_decimal_must_be_finite"):
        export_sidecar_query_json({"query_type": "x", "score": value})


def test_phase_1237_fix6_max_bytes_enforced() -> None:
    with pytest.raises(ValueError, match="sidecar_export_size_exceeded"):
        export_sidecar_query_json({"query_type": "ego_graph"}, max_bytes=1)


@pytest.mark.parametrize("max_bytes", (True, "10"))
def test_phase_1237_fix6_max_bytes_must_be_strict_int(max_bytes: object) -> None:
    with pytest.raises(ValueError, match="sidecar_export_max_bytes_must_be_int"):
        export_sidecar_query_json({"query_type": "ego_graph"}, max_bytes=max_bytes)


def test_phase_1237_fix6_max_bytes_must_be_non_negative() -> None:
    with pytest.raises(ValueError, match="sidecar_export_max_bytes_must_be_non_negative"):
        export_sidecar_query_json({"query_type": "ego_graph"}, max_bytes=-1)


def test_phase_1237_fix6_ndjson_export_is_deterministic() -> None:
    results = [
        {"query_type": "ego_graph", "z": 1},
        {"query_type": "convergence_trace", "a": 2},
    ]

    first = export_sidecar_query_ndjson(results)
    second = export_sidecar_query_ndjson(results)

    assert first == second
    assert first.splitlines() == [
        '{"query_type":"ego_graph","z":1}',
        '{"a":2,"query_type":"convergence_trace"}',
    ]


def test_phase_1237_fix6_ndjson_total_size_is_bounded() -> None:
    with pytest.raises(ValueError, match="sidecar_export_size_exceeded"):
        export_sidecar_query_ndjson(
            [
                {"query_type": "ego_graph", "payload": "abc"},
                {"query_type": "centrality_metrics", "payload": "def"},
            ],
            max_bytes=70,
        )


def test_phase_1237_fix6_bundle_has_version_dependency_and_metadata() -> None:
    projection = _projection()
    result = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id="a",
    )

    bundle = build_sidecar_query_bundle(
        projection=projection,
        query_results=[result],
    )

    assert bundle["bundle_version"] == SIDECAR_QUERY_RUNTIME_VERSION
    assert bundle["projection_dependency"] == SIDECAR_PROJECTION_DEPENDENCY
    assert bundle["projection_metadata"]["projection_id"] == "fixture"
    assert bundle["query_count"] == 1
    assert bundle["query_results"] == [result]


def test_phase_1237_fix6_bundle_has_no_wall_clock_field() -> None:
    bundle = build_sidecar_query_bundle(
        projection={"metadata": {}},
        query_results=[],
    )

    assert bundle["wall_clock_time_included"] is False
    time_like_keys = [
        key
        for key, value in bundle.items()
        if "time" in key and key != "wall_clock_time_included" and value is not False
    ]
    assert time_like_keys == []


def test_phase_1237_fix6_bundle_round_trips_through_json_loads() -> None:
    projection = _projection()
    centrality = execute_sidecar_query(
        query_type="centrality_metrics",
        projection=projection,
    )
    bundle = build_sidecar_query_bundle(
        projection=projection,
        query_results=[centrality],
    )

    payload = export_sidecar_query_json(bundle)
    decoded = json.loads(payload)

    assert decoded["query_count"] == 1
    assert decoded["query_results"][0]["query_type"] == "centrality_metrics"
    assert isinstance(
        decoded["query_results"][0]["top_nodes_by_degree"][0]["degree_centrality"],
        str,
    )


def test_phase_1237_fix6_source_json_dumps_calls_are_canonical() -> None:
    tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
    json_dumps_calls = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "json"
            and node.func.attr == "dumps"
        ):
            json_dumps_calls.append(node)

    assert json_dumps_calls
    for call in json_dumps_calls:
        keywords = {keyword.arg: keyword.value for keyword in call.keywords}
        assert isinstance(keywords["sort_keys"], ast.Constant)
        assert keywords["sort_keys"].value is True
        assert isinstance(keywords["allow_nan"], ast.Constant)
        assert keywords["allow_nan"].value is False


def test_phase_1237_fix6_source_has_no_filesystem_or_network_io() -> None:
    tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {"aiohttp", "requests", "urllib"}
    forbidden_calls = {"open"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_imports
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in forbidden_calls
