# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1325 CCSS-002 capability and membership boundary.

This module records a local-only contract for capability policy references,
opaque membership-boundary references, grant/revocation evidence, and an
optional ZK-membership seam. It does not disclose plaintext membership, create a
public membership directory, activate a public credential authority, serve
confidential coordination, open public P2P, or ratify a ZK verifier.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping, Sequence
from typing import Any


CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION = (
    "ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1"
)
PRIVATE_SHARD_ACCESS_CONTROL_BOUNDARY_RECORDED_TOKEN = (
    "private_shard_access_control_boundary_recorded_phase_1325"
)
MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN = (
    "membership_plaintext_disclosure_forbidden_phase_1325"
)
OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN = (
    "optional_zk_interface_boundary_recorded_phase_1325"
)
PHASE_1326_NEXT_TOKEN = "phase_1326_ccss_sealed_sender_boundary_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1325_TOKEN = (
    "public_rc_remains_blocked_after_phase_1325"
)

CapabilityPolicyRef = dict[str, Any]
MembershipBoundaryRef = dict[str, Any]
CapabilityGrantRef = dict[str, Any]
CapabilityRevocationRef = dict[str, Any]
ZKMembershipInterfaceRef = dict[str, Any]
CapabilityAccessDecision = dict[str, Any]

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_EPOCH = 1_000_000_000_000
_MAX_SEQUENCE = 1_000_000_000_000
_MAX_CANONICAL_JSON_INT_ABS = _MAX_SEQUENCE
_MAX_REF_LIST_ITEMS = 256
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_ACCESS_STATES = (
    "unknown",
    "candidate_granted",
    "active_local",
    "revoked",
    "expired_or_superseded",
    "zk_deferred",
)
_DENY_STATES = (
    "unknown",
    "candidate_granted",
    "revoked",
    "expired_or_superseded",
    "zk_deferred",
)
_GRANT_SCOPES = (
    "audit_header",
    "promote_candidate_ref",
    "read_ciphertext_ref",
    "read_header",
    "write_encrypted_envelope",
)
_FALSE_AUTHORIZATION_FLAGS = (
    "agent_identity_disclosure_enabled",
    "capability_bearer_identity_disclosed",
    "membership_list_disclosure_enabled",
    "membership_plaintext_disclosure_enabled",
    "non_loopback_listener_enabled",
    "plaintext_disclosure_enabled",
    "public_capability_directory_enabled",
    "public_confidential_coordination_serving_enabled",
    "public_credential_authority_enabled",
    "public_fetch_serving_enabled",
    "public_listener_enabled",
    "public_membership_directory_enabled",
    "public_p2p_enabled",
    "public_projection_serving_enabled",
    "public_revocation_registry_enabled",
    "public_serving_enabled",
    "public_sidecar_serving_enabled",
    "public_zk_verifier_enabled",
    "raw_grant_material_disclosed",
    "release_authority_enabled",
    "revocation_reason_disclosed",
    "source_publication_authorized",
)
_FORBIDDEN_PRIVATE_KEYS = frozenset(
    {
        "AgentID",
        "agent_id",
        "agentid",
        "bearer_agent_id",
        "capability_bearer",
        "capability_secret",
        "client_ip",
        "creator_agent_id",
        "grantee_agent_id",
        "grantor_agent_id",
        "harness_identity",
        "identity_seed",
        "member",
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
        "raw_capability",
        "raw_grant",
        "raw_membership",
        "raw_sealed_payload",
        "recipient",
        "recipient_identity",
        "revocation_reason",
        "route_history",
        "secret",
        "secret_material",
        "sender",
        "sender_identity",
        "tailscale_identity",
        "wallet_id",
        "witness",
        "zk_witness",
    }
)
_FORBIDDEN_VALUE_FRAGMENTS = tuple(
    fragment.lower()
    for fragment in (
        "agent_id",
        "bearer_agent",
        "capability_secret",
        "client_ip",
        "creator_agent_id",
        "grantee_agent",
        "grantor_agent",
        "harness_identity",
        "identity_seed",
        "member_agent",
        "membership_list",
        "mnemonic",
        "openclaw_identity",
        "participant_id",
        "plaintext",
        "private_key",
        "raw_capability",
        "raw_grant",
        "raw_membership",
        "raw_sealed_payload",
        "recipient_identity",
        "revocation_reason",
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
_CAPABILITY_POLICY_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "access_states",
        "capability_policy_ref",
        "deny_states",
        "fail_closed_conditions",
        "hash_inputs",
        "local_policy_inputs",
        "membership_boundary_ref",
        "non_protocol_metadata_fields",
        "ordering_model",
        "policy_epoch",
        "private_shard_ref",
        "revocation_wins_over_grant",
    }
)
_MEMBERSHIP_BOUNDARY_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "boundary_epoch",
        "member_count_disclosed",
        "membership_boundary_ref",
        "membership_material",
        "membership_proof_ref",
        "membership_root_ref",
        "participant_list_disclosed",
        "private_shard_ref",
    }
)
_CAPABILITY_GRANT_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "capability_policy_ref",
        "capability_ref",
        "grant_epoch",
        "grant_ref",
        "grant_scope",
        "grant_sequence",
        "grant_state",
        "membership_boundary_ref",
        "membership_proof_ref",
        "ordering_basis",
        "private_shard_ref",
        "shard_header_ref",
        "valid_from_epoch",
        "valid_to_epoch",
    }
)
_CAPABILITY_REVOCATION_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "capability_ref",
        "grant_ref",
        "ordering_basis",
        "private_shard_ref",
        "revocation_epoch",
        "revocation_ref",
        "revocation_scope",
        "revocation_sequence",
        "revocation_wins_over_grant",
    }
)
_ZK_MEMBERSHIP_INTERFACE_KEYS = _COMMON_RECORD_KEYS | frozenset(
    {
        "decision_state_without_ratified_verifier",
        "interface_status",
        "membership_boundary_ref",
        "private_shard_ref",
        "proof_payload_disclosed",
        "proof_system_ref",
        "proving_system_ratified",
        "public_verifier_enabled",
        "witness_material_disclosed",
        "zk_interface_ref",
        "zk_proof_ref",
    }
)
_RECORD_KEYS_BY_KIND = {
    "capability_grant_ref": _CAPABILITY_GRANT_KEYS,
    "capability_policy_ref": _CAPABILITY_POLICY_KEYS,
    "capability_revocation_ref": _CAPABILITY_REVOCATION_KEYS,
    "membership_boundary_ref": _MEMBERSHIP_BOUNDARY_KEYS,
    "zk_membership_interface_ref": _ZK_MEMBERSHIP_INTERFACE_KEYS,
}


