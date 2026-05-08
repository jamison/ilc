from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN,
    REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN,
    TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN,
    TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION,
    build_transport_principal_context,
    export_transport_principal_context_json,
    validate_transport_principal_context,
)


MODULE_PATH = Path("ilc_core/network/d2d/transport_principal_pre_public_path.py")
SPEC_PATH = Path(
    "docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1267_transport_principal_runtime_identity_pre_public_path_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1",
    "transport_principal_runtime_not_public_p2p_activation_phase_1267",
    "requester_id_rate_limit_fallback_still_forbidden_phase_1267",
    "non_loopback_projection_still_blocked_phase_1267",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1267-authenticated-handshake-material",
        handshake_nonce="phase-1267-nonce",
        issued_epoch=10,
        expires_epoch=12,
        current_epoch=11,
    )


def test_phase_1267_context_derives_full_hash_public_path_keys() -> None:
    context = _context()

    assert context["version"] == TRANSPORT_PRINCIPAL_PRE_PUBLIC_PATH_VERSION
    assert context["scope"] == "pre_public_path"
    assert context["public_p2p_enabled"] is False
    assert context["non_loopback_projection_enabled"] is False
    assert context["requester_id_fallback_allowed"] is False
    assert context["agent_id_rate_limit_key_allowed"] is False
    assert context["client_ip_rate_limit_key_allowed"] is False

    for key, prefix in (
        ("credential_fingerprint", ""),
        ("handshake_nonce_fingerprint", ""),
        ("principal_id", "tp:"),
        ("rate_limit_key", "tp_rate:"),
        ("admission_key", "tp_admission:"),
        ("ban_key", "tp_ban:"),
        ("replay_key", "tp_replay:"),
    ):
        value = context[key]
        assert isinstance(value, str)
        assert value.startswith(prefix)
        assert len(value.removeprefix(prefix)) == 64

    for token in REQUIRED_TOKENS:
        assert token in context["tokens"]


@pytest.mark.parametrize(
    "credential_kind",
    ["requester_id", "client_ip", "agent_id", "harness_identity", "json_body_requester_id"],
)
def test_phase_1267_rejects_public_rate_limit_fallback_identity_kinds(
    credential_kind: str,
) -> None:
    with pytest.raises(ValueError, match="transport_principal_forbidden_identity_fallback"):
        build_transport_principal_context(
            credential_kind=credential_kind,
            credential_material="fallback-identity-material",
            handshake_nonce="nonce",
            issued_epoch=1,
            expires_epoch=3,
            current_epoch=2,
        )


@pytest.mark.parametrize(
    "credential_material",
    [
        "requester_id:alice",
        "client_ip:127.0.0.1",
        "agent_id:agent-123",
        b"harness_identity:test-peer",
    ],
)
def test_phase_1267_rejects_disguised_fallback_material(
    credential_material: bytes | str,
) -> None:
    with pytest.raises(ValueError, match="transport_principal_forbidden_identity_fallback"):
        build_transport_principal_context(
            credential_kind="transport_credential",
            credential_material=credential_material,
            handshake_nonce="nonce",
            issued_epoch=1,
            expires_epoch=3,
            current_epoch=2,
        )


def test_phase_1267_public_p2p_and_non_loopback_flags_fail_closed() -> None:
    with pytest.raises(ValueError, match=TRANSPORT_PRINCIPAL_NOT_PUBLIC_P2P_TOKEN):
        build_transport_principal_context(
            credential_kind="transport_credential",
            credential_material="credential",
            handshake_nonce="nonce",
            issued_epoch=1,
            expires_epoch=3,
            current_epoch=2,
            public_p2p_enabled=True,
        )

    with pytest.raises(ValueError, match=NON_LOOPBACK_PROJECTION_STILL_BLOCKED_TOKEN):
        build_transport_principal_context(
            credential_kind="transport_credential",
            credential_material="credential",
            handshake_nonce="nonce",
            issued_epoch=1,
            expires_epoch=3,
            current_epoch=2,
            non_loopback_projection_enabled=True,
        )


def test_phase_1267_validates_epoch_revocation_and_replay_boundaries() -> None:
    context = _context()

    expired_context = dict(context)
    expired_context["current_epoch"] = 13
    with pytest.raises(ValueError, match="transport_principal_epoch_window_invalid"):
        validate_transport_principal_context(expired_context, current_epoch=13)

    with pytest.raises(ValueError, match="transport_principal_revoked"):
        validate_transport_principal_context(
            context,
            current_epoch=11,
            revoked_credential_fingerprints={str(context["credential_fingerprint"])},
        )

    with pytest.raises(ValueError, match="transport_principal_replay_detected"):
        validate_transport_principal_context(
            context,
            current_epoch=11,
            replay_cache={str(context["replay_key"])},
        )


def test_phase_1267_canonical_json_export_is_stable_and_rejects_float_tampering() -> None:
    context = _context()
    exported = export_transport_principal_context_json(context)

    assert exported == json.dumps(
        context,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    assert json.loads(exported) == context

    tampered = dict(context)
    tampered["current_epoch"] = 11.0
    with pytest.raises(ValueError, match="transport_principal_current_epoch_invalid"):
        export_transport_principal_context_json(tampered)


def test_phase_1267_runtime_module_has_no_public_server_or_predictable_identity_sources() -> None:
    source = _read(MODULE_PATH)

    for forbidden in (
        "ThreadingHTTPServer",
        "BaseHTTPRequestHandler",
        "socket",
        "time.time",
        "datetime.now",
        "random.",
        "rate_limit_key=client_ip",
        "effective_key = rate_limit_key if rate_limit_key is not None else requester_id",
    ):
        assert forbidden not in source

    assert "json.dumps(" in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source


def test_phase_1267_docs_status_and_planning_record_required_tokens() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)

    for text in (spec, walkthrough, status, planning):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Window 1265-1272 OPEN / PASS through Phase 1269" in planning
    assert "## Phase 1268" in status
    assert "Phase 1269 - Werner default topology-pressure profile" in status
    assert "phase_1269_werner_default_topology_pressure_profile_next" in status


def test_phase_1267_records_broad_discovery_and_non_claims() -> None:
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
        assert "public P2P" in text
        assert "non-loopback projection" in text
        assert "Graph Node" in text

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    assert "| open |" in cdl087_rows[0]


def test_phase_1267_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_code_added:ilc_core/network/d2d/transport_principal_pre_public_path.py -> transport/identity",
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md -> transport/identity",
        "graph_delta=support_tests_added:tests/test_phase_1267_transport_principal_runtime_identity_pre_public_path.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1267_transport_principal_runtime_identity_pre_public_path_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1267_preserves_phase_1253_forbidden_fallback_token() -> None:
    spec = _read(SPEC_PATH)

    assert REQUESTER_ID_RATE_LIMIT_FALLBACK_FORBIDDEN_TOKEN in spec
    assert "json_requester_id_rate_limit_fallback_forbidden_public_p2p_phase_1253" in spec
    assert "d2d_rate_limiter_key_must_be_authenticated_transport_principal" in spec
