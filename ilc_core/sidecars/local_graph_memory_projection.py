# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1311 local graph/memory projection sidecar substrate.

This module builds deterministic local-only projection envelopes for graph,
memory, private/gated shard header, and encrypted coordination-node references.
It does not create a server, listener, bind surface, peer discovery path, public
sidecar endpoint, public confidential messaging surface, wallet action, ECU
mint, or ILC settlement surface.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from ilc_core.graph.sidecar_query_runtime import SIDECAR_QUERY_RUNTIME_VERSION


LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION = (
    "local_graph_memory_projection_sidecar_phase_1311.v0.1"
)
PUBLIC_SAFE_PROJECTION_IMPLEMENTATION_LOCAL_ONLY_TOKEN = (
    "public_safe_projection_implementation_local_only_phase_1311"
)
CONFIDENTIAL_COORDINATION_PROJECTION_REFERENCE_LOCAL_ONLY_TOKEN = (
    "confidential_coordination_projection_reference_local_only_phase_1311"
)
PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN = (
    "public_sidecar_projection_serving_not_enabled_phase_1311"
)
PHASE_1312_NEXT_TOKEN = "phase_1312_projection_privacy_field_filtering_tests_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1311_TOKEN = (
    "public_rc_remains_blocked_after_phase_1311"
)
PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION = (
    "projection_privacy_field_filtering_tests_phase_1312.v0.1"
)
PROJECTION_PRIVACY_FILTERS_HARDENED_TOKEN = (
    "projection_privacy_filters_hardened_phase_1312"
)
CONFIDENTIAL_COORDINATION_PROJECTION_NON_LEAKAGE_TESTS_TOKEN = (
    "confidential_coordination_projection_non_leakage_tests_phase_1312"
)
PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_PHASE_1312_TOKEN = (
    "public_sidecar_projection_serving_not_enabled_phase_1312"
)
PHASE_1313_NEXT_TOKEN = "phase_1313_public_fetch_p2p_activation_candidate_default_off_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1312_TOKEN = (
    "public_rc_remains_blocked_after_phase_1312"
)

PUBLIC_SAFE_SCHEMA_DEPENDENCY = "sidecar_public_safe_projection_schema_phase_1297.v0.1"
LOCAL_GRAPH_MEMORY_PROJECTION_REF_PREFIX = "local_graph_memory_projection_sha256"

