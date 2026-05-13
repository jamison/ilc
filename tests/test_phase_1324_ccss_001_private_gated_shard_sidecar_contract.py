from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.sidecars.confidential_coordination_shard import (
    CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
    CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
    ENCRYPTED_COORDINATION_NODE_ENVELOPE_CONTRACT_RECORDED_TOKEN,
    PHASE_1325_NEXT_TOKEN,
    PRIVATE_TO_PUBLIC_PROMOTION_EVIDENCE_SHAPE_RECORDED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1324_TOKEN,
    SHARD_HEADER_PROJECTION_CONTRACT_RECORDED_TOKEN,
    ConfidentialCoordinationShardError,
    build_disclosure_denial,
    build_encrypted_coordination_node_envelope,
    build_private_shard_ref,
    build_promotion_evidence_ref,
    build_shard_header_projection,
    ccss_001_private_gated_shard_manifest,
    ccss_001_record_ref,
    ccss_001_required_tokens,
    export_ccss_001_record_json,
    validate_ccss_001_manifest,
    validate_ccss_001_record,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/confidential_coordination_shard.py"
INIT_PATH = ROOT / "ilc_core/sidecars/__init__.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
GUARDRAIL_PATH = ROOT / "tools/check_sensitive_runtime_coding_taboos.py"
SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_ccss_001_private_gated_shard_sidecar_contract_1324_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1324_ccss_001_private_gated_shard_sidecar_contract_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
FORWARD_PLAN_PATH = (
    ROOT
    / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md"
)
CCSS_FORWARD_PLAN_PATH = (
    ROOT / "docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md"
)

REQUIRED_TOKENS = [
    CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION,
    ENCRYPTED_COORDINATION_NODE_ENVELOPE_CONTRACT_RECORDED_TOKEN,
    SHARD_HEADER_PROJECTION_CONTRACT_RECORDED_TOKEN,
    PRIVATE_TO_PUBLIC_PROMOTION_EVIDENCE_SHAPE_RECORDED_TOKEN,
    CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
    PHASE_1325_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1324_TOKEN,
]


def _ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def _records() -> dict[str, dict]:
    denial = build_disclosure_denial()
    shard = build_private_shard_ref(
        genesis_lineage_ref=_ref("genesis_lineage", "a"),
        root_commitment_ref=_ref("shard_commitment", "b"),
        gate_control_ref=_ref("gate_control", "c"),
        access_policy_ref=_ref("capability_policy", "d"),
        visibility_mode="gated",
    )
    envelope = build_encrypted_coordination_node_envelope(
        private_shard_ref=shard["private_shard_ref"],
        shard_header_ref=_ref("private_shard_header", "e"),
        capability_policy_ref=_ref("capability_policy", "f"),
        disclosure_denial_ref=denial["disclosure_denial_ref"],
        encryption_scheme_ref=_ref("encryption_scheme", "1"),
        ciphertext_digest_ref=_ref("ciphertext", "2"),
        ciphertext_storage_ref=_ref("ciphertext_storage", "3"),
        ciphertext_size_bytes=4096,
        envelope_epoch=1324,
    )
    promotion = build_promotion_evidence_ref(
        source_private_shard_ref=shard["private_shard_ref"],
        source_shard_header_ref=_ref("private_shard_header", "e"),
        original_private_node_commitment_ref=_ref("private_node_commitment", "4"),
        successor_public_node_candidate_ref=_ref("public_successor_candidate", "5"),
        disclosed_lineage_ref=_ref("disclosed_lineage", "6"),
        promotion_epoch=1324,
    )
    projection = build_shard_header_projection(
        private_shard_ref=shard["private_shard_ref"],
        shard_header_ref=_ref("private_shard_header", "e"),
        root_commitment_ref=_ref("shard_commitment", "b"),
        capability_policy_ref=_ref("capability_policy", "f"),
        disclosure_denial_ref=denial["disclosure_denial_ref"],
        header_epoch=1324,
        encrypted_coordination_refs=[envelope["envelope_ref"]],
        promotion_evidence_refs=[promotion["promotion_evidence_ref"]],
    )
    return {
        "denial": denial,
        "envelope": envelope,
        "projection": projection,
        "promotion": promotion,
        "shard": shard,
    }


def test_phase_1324_manifest_and_records_are_deterministic_local_only() -> None:
    manifest = ccss_001_private_gated_shard_manifest()

    assert ccss_001_required_tokens() == REQUIRED_TOKENS
    assert manifest["contract_version"] == CCSS_001_PRIVATE_GATED_SHARD_CONTRACT_VERSION
    assert manifest["tokens"] == REQUIRED_TOKENS
    assert manifest["local_only"] is True
    assert manifest["next_phase"] == PHASE_1325_NEXT_TOKEN
    assert manifest["public_confidential_coordination_serving_enabled"] is False
    assert manifest["public_p2p_enabled"] is False
    assert all(value is False for value in manifest["authorization_flags"].values())
    assert validate_ccss_001_manifest(manifest) == manifest

    for record in _records().values():
        exported_once = export_ccss_001_record_json(record)
        exported_twice = export_ccss_001_record_json(record)
        assert validate_ccss_001_record(record) == record
        assert ccss_001_record_ref(record).startswith("ccss_001_record:")
        assert exported_once == exported_twice
        assert exported_once == json.dumps(
            json.loads(exported_once),
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )


def test_phase_1324_encrypted_envelope_and_header_projection_are_opaque_only() -> None:
    records = _records()
    envelope = records["envelope"]
    projection = records["projection"]

    assert envelope["encryption_status"] == "encrypted_payload_digest_only"
    assert envelope["ciphertext_transport"] == "opaque_ref_only_ciphertext_digest"
    assert envelope["envelope_ref"].startswith("encrypted_coordination:")
    assert envelope["canonical_body_sha256"] in envelope["envelope_ref"]
    assert projection["projection_scope"] == "private_local_header_only"
    assert projection["phase_1311_projection_record_kind"] == "private_gated_shard_header"
    assert projection["envelope_count"] == 1
    assert projection["encrypted_coordination_refs"] == [envelope["envelope_ref"]]

    projection_text = json.dumps(projection, sort_keys=True)
    for forbidden in (
        "AgentID",
        "agent_id",
        "client_ip",
        "harness_identity",
        "membership_list",
        "plaintext",
        "raw_sealed_payload",
        "route_history",
        "sender_identity",
        "recipient_identity",
        "wallet_id",
    ):
        assert forbidden not in projection_text


def test_phase_1324_promotion_evidence_shape_does_not_promote_or_reveal() -> None:
    promotion = _records()["promotion"]

    assert promotion["promotion_evidence_ref"].startswith("promotion_evidence:")
    assert promotion["promotion_authorized"] is False
    assert promotion["promotion_executed"] is False
    assert promotion["promotion_receipt_materialized"] is False
    assert promotion["public_availability_claimed"] is False
    assert promotion["private_content_revealed"] is False
    assert promotion["automatic_public_corroboration_carry_forward"] is False
    assert promotion["automatic_public_reputation_carry_forward"] is False
    assert (
        promotion["promotion_receipt_shape"]
        == "successor_node_plus_promotion_receipt_without_automatic_reputation_carry_forward"
    )

    mutated = copy.deepcopy(promotion)
    mutated["promotion_authorized"] = True
    with pytest.raises(ConfidentialCoordinationShardError) as auth_exc:
        validate_ccss_001_record(mutated)
    assert auth_exc.value.token == "ccss_001_promotion_authority_forbidden_phase_1324"

    mutated = copy.deepcopy(promotion)
    mutated["automatic_public_reputation_carry_forward"] = True
    with pytest.raises(ConfidentialCoordinationShardError) as reputation_exc:
        validate_ccss_001_record(mutated)
    assert reputation_exc.value.token == "ccss_001_promotion_carry_forward_forbidden_phase_1324"


def test_phase_1324_negative_paths_reject_plaintext_identity_oversize_and_hash_drift() -> None:
    records = _records()
    envelope = records["envelope"]
    projection = records["projection"]

    mutated = copy.deepcopy(envelope)
    mutated["ciphertext_transport"] = "plaintext_body_inline"
    with pytest.raises(ConfidentialCoordinationShardError) as plaintext_exc:
        validate_ccss_001_record(mutated)
    assert plaintext_exc.value.token == "ccss_001_private_value_forbidden_phase_1324"

    mutated = copy.deepcopy(envelope)
    mutated["agent_id"] = "agent-id-leak"
    with pytest.raises(ConfidentialCoordinationShardError) as identity_exc:
        validate_ccss_001_record(mutated)
    assert identity_exc.value.token == "ccss_001_record_keys_invalid_phase_1324"

    with pytest.raises(ConfidentialCoordinationShardError) as size_exc:
        build_encrypted_coordination_node_envelope(
            private_shard_ref=records["shard"]["private_shard_ref"],
            shard_header_ref=_ref("private_shard_header", "e"),
            capability_policy_ref=_ref("capability_policy", "f"),
            disclosure_denial_ref=records["denial"]["disclosure_denial_ref"],
            encryption_scheme_ref=_ref("encryption_scheme", "1"),
            ciphertext_digest_ref=_ref("ciphertext", "2"),
            ciphertext_storage_ref=_ref("ciphertext_storage", "3"),
            ciphertext_size_bytes=1_048_577,
            envelope_epoch=1324,
        )
    assert size_exc.value.token == "ccss_001_ciphertext_size_invalid_phase_1324"

    mutated = copy.deepcopy(envelope)
    mutated["encryption_status"] = "missing_encryption_marker"
    with pytest.raises(ConfidentialCoordinationShardError) as marker_exc:
        validate_ccss_001_record(mutated)
    assert marker_exc.value.token == "ccss_001_encryption_status_invalid_phase_1324"

    mutated = copy.deepcopy(envelope)
    mutated["canonical_body_sha256"] = "0" * 64
    with pytest.raises(ConfidentialCoordinationShardError) as hash_exc:
        validate_ccss_001_record(mutated)
    assert hash_exc.value.token == "ccss_001_envelope_hash_mismatch_phase_1324"

    mutated = copy.deepcopy(projection)
    mutated["encrypted_coordination_refs"] = tuple(mutated["encrypted_coordination_refs"])
    with pytest.raises(ConfidentialCoordinationShardError) as tuple_exc:
        validate_ccss_001_record(mutated)
    assert tuple_exc.value.token == "ccss_001_payload_key_invalid_phase_1324"


def test_phase_1324_public_serving_and_manifest_authorization_flags_fail_closed() -> None:
    manifest = ccss_001_private_gated_shard_manifest()
    mutated_manifest = copy.deepcopy(manifest)
    mutated_manifest["authorization_flags"]["public_p2p_enabled"] = True
    with pytest.raises(ConfidentialCoordinationShardError) as manifest_exc:
        validate_ccss_001_manifest(mutated_manifest)
    assert manifest_exc.value.token == CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN

    envelope = _records()["envelope"]
    mutated = copy.deepcopy(envelope)
    mutated["public_serving_enabled"] = True
    with pytest.raises(ConfidentialCoordinationShardError) as serving_exc:
        validate_ccss_001_record(mutated)
    assert serving_exc.value.token == CCSS_PUBLIC_SERVING_NOT_ENABLED_TOKEN


def test_phase_1324_module_has_no_network_server_or_protocol_taboo_surface() -> None:
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


def test_phase_1324_docs_registry_guardrail_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MODULE_PATH,
            INIT_PATH,
            REGISTRY_PATH,
            GUARDRAIL_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            FORWARD_PLAN_PATH,
            CCSS_FORWARD_PLAN_PATH,
        )
    )
    for token in REQUIRED_TOKENS:
        assert token in corpus
    for token in (
        "PrivateShardRef",
        "EncryptedCoordinationNodeEnvelope",
        "ShardHeaderProjection",
        "PromotionEvidenceRef",
        "DisclosureDenial",
        "ccss_tail_routed_without_atlas_g_compression_phase_1317",
        "atlas_g_tail_carried_forward_not_hidden_inside_ccss_phase_1317_1329",
    ):
        assert token in corpus
    for non_claim in (
        "no public confidential coordination serving",
        "no public P2P",
        "no public promotion",
        "no source publication",
        "no release signing",
        "Phase 1325 is sensitive and requires explicit `GO Phase 1325`",
    ):
        assert non_claim in corpus
