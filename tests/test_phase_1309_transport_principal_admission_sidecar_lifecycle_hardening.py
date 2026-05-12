from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
    build_transport_principal_context,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest
from ilc_core.sidecars.transport_principal_admission import (
    ADMISSION_DECISION_STATE,
    ADMITTED_LOCAL_ONLY_DECISION,
    PHASE_1310_NEXT_TOKEN,
    PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1309_TOKEN,
    TRANSPORT_PRINCIPAL_ADMISSION_DECISION_REF_PREFIX,
    TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION,
    TRANSPORT_PRINCIPAL_LIFECYCLE_POLICY_LOCAL_SUBSTRATE_TOKEN,
    TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN,
    TransportPrincipalAdmissionSidecarError,
    build_transport_principal_admission_decision,
    export_transport_principal_admission_decision_json,
    transport_principal_admission_decision_ref,
    transport_principal_admission_required_tokens,
    transport_principal_admission_sidecar_manifest,
    validate_transport_principal_admission_decision,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/transport_principal_admission.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
GUARDRAIL_PATH = ROOT / "tools/check_sensitive_runtime_coding_taboos.py"
SPEC_PATH = (
    ROOT
    / "docs/specs/ilc_transport_principal_admission_sidecar_lifecycle_1309_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1309_transport_principal_admission_sidecar_lifecycle_hardening_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
SIDECAR_ARCH_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"

REQUIRED_TOKENS = [
    TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION,
    TRANSPORT_PRINCIPAL_LIFECYCLE_POLICY_LOCAL_SUBSTRATE_TOKEN,
    TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN,
    PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
    PHASE_1310_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1309_TOKEN,
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1309-authenticated-handshake-material",
        handshake_nonce="phase-1309-nonce",
        issued_epoch=40,
        expires_epoch=44,
        current_epoch=42,
    )


def _decision() -> dict[str, object]:
    return build_transport_principal_admission_decision(
        transport_principal_context=_context(),
        current_epoch=42,
    )


def test_phase_1309_admission_decision_is_local_lifecycle_substrate_only() -> None:
    decision = _decision()

    assert decision["version"] == TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION
    assert decision["state"] == ADMISSION_DECISION_STATE
    assert decision["decision"] == ADMITTED_LOCAL_ONLY_DECISION
    assert decision["context_version"] == TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION
    assert decision["context_scope"] == "pre_public_path"
    assert decision["current_epoch"] == 42
    assert decision["issued_epoch"] == 40
    assert decision["expires_epoch"] == 44
    assert decision["privacy_mode"] == "ephemeral_principal_no_agentid_default"

    for key, prefix in (
        ("credential_fingerprint", ""),
        ("context_sha256", ""),
        ("admission_decision_sha256", ""),
        ("principal_id", "tp:"),
        ("rate_limit_key", "tp_rate:"),
        ("admission_key", "tp_admission:"),
        ("ban_key", "tp_ban:"),
        ("replay_key", "tp_replay:"),
    ):
        value = decision[key]
        assert isinstance(value, str)
        assert value.startswith(prefix)
        assert len(value.removeprefix(prefix)) == 64

    assert decision["tokens"] == sorted(REQUIRED_TOKENS)
    for token in REQUIRED_TOKENS:
        assert token in decision["tokens"]
    assert transport_principal_admission_required_tokens() == REQUIRED_TOKENS

    for value in decision["authorization_flags"].values():
        assert value is False
    for key, value in decision["fallback_policy"].items():
        if key == "rate_limit_identity_source":
            assert value == "authenticated_transport_principal"
        else:
            assert value is False
    assert decision["state_checks"]["public_persistent_state_activated"] is False
    assert decision["state_checks"]["rate_limit_key_bound_to_transport_principal"] is True


def test_phase_1309_manifest_and_registry_record_local_only_transport_sidecar() -> None:
    manifest = transport_principal_admission_sidecar_manifest()
    registry = build_sidecar_registry_manifest()
    sidecars = {record["sidecar_id"]: record for record in registry["sidecars"]}

    assert manifest["contract_version"] == TRANSPORT_PRINCIPAL_ADMISSION_SIDECAR_VERSION
    assert manifest["local_only"] is True
    assert manifest["public_path_activation_authorized"] is False
    assert manifest["public_p2p_enabled"] is False
    assert manifest["public_fetch_serving_enabled"] is False
    assert manifest["public_credential_issuer_authorized"] is False
    assert manifest["tokens"] == REQUIRED_TOKENS

    transport = sidecars["transport_principal_admission"]
    assert transport["authority_gate"] == (
        "phase_1309_1310_local_lifecycle_substrate_public_path_blocked"
    )
    assert transport["implementation_status"] == (
        "lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310"
    )
    assert transport["public_serving_enabled"] is False
    assert TRANSPORT_PRINCIPAL_LIFECYCLE_POLICY_LOCAL_SUBSTRATE_TOKEN in transport[
        "required_capabilities"
    ]
    assert registry["package_profile_integrity"][
        "transport_principal_admission_sidecar_manifest"
    ] == manifest


def test_phase_1309_canonical_export_and_ref_are_stable() -> None:
    decision = _decision()
    validated = validate_transport_principal_admission_decision(decision, current_epoch=42)
    exported_once = export_transport_principal_admission_decision_json(decision)
    exported_twice = export_transport_principal_admission_decision_json(decision)

    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        validated,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert json.loads(exported_once) == validated
    assert transport_principal_admission_decision_ref(decision) == (
        f"{TRANSPORT_PRINCIPAL_ADMISSION_DECISION_REF_PREFIX}:"
        f"{decision['admission_decision_sha256']}"
    )


@pytest.mark.parametrize(
    ("flag_name", "token"),
    (
        ("public_path_activation_authorized", TRANSPORT_PRINCIPAL_PUBLIC_PATH_NOT_ACTIVATED_TOKEN),
        ("public_p2p_enabled", PUBLIC_P2P_NOT_ACTIVATED_TOKEN),
        ("public_fetch_serving_enabled", "transport_principal_admission_public_authority_forbidden_phase_1309"),
        ("public_listener_enabled", "transport_principal_admission_public_authority_forbidden_phase_1309"),
        ("peer_discovery_enabled", "transport_principal_admission_public_authority_forbidden_phase_1309"),
        ("requester_id_fallback_allowed", "transport_principal_admission_fallback_identity_forbidden_phase_1309"),
        ("client_ip_rate_limit_key_allowed", "transport_principal_admission_fallback_identity_forbidden_phase_1309"),
        ("agent_id_rate_limit_key_allowed", "transport_principal_admission_fallback_identity_forbidden_phase_1309"),
    ),
)
def test_phase_1309_public_authority_and_fallback_flags_fail_closed(
    flag_name: str,
    token: str,
) -> None:
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as exc_info:
        build_transport_principal_admission_decision(
            transport_principal_context=_context(),
            current_epoch=42,
            **{flag_name: True},
        )

    assert exc_info.value.token == token


def test_phase_1309_lifecycle_revocation_replay_ban_and_policy_checks_fail_closed() -> None:
    context = _context()

    with pytest.raises(ValueError, match="transport_principal_revoked"):
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=42,
            revoked_credential_fingerprints={str(context["credential_fingerprint"])},
        )

    with pytest.raises(ValueError, match="transport_principal_replay_detected"):
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=42,
            replay_cache={str(context["replay_key"])},
        )

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as banned:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=42,
            banned_transport_keys={str(context["ban_key"])},
        )
    assert banned.value.token == "transport_principal_admission_banned_phase_1309"

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as rejected_kind:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=42,
            accepted_credential_kinds={"transport_credential"},
        )
    assert rejected_kind.value.token == (
        "transport_principal_admission_credential_kind_rejected_phase_1309"
    )

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as bad_privacy:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=42,
            privacy_mode="agentid_visible_default",
        )
    assert bad_privacy.value.token == (
        "transport_principal_admission_privacy_mode_invalid_phase_1309"
    )


