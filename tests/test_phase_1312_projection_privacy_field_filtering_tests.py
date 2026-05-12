from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.sidecars.local_graph_memory_projection import (
    CONFIDENTIAL_COORDINATION_PROJECTION_NON_LEAKAGE_TESTS_TOKEN,
    PHASE_1313_NEXT_TOKEN,
    PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION,
    PROJECTION_PRIVACY_FILTERS_HARDENED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1312_TOKEN,
    PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_PHASE_1312_TOKEN,
    LocalGraphMemoryProjectionError,
    build_aggregate_summary_record_from_query_result,
    build_encrypted_coordination_reference_record,
    build_private_gated_shard_header_record,
    build_public_safe_projection_envelope,
    canonical_local_graph_memory_projection_json,
    export_public_safe_projection_envelope_json,
    local_graph_memory_projection_sidecar_manifest,
    projection_privacy_field_filtering_required_tokens,
    projection_privacy_forbidden_fragments,
    validate_projection_privacy_filtering_payload,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/local_graph_memory_projection.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
SPEC_PATH = ROOT / "docs/specs/ilc_projection_privacy_field_filtering_tests_1312_v0.1.md"
WALKTHROUGH_PATH = (
    ROOT / "docs/phases/phase_1312_projection_privacy_field_filtering_tests_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
ARCHITECTURE_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"
CCSS_PATH = ROOT / "docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md"

H1 = "a" * 64
H2 = "b" * 64
H3 = "c" * 64

REQUIRED_TOKENS = [
    PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION,
    PROJECTION_PRIVACY_FILTERS_HARDENED_TOKEN,
    CONFIDENTIAL_COORDINATION_PROJECTION_NON_LEAKAGE_TESTS_TOKEN,
    PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_PHASE_1312_TOKEN,
    PHASE_1313_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1312_TOKEN,
]


def _ref(prefix: str, digest: str = H1) -> str:
    return f"{prefix}:{digest}"


def _projection_envelope() -> dict:
    aggregate = build_aggregate_summary_record_from_query_result(
        {
            "edge_count": 2,
            "edges": [
                {
                    "canonical_id": "edge:private-edge-a",
                    "source": "private-node-a",
                    "target": "private-node-b",
                }
            ],
            "hyperedge_count": 1,
            "node_count": 3,
            "nodes": [
                {"canonical_id": "node:private-node-a", "label": "AgentID:agent-a"},
                {"canonical_id": "node:private-node-b", "label": "requester_id:requester-a"},
            ],
        },
        artifact_refs=[_ref("artifact", H2)],
        record_id=_ref("record", H1),
    )
    shard = build_private_gated_shard_header_record(
        capability_policy_ref=_ref("capability_policy", H1),
        encrypted_coordination_refs=[_ref("encrypted_coordination", H2)],
        record_id=_ref("record", H2),
        shard_commitment_ref=_ref("shard_commitment", H1),
        shard_epoch=31,
        shard_header_ref=_ref("private_shard_header", H1),
    )
    coordination = build_encrypted_coordination_reference_record(
        capability_ref=_ref("capability", H1),
        ciphertext_digest_ref=_ref("ciphertext", H1),
        coordination_epoch=31,
        encrypted_coordination_ref=_ref("encrypted_coordination", H2),
        record_id=_ref("record", H3),
    )
    return build_public_safe_projection_envelope(
        projection_epoch=31,
        projection_kind="confidential_coordination_projection",
        projection_profile="confidential_coordination_local_preview",
        records=[aggregate, shard, coordination],
        source_artifact_root_ref=_ref("root", H1),
    )


def test_phase_1312_manifest_and_registry_record_privacy_hardening() -> None:
    manifest = local_graph_memory_projection_sidecar_manifest()
    registry = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in registry["sidecars"]}
    projection = sidecars["local_graph_memory_projection"]

    assert projection_privacy_field_filtering_required_tokens() == REQUIRED_TOKENS
    assert manifest["projection_privacy_field_filtering_tests_version"] == (
        PROJECTION_PRIVACY_FIELD_FILTERING_TESTS_VERSION
    )
    assert manifest["phase_1312_tokens"] == sorted(REQUIRED_TOKENS)
    assert manifest["projection_privacy_filtering_hardened"] is True
    assert manifest["confidential_coordination_projection_non_leakage_tests"] is True
    assert manifest["bounded_projection_serving_blocker_tests_hardened"] is True
    assert manifest["public_sidecar_projection_serving_enabled"] is False
    assert projection["authority_gate"] == (
        "phase_1311_1312_local_projection_substrate_privacy_hardened_public_serving_blocked"
    )
    assert projection["implementation_status"] == (
        "local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312"
    )
    for token in REQUIRED_TOKENS[1:4]:
        assert token in projection["required_capabilities"]
    integrity_projection = registry["package_profile_integrity"][
        "local_graph_memory_projection_sidecar_manifest"
    ]
    assert integrity_projection["phase_1312_tokens"] == sorted(REQUIRED_TOKENS)


@pytest.mark.parametrize(
    "payload",
    (
        {"safe": "AgentID:agent-a"},
        {"safe": "agent_id:agent-a"},
        {"safe": "requester_id:req-a"},
        {"safe": "client_ip:203.0.113.4"},
        {"safe": "node:private-node-a"},
        {"safe": "edge:private-edge-a"},
        {"safe": "private-node-a"},
        {"safe": "group_membership:alpha"},
        {"safe": "route_history:relay-a"},
        {"safe": "sealed_payload:cid"},
        {"safe": "plaintext_payload:secret"},
        {"safe": "wallet_address:abc"},
        {"safe": "stake_balance:10"},
        {"safe": "economic_position:long"},
        {"route_history_ref": _ref("artifact", H1)},
    ),
)
def test_phase_1312_export_guard_rejects_forbidden_fragments(payload: dict) -> None:
    with pytest.raises(LocalGraphMemoryProjectionError) as exc:
        validate_projection_privacy_filtering_payload(payload)

    assert exc.value.token == "local_graph_memory_projection_private_fragment_forbidden_phase_1312"


def test_phase_1312_query_summary_redacts_raw_identifiers_before_export() -> None:
    envelope = _projection_envelope()
    exported = export_public_safe_projection_envelope_json(envelope)
    parsed = json.loads(exported)

    assert parsed["query_result_count"] == 3
    assert parsed["records"][0]["counts"] == {
        "edge_count": 2,
        "hyperedge_count": 1,
        "node_count": 3,
        "query_result_count": 1,
    }
    for forbidden in projection_privacy_forbidden_fragments():
        assert forbidden not in exported.lower()
    assert canonical_local_graph_memory_projection_json(parsed) == exported


def test_phase_1312_confidential_coordination_projection_is_opaque_refs_only() -> None:
    exported = export_public_safe_projection_envelope_json(_projection_envelope())

    for allowed in (
        "private_gated_shard_header",
        _ref("private_shard_header", H1),
        _ref("shard_commitment", H1),
        _ref("capability_policy", H1),
        "encrypted_coordination_reference",
        _ref("encrypted_coordination", H2),
        _ref("ciphertext", H1),
        _ref("capability", H1),
    ):
        assert allowed in exported
    for forbidden in (
        "AgentID",
        "agent_id",
        "requester_id",
        "client_ip",
        "membership",
        "route_history",
        "sealed_payload",
        "plaintext",
        "wallet",
        "stake_balance",
        "economic_position",
        "graph_position",
    ):
        assert forbidden.lower() not in exported.lower()


def test_phase_1312_public_serving_flags_remain_fail_closed() -> None:
    envelope = _projection_envelope()
    parsed = json.loads(export_public_safe_projection_envelope_json(envelope))

    assert all(value is False for value in parsed["authorization_flags"].values())
    assert parsed["local_only"] is True
    assert parsed["projection_profile"] == "confidential_coordination_local_preview"

    drift = copy.deepcopy(envelope)
    drift["authorization_flags"]["public_sidecar_projection_serving_enabled"] = True
    with pytest.raises(LocalGraphMemoryProjectionError):
        export_public_safe_projection_envelope_json(drift)

    drift = copy.deepcopy(envelope)
    drift["records"].append(drift["records"][0])
    with pytest.raises(LocalGraphMemoryProjectionError) as exc:
        build_public_safe_projection_envelope(
            max_records=1,
            projection_epoch=31,
            records=drift["records"],
            source_artifact_root_ref=_ref("root", H1),
        )
    assert exc.value.token == "local_graph_memory_projection_record_count_exceeded_phase_1311"


def test_phase_1312_deny_by_default_rejects_unknown_and_private_fields() -> None:
    record = build_private_gated_shard_header_record(
        capability_policy_ref=_ref("capability_policy", H1),
        encrypted_coordination_refs=[],
        record_id=_ref("record", H1),
        shard_commitment_ref=_ref("shard_commitment", H1),
        shard_epoch=31,
        shard_header_ref=_ref("private_shard_header", H1),
    )
    with_unknown = dict(record)
    with_unknown["display_name"] = "safe-looking name"

    with pytest.raises(LocalGraphMemoryProjectionError) as exc:
        build_public_safe_projection_envelope(
            projection_epoch=31,
            records=[with_unknown],
            source_artifact_root_ref=_ref("root", H1),
        )
    assert exc.value.token == "local_graph_memory_projection_record_keys_invalid_phase_1311"

    with_private = dict(record)
    with_private["membership"] = ["agent-a"]
    with pytest.raises(LocalGraphMemoryProjectionError) as private_exc:
        build_public_safe_projection_envelope(
            projection_epoch=31,
            records=[with_private],
            source_artifact_root_ref=_ref("root", H1),
        )
    assert private_exc.value.token == (
        "local_graph_memory_projection_private_field_forbidden_phase_1311"
    )


def test_phase_1312_source_has_no_public_server_network_or_assert_surface() -> None:
    for path in (MODULE_PATH, REGISTRY_PATH):
        tree = ast.parse(path.read_text(encoding="utf-8"))
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


def test_phase_1312_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MODULE_PATH,
            REGISTRY_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            ARCHITECTURE_PATH,
            CCSS_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for phrase in (
        "no public sidecar/projection serving",
        "no non-loopback bind",
        "no public listener",
        "no peer discovery",
        "no public confidential messaging",
        "no public confidential coordination serving",
        "no wallet withdrawal",
        "no ECU minting",
        "no ILC settlement",
        "Phase 1313 is sensitive and requires explicit `GO Phase 1313`",
    ):
        assert phrase in corpus
