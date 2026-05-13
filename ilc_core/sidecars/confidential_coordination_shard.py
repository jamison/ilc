"""Phase 1324 CCSS-001 private/gated shard contract.

This module records a local-only contract for encrypted coordination-node
envelopes, private/gated shard header projection, and promotion-evidence
references. It does not encrypt payloads, serve confidential coordination,
open public P2P, promote private nodes, publish shard contents, or authorize
public availability.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any


CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION = (
    "ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1"
)
ENCRYPTED_COORDINATION_NODE_ENVELOPE_CONTRACT_RECORDED_TOKEN = (
    "encrypted_coordination_node_envelope_contract_recorded_phase_1324"
)
SHARD_HEADER_PROJECTION_CONTRACT_RECORDED_TOKEN = (
    "shard_header_projection_contract_recorded_phase_1324"
)
PRIVATE_TO_PUBLIC_PROMOTION_EVIDENCE_SHAPE_RECORDED_TOKEN = (
    "private_to_public_promotion_evidence_shape_recorded_phase_1324"
)
CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN = "ccss_public_serving_not_enabled_phase_1324"
PHASE_1325_NEXT_TOKEN = "phase_1325_ccss_capability_membership_boundary_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1324_TOKEN = (
    "public_rc_remains_blocked_after_phase_1324"
)

PrivateShardRef = dict[str, Any]
EncryptedCoordinationNodeEnvelope = dict[str, Any]
ShardHeaderProjection = dict[str, Any]
PromotionEvidenceRef = dict[str, Any]
DisclosureDenial = dict[str, Any]

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_EPOCH = 1_000_000_000_000
_MAX_CANONICAL_JSON_INT_ABS = _MAX_EPOCH
_MAX_CIPHERTEXT_BYTES = 1_048_576
_MAX_ENVELOPES_PER_SHARD_HEADER = 256
_MAX_PROMOTION_EVIDENCE_REFS = 64
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_PRIVATE_SHARD_REF_KEYS = frozenset(
    {
        "access_policy_ref",
        "contract_version",
        "gate_control_ref",
        "genesis_lineage_ref",
        "label_policy",
        "local_only",
        "private_shard_ref",
        "public_serving_enabled",
        "record_kind",
        "root_commitment_ref",
        "routing_scope",
        "visibility_mode",
    }
)
_ENCRYPTED_ENVELOPE_KEYS = frozenset(
    {
        "canonical_body_sha256",
        "capability_policy_ref",
        "ciphertext_digest_ref",
        "ciphertext_size_bytes",
        "ciphertext_size_class",
        "ciphertext_storage_ref",
        "ciphertext_transport",
        "contract_version",
        "disclosure_denial_ref",
        "encryption_scheme_ref",
        "encryption_status",
        "envelope_epoch",
        "envelope_ref",
        "local_only",
        "private_shard_ref",
        "public_serving_enabled",
        "record_kind",
        "shard_header_ref",
    }
)
_SHARD_HEADER_PROJECTION_KEYS = frozenset(
    {
        "capability_policy_ref",
        "contract_version",
        "disclosure_denial_ref",
        "encrypted_coordination_refs",
        "envelope_count",
        "header_epoch",
        "local_only",
        "phase_1311_projection_record_kind",
        "private_shard_ref",
        "projection_scope",
        "projection_sha256",
        "promotion_evidence_refs",
        "public_serving_enabled",
        "record_kind",
        "root_commitment_ref",
        "shard_header_ref",
    }
)
_PROMOTION_EVIDENCE_REF_KEYS = frozenset(
    {
        "automatic_public_corroboration_carry_forward",
        "automatic_public_reputation_carry_forward",
        "contract_version",
        "destination_public_object_intent",
        "disclosed_lineage_ref",
        "local_only",
        "original_private_node_commitment_ref",
        "private_content_revealed",
        "promotion_authorized",
        "promotion_epoch",
        "promotion_evidence_ref",
        "promotion_executed",
        "promotion_receipt_materialized",
        "promotion_receipt_shape",
        "public_availability_claimed",
        "record_kind",
        "source_private_shard_ref",
        "source_shard_header_ref",
        "successor_public_node_candidate_ref",
    }
)
_DISCLOSURE_DENIAL_KEYS = frozenset(
    {
        "contract_version",
        "denial_policy",
        "denied_fields",
        "disclosure_denial_ref",
        "local_only",
        "public_serving_enabled",
        "record_kind",
    }
)
_RECORD_KEYS_BY_KIND = {
    "private_shard_ref": _PRIVATE_SHARD_REF_KEYS,
    "encrypted_coordination_node_envelope": _ENCRYPTED_ENVELOPE_KEYS,
    "shard_header_projection": _SHARD_HEADER_PROJECTION_KEYS,
    "promotion_evidence_ref": _PROMOTION_EVIDENCE_REF_KEYS,
    "disclosure_denial": _DISCLOSURE_DENIAL_KEYS,
}

_FALSE_AUTHORIZATION_FLAGS = (
    "non_loopback_listener_enabled",
    "private_to_public_promotion_executed",
    "public_availability_claimed",
    "public_confidential_coordination_serving_enabled",
    "public_confidential_messaging_claimed",
    "public_fetch_serving_enabled",
    "public_listener_enabled",
    "public_p2p_enabled",
    "public_projection_serving_enabled",
    "public_registry_enabled",
    "public_sidecar_serving_enabled",
    "release_authority_enabled",
    "source_publication_authorized",
)
_DISCLOSURE_DENIAL_FIELDS = (
    "AgentID",
    "agent_id",
    "capability_contents",
    "client_ip",
    "harness_identity",
    "identity_seed",
    "member_agent_ids",
    "membership_list",
    "mnemonic",
    "openclaw_identity",
    "plaintext_body",
    "private_key",
    "raw_sealed_payload",
    "recipient_identity",
    "route_history",
    "secret_material",
    "sender_identity",
    "tailscale_identity",
    "wallet_id",
)
_FORBIDDEN_PRIVATE_KEYS = frozenset(
    {
        "AgentID",
        "agent_id",
        "capability_contents",
        "client_ip",
        "creator_agent_id",
        "harness_identity",
        "identity_seed",
        "member_agent_ids",
        "membership",
        "membership_list",
        "mnemonic",
        "openclaw_identity",
        "participant",
        "participant_id",
        "plaintext",
        "plaintext_body",
        "plaintext_payload",
        "private_key",
        "raw_sealed_payload",
        "recipient",
        "recipient_identity",
        "route_history",
        "secret",
        "secret_material",
        "sender",
        "sender_identity",
        "tailscale_identity",
        "wallet_id",
    }
)
_FORBIDDEN_VALUE_FRAGMENTS = tuple(
    fragment.lower()
    for fragment in (
        "agent_id",
        "client_ip",
        "creator_agent_id",
        "harness_identity",
        "identity_seed",
        "member_agent",
        "membership_list",
        "mnemonic",
        "openclaw_identity",
        "participant_id",
        "plaintext",
        "private_key",
        "raw_sealed_payload",
        "recipient_identity",
        "route_history",
        "secret_material",
        "sender_identity",
        "tailscale_identity",
        "wallet_id",
    )
)
_PROMOTION_RECEIPT_SHAPE = (
    "successor_node_plus_promotion_receipt_without_automatic_reputation_carry_forward"
)


class ConfidentialCoordinationShardError(ValueError):
    """Fail-closed Phase 1324 error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def ccss_001_required_tokens() -> list[str]:
    return [
        CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        ENCRYPTED_COORDINATION_NODE_ENVELOPE_CONTRACT_RECORDED_TOKEN,
        SHARD_HEADER_PROJECTION_CONTRACT_RECORDED_TOKEN,
        PRIVATE_TO_PUBLIC_PROMOTION_EVIDENCE_SHAPE_RECORDED_TOKEN,
        CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
        PHASE_1325_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1324_TOKEN,
    ]