def test_phase_1309_validation_rejects_tampering_float_tuple_cycle_and_hash_drift() -> None:
    decision = _decision()

    public_tampered = dict(decision)
    public_tampered["authorization_flags"] = dict(decision["authorization_flags"])
    public_tampered["authorization_flags"]["public_p2p_enabled"] = True
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as public_error:
        validate_transport_principal_admission_decision(public_tampered, current_epoch=42)
    assert public_error.value.token == (
        "transport_principal_admission_authorization_flags_invalid_phase_1309"
    )

    hash_tampered = dict(decision)
    hash_tampered["privacy_mode"] = "rotating_pseudonymous_transport_principal"
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as hash_error:
        validate_transport_principal_admission_decision(hash_tampered, current_epoch=42)
    assert hash_error.value.token == (
        "transport_principal_admission_decision_hash_mismatch_phase_1309"
    )

    float_tampered = dict(decision)
    float_tampered["unexpected_float"] = 1.0
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as float_error:
        validate_transport_principal_admission_decision(float_tampered, current_epoch=42)
    assert float_error.value.token == (
        "transport_principal_admission_float_values_forbidden_phase_1309"
    )

    tuple_tampered = dict(decision)
    tuple_tampered["unexpected_tuple"] = ("not", "json")
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as tuple_error:
        validate_transport_principal_admission_decision(tuple_tampered, current_epoch=42)
    assert tuple_error.value.token == (
        "transport_principal_admission_tuple_values_forbidden_phase_1309"
    )

    cycle_tampered: dict[str, object] = dict(decision)
    cycle_tampered["cycle"] = cycle_tampered
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as cycle_error:
        validate_transport_principal_admission_decision(cycle_tampered, current_epoch=42)
    assert cycle_error.value.token == (
        "transport_principal_admission_payload_cycle_forbidden_phase_1309"
    )


def test_phase_1309_source_has_no_public_server_network_randomness_or_stale_helper_import() -> None:
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
    assert "ilc_core/sidecars/transport_principal_admission.py" in _read(GUARDRAIL_PATH)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_roots
        if isinstance(node, ast.Assert):
            raise AssertionError("assert forbidden in Phase 1309 admission sidecar")


def test_phase_1309_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        _read(path)
        for path in (
            MODULE_PATH,
            REGISTRY_PATH,
            GUARDRAIL_PATH,
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
        "Phase 1310 is sensitive and requires explicit `GO Phase 1310`",
        "no public P2P",
        "no public fetch serving",
        "no public sidecar/projection serving",
        "no public credential issuer authority",
        "no public revocation registry activation",
        "no public replay cache activation",
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