class ConfidentialCoordinationCapabilityError(ValueError):
    """Fail-closed Phase 1325 error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def ccss_002_required_tokens() -> list[str]:
    return [
        CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        PRIVATE_SHARD_ACCESS_CONTROL_BOUNDARY_RECORDED_TOKEN,
        MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN,
        OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
        PHASE_1326_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1325_TOKEN,
    ]


def ccss_002_capability_membership_boundary_manifest() -> dict[str, Any]:
    """Return deterministic local/package metadata for CCSS-002."""

    manifest = {
        "access_states": list(_ACCESS_STATES),
        "authorization_flags": {key: False for key in _FALSE_AUTHORIZATION_FLAGS},
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "grant_revocation_boundary_recorded": True,
        "local_only": True,
        "max_canonical_json_bytes": _MAX_CANONICAL_JSON_BYTES,
        "max_reference_list_items": _MAX_REF_LIST_ITEMS,
        "membership_plaintext_disclosure_forbidden": True,
        "next_phase": PHASE_1326_NEXT_TOKEN,
        "optional_zk_interface_boundary_recorded": True,
        "private_shard_access_control_boundary_recorded": True,
        "public_confidential_coordination_serving_enabled": False,
        "public_membership_directory_enabled": False,
        "public_p2p_enabled": False,
        "public_zk_verifier_enabled": False,
        "record_kinds": sorted(_RECORD_KEYS_BY_KIND),
        "tokens": ccss_002_required_tokens(),
    }
    return validate_ccss_002_manifest(manifest)


def build_capability_policy_ref(
    *,
    private_shard_ref: str,
    membership_boundary_ref: str,
    policy_epoch: int,
) -> CapabilityPolicyRef:
    body: dict[str, Any] = {
        "access_states": list(_ACCESS_STATES),
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "deny_states": list(_DENY_STATES),
        "fail_closed_conditions": [
            "unknown",
            "malformed",
            "replayed",
            "revoked",
            "cross_shard",
            "expired",
            "superseded",
            "zk_deferred_without_ratified_verifier",
            "public_serving_dependency",
            "public_membership_directory_dependency",
            "public_credential_authority_dependency",
        ],
        "hash_inputs": [
            "access_states",
            "membership_boundary_ref",
            "ordering_model",
            "policy_epoch",
            "private_shard_ref",
            "revocation_wins_over_grant",
        ],
        "local_only": True,
        "local_policy_inputs": [
            "current_epoch",
            "local_replay_collection",
            "local_supersession_collection",
            "local_revocation_evidence",
        ],
        "membership_boundary_ref": membership_boundary_ref,
        "non_protocol_metadata_fields": [],
        "ordering_model": "epoch_then_local_sequence_no_wall_clock",
        "policy_epoch": _require_epoch("policy", policy_epoch),
        "private_shard_ref": private_shard_ref,
        "public_serving_enabled": False,
        "record_kind": "capability_policy_ref",
        "revocation_wins_over_grant": True,
    }
    body["capability_policy_ref"] = f"capability_policy:{_hash_payload(body)}"
    return validate_ccss_002_record(body)


def build_membership_boundary_ref(
    *,
    private_shard_ref: str,
    membership_root_ref: str,
    membership_proof_ref: str,
    boundary_epoch: int,
) -> MembershipBoundaryRef:
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "boundary_epoch": _require_epoch("boundary", boundary_epoch),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "local_only": True,
        "member_count_disclosed": False,
        "membership_material": "opaque_commitment_refs_only",
        "membership_proof_ref": membership_proof_ref,
        "membership_root_ref": membership_root_ref,
        "participant_list_disclosed": False,
        "private_shard_ref": private_shard_ref,
        "public_serving_enabled": False,
        "record_kind": "membership_boundary_ref",
    }
    body["membership_boundary_ref"] = f"membership_boundary:{_hash_payload(body)}"
    return validate_ccss_002_record(body)


def build_capability_grant_ref(
    *,
    private_shard_ref: str,
    shard_header_ref: str,
    capability_policy_ref: str,
    membership_boundary_ref: str,
    membership_proof_ref: str,
    capability_ref: str,
    grant_scope: str,
    grant_epoch: int,
    grant_sequence: int,
    valid_from_epoch: int,
    valid_to_epoch: int,
) -> CapabilityGrantRef:
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "capability_policy_ref": capability_policy_ref,
        "capability_ref": capability_ref,
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "grant_epoch": _require_epoch("grant", grant_epoch),
        "grant_scope": grant_scope,
        "grant_sequence": _require_sequence("grant_sequence", grant_sequence),
        "grant_state": "candidate_granted",
        "local_only": True,
        "membership_boundary_ref": membership_boundary_ref,
        "membership_proof_ref": membership_proof_ref,
        "ordering_basis": "epoch_then_grant_sequence_no_wall_clock",
        "private_shard_ref": private_shard_ref,
        "public_serving_enabled": False,
        "record_kind": "capability_grant_ref",
        "shard_header_ref": shard_header_ref,
        "valid_from_epoch": _require_epoch("valid_from", valid_from_epoch),
        "valid_to_epoch": _require_epoch("valid_to", valid_to_epoch),
    }
    body["grant_ref"] = f"capability_grant:{_hash_payload(body)}"
    return validate_ccss_002_record(body)


def build_capability_revocation_ref(
    *,
    private_shard_ref: str,
    capability_ref: str,
    grant_ref: str,
    revocation_epoch: int,
    revocation_sequence: int,
) -> CapabilityRevocationRef:
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "capability_ref": capability_ref,
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "grant_ref": grant_ref,
        "local_only": True,
        "ordering_basis": "epoch_then_revocation_sequence_no_wall_clock",
        "private_shard_ref": private_shard_ref,
        "public_serving_enabled": False,
        "record_kind": "capability_revocation_ref",
        "revocation_epoch": _require_epoch("revocation", revocation_epoch),
        "revocation_scope": "capability_grant_ref_only",
        "revocation_sequence": _require_sequence(
            "revocation_sequence",
            revocation_sequence,
        ),
        "revocation_wins_over_grant": True,
    }
    body["revocation_ref"] = f"capability_revocation:{_hash_payload(body)}"
    return validate_ccss_002_record(body)


def build_zk_membership_interface_ref(
    *,
    private_shard_ref: str,
    membership_boundary_ref: str,
    proof_system_ref: str,
    zk_proof_ref: str,
) -> ZKMembershipInterfaceRef:
    body: dict[str, Any] = {
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "decision_state_without_ratified_verifier": "zk_deferred",
        "interface_status": "seam_only_no_ratified_verifier",
        "local_only": True,
        "membership_boundary_ref": membership_boundary_ref,
        "private_shard_ref": private_shard_ref,
        "proof_payload_disclosed": False,
        "proof_system_ref": proof_system_ref,
        "proving_system_ratified": False,
        "public_serving_enabled": False,
        "public_verifier_enabled": False,
        "record_kind": "zk_membership_interface_ref",
        "witness_material_disclosed": False,
        "zk_proof_ref": zk_proof_ref,
    }
    body["zk_interface_ref"] = f"zk_membership_interface:{_hash_payload(body)}"
    return validate_ccss_002_record(body)


def build_local_access_decision(
    *,
    private_shard_ref: str,
    capability_ref: str,
    current_epoch: int,
    grant_record: Mapping[str, Any] | None,
    membership_boundary_record: Mapping[str, Any] | None = None,
    revocation_record: Mapping[str, Any] | None = None,
    zk_interface_record: Mapping[str, Any] | None = None,
    replayed_grant_refs: Collection[str] = (),
    superseded_capability_refs: Collection[str] = (),
    public_serving_enabled: bool = False,
    public_membership_directory_enabled: bool = False,
    public_credential_authority_enabled: bool = False,
) -> CapabilityAccessDecision:
    """Resolve the local access state without activating public authority."""

    _require_false(
        public_serving_enabled,
        token="ccss_002_public_serving_dependency_forbidden_phase_1325",
    )
    _require_false(
        public_membership_directory_enabled,
        token="ccss_002_public_membership_directory_dependency_forbidden_phase_1325",
    )
    _require_false(
        public_credential_authority_enabled,
        token="ccss_002_public_credential_authority_dependency_forbidden_phase_1325",
    )
    shard_ref = _require_prefixed_digest(
        "private_shard_ref",
        private_shard_ref,
        allowed_prefixes=("private_shard",),
    )
    cap_ref = _require_prefixed_digest(
        "capability_ref",
        capability_ref,
        allowed_prefixes=("capability",),
    )
    current = _require_epoch("current", current_epoch)
    replayed = _normalize_ref_set(
        replayed_grant_refs,
        token="ccss_002_replay_collection_invalid_phase_1325",
        allowed_prefixes=("capability_grant",),
        max_items=_MAX_REF_LIST_ITEMS,
    )
    superseded = _normalize_ref_set(
        superseded_capability_refs,
        token="ccss_002_supersession_collection_invalid_phase_1325",
        allowed_prefixes=("capability",),
        max_items=_MAX_REF_LIST_ITEMS,
    )

    if grant_record is None:
        return _access_decision("unknown", "no_grant_evidence", shard_ref, cap_ref, current)
    try:
        grant = validate_ccss_002_record(grant_record)
    except ConfidentialCoordinationCapabilityError:
        return _access_decision("unknown", "malformed_grant", shard_ref, cap_ref, current)
    if grant["capability_ref"] != cap_ref:
        return _access_decision("candidate_granted", "capability_ref_mismatch", shard_ref, cap_ref, current)
    if grant["private_shard_ref"] != shard_ref:
        return _access_decision("candidate_granted", "cross_shard_capability", shard_ref, cap_ref, current)
    if grant["grant_ref"] in replayed:
        return _access_decision("candidate_granted", "replayed_capability_grant", shard_ref, cap_ref, current)
    if cap_ref in superseded:
        return _access_decision("expired_or_superseded", "superseded_capability", shard_ref, cap_ref, current)

    if revocation_record is not None:
        try:
            revocation = validate_ccss_002_record(revocation_record)
        except ConfidentialCoordinationCapabilityError:
            return _access_decision("revoked", "malformed_revocation_fail_closed", shard_ref, cap_ref, current)
        if (
            revocation["private_shard_ref"] == shard_ref
            and revocation["capability_ref"] == cap_ref
            and revocation["grant_ref"] == grant["grant_ref"]
        ):
            return _access_decision("revoked", "revocation_wins_over_grant", shard_ref, cap_ref, current)

    if not (grant["valid_from_epoch"] <= current <= grant["valid_to_epoch"]):
        return _access_decision("expired_or_superseded", "epoch_window_closed", shard_ref, cap_ref, current)

    if zk_interface_record is not None:
        try:
            zk = validate_ccss_002_record(zk_interface_record)
        except ConfidentialCoordinationCapabilityError:
            return _access_decision("zk_deferred", "malformed_zk_interface", shard_ref, cap_ref, current)
        if (
            zk["record_kind"] != "zk_membership_interface_ref"
            or zk["private_shard_ref"] != shard_ref
            or zk["membership_boundary_ref"] != grant["membership_boundary_ref"]
        ):
            return _access_decision("zk_deferred", "malformed_zk_interface", shard_ref, cap_ref, current)
        return _access_decision("zk_deferred", "zk_verifier_not_ratified", shard_ref, cap_ref, current)

    if membership_boundary_record is None:
        return _access_decision("candidate_granted", "membership_boundary_unresolved", shard_ref, cap_ref, current)
    try:
        boundary = validate_ccss_002_record(membership_boundary_record)
    except ConfidentialCoordinationCapabilityError:
        return _access_decision("candidate_granted", "malformed_membership_boundary", shard_ref, cap_ref, current)
    if boundary["private_shard_ref"] != shard_ref:
        return _access_decision("candidate_granted", "membership_boundary_shard_mismatch", shard_ref, cap_ref, current)
    if grant["membership_boundary_ref"] != boundary["membership_boundary_ref"]:
        return _access_decision("candidate_granted", "membership_boundary_ref_mismatch", shard_ref, cap_ref, current)

    return _access_decision("active_local", "grant_current_and_not_revoked", shard_ref, cap_ref, current)


def validate_ccss_002_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_invalid_phase_1325",
            "CCSS-002 manifest must be a mapping",
        )
    _reject_unsafe_json_tree(manifest)
    payload = dict(manifest)
    required_keys = {
        "access_states",
        "authorization_flags",
        "contract_version",
        "grant_revocation_boundary_recorded",
        "local_only",
        "max_canonical_json_bytes",
        "max_reference_list_items",
        "membership_plaintext_disclosure_forbidden",
        "next_phase",
        "optional_zk_interface_boundary_recorded",
        "private_shard_access_control_boundary_recorded",
        "public_confidential_coordination_serving_enabled",
        "public_membership_directory_enabled",
        "public_p2p_enabled",
        "public_zk_verifier_enabled",
        "record_kinds",
        "tokens",
    }
    if set(payload) != required_keys:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_keys_invalid_phase_1325",
            "CCSS-002 manifest keys do not match the Phase 1325 contract",
        )
    if payload.get("contract_version") != CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_contract_version_invalid_phase_1325",
            "CCSS-002 manifest version is invalid",
        )
    for key in (
        "grant_revocation_boundary_recorded",
        "local_only",
        "membership_plaintext_disclosure_forbidden",
        "optional_zk_interface_boundary_recorded",
        "private_shard_access_control_boundary_recorded",
    ):
        if payload.get(key) is not True:
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_manifest_required_true_invalid_phase_1325",
                "CCSS-002 manifest true flag is invalid",
            )
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_membership_directory_enabled",
        "public_p2p_enabled",
        "public_zk_verifier_enabled",
    ):
        _require_false(payload.get(key), token=MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN)
    if payload.get("access_states") != list(_ACCESS_STATES):
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_access_states_invalid_phase_1325",
            "CCSS-002 access states are invalid",
        )
    if payload.get("record_kinds") != sorted(_RECORD_KEYS_BY_KIND):
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_record_kinds_invalid_phase_1325",
            "CCSS-002 record kinds are invalid",
        )
    if payload.get("tokens") != ccss_002_required_tokens():
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_tokens_invalid_phase_1325",
            "CCSS-002 manifest tokens are invalid",
        )
    if payload.get("authorization_flags") != _false_authorization_flags():
        raise ConfidentialCoordinationCapabilityError(
            MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN,
            "CCSS-002 authorization flags must remain false",
        )
    if payload.get("max_canonical_json_bytes") != _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_size_bound_invalid_phase_1325",
            "CCSS-002 canonical JSON bound is invalid",
        )
    if payload.get("max_reference_list_items") != _MAX_REF_LIST_ITEMS:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_ref_bound_invalid_phase_1325",
            "CCSS-002 reference list bound is invalid",
        )
    if payload.get("next_phase") != PHASE_1326_NEXT_TOKEN:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_manifest_next_phase_invalid_phase_1325",
            "CCSS-002 manifest next phase is invalid",
        )
    canonical_ccss_002_json(payload)
    return payload


def validate_ccss_002_record(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_record_invalid_phase_1325",
            "CCSS-002 record must be a mapping",
        )
    _reject_unsafe_json_tree(record)
    payload = dict(record)
    kind = _require_choice(
        "record_kind",
        payload.get("record_kind"),
        allowed=tuple(_RECORD_KEYS_BY_KIND),
        token="ccss_002_record_kind_invalid_phase_1325",
    )
    if set(payload) != _RECORD_KEYS_BY_KIND[kind]:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_record_keys_invalid_phase_1325",
            "CCSS-002 record keys do not match the Phase 1325 contract",
        )
    if payload.get("contract_version") != CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_contract_version_invalid_phase_1325",
            "CCSS-002 record version is invalid",
        )
    _reject_forbidden_private_keys(payload)
    _reject_forbidden_private_values(payload)
    if kind == "capability_policy_ref":
        return _validate_capability_policy_ref(payload)
    if kind == "membership_boundary_ref":
        return _validate_membership_boundary_ref(payload)
    if kind == "capability_grant_ref":
        return _validate_capability_grant_ref(payload)
    if kind == "capability_revocation_ref":
        return _validate_capability_revocation_ref(payload)
    return _validate_zk_membership_interface_ref(payload)


def canonical_ccss_002_json(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_payload_size_exceeded_phase_1325",
            "canonical JSON payload exceeds byte bound",
        )
    return canonical


def ccss_002_record_ref(record: Mapping[str, Any]) -> str:
    payload = validate_ccss_002_record(record)
    return f"ccss_002_record:{_hash_payload(payload)}"


def export_ccss_002_record_json(record: Mapping[str, Any]) -> str:
    return canonical_ccss_002_json(validate_ccss_002_record(record))


def _validate_capability_policy_ref(payload: Mapping[str, Any]) -> CapabilityPolicyRef:
    normalized: dict[str, Any] = {
        "access_states": _normalize_exact_text_list(
            payload.get("access_states"),
            expected=_ACCESS_STATES,
            token="ccss_002_access_states_invalid_phase_1325",
        ),
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "deny_states": _normalize_exact_text_list(
            payload.get("deny_states"),
            expected=_DENY_STATES,
            token="ccss_002_deny_states_invalid_phase_1325",
        ),
        "fail_closed_conditions": _normalize_text_list(
            payload.get("fail_closed_conditions"),
            token="ccss_002_fail_closed_conditions_invalid_phase_1325",
            max_items=_MAX_REF_LIST_ITEMS,
        ),
        "hash_inputs": _normalize_text_list(
            payload.get("hash_inputs"),
            token="ccss_002_hash_inputs_invalid_phase_1325",
            max_items=_MAX_REF_LIST_ITEMS,
        ),
        "local_only": _require_true(payload.get("local_only")),
        "local_policy_inputs": _normalize_text_list(
            payload.get("local_policy_inputs"),
            token="ccss_002_local_policy_inputs_invalid_phase_1325",
            max_items=_MAX_REF_LIST_ITEMS,
        ),
        "membership_boundary_ref": _require_prefixed_digest(
            "membership_boundary_ref",
            payload.get("membership_boundary_ref"),
            allowed_prefixes=("membership_boundary",),
        ),
        "non_protocol_metadata_fields": _normalize_text_list(
            payload.get("non_protocol_metadata_fields"),
            token="ccss_002_non_protocol_metadata_fields_invalid_phase_1325",
            max_items=_MAX_REF_LIST_ITEMS,
        ),
        "ordering_model": _require_choice(
            "ordering_model",
            payload.get("ordering_model"),
            allowed=("epoch_then_local_sequence_no_wall_clock",),
            token="ccss_002_ordering_model_invalid_phase_1325",
        ),
        "policy_epoch": _require_epoch("policy", payload.get("policy_epoch")),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token="ccss_002_public_serving_forbidden_phase_1325",
        ),
        "record_kind": "capability_policy_ref",
        "revocation_wins_over_grant": _require_true_token(
            payload.get("revocation_wins_over_grant"),
            token="ccss_002_revocation_precedence_invalid_phase_1325",
        ),
    }
    expected = f"capability_policy:{_hash_payload(normalized)}"
    normalized["capability_policy_ref"] = _require_prefixed_digest(
        "capability_policy_ref",
        payload.get("capability_policy_ref"),
        allowed_prefixes=("capability_policy",),
    )
    if normalized["capability_policy_ref"] != expected:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_capability_policy_ref_mismatch_phase_1325",
            "capability policy ref does not match canonical payload hash",
        )
    return normalized


def _validate_membership_boundary_ref(payload: Mapping[str, Any]) -> MembershipBoundaryRef:
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "boundary_epoch": _require_epoch("boundary", payload.get("boundary_epoch")),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "local_only": _require_true(payload.get("local_only")),
        "member_count_disclosed": _require_false(
            payload.get("member_count_disclosed"),
            token=MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN,
        ),
        "membership_material": _require_choice(
            "membership_material",
            payload.get("membership_material"),
            allowed=("opaque_commitment_refs_only",),
            token="ccss_002_membership_material_invalid_phase_1325",
        ),
        "membership_proof_ref": _require_prefixed_digest(
            "membership_proof_ref",
            payload.get("membership_proof_ref"),
            allowed_prefixes=("membership_proof",),
        ),
        "membership_root_ref": _require_prefixed_digest(
            "membership_root_ref",
            payload.get("membership_root_ref"),
            allowed_prefixes=("membership_root",),
        ),
        "participant_list_disclosed": _require_false(
            payload.get("participant_list_disclosed"),
            token=MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN,
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token="ccss_002_public_serving_forbidden_phase_1325",
        ),
        "record_kind": "membership_boundary_ref",
    }
    expected = f"membership_boundary:{_hash_payload(normalized)}"
    normalized["membership_boundary_ref"] = _require_prefixed_digest(
        "membership_boundary_ref",
        payload.get("membership_boundary_ref"),
        allowed_prefixes=("membership_boundary",),
    )
    if normalized["membership_boundary_ref"] != expected:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_membership_boundary_ref_mismatch_phase_1325",
            "membership boundary ref does not match canonical payload hash",
        )
    return normalized


def _validate_capability_grant_ref(payload: Mapping[str, Any]) -> CapabilityGrantRef:
    valid_from = _require_epoch("valid_from", payload.get("valid_from_epoch"))
    valid_to = _require_epoch("valid_to", payload.get("valid_to_epoch"))
    if valid_to < valid_from:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_grant_epoch_window_invalid_phase_1325",
            "grant validity window is invalid",
        )
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "capability_policy_ref": _require_prefixed_digest(
            "capability_policy_ref",
            payload.get("capability_policy_ref"),
            allowed_prefixes=("capability_policy",),
        ),
        "capability_ref": _require_prefixed_digest(
            "capability_ref",
            payload.get("capability_ref"),
            allowed_prefixes=("capability",),
        ),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "grant_epoch": _require_epoch("grant", payload.get("grant_epoch")),
        "grant_scope": _require_choice(
            "grant_scope",
            payload.get("grant_scope"),
            allowed=_GRANT_SCOPES,
            token="ccss_002_grant_scope_invalid_phase_1325",
        ),
        "grant_sequence": _require_sequence("grant_sequence", payload.get("grant_sequence")),
        "grant_state": _require_choice(
            "grant_state",
            payload.get("grant_state"),
            allowed=("candidate_granted",),
            token="ccss_002_grant_state_invalid_phase_1325",
        ),
        "local_only": _require_true(payload.get("local_only")),
        "membership_boundary_ref": _require_prefixed_digest(
            "membership_boundary_ref",
            payload.get("membership_boundary_ref"),
            allowed_prefixes=("membership_boundary",),
        ),
        "membership_proof_ref": _require_prefixed_digest(
            "membership_proof_ref",
            payload.get("membership_proof_ref"),
            allowed_prefixes=("membership_proof",),
        ),
        "ordering_basis": _require_choice(
            "ordering_basis",
            payload.get("ordering_basis"),
            allowed=("epoch_then_grant_sequence_no_wall_clock",),
            token="ccss_002_grant_ordering_invalid_phase_1325",
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token="ccss_002_public_serving_forbidden_phase_1325",
        ),
        "record_kind": "capability_grant_ref",
        "shard_header_ref": _require_prefixed_digest(
            "shard_header_ref",
            payload.get("shard_header_ref"),
            allowed_prefixes=("private_shard_header",),
        ),
        "valid_from_epoch": valid_from,
        "valid_to_epoch": valid_to,
    }
    expected = f"capability_grant:{_hash_payload(normalized)}"
    normalized["grant_ref"] = _require_prefixed_digest(
        "grant_ref",
        payload.get("grant_ref"),
        allowed_prefixes=("capability_grant",),
    )
    if normalized["grant_ref"] != expected:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_grant_ref_mismatch_phase_1325",
            "capability grant ref does not match canonical payload hash",
        )
    return normalized


def _validate_capability_revocation_ref(payload: Mapping[str, Any]) -> CapabilityRevocationRef:
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "capability_ref": _require_prefixed_digest(
            "capability_ref",
            payload.get("capability_ref"),
            allowed_prefixes=("capability",),
        ),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "grant_ref": _require_prefixed_digest(
            "grant_ref",
            payload.get("grant_ref"),
            allowed_prefixes=("capability_grant",),
        ),
        "local_only": _require_true(payload.get("local_only")),
        "ordering_basis": _require_choice(
            "ordering_basis",
            payload.get("ordering_basis"),
            allowed=("epoch_then_revocation_sequence_no_wall_clock",),
            token="ccss_002_revocation_ordering_invalid_phase_1325",
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token="ccss_002_public_serving_forbidden_phase_1325",
        ),
        "record_kind": "capability_revocation_ref",
        "revocation_epoch": _require_epoch("revocation", payload.get("revocation_epoch")),
        "revocation_scope": _require_choice(
            "revocation_scope",
            payload.get("revocation_scope"),
            allowed=("capability_grant_ref_only",),
            token="ccss_002_revocation_scope_invalid_phase_1325",
        ),
        "revocation_sequence": _require_sequence(
            "revocation_sequence",
            payload.get("revocation_sequence"),
        ),
        "revocation_wins_over_grant": _require_true_token(
            payload.get("revocation_wins_over_grant"),
            token="ccss_002_revocation_precedence_invalid_phase_1325",
        ),
    }
    expected = f"capability_revocation:{_hash_payload(normalized)}"
    normalized["revocation_ref"] = _require_prefixed_digest(
        "revocation_ref",
        payload.get("revocation_ref"),
        allowed_prefixes=("capability_revocation",),
    )
    if normalized["revocation_ref"] != expected:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_revocation_ref_mismatch_phase_1325",
            "capability revocation ref does not match canonical payload hash",
        )
    return normalized


def _validate_zk_membership_interface_ref(payload: Mapping[str, Any]) -> ZKMembershipInterfaceRef:
    normalized: dict[str, Any] = {
        "authorization_flags": _normalize_false_flag_mapping(payload.get("authorization_flags")),
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "decision_state_without_ratified_verifier": _require_choice(
            "decision_state_without_ratified_verifier",
            payload.get("decision_state_without_ratified_verifier"),
            allowed=("zk_deferred",),
            token="ccss_002_zk_decision_state_invalid_phase_1325",
        ),
        "interface_status": _require_choice(
            "interface_status",
            payload.get("interface_status"),
            allowed=("seam_only_no_ratified_verifier",),
            token="ccss_002_zk_interface_status_invalid_phase_1325",
        ),
        "local_only": _require_true(payload.get("local_only")),
        "membership_boundary_ref": _require_prefixed_digest(
            "membership_boundary_ref",
            payload.get("membership_boundary_ref"),
            allowed_prefixes=("membership_boundary",),
        ),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            payload.get("private_shard_ref"),
            allowed_prefixes=("private_shard",),
        ),
        "proof_payload_disclosed": _require_false(
            payload.get("proof_payload_disclosed"),
            token=OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
        ),
        "proof_system_ref": _require_prefixed_digest(
            "proof_system_ref",
            payload.get("proof_system_ref"),
            allowed_prefixes=("zk_proof_system",),
        ),
        "proving_system_ratified": _require_false(
            payload.get("proving_system_ratified"),
            token=OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
        ),
        "public_serving_enabled": _require_false(
            payload.get("public_serving_enabled"),
            token="ccss_002_public_serving_forbidden_phase_1325",
        ),
        "public_verifier_enabled": _require_false(
            payload.get("public_verifier_enabled"),
            token=OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
        ),
        "record_kind": "zk_membership_interface_ref",
        "witness_material_disclosed": _require_false(
            payload.get("witness_material_disclosed"),
            token=OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
        ),
        "zk_proof_ref": _require_prefixed_digest(
            "zk_proof_ref",
            payload.get("zk_proof_ref"),
            allowed_prefixes=("zk_membership_proof",),
        ),
    }
    expected = f"zk_membership_interface:{_hash_payload(normalized)}"
    normalized["zk_interface_ref"] = _require_prefixed_digest(
        "zk_interface_ref",
        payload.get("zk_interface_ref"),
        allowed_prefixes=("zk_membership_interface",),
    )
    if normalized["zk_interface_ref"] != expected:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_zk_interface_ref_mismatch_phase_1325",
            "ZK membership interface ref does not match canonical payload hash",
        )
    return normalized


def _access_decision(
    access_state: str,
    deny_reason: str,
    private_shard_ref: str,
    capability_ref: str,
    current_epoch: int,
) -> CapabilityAccessDecision:
    allowed_state = _require_choice(
        "access_state",
        access_state,
        allowed=_ACCESS_STATES,
        token="ccss_002_access_state_invalid_phase_1325",
    )
    body: dict[str, Any] = {
        "access_state": allowed_state,
        "capability_ref": capability_ref,
        "contract_version": CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
        "current_epoch": current_epoch,
        "deny_reason": _require_text("deny_reason", deny_reason),
        "local_access_allowed": allowed_state == "active_local",
        "local_only": True,
        "private_shard_ref": private_shard_ref,
        "public_serving_enabled": False,
        "record_kind": "capability_access_decision",
        "revocation_wins_over_grant": True,
    }
    body["decision_ref"] = f"ccss_002_access_decision:{_hash_payload(body)}"
    return body


def _false_authorization_flags() -> dict[str, bool]:
    return {key: False for key in _FALSE_AUTHORIZATION_FLAGS}


def _normalize_false_flag_mapping(value: object) -> dict[str, bool]:
    if not isinstance(value, Mapping):
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_authorization_flags_invalid_phase_1325",
            "authorization flags must be a mapping",
        )
    flags = dict(value)
    if set(flags) != set(_FALSE_AUTHORIZATION_FLAGS):
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_authorization_flags_invalid_phase_1325",
            "authorization flags do not match the Phase 1325 contract",
        )
    for key in _FALSE_AUTHORIZATION_FLAGS:
        _require_false(
            flags.get(key),
            token="ccss_002_authorization_flag_forbidden_phase_1325",
        )
    return {key: False for key in _FALSE_AUTHORIZATION_FLAGS}


def _normalize_exact_text_list(
    value: object,
    *,
    expected: tuple[str, ...],
    token: str,
) -> list[str]:
    observed = _normalize_text_list(value, token=token, max_items=len(expected))
    if observed != list(expected):
        raise ConfidentialCoordinationCapabilityError(token, "text list is invalid")
    return observed


def _normalize_text_list(value: object, *, token: str, max_items: int) -> list[str]:
    if not isinstance(value, list):
        raise ConfidentialCoordinationCapabilityError(token, "text list must be a list")
    if len(value) > max_items:
        raise ConfidentialCoordinationCapabilityError(token, "text list exceeds bound")
    return [_require_text("list_item", item) for item in value]


def _normalize_ref_set(
    value: Collection[str],
    *,
    token: str,
    allowed_prefixes: tuple[str, ...],
    max_items: int,
) -> set[str]:
    if not isinstance(value, Collection) or isinstance(value, (str, bytes, bytearray)):
        raise ConfidentialCoordinationCapabilityError(token, "reference collection is invalid")
    if len(value) > max_items:
        raise ConfidentialCoordinationCapabilityError(token, "reference collection exceeds bound")
    refs = {
        _require_prefixed_digest("ref", item, allowed_prefixes=allowed_prefixes)
        for item in value
    }
    if len(refs) != len(value):
        raise ConfidentialCoordinationCapabilityError(token, "reference collection contains duplicates")
    return refs


def _require_epoch(label: str, value: object) -> int:
    epoch = _require_non_negative_int(f"{label}_epoch", value)
    if epoch < 1:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_epoch_invalid_phase_1325",
            "epoch must be positive",
        )
    if epoch > _MAX_EPOCH:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_epoch_invalid_phase_1325",
            "epoch value exceeds bound",
        )
    return epoch


def _require_sequence(label: str, value: object) -> int:
    sequence = _require_non_negative_int(label, value)
    if sequence < 1 or sequence > _MAX_SEQUENCE:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_invalid_phase_1325",
            "sequence must be positive and bounded",
        )
    return sequence


def _require_non_negative_int(label: str, value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_invalid_phase_1325",
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
        raise ConfidentialCoordinationCapabilityError(token, "field value is not allowed")
    return text


def _require_true(value: object) -> bool:
    if value is not True:
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_local_only_required_phase_1325",
            "local-only flag must be true",
        )
    return True


def _require_true_token(value: object, *, token: str) -> bool:
    if value is not True:
        raise ConfidentialCoordinationCapabilityError(token, "required true flag is invalid")
    return True


def _require_false(value: object, *, token: str) -> bool:
    if value is not False:
        raise ConfidentialCoordinationCapabilityError(token, "authorization flag must be false")
    return False


def _require_prefixed_digest(
    label: str,
    value: object,
    *,
    allowed_prefixes: tuple[str, ...],
) -> str:
    text = _require_text(label, value)
    if ":" not in text:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_ref_invalid_phase_1325",
            "reference must use prefix:digest format",
        )
    prefix, digest = text.split(":", 1)
    if prefix not in allowed_prefixes:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_ref_invalid_phase_1325",
            "reference prefix is not allowed",
        )
    _require_hex_digest(label, digest)
    return text


def _require_hex_digest(label: str, value: object) -> str:
    text = _require_text(label, value)
    if len(text) != _HEX_DIGEST_LENGTH or any(char not in _HEX for char in text):
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_digest_invalid_phase_1325",
            "digest must be lowercase sha256 hex",
        )
    return text


def _require_text(label: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_text_invalid_phase_1325",
            "expected non-empty text",
        )
    if len(value) > _MAX_TEXT_LENGTH or any(ord(char) < 0x20 or char == "\x7f" for char in value):
        raise ConfidentialCoordinationCapabilityError(
            f"ccss_002_{label}_text_invalid_phase_1325",
            "text field is invalid or oversized",
        )
    return value


def _hash_payload(payload: Mapping[str, Any]) -> str:
    canonical = canonical_ccss_002_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _reject_forbidden_private_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in _FORBIDDEN_PRIVATE_KEYS:
                raise ConfidentialCoordinationCapabilityError(
                    "ccss_002_private_field_forbidden_phase_1325",
                    "private field is forbidden in CCSS-002 records",
                )
            _reject_forbidden_private_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_private_keys(item)


def _reject_forbidden_private_values(value: object) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in _FORBIDDEN_VALUE_FRAGMENTS):
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_private_value_forbidden_phase_1325",
                "private value fragment is forbidden in CCSS-002 records",
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
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_payload_size_exceeded_phase_1325",
                "canonical JSON payload exceeds byte bound",
            )

    def visit(item: object, depth: int) -> None:
        nonlocal node_count
        if depth > _MAX_PAYLOAD_DEPTH:
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_payload_depth_exceeded_phase_1325",
                "payload exceeds depth bound",
            )
        node_count += 1
        if node_count > _MAX_PAYLOAD_NODES:
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_payload_node_limit_exceeded_phase_1325",
                "payload exceeds node bound",
            )
        if isinstance(item, (Mapping, list)):
            marker = id(item)
            if marker in seen:
                raise ConfidentialCoordinationCapabilityError(
                    "ccss_002_payload_cycle_forbidden_phase_1325",
                    "payload cycles are forbidden",
                )
            seen.add(marker)
            if isinstance(item, Mapping):
                for key, nested in item.items():
                    if not isinstance(key, str):
                        raise ConfidentialCoordinationCapabilityError(
                            "ccss_002_payload_key_invalid_phase_1325",
                            "payload keys must be strings",
                        )
                    _require_text("payload_key", key)
                    add_payload_bytes(key)
                    node_count += 1
                    if node_count > _MAX_PAYLOAD_NODES:
                        raise ConfidentialCoordinationCapabilityError(
                            "ccss_002_payload_node_limit_exceeded_phase_1325",
                            "payload exceeds node bound",
                        )
                    visit(nested, depth + 1)
            else:
                for nested in item:
                    visit(nested, depth + 1)
            seen.remove(marker)
            return
        if isinstance(item, tuple):
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_payload_key_invalid_phase_1325",
                "tuple values are not canonical JSON",
            )
        if isinstance(item, float):
            raise ConfidentialCoordinationCapabilityError(
                "ccss_002_float_values_forbidden_phase_1325",
                "float values are forbidden",
            )
        if item is None or isinstance(item, (str, int, bool)):
            if isinstance(item, str):
                _require_text("payload_text", item)
                add_payload_bytes(item)
            elif isinstance(item, int) and not isinstance(item, bool):
                if abs(item) > _MAX_CANONICAL_JSON_INT_ABS:
                    raise ConfidentialCoordinationCapabilityError(
                        "ccss_002_payload_int_invalid_phase_1325",
                        "integer payload exceeds canonical JSON integer bound",
                    )
                add_payload_bytes(str(item))
            return
        raise ConfidentialCoordinationCapabilityError(
            "ccss_002_payload_key_invalid_phase_1325",
            "payload contains non-JSON value",
        )

    visit(value, 0)


__all__ = [
    "CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION",
    "CapabilityAccessDecision",
    "CapabilityGrantRef",
    "CapabilityPolicyRef",
    "CapabilityRevocationRef",
    "ConfidentialCoordinationCapabilityError",
    "MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN",
    "MembershipBoundaryRef",
    "OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN",
    "PHASE_1326_NEXT_TOKEN",
    "PRIVATE_SHARD_ACCESS_CONTROL_BOUNDARY_RECORDED_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1325_TOKEN",
    "ZKMembershipInterfaceRef",
    "build_capability_grant_ref",
    "build_capability_policy_ref",
    "build_capability_revocation_ref",
    "build_local_access_decision",
    "build_membership_boundary_ref",
    "build_zk_membership_interface_ref",
    "canonical_ccss_002_json",
    "ccss_002_capability_membership_boundary_manifest",
    "ccss_002_record_ref",
    "ccss_002_required_tokens",
    "export_ccss_002_record_json",
    "validate_ccss_002_manifest",
    "validate_ccss_002_record",
]
