from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Mapping

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest
from ilc_core.sidecars.transport_principal_admission import (
    ADMISSION_BAN_RATE_PRIVACY_TESTS_HARDENED_PHASE_1310_TOKEN,
    HOSTILE_NETWORK_PUBLIC_PATH_STILL_BLOCKED_PHASE_1310_TOKEN,
    PHASE_1311_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1310_TOKEN,
    REVOCATION_REPLAY_ADMISSION_BAN_TESTS_PHASE_1310_VERSION,
    TRANSPORT_PRINCIPAL_REVOCATION_REPLAY_TESTS_HARDENED_PHASE_1310_TOKEN,
    TransportPrincipalAdmissionSidecarError,
    build_transport_principal_admission_decision,
    export_transport_principal_admission_decision_json,
    transport_principal_admission_sidecar_manifest,
    transport_principal_hostile_network_required_tokens,
    validate_transport_principal_admission_decision,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/transport_principal_admission.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
SPEC_PATH = ROOT / "docs/specs/ilc_revocation_replay_admission_ban_tests_1310_v0.1.md"
WALKTHROUGH_PATH = (
    ROOT / "docs/phases/phase_1310_revocation_replay_admission_ban_tests_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
SIDECAR_ARCH_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"

REQUIRED_TOKENS = [
    REVOCATION_REPLAY_ADMISSION_BAN_TESTS_PHASE_1310_VERSION,
    TRANSPORT_PRINCIPAL_REVOCATION_REPLAY_TESTS_HARDENED_PHASE_1310_TOKEN,
    ADMISSION_BAN_RATE_PRIVACY_TESTS_HARDENED_PHASE_1310_TOKEN,
    HOSTILE_NETWORK_PUBLIC_PATH_STILL_BLOCKED_PHASE_1310_TOKEN,
    PHASE_1311_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1310_TOKEN,
]

FORBIDDEN_PRIVACY_KEYS = {
    "AgentID",
    "agent_id",
    "agentid",
    "client_ip",
    "economic_position",
    "graph_position",
    "harness_identity",
    "json_body_requester_id",
    "openclaw_identity",
    "private_graph_position",
    "requester_id",
    "stake",
    "stake_balance",
    "tailscale_identity",
    "wallet",
    "wallet_address",
    "wallet_balance",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1310-authenticated-handshake-material",
        handshake_nonce="phase-1310-nonce",
        issued_epoch=50,
        expires_epoch=56,
        current_epoch=52,
    )


def _decision() -> dict[str, object]:
    return build_transport_principal_admission_decision(
        transport_principal_context=_context(),
        current_epoch=52,
    )


def _walk_keys(value: object) -> set[str]:
    if isinstance(value, Mapping):
        keys = {str(key) for key in value}
        for item in value.values():
            keys |= _walk_keys(item)
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys |= _walk_keys(item)
        return keys
    return set()


def test_phase_1310_required_tokens_are_exposed_in_manifest() -> None:
    manifest = transport_principal_admission_sidecar_manifest()
    registry = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in registry["sidecars"]}
    transport = sidecars["transport_principal_admission"]

    assert transport_principal_hostile_network_required_tokens() == REQUIRED_TOKENS
    assert manifest["hostile_network_test_tokens"] == REQUIRED_TOKENS
    assert manifest["revocation_replay_tests_hardened"] is True
    assert manifest["admission_ban_rate_privacy_tests_hardened"] is True
    assert manifest["hostile_network_public_path_blocked"] is True
    assert transport["authority_gate"] == (
        "phase_1309_1310_local_lifecycle_substrate_public_path_blocked"
    )
    assert transport["implementation_status"] == (
        "lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310"
    )
    assert transport["public_serving_enabled"] is False
    assert TRANSPORT_PRINCIPAL_REVOCATION_REPLAY_TESTS_HARDENED_PHASE_1310_TOKEN in (
        transport["required_capabilities"]
    )
    assert ADMISSION_BAN_RATE_PRIVACY_TESTS_HARDENED_PHASE_1310_TOKEN in (
        transport["required_capabilities"]
    )


def test_phase_1310_revocation_and_replay_negative_paths_fail_closed() -> None:
    context = _context()

    for revoked_subject in (
        str(context["credential_fingerprint"]),
        str(context["principal_id"]),
    ):
        with pytest.raises(ValueError, match="transport_principal_revoked"):
            build_transport_principal_admission_decision(
                transport_principal_context=context,
                current_epoch=52,
                revoked_credential_fingerprints={revoked_subject},
            )

    with pytest.raises(ValueError, match="transport_principal_replay_detected"):
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=52,
            replay_cache={str(context["replay_key"])},
        )