def ccss_001_private_gated_shard_manifest() -> dict[str, Any]:
    """Return deterministic local/package metadata for CCSS-001."""

    manifest = {
        "authorization_flags": {key: False for key in _FALSE_AUTHORIZATION_FLAGS},
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "disclosure_denial_fields": list(_DISCLOSURE_DENIAL_FIELDS),
        "encrypted_coordination_node_envelope_contract_recorded": True,
        "local_only": True,
        "max_canonical_json_bytes": _MAX_CANONICAL_JSON_BYTES,
        "max_ciphertext_bytes": _MAX_CIPHERTEXT_BYTES,
        "max_envelopes_per_shard_header": _MAX_ENVELOPES_PER_SHARD_HEADER,
        "max_promotion_evidence_refs": _MAX_PROMOTION_EVIDENCE_REFS,
        "next_phase": PHASE_1325_NEXT_TOKEN,
        "private_to_public_promotion_evidence_shape_recorded": True,
        "public_confidential_coordination_serving_enabled": False,
        "public_p2p_enabled": False,
        "record_kinds": sorted(_RECORD_KEYS_BY_KIND),
        "shard_header_projection_contract_recorded": True,
        "tokens": ccss_001_required_tokens(),
    }
    return validate_ccss_001_manifest(manifest)


def build_disclosure_denial() -> DisclosureDenial:
    body: dict[str, Any] = {
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "denial_policy": "deny_plaintext_membership_route_identity_wallet_and_secret_fields",
        "denied_fields": list(_DISCLOSURE_DENIAL_FIELDS),
        "local_only": True,
        "public_serving_enabled": False,
        "record_kind": "disclosure_denial",
    }
    body["disclosure_denial_ref"] = f"disclosure_denial:{_hash_payload(body)}"
    return validate_ccss_001_record(body)


def build_private_shard_ref(
    *,
    genesis_lineage_ref: str,
    root_commitment_ref: str,
    gate_control_ref: str,
    access_policy_ref: str,
    visibility_mode: str,
) -> PrivateShardRef:
    body: dict[str, Any] = {
        "access_policy_ref": access_policy_ref,
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "gate_control_ref": gate_control_ref,
        "genesis_lineage_ref": genesis_lineage_ref,
        "label_policy": "opaque_refs_only_no_identity_labels",
        "local_only": True,
        "public_serving_enabled": False,
        "record_kind": "private_shard_ref",
        "root_commitment_ref": root_commitment_ref,
        "routing_scope": "private_local_or_private_overlay_only",
        "visibility_mode": visibility_mode,
    }
    body["private_shard_ref"] = f"private_shard:{_hash_payload(body)}"
    return validate_ccss_001_record(body)


