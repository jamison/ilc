# SPDX-License-Identifier: AGPL-3.0-or-later
"""CDL-052 reuse-centrality runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .node_submission_runtime import EpistemicSubmissionError

REUSE_CENTRALITY_RUNTIME_VERSION = "reuse_centrality_runtime_537.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"
U_FLOOR = 0.05
COMPUTATION_BACKEND_V1 = "incremental_direct_use_v1"


@dataclass(frozen=True)
class ReuseCentralityResult:
    centrality_score: float
    computation_backend: str


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EpistemicSubmissionError("REUSE_CENTRALITY_MALFORMED_QUERY", f"{name} must be a dict")
    return value


def _require_non_negative_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise EpistemicSubmissionError(
            "REUSE_CENTRALITY_MALFORMED_QUERY",
            f"{name} must be a non-negative int",
        )
    return value


def _validated_usage_ratio(usage_data: Any) -> float | None:
    if usage_data is None:
        return None
    usage_map = _require_mapping("usage_data", usage_data)
    direct_use_count = _require_non_negative_int("direct_use_count", usage_map.get("direct_use_count"))
    total_pool_size = _require_non_negative_int("total_pool_size", usage_map.get("total_pool_size"))
    if total_pool_size == 0:
        raise EpistemicSubmissionError(
            "REUSE_CENTRALITY_MALFORMED_QUERY",
            "total_pool_size must be positive",
        )
    return direct_use_count / total_pool_size


def validate_epistemic_reuse_centrality_query(query: dict) -> None:
    query_map = _require_mapping("query", query)
    if not isinstance(query_map.get("cid"), str) or not query_map["cid"]:
        raise EpistemicSubmissionError("REUSE_CENTRALITY_MALFORMED_QUERY", "cid must be a non-empty string")
    if not isinstance(query_map.get("agent_id"), str) or not query_map["agent_id"]:
        raise EpistemicSubmissionError(
            "REUSE_CENTRALITY_MALFORMED_QUERY",
            "agent_id must be a non-empty string",
        )


def query_reuse_centrality(query: dict) -> ReuseCentralityResult:
    validate_epistemic_reuse_centrality_query(query)
    raw_ratio = _validated_usage_ratio(query.get("usage_data"))
    if raw_ratio is None or raw_ratio < U_FLOOR:
        centrality_score = 0.0
    else:
        centrality_score = min(1.0, raw_ratio)
    return ReuseCentralityResult(
        centrality_score=centrality_score,
        computation_backend=COMPUTATION_BACKEND_V1,
    )
