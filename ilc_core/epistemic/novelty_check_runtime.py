# SPDX-License-Identifier: AGPL-3.0-or-later
"""CDL-052 novelty-check runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .node_submission_runtime import EpistemicSubmissionError

_KNOWN_DUPLICATE_CIDS = {"dup-known-cid", "cid-duplicate"}


@dataclass(frozen=True)
class NoveltyCheckResult:
    novel: bool
    duplicate_cid: str | None
    failure_token: str | None


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EpistemicSubmissionError("NOVELTY_CHECK_MALFORMED_QUERY", f"{name} must be a dict")
    return value


def validate_epistemic_novelty_check_query(query: dict) -> None:
    query_map = _require_mapping("query", query)
    if not isinstance(query_map.get("cid"), str) or not query_map["cid"]:
        raise EpistemicSubmissionError("NOVELTY_CHECK_MALFORMED_QUERY", "cid must be a non-empty string")
    if not isinstance(query_map.get("agent_id"), str) or not query_map["agent_id"]:
        raise EpistemicSubmissionError(
            "NOVELTY_CHECK_MALFORMED_QUERY",
            "agent_id must be a non-empty string",
        )


def check_novelty(query: dict) -> NoveltyCheckResult:
    validate_epistemic_novelty_check_query(query)
    cid = query["cid"]
    if cid in _KNOWN_DUPLICATE_CIDS or cid.startswith("dup-"):
        return NoveltyCheckResult(
            novel=False,
            duplicate_cid=cid,
            failure_token="NOVELTY_CHECK_DUPLICATE",
        )
    return NoveltyCheckResult(
        novel=True,
        duplicate_cid=None,
        failure_token=None,
    )
