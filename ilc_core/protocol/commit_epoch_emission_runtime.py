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
COMMIT_EPOCH_CAUSAL_FRONTIER_PROJECTION_VERSION = "commit_epoch_causal_frontier_projection_1236_fix3.v0.1"
COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION = "commit_epoch_finalized_adapter_1236_fix4.v0.1"
COMMIT_EPOCH_CAUSAL_FRONTIER_SCHEMA_VERSION = "commit_epoch_causal_frontier_mapping_1226.v0.1"
COMMIT_EPOCH_TIMESTAMP_POLICY = "epoch_sequence_only_no_wall_clock"
COMMIT_EPOCH_ISSUER = "consensus_layer"
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


def _require_sha256_ref(value: object, token: str) -> str:
    text = _require_optional_sha256_ref(value, token)
    if text is None:
        raise ValueError(token)
    suffix = text.removeprefix("sha256:")
    if len(suffix) != 64:
        raise ValueError(token)
    return text


def _require_genesis_domain_hash(value: object, token: str) -> str:
    text = _require_lower_hex(value, token)
    if len(text) != 64:
        raise ValueError(token)
    return text


def _require_state_root_cidv1_hex(value: object, token: str) -> str:
    text = _require_lower_hex(value, token)
    if len(text) != 72:
        raise ValueError(token)
    return text


def _normalize_causal_frontier_refs(refs: object, *, genesis_domain_hash: str, epoch_sequence: int) -> list[str]:
    expected_genesis_ref = f"genesis_root:{genesis_domain_hash}"
    if epoch_sequence == 0:
        if refs != [expected_genesis_ref]:
            raise ValueError("causal_frontier_refs_genesis_must_equal_domain_anchor")
        return [expected_genesis_ref]
    if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes, bytearray)):
        raise ValueError("causal_frontier_refs_must_be_sequence")
    if len(refs) == 0:
        raise ValueError("causal_frontier_refs_must_be_non_empty")
    return [
        _require_sha256_ref(ref, "causal_frontier_ref_invalid")
        for ref in refs
    ]


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
        "state_root_cidv1_hex": _require_state_root_cidv1_hex(
            state_root_cidv1_hex,
            "quorum_projection_state_root_cidv1_hex_invalid",
        ),
    }


def compute_quorum_proof_ref(projection: Mapping[str, object]) -> str:
    """Return the canonical SHA-256 reference for a quorum-proof projection."""

    digest = hashlib.sha256(_canonical_json_bytes(projection)).hexdigest()
    return f"sha256:{digest}"


def build_commit_epoch_causal_frontier_projection(
    *,
    epoch_sequence: int,
    state_root_cidv1_hex: str | None,
    causal_predecessor_ref: str | None,
    quorum_proof_ref: str | None,
    causal_frontier_refs: Sequence[str],
    genesis_domain_hash: str,
) -> dict[str, object]:
    """Build the canonical Layer-C causal-frontier projection.

    Genesis epoch-zero is the only case that allows nullable consensus refs.
    Post-Genesis epochs must carry explicit predecessor, quorum, and state-root
    material. This helper only renders deterministic projection data.
    """

    normalized_epoch_sequence = _require_non_negative_int(
        epoch_sequence,
        "causal_frontier_epoch_sequence_must_be_non_negative_int",
    )
    normalized_genesis_domain_hash = _require_genesis_domain_hash(
        genesis_domain_hash,
        "causal_frontier_genesis_domain_hash_invalid",
    )

    if normalized_epoch_sequence == 0:
        if state_root_cidv1_hex is not None:
            raise ValueError("causal_frontier_genesis_state_root_must_be_null")
        if causal_predecessor_ref is not None:
            raise ValueError("causal_frontier_genesis_predecessor_must_be_null")
        if quorum_proof_ref is not None:
            raise ValueError("causal_frontier_genesis_quorum_proof_must_be_null")
        normalized_state_root: str | None = None
        normalized_predecessor: str | None = None
        normalized_quorum_proof: str | None = None
    else:
        if state_root_cidv1_hex is None:
            raise ValueError("causal_frontier_state_root_required")
        normalized_state_root = _require_state_root_cidv1_hex(
            state_root_cidv1_hex,
            "causal_frontier_state_root_cidv1_hex_invalid",
        )
        normalized_predecessor = _require_sha256_ref(
            causal_predecessor_ref,
            "causal_frontier_predecessor_ref_invalid",
        )
        normalized_quorum_proof = _require_sha256_ref(
            quorum_proof_ref,
            "causal_frontier_quorum_proof_ref_invalid",
        )

    return {
        "causal_frontier_refs": _normalize_causal_frontier_refs(
            causal_frontier_refs,
            genesis_domain_hash=normalized_genesis_domain_hash,
            epoch_sequence=normalized_epoch_sequence,
        ),
        "causal_predecessor_ref": normalized_predecessor,
        "epoch_sequence": normalized_epoch_sequence,
        "event_kind": "commit.epoch",
        "genesis_domain_hash": normalized_genesis_domain_hash,
        "issuer": COMMIT_EPOCH_ISSUER,
        "quorum_proof_ref": normalized_quorum_proof,
        "schema_version": COMMIT_EPOCH_CAUSAL_FRONTIER_SCHEMA_VERSION,
        "state_root_cidv1_hex": normalized_state_root,
        "timestamp_policy": COMMIT_EPOCH_TIMESTAMP_POLICY,
    }