def test_phase_1310_admission_ban_and_local_rate_limit_paths_fail_closed() -> None:
    context = _context()

    for ban_subject in (
        str(context["ban_key"]),
        str(context["credential_fingerprint"]),
        str(context["principal_id"]),
    ):
        with pytest.raises(TransportPrincipalAdmissionSidecarError) as banned:
            build_transport_principal_admission_decision(
                transport_principal_context=context,
                current_epoch=52,
                banned_transport_keys={ban_subject},
            )
        assert banned.value.token == "transport_principal_admission_banned_phase_1309"

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as rejected_kind:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=52,
            accepted_credential_kinds={"transport_credential"},
        )
    assert rejected_kind.value.token == (
        "transport_principal_admission_credential_kind_rejected_phase_1309"
    )

    below_ceiling = build_transport_principal_admission_decision(
        transport_principal_context=context,
        current_epoch=52,
        rate_limit_counters={str(context["rate_limit_key"]): 2},
        local_rate_limit_ceiling=3,
    )
    assert below_ceiling["state_checks"]["rate_limit_checked"] is True
    assert below_ceiling["state_checks"]["rate_limit_counter"] == 2
    assert below_ceiling["state_checks"]["rate_limit_ceiling"] == 3
    assert below_ceiling["state_checks"]["rate_limit_state_source"] == (
        "caller_supplied_local_collection"
    )

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as limited:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=52,
            rate_limit_counters={str(context["rate_limit_key"]): 3},
            local_rate_limit_ceiling=3,
        )
    assert limited.value.token == "transport_principal_admission_rate_limit_exceeded_phase_1310"


@pytest.mark.parametrize("forbidden_key", sorted(FORBIDDEN_PRIVACY_KEYS))
def test_phase_1310_fallback_and_privacy_context_keys_fail_closed(forbidden_key: str) -> None:
    context = dict(_context())
    context[forbidden_key] = "attacker-supplied-fallback-or-private-field"

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as exc_info:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=52,
        )

    assert exc_info.value.token == (
        "transport_principal_admission_forbidden_identity_context_key_phase_1310"
    )


def test_phase_1310_validation_rejects_extra_keys_non_json_types_and_rate_state_drift() -> None:
    decision = _decision()

    extra_key = dict(decision)
    extra_key["client_ip"] = "203.0.113.10"
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as extra_error:
        validate_transport_principal_admission_decision(extra_key, current_epoch=52)
    assert extra_error.value.token == (
        "transport_principal_admission_unexpected_keys_forbidden_phase_1310"
    )

    nested_set = dict(decision)
    nested_set["state_checks"] = dict(decision["state_checks"])
    nested_set["state_checks"]["rate_limit_counter"] = {"not-json"}
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as type_error:
        validate_transport_principal_admission_decision(nested_set, current_epoch=52)
    assert type_error.value.token == "transport_principal_admission_payload_type_invalid_phase_1310"

    state_drift = dict(decision)
    state_drift["state_checks"] = dict(decision["state_checks"])
    state_drift["state_checks"]["rate_limit_state_source"] = "public_rate_limit_registry"
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as drift_error:
        validate_transport_principal_admission_decision(state_drift, current_epoch=52)
    assert drift_error.value.token == (
        "transport_principal_admission_state_checks_invalid_phase_1309"
    )


def test_phase_1310_exported_decision_does_not_leak_fallback_or_private_fields() -> None:
    decision = _decision()
    exported = json.loads(export_transport_principal_admission_decision_json(decision))
    leaked_keys = _walk_keys(exported) & FORBIDDEN_PRIVACY_KEYS

    assert leaked_keys == set()
    assert exported["fallback_policy"]["rate_limit_identity_source"] == (
        "authenticated_transport_principal"
    )
    assert exported["authorization_flags"]["public_rate_limit_state_activated"] is False
    assert exported["state_checks"]["public_persistent_state_activated"] is False


def test_phase_1310_source_keeps_network_public_surface_absent() -> None:
    source = _read(MODULE_PATH)
    tree = ast.parse(source)
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

    assert "transport_principal_public_path_preflight" not in source
    assert "PUBLIC_RC_EXCLUDE" not in source
    assert "json.dumps(" in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_roots
        if isinstance(node, ast.Assert):
            raise AssertionError("assert forbidden in Phase 1310 admission sidecar")


def test_phase_1310_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        _read(path)
        for path in (
            MODULE_PATH,
            REGISTRY_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            SIDECAR_ARCH_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for phrase in (
        "Phase 1311 is sensitive and requires explicit `GO Phase 1311`",
        "no public P2P",
        "no public fetch serving",
        "no public sidecar/projection serving",
        "no public credential issuer authority",
        "no public revocation registry activation",
        "no public replay cache activation",
        "no public rate-limit state activation",
        "no non-loopback bind",
        "no listener",
        "no peer discovery",
        "no source allowlist export",
        "no public package publication",
        "no wallet withdrawal",
        "no ECU minting",
        "no ILC settlement",
    ):
        assert phrase in corpus
