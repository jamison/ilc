"""CDL-052 reuse-centrality runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .node_submission_runtime import EpistemicSubmissionError


@dataclass(frozen=True)
class ReuseCentralityResult:
    centrality_score: float
    computation_backend: str


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EpistemicSubmissionError("REUSE_CENTRALITY_MALFORMED_QUERY", f"{name} must be a dict")
    return value


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
    return ReuseCentralityResult(
        centrality_score=0.0,
        computation_backend="stub_deferred",
    )
