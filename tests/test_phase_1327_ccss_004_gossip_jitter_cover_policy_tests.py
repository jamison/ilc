import json
from pathlib import Path

import pytest

from ilc_core.sidecars.confidential_coordination_gossip_policy import (
    ANONYMITY_GUARANTEE_NOT_CLAIMED_TOKEN,
    CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
    GOSSIP_ANNOUNCE_PULL_JITTER_POLICY_RECORDED_TOKEN,
    PHASE_1328_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1327_TOKEN,
    TRAFFIC_ANALYSIS_NEGATIVE_TESTS_RECORDED_TOKEN,
    ConfidentialCoordinationGossipPolicyError,
    build_gossip_announce_pull_policy_ref,
    build_gossip_cover_policy_decision,
    build_traffic_analysis_matrix_ref,
    canonical_ccss_004_json,
    ccss_004_gossip_jitter_cover_policy_manifest,
    ccss_004_required_tokens,
    derive_test_fixture_jitter_epoch,
    validate_ccss_004_record,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


_DIGEST = "a" * 64
_PRIVATE_SHARD_REF = f"private_shard:{_DIGEST}"


def _matrix():
    return build_traffic_analysis_matrix_ref(matrix_epoch=1)


def _policy():
    matrix = _matrix()
    return build_gossip_announce_pull_policy_ref(
        private_shard_ref=_PRIVATE_SHARD_REF,
        traffic_analysis_matrix_ref=matrix["matrix_ref"],
        policy_epoch=1,
    )


def test_manifest_records_phase_1327_private_local_non_claims():
    manifest = ccss_004_gossip_jitter_cover_policy_manifest()

    assert manifest["contract_version"] == CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION
    assert manifest["tokens"] == [
        CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION,
        GOSSIP_ANNOUNCE_PULL_JITTER_POLICY_RECORDED_TOKEN,
        TRAFFIC_ANALYSIS_NEGATIVE_TESTS_RECORDED_TOKEN,
        ANONYMITY_GUARANTEE_NOT_CLAIMED_TOKEN,
        PHASE_1328_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1327_TOKEN,
    ]
    assert manifest["tokens"] == ccss_004_required_tokens()
    assert manifest["local_only"] is True
    assert manifest["public_p2p_enabled"] is False
    assert manifest["public_confidential_coordination_serving_enabled"] is False
    assert manifest["anonymity_guarantee_claimed"] is False
    assert manifest["unlinkability_claimed"] is False
    assert manifest["signal_equivalent_claimed"] is False


def test_traffic_matrix_covers_required_adversary_observations():
    matrix = _matrix()
    observations = [row["adversary_observation"] for row in matrix["rows"]]

    assert observations == [
        "sender_timing_correlation_against_local_enqueue_time",
        "receiver_timing_correlation_against_local_delivery_time",
        "batch_size_leakage_across_shards",
        "cover_message_absence_during_idle_periods",
        "retry_burst_correlation_after_failed_delivery",
        "shard_header_correlation_across_announce_pull_cycles",
        "harness_identity_leakage_through_adapter_metadata",
    ]
    assert {row["test_status"] for row in matrix["rows"]} == {"tested_local_negative"}
    assert {row["non_claim"] for row in matrix["rows"]} == {
        "does_not_claim_anonymity_or_unlinkability"
    }
    assert all(row["residual_risk"] for row in matrix["rows"])


def test_policy_records_bounded_push_pull_jitter_and_cover():
    policy = _policy()

    assert policy["announce_scope"] == "private_local_opaque_availability_only"
    assert policy["push_payload_class"] == "bounded_metadata_ref_only"
    assert policy["pull_payload_class"] == "heavy_payload_receiver_controlled"
    assert policy["receiver_controlled_pull"] is True
    assert policy["min_jitter_epochs"] == 0
    assert policy["max_jitter_epochs"] == 3
    assert policy["max_announce_refs_per_batch"] == 64
    assert policy["cover_policy_mode"] == "idle_cover_required"
    assert policy["runtime_jitter_source"] == "secure_random_or_ratified_vrf_required"
    assert policy["test_fixture_jitter_derivation"] == (
        "sha256_domain_separated_epoch_ref_fixture_only"
    )
    assert policy["no_anonymity_guarantee"] is True

    release_epoch = derive_test_fixture_jitter_epoch(
        policy_record=policy,
        object_ref=_PRIVATE_SHARD_REF,
        base_epoch=9,
    )
    assert 9 <= release_epoch <= 12


def test_cover_policy_decisions_are_fail_closed_for_negative_conditions():
    policy = _policy()

    active = build_gossip_cover_policy_decision(policy_record=policy, decision_epoch=2)
    assert active["decision_state"] == "announce_pending_local"
    assert active["private_local_action_allowed"] is True

    pull = build_gossip_cover_policy_decision(
        policy_record=policy,
        decision_epoch=2,
        pull_available=True,
    )
    assert pull["decision_state"] == "pull_available_local"

    public = build_gossip_cover_policy_decision(
        policy_record=policy,
        decision_epoch=2,
        public_network_attempted=True,
    )
    assert public["decision_state"] == "rejected_public_network"
    assert public["private_local_action_allowed"] is False
    assert public["public_network_attempt_blocked"] is True

    deterministic = build_gossip_cover_policy_decision(
        policy_record=policy,
        decision_epoch=2,
        deterministic_runtime_jitter_seed_attempted=True,
    )
    assert deterministic["decision_state"] == "rejected_deterministic_runtime_jitter_seed"

    metadata = build_gossip_cover_policy_decision(
        policy_record=policy,
        decision_epoch=2,
        participant_metadata_field_count=1,
    )
    assert metadata["decision_state"] == "rejected_participant_metadata"

    cover_disabled = build_gossip_cover_policy_decision(
        policy_record=policy,
        decision_epoch=2,
        cover_messages_in_idle_epoch=0,
    )
    assert cover_disabled["decision_state"] == "rejected_cover_disabled"

    unbounded = build_gossip_cover_policy_decision(
        policy_record=policy,
        decision_epoch=2,
        announce_ref_count=policy["max_announce_refs_per_batch"] + 1,
    )
    assert unbounded["decision_state"] == "rejected_unbounded_batch"


@pytest.mark.parametrize(
    ("kwargs", "token"),
    [
        ({"max_jitter_epochs": 0}, "ccss_004_zero_jitter_forbidden_phase_1327"),
        ({"cover_policy_enabled": False}, "ccss_004_cover_policy_disabled_phase_1327"),
        ({"unbounded_batch_enabled": True}, "ccss_004_unbounded_batch_forbidden_phase_1327"),
        ({"public_network_enabled": True}, "ccss_004_public_network_forbidden_phase_1327"),
        (
            {"deterministic_runtime_jitter_seed_enabled": True},
            "ccss_004_runtime_jitter_seed_forbidden_phase_1327",
        ),
    ],
)
def test_policy_builder_rejects_forbidden_authority_modes(kwargs, token):
    matrix = _matrix()
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as excinfo:
        build_gossip_announce_pull_policy_ref(
            private_shard_ref=_PRIVATE_SHARD_REF,
            traffic_analysis_matrix_ref=matrix["matrix_ref"],
            policy_epoch=1,
            **kwargs,
        )
    assert excinfo.value.token == token


def test_record_validation_rejects_public_flags_and_participant_metadata_fields():
    policy = _policy()

    polluted = dict(policy)
    polluted["authorization_flags"] = dict(policy["authorization_flags"])
    polluted["authorization_flags"]["public_p2p_enabled"] = True
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as excinfo:
        validate_ccss_004_record(polluted)
    assert excinfo.value.token == "ccss_004_public_or_metadata_authority_forbidden_phase_1327"

    with_private_key = dict(policy)
    with_private_key["harness_identity"] = "example"
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as private_excinfo:
        validate_ccss_004_record(with_private_key)
    assert private_excinfo.value.token == "ccss_004_private_key_field_forbidden_phase_1327"

    with_private_value = dict(policy)
    with_private_value["announce_scope"] = "agent_id=abc"
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as value_excinfo:
        validate_ccss_004_record(with_private_value)
    assert value_excinfo.value.token == "ccss_004_private_value_disclosure_forbidden_phase_1327"


def test_canonical_json_rejects_unsafe_payloads_before_serialization(monkeypatch):
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as float_excinfo:
        canonical_ccss_004_json({"x": 1.25})
    assert float_excinfo.value.token == "ccss_004_float_values_forbidden_phase_1327"

    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as tuple_excinfo:
        canonical_ccss_004_json({"x": ("not", "json")})
    assert tuple_excinfo.value.token == "ccss_004_tuple_values_forbidden_phase_1327"

    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as text_excinfo:
        canonical_ccss_004_json({"x": "bad\x7f"})
    assert text_excinfo.value.token == "ccss_004_text_invalid_phase_1327"

    cycle = {}
    cycle["self"] = cycle
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as cycle_excinfo:
        canonical_ccss_004_json(cycle)
    assert cycle_excinfo.value.token == "ccss_004_payload_cycle_forbidden_phase_1327"

    oversized = {f"k{i}": "a" * 4096 for i in range(2600)}

    def fail_json_dumps(*_args, **_kwargs):
        raise AssertionError("json.dumps should not run after pre-serialization budget failure")

    monkeypatch.setattr(json, "dumps", fail_json_dumps)
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as size_excinfo:
        canonical_ccss_004_json(oversized)
    assert size_excinfo.value.token == "ccss_004_payload_size_exceeded_phase_1327"


def test_invalid_epoch_sequence_depth_and_node_bounds_are_rejected():
    matrix = _matrix()
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as epoch_excinfo:
        build_gossip_announce_pull_policy_ref(
            private_shard_ref=_PRIVATE_SHARD_REF,
            traffic_analysis_matrix_ref=matrix["matrix_ref"],
            policy_epoch=0,
        )
    assert epoch_excinfo.value.token == "ccss_004_policy_epoch_invalid_phase_1327"

    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as sequence_excinfo:
        build_gossip_announce_pull_policy_ref(
            private_shard_ref=_PRIVATE_SHARD_REF,
            traffic_analysis_matrix_ref=matrix["matrix_ref"],
            policy_epoch=1,
            policy_sequence=0,
        )
    assert sequence_excinfo.value.token == "ccss_004_policy_sequence_invalid_phase_1327"

    deep = {}
    cursor = deep
    for index in range(34):
        cursor["x"] = {}
        cursor = cursor["x"]
    with pytest.raises(ConfidentialCoordinationGossipPolicyError) as depth_excinfo:
        canonical_ccss_004_json(deep)
    assert depth_excinfo.value.token == "ccss_004_payload_too_deep_phase_1327"


def test_registry_integrates_ccss_004_without_public_authority():
    registry = build_sidecar_registry_manifest()
    sidecars = {sidecar["sidecar_id"]: sidecar for sidecar in registry["sidecars"]}
    profile = next(
        item
        for item in registry["profiles"]
        if item["profile_id"] == "confidential_coordination_local_preview"
    )
    integrity = registry["package_profile_integrity"]["confidential_coordination_gossip_policy_manifest"]

    assert "confidential_coordination_gossip_jitter_cover_policy" in sidecars
    assert "confidential_coordination_gossip_jitter_cover_policy" in profile["required_sidecars"]
    assert integrity["contract_version"] == CCSS_004_GOSSIP_JITTER_COVER_POLICY_TESTS_VERSION
    assert integrity["public_p2p_enabled"] is False
    assert integrity["public_confidential_coordination_serving_enabled"] is False
    assert integrity["anonymity_guarantee_claimed"] is False


def test_ccss_004_module_does_not_import_predictable_prng_or_network_runtime():
    source = Path("ilc_core/sidecars/confidential_coordination_gossip_policy.py").read_text()

    assert "import random" not in source
    assert "from random" not in source
    assert "requests" not in source
    assert "socket" not in source