DEFAULT_LOCAL_GRAPH_MEMORY_PROJECTION_MAX_BYTES = 2_000_000
DEFAULT_LOCAL_GRAPH_MEMORY_PROJECTION_MAX_RECORDS = 1_000

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_COLLECTION_SIZE = 10_000
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_PROTOCOL_INT = 1_000_000_000_000
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_FALSE_AUTHORIZATION_FLAGS = (
    "non_loopback_projection_enabled",
    "peer_discovery_enabled",
    "public_confidential_coordination_serving_enabled",
    "public_confidential_messaging_claimed",
    "public_fetch_serving_enabled",
    "public_listener_enabled",
    "public_p2p_enabled",
    "public_sidecar_projection_serving_enabled",
    "source_allowlist_export_executed",
)
_PROJECTION_ENVELOPE_KEYS = frozenset(
    {
        "authorization_flags",
        "field_policy_ref",
        "local_only",
        "projection_envelope_sha256",
        "projection_epoch",
        "projection_kind",
        "projection_profile",
        "query_result_bytes",
        "query_result_count",
        "records",
        "schema_dependency",
        "source_artifact_root_ref",
        "tokens",
        "version",
    }
)
_RECORD_KEYS_BY_KIND = {
    "aggregate_summary": frozenset(
        {
            "artifact_refs",
            "counts",
            "record_id",
            "record_kind",
            "source_kind",
        }
    ),
    "proof_reference": frozenset(
        {
            "artifact_ref",
            "proof_ref",
            "record_id",
            "record_kind",
        }
    ),
    "private_gated_shard_header": frozenset(
        {
            "capability_policy_ref",
            "encrypted_coordination_refs",
            "record_id",
            "record_kind",
            "shard_commitment_ref",
            "shard_epoch",
            "shard_header_ref",
        }
    ),
    "encrypted_coordination_reference": frozenset(
        {
            "capability_ref",
            "ciphertext_digest_ref",
            "coordination_epoch",
            "encrypted_coordination_ref",
            "record_id",
            "record_kind",
        }
    ),
}
_COUNT_KEYS = frozenset(
    {
        "edge_count",
        "encrypted_coordination_ref_count",
        "hyperedge_count",
        "node_count",
        "private_shard_header_count",
        "query_result_count",
        "record_count",
    }
)
_SOURCE_KINDS = frozenset(
    {
        "local_sidecar_query_result",
        "local_graph_projection",
        "local_memory_projection",
        "release_eligible_artifact_summary",
    }
)
_FORBIDDEN_PRIVATE_KEYS = frozenset(
    {
        "AgentID",
        "agent_id",
        "agentid",
        "capability_membership",
        "ciphertext",
        "client_ip",
        "creator_agent_id",
        "economic_position",
        "graph_position",
        "group_membership",
        "harness_identity",
        "ip_address",
        "json_body_requester_id",
        "membership",
        "membership_set",
        "openclaw_identity",
        "plaintext",
        "plaintext_payload",
        "private_graph_membership",
        "private_graph_position",
        "raw_node_id",
        "raw_sealed_payload",
        "requester_id",
        "route_history",
        "sealed_payload",
        "stake",
        "stake_balance",
        "tailscale_identity",
        "wallet",
        "wallet_address",
        "wallet_balance",
    }
)
_PUBLIC_EXPORT_FORBIDDEN_FRAGMENTS = frozenset(
    {
        "agent_id",
        "agentid",
        "client_ip",
        "creator_agent_id",
        "economic_position",
        "edge:",
        "graph_position",
        "group_membership",
        "harness_identity",
        "membership",
        "membership_set",
        "node:",
        "openclaw_identity",
        "plaintext",
        "plaintext_payload",
        "private-node",
        "private_graph_membership",
        "private_graph_position",
        "raw_node_id",
        "raw_sealed_payload",
        "requester_id",
        "route_history",
        "sealed_payload",
        "stake_balance",
        "tailscale_identity",
        "wallet",
        "wallet_address",
        "wallet_balance",
    }
)