def build_encrypted_coordination_node_envelope(
    *,
    private_shard_ref: str,
    shard_header_ref: str,
    capability_policy_ref: str,
    disclosure_denial_ref: str,
    encryption_scheme_ref: str,
    ciphertext_digest_ref: str,
    ciphertext_storage_ref: str,
    ciphertext_size_bytes: int,
    envelope_epoch: int,
) -> EncryptedCoordinationNodeEnvelope:
    body: dict[str, Any] = {
        "capability_policy_ref": capability_policy_ref,
        "ciphertext_digest_ref": ciphertext_digest_ref,
        "ciphertext_size_bytes": _require_ciphertext_size(ciphertext_size_bytes),
        "ciphertext_size_class": _ciphertext_size_class(ciphertext_size_bytes),
        "ciphertext_storage_ref": ciphertext_storage_ref,
        "ciphertext_transport": "opaque_ref_only_ciphertext_digest",
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "disclosure_denial_ref": disclosure_denial_ref,
        "encryption_scheme_ref": encryption_scheme_ref,
        "encryption_status": "encrypted_payload_digest_only",
        "envelope_epoch": _require_epoch("envelope", envelope_epoch),
        "local_only": True,
        "private_shard_ref": private_shard_ref,
        "public_serving_enabled": False,
        "record_kind": "encrypted_coordination_node_envelope",
        "shard_header_ref": shard_header_ref,
    }
    digest = _hash_payload(body)
    body["canonical_body_sha256"] = digest
    body["envelope_ref"] = f"encrypted_coordination:{digest}"
    return validate_ccss_001_record(body)


def build_shard_header_projection(
    *,
    private_shard_ref: str,
    shard_header_ref: str,
    root_commitment_ref: str,
    capability_policy_ref: str,
    disclosure_denial_ref: str,
    header_epoch: int,
    encrypted_coordination_refs: Sequence[str],
    promotion_evidence_refs: Sequence[str] = (),
) -> ShardHeaderProjection:
    envelope_refs = _normalize_ref_list(
        encrypted_coordination_refs,
        token="ccss_001_encrypted_coordination_refs_invalid_phase_1324",
        allowed_prefixes=("encrypted_coordination",),
        max_items=_MAX_ENVELOPES_PER_SHARD_HEADER,
    )
    promotion_refs = _normalize_ref_list(
        promotion_evidence_refs,
        token="ccss_001_promotion_evidence_refs_invalid_phase_1324",
        allowed_prefixes=("promotion_evidence",),
        max_items=_MAX_PROMOTION_EVIDENCE_REFS,
    )
    body: dict[str, Any] = {
        "capability_policy_ref": capability_policy_ref,
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "disclosure_denial_ref": disclosure_denial_ref,
        "encrypted_coordination_refs": envelope_refs,
        "envelope_count": len(envelope_refs),
        "header_epoch": _require_epoch("header", header_epoch),
        "local_only": True,
        "phase_1311_projection_record_kind": "private_gated_shard_header",
        "private_shard_ref": private_shard_ref,
        "projection_scope": "private_local_header_only",
        "promotion_evidence_refs": promotion_refs,
        "public_serving_enabled": False,
        "record_kind": "shard_header_projection",
        "root_commitment_ref": root_commitment_ref,
        "shard_header_ref": shard_header_ref,
    }
    body["projection_sha256"] = _hash_payload(body)
    return validate_ccss_001_record(body)


def build_promotion_evidence_ref(
    *,
    source_private_shard_ref: str,
    source_shard_header_ref: str,
    original_private_node_commitment_ref: str,
    successor_public_node_candidate_ref: str,
    disclosed_lineage_ref: str,
    promotion_epoch: int,
) -> PromotionEvidenceRef:
    body: dict[str, Any] = {
        "automatic_public_corroboration_carry_forward": False,
        "automatic_public_reputation_carry_forward": False,
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "destination_public_object_intent": "successor_public_node_candidate_only",
        "disclosed_lineage_ref": disclosed_lineage_ref,
        "local_only": True,
        "original_private_node_commitment_ref": original_private_node_commitment_ref,
        "private_content_revealed": False,
        "promotion_authorized": False,
        "promotion_epoch": _require_epoch("promotion", promotion_epoch),
        "promotion_executed": False,
        "promotion_receipt_materialized": False,
        "promotion_receipt_shape": _PROMOTION_RECEIPT_SHAPE,
        "public_availability_claimed": False,
        "record_kind": "promotion_evidence_ref",
        "source_private_shard_ref": source_private_shard_ref,
        "source_shard_header_ref": source_shard_header_ref,
        "successor_public_node_candidate_ref": successor_public_node_candidate_ref,
    }
    body["promotion_evidence_ref"] = f"promotion_evidence:{_hash_payload(body)}"
    return validate_ccss_001_record(body)


