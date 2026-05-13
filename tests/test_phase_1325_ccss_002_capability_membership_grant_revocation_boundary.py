from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

import ilc_core.sidecars.confidential_coordination_capability as ccss
from ilc_core.sidecars.confidential_coordination_capability import (
    CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
    MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN,
    OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
    PHASE_1326_NEXT_TOKEN,
    PRIVATE_SHARD_ACCESS_CONTROL_BOUNDARY_RECORDED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1325_TOKEN,
    ConfidentialCoordinationCapabilityError,
    build_capability_grant_ref,
    build_capability_policy_ref,
    build_capability_revocation_ref,
    build_local_access_decision,
    build_membership_boundary_ref,
    build_zk_membership_interface_ref,
    canonical_ccss_002_json,
    ccss_002_capability_membership_boundary_manifest,
    ccss_002_record_ref,
    ccss_002_required_tokens,
    export_ccss_002_record_json,
    validate_ccss_002_manifest,
    validate_ccss_002_record,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/confidential_coordination_capability.py"
INIT_PATH = ROOT / "ilc_core/sidecars/__init__.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
GUARDRAIL_PATH = ROOT / "tools/check_sensitive_runtime_coding_taboos.py"
SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_ccss_002_capability_membership_grant_revocation_boundary_1325_v0.1.md"
)
FIX1_SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_phase_1325_fix1_ccss_002_access_audit_hardening_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1325_ccss_002_capability_membership_grant_revocation_boundary_walkthrough.md"
)
FIX1_WALKTHROUGH_PATH = (
    ROOT / "docs/phases/phase_1325_fix1_ccss_002_access_audit_hardening_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CCSS_FORWARD_PLAN_PATH = (
    ROOT / "docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md"
)

REQUIRED_TOKENS = [
    CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION,
    PRIVATE_SHARD_ACCESS_CONTROL_BOUNDARY_RECORDED_TOKEN,
    MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN,
    OPTIONAL_ZK_INTERFACE_BOUNDARY_RECORDED_TOKEN,
    PHASE_1326_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1325_TOKEN,
]
FIX1_TOKENS = [
    "phase_1325_fix1_ccss_002_access_audit_hardening.v0.1",
    "ccss_002_zk_record_kind_validated_phase_1325_fix1",
    "ccss_002_revocation_precedes_zk_deferred_phase_1325_fix1",
    "ccss_002_pre_serialization_payload_byte_budget_phase_1325_fix1",
    "sidecar_del_control_character_rejected_cross_module_phase_1325_fix1",
    "public_rc_remains_blocked_after_phase_1325_fix1",
    "phase_1326_ccss_sealed_sender_boundary_next_after_fix1",
]


def _ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def _records() -> dict[str, dict]:
    membership = build_membership_boundary_ref(
        private_shard_ref=_ref("private_shard", "a"),
        membership_root_ref=_ref("membership_root", "b"),
        membership_proof_ref=_ref("membership_proof", "c"),
        boundary_epoch=1325,
    )
    policy = build_capability_policy_ref(
        private_shard_ref=_ref("private_shard", "a"),
        membership_boundary_ref=membership["membership_boundary_ref"],
        policy_epoch=1325,
    )
    grant = build_capability_grant_ref(
        private_shard_ref=_ref("private_shard", "a"),
        shard_header_ref=_ref("private_shard_header", "d"),
        capability_policy_ref=policy["capability_policy_ref"],
        membership_boundary_ref=membership["membership_boundary_ref"],
        membership_proof_ref=_ref("membership_proof", "c"),
        capability_ref=_ref("capability", "e"),
        grant_scope="read_ciphertext_ref",
        grant_epoch=1325,
        grant_sequence=1,
        valid_from_epoch=1325,
        valid_to_epoch=1330,
    )
    revocation = build_capability_revocation_ref(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        grant_ref=grant["grant_ref"],
        revocation_epoch=1326,
        revocation_sequence=1,
    )
    zk = build_zk_membership_interface_ref(
        private_shard_ref=_ref("private_shard", "a"),
        membership_boundary_ref=membership["membership_boundary_ref"],
        proof_system_ref=_ref("zk_proof_system", "f"),
        zk_proof_ref=_ref("zk_membership_proof", "1"),
    )
    return {
        "grant": grant,
        "membership": membership,
        "policy": policy,
        "revocation": revocation,
        "zk": zk,
    }