class LocalGraphMemoryProjectionError(ValueError):
    """Fail-closed local projection error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def local_graph_memory_projection_required_tokens() -> list[str]:
    return [
        LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION,
        PUBLIC_SAFE_PROJECTION_IMPLEMENTATION_LOCAL_ONLY_TOKEN,
        CONFIDENTIAL_COORDINATION_PROJECTION_REFERENCE_LOCAL_ONLY_TOKEN,
        PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN,
        PHASE_1312_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1311_TOKEN,
    ]


def projection_privacy_field_filtering_required_tokens() -> list[str]:
    return [
        PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION,
        PROJECTION_PRIVACY_FILTERS_HARDENED_TOKEN,
        CONFIDENTIAL_COORDINATION_PROJECTION_NON_LEAKAGE_TESTS_TOKEN,
        PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_PHASE_1312_TOKEN,
        PHASE_1313_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1312_TOKEN,
    ]


def projection_privacy_forbidden_fragments() -> list[str]:
    return sorted(_PUBLIC_EXPORT_FORBIDDEN_FRAGMENTS)


def local_graph_memory_projection_sidecar_manifest() -> dict[str, Any]:
    """Return deterministic local-only projection sidecar metadata."""

    manifest = {
        "allowed_binding_modes": [
            "in_process_import",
            "local_cli_subprocess",
            "private_loopback_or_private_overlay_when_authorized_by_harness",
        ],
        "contract_version": LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION,
        "bounded_projection_serving_blocker_tests_hardened": True,
        "confidential_coordination_projection_non_leakage_tests": True,
        "field_policy": "deny_by_default_exact_record_schema_phase_1311",
        "local_only": True,
        "max_projection_bytes": DEFAULT_LOCAL_GRAPH_MEMORY_PROJECTION_MAX_BYTES,
        "max_projection_records": DEFAULT_LOCAL_GRAPH_MEMORY_PROJECTION_MAX_RECORDS,
        "phase_1312_tokens": sorted(projection_privacy_field_filtering_required_tokens()),
        "private_gated_shard_header_projection_supported": True,
        "projection_privacy_field_filtering_tests_version": (
            PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION
        ),
        "projection_privacy_filtering_hardened": True,
        "projection_privacy_forbidden_fragment_count": len(
            _PUBLIC_EXPORT_FORBIDDEN_FRAGMENTS
        ),
        "public_confidential_coordination_serving_enabled": False,
        "public_confidential_messaging_claimed": False,
        "public_fetch_serving_enabled": False,
        "public_listener_enabled": False,
        "public_p2p_enabled": False,
        "public_safe_projection_local_only": True,
        "public_sidecar_projection_serving_enabled": False,
        "public_sidecar_projection_serving_phase_1312_token": (
            PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_PHASE_1312_TOKEN
        ),
        "schema_dependency": PUBLIC_SAFE_SCHEMA_DEPENDENCY,
        "source_query_runtime_version": SIDECAR_QUERY_RUNTIME_VERSION,
        "tokens": sorted(local_graph_memory_projection_required_tokens()),
    }
    _reject_unsafe_json_tree(manifest)
    return manifest


def build_aggregate_summary_record_from_query_result(
    query_result: Mapping[str, Any],
    *,
    record_id: str,
    artifact_refs: Sequence[str] = (),
    source_kind: str = "local_sidecar_query_result",
) -> dict[str, Any]:
    """Summarize a local query result without passing through raw graph fields."""

    _reject_unsafe_json_tree(query_result)
    _reject_forbidden_private_keys(query_result)
    counts: dict[str, int] = {}
    for output_key, input_key in (
        ("node_count", "node_count"),
        ("edge_count", "edge_count"),
        ("hyperedge_count", "hyperedge_count"),
    ):
        value = query_result.get(input_key)
        if value is not None:
            counts[output_key] = _require_non_negative_int(output_key, value)
    counts["query_result_count"] = 1
    return validate_local_graph_memory_projection_record(
        {
            "artifact_refs": list(artifact_refs),
            "counts": counts,
            "record_id": record_id,
            "record_kind": "aggregate_summary",
            "source_kind": source_kind,
        }
    )


def build_private_gated_shard_header_record(
    *,
    record_id: str,
    shard_header_ref: str,
    shard_commitment_ref: str,
    capability_policy_ref: str,
    shard_epoch: int,
    encrypted_coordination_refs: Sequence[str] = (),
) -> dict[str, Any]:
    return validate_local_graph_memory_projection_record(
        {
            "capability_policy_ref": capability_policy_ref,
            "encrypted_coordination_refs": list(encrypted_coordination_refs),
            "record_id": record_id,
            "record_kind": "private_gated_shard_header",
            "shard_commitment_ref": shard_commitment_ref,
            "shard_epoch": shard_epoch,
            "shard_header_ref": shard_header_ref,
        }
    )


def build_encrypted_coordination_reference_record(
    *,
    record_id: str,
    encrypted_coordination_ref: str,
    ciphertext_digest_ref: str,
    capability_ref: str,
    coordination_epoch: int,
) -> dict[str, Any]:
    return validate_local_graph_memory_projection_record(
        {
            "capability_ref": capability_ref,
            "ciphertext_digest_ref": ciphertext_digest_ref,
            "coordination_epoch": coordination_epoch,
            "encrypted_coordination_ref": encrypted_coordination_ref,
            "record_id": record_id,
            "record_kind": "encrypted_coordination_reference",
        }
    )


def build_public_safe_projection_envelope(
    *,
    projection_epoch: int,
    source_artifact_root_ref: str,
    records: Sequence[Mapping[str, Any]],
    projection_profile: str = "local_graph_memory_public_safe_projection",
    projection_kind: str = "local_graph_memory_projection",
    field_policy_ref: str = (
        "field_policy:public_safe_projection_implementation_local_only_phase_1311"
    ),
    max_records: int = DEFAULT_LOCAL_GRAPH_MEMORY_PROJECTION_MAX_RECORDS,
    max_bytes: int = DEFAULT_LOCAL_GRAPH_MEMORY_PROJECTION_MAX_BYTES,
) -> dict[str, Any]:
    """Build a canonical local-only public-safe projection envelope."""

    epoch = _require_epoch("projection", projection_epoch)
    record_limit = _require_positive_int("max_records", max_records)
    byte_limit = _require_non_negative_int("max_bytes", max_bytes)
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_records_invalid_phase_1311",
            "projection records must be a bounded sequence",
        )
    if len(records) > record_limit or len(records) > _MAX_COLLECTION_SIZE:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_record_count_exceeded_phase_1311",
            "projection record count exceeds the local bound",
        )
    normalized_records = [
        validate_local_graph_memory_projection_record(record)
        for record in records
    ]
    records_payload = canonical_local_graph_memory_projection_json(normalized_records)
    query_result_bytes = len(records_payload.encode("utf-8"))
    if query_result_bytes > byte_limit:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_size_exceeded_phase_1311",
            "projection records exceed the local byte bound",
        )
    authorization_flags = {key: False for key in _FALSE_AUTHORIZATION_FLAGS}
    body = {
        "authorization_flags": authorization_flags,
        "field_policy_ref": _require_policy_ref(field_policy_ref),
        "local_only": True,
        "projection_epoch": epoch,
        "projection_kind": _require_choice(
            "projection_kind",
            projection_kind,
            allowed=("local_graph_memory_projection", "confidential_coordination_projection"),
            token="local_graph_memory_projection_kind_invalid_phase_1311",
        ),
        "projection_profile": _require_choice(
            "projection_profile",
            projection_profile,
            allowed=(
                "local_graph_memory_public_safe_projection",
                "confidential_coordination_local_preview",
            ),
            token="local_graph_memory_projection_profile_invalid_phase_1311",
        ),
        "query_result_bytes": query_result_bytes,
        "query_result_count": len(normalized_records),
        "records": normalized_records,
        "schema_dependency": PUBLIC_SAFE_SCHEMA_DEPENDENCY,
        "source_artifact_root_ref": _require_prefixed_digest(
            "source_artifact_root_ref",
            source_artifact_root_ref,
            allowed_prefixes=("artifact", "manifest", "root"),
        ),
        "tokens": sorted(local_graph_memory_projection_required_tokens()),
        "version": LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION,
    }
    envelope = {"projection_envelope_sha256": _sha256_payload(body), **body}
    return validate_public_safe_projection_envelope(envelope, projection_epoch=epoch)


def validate_local_graph_memory_projection_record(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_record_invalid_phase_1311",
            "projection record must be a mapping",
        )
    _reject_unsafe_json_tree(record)
    _reject_forbidden_private_keys(record)
    payload = dict(record)
    kind = _require_text(payload.get("record_kind"))
    expected_keys = _RECORD_KEYS_BY_KIND.get(kind)
    if expected_keys is None:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_record_kind_invalid_phase_1311",
            "projection record kind is not supported",
        )
    if set(payload) != expected_keys:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_record_keys_invalid_phase_1311",
            "projection record keys do not match the Phase 1311 contract",
        )
    if kind == "aggregate_summary":
        return {
            "artifact_refs": _normalize_ref_list(
                payload.get("artifact_refs"),
                token="local_graph_memory_projection_artifact_refs_invalid_phase_1311",
                allowed_prefixes=("artifact", "manifest", "proof", "root"),
            ),
            "counts": _normalize_counts(payload.get("counts")),
            "record_id": _require_prefixed_digest(
                "record_id",
                payload.get("record_id"),
                allowed_prefixes=("record",),
            ),
            "record_kind": kind,
            "source_kind": _require_choice(
                "source_kind",
                payload.get("source_kind"),
                allowed=_SOURCE_KINDS,
                token="local_graph_memory_projection_source_kind_invalid_phase_1311",
            ),
        }
    if kind == "proof_reference":
        return {
            "artifact_ref": _require_prefixed_digest(
                "artifact_ref",
                payload.get("artifact_ref"),
                allowed_prefixes=("artifact", "manifest", "root"),
            ),
            "proof_ref": _require_prefixed_digest(
                "proof_ref",
                payload.get("proof_ref"),
                allowed_prefixes=("proof",),
            ),
            "record_id": _require_prefixed_digest(
                "record_id",
                payload.get("record_id"),
                allowed_prefixes=("record",),
            ),
            "record_kind": kind,
        }
    if kind == "private_gated_shard_header":
        return {
            "capability_policy_ref": _require_prefixed_digest(
                "capability_policy_ref",
                payload.get("capability_policy_ref"),
                allowed_prefixes=("capability_policy",),
            ),
            "encrypted_coordination_refs": _normalize_ref_list(
                payload.get("encrypted_coordination_refs"),
                token="local_graph_memory_projection_encrypted_refs_invalid_phase_1311",
                allowed_prefixes=("encrypted_coordination",),
            ),
            "record_id": _require_prefixed_digest(
                "record_id",
                payload.get("record_id"),
                allowed_prefixes=("record",),
            ),
            "record_kind": kind,
            "shard_commitment_ref": _require_prefixed_digest(
                "shard_commitment_ref",
                payload.get("shard_commitment_ref"),
                allowed_prefixes=("shard_commitment",),
            ),
            "shard_epoch": _require_epoch("shard", payload.get("shard_epoch")),
            "shard_header_ref": _require_prefixed_digest(
                "shard_header_ref",
                payload.get("shard_header_ref"),
                allowed_prefixes=("private_shard_header",),
            ),
        }
    return {
        "capability_ref": _require_prefixed_digest(
            "capability_ref",
            payload.get("capability_ref"),
            allowed_prefixes=("capability",),
        ),
        "ciphertext_digest_ref": _require_prefixed_digest(
            "ciphertext_digest_ref",
            payload.get("ciphertext_digest_ref"),
            allowed_prefixes=("ciphertext",),
        ),
        "coordination_epoch": _require_epoch("coordination", payload.get("coordination_epoch")),
        "encrypted_coordination_ref": _require_prefixed_digest(
            "encrypted_coordination_ref",
            payload.get("encrypted_coordination_ref"),
            allowed_prefixes=("encrypted_coordination",),
        ),
        "record_id": _require_prefixed_digest(
            "record_id",
            payload.get("record_id"),
            allowed_prefixes=("record",),
        ),
        "record_kind": kind,
    }


def validate_public_safe_projection_envelope(
    envelope: Mapping[str, Any],
    *,
    projection_epoch: int,
) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_envelope_invalid_phase_1311",
            "projection envelope must be a mapping",
        )
    _reject_unsafe_json_tree(envelope)
    _reject_forbidden_private_keys(envelope)
    payload = dict(envelope)
    if set(payload) != _PROJECTION_ENVELOPE_KEYS:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_envelope_keys_invalid_phase_1311",
            "projection envelope keys do not match the Phase 1311 contract",
        )
    epoch = _require_epoch("projection", projection_epoch)
    if _require_epoch("projection", payload.get("projection_epoch")) != epoch:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_epoch_mismatch_phase_1311",
            "projection epoch does not match caller epoch",
        )
    if payload.get("version") != LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_version_invalid_phase_1311",
            "projection envelope version is invalid",
        )
    if payload.get("schema_dependency") != PUBLIC_SAFE_SCHEMA_DEPENDENCY:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_schema_dependency_invalid_phase_1311",
            "projection schema dependency is invalid",
        )
    if payload.get("local_only") is not True:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_local_only_required_phase_1311",
            "projection envelope must remain local-only",
        )
    normalized = {
        "authorization_flags": _normalize_authorization_flags(payload.get("authorization_flags")),
        "field_policy_ref": _require_policy_ref(payload.get("field_policy_ref")),
        "local_only": True,
        "projection_envelope_sha256": _require_hex_digest(
            "projection_envelope_sha256",
            payload.get("projection_envelope_sha256"),
        ),
        "projection_epoch": epoch,
        "projection_kind": _require_choice(
            "projection_kind",
            payload.get("projection_kind"),
            allowed=("local_graph_memory_projection", "confidential_coordination_projection"),
            token="local_graph_memory_projection_kind_invalid_phase_1311",
        ),
        "projection_profile": _require_choice(
            "projection_profile",
            payload.get("projection_profile"),
            allowed=(
                "local_graph_memory_public_safe_projection",
                "confidential_coordination_local_preview",
            ),
            token="local_graph_memory_projection_profile_invalid_phase_1311",
        ),
        "query_result_bytes": _require_non_negative_int(
            "query_result_bytes",
            payload.get("query_result_bytes"),
        ),
        "query_result_count": _require_non_negative_int(
            "query_result_count",
            payload.get("query_result_count"),
        ),
        "records": [
            validate_local_graph_memory_projection_record(record)
            for record in _require_sequence(
                payload.get("records"),
                token="local_graph_memory_projection_records_invalid_phase_1311",
            )
        ],
        "schema_dependency": PUBLIC_SAFE_SCHEMA_DEPENDENCY,
        "source_artifact_root_ref": _require_prefixed_digest(
            "source_artifact_root_ref",
            payload.get("source_artifact_root_ref"),
            allowed_prefixes=("artifact", "manifest", "root"),
        ),
        "tokens": _normalize_exact_text_list(
            payload.get("tokens"),
            expected=local_graph_memory_projection_required_tokens(),
            token="local_graph_memory_projection_tokens_invalid_phase_1311",
        ),
        "version": LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION,
    }
    records_payload = canonical_local_graph_memory_projection_json(normalized["records"])
    if normalized["query_result_count"] != len(normalized["records"]):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_count_mismatch_phase_1311",
            "query result count does not match record count",
        )
    if normalized["query_result_bytes"] != len(records_payload.encode("utf-8")):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_size_mismatch_phase_1311",
            "query result byte count does not match canonical records",
        )
    expected_hash_body = dict(normalized)
    actual_hash = expected_hash_body.pop("projection_envelope_sha256")
    if actual_hash != _sha256_payload(expected_hash_body):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_envelope_hash_mismatch_phase_1311",
            "projection envelope hash does not match canonical body",
        )
    return normalized


def local_graph_memory_projection_ref(envelope: Mapping[str, Any]) -> str:
    if not isinstance(envelope, Mapping):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_envelope_invalid_phase_1311",
            "projection envelope must be a mapping",
        )
    validated = validate_public_safe_projection_envelope(
        envelope,
        projection_epoch=_require_epoch("projection", envelope.get("projection_epoch")),
    )
    return f"{LOCAL_GRAPH_MEMORY_PROJECTION_REF_PREFIX}:{validated['projection_envelope_sha256']}"


def canonical_local_graph_memory_projection_json(payload: object) -> str:
    validate_projection_privacy_filtering_payload(payload)
    canonical = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_payload_size_exceeded_phase_1311",
            "canonical projection JSON exceeds the byte bound",
        )
    return canonical


def validate_projection_privacy_filtering_payload(payload: object) -> None:
    _reject_unsafe_json_tree(payload)
    _reject_forbidden_private_keys(payload)
    _reject_public_export_fragments(payload)


def export_public_safe_projection_envelope_json(envelope: Mapping[str, Any]) -> str:
    if not isinstance(envelope, Mapping):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_envelope_invalid_phase_1311",
            "projection envelope must be a mapping",
        )
    validated = validate_public_safe_projection_envelope(
        envelope,
        projection_epoch=_require_epoch("projection", envelope.get("projection_epoch")),
    )
    return canonical_local_graph_memory_projection_json(validated)


def _normalize_authorization_flags(value: object) -> dict[str, bool]:
    flags = _require_mapping(
        value,
        token="local_graph_memory_projection_authorization_flags_invalid_phase_1311",
    )
    if set(flags) != set(_FALSE_AUTHORIZATION_FLAGS):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_authorization_flags_invalid_phase_1311",
            "authorization flag keys are invalid",
        )
    normalized: dict[str, bool] = {}
    for key in _FALSE_AUTHORIZATION_FLAGS:
        if flags.get(key) is not False:
            raise LocalGraphMemoryProjectionError(
                PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN,
                f"{key} must be false",
            )
        normalized[key] = False
    return normalized


def _normalize_counts(value: object) -> dict[str, int]:
    counts = _require_mapping(
        value,
        token="local_graph_memory_projection_counts_invalid_phase_1311",
    )
    if not counts:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_counts_invalid_phase_1311",
            "counts must not be empty",
        )
    if not set(counts) <= _COUNT_KEYS:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_counts_invalid_phase_1311",
            "count keys are not public-safe",
        )
    return {
        key: _require_non_negative_int(key, counts[key])
        for key in sorted(counts)
    }


def _normalize_ref_list(value: object, *, token: str, allowed_prefixes: Sequence[str]) -> list[str]:
    refs = _require_sequence(value, token=token)
    if len(refs) > _MAX_COLLECTION_SIZE:
        raise LocalGraphMemoryProjectionError(token, "reference list is too large")
    normalized = [
        _require_prefixed_digest("ref", item, allowed_prefixes=allowed_prefixes)
        for item in refs
    ]
    if normalized != sorted(normalized) or len(set(normalized)) != len(normalized):
        raise LocalGraphMemoryProjectionError(token, "reference list must be sorted and unique")
    return normalized


def _normalize_exact_text_list(value: object, *, expected: Sequence[str], token: str) -> list[str]:
    refs = _require_sequence(value, token=token)
    normalized = [_require_text(item) for item in refs]
    expected_list = sorted(_require_text(item) for item in expected)
    if normalized != expected_list:
        raise LocalGraphMemoryProjectionError(token, "text list does not match contract")
    return normalized


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise LocalGraphMemoryProjectionError(token, "value must be a mapping")
    return value


def _require_sequence(value: object, *, token: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise LocalGraphMemoryProjectionError(token, "value must be a bounded sequence")
    if len(value) > _MAX_COLLECTION_SIZE:
        raise LocalGraphMemoryProjectionError(token, "sequence is too large")
    return value


def _require_choice(name: str, value: object, *, allowed: Sequence[str] | frozenset[str], token: str) -> str:
    text = _require_text(value)
    if text not in set(allowed):
        raise LocalGraphMemoryProjectionError(token, f"{name} is not allowed")
    return text


def _require_epoch(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > _MAX_PROTOCOL_INT
    ):
        raise LocalGraphMemoryProjectionError(
            f"local_graph_memory_projection_{name}_epoch_invalid_phase_1311",
            f"{name} epoch must be a positive bounded integer",
        )
    return value


def _require_positive_int(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
        or value > _MAX_PROTOCOL_INT
    ):
        raise LocalGraphMemoryProjectionError(
            f"local_graph_memory_projection_{name}_invalid_phase_1311",
            f"{name} must be a positive integer",
        )
    return value


def _require_non_negative_int(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > _MAX_PROTOCOL_INT
    ):
        raise LocalGraphMemoryProjectionError(
            f"local_graph_memory_projection_{name}_invalid_phase_1311",
            f"{name} must be a non-negative integer",
        )
    return value


def _require_policy_ref(value: object) -> str:
    text = _require_text(value)
    if text != "field_policy:public_safe_projection_implementation_local_only_phase_1311":
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_field_policy_invalid_phase_1311",
            "field policy ref is invalid",
        )
    return text


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_text_invalid_phase_1311",
            "text value is invalid",
        )
    if any(ord(char) < 0x20 or char == "\x7f" for char in value):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_text_invalid_phase_1311",
            "text value must not contain control characters",
        )
    if len(value) > _MAX_TEXT_LENGTH:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_text_too_large_phase_1311",
            "text value is too large",
        )
    return value


def _require_hex_digest(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _HEX_DIGEST_LENGTH
        or any(char not in _HEX for char in value)
    ):
        raise LocalGraphMemoryProjectionError(
            f"local_graph_memory_projection_{name}_invalid_phase_1311",
            f"{name} must be a lowercase sha256 hex digest",
        )
    return value


def _require_prefixed_digest(
    name: str,
    value: object,
    *,
    allowed_prefixes: Sequence[str],
) -> str:
    text = _require_text(value)
    for prefix in allowed_prefixes:
        expected_prefix = f"{prefix}:"
        if text.startswith(expected_prefix):
            _require_hex_digest(name, text[len(expected_prefix) :])
            return text
    raise LocalGraphMemoryProjectionError(
        f"local_graph_memory_projection_{name}_invalid_phase_1311",
        f"{name} has an invalid digest prefix",
    )


def _sha256_payload(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_local_graph_memory_projection_json(value).encode("utf-8")).hexdigest()


def _reject_forbidden_private_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in _FORBIDDEN_PRIVATE_KEYS:
                raise LocalGraphMemoryProjectionError(
                    "local_graph_memory_projection_private_field_forbidden_phase_1311",
                    "projection includes a forbidden private, identity, or payload field",
                )
            _reject_forbidden_private_keys(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_forbidden_private_keys(item)


def _reject_public_export_fragments(value: object) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_public_export_text(key)
            _reject_public_export_fragments(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_public_export_fragments(item)
        return
    if isinstance(value, str):
        _reject_public_export_text(value)


def _reject_public_export_text(value: str) -> None:
    normalized = value.lower()
    if any(fragment in normalized for fragment in _PUBLIC_EXPORT_FORBIDDEN_FRAGMENTS):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_private_fragment_forbidden_phase_1312",
            "projection includes a forbidden private, identity, route, or payload fragment",
        )


def _reject_unsafe_json_tree(
    value: object,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_PAYLOAD_DEPTH:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_payload_too_deep_phase_1311",
            "payload nesting is too deep",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_PAYLOAD_NODES:
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_payload_too_large_phase_1311",
            "payload has too many nodes",
        )
    if isinstance(value, float):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_float_values_forbidden_phase_1311",
            "float values are not allowed in projection payloads",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_PROTOCOL_INT:
            raise LocalGraphMemoryProjectionError(
                "local_graph_memory_projection_payload_int_invalid_phase_1311",
                "integer values must be non-negative and bounded",
            )
        return
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise LocalGraphMemoryProjectionError(
                "local_graph_memory_projection_payload_cycle_forbidden_phase_1311",
                "mapping cycle is not allowed",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise LocalGraphMemoryProjectionError(
                        "local_graph_memory_projection_payload_key_invalid_phase_1311",
                        "mapping keys must be strings",
                    )
                _require_text(key)
                _counter[0] += 1
                if _counter[0] > _MAX_PAYLOAD_NODES:
                    raise LocalGraphMemoryProjectionError(
                        "local_graph_memory_projection_payload_too_large_phase_1311",
                        "payload has too many nodes",
                    )
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, tuple):
        raise LocalGraphMemoryProjectionError(
            "local_graph_memory_projection_tuple_values_forbidden_phase_1311",
            "tuple values are not canonical JSON",
        )
    if isinstance(value, list):
        object_id = id(value)
        if object_id in _seen:
            raise LocalGraphMemoryProjectionError(
                "local_graph_memory_projection_payload_cycle_forbidden_phase_1311",
                "list cycle is not allowed",
            )
        _seen.add(object_id)
        try:
            for item in value:
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, str):
        _require_text(value)
        return
    if value is None:
        return
    raise LocalGraphMemoryProjectionError(
        "local_graph_memory_projection_payload_type_invalid_phase_1311",
        "payload contains a non-JSON value type",
    )


__all__ = [
    "CONFIDENTIAL_COORDINATION_PROJECTION_REFERENCE_LOCAL_ONLY_TOKEN",
    "LOCAL_GRAPH_MEMORY_PROJECTION_REF_PREFIX",
    "LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION",
    "LocalGraphMemoryProjectionError",
    "PHASE_1312_NEXT_TOKEN",
    "PHASE_1313_NEXT_TOKEN",
    "PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION",
    "PROJECTION_PRIVACY_FILTERS_HARDENED_TOKEN",
    "CONFIDENTIAL_COORDINATION_PROJECTION_NON_LEAKAGE_TESTS_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1311_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1312_TOKEN",
    "PUBLIC_SAFE_PROJECTION_IMPLEMENTATION_LOCAL_ONLY_TOKEN",
    "PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_PHASE_1312_TOKEN",
    "PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN",
    "build_aggregate_summary_record_from_query_result",
    "build_encrypted_coordination_reference_record",
    "build_private_gated_shard_header_record",
    "build_public_safe_projection_envelope",
    "canonical_local_graph_memory_projection_json",
    "export_public_safe_projection_envelope_json",
    "local_graph_memory_projection_ref",
    "local_graph_memory_projection_required_tokens",
    "local_graph_memory_projection_sidecar_manifest",
    "projection_privacy_field_filtering_required_tokens",
    "projection_privacy_forbidden_fragments",
    "validate_local_graph_memory_projection_record",
    "validate_projection_privacy_filtering_payload",
    "validate_public_safe_projection_envelope",
]
