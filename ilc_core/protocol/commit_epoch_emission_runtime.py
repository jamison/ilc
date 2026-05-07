"""Phase 1236 commit.epoch emission connector.

This module is finality-surface infrastructure, but not production emission
authorization. It builds the Phase 1235 canonical commit.epoch event from
caller-supplied epoch/finality inputs. Consensus/DAG traversal and production
emission remain separately gated.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any, Mapping, Sequence

from ilc_core.protocol.event_log import (
    COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION,
    ProtocolEvent,
    make_canonical_commit_epoch_event,
    validate_canonical_commit_epoch_payload,
)

COMMIT_EPOCH_EMISSION_RUNTIME_VERSION = "commit_epoch_emission_runtime_1236.v0.1"
COMMIT_EPOCH_QUORUM_PROJECTION_VERSION = "commit_epoch_quorum_projection_1236_fix2.v0.1"
CDL_051_DEPENDENCY = "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"
COMMIT_EPOCH_CANONICAL_DEPENDENCY = COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION

_ALLOWED_FINALIZATION_STATES = {"committed", "rolled_back", "superseded"}
_ZERO = Decimal("0")
_LOWER_HEX = frozenset("0123456789abcdef")


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


def _require_lower_hex(value: object, token: str) -> str:
    text = _require_non_empty_string(value, token)
    if any(char not in _LOWER_HEX for char in text):
        raise ValueError(token)
    return text


def _require_optional_sha256_ref(value: object, token: str) -> str | None:
    if value is None:
        return None
    text = _require_non_empty_string(value, token)
    if not text.startswith("sha256:"):
        raise ValueError(token)
    suffix = text.removeprefix("sha256:")
    if suffix == "" or any(char not in _LOWER_HEX for char in suffix):
        raise ValueError(token)
    return text


def _normalize_signers(signers: object) -> tuple[int, ...]:
    if not isinstance(signers, Sequence) or isinstance(signers, (str, bytes, bytearray)):
        raise ValueError("quorum_projection_signers_must_be_sequence")
    if len(signers) == 0:
        raise ValueError("quorum_projection_signers_must_be_non_empty")
    normalized: list[int] = []
    seen: set[int] = set()
    for signer in signers:
        if type(signer) is not int or signer < 0:
            raise ValueError("quorum_projection_signer_must_be_non_negative_int")
        if signer in seen:
            raise ValueError("quorum_projection_signers_must_be_unique")
        seen.add(signer)
        normalized.append(signer)
    return tuple(sorted(normalized))


def _canonical_json_bytes(payload: Mapping[str, object]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def build_quorum_proof_projection(
    *,
    epoch_sequence: int,
    state_root_cidv1_hex: str,
    signers: Sequence[int],
    agg_sig_bytes_hex: str,
    source_record_digest: str | None = None,
) -> dict[str, object]:
    """Build the canonical Layer-B quorum-proof projection.

    The projection is pure fixture/proof material for later causal-frontier
    mapping. It does not verify BLS signatures or write to consensus.
    """

    return {
        "agg_sig_bytes_hex": _require_lower_hex(
            agg_sig_bytes_hex,
            "quorum_projection_agg_sig_bytes_hex_invalid",
        ),
        "epoch_sequence": _require_non_negative_int(
            epoch_sequence,
            "quorum_projection_epoch_sequence_must_be_non_negative_int",
        ),
        "signers": list(_normalize_signers(signers)),
        "source_record_digest": _require_optional_sha256_ref(
            source_record_digest,
            "quorum_projection_source_record_digest_invalid",
        ),
        "state_root_cidv1_hex": _require_lower_hex(
            state_root_cidv1_hex,
            "quorum_projection_state_root_cidv1_hex_invalid",
        ),
    }


def compute_quorum_proof_ref(projection: Mapping[str, object]) -> str:
    """Return the canonical SHA-256 reference for a quorum-proof projection."""

    digest = hashlib.sha256(_canonical_json_bytes(projection)).hexdigest()
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