def test_phase_1325_manifest_records_private_local_boundary_and_no_public_authority() -> None:
    manifest = ccss_002_capability_membership_boundary_manifest()

    assert ccss_002_required_tokens() == REQUIRED_TOKENS
    assert manifest["contract_version"] == CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION
    assert manifest["tokens"] == REQUIRED_TOKENS
    assert manifest["local_only"] is True
    assert manifest["next_phase"] == PHASE_1326_NEXT_TOKEN
    assert manifest["access_states"] == [
        "unknown",
        "candidate_granted",
        "active_local",
        "revoked",
        "expired_or_superseded",
        "zk_deferred",
    ]
    assert manifest["membership_plaintext_disclosure_forbidden"] is True
    assert manifest["optional_zk_interface_boundary_recorded"] is True
    assert manifest["public_confidential_coordination_serving_enabled"] is False
    assert manifest["public_membership_directory_enabled"] is False
    assert manifest["public_p2p_enabled"] is False
    assert manifest["public_zk_verifier_enabled"] is False
    assert all(value is False for value in manifest["authorization_flags"].values())
    assert validate_ccss_002_manifest(manifest) == manifest

    mutated = copy.deepcopy(manifest)
    mutated["authorization_flags"]["public_membership_directory_enabled"] = True
    with pytest.raises(ConfidentialCoordinationCapabilityError) as exc:
        validate_ccss_002_manifest(mutated)
    assert exc.value.token == MEMBERSHIP_PLAINTEXT_DISCLOSURE_FORBIDDEN_TOKEN


def test_phase_1325_records_are_deterministic_refs_and_opaque_only() -> None:
    records = _records()

    for record in records.values():
        assert validate_ccss_002_record(record) == record
        assert ccss_002_record_ref(record).startswith("ccss_002_record:")
        exported_once = export_ccss_002_record_json(record)
        exported_twice = export_ccss_002_record_json(record)
        assert exported_once == exported_twice
        assert exported_once == json.dumps(
            json.loads(exported_once),
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    corpus = json.dumps(records, sort_keys=True)
    for forbidden in (
        "AgentID",
        "client_ip",
        "grantee_agent",
        "grantor_agent",
        "member_agent_ids",
        "participant_id",
        "route_history",
        "wallet_id",
        "zk_witness",
    ):
        assert forbidden not in corpus


def test_phase_1325_access_state_machine_fails_closed_for_required_negative_paths() -> None:
    records = _records()
    grant = records["grant"]
    membership = records["membership"]
    revocation = records["revocation"]

    active = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=grant,
        membership_boundary_record=membership,
    )
    assert active["access_state"] == "active_local"
    assert active["local_access_allowed"] is True

    unknown = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=None,
    )
    assert unknown["access_state"] == "unknown"
    assert unknown["local_access_allowed"] is False

    candidate = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=grant,
        membership_boundary_record=None,
    )
    assert candidate["access_state"] == "candidate_granted"
    assert candidate["deny_reason"] == "membership_boundary_unresolved"

    revoked = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1326,
        grant_record=grant,
        membership_boundary_record=membership,
        revocation_record=revocation,
    )
    assert revoked["access_state"] == "revoked"
    assert revoked["deny_reason"] == "revocation_wins_over_grant"

    revoked_with_zk = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1326,
        grant_record=grant,
        membership_boundary_record=membership,
        revocation_record=revocation,
        zk_interface_record=records["zk"],
    )
    assert revoked_with_zk["access_state"] == "revoked"
    assert revoked_with_zk["deny_reason"] == "revocation_wins_over_grant"

    expired = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1331,
        grant_record=grant,
        membership_boundary_record=membership,
    )
    assert expired["access_state"] == "expired_or_superseded"

    replay = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=grant,
        membership_boundary_record=membership,
        replayed_grant_refs=[grant["grant_ref"]],
    )
    assert replay["access_state"] == "candidate_granted"
    assert replay["deny_reason"] == "replayed_capability_grant"

    cross_shard = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "9"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=grant,
        membership_boundary_record=membership,
    )
    assert cross_shard["access_state"] == "candidate_granted"
    assert cross_shard["deny_reason"] == "cross_shard_capability"


