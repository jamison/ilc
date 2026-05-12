from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.sidecars.local_graph_memory_projection import (
    CONFIDENTIAL_COORDINATION_PROJECTION_REFERENCE_LOCAL_ONLY_TOKEN,
    LOCAL_GRAPH_MEMORY_PROJECTION_REF_PREFIX,
    LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION,
    PHASE_1312_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1311_TOKEN,
    PUBLIC_SAFE_PROJECTION_IMPLEMENTATION_LOCAL_ONLY_TOKEN,
    PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN,
    LocalGraphMemoryProjectionError,
    build_aggregate_summary_record_from_query_result,
    build_encrypted_coordination_reference_record,
    build_private_gated_shard_header_record,
    build_public_safe_projection_envelope,
    canonical_local_graph_memory_projection_json,
    export_public_safe_projection_envelope_json,
    local_graph_memory_projection_ref,
    local_graph_memory_projection_required_tokens,
    local_graph_memory_projection_sidecar_manifest,
    validate_public_safe_projection_envelope,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/local_graph_memory_projection.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
SPEC_PATH = ROOT / "docs/specs/ilc_local_graph_memory_projection_sidecar_1311_v0.1.md"
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1311_local_graph_memory_projection_sidecar_public_safe_projection_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
ARCHITECTURE_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"

H1 = "a" * 64
H2 = "b" * 64
H3 = "c" * 64

REQUIRED_TOKENS = [
    LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION,
    PUBLIC_SAFE_PROJECTION_IMPLEMENTATION_LOCAL_ONLY_TOKEN,
    CONFIDENTIAL_COORDINATION_PROJECTION_REFERENCE_LOCAL_ONLY_TOKEN,
    PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN,
    PHASE_1312_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1311_TOKEN,
]


def _ref(prefix: str, digest: str = H1) -> str:
    return f"{prefix}:{digest}"


def _projection_envelope() -> dict:
    aggregate = build_aggregate_summary_record_from_query_result(
        {
            "edge_count": 2,
            "hyperedge_count": 1,
            "node_count": 3,
            "nodes": [
                {"canonical_id": "private-node-a"},
                {"canonical_id": "private-node-b"},
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


def test_phase_1311_manifest_is_local_only_and_deterministic() -> None:
    manifest = local_graph_memory_projection_sidecar_manifest()

    assert manifest["contract_version"] == LOCAL_GRAPH_MEMORY_PROJECTION_SIDECAR_VERSION
    assert manifest["tokens"] == sorted(REQUIRED_TOKENS)
    assert local_graph_memory_projection_required_tokens() == REQUIRED_TOKENS
    assert manifest["local_only"] is True
    assert manifest["public_safe_projection_local_only"] is True
    assert manifest["private_gated_shard_header_projection_supported"] is True
    assert manifest["public_sidecar_projection_serving_enabled"] is False
    assert manifest["public_confidential_messaging_claimed"] is False
    assert manifest["public_confidential_coordination_serving_enabled"] is False
    assert canonical_local_graph_memory_projection_json(manifest) == json.dumps(
        manifest,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1311_projection_envelope_is_canonical_local_and_hash_bound() -> None:
    envelope = _projection_envelope()
    exported_once = export_public_safe_projection_envelope_json(envelope)
    exported_twice = export_public_safe_projection_envelope_json(envelope)
    parsed = json.loads(exported_once)

    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        parsed,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert parsed["tokens"] == sorted(REQUIRED_TOKENS)
    assert parsed["local_only"] is True
    assert parsed["query_result_count"] == 3
    assert parsed["query_result_bytes"] == len(
        canonical_local_graph_memory_projection_json(parsed["records"]).encode("utf-8")
    )
    assert local_graph_memory_projection_ref(envelope).startswith(
        f"{LOCAL_GRAPH_MEMORY_PROJECTION_REF_PREFIX}:"
    )
    assert validate_public_safe_projection_envelope(envelope, projection_epoch=31) == envelope


def test_phase_1311_query_summary_does_not_leak_raw_graph_identifiers() -> None:
    record = build_aggregate_summary_record_from_query_result(
        {
            "edge_count": 2,
            "hyperedge_count": 1,
            "node_count": 3,
            "nodes": [
                {"canonical_id": "private-node-a"},
                {"canonical_id": "private-node-b"},
            ],
            "edges": [{"source": "private-node-a", "target": "private-node-b"}],
        },
        record_id=_ref("record", H1),
    )
    payload = canonical_local_graph_memory_projection_json(record)

    assert record == {
        "artifact_refs": [],
        "counts": {
            "edge_count": 2,
            "hyperedge_count": 1,
            "node_count": 3,
            "query_result_count": 1,
        },
        "record_id": _ref("record", H1),
        "record_kind": "aggregate_summary",
        "source_kind": "local_sidecar_query_result",
    }
    for forbidden in ("private-node-a", "private-node-b", "canonical_id"):
        assert forbidden not in payload


def test_phase_1311_confidential_coordination_records_are_opaque_refs_only() -> None:
    envelope = _projection_envelope()
    exported = export_public_safe_projection_envelope_json(envelope)

    for allowed in (
        "private_gated_shard_header",
        "encrypted_coordination_reference",
        _ref("private_shard_header", H1),
        _ref("encrypted_coordination", H2),
        _ref("ciphertext", H1),
        _ref("capability", H1),
    ):
        assert allowed in exported
    for forbidden in (
        "plaintext",
        "membership",
        "route_history",
        "sealed_payload",
        "private-node",
        "AgentID",
        "wallet",
    ):
        assert forbidden not in exported


def test_phase_1311_envelope_rejects_public_authority_flags() -> None:
    envelope = _projection_envelope()
    drift = copy.deepcopy(envelope)
    drift["authorization_flags"]["public_sidecar_projection_serving_enabled"] = True

    with pytest.raises(LocalGraphMemoryProjectionError) as exc:
        validate_public_safe_projection_envelope(drift, projection_epoch=31)
    assert exc.value.token == PUBLIC_SIDECAR_PROJECTION_SERVING_NOT_ENABLED_TOKEN


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("plaintext", "secret"),
        ("membership", ["agent-a"]),
        ("route_history", ["relay-a"]),
        ("sealed_payload", "payload"),
        ("AgentID", "agent-a"),
        ("wallet", "wallet-a"),
    ),
)
def test_phase_1311_records_reject_private_or_identity_fields(key: str, value: object) -> None:
    record = build_private_gated_shard_header_record(
        capability_policy_ref=_ref("capability_policy", H1),
        encrypted_coordination_refs=[],
        record_id=_ref("record", H1),
        shard_commitment_ref=_ref("shard_commitment", H1),
        shard_epoch=31,
        shard_header_ref=_ref("private_shard_header", H1),
    )
    record[key] = value

    with pytest.raises(LocalGraphMemoryProjectionError) as exc:
        build_public_safe_projection_envelope(
            projection_epoch=31,
            records=[record],
            source_artifact_root_ref=_ref("root", H1),
        )
    assert exc.value.token in {
        "local_graph_memory_projection_private_field_forbidden_phase_1311",
        "local_graph_memory_projection_record_keys_invalid_phase_1311",
    }


def test_phase_1311_rejects_floats_tuples_cycles_and_size_drift() -> None:
    with pytest.raises(LocalGraphMemoryProjectionError, match="float"):
        build_aggregate_summary_record_from_query_result(
            {"node_count": 1.5},
            record_id=_ref("record", H1),
        )

    with pytest.raises(LocalGraphMemoryProjectionError, match="tuple"):
        build_public_safe_projection_envelope(
            projection_epoch=31,
            records=[
                {
                    "artifact_refs": (),
                    "counts": {"node_count": 1},
                    "record_id": _ref("record", H1),
                    "record_kind": "aggregate_summary",
                    "source_kind": "local_sidecar_query_result",
                }
            ],
            source_artifact_root_ref=_ref("root", H1),
        )

    cycle: dict[str, object] = {
        "artifact_refs": [],
        "counts": {"node_count": 1},
        "record_id": _ref("record", H1),
        "record_kind": "aggregate_summary",
        "source_kind": "local_sidecar_query_result",
    }
    cycle["self"] = cycle
    with pytest.raises(LocalGraphMemoryProjectionError, match="cycle"):
        build_public_safe_projection_envelope(
            projection_epoch=31,
            records=[cycle],
            source_artifact_root_ref=_ref("root", H1),
        )

    with pytest.raises(LocalGraphMemoryProjectionError) as exc:
        build_public_safe_projection_envelope(
            max_bytes=1,
            projection_epoch=31,
            records=[build_aggregate_summary_record_from_query_result({"node_count": 1}, record_id=_ref("record", H1))],
            source_artifact_root_ref=_ref("root", H1),
        )
    assert exc.value.token == "local_graph_memory_projection_size_exceeded_phase_1311"


def test_phase_1311_registry_manifest_records_projection_sidecar_without_serving() -> None:
    manifest = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in manifest["sidecars"]}
    projection = sidecars["local_graph_memory_projection"]

    assert projection["authority_gate"] == (
        "phase_1311_1312_local_projection_substrate_privacy_hardened_public_serving_blocked"
    )
    assert (
        projection["implementation_status"]
        == "local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312"
    )
    assert projection["public_serving_enabled"] is False
    assert PUBLIC_SAFE_PROJECTION_IMPLEMENTATION_LOCAL_ONLY_TOKEN in projection["required_capabilities"]
    integrity_projection = manifest["package_profile_integrity"][
        "local_graph_memory_projection_sidecar_manifest"
    ]
    assert integrity_projection["local_only"] is True
    assert integrity_projection["public_sidecar_projection_serving_enabled"] is False


def test_phase_1311_source_has_no_public_server_network_or_assert_surface() -> None:
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


def test_phase_1311_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            MODULE_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            ARCHITECTURE_PATH,
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
        "no wallet withdrawal",
        "no ECU minting",
        "no ILC settlement",
        "Phase 1312 is sensitive and requires explicit `GO Phase 1312`",
    ):
        assert phrase in corpus
