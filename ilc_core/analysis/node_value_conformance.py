# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Mapping, TypedDict

from ilc_core.analysis.node_value_input_canon import NodeValueInputEvent
from ilc_core.analysis.node_value_kernel import (
    DEFAULT_EW_WEIGHTS,
    NodeEvidenceVector,
    NodeScoreVector,
    build_node_evidence_vectors,
    compute_node_scores,
)


class NodeValueConformanceReport(TypedDict):
    score_rows: list[NodeScoreVector]
    score_rows_sha256: str
    anti_sybil_ok: bool
    anti_sybil_flags: list[str]


class NodeValueChallengeVerification(TypedDict):
    ok: bool
    errors: list[str]
    expected_sha256: str
    expected_row_count: int


def compute_score_rows_sha256(score_rows: list[NodeScoreVector]) -> str:
    def _stable_decimal_default(value: object) -> str:
        if isinstance(value, Decimal):
            if not value.is_finite():
                raise ValueError("node_value_conformance_non_finite_decimal")
            return format(value, "f")
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

    payload = json.dumps(
        score_rows,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=_stable_decimal_default,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate_anti_sybil_invariants(evidence_vectors: list[NodeEvidenceVector]) -> list[str]:
    flags: list[str] = []
    for vector in evidence_vectors:
        node_id = vector["node_id"]
        reuse_count = float(vector["reuse_count"])
        unique_agents = float(vector["unique_agents_using"])

        if reuse_count >= 2.0 and unique_agents < 2.0:
            flags.append(f"sybil_low_diversity_reuse:{node_id}")
        if unique_agents > reuse_count and reuse_count > 0.0:
            flags.append(f"sybil_invariant_inconsistent_agent_reuse_count:{node_id}")
    return sorted(flags)


def build_node_value_conformance_report(
    events: list[NodeValueInputEvent],
    *,
    weights: Mapping[str, float] = DEFAULT_EW_WEIGHTS,
) -> NodeValueConformanceReport:
    score_rows = compute_node_scores(events, weights=weights)
    evidence_vectors = build_node_evidence_vectors(events)
    anti_sybil_flags = evaluate_anti_sybil_invariants(evidence_vectors)

    return {
        "score_rows": score_rows,
        "score_rows_sha256": compute_score_rows_sha256(score_rows),
        "anti_sybil_ok": len(anti_sybil_flags) == 0,
        "anti_sybil_flags": anti_sybil_flags,
    }


def verify_node_value_challenge(
    events: list[NodeValueInputEvent],
    *,
    claimed_sha256: str,
    claimed_row_count: int,
    weights: Mapping[str, float] = DEFAULT_EW_WEIGHTS,
) -> NodeValueChallengeVerification:
    report = build_node_value_conformance_report(events, weights=weights)
    expected_sha256 = report["score_rows_sha256"]
    expected_row_count = len(report["score_rows"])

    errors: list[str] = []
    if claimed_sha256 != expected_sha256:
        errors.append("challenge_hash_mismatch")
    if claimed_row_count != expected_row_count:
        errors.append("challenge_row_count_mismatch")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "expected_sha256": expected_sha256,
        "expected_row_count": expected_row_count,
    }
