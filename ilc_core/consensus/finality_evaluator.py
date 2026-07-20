# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-445 deterministic finality evaluator and Phase-470 diversity-aware extension."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from .diversity_floor_runtime import (
    CDL_V3_DEPENDENCY,
    compute_diversity_floor_penalty,
    compute_max_cluster_share,
    meets_distinct_cluster_floor,
    meets_max_cluster_share_ceiling,
)

FINALITY_EVALUATOR_VERSION = "finality_evaluator_445.v0.1"
DIVERSITY_AWARE_FINALITY_VERSION = "finality_diversity_floor_runtime_470.v0.1"
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


def _require_positive_number(value: Any, token: str, message: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise ConsensusFinalityEvaluatorError(token, message)
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ConsensusFinalityEvaluatorError(token, message) from exc
    if not number.is_finite() or number <= Decimal("0"):
        raise ConsensusFinalityEvaluatorError(token, message)
    return number


def _require_positive_exact_weight(value: Any, token: str, message: str) -> Decimal:
    # Phase 1235: finality vote weights may be fractional, but not Python float.
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (int, str, Decimal)):
        raise ConsensusFinalityEvaluatorError(token, message)
    try:
        number = value if isinstance(value, Decimal) else Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ConsensusFinalityEvaluatorError(token, message) from exc
    if not number.is_finite() or number <= Decimal("0"):
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
    if type(numerator) is not int or numerator <= 0:
        raise ConsensusFinalityEvaluatorError(
            "consensus_finality_evaluator_quorum_threshold_invalid",
            "quorum_threshold.numerator must be a positive integer",
        )
    if type(denominator) is not int or denominator <= 0:
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
        if type(record_epoch) is not int or record_epoch < 0:
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
                "vote_weight": _require_positive_exact_weight(
                    record.get("vote_weight"),
                    "consensus_finality_evaluator_quorum_record_invalid",
                    "vote_weight must be > 0",
                ),
            }
        )
    return normalized


def _normalize_quorum_records_with_validator(quorum_records: Any) -> list[dict[str, Any]]:
    normalized = _normalize_quorum_records(quorum_records)
    result: list[dict[str, Any]] = []
    for raw_record, normalized_record in zip(quorum_records, normalized):
        validator_id = _require_non_empty_str(
            raw_record.get("validator_id"),
            "consensus_diversity_finality_validator_id_missing",
            "validator_id is required for diversity-aware finality evaluation",
        )
        enriched = dict(normalized_record)
        enriched["validator_id"] = validator_id
        result.append(enriched)
    return result


def _normalize_validator_clusters(raw: Any) -> dict[str, str]:
    data = _require_mapping(
        raw,
        "consensus_diversity_finality_validator_clusters_invalid",
        "validator_clusters must be an object",
    )
    normalized: dict[str, str] = {}
    for validator_id, cluster_id in data.items():
        normalized[_require_non_empty_str(
            validator_id,
            "consensus_diversity_finality_validator_clusters_invalid",
            "validator_clusters keys must be non-empty strings",
        )] = _require_non_empty_str(
            cluster_id,
            "consensus_diversity_finality_validator_clusters_invalid",
            "validator_clusters values must be non-empty strings",
        )
    if not normalized:
        raise ConsensusFinalityEvaluatorError(
            "consensus_diversity_finality_validator_clusters_invalid",
            "validator_clusters must be non-empty",
        )
    return normalized


def _normalize_diversity_policy(raw: Any) -> dict[str, Decimal | int]:
    data = _require_mapping(
        raw,
        "consensus_diversity_finality_diversity_policy_invalid",
        "diversity_policy must be an object",
    )
    distinct_cluster_floor = data.get("distinct_cluster_floor")
    max_cluster_share_ceiling = data.get("max_cluster_share_ceiling")
    if not isinstance(distinct_cluster_floor, int) or distinct_cluster_floor <= 0:
        raise ConsensusFinalityEvaluatorError(
            "consensus_diversity_finality_diversity_policy_invalid",
            "distinct_cluster_floor must be a positive integer",
        )
    ceiling = _require_positive_number(
        max_cluster_share_ceiling,
        "consensus_diversity_finality_diversity_policy_invalid",
        "max_cluster_share_ceiling must be > 0",
    )
    if ceiling > Decimal("1"):
        raise ConsensusFinalityEvaluatorError(
            "consensus_diversity_finality_diversity_policy_invalid",
            "max_cluster_share_ceiling must be <= 1",
        )
    return {
        "distinct_cluster_floor": distinct_cluster_floor,
        "max_cluster_share_ceiling": ceiling,
    }


def _aggregate_weights(normalized_records: list[dict[str, Any]]) -> dict[str, Decimal]:
    # Phase 1235: exact Decimal aggregation prevents float drift before this
    # finality-surface code is wired into production.
    aggregate_weights: dict[str, Decimal] = {}
    for record in normalized_records:
        block_hash = record["block_hash"]
        aggregate_weights[block_hash] = aggregate_weights.get(block_hash, Decimal("0")) + record["vote_weight"]
    return {key: aggregate_weights[key] for key in sorted(aggregate_weights)}


def _aggregate_weights_for_output(aggregate_weights: dict[str, Decimal]) -> dict[str, Decimal]:
    return {key: aggregate_weights[key] for key in sorted(aggregate_weights)}


