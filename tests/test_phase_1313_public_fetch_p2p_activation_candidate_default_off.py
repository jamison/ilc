from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.sidecars.public_fetch_p2p_readiness import (
    PHASE_1314_NEXT_TOKEN,
    PUBLIC_FETCH_P2P_READINESS_VERSION,
    PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN,
    PUBLIC_P2P_DEFAULT_OFF_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1313_TOKEN,
    READINESS_REF_PREFIX,
    RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN,
    TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN,
    PublicFetchP2PReadinessError,
    build_public_fetch_p2p_readiness_candidate,
    export_public_fetch_p2p_readiness_candidate_json,
    public_fetch_p2p_readiness_candidate_manifest,
    public_fetch_p2p_readiness_candidate_ref,
    public_fetch_p2p_readiness_required_tokens,
    validate_public_fetch_p2p_readiness_candidate,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/public_fetch_p2p_readiness.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_public_fetch_p2p_activation_candidate_default_off_1313_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1313_public_fetch_p2p_activation_candidate_default_off_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
NETWORK_PLAN_PATH = (
    ROOT / "docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md"
)
ARCHITECTURE_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"

REQUIRED_TOKENS = [
    PUBLIC_FETCH_P2P_READINESS_VERSION,
    RUST_PUBLIC_P2P_SUBSTRATE_GATE_STATUS_RECORDED_TOKEN,
    PUBLIC_P2P_DEFAULT_OFF_TOKEN,
    PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN,
    TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN,
    PHASE_1314_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1313_TOKEN,
]


def _candidate() -> dict:
    return build_public_fetch_p2p_readiness_candidate(current_epoch=1313)


def test_phase_1313_default_off_readiness_packet_is_deterministic() -> None:
    packet = _candidate()
    exported_once = export_public_fetch_p2p_readiness_candidate_json(packet)
    exported_twice = export_public_fetch_p2p_readiness_candidate_json(packet)

    assert public_fetch_p2p_readiness_required_tokens() == REQUIRED_TOKENS
    assert packet["version"] == PUBLIC_FETCH_P2P_READINESS_VERSION
    assert packet["tokens"] == REQUIRED_TOKENS
    assert packet["local_only"] is True
    assert packet["readiness_verdict"] == (
        "blocked_default_off_rust_public_p2p_substrate_gate_required"
    )
    assert packet["rust_public_p2p_substrate_gate"]["status"] == "gate_required_not_satisfied"
    assert packet["rust_public_p2p_substrate_gate"][
        "explicit_adr_integration_gate_present"
    ] is False
    assert packet["rust_public_p2p_substrate_gate"]["substrate_decision_adr_required"] is True
    assert packet["rust_public_p2p_substrate_gate"]["rust_network_rs_path"] == (
        "ilc_consensus/src/network.rs"
    )
    assert all(value is False for value in packet["authorization_flags"].values())
    assert packet["transport_principal_dependency"]["local_only"] is True
    assert packet["transport_principal_dependency"][
        "hostile_network_public_path_blocked"
    ] is True
    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        json.loads(exported_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert public_fetch_p2p_readiness_candidate_ref(packet).startswith(
        f"{READINESS_REF_PREFIX}:"
    )


def test_phase_1313_public_activation_flags_fail_closed() -> None:
    cases = [
        ("public_p2p_enabled", PUBLIC_P2P_DEFAULT_OFF_TOKEN),
        ("public_fetch_serving_enabled", PUBLIC_FETCH_SERVING_DEFAULT_OFF_TOKEN),
        (
            "transport_public_path_activation_authorized",
            TRANSPORT_PUBLIC_PATH_ACTIVATION_NOT_AUTHORIZED_TOKEN,
        ),
        ("public_listener_enabled", "public_fetch_p2p_public_authority_forbidden_phase_1313"),
        ("peer_discovery_enabled", "public_fetch_p2p_public_authority_forbidden_phase_1313"),
        ("non_loopback_bind_enabled", "public_fetch_p2p_public_authority_forbidden_phase_1313"),
        ("wildcard_bind_enabled", "public_fetch_p2p_public_authority_forbidden_phase_1313"),
        ("public_host_bind_enabled", "public_fetch_p2p_public_authority_forbidden_phase_1313"),
        (
            "python_http_transport_public_substrate_enabled",
            "public_fetch_p2p_public_authority_forbidden_phase_1313",
        ),
        (
            "public_sidecar_projection_serving_enabled",
            "public_fetch_p2p_public_authority_forbidden_phase_1313",
        ),
    ]
    for field, token in cases:
        with pytest.raises(PublicFetchP2PReadinessError) as exc:
            build_public_fetch_p2p_readiness_candidate(current_epoch=1313, **{field: True})
        assert exc.value.token == token


def test_phase_1313_rust_gate_status_is_recorded_without_activation() -> None:
    with pytest.raises(PublicFetchP2PReadinessError) as exc:
        build_public_fetch_p2p_readiness_candidate(
            current_epoch=1313,
            rust_public_p2p_substrate_gate_status=(
                "adr_integration_gate_satisfied_but_activation_out_of_scope"
            ),
        )
    assert exc.value.token == "public_fetch_p2p_rust_gate_evidence_required_phase_1313"

    packet = build_public_fetch_p2p_readiness_candidate(
        current_epoch=1313,
        rust_public_p2p_substrate_gate_status=(
            "adr_integration_gate_satisfied_but_activation_out_of_scope"
        ),
        explicit_rust_public_p2p_adr_integration_gate_present=True,
    )
    assert packet["readiness_verdict"] == (
        "readiness_only_activation_out_of_scope_even_with_substrate_gate"
    )
    assert packet["rust_public_p2p_substrate_gate"][
        "activation_candidate_authorized"
    ] is False
    assert all(value is False for value in packet["authorization_flags"].values())

    with pytest.raises(PublicFetchP2PReadinessError) as ambiguous_exc:
        build_public_fetch_p2p_readiness_candidate(
            current_epoch=1313,
            rust_public_p2p_substrate_gate_status="gate_ambiguous_human_review_required",
            explicit_rust_public_p2p_adr_integration_gate_present=True,
        )
    assert ambiguous_exc.value.token == (
        "public_fetch_p2p_rust_gate_status_contradiction_phase_1313"
    )


def test_phase_1313_validation_rejects_mutated_public_claims_and_hash_drift() -> None:
    packet = _candidate()

    mutated = copy.deepcopy(packet)
    mutated["authorization_flags"]["public_listener_enabled"] = True
    with pytest.raises(PublicFetchP2PReadinessError) as exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert exc.value.token == "public_fetch_p2p_public_authority_forbidden_phase_1313"

    mutated = copy.deepcopy(packet)
    mutated["python_http_transport_classification"]["public_substrate_enabled"] = True
    with pytest.raises(PublicFetchP2PReadinessError) as python_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert python_exc.value.token == (
        "public_fetch_p2p_python_http_public_substrate_forbidden_phase_1313"
    )

    mutated = copy.deepcopy(packet)
    mutated["transport_principal_dependency"]["local_only"] = False
    with pytest.raises(PublicFetchP2PReadinessError) as transport_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert transport_exc.value.token == (
        "public_fetch_p2p_transport_dependency_local_only_required_phase_1313"
    )

    mutated = copy.deepcopy(packet)
    mutated["candidate_sha256"] = "0" * 64
    with pytest.raises(PublicFetchP2PReadinessError) as hash_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert hash_exc.value.token == "public_fetch_p2p_readiness_candidate_hash_mismatch_phase_1313"

    mutated = copy.deepcopy(packet)
    mutated["readiness_verdict"] = "public_fetch_p2p_ready"
    with pytest.raises(PublicFetchP2PReadinessError) as verdict_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert verdict_exc.value.token == "public_fetch_p2p_readiness_verdict_invalid_phase_1313"

    mutated = copy.deepcopy(packet)
    mutated["source_evidence"]["phase_1313_scope"] = "activation_claimed"
    with pytest.raises(PublicFetchP2PReadinessError) as evidence_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert evidence_exc.value.token == "public_fetch_p2p_source_evidence_invalid_phase_1313"

    mutated = copy.deepcopy(packet)
    mutated["required_before_public_activation"].append("optional_public_activation")
    with pytest.raises(PublicFetchP2PReadinessError) as requirements_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert requirements_exc.value.token == "public_fetch_p2p_requirements_invalid_phase_1313"

    mutated = copy.deepcopy(packet)
    mutated["rust_public_p2p_substrate_gate"]["rust_network_rs_path"] = "network.rs"
    with pytest.raises(PublicFetchP2PReadinessError) as path_exc:
        validate_public_fetch_p2p_readiness_candidate(mutated)
    assert path_exc.value.token == "public_fetch_p2p_rust_gate_path_invalid_phase_1313"


def test_phase_1313_registry_records_readiness_sidecar_without_public_serving() -> None:
    manifest = public_fetch_p2p_readiness_candidate_manifest()
    registry = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in registry["sidecars"]}
    readiness = sidecars["public_fetch_p2p_readiness_candidate"]
    integrity = registry["package_profile_integrity"][
        "public_fetch_p2p_readiness_candidate_manifest"
    ]

    assert manifest["contract_version"] == PUBLIC_FETCH_P2P_READINESS_VERSION
    assert manifest["readiness_only"] is True
    assert manifest["public_p2p_enabled"] is False
    assert manifest["public_fetch_serving_enabled"] is False
    assert manifest["tokens"] == REQUIRED_TOKENS
    assert readiness["authority_gate"] == (
        "phase_1313_default_off_readiness_only_rust_public_p2p_gate_required"
    )
    assert readiness["implementation_status"] == (
        "readiness_candidate_recorded_phase_1313_default_off"
    )
    for token in REQUIRED_TOKENS[1:5]:
        assert token in readiness["required_capabilities"]
    assert integrity == manifest


def test_phase_1313_source_has_no_network_server_or_clock_surface() -> None:
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
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_roots


def test_phase_1313_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
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
            NETWORK_PLAN_PATH,
            ARCHITECTURE_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for non_claim in (
        "no public P2P",
        "no public fetch serving",
        "no public listener",
        "no peer discovery",
        "no non-loopback bind",
        "no public transport claim",
        "Phase 1314 is sensitive and requires explicit `GO Phase 1314`",
    ):
        assert non_claim in corpus