def validate_ccss_001_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_invalid_phase_1324",
            "CCSS-001 manifest must be a mapping",
        )
    _reject_unsafe_json_tree(manifest)
    payload = dict(manifest)
    required_keys = {
        "authorization_flags",
        "contract_version",
        "disclosure_denial_fields",
        "encrypted_coordination_node_envelope_contract_recorded",
        "local_only",
        "max_canonical_json_bytes",
        "max_ciphertext_bytes",
        "max_envelopes_per_shard_header",
        "max_promotion_evidence_refs",
        "next_phase",
        "private_to_public_promotion_evidence_shape_recorded",
        "public_confidential_coordination_serving_enabled",
        "public_p2p_enabled",
        "record_kinds",
        "shard_header_projection_contract_recorded",
        "tokens",
    }
    if set(payload) != required_keys:
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_keys_invalid_phase_1324",
            "CCSS-001 manifest keys do not match the Phase 1324 contract",
        )
    if payload.get("contract_version") != CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION:
        raise ConfidentialCoordinationShardError(
            "ccss_001_contract_version_invalid_phase_1324",
            "CCSS-001 manifest version is invalid",
        )
    for key in (
        "encrypted_coordination_node_envelope_contract_recorded",
        "local_only",
        "private_to_public_promotion_evidence_shape_recorded",
        "shard_header_projection_contract_recorded",
    ):
        if payload.get(key) is not True:
            raise ConfidentialCoordinationShardError(
                "ccss_001_manifest_required_true_invalid_phase_1324",
                "CCSS-001 manifest true flag is invalid",
            )
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_p2p_enabled",
    ):
        _require_false(payload.get(key), token=CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN)
    if payload.get("tokens") != ccss_001_required_tokens():
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_tokens_invalid_phase_1324",
            "CCSS-001 manifest tokens are invalid",
        )
    if payload.get("record_kinds") != sorted(_RECORD_KEYS_BY_KIND):
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_record_kinds_invalid_phase_1324",
            "CCSS-001 manifest record kinds are invalid",
        )
    if payload.get("disclosure_denial_fields") != list(_DISCLOSURE_DENIAL_FIELDS):
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_disclosure_denials_invalid_phase_1324",
            "CCSS-001 manifest disclosure denials are invalid",
        )
    if payload.get("authorization_flags") != {
        key: False for key in _FALSE_AUTHORIZATION_FLAGS
    }:
        raise ConfidentialCoordinationShardError(
            CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
            "CCSS-001 manifest authorization flags must remain false",
        )
    if payload.get("max_ciphertext_bytes") != _MAX_CIPHERTEXT_BYTES:
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_size_bound_invalid_phase_1324",
            "CCSS-001 manifest ciphertext bound is invalid",
        )
    if payload.get("max_canonical_json_bytes") != _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_size_bound_invalid_phase_1324",
            "CCSS-001 manifest canonical JSON bound is invalid",
        )
    if payload.get("max_envelopes_per_shard_header") != _MAX_ENVELOPES_PER_SHARD_HEADER:
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_envelope_bound_invalid_phase_1324",
            "CCSS-001 manifest envelope count bound is invalid",
        )
    if payload.get("max_promotion_evidence_refs") != _MAX_PROMOTION_EVIDENCE_REFS:
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_promotion_ref_bound_invalid_phase_1324",
            "CCSS-001 manifest promotion ref count bound is invalid",
        )
    if payload.get("next_phase") != PHASE_1325_NEXT_TOKEN:
        raise ConfidentialCoordinationShardError(
            "ccss_001_manifest_next_phase_invalid_phase_1324",
            "CCSS-001 manifest next phase is invalid",
        )
    canonical_ccss_001_json(payload)
    return payload


