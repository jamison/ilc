"""Read-only sidecar query runtime skeleton for graph projections.

Phase 1237 Fix1 establishes the sidecar query contract without implementing
query behavior. Later Fix phases fill the dispatcher arms.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ilc_core.graph.agent_graph_projection_runtime import (
    AGENT_GRAPH_PROJECTION_RUNTIME_VERSION,
)


SIDECAR_QUERY_RUNTIME_VERSION = "sidecar_query_runtime_1237.v0.1"
SIDECAR_PROJECTION_DEPENDENCY = AGENT_GRAPH_PROJECTION_RUNTIME_VERSION

QUERY_TYPES = frozenset(
    {
        "ego_graph",
        "centrality_metrics",
        "convergence_trace",
    }
)


@dataclass(frozen=True)
class SidecarQueryBounds:
    max_hops: int = 4
    max_nodes: int = 200
    max_results: int = 100

    def validate(self) -> None:
        for field_name in ("max_hops", "max_nodes", "max_results"):
            value = getattr(self, field_name)
            if type(value) is not int:
                raise ValueError(f"{field_name}_must_be_positive_int")
            if value <= 0:
                raise ValueError(f"{field_name}_must_be_positive_int")


def execute_sidecar_query(
    *,
    query_type: str,
    projection: Mapping[str, Any],
    bounds: SidecarQueryBounds | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if query_type not in QUERY_TYPES:
        raise ValueError("sidecar_query_type_unsupported")

    active_bounds = bounds or SidecarQueryBounds()
    active_bounds.validate()

    raise NotImplementedError(f"sidecar_query_{query_type}_not_yet_implemented")
