from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md")
PROMPT_PATH = Path(
    "docs/antigravity_tasks/antigravity_prompt__phase_1253_g8_transport_principal_identity_and_http_downgrade.md"
)
FETCH_PATH = Path("ilc_core/network/d2d/http_fetch_transport_runtime.py")
GOSSIP_PATH = Path("ilc_core/network/d2d/http_gossip_transport_runtime.py")
FETCH_HANDLER_PATH = Path("ilc_core/network/d2d/truth_primitive_fetch_runtime.py")
RUST_NETWORK_PATH = Path("ilc_consensus/src/network.rs")
RUST_NODE_PATH = Path("ilc_consensus/src/node.rs")
SIDECAR_PATH = Path("ilc_core/graph/sidecar_query_runtime.py")

REQUIRED_TOKENS = (
    "transport_principal_identity_spec_phase_1253.v0.1",
    "python_http_transport_devnet_test_downgrade_plan_phase_1253",
    "json_requester_id_rate_limit_fallback_forbidden_public_p2p_phase_1253",
    "phase_1253_transport_digest_and_rust_m5_disposition_recorded",
    "phase_1253_transport_principal_spec_complete",
)

CANON_TOKENS = (
    "transport_principal_identity_required_before_public_p2p",
    "d2d_rate_limiter_key_must_be_authenticated_transport_principal",
    "agent_id_must_not_be_default_transport_rate_limit_key",
    "json_requester_id_rate_limit_fallback_forbidden_public_p2p",
    "transport_principal_cdl_required_before_runtime_implementation",
    "transport_principal_lifecycle_and_revocation_spec_required",
    "sidecar_projection_endpoint_public_path_requires_transport_principal_auth",
)

PHASE_1250_FIX1_FINDINGS = (
    "RCGAP-1250-FIX1-004",
    "RCGAP-1250-FIX1-005",
    "RCGAP-1250-FIX1-008",
)


def _spec_text() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def test_phase_1253_spec_contains_required_tokens_and_identity_invariants() -> None:
    text = _spec_text()

    for token in REQUIRED_TOKENS + CANON_TOKENS:
        assert token in text

    assert "TransportPrincipal is the missing L3 transport identity layer" in text
    assert "distinct from permanent AgentID" in text
    assert "BLS consensus/economic keys" in text
    assert "OpenClaw/NemoClaw harness identity" in text


def test_phase_1253_prompt_reads_current_transport_paths_not_stale_paths() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")

    assert "ilc_core/network/d2d/http_fetch_transport_runtime.py" in text
    assert "ilc_core/network/d2d/http_gossip_transport_runtime.py" in text
    assert "ilc_core/transport/http_fetch_transport_runtime.py" not in text
    assert "ilc_core/transport/http_gossip_transport_runtime.py" not in text


def test_spec_formally_downgrades_python_http_to_devnet_test_only() -> None:
    text = _spec_text()

    assert str(FETCH_PATH) in text
    assert str(GOSSIP_PATH) in text
    assert "formally classified as devnet/test harnesses" in text
    assert "Do not claim them as public-internet-facing P2P substrate" in text
    assert "Do not bind them beyond loopback or private harness networks" in text
    assert "Keep the modules intact" in text


def test_fetch_http_uses_client_ip_for_http_rate_limit_but_spec_forbids_public_fallback() -> None:
    fetch_source = FETCH_PATH.read_text(encoding="utf-8")
    handler_source = FETCH_HANDLER_PATH.read_text(encoding="utf-8")
    spec = _spec_text()

    assert "client_ip = self.client_address[0]" in fetch_source
    assert "rate_limit_key=client_ip" in fetch_source
    assert "effective_key = rate_limit_key if rate_limit_key is not None else requester_id" in handler_source
    assert "The direct-call fallback to body `requester_id` remains a" in spec
    assert "forbidden for public P2P" in spec


def test_rust_quic_substrate_and_m5_gap_are_recorded() -> None:
    network_source = RUST_NETWORK_PATH.read_text(encoding="utf-8")
    node_source = RUST_NODE_PATH.read_text(encoding="utf-8")
    spec = _spec_text()

    assert "use quinn::" in network_source
    assert "impl rustls::client::danger::ServerCertVerifier" in network_source
    assert "impl rustls::server::danger::ClientCertVerifier" in network_source
    assert "pub const IO_TIMEOUT_MS" in network_source
    assert "FIXME(M-5)" in node_source
    assert "ilc_consensus/src/node.rs:636" in spec
    assert "dynamic-membership/public-P2P substrate confidence gap" in spec
    assert "rust_p2p_substrate_decision_adr_required_quinn_vs_libp2p" in spec


def test_phase_1250_fix1_transport_findings_are_dispositioned() -> None:
    text = _spec_text()

    for finding in PHASE_1250_FIX1_FINDINGS:
        assert finding in text

    for candidate in (
        "ilc_core/network/d2d/gossip.py:181",
        "ilc_core/network/d2d/spectral_beacon.py:207",
        "ilc_core/network/star_map/star_map_route_index_runtime.py:120",
        "ilc_consensus/src/node.rs:636",
    ):
        assert candidate in text

    assert "No public security, ban, revocation, or admission decision may depend on the truncated tag" in text
    assert "must not become the public transport rate-limit key or peer-ban key" in text
    assert "not transport auth, settlement proof, or security root" in text


def test_sidecar_public_path_remains_transportprincipal_gated() -> None:
    sidecar_source = SIDECAR_PATH.read_text(encoding="utf-8")
    spec = _spec_text()

    assert "allow_nan=False" in sidecar_source
    assert "sort_keys=True" in sidecar_source
    assert "sidecar_export_float_values_forbidden" in sidecar_source
    assert "sidecar_export_size_exceeded" in sidecar_source
    assert "Phase 1253 does not add a sidecar HTTP server or projection endpoint" in spec
    assert "TransportPrincipal authentication" in spec


def test_phase_1253_spec_preserves_non_activation_boundary() -> None:
    text = _spec_text()

    for phrase in (
        "does not activate TransportPrincipal runtime",
        "public P2P",
        "public sidecar/projection serving",
        "public claimability",
        "CDL mutation",
        "v0.2 signing",
        "production `commit.epoch` emission",
    ):
        assert phrase in text