def validate_ccss_001_record(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise ConfidentialCoordinationShardError(
            "ccss_001_record_invalid_phase_1324",
            "CCSS-001 record must be a mapping",
        )
    _reject_unsafe_json_tree(record)
    payload = dict(record)
    kind = _require_choice(
        "record_kind",
        payload.get("record_kind"),
        allowed=tuple(_RECORD_KEYS_BY_KIND),
        token="ccss_001_record_kind_invalid_phase_1324",
    )
    if set(payload) != _RECORD_KEYS_BY_KIND[kind]:
        raise ConfidentialCoordinationShardError(
            "ccss_001_record_keys_invalid_phase_1324",
            "CCSS-001 record keys do not match the Phase 1324 contract",
        )
    if payload.get("contract_version") != CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION:
        raise ConfidentialCoordinationShardError(
            "ccss_001_contract_version_invalid_phase_1324",
            "CCSS-001 record version is invalid",
        )
    if kind != "disclosure_denial":
        _reject_forbidden_private_keys(payload)
        _reject_forbidden_private_values(payload)
    if kind == "private_shard_ref":
        return _validate_private_shard_ref(payload)
    if kind == "encrypted_coordination_node_envelope":
        return _validate_encrypted_coordination_node_envelope(payload)
    if kind == "shard_header_projection":
        return _validate_shard_header_projection(payload)
    if kind == "promotion_evidence_ref":
        return _validate_promotion_evidence_ref(payload)
    return _validate_disclosure_denial(payload)


def canonical_ccss_001_json(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationShardError(
            "ccss_001_payload_size_exceeded_phase_1324",
            "canonical JSON payload exceeds byte bound",
        )
    return canonical


def ccss_001_record_ref(record: Mapping[str, Any]) -> str:
    payload = validate_ccss_001_record(record)
    return f"ccss_001_record:{_hash_payload(payload)}"


def export_ccss_001_record_json(record: Mapping[str, Any]) -> str:
    return canonical_ccss_001_json(validate_ccss_001_record(record))


def _validate_private_shard_ref(payload: Mapping[str, Any]) -> PrivateShardRef:
    normalized: dict[str, Any] = {
        "access_policy_ref": _require_prefixed_digest(
            "access_policy_ref",
            payload.get("access_policy_ref"),
            allowed_prefixes=("capability_policy",),
        ),
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "gate_control_ref": _require_prefixed_digest(
            "gate_control_ref",
            payload.get("gate_control_ref"),
            allowed_prefixes=("gate_control",),
        ),
        "genesis_lineage_ref": _require_prefixed_digest(
            "genesis_lineage_ref",
            payload.get("genesis_lineage_ref"),
            allowed_prefixes=("genesis_lineage",),
        ),
        "label_policy": _require_choice(
            "label_policy",
            payload.get("label_policy"),
            allowed=("opaque_refs_only_no_identity_labels",),
            token="ccss_001_label_policy_invalid_phase_1324",
        ),
        "local_only": _require_true(payload.get("local_only")),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
        ),
        "record_kind": "private_shard_ref",
        "root_commitment_ref": _require_prefixed_digest(
            "root_commitment_ref",
            payload.get("root_commitment_ref"),
            allowed_prefixes=("shard_commitment",),
        ),
        "routing_scope": _require_choice(
            "routing_scope",
            payload.get("routing_scope"),
            allowed=("private_local_or_private_overlay_only",),
            token="ccss_001_routing_scope_invalid_phase_1324",
        ),
        "visibility_mode": _require_choice(
            "visibility_mode",
            payload.get("visibility_mode"),
            allowed=("private", "gated"),
            token="ccss_001_visibility_mode_invalid_phase_1324",
        ),
    }
    expected = f"private_shard:{_hash_payload(normalized)}"
    normalized["private_shard_ref"] = _require_prefixed_digest(
        "private_shard_ref",
        payload.get("private_shard_ref"),
        allowed_prefixes=("private_shard",),
    )
    if normalized["private_shard_ref"] != expected:
        raise ConfidentialCoordinationShardError(
            "ccss_001_private_shard_ref_mismatch_phase_1324",
            "private shard ref does not match canonical payload hash",
        )
    return normalized


def _validate_encrypted_coordination_node_envelope(
    payload: Mapping[str, Any],
) -> EncryptedCoordinationNodeEnvelope:
    size = _require_ciphertext_size(payload.get("ciphertext_size_bytes"))
    normalized: dict[str, Any] = {
        "capability_policy_ref": _require_prefixed_digest(
            "capability_policy_ref",
            payload.get("capability_policy_ref"),
            allowed_prefixes=("capability_policy",),
        ),
        "ciphertext_digest_ref": _require_prefixed_digest(
            "ciphertext_digest_ref",
            payload.get("ciphertext_digest_ref"),
            allowed_prefixes=("ciphertext",),
        ),
        "ciphertext_size_bytes": size,
        "ciphertext_size_class": _require_choice(
            "ciphertext_size_class",
            payload.get("ciphertext_size_class"),
            allowed=("tiny_4k", "small_64k", "medium_1m"),
            token="ccss_001_ciphertext_size_class_invalid_phase_1324",
        ),
        "ciphertext_storage_ref": _require_prefixed_digest(
            "ciphertext_storage_ref",
            payload.get("ciphertext_storage_ref"),
            allowed_prefixes=("ciphertext_storage",),
        ),
        "ciphertext_transport": _require_choice(
            "ciphertext_transport",
            payload.get("ciphertext_transport"),
            allowed=("opaque_ref_only_ciphertext_digest",),
            token="ccss_001_ciphertext_transport_invalid_phase_1324",
        ),
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "disclosure_denial_ref": _require_prefixed_digest(
            "disclosure_denial_ref",
            payload.get("disclosure_denial_ref"),
            allowed_prefixes=("disclosure_denial",),
        ),
        "encryption_scheme_ref": _require_prefixed_digest(
            "encryption_scheme_ref",
            payload.get("encryption_scheme_ref"),
            allowed_prefixes=("encryption_scheme",),
        ),
        "encryption_status": _require_choice(
            "encryption_status",
            payload.get("encryption_status"),
            allowed=("encrypted_payload_digest_only",),
            token="ccss_001_encryption_status_invalid_phase_1324",
        ),
        "envelope_epoch": _require_epoch("envelope", payload.get("envelope_epoch")),
        "local_only": _require_true(payload.get("local_only")),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
        ),
        "record_kind": "encrypted_coordination_node_envelope",
        "shard_header_ref": _require_prefixed_digest(
            "shard_header_ref",
            payload.get("shard_header_ref"),
            allowed_prefixes=("private_shard_header",),
        ),
    }
    if normalized["ciphertext_size_class"] != _ciphertext_size_class(size):
        raise ConfidentialCoordinationShardError(
            "ccss_001_ciphertext_size_class_invalid_phase_1324",
            "ciphertext size class does not match size bound",
        )
    expected = _hash_payload(normalized)
    normalized["canonical_body_sha256"] = _require_hex_digest(
        "canonical_body_sha256",
        payload.get("canonical_body_sha256"),
    )
    normalized["envelope_ref"] = _require_prefixed_digest(
        "envelope_ref",
        payload.get("envelope_ref"),
        allowed_prefixes=("encrypted_coordination",),
    )
    if normalized["canonical_body_sha256"] != expected:
        raise ConfidentialCoordinationShardError(
            "ccss_001_envelope_hash_mismatch_phase_1324",
            "encrypted envelope canonical hash does not match payload",
        )
    if normalized["envelope_ref"] != f"encrypted_coordination:{expected}":
        raise ConfidentialCoordinationShardError(
            "ccss_001_envelope_ref_mismatch_phase_1324",
            "encrypted envelope ref does not match canonical payload hash",
        )
    return normalized


