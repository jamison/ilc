# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-052 epistemic node-submission runtime.

Phase 477 implements the node-submission envelope and mode-routing boundary only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ilc_core.consensus.popperian_gate_runtime import (
    PopperianGateValidationError,
    evaluate_decomposition_admissibility,
)

EPISTEMIC_RUNTIME_PART1_VERSION = "epistemic_node_submission_runtime_477.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"


@dataclass(frozen=True)
class EpistemicSubmissionError(ValueError):
    token: str
    message: str

    def __str__(self) -> str:
        return self.message


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EpistemicSubmissionError(
            "MALFORMED_SUBMISSION",
            f"{name} must be a dict",
        )
    return value


def _validate_refutation_criterion(criterion: dict[str, Any]) -> None:
    required_fields = (
        "claim",
        "evidence_type",
        "scope_boundary",
        "claim_form",
        "has_falsifiable_test",
    )
    for field in required_fields:
        if field not in criterion:
            raise EpistemicSubmissionError(
                "MALFORMED_REFUTATION_CRITERION",
                f"refutation_criterion missing required field: {field}",
            )
    if criterion["evidence_type"] not in {"empirical", "logical", "counter_example"}:
        raise EpistemicSubmissionError(
            "MALFORMED_REFUTATION_CRITERION",
            "refutation_criterion.evidence_type must be empirical, logical, or counter_example",
        )
    try:
        admissible = evaluate_decomposition_admissibility(
            claim_form=criterion["claim_form"],
            has_falsifiable_test=criterion["has_falsifiable_test"],
            is_inadmissible_counterexample=criterion.get("is_inadmissible_counterexample", False),
            agreement_score=criterion.get("agreement_score", "1.0"),
            reproducibility_threshold=criterion.get("reproducibility_threshold", "0.85"),
        )
    except PopperianGateValidationError as exc:
        raise EpistemicSubmissionError(
            "MALFORMED_REFUTATION_CRITERION",
            f"refutation_criterion failed Popperian gate validation: {exc.token}",
        ) from exc
    if not admissible:
        raise EpistemicSubmissionError(
            "MALFORMED_REFUTATION_CRITERION",
            "refutation_criterion did not satisfy the CDL-V7 Popperian admissibility gate",
        )


def route_epistemic_mode(submission: dict) -> str:
    submission_map = _require_mapping("submission", submission)
    authored_envelope = _require_mapping(
        "authored_envelope",
        submission_map.get("authored_envelope"),
    )
    protocol_envelope = submission_map.get("protocol_envelope", {})
    if protocol_envelope is not None:
        protocol_envelope = _require_mapping("protocol_envelope", protocol_envelope)
    transport_envelope = submission_map.get("transport_envelope", {})
    if transport_envelope is not None:
        transport_envelope = _require_mapping("transport_envelope", transport_envelope)

    if submission_map.get("normative") is True and "refutation_criterion" in authored_envelope:
        raise EpistemicSubmissionError(
            "NORMATIVE_REFUTATION_COLLISION",
            "normative: true may not co-exist with refutation_criterion",
        )

    if "refutation_criterion" in submission_map:
        raise EpistemicSubmissionError(
            "AUTHORED_ENVELOPE_VIOLATION",
            "refutation_criterion must not be placed at the top level",
        )
    if "refutation_criterion" in protocol_envelope or "refutation_criterion" in transport_envelope:
        raise EpistemicSubmissionError(
            "AUTHORED_ENVELOPE_VIOLATION",
            "refutation_criterion must live in the authored envelope only",
        )

    if submission_map.get("anomaly_signal") is True:
        return "mode_3_boundary_detected"

    criterion = authored_envelope.get("refutation_criterion")
    if criterion is None:
        return "mode_1"
    _validate_refutation_criterion(_require_mapping("refutation_criterion", criterion))
    return "mode_2"


def validate_epistemic_node_submission(submission: dict) -> None:
    submission_map = _require_mapping("submission", submission)
    if not isinstance(submission_map.get("cid"), str) or not submission_map["cid"]:
        raise EpistemicSubmissionError(
            "MALFORMED_SUBMISSION",
            "cid must be a non-empty string",
        )
    if not isinstance(submission_map.get("agent_id"), str) or not submission_map["agent_id"]:
        raise EpistemicSubmissionError(
            "MALFORMED_SUBMISSION",
            "agent_id must be a non-empty string",
        )
    route_epistemic_mode(submission_map)