def test_phase_1325_rejects_plaintext_membership_malformed_refs_public_dependencies_and_epoch_zero() -> None:
    records = _records()
    grant = records["grant"]
    membership = records["membership"]
    zk = records["zk"]

    mutated = copy.deepcopy(membership)
    mutated["membership_list"] = ["agent-a"]
    with pytest.raises(ConfidentialCoordinationCapabilityError) as leak_exc:
        validate_ccss_002_record(mutated)
    assert leak_exc.value.token == "ccss_002_record_keys_invalid_phase_1325"

    mutated = copy.deepcopy(grant)
    mutated["grant_scope"] = "raw_grant_material"
    with pytest.raises(ConfidentialCoordinationCapabilityError) as scope_exc:
        validate_ccss_002_record(mutated)
    assert scope_exc.value.token == "ccss_002_private_value_forbidden_phase_1325"

    mutated = copy.deepcopy(grant)
    mutated["grant_scope"] = "unexpected_privilege_escalation"
    with pytest.raises(ConfidentialCoordinationCapabilityError) as escalation_exc:
        validate_ccss_002_record(mutated)
    assert escalation_exc.value.token == "ccss_002_grant_scope_invalid_phase_1325"

    mutated = copy.deepcopy(grant)
    mutated["membership_proof_ref"] = "badref"
    malformed = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=mutated,
        membership_boundary_record=membership,
    )
    assert malformed["access_state"] == "unknown"
    assert malformed["deny_reason"] == "malformed_grant"

    with pytest.raises(ConfidentialCoordinationCapabilityError) as public_exc:
        build_local_access_decision(
            private_shard_ref=_ref("private_shard", "a"),
            capability_ref=_ref("capability", "e"),
            current_epoch=1325,
            grant_record=grant,
            membership_boundary_record=membership,
            public_membership_directory_enabled=True,
        )
    assert public_exc.value.token == "ccss_002_public_membership_directory_dependency_forbidden_phase_1325"

    with pytest.raises(ConfidentialCoordinationCapabilityError) as epoch_exc:
        build_capability_grant_ref(
            private_shard_ref=_ref("private_shard", "a"),
            shard_header_ref=_ref("private_shard_header", "d"),
            capability_policy_ref=records["policy"]["capability_policy_ref"],
            membership_boundary_ref=membership["membership_boundary_ref"],
            membership_proof_ref=_ref("membership_proof", "c"),
            capability_ref=_ref("capability", "e"),
            grant_scope="read_ciphertext_ref",
            grant_epoch=0,
            grant_sequence=1,
            valid_from_epoch=1325,
            valid_to_epoch=1330,
        )
    assert epoch_exc.value.token == "ccss_002_grant_epoch_invalid_phase_1325"

    zk_decision = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=grant,
        membership_boundary_record=membership,
        zk_interface_record=zk,
    )
    assert zk_decision["access_state"] == "zk_deferred"
    assert zk_decision["local_access_allowed"] is False
    assert zk_decision["deny_reason"] == "zk_verifier_not_ratified"

    wrong_zk_kind = build_local_access_decision(
        private_shard_ref=_ref("private_shard", "a"),
        capability_ref=_ref("capability", "e"),
        current_epoch=1325,
        grant_record=grant,
        membership_boundary_record=membership,
        zk_interface_record=grant,
    )
    assert wrong_zk_kind["access_state"] == "zk_deferred"
    assert wrong_zk_kind["local_access_allowed"] is False
    assert wrong_zk_kind["deny_reason"] == "malformed_zk_interface"


