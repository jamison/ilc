from __future__ import annotations

import ast
import json
from pathlib import Path

import ilc_core.graph.sidecar_query_runtime as sidecar_mod
from ilc_core.graph.agent_graph_projection_runtime import (
    build_fetch_incentive_hypergraph_slice,
)
from ilc_core.graph.sidecar_query_runtime import (
    SIDECAR_QUERY_RUNTIME_VERSION,
    SidecarQuery,
    build_sidecar_query_bundle,
    execute_sidecar_query,
    export_sidecar_query_json,
    export_sidecar_query_ndjson,
)


RUNTIME_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")
SIDECAR_SPEC_PATH = Path("docs/specs/ilc_l3_sidecar_infrastructure_spec_1237_v0.1.md")


def _real_projection() -> dict[str, object]:
    return build_fetch_incentive_hypergraph_slice()


def _node_ids(projection: dict[str, object]) -> list[str]:
    return [str(node["canonical_id"]) for node in projection["nodes"]]


def test_phase_1237_fix7_all_query_types_run_on_real_projection() -> None:
    projection = _real_projection()
    node_ids = _node_ids(projection)

    ego = execute_sidecar_query(
        query_type="ego_graph",
        projection=projection,
        root_id=node_ids[0],
    )
    centrality = execute_sidecar_query(
        query_type="centrality_metrics",
        projection=projection,
    )
    trace = execute_sidecar_query(
        query_type="convergence_trace",
        projection=projection,
        node_ids=(node_ids[0], node_ids[1]),
    )

    assert ego["query_type"] == "ego_graph"
    assert ego["node_count"] >= 1
    assert centrality["query_type"] == "centrality_metrics"
    assert centrality["node_count"] == len(node_ids)
    assert trace["query_type"] == "convergence_trace"
    assert "common_ancestors" in trace


def test_phase_1237_fix7_sidecar_query_object_runs_on_real_projection() -> None:
    projection = _real_projection()
    node_ids = _node_ids(projection)

    result = execute_sidecar_query(
        projection=projection,
        query=SidecarQuery(query_type="ego_graph", root_id=node_ids[0], hops=1),
    )

    assert result["query_type"] == "ego_graph"
    assert result["root_id"] == node_ids[0]


def test_phase_1237_fix7_bundle_exports_deterministic_json_and_ndjson() -> None:
    projection = _real_projection()
    node_ids = _node_ids(projection)
    results = [
        execute_sidecar_query(
            query_type="ego_graph",
            projection=projection,
            root_id=node_ids[0],
        ),
        execute_sidecar_query(
            query_type="centrality_metrics",
            projection=projection,
        ),
    ]
    bundle = build_sidecar_query_bundle(projection=projection, query_results=results)

    json_1 = export_sidecar_query_json(bundle)
    json_2 = export_sidecar_query_json(bundle)
    ndjson_1 = export_sidecar_query_ndjson(results)
    ndjson_2 = export_sidecar_query_ndjson(results)

    assert json_1 == json_2
    assert ndjson_1 == ndjson_2
    parsed = json.loads(json_1)
    assert parsed["bundle_version"] == SIDECAR_QUERY_RUNTIME_VERSION
    assert parsed["query_count"] == 2


def test_phase_1237_fix7_smoke_path_has_no_network_dependency() -> None:
    tree = ast.parse(RUNTIME_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {"aiohttp", "http", "requests", "socket", "urllib"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_imports
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports


def test_phase_1237_fix7_bundle_has_no_wall_clock_field() -> None:
    bundle = build_sidecar_query_bundle(projection=_real_projection(), query_results=[])

    assert bundle["wall_clock_time_included"] is False
    for key, value in bundle.items():
        if "time" in key and key != "wall_clock_time_included":
            assert value is False or value == 0


def test_phase_1237_fix7_sidecar_excluded_from_protocol_participation() -> None:
    spec = SIDECAR_SPEC_PATH.read_text(encoding="utf-8")

    assert "l3_sidecar_infrastructure_spec_committed_phase_1237" in spec
    assert "no mutation authority" in spec.lower()
    assert "no write path" in spec.lower()

    public_names = [name for name in dir(sidecar_mod) if not name.startswith("_")]
    for name in public_names:
        lowered = name.lower()
        assert "gossip" not in lowered
        assert "submit" not in lowered
        assert "write" not in lowered


def test_phase_1237_fix7_combined_sidecar_test_suite_loaded() -> None:
    assert SIDECAR_QUERY_RUNTIME_VERSION == "sidecar_query_runtime_1237.v0.1"
