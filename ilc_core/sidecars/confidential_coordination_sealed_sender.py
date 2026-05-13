"""Phase 1326 CCSS-003 sealed-sender local delivery boundary.

This module records a private/local contract for fixed-size sealed payload
classes, local delivery intents, delivery receipts, and safe projection states.
It references the H-013/H-015 seams without activating public P2P, public relay
serving, public confidential coordination, or a general messaging product.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping
from typing import Any


CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION = (
    "ccss_003_sealed_sender_local_delivery_boundary_phase_1326.v0.1"
)
SEALED_SENDER_FIXED_SIZE_PAYLOAD_BOUNDARY_RECORDED_TOKEN = (
    "sealed_sender_fixed_size_payload_boundary_recorded_phase_1326"
)
H013_H015_DEPENDENCY_SEAMS_RECORDED_TOKEN = (
    "h013_h015_dependency_seams_recorded_phase_1326"
)
PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN = (
    "public_p2p_not_activated_by_ccss_phase_1326"
)
PHASE_1327_NEXT_TOKEN = "phase_1327_ccss_gossip_jitter_cover_policy_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1326_TOKEN = (
    "public_rc_remains_blocked_after_phase_1326"
)

H013_DEPENDENCY_REF = "run_h013_d2d_sealed_sender_adr_verdict=accepted"
H015_DEPENDENCY_REF = "spectral_routing_runtime_h015.v0.1"
SEALED_MARKER = "h013_fixed_size_sealed_payload"

SealedPayloadClassRef = dict[str, Any]
SealedLocalDeliveryIntent = dict[str, Any]
SealedLocalDeliveryReceipt = dict[str, Any]
SealedDeliveryProjection = dict[str, Any]

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_EPOCH = 1_000_000_000_000
_MAX_SEQUENCE = 1_000_000_000_000
_MAX_CANONICAL_JSON_INT_ABS = _MAX_SEQUENCE
_MAX_REF_LIST_ITEMS = 256
_MAX_LOCAL_DELIVERY_QUEUE_BOUND = 1024
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_H013_INNER_PLAINTEXT_BYTES = 2048
_H013_OUTER_PLAINTEXT_BYTES = 4096
_H013_INNER_ENVELOPE_BYTES = 2108
_H013_OUTER_ENVELOPE_BYTES = 4156
_SEALED_TO_PLAINTEXT_SIZE = {
    _H013_INNER_ENVELOPE_BYTES: _H013_INNER_PLAINTEXT_BYTES,
    _H013_OUTER_ENVELOPE_BYTES: _H013_OUTER_PLAINTEXT_BYTES,
}

_DELIVERY_STATES = (
    "sealed_pending_local",
    "sealed_delivered_local",
    "rejected_size_class",
    "rejected_metadata_leak",
    "rejected_replay",
    "blocked_public_transport",
)
_REJECTION_REASON_BY_STATE = {
    "sealed_pending_local": "none",
    "sealed_delivered_local": "none",
    "rejected_size_class": "size_class_invalid",
    "rejected_metadata_leak": "metadata_leak_detected",
    "rejected_replay": "replayed_delivery_token",
    "blocked_public_transport": "public_transport_blocked",
}
_FALSE_AUTHORIZATION_FLAGS = (
    "harness_identity_disclosure_enabled",
    "ip_address_disclosure_enabled",
    "metadata_leakage_enabled",
    "network_transport_enabled",
    "non_loopback_listener_enabled",
    "plaintext_disclosure_enabled",
    "public_confidential_coordination_serving_enabled",
    "public_confidential_messaging_claimed",
    "public_fetch_serving_enabled",
    "public_listener_enabled",
    "public_p2p_enabled",
    "public_projection_serving_enabled",
    "public_relay_serving_enabled",
    "public_serving_enabled",
    "public_sidecar_serving_enabled",
    "raw_sealed_payload_disclosed",
    "recipient_identity_disclosure_enabled",
    "release_authority_enabled",
    "retry_schedule_disclosure_enabled",
    "route_history_disclosure_enabled",
    "sender_identity_disclosure_enabled",
    "source_publication_authorized",
    "unbounded_delivery_queue_enabled",
    "wall_clock_expiry_enabled",
)
_FORBIDDEN_PRIVATE_KEYS = frozenset(
    {
        "AgentID",
        "agent_id",
        "agentid",
        "client_ip",
        "creator_agent_id",
        "harness_identity",
        "identity_seed",
        "ip_address",
        "membership_list",
        "mnemonic",
        "openclaw_identity",
        "plaintext",
        "plaintext_body",
        "plaintext_payload",
        "private_key",
        "raw_payload",
        "raw_sealed_payload",
        "recipient",
        "recipient_identity",
        "retry_schedule",
        "route_history",
        "secret",
        "secret_material",
        "sender",
        "sender_identity",
        "tailscale_identity",
        "wallet_id",
        "zk_witness",
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
        "ip_address",
        "membership_list",
        "mnemonic",
        "openclaw_identity",
        "plaintext",
        "private_key",
        "raw_payload",
        "raw_sealed_payload",
        "recipient_identity",
        "retry_schedule",
        "route_history",
        "secret_material",
        "sender_identity",
        "tailscale_identity",
        "wallet_id",
        "zk_witness",
    )
)

_COMMON_RECORD_KEYS = frozenset(
    {
        "authorization_flags",
        "contract_version",
        "local_only",
        "public_serving_enabled",
        "record_kind",
    }
)
_PAYLOAD_CLASS_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "allowed_plaintext_size_bytes",
        "allowed_sealed_payload_size_bytes",
        "fixed_size_payload_boundary_recorded",
        "h013_inner_envelope_size_bytes",
        "h013_inner_plaintext_size_bytes",
        "h013_outer_envelope_size_bytes",
        "h013_outer_plaintext_size_bytes",
        "padding_model",
        "plaintext_size_class_bytes",
        "sealed_marker",
        "sealed_payload_class_ref",
        "sealed_payload_size_class_bytes",
    }
)
_DELIVERY_INTENT_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "capability_ref",
        "delivery_epoch",
        "delivery_queue_bound",
        "delivery_sequence",
        "delivery_state",
        "h013_dependency_ref",
        "h015_dependency_ref",
        "local_delivery_token_ref",
        "opaque_channel_ref",
        "private_shard_ref",
        "relay_instruction_ref",
        "sealed_delivery_intent_ref",
        "sealed_marker",
        "sealed_payload_class_ref",
        "sealed_payload_digest_ref",
        "sealed_payload_size_bytes",
    }
)
_DELIVERY_RECEIPT_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "delivery_epoch",
        "delivery_intent_ref",
        "delivery_sequence",
        "delivery_state",
        "local_delivery_token_ref",
        "local_recipient_adapter_ref",
        "private_shard_ref",
        "sealed_delivery_receipt_ref",
        "sealed_payload_class_ref",
    }
)
_DELIVERY_PROJECTION_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "delivery_intent_ref",
        "delivery_state",
        "metadata_leakage_checks_recorded",
        "private_shard_ref",
        "projection_epoch",
        "projection_scope",
        "rejection_reason",
        "sealed_delivery_projection_ref",
        "sealed_payload_class_ref",
    }
)
_RECORD_KEYS_BY_KIND = {
    "sealed_payload_class_ref": _PAYLOAD_CLASS_KEYS,
    "sealed_local_delivery_intent": _DELIVERY_INTENT_KEYS,
    "sealed_local_delivery_receipt": _DELIVERY_RECEIPT_KEYS,
    "sealed_delivery_projection": _DELIVERY_PROJECTION_KEYS,
}


class ConfidentialCoordinationSealedSenderError(ValueError):
    """Stable Phase 1326 validation error."""

    def __init__(self, token: str, detail: str) -> None:
        super().__init__(token)
        self.token = token
        self.detail = detail


def ccss_003_required_tokens() -> list[str]:
    return [
        CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        SEALED_SENDER_FIXED_SIZE_PAYLOAD_BOUNDARY_RECORDED_TOKEN,
        H013_H015_DEPENDENCY_SEAMS_RECORDED_TOKEN,
        PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
        PHASE_1327_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1326_TOKEN,
    ]


def ccss_003_sealed_sender_local_delivery_manifest() -> dict[str, Any]:
    manifest = {
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_states": list(_DELIVERY_STATES),
        "fixed_size_payload_boundary_recorded": True,
        "h013_dependency_ref": H013_DEPENDENCY_REF,
        "h013_h015_dependency_seams_recorded": True,
        "h015_dependency_ref": H015_DEPENDENCY_REF,
        "local_only": True,
        "max_canonical_json_bytes": _MAX_CANONICAL_JSON_BYTES,
        "max_local_delivery_queue_bound": _MAX_LOCAL_DELIVERY_QUEUE_BOUND,
        "next_phase": PHASE_1327_NEXT_TOKEN,
        "plaintext_size_classes": sorted(_SEALED_TO_PLAINTEXT_SIZE.values()),
        "public_confidential_coordination_serving_enabled": False,
        "public_confidential_messaging_claimed": False,
        "public_p2p_enabled": False,
        "public_relay_serving_enabled": False,
        "record_kinds": sorted(_RECORD_KEYS_BY_KIND),
        "sealed_payload_size_classes": sorted(_SEALED_TO_PLAINTEXT_SIZE),
        "sealed_sender_fixed_size_payload_boundary_recorded": True,
        "tokens": ccss_003_required_tokens(),
    }
    return validate_ccss_003_manifest(manifest)


def build_sealed_payload_class_ref(*, sealed_payload_size_class_bytes: int) -> SealedPayloadClassRef:
    sealed_size = _require_size_class(sealed_payload_size_class_bytes)
    plaintext_size = _SEALED_TO_PLAINTEXT_SIZE[sealed_size]
    body: dict[str, Any] = {
        "allowed_plaintext_size_bytes": sorted(_SEALED_TO_PLAINTEXT_SIZE.values()),
        "allowed_sealed_payload_size_bytes": sorted(_SEALED_TO_PLAINTEXT_SIZE),
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "fixed_size_payload_boundary_recorded": True,
        "h013_inner_envelope_size_bytes": _H013_INNER_ENVELOPE_BYTES,
        "h013_inner_plaintext_size_bytes": _H013_INNER_PLAINTEXT_BYTES,
        "h013_outer_envelope_size_bytes": _H013_OUTER_ENVELOPE_BYTES,
        "h013_outer_plaintext_size_bytes": _H013_OUTER_PLAINTEXT_BYTES,
        "local_only": True,
        "padding_model": "fixed_size_h013_inner_outer_classes",
        "plaintext_size_class_bytes": plaintext_size,
        "public_serving_enabled": False,
        "record_kind": "sealed_payload_class_ref",
        "sealed_marker": SEALED_MARKER,
        "sealed_payload_size_class_bytes": sealed_size,
    }
    body["sealed_payload_class_ref"] = f"sealed_payload_class:{_hash_payload(body)}"
    return validate_ccss_003_record(body)


def build_sealed_local_delivery_intent(
    *,
    private_shard_ref: str,
    capability_ref: str,
    sealed_payload_class_ref: str,
    sealed_payload_digest_ref: str,
    relay_instruction_ref: str,
    opaque_channel_ref: str,
    local_delivery_token_ref: str,
    delivery_epoch: int,
    delivery_sequence: int,
    sealed_payload_size_bytes: int,
    delivery_queue_bound: int = 128,
) -> SealedLocalDeliveryIntent:
    sealed_size = _require_size_class(sealed_payload_size_bytes)
    queue_bound = _require_queue_bound(delivery_queue_bound)
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "capability_ref": _require_prefixed_digest("capability", capability_ref, allowed_prefixes=("capability",)),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_epoch": _require_epoch("delivery", delivery_epoch),
        "delivery_queue_bound": queue_bound,
        "delivery_sequence": _require_sequence("delivery_sequence", delivery_sequence),
        "delivery_state": "sealed_pending_local",
        "h013_dependency_ref": H013_DEPENDENCY_REF,
        "h015_dependency_ref": H015_DEPENDENCY_REF,
        "local_delivery_token_ref": _require_prefixed_digest(
            "local_delivery_token",
            local_delivery_token_ref,
            allowed_prefixes=("local_delivery_token",),
        ),
        "local_only": True,
        "opaque_channel_ref": _require_prefixed_digest(
            "opaque_channel",
            opaque_channel_ref,
            allowed_prefixes=("opaque_channel",),
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard",
            private_shard_ref,
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": False,
        "record_kind": "sealed_local_delivery_intent",
        "relay_instruction_ref": _require_prefixed_digest(
            "relay_instruction",
            relay_instruction_ref,
            allowed_prefixes=("relay_instruction",),
        ),
        "sealed_marker": SEALED_MARKER,
        "sealed_payload_class_ref": _require_prefixed_digest(
            "sealed_payload_class",
            sealed_payload_class_ref,
            allowed_prefixes=("sealed_payload_class",),
        ),
        "sealed_payload_digest_ref": _require_prefixed_digest(
            "sealed_payload_digest",
            sealed_payload_digest_ref,
            allowed_prefixes=("sealed_payload_digest",),
        ),
        "sealed_payload_size_bytes": sealed_size,
    }
    body["sealed_delivery_intent_ref"] = f"sealed_delivery_intent:{_hash_payload(body)}"
    return validate_ccss_003_record(body)


def build_sealed_local_delivery_receipt(
    *,
    private_shard_ref: str,
    delivery_intent_ref: str,
    sealed_payload_class_ref: str,
    local_delivery_token_ref: str,
    local_recipient_adapter_ref: str,
    delivery_epoch: int,
    delivery_sequence: int,
) -> SealedLocalDeliveryReceipt:
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_epoch": _require_epoch("delivery", delivery_epoch),
        "delivery_intent_ref": _require_prefixed_digest(
            "delivery_intent",
            delivery_intent_ref,
            allowed_prefixes=("sealed_delivery_intent",),
        ),
        "delivery_sequence": _require_sequence("delivery_sequence", delivery_sequence),
        "delivery_state": "sealed_delivered_local",
        "local_delivery_token_ref": _require_prefixed_digest(
            "local_delivery_token",
            local_delivery_token_ref,
            allowed_prefixes=("local_delivery_token",),
        ),
        "local_only": True,
        "local_recipient_adapter_ref": _require_prefixed_digest(
            "local_recipient_adapter",
            local_recipient_adapter_ref,
            allowed_prefixes=("local_recipient_adapter",),
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard",
            private_shard_ref,
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": False,
        "record_kind": "sealed_local_delivery_receipt",
        "sealed_payload_class_ref": _require_prefixed_digest(
            "sealed_payload_class",
            sealed_payload_class_ref,
            allowed_prefixes=("sealed_payload_class",),
        ),
    }
    body["sealed_delivery_receipt_ref"] = f"sealed_delivery_receipt:{_hash_payload(body)}"
    return validate_ccss_003_record(body)


def build_sealed_delivery_projection(
    *,
    private_shard_ref: str,
    delivery_intent_ref: str,
    sealed_payload_class_ref: str,
    delivery_state: str,
    projection_epoch: int,
) -> SealedDeliveryProjection:
    state = _require_delivery_state(delivery_state)
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_intent_ref": _require_prefixed_digest(
            "delivery_intent",
            delivery_intent_ref,
            allowed_prefixes=("sealed_delivery_intent",),
        ),
        "delivery_state": state,
        "local_only": True,
        "metadata_leakage_checks_recorded": True,
        "private_shard_ref": _require_prefixed_digest(
            "private_shard",
            private_shard_ref,
            allowed_prefixes=("private_shard",),
        ),
        "projection_epoch": _require_epoch("projection", projection_epoch),
        "projection_scope": "private_local_delivery_state_only",
        "public_serving_enabled": False,
        "record_kind": "sealed_delivery_projection",
        "rejection_reason": _REJECTION_REASON_BY_STATE[state],
        "sealed_payload_class_ref": _require_prefixed_digest(
            "sealed_payload_class",
            sealed_payload_class_ref,
            allowed_prefixes=("sealed_payload_class",),
        ),
    }
    body["sealed_delivery_projection_ref"] = f"sealed_delivery_projection:{_hash_payload(body)}"
    return validate_ccss_003_record(body)


def build_local_delivery_projection(
    *,
    intent_record: Mapping[str, Any] | None,
    projection_epoch: int,
    replayed_delivery_token_refs: Collection[str] = (),
    mark_delivered: bool = False,
    public_p2p_enabled: bool = False,
    public_relay_serving_enabled: bool = False,
    public_confidential_coordination_serving_enabled: bool = False,
    non_loopback_listener_enabled: bool = False,
    network_transport_enabled: bool = False,
    unbounded_delivery_queue_enabled: bool = False,
    wall_clock_expiry_enabled: bool = False,
) -> SealedDeliveryProjection:
    """Build a fail-closed local projection without opening a transport path."""

    epoch = _require_epoch("projection", projection_epoch)
    if (
        public_p2p_enabled
        or public_relay_serving_enabled
        or public_confidential_coordination_serving_enabled
        or non_loopback_listener_enabled
        or network_transport_enabled
        or unbounded_delivery_queue_enabled
        or wall_clock_expiry_enabled
    ):
        return _fallback_projection("blocked_public_transport", epoch)
    replayed = _normalize_ref_set(
        replayed_delivery_token_refs,
        token="ccss_003_replay_collection_invalid_phase_1326",
        allowed_prefixes=("local_delivery_token",),
        max_items=_MAX_REF_LIST_ITEMS,
    )
    if intent_record is None:
        return _fallback_projection("rejected_metadata_leak", epoch)
    if not isinstance(intent_record, Mapping):
        return _fallback_projection("rejected_metadata_leak", epoch)
    if intent_record.get("sealed_payload_size_bytes") not in _SEALED_TO_PLAINTEXT_SIZE:
        return _fallback_projection("rejected_size_class", epoch)
    try:
        intent = validate_ccss_003_record(intent_record)
    except ConfidentialCoordinationSealedSenderError:
        return _fallback_projection("rejected_metadata_leak", epoch)
    state = "sealed_delivered_local" if mark_delivered else "sealed_pending_local"
    if intent["local_delivery_token_ref"] in replayed:
        state = "rejected_replay"
    return build_sealed_delivery_projection(
        private_shard_ref=intent["private_shard_ref"],
        delivery_intent_ref=intent["sealed_delivery_intent_ref"],
        sealed_payload_class_ref=intent["sealed_payload_class_ref"],
        delivery_state=state,
        projection_epoch=epoch,
    )


def validate_ccss_003_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_invalid_phase_1326",
            "CCSS-003 manifest must be a mapping",
        )
    _reject_unsafe_json_tree(manifest)
    payload = dict(manifest)
    required_keys = {
        "authorization_flags",
        "contract_version",
        "delivery_states",
        "fixed_size_payload_boundary_recorded",
        "h013_dependency_ref",
        "h013_h015_dependency_seams_recorded",
        "h015_dependency_ref",
        "local_only",
        "max_canonical_json_bytes",
        "max_local_delivery_queue_bound",
        "next_phase",
        "plaintext_size_classes",
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_p2p_enabled",
        "public_relay_serving_enabled",
        "record_kinds",
        "sealed_payload_size_classes",
        "sealed_sender_fixed_size_payload_boundary_recorded",
        "tokens",
    }
    if set(payload) != required_keys:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_keys_invalid_phase_1326",
            "CCSS-003 manifest keys do not match the Phase 1326 contract",
        )
    if payload.get("contract_version") != CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_contract_version_invalid_phase_1326",
            "CCSS-003 manifest version is invalid",
        )
    for key in (
        "fixed_size_payload_boundary_recorded",
        "h013_h015_dependency_seams_recorded",
        "local_only",
        "sealed_sender_fixed_size_payload_boundary_recorded",
    ):
        if payload.get(key) is not True:
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_manifest_required_true_invalid_phase_1326",
                "CCSS-003 manifest true flag is invalid",
            )
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_p2p_enabled",
        "public_relay_serving_enabled",
    ):
        _require_false(payload.get(key), token=PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN)
    if payload.get("h013_dependency_ref") != H013_DEPENDENCY_REF:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_h013_dependency_invalid_phase_1326",
            "H-013 dependency seam is invalid",
        )
    if payload.get("h015_dependency_ref") != H015_DEPENDENCY_REF:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_h015_dependency_invalid_phase_1326",
            "H-015 dependency seam is invalid",
        )
    if payload.get("delivery_states") != list(_DELIVERY_STATES):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_delivery_states_invalid_phase_1326",
            "CCSS-003 delivery states are invalid",
        )
    if payload.get("record_kinds") != sorted(_RECORD_KEYS_BY_KIND):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_record_kinds_invalid_phase_1326",
            "CCSS-003 record kinds are invalid",
        )
    if payload.get("sealed_payload_size_classes") != sorted(_SEALED_TO_PLAINTEXT_SIZE):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_size_classes_invalid_phase_1326",
            "sealed payload size classes are invalid",
        )
    if payload.get("plaintext_size_classes") != sorted(_SEALED_TO_PLAINTEXT_SIZE.values()):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_plaintext_size_classes_invalid_phase_1326",
            "plaintext size classes are invalid",
        )
    if payload.get("authorization_flags") != _false_authorization_flags():
        raise ConfidentialCoordinationSealedSenderError(
            PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
            "CCSS-003 authorization flags must remain false",
        )
    if payload.get("max_canonical_json_bytes") != _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_size_bound_invalid_phase_1326",
            "CCSS-003 canonical JSON bound is invalid",
        )
    if payload.get("max_local_delivery_queue_bound") != _MAX_LOCAL_DELIVERY_QUEUE_BOUND:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_queue_bound_invalid_phase_1326",
            "CCSS-003 queue bound is invalid",
        )
    if payload.get("next_phase") != PHASE_1327_NEXT_TOKEN:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_next_phase_invalid_phase_1326",
            "CCSS-003 manifest next phase is invalid",
        )
    if payload.get("tokens") != ccss_003_required_tokens():
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_manifest_tokens_invalid_phase_1326",
            "CCSS-003 manifest tokens are invalid",
        )
    canonical_ccss_003_json(payload)
    return payload


def validate_ccss_003_record(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_record_invalid_phase_1326",
            "CCSS-003 record must be a mapping",
        )
    _reject_unsafe_json_tree(record)
    payload = dict(record)
    kind = _require_choice(
        "record_kind",
        payload.get("record_kind"),
        allowed=tuple(_RECORD_KEYS_BY_KIND),
        token="ccss_003_record_kind_invalid_phase_1326",
    )
    if set(payload) != _RECORD_KEYS_BY_KIND[kind]:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_record_keys_invalid_phase_1326",
            "CCSS-003 record keys do not match the Phase 1326 contract",
        )
    if payload.get("contract_version") != CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_contract_version_invalid_phase_1326",
            "CCSS-003 record version is invalid",
        )
    _reject_forbidden_private_keys(payload)
    _reject_forbidden_private_values(payload)
    if kind == "sealed_payload_class_ref":
        return _validate_payload_class_ref(payload)
    if kind == "sealed_local_delivery_intent":
        return _validate_local_delivery_intent(payload)
    if kind == "sealed_local_delivery_receipt":
        return _validate_local_delivery_receipt(payload)
    return _validate_delivery_projection(payload)


def canonical_ccss_003_json(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_payload_size_exceeded_phase_1326",
            "canonical JSON payload exceeds byte bound",
        )
    return canonical


def ccss_003_record_ref(record: Mapping[str, Any]) -> str:
    payload = validate_ccss_003_record(record)
    return f"ccss_003_record:{_hash_payload(payload)}"


def export_ccss_003_record_json(record: Mapping[str, Any]) -> str:
    return canonical_ccss_003_json(validate_ccss_003_record(record))


def _validate_payload_class_ref(payload: Mapping[str, Any]) -> SealedPayloadClassRef:
    sealed_size = _require_size_class(payload.get("sealed_payload_size_class_bytes"))
    plaintext_size = _SEALED_TO_PLAINTEXT_SIZE[sealed_size]
    normalized: dict[str, Any] = {
        "allowed_plaintext_size_bytes": _normalize_exact_int_list(
            payload.get("allowed_plaintext_size_bytes"),
            expected=tuple(sorted(_SEALED_TO_PLAINTEXT_SIZE.values())),
            token="ccss_003_plaintext_size_classes_invalid_phase_1326",
        ),
        "allowed_sealed_payload_size_bytes": _normalize_exact_int_list(
            payload.get("allowed_sealed_payload_size_bytes"),
            expected=tuple(sorted(_SEALED_TO_PLAINTEXT_SIZE)),
            token="ccss_003_size_classes_invalid_phase_1326",
        ),
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "fixed_size_payload_boundary_recorded": _require_true_token(
            payload.get("fixed_size_payload_boundary_recorded"),
            token=SEALED_SENDER_FIXED_SIZE_PAYLOAD_BOUNDARY_RECORDED_TOKEN,
        ),
        "h013_inner_envelope_size_bytes": _require_exact_int(
            "h013_inner_envelope_size_bytes",
            payload.get("h013_inner_envelope_size_bytes"),
            expected=_H013_INNER_ENVELOPE_BYTES,
        ),
        "h013_inner_plaintext_size_bytes": _require_exact_int(
            "h013_inner_plaintext_size_bytes",
            payload.get("h013_inner_plaintext_size_bytes"),
            expected=_H013_INNER_PLAINTEXT_BYTES,
        ),
        "h013_outer_envelope_size_bytes": _require_exact_int(
            "h013_outer_envelope_size_bytes",
            payload.get("h013_outer_envelope_size_bytes"),
            expected=_H013_OUTER_ENVELOPE_BYTES,
        ),
        "h013_outer_plaintext_size_bytes": _require_exact_int(
            "h013_outer_plaintext_size_bytes",
            payload.get("h013_outer_plaintext_size_bytes"),
            expected=_H013_OUTER_PLAINTEXT_BYTES,
        ),
        "local_only": _require_true(payload.get("local_only")),
        "padding_model": _require_choice(
            "padding_model",
            payload.get("padding_model"),
            allowed=("fixed_size_h013_inner_outer_classes",),
            token="ccss_003_padding_model_invalid_phase_1326",
        ),
        "plaintext_size_class_bytes": _require_exact_int(
            "plaintext_size_class_bytes",
            payload.get("plaintext_size_class_bytes"),
            expected=plaintext_size,
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
        ),
        "record_kind": "sealed_payload_class_ref",
        "sealed_marker": _require_choice(
            "sealed_marker",
            payload.get("sealed_marker"),
            allowed=(SEALED_MARKER,),
            token="ccss_003_sealed_marker_invalid_phase_1326",
        ),
        "sealed_payload_size_class_bytes": sealed_size,
    }
    normalized["sealed_payload_class_ref"] = _require_prefixed_digest(
        "sealed_payload_class",
        payload.get("sealed_payload_class_ref"),
        allowed_prefixes=("sealed_payload_class",),
    )
    _verify_ref(normalized, ref_key="sealed_payload_class_ref", prefix="sealed_payload_class")
    return normalized


def _validate_local_delivery_intent(payload: Mapping[str, Any]) -> SealedLocalDeliveryIntent:
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "capability_ref": _require_prefixed_digest(
            "capability",
            payload.get("capability_ref"),
            allowed_prefixes=("capability",),
        ),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_epoch": _require_epoch("delivery", payload.get("delivery_epoch")),
        "delivery_queue_bound": _require_queue_bound(payload.get("delivery_queue_bound")),
        "delivery_sequence": _require_sequence("delivery_sequence", payload.get("delivery_sequence")),
        "delivery_state": _require_choice(
            "delivery_state",
            payload.get("delivery_state"),
            allowed=("sealed_pending_local",),
            token="ccss_003_delivery_state_invalid_phase_1326",
        ),
        "h013_dependency_ref": _require_choice(
            "h013_dependency_ref",
            payload.get("h013_dependency_ref"),
            allowed=(H013_DEPENDENCY_REF,),
            token="ccss_003_h013_dependency_invalid_phase_1326",
        ),
        "h015_dependency_ref": _require_choice(
            "h015_dependency_ref",
            payload.get("h015_dependency_ref"),
            allowed=(H015_DEPENDENCY_REF,),
            token="ccss_003_h015_dependency_invalid_phase_1326",
        ),
        "local_delivery_token_ref": _require_prefixed_digest(
            "local_delivery_token",
            payload.get("local_delivery_token_ref"),
            allowed_prefixes=("local_delivery_token",),
        ),
        "local_only": _require_true(payload.get("local_only")),
        "opaque_channel_ref": _require_prefixed_digest(
            "opaque_channel",
            payload.get("opaque_channel_ref"),
            allowed_prefixes=("opaque_channel",),
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
        ),
        "record_kind": "sealed_local_delivery_intent",
        "relay_instruction_ref": _require_prefixed_digest(
            "relay_instruction",
            payload.get("relay_instruction_ref"),
            allowed_prefixes=("relay_instruction",),
        ),
        "sealed_marker": _require_choice(
            "sealed_marker",
            payload.get("sealed_marker"),
            allowed=(SEALED_MARKER,),
            token="ccss_003_sealed_marker_invalid_phase_1326",
        ),
        "sealed_payload_class_ref": _require_prefixed_digest(
            "sealed_payload_class",
            payload.get("sealed_payload_class_ref"),
            allowed_prefixes=("sealed_payload_class",),
        ),
        "sealed_payload_digest_ref": _require_prefixed_digest(
            "sealed_payload_digest",
            payload.get("sealed_payload_digest_ref"),
            allowed_prefixes=("sealed_payload_digest",),
        ),
        "sealed_payload_size_bytes": _require_size_class(payload.get("sealed_payload_size_bytes")),
    }
    normalized["sealed_delivery_intent_ref"] = _require_prefixed_digest(
        "sealed_delivery_intent",
        payload.get("sealed_delivery_intent_ref"),
        allowed_prefixes=("sealed_delivery_intent",),
    )
    _verify_ref(normalized, ref_key="sealed_delivery_intent_ref", prefix="sealed_delivery_intent")
    return normalized


def _validate_local_delivery_receipt(payload: Mapping[str, Any]) -> SealedLocalDeliveryReceipt:
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_epoch": _require_epoch("delivery", payload.get("delivery_epoch")),
        "delivery_intent_ref": _require_prefixed_digest(
            "delivery_intent",
            payload.get("delivery_intent_ref"),
            allowed_prefixes=("sealed_delivery_intent",),
        ),
        "delivery_sequence": _require_sequence("delivery_sequence", payload.get("delivery_sequence")),
        "delivery_state": _require_choice(
            "delivery_state",
            payload.get("delivery_state"),
            allowed=("sealed_delivered_local",),
            token="ccss_003_delivery_state_invalid_phase_1326",
        ),
        "local_delivery_token_ref": _require_prefixed_digest(
            "local_delivery_token",
            payload.get("local_delivery_token_ref"),
            allowed_prefixes=("local_delivery_token",),
        ),
        "local_only": _require_true(payload.get("local_only")),
        "local_recipient_adapter_ref": _require_prefixed_digest(
            "local_recipient_adapter",
            payload.get("local_recipient_adapter_ref"),
            allowed_prefixes=("local_recipient_adapter",),
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
        ),
        "record_kind": "sealed_local_delivery_receipt",
        "sealed_payload_class_ref": _require_prefixed_digest(
            "sealed_payload_class",
            payload.get("sealed_payload_class_ref"),
            allowed_prefixes=("sealed_payload_class",),
        ),
    }
    normalized["sealed_delivery_receipt_ref"] = _require_prefixed_digest(
        "sealed_delivery_receipt",
        payload.get("sealed_delivery_receipt_ref"),
        allowed_prefixes=("sealed_delivery_receipt",),
    )
    _verify_ref(normalized, ref_key="sealed_delivery_receipt_ref", prefix="sealed_delivery_receipt")
    return normalized


def _validate_delivery_projection(payload: Mapping[str, Any]) -> SealedDeliveryProjection:
    state = _require_delivery_state(payload.get("delivery_state"))
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "contract_version": CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION,
        "delivery_intent_ref": _require_prefixed_digest(
            "delivery_intent",
            payload.get("delivery_intent_ref"),
            allowed_prefixes=("sealed_delivery_intent",),
        ),
        "delivery_state": state,
        "local_only": _require_true(payload.get("local_only")),
        "metadata_leakage_checks_recorded": _require_true_token(
            payload.get("metadata_leakage_checks_recorded"),
            token="ccss_003_metadata_leakage_checks_required_phase_1326",
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "projection_epoch": _require_epoch("projection", payload.get("projection_epoch")),
        "projection_scope": _require_choice(
            "projection_scope",
            payload.get("projection_scope"),
            allowed=("private_local_delivery_state_only",),
            token="ccss_003_projection_scope_invalid_phase_1326",
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token=PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
        ),
        "record_kind": "sealed_delivery_projection",
        "rejection_reason": _require_choice(
            "rejection_reason",
            payload.get("rejection_reason"),
            allowed=tuple(_REJECTION_REASON_BY_STATE.values()),
            token="ccss_003_rejection_reason_invalid_phase_1326",
        ),
        "sealed_payload_class_ref": _require_prefixed_digest(
            "sealed_payload_class",
            payload.get("sealed_payload_class_ref"),
            allowed_prefixes=("sealed_payload_class",),
        ),
    }
    if normalized["rejection_reason"] != _REJECTION_REASON_BY_STATE[state]:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_delivery_state_reason_invalid_phase_1326",
            "delivery state and rejection reason do not match",
        )
    normalized["sealed_delivery_projection_ref"] = _require_prefixed_digest(
        "sealed_delivery_projection",
        payload.get("sealed_delivery_projection_ref"),
        allowed_prefixes=("sealed_delivery_projection",),
    )
    _verify_ref(
        normalized,
        ref_key="sealed_delivery_projection_ref",
        prefix="sealed_delivery_projection",
    )
    return normalized


def _fallback_projection(state: str, epoch: int) -> SealedDeliveryProjection:
    fallback_ref = _digest_ref("sealed_delivery_intent", f"fallback:{state}:{epoch}")
    return build_sealed_delivery_projection(
        private_shard_ref=_digest_ref("private_shard", "fallback-private-shard"),
        delivery_intent_ref=fallback_ref,
        sealed_payload_class_ref=_digest_ref("sealed_payload_class", "fallback-payload-class"),
        delivery_state=state,
        projection_epoch=epoch,
    )


def _verify_ref(payload: Mapping[str, Any], *, ref_key: str, prefix: str) -> None:
    body = dict(payload)
    active_ref = body.pop(ref_key)
    expected = f"{prefix}:{_hash_payload(body)}"
    if active_ref != expected:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{ref_key}_mismatch_phase_1326",
            "record reference does not match canonical body",
        )


def _digest_ref(prefix: str, material: str) -> str:
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _false_authorization_flags() -> dict[str, bool]:
    return {key: False for key in _FALSE_AUTHORIZATION_FLAGS}


def _normalize_false_flag_mapping(value: object) -> dict[str, bool]:
    if not isinstance(value, Mapping):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_authorization_flags_invalid_phase_1326",
            "authorization flags must be a mapping",
        )
    if set(value) != set(_FALSE_AUTHORIZATION_FLAGS):
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_authorization_flags_invalid_phase_1326",
            "authorization flags do not match the Phase 1326 contract",
        )
    return {
        key: _require_false(
            value.get(key),
            token=PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN,
        )
        for key in _FALSE_AUTHORIZATION_FLAGS
    }


def _normalize_exact_int_list(value: object, *, expected: tuple[int, ...], token: str) -> list[int]:
    if not isinstance(value, list):
        raise ConfidentialCoordinationSealedSenderError(token, "expected exact integer list")
    normalized = [_require_non_negative_int("int_list_item", item) for item in value]
    if normalized != list(expected):
        raise ConfidentialCoordinationSealedSenderError(token, "integer list does not match expected values")
    return normalized


def _normalize_ref_set(
    value: Collection[str],
    *,
    token: str,
    allowed_prefixes: tuple[str, ...],
    max_items: int,
) -> set[str]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Collection):
        raise ConfidentialCoordinationSealedSenderError(token, "expected reference collection")
    if len(value) > max_items:
        raise ConfidentialCoordinationSealedSenderError(token, "reference collection exceeds bound")
    refs = {
        _require_prefixed_digest("ref", item, allowed_prefixes=allowed_prefixes)
        for item in value
    }
    if len(refs) != len(value):
        raise ConfidentialCoordinationSealedSenderError(token, "reference collection contains duplicates")
    return refs


def _require_delivery_state(value: object) -> str:
    return _require_choice(
        "delivery_state",
        value,
        allowed=_DELIVERY_STATES,
        token="ccss_003_delivery_state_invalid_phase_1326",
    )


def _require_size_class(value: object) -> int:
    size = _require_non_negative_int("sealed_payload_size_bytes", value)
    if size not in _SEALED_TO_PLAINTEXT_SIZE:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_size_class_invalid_phase_1326",
            "sealed payload size is not an allowed fixed-size class",
        )
    return size


def _require_queue_bound(value: object) -> int:
    bound = _require_non_negative_int("delivery_queue_bound", value)
    if bound < 1 or bound > _MAX_LOCAL_DELIVERY_QUEUE_BOUND:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_delivery_queue_bound_invalid_phase_1326",
            "delivery queue bound must be positive and bounded",
        )
    return bound


def _require_epoch(label: str, value: object) -> int:
    epoch = _require_non_negative_int(f"{label}_epoch", value)
    if epoch < 1:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_epoch_invalid_phase_1326",
            "epoch must be positive",
        )
    if epoch > _MAX_EPOCH:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_epoch_invalid_phase_1326",
            "epoch value exceeds bound",
        )
    return epoch


def _require_sequence(label: str, value: object) -> int:
    sequence = _require_non_negative_int(label, value)
    if sequence < 1 or sequence > _MAX_SEQUENCE:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_invalid_phase_1326",
            "sequence must be positive and bounded",
        )
    return sequence


def _require_non_negative_int(label: str, value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_invalid_phase_1326",
            "expected a non-negative integer",
        )
    return value


def _require_exact_int(label: str, value: object, *, expected: int) -> int:
    actual = _require_non_negative_int(label, value)
    if actual != expected:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_invalid_phase_1326",
            "integer does not match expected value",
        )
    return actual


def _require_choice(
    label: str,
    value: object,
    *,
    allowed: tuple[str, ...],
    token: str,
) -> str:
    text = _require_text(label, value)
    if text not in allowed:
        raise ConfidentialCoordinationSealedSenderError(token, "field value is not allowed")
    return text


def _require_true(value: object) -> bool:
    if value is not True:
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_local_only_required_phase_1326",
            "local-only flag must be true",
        )
    return True


def _require_true_token(value: object, *, token: str) -> bool:
    if value is not True:
        raise ConfidentialCoordinationSealedSenderError(token, "required true flag is invalid")
    return True


def _require_false(value: object, *, token: str) -> bool:
    if value is not False:
        raise ConfidentialCoordinationSealedSenderError(token, "authorization flag must be false")
    return False


def _require_prefixed_digest(
    label: str,
    value: object,
    *,
    allowed_prefixes: tuple[str, ...],
) -> str:
    text = _require_text(label, value)
    if ":" not in text:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_ref_invalid_phase_1326",
            "reference must use prefix:digest format",
        )
    prefix, digest = text.split(":", 1)
    if prefix not in allowed_prefixes:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_ref_invalid_phase_1326",
            "reference prefix is not allowed",
        )
    _require_hex_digest(label, digest)
    return text


def _require_hex_digest(label: str, value: object) -> str:
    text = _require_text(label, value)
    if len(text) != _HEX_DIGEST_LENGTH or any(char not in _HEX for char in text):
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_digest_invalid_phase_1326",
            "digest must be lowercase sha256 hex",
        )
    return text


def _require_text(label: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_text_invalid_phase_1326",
            "expected non-empty text",
        )
    if len(value) > _MAX_TEXT_LENGTH or any(ord(char) < 0x20 or char == "\x7f" for char in value):
        raise ConfidentialCoordinationSealedSenderError(
            f"ccss_003_{label}_text_invalid_phase_1326",
            "text field is invalid or oversized",
        )
    return value


def _hash_payload(payload: Mapping[str, Any]) -> str:
    canonical = canonical_ccss_003_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reject_forbidden_private_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in _FORBIDDEN_PRIVATE_KEYS:
                raise ConfidentialCoordinationSealedSenderError(
                    "ccss_003_private_field_forbidden_phase_1326",
                    "private field is forbidden in CCSS-003 records",
                )
            _reject_forbidden_private_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_private_keys(item)


def _reject_forbidden_private_values(value: object) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in _FORBIDDEN_VALUE_FRAGMENTS):
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_private_value_forbidden_phase_1326",
                "private value fragment is forbidden in CCSS-003 records",
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
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_payload_size_exceeded_phase_1326",
                "canonical JSON payload exceeds byte bound",
            )

    def visit(item: object, depth: int) -> None:
        nonlocal node_count
        if depth > _MAX_PAYLOAD_DEPTH:
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_payload_depth_exceeded_phase_1326",
                "payload exceeds depth bound",
            )
        node_count += 1
        if node_count > _MAX_PAYLOAD_NODES:
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_payload_node_limit_exceeded_phase_1326",
                "payload exceeds node bound",
            )
        if isinstance(item, (Mapping, list)):
            marker = id(item)
            if marker in seen:
                raise ConfidentialCoordinationSealedSenderError(
                    "ccss_003_payload_cycle_forbidden_phase_1326",
                    "payload cycles are forbidden",
                )
            seen.add(marker)
            if isinstance(item, Mapping):
                for key, nested in item.items():
                    if not isinstance(key, str):
                        raise ConfidentialCoordinationSealedSenderError(
                            "ccss_003_payload_key_invalid_phase_1326",
                            "payload keys must be strings",
                        )
                    _require_text("payload_key", key)
                    add_payload_bytes(key)
                    node_count += 1
                    if node_count > _MAX_PAYLOAD_NODES:
                        raise ConfidentialCoordinationSealedSenderError(
                            "ccss_003_payload_node_limit_exceeded_phase_1326",
                            "payload exceeds node bound",
                        )
                    visit(nested, depth + 1)
            else:
                for nested in item:
                    visit(nested, depth + 1)
            seen.remove(marker)
            return
        if isinstance(item, tuple):
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_payload_key_invalid_phase_1326",
                "tuple values are not canonical JSON",
            )
        if isinstance(item, float):
            raise ConfidentialCoordinationSealedSenderError(
                "ccss_003_float_values_forbidden_phase_1326",
                "float values are forbidden",
            )
        if item is None or isinstance(item, (str, int, bool)):
            if isinstance(item, str):
                _require_text("payload_text", item)
                add_payload_bytes(item)
            elif isinstance(item, int) and not isinstance(item, bool):
                if abs(item) > _MAX_CANONICAL_JSON_INT_ABS:
                    raise ConfidentialCoordinationSealedSenderError(
                        "ccss_003_payload_int_invalid_phase_1326",
                        "integer payload exceeds canonical JSON integer bound",
                    )
                add_payload_bytes(str(item))
            return
        raise ConfidentialCoordinationSealedSenderError(
            "ccss_003_payload_key_invalid_phase_1326",
            "payload contains non-JSON value",
        )

    visit(value, 0)


__all__ = [
    "CCSS_003_SEALED_SENDER_LOCAL_DELIVERY_BOUNDARY_VERSION",
    "H013_DEPENDENCY_REF",
    "H013_H015_DEPENDENCY_SEAMS_RECORDED_TOKEN",
    "H015_DEPENDENCY_REF",
    "PHASE_1327_NEXT_TOKEN",
    "PUBLIC_P2P_NOT_ACTIVATED_BY_CCSS_PHASE_1326_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1326_TOKEN",
    "SEALED_MARKER",
    "SEALED_SENDER_FIXED_SIZE_PAYLOAD_BOUNDARY_RECORDED_TOKEN",
    "ConfidentialCoordinationSealedSenderError",
    "SealedDeliveryProjection",
    "SealedLocalDeliveryIntent",
    "SealedLocalDeliveryReceipt",
    "SealedPayloadClassRef",
    "build_local_delivery_projection",
    "build_sealed_delivery_projection",
    "build_sealed_local_delivery_intent",
    "build_sealed_local_delivery_receipt",
    "build_sealed_payload_class_ref",
    "canonical_ccss_003_json",
    "ccss_003_record_ref",
    "ccss_003_required_tokens",
    "ccss_003_sealed_sender_local_delivery_manifest",
    "export_ccss_003_record_json",
    "validate_ccss_003_manifest",
    "validate_ccss_003_record",
]
