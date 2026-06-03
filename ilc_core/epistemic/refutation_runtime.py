# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-052 refutation runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .node_submission_runtime import EpistemicSubmissionError

EPISTEMIC_RUNTIME_PART2_VERSION = "epistemic_refutation_novelty_reuse_runtime_478.v0.1"
EPISTEMIC_PART1_DEPENDENCY = "epistemic_node_submission_runtime_477.v0.1"

# TBD: pending future simulation lane
SUBMISSION_STAKE_AMOUNT_TBD = "submission_stake_amount_tbd"
# TBD: pending future simulation lane
REFUTATION_STAKE_AMOUNT_TBD = "refutation_stake_amount_tbd"


@dataclass(frozen=True)
class RefutationSubmissionResult:
    stake_action: str
    failed_novelty_record_added: bool
    reputation_event: dict[str, Any]


def _require_mapping(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EpistemicSubmissionError("MALFORMED_REFUTATION_SUBMISSION", f"{name} must be a dict")
    return value


def _record_reputation_event(agent_id: str, event_type: str) -> dict[str, Any]:
    return {
        "agent_id": agent_id,
        "event_type": event_type,
        "recorded": False,
    }


def validate_epistemic_refutation_submission(submission: dict) -> None:
    submission_map = _require_mapping("submission", submission)
    required_fields = ("target_cid", "agent_id", "authored_envelope", "refutation_criterion")
    for field in required_fields:
        if field not in submission_map:
            raise EpistemicSubmissionError(
                "MALFORMED_REFUTATION_SUBMISSION",
                f"missing required field: {field}",
            )
    if not isinstance(submission_map["target_cid"], str) or not submission_map["target_cid"]:
        raise EpistemicSubmissionError(
            "MALFORMED_REFUTATION_SUBMISSION",
            "target_cid must be a non-empty string",
        )
    if not isinstance(submission_map["agent_id"], str) or not submission_map["agent_id"]:
        raise EpistemicSubmissionError(
            "MALFORMED_REFUTATION_SUBMISSION",
            "agent_id must be a non-empty string",
        )
    _require_mapping("authored_envelope", submission_map["authored_envelope"])
    criterion = _require_mapping("refutation_criterion", submission_map["refutation_criterion"])
    for field in ("claim", "evidence_type", "scope_boundary"):
        if field not in criterion:
            raise EpistemicSubmissionError(
                "MALFORMED_REFUTATION_SUBMISSION",
                f"refutation_criterion missing required field: {field}",
            )


def process_refutation_submission(
    submission: dict,
    *,
    novelty_failed: bool = False,
    challenge_succeeds: bool = False,
) -> RefutationSubmissionResult:
    validate_epistemic_refutation_submission(submission)
    agent_id = submission["agent_id"]
    if novelty_failed:
        return RefutationSubmissionResult(
            stake_action="return_full",
            failed_novelty_record_added=True,
            reputation_event=_record_reputation_event(agent_id, "novelty_failed"),
        )
    if challenge_succeeds:
        return RefutationSubmissionResult(
            stake_action="partial_slash_hook",
            failed_novelty_record_added=False,
            reputation_event=_record_reputation_event(agent_id, "challenge_succeeded"),
        )
    return RefutationSubmissionResult(
        stake_action="hold_pending",
        failed_novelty_record_added=False,
        reputation_event=_record_reputation_event(agent_id, "submitted"),
    )
