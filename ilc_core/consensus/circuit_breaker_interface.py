"""Validator-facing CDL-045 circuit-breaker surface."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .diversity_floor_runtime import (
    compute_max_cluster_share,
    meets_distinct_cluster_floor,
    meets_max_cluster_share_ceiling,
)
from .finality_evaluator import CDL_051_RATIFICATION_DEPENDENCY

CDL_045_DEPENDENCY = 'cdl_045_operational_emergency_response_408.v0.1'
CIRCUIT_BREAKER_INTERFACE_VERSION = 'validator_circuit_breaker_surface_488.v0.1'
DEFAULT_DISTINCT_CLUSTER_FLOOR = 2
DEFAULT_MAX_CLUSTER_SHARE_CEILING = 0.60
DEFAULT_QUORUM_WEIGHT_THRESHOLD = 2.0 / 3.0


class CircuitBreakerInterfaceError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _normalize_votes(validator_votes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(validator_votes, list) or not validator_votes:
        raise CircuitBreakerInterfaceError(
            'circuit_breaker_votes_missing',
            'validator_votes must be a non-empty list',
        )
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for vote in validator_votes:
        if not isinstance(vote, dict):
            raise CircuitBreakerInterfaceError(
                'circuit_breaker_vote_invalid',
                'each validator vote must be a mapping',
            )
        validator_id = vote.get('validator_id')
        cluster_id = vote.get('cluster_id')
        vote_weight = vote.get('vote_weight')
        requested = vote.get('circuit_breaker_requested')
        if not isinstance(validator_id, str) or not validator_id:
            raise CircuitBreakerInterfaceError(
                'circuit_breaker_validator_id_invalid',
                'validator_id must be a non-empty string',
            )
        if validator_id in seen:
            raise CircuitBreakerInterfaceError(
                'circuit_breaker_duplicate_validator',
                'duplicate validator_id in validator_votes',
            )
        seen.add(validator_id)
        if not isinstance(cluster_id, str) or not cluster_id:
            raise CircuitBreakerInterfaceError(
                'circuit_breaker_cluster_id_invalid',
                'cluster_id must be a non-empty string',
            )
        # Phase 1235: align validator-facing vote weights with Genesis bootstrap
        # positive-int enforcement; fractional float weights are rejected.
        if isinstance(vote_weight, bool) or not isinstance(vote_weight, int) or vote_weight <= 0:
            raise CircuitBreakerInterfaceError(
                'circuit_breaker_vote_weight_invalid',
                'vote_weight must be a positive integer',
            )
        if not isinstance(requested, bool):
            raise CircuitBreakerInterfaceError(
                'circuit_breaker_request_flag_invalid',
                'circuit_breaker_requested must be a bool',
            )
        normalized.append(
            {
                'validator_id': validator_id,
                'cluster_id': cluster_id,
                'vote_weight': vote_weight,
                'circuit_breaker_requested': requested,
            }
        )
    return normalized


def summarize_circuit_breaker_quorum_state(
    validator_votes: list[dict[str, Any]],
    *,
    distinct_cluster_floor: int = DEFAULT_DISTINCT_CLUSTER_FLOOR,
    max_cluster_share_ceiling: float = DEFAULT_MAX_CLUSTER_SHARE_CEILING,
    quorum_weight_threshold: float = DEFAULT_QUORUM_WEIGHT_THRESHOLD,
) -> dict[str, Any]:
    normalized = _normalize_votes(validator_votes)
    total_weight = sum(v['vote_weight'] for v in normalized)
    requested_votes = [v for v in normalized if v['circuit_breaker_requested']]
    requested_weight = round(sum(v['vote_weight'] for v in requested_votes), 12)
    cluster_counts = Counter(v['cluster_id'] for v in requested_votes)
    largest_cluster_slots = max(cluster_counts.values(), default=0)
    distinct_clusters = len(cluster_counts)
    max_cluster_share = compute_max_cluster_share(
        largest_cluster_slots=largest_cluster_slots,
        total_panel_slots=max(len(requested_votes), 1),
    )
    quorum_share = 0.0 if total_weight == 0 else round(requested_weight / total_weight, 12)
    distinct_ok = meets_distinct_cluster_floor(
        distinct_clusters=distinct_clusters,
        distinct_cluster_floor=distinct_cluster_floor,
    )
    share_ok = meets_max_cluster_share_ceiling(
        max_cluster_share=max_cluster_share,
        max_cluster_share_ceiling=max_cluster_share_ceiling,
    )
    quorum_ok = quorum_share >= quorum_weight_threshold
    return {
        'requested_validator_count': len(requested_votes),
        'requested_weight': requested_weight,
        'total_weight': round(total_weight, 12),
        'quorum_share': quorum_share,
        'distinct_clusters': distinct_clusters,
        'max_cluster_share': max_cluster_share,
        'distinct_ok': distinct_ok,
        'share_ok': share_ok,
        'quorum_ok': quorum_ok,
        'eligible': quorum_ok and distinct_ok and share_ok,
        'distinct_cluster_floor': distinct_cluster_floor,
        'max_cluster_share_ceiling': max_cluster_share_ceiling,
        'quorum_weight_threshold': quorum_weight_threshold,
    }


def build_circuit_breaker_request(
    *,
    epoch: int,
    canonical_block_hash: str,
    reason: str,
    validator_votes: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(epoch, int) or epoch < 0:
        raise CircuitBreakerInterfaceError(
            'circuit_breaker_epoch_invalid',
            'epoch must be a non-negative integer',
        )
    if not isinstance(canonical_block_hash, str) or not canonical_block_hash:
        raise CircuitBreakerInterfaceError(
            'circuit_breaker_block_hash_invalid',
            'canonical_block_hash must be a non-empty string',
        )
    if not isinstance(reason, str) or not reason:
        raise CircuitBreakerInterfaceError(
            'circuit_breaker_reason_invalid',
            'reason must be a non-empty string',
        )
    summary = summarize_circuit_breaker_quorum_state(validator_votes)
    return {
        'epoch': epoch,
        'canonical_block_hash': canonical_block_hash,
        'reason': reason,
        'validator_votes': _normalize_votes(validator_votes),
        'quorum_summary': summary,
        'request_status': 'eligible' if summary['eligible'] else 'insufficient_quorum_state',
    }


def verify_circuit_breaker_request(request: dict[str, Any]) -> None:
    if not isinstance(request, dict):
        raise CircuitBreakerInterfaceError(
            'circuit_breaker_request_invalid',
            'request must be a mapping',
        )
    build = build_circuit_breaker_request(
        epoch=request.get('epoch'),
        canonical_block_hash=request.get('canonical_block_hash'),
        reason=request.get('reason'),
        validator_votes=request.get('validator_votes'),
    )
    if build['request_status'] != 'eligible':
        raise CircuitBreakerInterfaceError(
            'circuit_breaker_request_not_eligible',
            'request does not satisfy quorum and diversity conditions',
        )