def evaluate_epoch_finality(
    quorum_records: list[dict[str, Any]],
    quorum_threshold: dict[str, int],
) -> dict[str, Any]:
    numerator, denominator = _normalize_quorum_threshold(quorum_threshold)
    normalized_records = _normalize_quorum_records(quorum_records)
    threshold_fraction = Decimal(numerator) / Decimal(denominator)

    aggregate_weights = _aggregate_weights(normalized_records)
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
        "aggregate_weights": _aggregate_weights_for_output(aggregate_weights),
        "threshold_fraction": threshold_fraction,
        "fork_resolution_applied": False,
        "runtime_version": FINALITY_EVALUATOR_VERSION,
        "dependency": CDL_051_RATIFICATION_DEPENDENCY,
    }


def evaluate_epoch_finality_with_diversity(
    quorum_records: list[dict[str, Any]],
    quorum_threshold: dict[str, int],
    validator_clusters: dict[str, str],
    diversity_policy: dict[str, int | float],
) -> dict[str, Any]:
    numerator, denominator = _normalize_quorum_threshold(quorum_threshold)
    normalized_records = _normalize_quorum_records_with_validator(quorum_records)
    threshold_fraction = Decimal(numerator) / Decimal(denominator)
    clusters = _normalize_validator_clusters(validator_clusters)
    policy = _normalize_diversity_policy(diversity_policy)

    aggregate_weights = _aggregate_weights(normalized_records)
    qualifying_hashes = [
        block_hash for block_hash, weight in aggregate_weights.items() if weight >= threshold_fraction
    ]

    canonical_block_hash: str | None = None
    distinct_clusters: int | None = None
    max_cluster_share: Decimal | None = None
    diversity_penalty: Decimal | None = None
    diversity_status = "not_evaluated"

    if len(qualifying_hashes) == 1:
        candidate_hash = qualifying_hashes[0]
        candidate_records = [record for record in normalized_records if record["block_hash"] == candidate_hash]
        cluster_counts: dict[str, int] = {}
        cluster_weights: dict[str, Decimal] = {}
        for record in candidate_records:
            validator_id = record["validator_id"]
            if validator_id not in clusters:
                raise ConsensusFinalityEvaluatorError(
                    "consensus_diversity_finality_validator_cluster_missing",
                    f"missing cluster assignment for validator_id={validator_id}",
                )
            cluster_id = clusters[validator_id]
            cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1
            cluster_weights[cluster_id] = cluster_weights.get(cluster_id, Decimal("0")) + record["vote_weight"]

        distinct_clusters = len(cluster_counts)
        largest_cluster_weight = max(cluster_weights.values())
        total_candidate_weight = sum(cluster_weights.values(), Decimal("0"))
        max_cluster_share = compute_max_cluster_share(
            largest_cluster_slots=largest_cluster_weight,
            total_panel_slots=total_candidate_weight,
        )
        diversity_penalty = compute_diversity_floor_penalty(
            distinct_clusters=distinct_clusters,
            distinct_cluster_floor=policy["distinct_cluster_floor"],
            max_cluster_share=max_cluster_share,
            max_cluster_share_ceiling=policy["max_cluster_share_ceiling"],
        )
        distinct_ok = meets_distinct_cluster_floor(
            distinct_clusters=distinct_clusters,
            distinct_cluster_floor=policy["distinct_cluster_floor"],
        )
        share_ok = meets_max_cluster_share_ceiling(
            max_cluster_share=max_cluster_share,
            max_cluster_share_ceiling=policy["max_cluster_share_ceiling"],
        )

        if distinct_ok and share_ok:
            finality_status = "finalized"
            canonical_block_hash = candidate_hash
            diversity_status = "diversity_pass"
        else:
            finality_status = "insufficient_diversity"
            diversity_status = "diversity_fail"
    elif len(aggregate_weights) == 1:
        finality_status = "provisional"
    else:
        finality_status = "conflict"

    return {
        "finality_status": finality_status,
        "canonical_block_hash": canonical_block_hash,
        "aggregate_weights": _aggregate_weights_for_output(aggregate_weights),
        "threshold_fraction": threshold_fraction,
        "diversity_status": diversity_status,
        "distinct_clusters": distinct_clusters,
        "max_cluster_share": max_cluster_share,
        "diversity_penalty": diversity_penalty,
        "runtime_version": DIVERSITY_AWARE_FINALITY_VERSION,
        "dependency": CDL_051_RATIFICATION_DEPENDENCY,
        "cdl_v3_dependency": CDL_V3_DEPENDENCY,
    }


def resolve_fork(epoch_states: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(epoch_states, list) or len(epoch_states) < 2:
        raise ConsensusFinalityEvaluatorError(
            "consensus_fork_resolution_insufficient_candidates",
            "at least two epoch-state records are required",
        )

    epoch_index: int | None = None
    candidate_block_hashes: set[str] = set()
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
        candidate_block_hashes.add(
            _require_non_empty_str(
                state.get("candidate_block_hash"),
                "consensus_fork_resolution_state_invalid",
                "candidate_block_hash is required",
            )
        )
        state_digests.append(
            _require_non_empty_str(
                state.get("state_digest"),
                "consensus_fork_resolution_state_digest_missing",
                "state_digest is required",
            )
        )

    if len(candidate_block_hashes) < 2:
        raise ConsensusFinalityEvaluatorError(
            "consensus_fork_resolution_non_conflicting_candidates",
            "fork resolution requires at least two distinct candidate_block_hash values",
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
    "DIVERSITY_AWARE_FINALITY_VERSION",
    "FINALITY_EVALUATOR_VERSION",
    "ConsensusFinalityEvaluatorError",
    "evaluate_epoch_finality",
    "evaluate_epoch_finality_with_diversity",
    "resolve_fork",
]