def compute_causal_frontier_ref(projection: Mapping[str, object]) -> str:
    """Return the canonical SHA-256 reference for a causal-frontier projection."""

    digest = hashlib.sha256(_canonical_json_bytes(projection)).hexdigest()
    return f"sha256:{digest}"


def _require_non_empty_quorum_records_for_adapter(
    quorum_records: object,
    epoch_index: int,
) -> tuple[Mapping[str, Any], ...]:
    normalized = _validate_quorum_records(quorum_records, epoch_index)
    if len(normalized) == 0:
        raise ValueError("finalized_epoch_adapter_quorum_records_empty")
    return normalized


def _validate_adapter_finalization_state(
    quorum_records: Sequence[Mapping[str, Any]],
    finalization_state: str,
) -> None:
    if finalization_state not in _ALLOWED_FINALIZATION_STATES:
        raise ValueError("finalization_state_invalid")
    for record in quorum_records:
        record_state = record.get("finalization_state")
        if record_state is not None and record_state != finalization_state:
            raise ValueError("finalized_epoch_adapter_conflicting_finalization_state")


def _require_quorum_ref_in_frontier_refs(quorum_ref: str, frontier_refs: object) -> Sequence[str]:
    if not isinstance(frontier_refs, Sequence) or isinstance(frontier_refs, (str, bytes, bytearray)):
        raise ValueError("finalized_epoch_adapter_frontier_refs_must_be_sequence")
    if quorum_ref not in frontier_refs:
        raise ValueError("finalized_epoch_adapter_quorum_proof_ref_missing_from_frontier")
    return frontier_refs


def adapt_finalized_epoch_to_connector_inputs(
    *,
    epoch_index: int,
    epoch_id: str,
    namespace_id: str,
    finalization_state: str,
    quorum_records: Sequence[Mapping[str, Any]],
    state_root_cidv1_hex: str,
    agg_sig_bytes_hex: str,
    signers: Sequence[int],
    source_record_digest: str | None,
    causal_predecessor_ref: str | None,
    causal_frontier_refs: Sequence[str],
    genesis_domain_hash: str,
    reward_total: Decimal,
    stake_total: Decimal,
    task_count: int,
    agent_count: int,
) -> dict[str, Any]:
    """Compose finalized epoch inputs through Layers A-C.

    This adapter is still a pure projection helper. It does not read Rust state,
    verify BLS signatures, write consensus records, or authorize production
    emission.
    """

    normalized_epoch_index = _require_non_negative_int(
        epoch_index,
        "epoch_index_must_be_non_negative_int",
    )
    if normalized_epoch_index == 0:
        raise ValueError("finalized_epoch_adapter_genesis_epoch_zero_unsupported")
    normalized_quorum_records = _require_non_empty_quorum_records_for_adapter(
        quorum_records,
        normalized_epoch_index,
    )
    _validate_adapter_finalization_state(normalized_quorum_records, finalization_state)

    quorum_projection = build_quorum_proof_projection(
        epoch_sequence=normalized_epoch_index,
        state_root_cidv1_hex=state_root_cidv1_hex,
        signers=signers,
        agg_sig_bytes_hex=agg_sig_bytes_hex,
        source_record_digest=source_record_digest,
    )
    quorum_proof_ref = compute_quorum_proof_ref(quorum_projection)
    normalized_frontier_refs = _require_quorum_ref_in_frontier_refs(
        quorum_proof_ref,
        causal_frontier_refs,
    )
    causal_frontier_projection = build_commit_epoch_causal_frontier_projection(
        epoch_sequence=normalized_epoch_index,
        state_root_cidv1_hex=state_root_cidv1_hex,
        causal_predecessor_ref=causal_predecessor_ref,
        quorum_proof_ref=quorum_proof_ref,
        causal_frontier_refs=normalized_frontier_refs,
        genesis_domain_hash=genesis_domain_hash,
    )
    causal_frontier_ref = compute_causal_frontier_ref(causal_frontier_projection)
    commit_epoch_event = build_commit_epoch_event(
        epoch_index=normalized_epoch_index,
        epoch_id=epoch_id,
        namespace_id=namespace_id,
        finalization_state=finalization_state,
        quorum_records=normalized_quorum_records,
        epoch_state_digest=causal_frontier_ref,
        epoch_events_digest=quorum_proof_ref,
        reward_total=reward_total,
        stake_total=stake_total,
        task_count=task_count,
        agent_count=agent_count,
    )
    return {
        "adapter_version": COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION,
        "causal_frontier_projection": causal_frontier_projection,
        "causal_frontier_ref": causal_frontier_ref,
        "commit_epoch_event": commit_epoch_event,
        "quorum_proof_projection": quorum_projection,
        "quorum_proof_ref": quorum_proof_ref,
    }


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