def _validate_shard_header_projection(payload: Mapping[str, Any]) -> ShardHeaderProjection:
    envelope_refs = _normalize_ref_list(
        payload.get("encrypted_coordination_refs"),
        token="ccss_001_encrypted_coordination_refs_invalid_phase_1324",
        allowed_prefixes=("encrypted_coordination",),
        max_items=_MAX_ENVELOPES_PER_SHARD_HEADER,
    )
    promotion_refs = _normalize_ref_list(
        payload.get("promotion_evidence_refs"),
        token="ccss_001_promotion_evidence_refs_invalid_phase_1324",
        allowed_prefixes=("promotion_evidence",),
        max_items=_MAX_PROMOTION_EVIDENCE_REFS,
    )
    normalized: dict[str, Any] = {
        "capability_policy_ref": _require_prefixed_digest(
            "capability_policy_ref",
            payload.get("capability_policy_ref"),
            allowed_prefixes=("capability_policy",),
        ),
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "disclosure_denial_ref": _require_prefixed_digest(
            "disclosure_denial_ref",
            payload.get("disclosure_denial_ref"),
            allowed_prefixes=("disclosure_denial",),
        ),
        "encrypted_coordination_refs": envelope_refs,
        "envelope_count": _require_non_negative_int(
            "envelope_count",
            payload.get("envelope_count"),
        ),
        "header_epoch": _require_epoch("header", payload.get("header_epoch")),
        "local_only": _require_true(payload.get("local_only")),
        "phase_1311_projection_record_kind": _require_choice(
            "phase_1311_projection_record_kind",
            payload.get("phase_1311_projection_record_kind"),
            allowed=("private_gated_shard_header",),
            token="ccss_001_phase_1311_projection_kind_invalid_phase_1324",
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "projection_scope": _require_choice(
            "projection_scope",
            payload.get("projection_scope"),
            allowed=("private_local_header_only",),
            token="ccss_001_projection_scope_invalid_phase_1324",
        ),
        "promotion_evidence_refs": promotion_refs,
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
        ),
        "record_kind": "shard_header_projection",
        "root_commitment_ref": _require_prefixed_digest(
            "root_commitment_ref",
            payload.get("root_commitment_ref"),
            allowed_prefixes=("shard_commitment",),
        ),
        "shard_header_ref": _require_prefixed_digest(
            "shard_header_ref",
            payload.get("shard_header_ref"),
            allowed_prefixes=("private_shard_header",),
        ),
    }
    if normalized["envelope_count"] != len(envelope_refs):
        raise ConfidentialCoordinationShardError(
            "ccss_001_envelope_count_mismatch_phase_1324",
            "shard-header envelope count does not match references",
        )
    if normalized["envelope_count"] < 1:
        raise ConfidentialCoordinationShardError(
            "ccss_001_envelope_count_invalid_phase_1324",
            "shard header projection requires at least one envelope",
        )
    expected = _hash_payload(normalized)
    normalized["projection_sha256"] = _require_hex_digest(
        "projection_sha256",
        payload.get("projection_sha256"),
    )
    if normalized["projection_sha256"] != expected:
        raise ConfidentialCoordinationShardError(
            "ccss_001_shard_header_projection_hash_mismatch_phase_1324",
            "shard-header projection hash does not match payload",
        )
    return normalized


def _validate_promotion_evidence_ref(payload: Mapping[str, Any]) -> PromotionEvidenceRef:
    normalized: dict[str, Any] = {
        "automatic_public_corroboration_carry_forward": _require_false(
            payload.get("automatic_public_corroboration_carry_forward"),
            token="ccss_001_promotion_carry_forward_forbidden_phase_1324",
        ),
        "automatic_public_reputation_carry_forward": _require_false(
            payload.get("automatic_public_reputation_carry_forward"),
            token="ccss_001_promotion_carry_forward_forbidden_phase_1324",
        ),
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "destination_public_object_intent": _require_choice(
            "destination_public_object_intent",
            payload.get("destination_public_object_intent"),
            allowed=("successor_public_node_candidate_only",),
            token="ccss_001_promotion_destination_intent_invalid_phase_1324",
        ),
        "disclosed_lineage_ref": _require_prefixed_digest(
            "disclosed_lineage_ref",
            payload.get("disclosed_lineage_ref"),
            allowed_prefixes=("disclosed_lineage",),
        ),
        "local_only": _require_true(payload.get("local_only")),
        "original_private_node_commitment_ref": _require_prefixed_digest(
            "original_private_node_commitment_ref",
            payload.get("original_private_node_commitment_ref"),
            allowed_prefixes=("private_node_commitment",),
        ),
        "private_content_revealed": _require_false(
            payload.get("private_content_revealed"),
            token="ccss_001_private_content_reveal_forbidden_phase_1324",
        ),
        "promotion_authorized": _require_false(
            payload.get("promotion_authorized"),
            token="ccss_001_promotion_authority_forbidden_phase_1324",
        ),
        "promotion_epoch": _require_epoch("promotion", payload.get("promotion_epoch")),
        "promotion_executed": _require_false(
            payload.get("promotion_executed"),
            token="ccss_001_promotion_execution_forbidden_phase_1324",
        ),
        "promotion_receipt_materialized": _require_false(
            payload.get("promotion_receipt_materialized"),
            token="ccss_001_promotion_execution_forbidden_phase_1324",
        ),
        "promotion_receipt_shape": _require_choice(
            "promotion_receipt_shape",
            payload.get("promotion_receipt_shape"),
            allowed=(_PROMOTION_RECEIPT_SHAPE,),
            token="ccss_001_promotion_receipt_shape_invalid_phase_1324",
        ),
        "public_availability_claimed": _require_false(
            payload.get("public_availability_claimed"),
            token="ccss_001_public_availability_forbidden_phase_1324",
        ),
        "record_kind": "promotion_evidence_ref",
        "source_private_shard_ref": _require_prefixed_digest(
            "source_private_shard_ref",
            payload.get("source_private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "source_shard_header_ref": _require_prefixed_digest(
            "source_shard_header_ref",
            payload.get("source_shard_header_ref"),
            allowed_prefixes=("private_shard_header",),
        ),
        "successor_public_node_candidate_ref": _require_prefixed_digest(
            "successor_public_node_candidate_ref",
            payload.get("successor_public_node_candidate_ref"),
            allowed_prefixes=("public_successor_candidate",),
        ),
    }
    expected = f"promotion_evidence:{_hash_payload(normalized)}"
    normalized["promotion_evidence_ref"] = _require_prefixed_digest(
        "promotion_evidence_ref",
        payload.get("promotion_evidence_ref"),
        allowed_prefixes=("promotion_evidence",),
    )
    if normalized["promotion_evidence_ref"] != expected:
        raise ConfidentialCoordinationShardError(
            "ccss_001_promotion_evidence_ref_mismatch_phase_1324",
            "promotion evidence ref does not match canonical payload hash",
        )
    return normalized


def _validate_disclosure_denial(payload: Mapping[str, Any]) -> DisclosureDenial:
    normalized: dict[str, Any] = {
        "contract_version": CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
        "denial_policy": _require_choice(
            "denial_policy",
            payload.get("denial_policy"),
            allowed=("deny_plaintext_membership_route_identity_wallet_and_secret_fields",),
            token="ccss_001_disclosure_denial_policy_invalid_phase_1324",
        ),
        "denied_fields": _normalize_denied_fields(payload.get("denied_fields")),
        "local_only": _require_true(payload.get("local_only")),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
        ),
        "record_kind": "disclosure_denial",
    }
    expected = f"disclosure_denial:{_hash_payload(normalized)}"
    normalized["disclosure_denial_ref"] = _require_prefixed_digest(
        "disclosure_denial_ref",
        payload.get("disclosure_denial_ref"),
        allowed_prefixes=("disclosure_denial",),
    )
    if normalized["disclosure_denial_ref"] != expected:
        raise ConfidentialCoordinationShardError(
            "ccss_001_disclosure_denial_ref_mismatch_phase_1324",
            "disclosure denial ref does not match canonical payload hash",
        )
    return normalized


