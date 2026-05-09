from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN as PHASE_1267_NON_LOOPBACK_TOKEN,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN as PHASE_1267_REQUESTER_TOKEN,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN as PHASE_1267_PUBLIC_P2P_TOKEN,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
    build_transport_principal_context,
)
from ilc_core.network.d2d.transport_principal_public_path_preflight import (
    CDL087_FIX_AFTER_1278_PLANNED_TOKEN,
    GENESIS_ATLAS_V02_SIGNING_DEFERRED_TOKEN,
    NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN,
    PREFLIGHT_REF_PREFIX,
    PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN,
    REQUESTER_ID_FALLBACK_STILL_FORBIDDEN_TOKEN,
    TRANSPORT_PRINCIPAL_PUBLIC_PATH_PREFLIGHT_VERSION,
    TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN,
    build_transport_principal_public_path_preflight,
    export_transport_principal_public_path_preflight_json,
    transport_principal_public_path_preflight_ref,
    validate_transport_principal_public_path_preflight,
)


MODULE_PATH = Path("ilc_core/network/d2d/transport_principal_public_path_preflight.py")
SPEC_PATH = Path(
    "docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1277_transport_principal_public_path_adr_runtime_integration_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1",
    "transport_principal_public_p2p_not_activated_phase_1277",
    "requester_id_fallback_still_forbidden_phase_1277",
    "non_loopback_projection_still_blocked_phase_1277",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1277-authenticated-handshake-material",
        handshake_nonce="phase-1277-nonce",
        issued_epoch=20,
        expires_epoch=24,
        current_epoch=22,
    )


def _preflight() -> dict[str, object]:
    return build_transport_principal_public_path_preflight(
        transport_principal_context=_context(),
        current_epoch=22,
    )


def test_phase_1277_preflight_binds_transport_principal_without_public_activation() -> None:
    preflight = _preflight()

    assert preflight["version"] == TRANSPORT_PRINCIPAL_PUBLIC_PATH_PREFLIGHT_VERSION
    assert preflight["state"] == "public_path_preflight_only"
    assert preflight["context_version"] == TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION
    assert preflight["context_scope"] == "pre_public_path"
    assert preflight["issued_epoch"] == 20
    assert preflight["current_epoch"] == 22
    assert preflight["expires_epoch"] == 24

    authorization_flags = preflight["authorization_flags"]
    assert isinstance(authorization_flags, dict)
    for flag in (
        "public_p2p_enabled",
        "public_fetch_serving_enabled",
        "non_loopback_projection_enabled",
        "cdl087_ratified",
        "sidecar_public_path_authorized",
        "rust_public_p2p_hardening_complete",
        "release_artifact_authorized",
    ):
        assert authorization_flags[flag] is False

    fallback_policy = preflight["fallback_policy"]
    assert isinstance(fallback_policy, dict)
    assert fallback_policy["rate_limit_identity_source"] == "authenticated_transport_principal"
    assert fallback_policy["requester_id_fallback_allowed"] is False
    assert fallback_policy["client_ip_rate_limit_key_allowed"] is False
    assert fallback_policy["agent_id_rate_limit_key_allowed"] is False
    assert fallback_policy["harness_identity_rate_limit_key_allowed"] is False

    for key, prefix in (
        ("credential_fingerprint", ""),
        ("principal_id", "tp:"),
        ("rate_limit_key", "tp_rate:"),
        ("admission_key", "tp_admission:"),
        ("ban_key", "tp_ban:"),
        ("replay_key", "tp_replay:"),
        ("preflight_sha256", ""),
    ):
        value = preflight[key]
        assert isinstance(value, str)
        assert value.startswith(prefix)
        assert len(value.removeprefix(prefix)) == 64

    for token in REQUIRED_TOKENS:
        assert token in preflight["tokens"]
    assert PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN in preflight["tokens"]
    assert CDL087_FIX_AFTER_1278_PLANNED_TOKEN in preflight["tokens"]
    assert GENESIS_ATLAS_V02_SIGNING_DEFERRED_TOKEN in preflight["tokens"]

    for phase_1267_token in (
        PHASE_1267_PUBLIC_P2P_TOKEN,
        PHASE_1267_REQUESTER_TOKEN,
        PHASE_1267_NON_LOOPBACK_TOKEN,
    ):
        assert phase_1267_token in preflight["context_tokens"]


@pytest.mark.parametrize(
    ("flag_name", "token"),
    (
        ("public_p2p_enabled", TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN),
        ("public_fetch_serving_enabled", PUBLIC_FETCH_SERVING_NOT_ENABLED_TOKEN),
        ("non_loopback_projection_enabled", NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN),
        ("requester_id_fallback_allowed", REQUESTER_ID_FALLBACK_STILL_FORBIDDEN_TOKEN),
        ("client_ip_rate_limit_key_allowed", "client_ip_rate_limit_key_still_devnet_only_phase_1277"),
        ("agent_id_rate_limit_key_allowed", "agent_id_rate_limit_key_still_forbidden_phase_1277"),
        (
            "harness_identity_rate_limit_key_allowed",
            "harness_identity_rate_limit_key_still_forbidden_phase_1277",
        ),
    ),
)
def test_phase_1277_public_path_and_fallback_flags_fail_closed(
    flag_name: str,
    token: str,
) -> None:
    kwargs = {
        "transport_principal_context": _context(),
        "current_epoch": 22,
        flag_name: True,
    }
    with pytest.raises(ValueError, match=token):
        build_transport_principal_public_path_preflight(**kwargs)


