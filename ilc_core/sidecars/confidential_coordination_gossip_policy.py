"""Phase 1327 CCSS-004 gossip announce/pull jitter and cover policy tests.

This module records a private/local contract for bounded gossip announce
metadata, receiver-controlled pull policy, jitter/batching/cover-policy checks,
and traffic-analysis negative tests. It does not activate public P2P, public
relays, public confidential coordination serving, or an anonymity guarantee.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping
from typing import Any


CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION = (
    "ccss_004_gossip_jitter_cover_policy_tests_phase_1327.v0.1"
)
GOSSIP_ANNOUNCE_PULL_JITTER_POLICY_RECORDED_TOKEN = (
    "gossip_announce_pull_jitter_policy_recorded_phase_1327"
)
TRAFFIC_ANALYSIS_NEGATIVE_TESTS_RECORDED_TOKEN = (
    "traffic_analysis_negative_tests_recorded_phase_1327"
)
ANONYMITY_GUARANTEE_NOT_CLAIMED_TOKEN = "anonymity_guarantee_not_claimed_phase_1327"
PHASE_1328_NEXT_TOKEN = "phase_1328_ccss_private_droplet_reproducibility_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1327_TOKEN = (
    "public_rc_remains_blocked_after_phase_1327"
)

GossipAnnouncePullPolicyRef = dict[str, Any]
TrafficAnalysisMatrixRef = dict[str, Any]
GossipCoverPolicyDecision = dict[str, Any]

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_EPOCH = 1_000_000_000_000
_MAX_SEQUENCE = 1_000_000_000_000
_MAX_CANONICAL_JSON_INT_ABS = _MAX_SEQUENCE
_MAX_REF_LIST_ITEMS = 256
_MAX_ANNOUNCE_REFS_PER_BATCH = 64
_MAX_PULL_REFS_PER_BATCH = 64
_MAX_COVER_MESSAGES_PER_IDLE_EPOCH = 16
_MAX_JITTER_EPOCHS = 3
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_RECORD_KEYS_BY_KIND = {
    "traffic_analysis_matrix_ref": frozenset(
        {
            "authorization_flags",
            "contract_version",
            "local_only",
            "matrix_epoch",
            "matrix_ref",
            "matrix_sequence",
            "no_anonymity_guarantee",
            "public_serving_enabled",
            "record_kind",
            "rows",
        }
    ),
    "gossip_announce_pull_policy_ref": frozenset(
        {
            "announce_scope",
            "authorization_flags",
            "batching_mode",
            "contract_version",
            "cover_policy_mode",
            "local_only",
            "max_announce_refs_per_batch",
            "max_jitter_epochs",
            "max_pull_refs_per_batch",
            "metadata_correlation_tests_required",
            "min_cover_messages_per_idle_epoch",
            "min_jitter_epochs",
            "no_anonymity_guarantee",
            "policy_epoch",
            "policy_ref",
            "policy_sequence",
            "private_shard_ref",
            "public_serving_enabled",
            "pull_payload_class",
            "push_payload_class",
            "receiver_controlled_pull",
            "record_kind",
            "runtime_jitter_source",
            "test_fixture_jitter_derivation",
            "traffic_analysis_matrix_ref",
        }
    ),
    "gossip_cover_policy_decision": frozenset(
        {
            "announce_ref_count",
            "authorization_flags",
            "contract_version",
            "cover_messages_in_idle_epoch",
            "decision_epoch",
            "decision_reason",
            "decision_ref",
            "decision_sequence",
            "decision_state",
            "local_only",
            "metadata_correlation_tests_required",
            "no_anonymity_guarantee",
            "participant_metadata_field_count",
            "policy_ref",
            "private_local_action_allowed",
            "private_shard_ref",
            "public_network_attempt_blocked",
            "public_serving_enabled",
            "pull_ref_count",
            "record_kind",
            "traffic_analysis_matrix_ref",
        }
    ),
}
_REF_PREFIX_BY_KIND = {
    "gossip_announce_pull_policy_ref": "gossip_announce_pull_policy",
    "gossip_cover_policy_decision": "gossip_cover_policy_decision",
    "traffic_analysis_matrix_ref": "traffic_analysis_matrix",
}
_TRAFFIC_OBSERVATION_IDS = (
    "sender_timing_correlation_against_local_enqueue_time",
    "receiver_timing_correlation_against_local_delivery_time",
    "batch_size_leakage_across_shards",
    "cover_message_absence_during_idle_periods",
    "retry_burst_correlation_after_failed_delivery",
    "shard_header_correlation_across_announce_pull_cycles",
    "harness_identity_leakage_through_adapter_metadata",
)
_TRAFFIC_MITIGATION_BY_OBSERVATION = {
    "sender_timing_correlation_against_local_enqueue_time": "bounded_release_jitter_epochs",
    "receiver_timing_correlation_against_local_delivery_time": "receiver_controlled_pull_window",
    "batch_size_leakage_across_shards": "bounded_epoch_batching",
    "cover_message_absence_during_idle_periods": "idle_cover_messages_required",
    "retry_burst_correlation_after_failed_delivery": "retry_burst_coalescing_required",
    "shard_header_correlation_across_announce_pull_cycles": "opaque_shard_header_ref_only",
    "harness_identity_leakage_through_adapter_metadata": "adapter_identity_metadata_forbidden",
}
_TRAFFIC_ROW_KEYS = frozenset(
    {
        "adversary_observation",
        "evidence_artifact",
        "non_claim",
        "residual_risk",
        "test_status",
        "tested_mitigation",
    }
)
_TEST_STATUSES = frozenset({"tested_local_negative", "not_tested_carry_forward"})
_NON_CLAIMS = frozenset(
    {
        "does_not_claim_anonymity_or_unlinkability",
        "metadata_correlation_reduced_not_eliminated",
    }
)
_FALSE_AUTHORIZATION_FLAGS = (
    "anonymity_guarantee_claimed",
    "cover_policy_disabled",
    "deterministic_runtime_jitter_seed_enabled",
    "direct_peer_address_disclosure_enabled",
    "harness_identity_disclosure_enabled",
    "ip_address_disclosure_enabled",
    "network_transport_enabled",
    "non_loopback_listener_enabled",
    "participant_identity_metadata_enabled",
    "plaintext_disclosure_enabled",
    "public_confidential_coordination_serving_enabled",
    "public_confidential_messaging_claimed",
    "public_listener_enabled",
    "public_p2p_enabled",
    "public_peer_discovery_enabled",
    "public_projection_serving_enabled",
    "public_pull_endpoint_enabled",
    "public_push_endpoint_enabled",
    "public_relay_serving_enabled",
    "public_serving_enabled",
    "public_sidecar_serving_enabled",
    "raw_route_history_disclosure_enabled",
    "release_authority_enabled",
    "retry_schedule_disclosure_enabled",
    "sender_receiver_linkability_claimed",
    "signal_equivalent_claimed",
    "source_publication_authorized",
    "unbounded_batch_enabled",
    "unlinkability_claimed",
    "zero_jitter_enabled",
)
_FORBIDDEN_PRIVATE_KEYS = frozenset(
    {
        "AgentID",
        "agent_id",
        "agentid",
        "client_ip",
        "creator_agent_id",
        "direct_peer_address",
        "harness_identity",
        "identity_seed",
        "ip_address",
        "membership_list",
        "mnemonic",
        "openclaw_identity",
        "participant_identity",
        "plaintext",
        "plaintext_body",
        "plaintext_payload",
        "private_key",
        "raw_payload",
        "raw_route_history",
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
        "agent_id=",
        "client_ip=",
        "direct_peer_address=",
        "harness_identity=",
        "identity_seed",
        "ip_address=",
        "membership_list",
        "mnemonic",
        "participant_identity=",
        "plaintext_payload",
        "private_key",
        "raw_route_history",
        "recipient_identity=",
        "retry_schedule=",
        "route_history=",
        "secret_material",
        "sender_identity=",
        "tailscale_identity=",
        "wallet_id=",
        "zk_witness",
    )
)
_DECISION_STATES = (
    "announce_pending_local",
    "pull_available_local",
    "rejected_cover_disabled",
    "rejected_deterministic_runtime_jitter_seed",
    "rejected_participant_metadata",
    "rejected_public_network",
    "rejected_unbounded_batch",
    "rejected_zero_jitter",
    "not_tested_carry_forward",
)
_DECISION_REASON_BY_STATE = {
    "announce_pending_local": "none",
    "pull_available_local": "none",
    "rejected_cover_disabled": "cover_policy_disabled",
    "rejected_deterministic_runtime_jitter_seed": "runtime_jitter_seed_forbidden",
    "rejected_participant_metadata": "participant_metadata_forbidden",
    "rejected_public_network": "public_network_forbidden",
    "rejected_unbounded_batch": "batch_bound_exceeded",
    "rejected_zero_jitter": "zero_jitter_forbidden",
    "not_tested_carry_forward": "not_tested_carry_forward",
}
_ALLOWED_ACTION_STATES = frozenset({"announce_pending_local", "pull_available_local"})


class ConfidentialCoordinationGossipPolicyError(ValueError):
    """Stable fail-closed error for CCSS-004 contract validation."""

    def __init__(self, token: str, detail: str):
        super().__init__(token)
        self.token = token
        self.detail = detail


def ccss_004_required_tokens() -> list[str]:
    return [
        CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
        GOSSIP_ANNOUNCE_PULL_JITTER_POLICY_RECORDED_TOKEN,
        TRAFFIC_ANALYSIS_NEGATIVE_TESTS_RECORDED_TOKEN,
        ANONYMITY_GUARANTEE_NOT_CLAIMED_TOKEN,
        PHASE_1328_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1327_TOKEN,
    ]


def ccss_004_gossip_jitter_cover_policy_manifest() -> dict[str, Any]:
    manifest = {
        "anonymity_guarantee_claimed": False,
        "anonymity_guarantee_not_claimed": True,
        "contract_version": CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
        "decision_states": list(_DECISION_STATES),
        "gossip_announce_pull_jitter_policy_recorded": True,
        "local_only": True,
        "max_announce_refs_per_batch": _MAX_ANNOUNCE_REFS_PER_BATCH,
        "max_jitter_epochs": _MAX_JITTER_EPOCHS,
        "max_pull_refs_per_batch": _MAX_PULL_REFS_PER_BATCH,
        "metadata_correlation_tests_required": True,
        "next_phase": PHASE_1328_NEXT_TOKEN,
        "public_confidential_coordination_serving_enabled": False,
        "public_confidential_messaging_claimed": False,
        "public_listener_enabled": False,
        "public_p2p_enabled": False,
        "public_peer_discovery_enabled": False,
        "public_relay_serving_enabled": False,
        "public_serving_enabled": False,
        "public_sidecar_serving_enabled": False,
        "signal_equivalent_claimed": False,
        "tokens": ccss_004_required_tokens(),
        "traffic_analysis_negative_tests_recorded": True,
        "traffic_analysis_observations": list(_TRAFFIC_OBSERVATION_IDS),
        "unlinkability_claimed": False,
    }
    return validate_ccss_004_manifest(manifest)


def validate_ccss_004_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(_require_mapping(manifest, token="ccss_004_manifest_invalid_phase_1327"))
    _reject_unsafe_json_tree(payload)
    if payload.get("contract_version") != CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_version_invalid_phase_1327",
            "manifest contract version mismatch",
        )
    for key in (
        "anonymity_guarantee_not_claimed",
        "gossip_announce_pull_jitter_policy_recorded",
        "local_only",
        "metadata_correlation_tests_required",
        "traffic_analysis_negative_tests_recorded",
    ):
        _require_true(payload.get(key), token="ccss_004_manifest_true_flag_invalid_phase_1327")
    for key in (
        "anonymity_guarantee_claimed",
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_listener_enabled",
        "public_p2p_enabled",
        "public_peer_discovery_enabled",
        "public_relay_serving_enabled",
        "public_serving_enabled",
        "public_sidecar_serving_enabled",
        "signal_equivalent_claimed",
        "unlinkability_claimed",
    ):
        _require_false(payload.get(key), token="ccss_004_manifest_public_authority_forbidden_phase_1327")
    if payload.get("tokens") != ccss_004_required_tokens():
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_tokens_invalid_phase_1327",
            "manifest token list mismatch",
        )
    if payload.get("next_phase") != PHASE_1328_NEXT_TOKEN:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_next_phase_invalid_phase_1327",
            "manifest next phase mismatch",
        )
    if payload.get("traffic_analysis_observations") != list(_TRAFFIC_OBSERVATION_IDS):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_traffic_observations_invalid_phase_1327",
            "manifest traffic-analysis observation list mismatch",
        )
    if payload.get("decision_states") != list(_DECISION_STATES):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_decision_states_invalid_phase_1327",
            "manifest decision states mismatch",
        )
    if payload.get("max_jitter_epochs") != _MAX_JITTER_EPOCHS:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_jitter_bound_invalid_phase_1327",
            "manifest jitter bound mismatch",
        )
    if payload.get("max_announce_refs_per_batch") != _MAX_ANNOUNCE_REFS_PER_BATCH:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_batch_bound_invalid_phase_1327",
            "manifest announce batch bound mismatch",
        )
    if payload.get("max_pull_refs_per_batch") != _MAX_PULL_REFS_PER_BATCH:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_manifest_pull_batch_bound_invalid_phase_1327",
            "manifest pull batch bound mismatch",
        )
    canonical_ccss_004_json(payload)
    return payload


def build_traffic_analysis_matrix_ref(
    *,
    matrix_epoch: int,
    matrix_sequence: int = 1,
    not_tested_observations: Collection[str] = (),
) -> TrafficAnalysisMatrixRef:
    deferred = _require_text_set(
        not_tested_observations,
        allowed=set(_TRAFFIC_OBSERVATION_IDS),
        token="ccss_004_traffic_observation_invalid_phase_1327",
    )
    rows: list[dict[str, str]] = []
    for observation in _TRAFFIC_OBSERVATION_IDS:
        status = "not_tested_carry_forward" if observation in deferred else "tested_local_negative"
        rows.append(
            {
                "adversary_observation": observation,
                "evidence_artifact": "phase_1327_local_negative_test_fixture",
                "non_claim": "does_not_claim_anonymity_or_unlinkability",
                "residual_risk": "metadata_correlation_reduced_not_eliminated",
                "test_status": status,
                "tested_mitigation": _TRAFFIC_MITIGATION_BY_OBSERVATION[observation],
            }
        )
    body = {
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
        "local_only": True,
        "matrix_epoch": _require_epoch("matrix", matrix_epoch),
        "matrix_sequence": _require_sequence("matrix", matrix_sequence),
        "no_anonymity_guarantee": True,
        "public_serving_enabled": False,
        "record_kind": "traffic_analysis_matrix_ref",
        "rows": rows,
    }
    body["matrix_ref"] = _reference_for("traffic_analysis_matrix_ref", body)
    return validate_ccss_004_record(body)


def build_gossip_announce_pull_policy_ref(
    *,
    private_shard_ref: str,
    traffic_analysis_matrix_ref: str,
    policy_epoch: int,
    policy_sequence: int = 1,
    max_jitter_epochs: int = _MAX_JITTER_EPOCHS,
    max_announce_refs_per_batch: int = _MAX_ANNOUNCE_REFS_PER_BATCH,
    max_pull_refs_per_batch: int = _MAX_PULL_REFS_PER_BATCH,
    min_cover_messages_per_idle_epoch: int = 1,
    cover_policy_enabled: bool = True,
    unbounded_batch_enabled: bool = False,
    deterministic_runtime_jitter_seed_enabled: bool = False,
    public_network_enabled: bool = False,
) -> GossipAnnouncePullPolicyRef:
    if public_network_enabled:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_public_network_forbidden_phase_1327",
            "CCSS-004 does not authorize public network transport",
        )
    if deterministic_runtime_jitter_seed_enabled:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_runtime_jitter_seed_forbidden_phase_1327",
            "runtime jitter must use secure randomness or a later ratified VRF",
        )
    max_jitter = _require_bounded_positive_int(
        "max_jitter",
        max_jitter_epochs,
        upper_bound=_MAX_JITTER_EPOCHS,
        zero_token="ccss_004_zero_jitter_forbidden_phase_1327",
    )
    announce_batch = _require_bounded_positive_int(
        "max_announce_refs_per_batch",
        max_announce_refs_per_batch,
        upper_bound=_MAX_ANNOUNCE_REFS_PER_BATCH,
        zero_token="ccss_004_batch_bound_invalid_phase_1327",
    )
    pull_batch = _require_bounded_positive_int(
        "max_pull_refs_per_batch",
        max_pull_refs_per_batch,
        upper_bound=_MAX_PULL_REFS_PER_BATCH,
        zero_token="ccss_004_batch_bound_invalid_phase_1327",
    )
    cover_count = _require_bounded_positive_int(
        "min_cover_messages_per_idle_epoch",
        min_cover_messages_per_idle_epoch,
        upper_bound=_MAX_COVER_MESSAGES_PER_IDLE_EPOCH,
        zero_token="ccss_004_cover_policy_disabled_phase_1327",
    )
    if not cover_policy_enabled:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_cover_policy_disabled_phase_1327",
            "idle cover policy cannot be disabled in the CCSS-004 contract",
        )
    if unbounded_batch_enabled:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_unbounded_batch_forbidden_phase_1327",
            "unbounded announce/pull batches are forbidden",
        )
    body = {
        "announce_scope": "private_local_opaque_availability_only",
        "authorization_flags": _false_authorization_flags(),
        "batching_mode": "bounded_epoch_batch",
        "contract_version": CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
        "cover_policy_mode": "idle_cover_required",
        "local_only": True,
        "max_announce_refs_per_batch": announce_batch,
        "max_jitter_epochs": max_jitter,
        "max_pull_refs_per_batch": pull_batch,
        "metadata_correlation_tests_required": True,
        "min_cover_messages_per_idle_epoch": cover_count,
        "min_jitter_epochs": 0,
        "no_anonymity_guarantee": True,
        "policy_epoch": _require_epoch("policy", policy_epoch),
        "policy_sequence": _require_sequence("policy", policy_sequence),
        "private_shard_ref": _require_prefixed_digest(
            "private_shard_ref",
            private_shard_ref,
            prefixes=("private_shard",),
        ),
        "public_serving_enabled": False,
        "pull_payload_class": "heavy_payload_receiver_controlled",
        "push_payload_class": "bounded_metadata_ref_only",
        "receiver_controlled_pull": True,
        "record_kind": "gossip_announce_pull_policy_ref",
        "runtime_jitter_source": "secure_random_or_ratified_vrf_required",
        "test_fixture_jitter_derivation": "sha256_domain_separated_epoch_ref_fixture_only",
        "traffic_analysis_matrix_ref": _require_prefixed_digest(
            "traffic_analysis_matrix_ref",
            traffic_analysis_matrix_ref,
            prefixes=("traffic_analysis_matrix",),
        ),
    }
    body["policy_ref"] = _reference_for("gossip_announce_pull_policy_ref", body)
    return validate_ccss_004_record(body)


def build_gossip_cover_policy_decision(
    *,
    policy_record: Mapping[str, Any],
    decision_epoch: int,
    decision_sequence: int = 1,
    announce_ref_count: int = 1,
    pull_ref_count: int = 1,
    cover_messages_in_idle_epoch: int = 1,
    public_network_attempted: bool = False,
    deterministic_runtime_jitter_seed_attempted: bool = False,
    participant_metadata_field_count: int = 0,
    pull_available: bool = False,
) -> GossipCoverPolicyDecision:
    policy = validate_ccss_004_record(policy_record)
    if policy["record_kind"] != "gossip_announce_pull_policy_ref":
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_policy_record_kind_invalid_phase_1327",
            "gossip decision requires a gossip announce/pull policy record",
        )
    announce_count = _require_non_negative_int("announce_ref_count", announce_ref_count)
    pull_count = _require_non_negative_int("pull_ref_count", pull_ref_count)
    cover_count = _require_non_negative_int("cover_messages_in_idle_epoch", cover_messages_in_idle_epoch)
    metadata_count = _require_non_negative_int("participant_metadata_field_count", participant_metadata_field_count)

    if public_network_attempted:
        state = "rejected_public_network"
    elif deterministic_runtime_jitter_seed_attempted:
        state = "rejected_deterministic_runtime_jitter_seed"
    elif metadata_count:
        state = "rejected_participant_metadata"
    elif policy["max_jitter_epochs"] < 1:
        state = "rejected_zero_jitter"
    elif cover_count < policy["min_cover_messages_per_idle_epoch"]:
        state = "rejected_cover_disabled"
    elif announce_count > policy["max_announce_refs_per_batch"] or pull_count > policy["max_pull_refs_per_batch"]:
        state = "rejected_unbounded_batch"
    elif pull_available:
        state = "pull_available_local"
    else:
        state = "announce_pending_local"

    body = {
        "announce_ref_count": announce_count,
        "authorization_flags": _false_authorization_flags(),
        "contract_version": CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
        "cover_messages_in_idle_epoch": cover_count,
        "decision_epoch": _require_epoch("decision", decision_epoch),
        "decision_reason": _DECISION_REASON_BY_STATE[state],
        "decision_sequence": _require_sequence("decision", decision_sequence),
        "decision_state": state,
        "local_only": True,
        "metadata_correlation_tests_required": True,
        "no_anonymity_guarantee": True,
        "participant_metadata_field_count": metadata_count,
        "policy_ref": policy["policy_ref"],
        "private_local_action_allowed": state in _ALLOWED_ACTION_STATES,
        "private_shard_ref": policy["private_shard_ref"],
        "public_network_attempt_blocked": public_network_attempted,
        "public_serving_enabled": False,
        "pull_ref_count": pull_count,
        "record_kind": "gossip_cover_policy_decision",
        "traffic_analysis_matrix_ref": policy["traffic_analysis_matrix_ref"],
    }
    body["decision_ref"] = _reference_for("gossip_cover_policy_decision", body)
    return validate_ccss_004_record(body)


def derive_test_fixture_jitter_epoch(
    *,
    policy_record: Mapping[str, Any],
    object_ref: str,
    base_epoch: int,
) -> int:
    """Derive deterministic jitter for tests only, never for runtime scheduling."""

    policy = validate_ccss_004_record(policy_record)
    if policy["record_kind"] != "gossip_announce_pull_policy_ref":
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_policy_record_kind_invalid_phase_1327",
            "jitter fixture requires a gossip announce/pull policy record",
        )
    normalized_object_ref = _require_prefixed_digest(
        "object_ref",
        object_ref,
        prefixes=(
            "encrypted_coordination_envelope",
            "private_shard",
            "sealed_delivery_projection",
            "shard_header_projection",
        ),
    )
    epoch = _require_epoch("base", base_epoch)
    digest = hashlib.sha256(
        (
            "ccss-004-test-fixture-jitter-v1:"
            + policy["policy_ref"]
            + ":"
            + normalized_object_ref
            + ":"
            + str(epoch)
        ).encode("utf-8")
    ).digest()
    jitter = int.from_bytes(digest[:8], "big") % (policy["max_jitter_epochs"] + 1)
    return epoch + jitter


def validate_ccss_004_record(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(_require_mapping(record, token="ccss_004_record_invalid_phase_1327"))
    _reject_unsafe_json_tree(payload)
    _reject_forbidden_private_keys(payload)
    _reject_forbidden_private_values(payload)
    record_kind = _require_choice(
        "record_kind",
        payload.get("record_kind"),
        choices=tuple(_RECORD_KEYS_BY_KIND),
    )
    if set(payload) != _RECORD_KEYS_BY_KIND[record_kind]:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_record_keys_invalid_phase_1327",
            "record keys do not match declared kind",
        )
    if payload.get("contract_version") != CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_record_version_invalid_phase_1327",
            "record contract version mismatch",
        )
    _require_true(payload.get("local_only"), token="ccss_004_record_local_only_invalid_phase_1327")
    _require_false(payload.get("public_serving_enabled"), token="ccss_004_public_serving_forbidden_phase_1327")
    _require_authorization_flags(payload.get("authorization_flags"))
    if payload.get("no_anonymity_guarantee") is not True:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_anonymity_guarantee_claimed_phase_1327",
            "CCSS-004 must explicitly avoid anonymity guarantees",
        )
    if record_kind == "traffic_analysis_matrix_ref":
        return _validate_traffic_analysis_matrix_ref(payload)
    if record_kind == "gossip_announce_pull_policy_ref":
        return _validate_gossip_announce_pull_policy_ref(payload)
    return _validate_gossip_cover_policy_decision(payload)


def canonical_ccss_004_json(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_payload_size_exceeded_phase_1327",
            "canonical JSON payload exceeds byte bound",
        )
    return canonical


def _validate_traffic_analysis_matrix_ref(record: Mapping[str, Any]) -> dict[str, Any]:
    _require_epoch("matrix", record.get("matrix_epoch"))
    _require_sequence("matrix", record.get("matrix_sequence"))
    rows = record.get("rows")
    if not isinstance(rows, list) or len(rows) != len(_TRAFFIC_OBSERVATION_IDS):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_traffic_rows_invalid_phase_1327",
            "traffic-analysis rows must cover every required observation",
        )
    observations: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != _TRAFFIC_ROW_KEYS:
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_traffic_row_invalid_phase_1327",
                "traffic-analysis row shape is invalid",
            )
        observation = _require_choice(
            "adversary_observation",
            row.get("adversary_observation"),
            choices=_TRAFFIC_OBSERVATION_IDS,
        )
        observations.append(observation)
        if row.get("tested_mitigation") != _TRAFFIC_MITIGATION_BY_OBSERVATION[observation]:
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_traffic_mitigation_invalid_phase_1327",
                "traffic-analysis mitigation mismatch",
            )
        _require_choice("test_status", row.get("test_status"), choices=tuple(sorted(_TEST_STATUSES)))
        _require_choice("non_claim", row.get("non_claim"), choices=tuple(sorted(_NON_CLAIMS)))
        _require_text(row.get("evidence_artifact"), label="evidence_artifact")
        _require_text(row.get("residual_risk"), label="residual_risk")
    if tuple(observations) != _TRAFFIC_OBSERVATION_IDS:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_traffic_observations_invalid_phase_1327",
            "traffic-analysis observation ordering mismatch",
        )
    normalized = {key: value for key, value in record.items() if key != "matrix_ref"}
    if record.get("matrix_ref") != _reference_for("traffic_analysis_matrix_ref", normalized):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_matrix_ref_invalid_phase_1327",
            "traffic-analysis matrix reference hash mismatch",
        )
    return dict(record)


def _validate_gossip_announce_pull_policy_ref(record: Mapping[str, Any]) -> dict[str, Any]:
    _require_prefixed_digest("private_shard_ref", record.get("private_shard_ref"), prefixes=("private_shard",))
    _require_prefixed_digest(
        "traffic_analysis_matrix_ref",
        record.get("traffic_analysis_matrix_ref"),
        prefixes=("traffic_analysis_matrix",),
    )
    _require_epoch("policy", record.get("policy_epoch"))
    _require_sequence("policy", record.get("policy_sequence"))
    for key in ("metadata_correlation_tests_required", "receiver_controlled_pull"):
        _require_true(record.get(key), token="ccss_004_policy_true_flag_invalid_phase_1327")
    for key, expected in (
        ("announce_scope", "private_local_opaque_availability_only"),
        ("batching_mode", "bounded_epoch_batch"),
        ("cover_policy_mode", "idle_cover_required"),
        ("pull_payload_class", "heavy_payload_receiver_controlled"),
        ("push_payload_class", "bounded_metadata_ref_only"),
        ("runtime_jitter_source", "secure_random_or_ratified_vrf_required"),
        ("test_fixture_jitter_derivation", "sha256_domain_separated_epoch_ref_fixture_only"),
    ):
        if record.get(key) != expected:
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_policy_mode_invalid_phase_1327",
                "gossip policy mode mismatch",
            )
    if record.get("min_jitter_epochs") != 0:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_min_jitter_invalid_phase_1327",
            "minimum jitter must be zero to preserve bounded fixture semantics",
        )
    _require_bounded_positive_int(
        "max_jitter",
        record.get("max_jitter_epochs"),
        upper_bound=_MAX_JITTER_EPOCHS,
        zero_token="ccss_004_zero_jitter_forbidden_phase_1327",
    )
    _require_bounded_positive_int(
        "max_announce_refs_per_batch",
        record.get("max_announce_refs_per_batch"),
        upper_bound=_MAX_ANNOUNCE_REFS_PER_BATCH,
        zero_token="ccss_004_batch_bound_invalid_phase_1327",
    )
    _require_bounded_positive_int(
        "max_pull_refs_per_batch",
        record.get("max_pull_refs_per_batch"),
        upper_bound=_MAX_PULL_REFS_PER_BATCH,
        zero_token="ccss_004_batch_bound_invalid_phase_1327",
    )
    _require_bounded_positive_int(
        "min_cover_messages_per_idle_epoch",
        record.get("min_cover_messages_per_idle_epoch"),
        upper_bound=_MAX_COVER_MESSAGES_PER_IDLE_EPOCH,
        zero_token="ccss_004_cover_policy_disabled_phase_1327",
    )
    normalized = {key: value for key, value in record.items() if key != "policy_ref"}
    if record.get("policy_ref") != _reference_for("gossip_announce_pull_policy_ref", normalized):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_policy_ref_invalid_phase_1327",
            "gossip policy reference hash mismatch",
        )
    return dict(record)


def _validate_gossip_cover_policy_decision(record: Mapping[str, Any]) -> dict[str, Any]:
    _require_prefixed_digest("policy_ref", record.get("policy_ref"), prefixes=("gossip_announce_pull_policy",))
    _require_prefixed_digest("private_shard_ref", record.get("private_shard_ref"), prefixes=("private_shard",))
    _require_prefixed_digest(
        "traffic_analysis_matrix_ref",
        record.get("traffic_analysis_matrix_ref"),
        prefixes=("traffic_analysis_matrix",),
    )
    _require_epoch("decision", record.get("decision_epoch"))
    _require_sequence("decision", record.get("decision_sequence"))
    for key in ("metadata_correlation_tests_required",):
        _require_true(record.get(key), token="ccss_004_decision_true_flag_invalid_phase_1327")
    state = _require_choice("decision_state", record.get("decision_state"), choices=_DECISION_STATES)
    if record.get("decision_reason") != _DECISION_REASON_BY_STATE[state]:
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_decision_reason_invalid_phase_1327",
            "decision reason does not match decision state",
        )
    if record.get("private_local_action_allowed") is not (state in _ALLOWED_ACTION_STATES):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_decision_allowance_invalid_phase_1327",
            "decision allowance does not match state",
        )
    for key in (
        "announce_ref_count",
        "cover_messages_in_idle_epoch",
        "participant_metadata_field_count",
        "pull_ref_count",
    ):
        _require_non_negative_int(key, record.get(key))
    if record.get("public_network_attempt_blocked") is not (state == "rejected_public_network"):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_public_network_block_state_invalid_phase_1327",
            "public network block marker does not match state",
        )
    normalized = {key: value for key, value in record.items() if key != "decision_ref"}
    if record.get("decision_ref") != _reference_for("gossip_cover_policy_decision", normalized):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_decision_ref_invalid_phase_1327",
            "gossip decision reference hash mismatch",
        )
    return dict(record)


def _reference_for(record_kind: str, body: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical_ccss_004_json(body).encode("utf-8")).hexdigest()
    return f"{_REF_PREFIX_BY_KIND[record_kind]}:{digest}"


def _false_authorization_flags() -> dict[str, bool]:
    return {key: False for key in sorted(_FALSE_AUTHORIZATION_FLAGS)}


def _require_authorization_flags(value: object) -> None:
    flags = _require_mapping(value, token="ccss_004_authorization_flags_invalid_phase_1327")
    if set(flags) != set(_FALSE_AUTHORIZATION_FLAGS):
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_authorization_flags_invalid_phase_1327",
            "authorization flag set mismatch",
        )
    for key in _FALSE_AUTHORIZATION_FLAGS:
        _require_false(
            flags.get(key),
            token="ccss_004_public_or_metadata_authority_forbidden_phase_1327",
        )


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfidentialCoordinationGossipPolicyError(token, "expected mapping")
    return value


def _require_true(value: object, *, token: str) -> None:
    if value is not True:
        raise ConfidentialCoordinationGossipPolicyError(token, "expected true")


def _require_false(value: object, *, token: str) -> None:
    if value is not False:
        raise ConfidentialCoordinationGossipPolicyError(token, "expected false")


def _require_text(value: object, *, label: str = "text") -> str:
    if not isinstance(value, str) or not value:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "expected non-empty text",
        )
    if value != value.strip():
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "text must not contain leading or trailing whitespace",
        )
    if len(value) > _MAX_TEXT_LENGTH or any(ord(char) < 0x20 or char == "\x7f" for char in value):
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "text exceeds bounds or contains a control character",
        )
    return value


def _require_choice(label: str, value: object, *, choices: tuple[str, ...]) -> str:
    text = _require_text(value, label=label)
    if text not in choices:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "unexpected choice",
        )
    return text


def _require_text_set(value: Collection[str], *, allowed: set[str], token: str) -> frozenset[str]:
    if isinstance(value, (str, bytes, bytearray)):
        raise ConfidentialCoordinationGossipPolicyError(token, "expected a text collection")
    if not isinstance(value, Collection):
        raise ConfidentialCoordinationGossipPolicyError(token, "expected a text collection")
    if len(value) > _MAX_REF_LIST_ITEMS:
        raise ConfidentialCoordinationGossipPolicyError(token, "collection exceeds bound")
    normalized = frozenset(_require_text(item) for item in value)
    if len(normalized) != len(value) or not normalized <= allowed:
        raise ConfidentialCoordinationGossipPolicyError(token, "collection contains duplicate or unknown items")
    return normalized


def _require_prefixed_digest(label: str, value: object, *, prefixes: tuple[str, ...]) -> str:
    text = _require_text(value, label=label)
    if ":" not in text:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "expected prefixed digest",
        )
    prefix, digest = text.split(":", 1)
    if prefix not in prefixes:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "unexpected digest prefix",
        )
    if len(digest) != _HEX_DIGEST_LENGTH or any(char not in _HEX for char in digest):
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "digest is not lowercase sha256 hex",
        )
    return text


def _require_non_negative_int(label: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > _MAX_SEQUENCE
    ):
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_invalid_phase_1327",
            "expected bounded non-negative integer",
        )
    return value


def _require_epoch(label: str, value: object) -> int:
    epoch = _require_non_negative_int(f"{label}_epoch", value)
    if epoch < 1 or epoch > _MAX_EPOCH:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_epoch_invalid_phase_1327",
            "epoch must be positive and bounded",
        )
    return epoch


def _require_sequence(label: str, value: object) -> int:
    sequence = _require_non_negative_int(f"{label}_sequence", value)
    if sequence < 1 or sequence > _MAX_SEQUENCE:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_sequence_invalid_phase_1327",
            "sequence must be positive and bounded",
        )
    return sequence


def _require_bounded_positive_int(
    label: str,
    value: object,
    *,
    upper_bound: int,
    zero_token: str,
) -> int:
    integer = _require_non_negative_int(label, value)
    if integer < 1:
        raise ConfidentialCoordinationGossipPolicyError(zero_token, "value must be positive")
    if integer > upper_bound:
        raise ConfidentialCoordinationGossipPolicyError(
            f"ccss_004_{label}_exceeds_bound_phase_1327",
            "value exceeds allowed bound",
        )
    return integer


def _reject_forbidden_private_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in _FORBIDDEN_PRIVATE_KEYS:
                raise ConfidentialCoordinationGossipPolicyError(
                    "ccss_004_private_key_field_forbidden_phase_1327",
                    "private identifying field is forbidden",
                )
            _reject_forbidden_private_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_forbidden_private_keys(nested)


def _reject_forbidden_private_values(value: object) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in _FORBIDDEN_VALUE_FRAGMENTS):
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_private_value_disclosure_forbidden_phase_1327",
                "private identifying value is forbidden",
            )
    elif isinstance(value, Mapping):
        for nested in value.values():
            _reject_forbidden_private_values(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_forbidden_private_values(nested)


def _reject_unsafe_json_tree(value: object) -> None:
    seen: set[int] = set()
    node_count = 0
    payload_bytes = 0

    def add_payload_bytes(text: str) -> None:
        nonlocal payload_bytes
        payload_bytes += len(text.encode("utf-8"))
        if payload_bytes > _MAX_CANONICAL_JSON_BYTES:
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_payload_size_exceeded_phase_1327",
                "payload exceeds byte bound before serialization",
            )

    def visit(item: object, depth: int) -> None:
        nonlocal node_count
        if depth > _MAX_PAYLOAD_DEPTH:
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_payload_too_deep_phase_1327",
                "payload exceeds depth bound",
            )
        node_count += 1
        if node_count > _MAX_PAYLOAD_NODES:
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_payload_too_large_phase_1327",
                "payload exceeds node bound",
            )
        if isinstance(item, float):
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_float_values_forbidden_phase_1327",
                "float values are not allowed in canonical payloads",
            )
        if item is None or isinstance(item, bool):
            return
        if isinstance(item, int):
            if isinstance(item, bool) or abs(item) > _MAX_CANONICAL_JSON_INT_ABS:
                raise ConfidentialCoordinationGossipPolicyError(
                    "ccss_004_payload_int_invalid_phase_1327",
                    "integer exceeds canonical payload bound",
                )
            add_payload_bytes(str(item))
            return
        if isinstance(item, str):
            add_payload_bytes(_require_text(item))
            return
        if isinstance(item, tuple):
            raise ConfidentialCoordinationGossipPolicyError(
                "ccss_004_tuple_values_forbidden_phase_1327",
                "tuples are forbidden in canonical payloads",
            )
        if isinstance(item, (Mapping, list)):
            marker = id(item)
            if marker in seen:
                raise ConfidentialCoordinationGossipPolicyError(
                    "ccss_004_payload_cycle_forbidden_phase_1327",
                    "payload contains a cycle",
                )
            seen.add(marker)
            if isinstance(item, Mapping):
                for key, nested in item.items():
                    if not isinstance(key, str):
                        raise ConfidentialCoordinationGossipPolicyError(
                            "ccss_004_payload_key_invalid_phase_1327",
                            "mapping keys must be text",
                        )
                    add_payload_bytes(_require_text(key, label="payload_key"))
                    node_count += 1
                    if node_count > _MAX_PAYLOAD_NODES:
                        raise ConfidentialCoordinationGossipPolicyError(
                            "ccss_004_payload_too_large_phase_1327",
                            "payload exceeds node bound",
                        )
                    visit(nested, depth + 1)
            else:
                for nested in item:
                    visit(nested, depth + 1)
            seen.remove(marker)
            return
        raise ConfidentialCoordinationGossipPolicyError(
            "ccss_004_payload_type_invalid_phase_1327",
            "unsupported canonical payload type",
        )

    visit(value, 0)


__all__ = [
    "ANONYMITY_GUARANTEE_NOT_CLAIMED_TOKEN",
    "CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION",
    "ConfidentialCoordinationGossipPolicyError",
    "GOSSIP_ANNOUNCE_PULL_JITTER_POLICY_RECORDED_TOKEN",
    "GossipAnnouncePullPolicyRef",
    "GossipCoverPolicyDecision",
    "PHASE_1328_NEXT_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1327_TOKEN",
    "TRAFFIC_ANALYSIS_NEGATIVE_TESTS_RECORDED_TOKEN",
    "TrafficAnalysisMatrixRef",
    "build_gossip_announce_pull_policy_ref",
    "build_gossip_cover_policy_decision",
    "build_traffic_analysis_matrix_ref",
    "canonical_ccss_004_json",
    "ccss_004_gossip_jitter_cover_policy_manifest",
    "ccss_004_required_tokens",
    "derive_test_fixture_jitter_epoch",
    "validate_ccss_004_manifest",
    "validate_ccss_004_record",
]