def _normalize_denied_fields(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ConfidentialCoordinationShardError(
            "ccss_001_disclosure_denied_fields_invalid_phase_1324",
            "denied fields must be a list",
        )
    if value != list(_DISCLOSURE_DENIAL_FIELDS):
        raise ConfidentialCoordinationShardError(
            "ccss_001_disclosure_denied_fields_invalid_phase_1324",
            "denied fields do not match the Phase 1324 disclosure denial contract",
        )
    return list(_DISCLOSURE_DENIAL_FIELDS)


def _normalize_ref_list(
    value: object,
    *,
    token: str,
    allowed_prefixes: tuple[str, ...],
    max_items: int,
) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ConfidentialCoordinationShardError(token, "reference list must be a sequence")
    if len(value) > max_items:
        raise ConfidentialCoordinationShardError(token, "reference list exceeds bound")
    refs = [
        _require_prefixed_digest("ref", item, allowed_prefixes=allowed_prefixes)
        for item in value
    ]
    if len(set(refs)) != len(refs):
        raise ConfidentialCoordinationShardError(token, "reference list contains duplicates")
    sorted_refs = sorted(refs)
    if refs != sorted_refs:
        raise ConfidentialCoordinationShardError(token, "reference list must be sorted")
    return sorted_refs


def _ciphertext_size_class(size: int) -> str:
    checked = _require_ciphertext_size(size)
    if checked <= 4096:
        return "tiny_4k"
    if checked <= 65_536:
        return "small_64k"
    return "medium_1m"


def _require_ciphertext_size(value: object) -> int:
    size = _require_non_negative_int("ciphertext_size_bytes", value)
    if size <= 0 or size > _MAX_CIPHERTEXT_BYTES:
        raise ConfidentialCoordinationShardError(
            "ccss_001_ciphertext_size_invalid_phase_1324",
            "ciphertext size must be positive and bounded",
        )
    return size


def _require_epoch(label: str, value: object) -> int:
    epoch = _require_non_negative_int(f"{label}_epoch", value)
    if epoch < 1:
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_epoch_invalid_phase_1324",
            "epoch must be positive",
        )
    if epoch > _MAX_EPOCH:
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_epoch_invalid_phase_1324",
            "epoch value exceeds bound",
        )
    return epoch


def _require_non_negative_int(label: str, value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_invalid_phase_1324",
            "expected a non-negative integer",
        )
    return value


def _require_choice(
    label: str,
    value: object,
    *,
    allowed: tuple[str, ...],
    token: str,
) -> str:
    text = _require_text(label, value)
    if text not in allowed:
        raise ConfidentialCoordinationShardError(token, "field value is not allowed")
    return text


def _require_true(value: object) -> bool:
    if value is not True:
        raise ConfidentialCoordinationShardError(
            "ccss_001_local_only_required_phase_1324",
            "local-only flag must be true",
        )
    return True


def _require_false(value: object, *, token: str) -> bool:
    if value is not False:
        raise ConfidentialCoordinationShardError(token, "authorization flag must be false")
    return False


def _require_prefixed_digest(
    label: str,
    value: object,
    *,
    allowed_prefixes: tuple[str, ...],
) -> str:
    text = _require_text(label, value)
    if ":" not in text:
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_ref_invalid_phase_1324",
            "reference must use prefix:digest format",
        )
    prefix, digest = text.split(":", 1)
    if prefix not in allowed_prefixes:
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_ref_invalid_phase_1324",
            "reference prefix is not allowed",
        )
    _require_hex_digest(label, digest)
    return text


def _require_hex_digest(label: str, value: object) -> str:
    text = _require_text(label, value)
    if len(text) != _HEX_DIGEST_LENGTH or any(char not in _HEX for char in text):
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_digest_invalid_phase_1324",
            "digest must be lowercase sha256 hex",
        )
    return text


