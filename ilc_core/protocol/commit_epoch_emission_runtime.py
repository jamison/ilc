"""Phase 1236 commit.epoch emission connector.

This module is finality-surface infrastructure, but not production emission
authorization. It builds the Phase 1235 canonical commit.epoch event from
caller-supplied epoch/finality inputs. Consensus/DAG traversal and production
emission remain separately gated.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping, Sequence

from ilc_core.protocol.event_log import (
    COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION,
    ProtocolEvent,
    make_canonical_commit_epoch_event,
    validate_canonical_commit_epoch_payload,
)

COMMIT_EPOCH_EMISSION_RUNTIME_VERSION = "commit_epoch_emission_runtime_1236.v0.1"
CDL_051_DEPENDENCY = "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"
COMMIT_EPOCH_CANONICAL_DEPENDENCY = COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION

_ALLOWED_FINALIZATION_STATES = {"committed", "rolled_back", "superseded"}
_ZERO = Decimal("0")


def _require_non_negative_int(value: object, token: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(token)
    return value


def _require_non_empty_string(value: object, token: str) -> str:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)
    return value


def _require_non_negative_decimal(value: object, token: str) -> Decimal:
    if not isinstance(value, Decimal):
        raise ValueError(token)
    if not value.is_finite() or value < _ZERO:
        raise ValueError(token)
    return value


def _digest_to_sha256_cid(value: object, token: str) -> str:
    digest = _require_non_empty_string(value, token)
    if digest.startswith("sha256:"):
        suffix = digest.removeprefix("sha256:")
        if suffix == "":
            raise ValueError(token)
        return digest
    return f"sha256:{digest}"


def _validate_quorum_records(quorum_records: object, epoch_index: int) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(quorum_records, Sequence) or isinstance(quorum_records, (str, bytes, bytearray)):
        raise ValueError("quorum_records_must_be_sequence")
    normalized: list[Mapping[str, Any]] = []
    for record in quorum_records:
        if not isinstance(record, Mapping):
            raise ValueError("quorum_record_must_be_mapping")
        record_epoch = record.get("epoch_index")
        if type(record_epoch) is not int or record_epoch != epoch_index:
            raise ValueError("quorum_record_epoch_index_mismatch")
        _require_non_empty_string(record.get("block_hash"), "quorum_record_block_hash_missing")
        _require_non_empty_string(
            record.get("quorum_state_digest"),
            "quorum_record_quorum_state_digest_missing",
        )
        if "vote_weight" not in record:
            raise ValueError("quorum_record_vote_weight_missing")
        normalized.append(record)
    return tuple(normalized)


def build_commit_epoch_event(
    *,
    epoch_index: int,
    epoch_id: str,
    namespace_id: str,
    finalization_state: str,
    quorum_records: Sequence[Mapping[str, Any]],
    epoch_state_digest: str,
    epoch_events_digest: str,
    reward_total: Decimal,
    stake_total: Decimal,
    task_count: int,
    agent_count: int,
) -> ProtocolEvent:
    """Build a canonical commit.epoch event from finalized epoch inputs.

    The connector is pure: no filesystem I/O, no network I/O, no wall-clock, no
    random data, and no production consensus emission side effect.
    """

    normalized_epoch_index = _require_non_negative_int(epoch_index, "epoch_index_must_be_non_negative_int")
    normalized_task_count = _require_non_negative_int(task_count, "task_count_must_be_non_negative_int")
    normalized_agent_count = _require_non_negative_int(agent_count, "agent_count_must_be_non_negative_int")
    normalized_epoch_id = _require_non_empty_string(epoch_id, "epoch_id_must_be_non_empty_string")
    normalized_namespace_id = _require_non_empty_string(
        namespace_id,
        "namespace_id_must_be_non_empty_string",
    )

    if finalization_state not in _ALLOWED_FINALIZATION_STATES:
        raise ValueError("finalization_state_invalid")

    _validate_quorum_records(quorum_records, normalized_epoch_index)
    normalized_reward_total = _require_non_negative_decimal(
        reward_total,
        "reward_total_must_be_non_negative_finite_decimal",
    )
    normalized_stake_total = _require_non_negative_decimal(
        stake_total,
        "stake_total_must_be_non_negative_finite_decimal",
    )

    event = make_canonical_commit_epoch_event(
        epoch_index=normalized_epoch_index,
        epoch_id=normalized_epoch_id,
        namespace_id=normalized_namespace_id,
        finalization_state=finalization_state,  # type: ignore[arg-type]
        summary={
            "task_count": normalized_task_count,
            "agent_count": normalized_agent_count,
            "reward_total": normalized_reward_total,
            "stake_total": normalized_stake_total,
        },
        checksums={
            "epoch_events_cid": _digest_to_sha256_cid(
                epoch_events_digest,
                "epoch_events_digest_must_be_non_empty_string",
            ),
            "epoch_state_cid": _digest_to_sha256_cid(
                epoch_state_digest,
                "epoch_state_digest_must_be_non_empty_string",
            ),
        },
        source="protocol:commit_epoch_emission_runtime",
    )
    validate_canonical_commit_epoch_payload(event.payload)
    return event

