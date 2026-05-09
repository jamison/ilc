from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1261_sidecar_projection_endpoint_boundary_walkthrough.md"
)
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SIDECAR_RUNTIME_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")
PROJECTION_RUNTIME_PATH = Path("ilc_core/graph/agent_graph_projection_runtime.py")
PACKAGE_PROFILES_PATH = Path("ilc_core/rc/package_profiles.py")
TRANSPORT_PRINCIPAL_SPEC_PATH = Path(
    "docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md"
)


REQUIRED_TOKENS = (
    "sidecar_projection_endpoint_boundary_phase_1261.v0.1",
    "sidecar_projection_endpoint_not_publicly_exposed_phase_1261",
    "sidecar_public_path_requires_cdl087_and_transport_principal_phase_1261",
    "transport_principal_policy_gate_rechecked_phase_1261",
)

TRANSPORT_GATE_TOKENS = (
    "transport_principal_identity_required_before_public_p2p",
    "d2d_rate_limiter_key_must_be_authenticated_transport_principal",
    "agent_id_must_not_be_default_transport_rate_limit_key",
    "json_requester_id_rate_limit_fallback_forbidden_public_p2p",
    "transport_principal_cdl_required_before_runtime_implementation",
    "transport_principal_lifecycle_and_revocation_spec_required",
    "sidecar_projection_endpoint_public_path_requires_transport_principal_auth",
)


def _spec_text() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def test_phase_1261_spec_records_required_tokens_and_blocked_verdict() -> None:
    text = _spec_text()

    for token in REQUIRED_TOKENS:
        assert token in text

    assert (
        "sidecar_projection_endpoint_authorization_verdict_phase_1261=blocked_public_path"
        in text
    )
    assert "No HTTP server, socket listener, non-loopback bind" in text
    assert "No sidecar projection endpoint is publicly exposed" in text


def test_cdl087_gate_recheck_records_historical_no_ratification_before_fix1() -> None:
    spec = _spec_text()
    register = CDL_REGISTER_PATH.read_text(encoding="utf-8")

    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "ratified_phase: 1278 Fix1" in register
    assert "no_cdl_087_ratification_phase_1260" in spec
    assert (
        "cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review"
        in spec
    )
    assert "not ratification" in spec
    assert "the CDL-087 prerequisite for public sidecar/projection serving is not satisfied" in spec


def test_transportprincipal_public_path_gate_is_rechecked_without_runtime_activation() -> None:
    spec = _spec_text()
    transport_spec = TRANSPORT_PRINCIPAL_SPEC_PATH.read_text(encoding="utf-8")

    for token in TRANSPORT_GATE_TOKENS:
        assert token in spec
        assert token in transport_spec

    assert "TransportPrincipal runtime implementation" in spec
    assert "JSON/body `requester_id`" in spec
    assert "`client_ip` remains a devnet or local abuse-damping fallback only" in spec
    assert "OpenClaw or NemoClaw harness identity must not become" in spec


def test_current_sidecar_runtime_remains_local_bounded_and_not_a_server() -> None:
    sidecar = SIDECAR_RUNTIME_PATH.read_text(encoding="utf-8")
    projection = PROJECTION_RUNTIME_PATH.read_text(encoding="utf-8")
    package_profiles = PACKAGE_PROFILES_PATH.read_text(encoding="utf-8")

    assert "sort_keys=True" in sidecar
    assert "allow_nan=False" in sidecar
    assert "sidecar_export_float_values_forbidden" in sidecar
    assert "DEFAULT_SIDECAR_EXPORT_MAX_BYTES" in sidecar
    assert "DEFAULT_SIDECAR_EXPORT_MAX_RESULTS" in sidecar
    assert "sort_keys=True" in projection
    assert "allow_nan=False" in projection
    assert "PROFILE_LOCAL_SIDECAR_DAEMON" in package_profiles
    assert "Loopback-only sidecar profile" in package_profiles
    assert "no public sidecar endpoint claim" in package_profiles

    forbidden_server_terms = (
        "ThreadingHTTPServer",
        "HTTPServer",
        "socket.bind",
        "requests.",
        "aiohttp",
    )
    for term in forbidden_server_terms:
        assert term not in sidecar


def test_phase_1261_planning_status_and_walkthrough_are_backfilled() -> None:
    planning = PLANNING_INDEX_PATH.read_text(encoding="utf-8")
    status = STATUS_PATH.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH_PATH.read_text(encoding="utf-8")

    for text in (planning, status, walkthrough):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Phase 1262" in planning
    assert "Phase 1262" in status
    assert "graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_projection_endpoint_boundary_1261_v0.1.md -> transport/public_rc" in status