def _require_text(label: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_text_invalid_phase_1324",
            "expected non-empty text",
        )
    if len(value) > _MAX_TEXT_LENGTH or any(ord(char) < 0x20 or char == "\x7f" for char in value):
        raise ConfidentialCoordinationShardError(
            f"ccss_001_{label}_text_invalid_phase_1324",
            "text field is invalid or oversized",
        )
    return value


def _hash_payload(payload: Mapping[str, Any]) -> str:
    canonical = canonical_ccss_001_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reject_forbidden_private_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in _FORBIDDEN_PRIVATE_KEYS:
                raise ConfidentialCoordinationShardError(
                    "ccss_001_private_field_forbidden_phase_1324",
                    "private field is forbidden in CCSS-001 records",
                )
            _reject_forbidden_private_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_private_keys(item)


def _reject_forbidden_private_values(value: object) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in _FORBIDDEN_VALUE_FRAGMENTS):
            raise ConfidentialCoordinationShardError(
                "ccss_001_private_value_forbidden_phase_1324",
                "private value fragment is forbidden in CCSS-001 records",
            )
    elif isinstance(value, Mapping):
        for nested in value.values():
            _reject_forbidden_private_values(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_private_values(item)


def _reject_unsafe_json_tree(value: object) -> None:
    seen: set[int] = set()
    node_count = 0
    payload_text_bytes = 0

    def add_payload_bytes(text: str) -> None:
        nonlocal payload_text_bytes
        payload_text_bytes += len(text.encode("utf-8"))
        if payload_text_bytes > _MAX_CANONICAL_JSON_BYTES:
            raise ConfidentialCoordinationShardError(
                "ccss_001_payload_size_exceeded_phase_1324",
                "canonical JSON payload exceeds byte bound",
            )

    def visit(item: object, depth: int) -> None:
        nonlocal node_count
        if depth > _MAX_PAYLOAD_DEPTH:
            raise ConfidentialCoordinationShardError(
                "ccss_001_payload_depth_exceeded_phase_1324",
                "payload exceeds depth bound",
            )
        node_count += 1
        if node_count > _MAX_PAYLOAD_NODES:
            raise ConfidentialCoordinationShardError(
                "ccss_001_payload_node_limit_exceeded_phase_1324",
                "payload exceeds node bound",
            )
        if isinstance(item, (Mapping, list)):
            marker = id(item)
            if marker in seen:
                raise ConfidentialCoordinationShardError(
                    "ccss_001_payload_cycle_forbidden_phase_1324",
                    "payload cycles are forbidden",
                )
            seen.add(marker)
            if isinstance(item, Mapping):
                for key, nested in item.items():
                    if not isinstance(key, str):
                        raise ConfidentialCoordinationShardError(
                            "ccss_001_payload_key_invalid_phase_1324",
                            "payload keys must be strings",
                        )
                    _require_text("payload_key", key)
                    add_payload_bytes(key)
                    node_count += 1
                    if node_count > _MAX_PAYLOAD_NODES:
                        raise ConfidentialCoordinationShardError(
                            "ccss_001_payload_node_limit_exceeded_phase_1324",
                            "payload exceeds node bound",
                        )
                    visit(nested, depth + 1)
            else:
                for nested in item:
                    visit(nested, depth + 1)
            seen.remove(marker)
            return
        if isinstance(item, tuple):
            raise ConfidentialCoordinationShardError(
                "ccss_001_payload_key_invalid_phase_1324",
                "tuple values are not canonical JSON",
            )
        if isinstance(item, float):
            raise ConfidentialCoordinationShardError(
                "ccss_001_float_values_forbidden_phase_1324",
                "float values are forbidden",
            )
        if item is None or isinstance(item, (str, int, bool)):
            if isinstance(item, str):
                _require_text("payload_text", item)
                add_payload_bytes(item)
            elif isinstance(item, int) and not isinstance(item, bool):
                if abs(item) > _MAX_CANONICAL_JSON_INT_ABS:
                    raise ConfidentialCoordinationShardError(
                        "ccss_001_payload_int_invalid_phase_1324",
                        "integer payload exceeds canonical JSON integer bound",
                    )
                add_payload_bytes(str(item))
            return
        raise ConfidentialCoordinationShardError(
            "ccss_001_payload_key_invalid_phase_1324",
            "payload contains non-JSON value",
        )

    visit(value, 0)


__all__ = [
    "CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION",
    "CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN",
    "ConfidentialCoordinationShardError",
    "DisclosureDenial",
    "EncryptedCoordinationNodeEnvelope",
    "ENCRYPTED_COORDINATION_NODE_ENVELOPE_CONTRACT_RECORDED_TOKEN",
    "PHASE_1325_NEXT_TOKEN",
    "PRIVATE_TO_PUBLIC_PROMOTION_EVIDENCE_SHAPE_RECORDED_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1324_TOKEN",
    "PrivateShardRef",
    "PromotionEvidenceRef",
    "SHARD_HEADER_PROJECTION_CONTRACT_RECORDED_TOKEN",
    "ShardHeaderProjection",
    "build_disclosure_denial",
    "build_encrypted_coordination_node_envelope",
    "build_private_shard_ref",
    "build_promotion_evidence_ref",
    "build_shard_header_projection",
    "canonical_ccss_001_json",
    "ccss_001_private_gated_shard_manifest",
    "ccss_001_record_ref",
    "ccss_001_required_tokens",
    "export_ccss_001_record_json",
    "validate_ccss_001_manifest",
    "validate_ccss_001_record",
]