def test_phase_1277_validate_rejects_public_activation_tampering() -> None:
    preflight = _preflight()

    tampered_public = dict(preflight)
    tampered_public["authorization_flags"] = dict(preflight["authorization_flags"])
    tampered_public["authorization_flags"]["public_p2p_enabled"] = True
    with pytest.raises(ValueError, match=TRANSPORT_PRINCIPAL_PUBLIC_P2P_NOT_ACTIVATED_TOKEN):
        validate_transport_principal_public_path_preflight(tampered_public, current_epoch=22)

    tampered_projection = dict(preflight)
    tampered_projection["authorization_flags"] = dict(preflight["authorization_flags"])
    tampered_projection["authorization_flags"]["non_loopback_projection_enabled"] = True
    with pytest.raises(ValueError, match=NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN):
        validate_transport_principal_public_path_preflight(tampered_projection, current_epoch=22)

    tampered_fallback = dict(preflight)
    tampered_fallback["fallback_policy"] = dict(preflight["fallback_policy"])
    tampered_fallback["fallback_policy"]["requester_id_fallback_allowed"] = True
    with pytest.raises(ValueError, match=REQUESTER_ID_FALLBACK_STILL_FORBIDDEN_TOKEN):
        validate_transport_principal_public_path_preflight(tampered_fallback, current_epoch=22)


def test_phase_1277_validates_lifecycle_revocation_replay_and_float_boundaries() -> None:
    preflight = _preflight()

    expired = dict(preflight)
    expired["current_epoch"] = 25
    with pytest.raises(ValueError, match="transport_principal_public_path_current_epoch_mismatch"):
        validate_transport_principal_public_path_preflight(expired, current_epoch=22)

    expired_at_current = dict(preflight)
    expired_at_current["current_epoch"] = 25
    expired_at_current["preflight_sha256"] = preflight["preflight_sha256"]
    with pytest.raises(ValueError, match="transport_principal_public_path_epoch_window_invalid"):
        validate_transport_principal_public_path_preflight(expired_at_current, current_epoch=25)

    with pytest.raises(ValueError, match="transport_principal_public_path_revoked"):
        validate_transport_principal_public_path_preflight(
            preflight,
            current_epoch=22,
            revoked_credential_fingerprints={str(preflight["credential_fingerprint"])},
        )

    with pytest.raises(ValueError, match="transport_principal_public_path_replay_detected"):
        validate_transport_principal_public_path_preflight(
            preflight,
            current_epoch=22,
            replay_cache={str(preflight["replay_key"])},
        )

    float_tampered = dict(preflight)
    float_tampered["unexpected_float"] = 1.0
    with pytest.raises(ValueError, match="transport_principal_public_path_float_values_forbidden"):
        validate_transport_principal_public_path_preflight(float_tampered, current_epoch=22)


def test_phase_1277_canonical_export_and_ref_are_stable() -> None:
    preflight = _preflight()
    validated = validate_transport_principal_public_path_preflight(preflight, current_epoch=22)
    exported = export_transport_principal_public_path_preflight_json(preflight)

    assert exported == json.dumps(
        validated,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    assert json.loads(exported) == validated
    assert transport_principal_public_path_preflight_ref(preflight) == (
        f"{PREFLIGHT_REF_PREFIX}:{preflight['preflight_sha256']}"
    )

    hash_tampered = dict(preflight)
    hash_tampered["privacy_extra"] = "hash-mismatch"
    with pytest.raises(ValueError, match="transport_principal_public_path_preflight_hash_mismatch"):
        validate_transport_principal_public_path_preflight(hash_tampered, current_epoch=22)


def test_phase_1277_runtime_module_is_internal_only_and_has_no_public_server() -> None:
    source = _read(MODULE_PATH)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in source
    for forbidden in (
        "ThreadingHTTPServer",
        "BaseHTTPRequestHandler",
        "import socket",
        "socket.",
        "requests.",
        "urllib",
        "time.time",
        "datetime.now",
        "random.",
        "requester_id:alice",
        "rate_limit_key=client_ip",
    ):
        assert forbidden not in source

    assert "json.dumps(" in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source


def test_phase_1277_docs_status_planning_and_roadmap_record_required_tokens() -> None:
    for path in (SPEC_PATH, WALKTHROUGH_PATH, STATUS_PATH, PLANNING_INDEX_PATH, ROADMAP_PATH):
        text = _read(path)
        for token in REQUIRED_TOKENS:
            assert token in text
        assert CDL087_FIX_AFTER_1278_PLANNED_TOKEN in text
        assert GENESIS_ATLAS_V02_SIGNING_DEFERRED_TOKEN in text

    planning = _read(PLANNING_INDEX_PATH)
    assert "Window 1273-1280 OPEN through Phase 1277" in planning
    assert "Phase 1278 is next and remains SENSITIVE" in planning


def test_phase_1277_records_broad_discovery_non_claims_and_user_decisions() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    register = _read(CDL_REGISTER_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "Source expansion" in text
        assert "requester_id" in text
        assert "client_ip" in text
        assert "AgentID" in text
        assert "public P2P" in text
        assert "public fetch serving" in text
        assert "non-loopback projection" in text
        assert "CDL-087 ratification Fix phase" in text
        assert "Genesis Atlas v0.2 signing" in text

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    assert "| open |" in cdl087_rows[0]


def test_phase_1277_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_code_added:ilc_core/network/d2d/transport_principal_public_path_preflight.py -> transport/identity",
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md -> transport/identity",
        "graph_delta=support_tests_added:tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py -> validation",
        "graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security",
        "graph_delta=support_only:docs/phases/phase_1277_transport_principal_public_path_adr_runtime_integration_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status
