from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ilc_core.graph.agent_graph_projection_runtime import (
    AGENT_GRAPH_PROJECTION_RUNTIME_VERSION,
)
from ilc_core.graph.sidecar_query_runtime import (
    QUERY_TYPES,
    SIDECAR_PROJECTION_DEPENDENCY,
    SIDECAR_QUERY_RUNTIME_VERSION,
    SidecarQuery,
    SidecarQueryBounds,
    execute_sidecar_query,
)


RUNTIME_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")


def test_phase_1237_fix1_version_and_dependency_tokens() -> None:
    assert SIDECAR_QUERY_RUNTIME_VERSION == "sidecar_query_runtime_1237.v0.1"
    assert SIDECAR_PROJECTION_DEPENDENCY == AGENT_GRAPH_PROJECTION_RUNTIME_VERSION
    assert SIDECAR_PROJECTION_DEPENDENCY == "agent_graph_projection_runtime_1229.v0.1"


def test_phase_1237_fix1_query_types_are_locked() -> None:
    assert QUERY_TYPES == frozenset(
        {
            "ego_graph",
            "centrality_metrics",
            "convergence_trace",
        }
    )


def test_phase_1237_fix5_sidecar_query_dataclass_defaults_are_locked() -> None:
    query = SidecarQuery(query_type="ego_graph")

    assert query.query_type == "ego_graph"
    assert query.root_id is None
    assert query.hops == 1
    assert query.node_ids == ()
    assert query.genesis_id == "genesis:root"
    assert query.top_k is None
    assert query.bounds is None


@pytest.mark.parametrize("field_name", ("max_hops", "max_nodes", "max_results"))
def test_phase_1237_fix1_bounds_reject_bool(field_name: str) -> None:
    values = {
        "max_hops": 4,
        "max_nodes": 200,
        "max_results": 100,
    }
    values[field_name] = True
    with pytest.raises(ValueError, match=f"{field_name}_must_be_positive_int"):
        SidecarQueryBounds(**values).validate()


@pytest.mark.parametrize("field_name", ("max_hops", "max_nodes", "max_results"))
def test_phase_1237_fix1_bounds_reject_zero(field_name: str) -> None:
    values = {
        "max_hops": 4,
        "max_nodes": 200,
        "max_results": 100,
    }
    values[field_name] = 0
    with pytest.raises(ValueError, match=f"{field_name}_must_be_positive_int"):
        SidecarQueryBounds(**values).validate()


@pytest.mark.parametrize("field_name", ("max_hops", "max_nodes", "max_results"))
def test_phase_1237_fix1_bounds_reject_negative(field_name: str) -> None:
    values = {
        "max_hops": 4,
        "max_nodes": 200,
        "max_results": 100,
    }
    values[field_name] = -1
    with pytest.raises(ValueError, match=f"{field_name}_must_be_positive_int"):
        SidecarQueryBounds(**values).validate()


def test_phase_1237_fix1_unsupported_query_type_rejected() -> None:
    with pytest.raises(ValueError, match="sidecar_query_type_unsupported"):
        execute_sidecar_query(query_type="unsupported", projection={})


def test_phase_1237_fix4_all_supported_query_types_have_dispatch_arms() -> None:
    calls = (
        {
            "query_type": "ego_graph",
            "projection": {"nodes": [{"canonical_id": "root"}], "edges": []},
            "root_id": "root",
        },
        {
            "query_type": "centrality_metrics",
            "projection": {"nodes": [], "edges": [], "metrics": {}},
        },
        {
            "query_type": "convergence_trace",
            "projection": {"nodes": [{"canonical_id": "root"}], "edges": []},
            "node_ids": ("root",),
        },
    )
    for kwargs in calls:
        try:
            execute_sidecar_query(**kwargs)
        except NotImplementedError as exc:
            pytest.fail(f"unexpected stub remained: {exc}")


def test_phase_1237_fix1_dispatcher_validates_bounds_before_stub() -> None:
    with pytest.raises(ValueError, match="max_hops_must_be_positive_int"):
        execute_sidecar_query(
            query_type="centrality_metrics",
            projection={},
            bounds=SidecarQueryBounds(max_hops=0),
        )


def test_phase_1237_fix1_runtime_source_has_no_sensitive_constructs() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_imports = {"random", "requests"}
    forbidden_calls = {"open"}
    forbidden_attrs = {("datetime", "now"), ("time", "time")}

    for node in ast.walk(tree):
        assert not isinstance(node, ast.Assert)
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_imports
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                assert (node.func.value.id, node.func.attr) not in forbidden_attrs
        if isinstance(node, ast.Constant):
            assert not isinstance(node.value, float)
