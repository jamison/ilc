"""Phase-445 deterministic finality evaluator and fork-resolution runtime."""

from __future__ import annotations

from typing import Any


FINALITY_EVALUATOR_VERSION = "finality_evaluator_445.v0.1"
CDL_051_RATIFICATION_DEPENDENCY = "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"


class ConsensusFinalityEvaluatorError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_mapping(value: Any, token: str, message: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConsensusFinalityEvaluatorError(token, message)
    return value


def _require_non_empty_str(value: Any, token: str, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConsensusFinalityEvaluatorError(token, message)
    return value


def _require_positive_number(value: Any, token: str, message: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConsensusFinalityEvaluatorError(token, message)
    number = float(value)
    if number <= 0.0:
        raise ConsensusFinalityEvaluatorError(token, message)
    return number


def _normalize_quorum_threshold(quorum_threshold: Any) -> tuple[int, int]:
    if quorum_threshold is None:
        raise ConsensusFinalityEvaluatorError(
            "consensus_finality_evaluator_quorum_threshold_missing",
            "quorum_threshold is required",
        )
    threshold = _require_mapping(
        quorum_threshold,
        "consensus_finality_evaluator_quorum_threshold_invalid",
        "quorum_threshold must be an object",
    )
    numerator = threshold.get("numerator")
    denominator = threshold.get("denominator")
    if not isinstance(numerator, int) or numerator <= 0:
        raise ConsensusFinalityEvaluatorError(
            "consensus_finality_evaluator_quorum_threshold_invalid",
            "quorum_threshold.numerator must be a positive integer",
        )
    if not isinstance(denominator, int) or denominator <= 0:
        raise ConsensusFinalityEvaluatorError(
            "consensus_finality_evaluator_quorum_threshold_invalid",
            "quorum_threshold.denominator must be a positive integer",
        )
    if numerator > denominator:
        raise ConsensusFinalityEvaluatorError(
            "consensus_finality_evaluator_quorum_threshold_invalid",
            "quorum_threshold numerator cannot exceed denominator",
        )
    return numerator, denominator


def _normalize_quorum_records(quorum_records: Any) -> list[dict[str, Any]]:
    if not isinstance(quorum_records, list) or not quorum_records:
        raise ConsensusFinalityEvaluatorError(
            "consensus_finality_evaluator_quorum_records_empty",
            "quorum_records must be a non-empty list",
        )

    normalized: list[dict[str, Any]] = []
    epoch_index: int | None = None
    for raw_record in quorum_records:
        record = _require_mapping(
            raw_record,
            "consensus_finality_evaluator_quorum_record_invalid",
            "quorum record must be an object",
        )
        record_epoch = record.get("epoch_index")
        if not isinstance(record_epoch, int) or record_epoch < 0:
            raise ConsensusFinalityEvaluatorError(
                "consensus_finality_evaluator_quorum_record_invalid",
                "quorum record epoch_index must be an integer >= 0",
            )
        if epoch_index is None:
            epoch_index = record_epoch
        elif record_epoch != epoch_index:
            raise ConsensusFinalityEvaluatorError(
                "consensus_finality_evaluator_epoch_index_mismatch",
                "all quorum records must share one epoch_index",
            )
        normalized.append(
            {
                "block_hash": _require_non_empty_str(
                    record.get("block_hash"),
                    "consensus_finality_evaluator_quorum_record_invalid",
                    "block_hash is required",
                ),
                "epoch_index": record_epoch,
                "vote_weight": _require_positive_number(
                    record.get("vote_weight"),
                    "consensus_finality_evaluator_quorum_record_invalid",
                    "vote_weight must be > 0",
                ),
            }
        )
    return normalized


def evaluate_epoch_finality(
    quorum_records: list[dict[str, Any]],
    quorum_threshold: dict[str, int],
) -> dict[str, Any]:
    normalized_records = _normalize_quorum_records(quorum_records)
    numerator, denominator = _normalize_quorum_threshold(quorum_threshold)
    threshold_fraction = numerator / denominator

    aggregate_weights: dict[str, float] = {}
    for record in normalized_records:
        block_hash = record["block_hash"]
        aggregate_weights[block_hash] = aggregate_weights.get(block_hash, 0.0) + record["vote_weight"]
    aggregate_weights = {key: aggregate_weights[key] for key in sorted(aggregate_weights)}

    qualifying_hashes = [
        block_hash for block_hash, weight in aggregate_weights.items() if weight >= threshold_fraction
    ]
    if len(qualifying_hashes) == 1:
        finality_status = "finalized"
        canonical_block_hash: str | None = qualifying_hashes[0]
    elif len(aggregate_weights) == 1:
        finality_status = "provisional"
        canonical_block_hash = None
    else:
        finality_status = "conflict"
        canonical_block_hash = None

    return {
        "finality_status": finality_status,
        "canonical_block_hash": canonical_block_hash,
        "aggregate_weights": aggregate_weights,
        "threshold_fraction": threshold_fraction,
        "fork_resolution_applied": False,
        "runtime_version": FINALITY_EVALUATOR_VERSION,
        "dependency": CDL_051_RATIFICATION_DEPENDENCY,
    }


def resolve_fork(epoch_states: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(epoch_states, list) or len(epoch_states) < 2:
        raise ConsensusFinalityEvaluatorError(
            "consensus_fork_resolution_insufficient_candidates",
            "at least two epoch-state records are required",
        )

    epoch_index: int | None = None
    state_digests: list[str] = []
    for raw_state in epoch_states:
        state = _require_mapping(
            raw_state,
            "consensus_fork_resolution_state_invalid",
            "epoch-state record must be an object",
        )
        state_epoch = state.get("epoch_index")
        if not isinstance(state_epoch, int) or state_epoch < 0:
            raise ConsensusFinalityEvaluatorError(
                "consensus_fork_resolution_state_invalid",
                "epoch-state epoch_index must be an integer >= 0",
            )
        if epoch_index is None:
            epoch_index = state_epoch
        elif state_epoch != epoch_index:
            raise ConsensusFinalityEvaluatorError(
                "consensus_fork_resolution_epoch_index_mismatch",
                "all epoch-state records must share one epoch_index",
            )
        state_digests.append(
            _require_non_empty_str(
                state.get("state_digest"),
                "consensus_fork_resolution_state_digest_missing",
                "state_digest is required",
            )
        )

    selected_state_digest = min(state_digests)
    return {
        "selected_state_digest": selected_state_digest,
        "rule_applied": "lexicographic_state_digest_minimum",
        "candidate_count": len(epoch_states),
        "epoch_index": epoch_index,
        "runtime_version": FINALITY_EVALUATOR_VERSION,
        "dependency": CDL_051_RATIFICATION_DEPENDENCY,
    }


__all__ = [
    "CDL_051_RATIFICATION_DEPENDENCY",
    "FINALITY_EVALUATOR_VERSION",
    "ConsensusFinalityEvaluatorError",
    "evaluate_epoch_finality",
    "resolve_fork",
]