def test_phase_1325_bounds_payloads_and_rejects_control_chars_floats_tuples_and_cycles() -> None:
    with pytest.raises(ConfidentialCoordinationCapabilityError) as control_exc:
        canonical_ccss_002_json({"payload": "tab\tforbidden"})
    assert control_exc.value.token == "ccss_002_payload_text_text_invalid_phase_1325"

    with pytest.raises(ConfidentialCoordinationCapabilityError) as del_exc:
        canonical_ccss_002_json({"payload": "del\x7fforbidden"})
    assert del_exc.value.token == "ccss_002_payload_text_text_invalid_phase_1325"

    with pytest.raises(ConfidentialCoordinationCapabilityError) as float_exc:
        canonical_ccss_002_json({"payload": 3.14})
    assert float_exc.value.token == "ccss_002_float_values_forbidden_phase_1325"

    with pytest.raises(ConfidentialCoordinationCapabilityError) as tuple_exc:
        canonical_ccss_002_json({"payload": ("not", "json")})
    assert tuple_exc.value.token == "ccss_002_payload_key_invalid_phase_1325"

    cyclic: dict[str, object] = {}
    cyclic["self"] = cyclic
    with pytest.raises(ConfidentialCoordinationCapabilityError) as cycle_exc:
        canonical_ccss_002_json(cyclic)
    assert cycle_exc.value.token == "ccss_002_payload_cycle_forbidden_phase_1325"

    try:
        ccss._MAX_CANONICAL_JSON_BYTES = 10
        with pytest.raises(ConfidentialCoordinationCapabilityError) as size_exc:
            canonical_ccss_002_json({"alpha": "beta"})
        assert size_exc.value.token == "ccss_002_payload_size_exceeded_phase_1325"
    finally:
        ccss._MAX_CANONICAL_JSON_BYTES = 10_000_000


def test_phase_1325_rejects_oversized_payload_before_json_serialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ccss, "_MAX_CANONICAL_JSON_BYTES", 8)

    def fail_json_dumps(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("json.dumps should not run after traversal byte cap fails")

    monkeypatch.setattr(ccss.json, "dumps", fail_json_dumps)
    with pytest.raises(ConfidentialCoordinationCapabilityError) as size_exc:
        canonical_ccss_002_json({"alpha": "beta"})

    assert size_exc.value.token == "ccss_002_payload_size_exceeded_phase_1325"


def test_phase_1325_registry_guardrail_docs_and_frontier_record_boundary() -> None:
    manifest = build_sidecar_registry_manifest()
    sidecar_ids = {sidecar["sidecar_id"] for sidecar in manifest["sidecars"]}
    assert "confidential_coordination_capability_membership_boundary" in sidecar_ids
    profile = next(
        item
        for item in manifest["profiles"]
        if item["profile_id"] == "confidential_coordination_local_preview"
    )
    assert "confidential_coordination_capability_membership_boundary" in profile["required_sidecars"]
    assert (
        manifest["package_profile_integrity"]["confidential_coordination_capability_manifest"][
            "contract_version"
        ]
        == CCSS_002_CAPABILITY_MEMBERSHIP_BOUNDARY_VERSION
    )

    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MODULE_PATH,
            INIT_PATH,
            REGISTRY_PATH,
            GUARDRAIL_PATH,
            SPEC_PATH,
            FIX1_SPEC_PATH,
            WALKTHROUGH_PATH,
            FIX1_WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            CCSS_FORWARD_PLAN_PATH,
        )
    )
    for token in REQUIRED_TOKENS:
        assert token in corpus
    for token in FIX1_TOKENS:
        assert token in corpus
    for phrase in (
        "unknown",
        "candidate_granted",
        "active_local",
        "revoked",
        "expired_or_superseded",
        "zk_deferred",
        "no public confidential coordination serving",
        "no public P2P",
        "no public membership directory",
        "no public credential authority",
        "Phase 1326 is sensitive and requires explicit `GO Phase 1326`",
        "graph_delta=support_only:",
    ):
        assert phrase in corpus


def test_phase_1325_module_has_no_network_server_or_protocol_taboo_surface() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_roots = {
        "aiohttp",
        "datetime",
        "fastapi",
        "http",
        "random",
        "requests",
        "socket",
        "time",
        "urllib",
        "uvicorn",
    }
    for node in ast.walk(tree):
        assert not isinstance(node, ast.Assert)
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_roots
