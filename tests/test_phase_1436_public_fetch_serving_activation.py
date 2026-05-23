"""Regression tests for Phase 1436 public fetch/sidecar activation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.graph.agent_graph_projection_runtime import (
    export_projection_json_for_public_path,
    project_graph,
)
from ilc_core.graph.sidecar_query_runtime import export_sidecar_query_json_for_public_path
from ilc_core.network.d2d.http_fetch_transport_runtime import (
    FetchTransportConfig,
    HttpFetchTransportRuntime,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.sidecars.public_path_activation import (
    ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
    GAP_14_COMPLETE_GATE_WIRED_TOKEN,
    NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED_TOKEN,
    OPENCLAW_P2P_NOT_ACTIVATED_TOKEN,
    PUBLIC_FETCH_SERVING_ACTIVATED_TOKEN,
    PUBLIC_PATH_ACTIVATION_VERSION,
    TRANSPORT_PRINCIPAL_CDL_RATIFIED_GATE_WIRED_TOKEN,
    authorize_non_loopback_sidecar_projection,
    authorize_public_fetch_serving,
    export_public_path_activation_decision_json,
    public_path_activation_manifest,
    validate_public_path_activation_decision,
)


def _transport_context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="mtls_certificate_fingerprint",
        credential_material="phase-1436-credential",
        handshake_nonce="phase-1436-nonce",
        issued_epoch=10,
        expires_epoch=20,
        current_epoch=12,
    )


def test_phase_1436_activation_manifest_tokens_and_non_claims() -> None:
    manifest = public_path_activation_manifest()
    tokens = set(manifest["tokens"])

    assert manifest["version"] == PUBLIC_PATH_ACTIVATION_VERSION
    assert NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED_TOKEN in tokens
    assert PUBLIC_FETCH_SERVING_ACTIVATED_TOKEN in tokens
    assert TRANSPORT_PRINCIPAL_CDL_RATIFIED_GATE_WIRED_TOKEN in tokens
    assert GAP_14_COMPLETE_GATE_WIRED_TOKEN in tokens
    assert OPENCLAW_P2P_NOT_ACTIVATED_TOKEN in tokens
    assert ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN in tokens
    assert EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN in tokens
    assert manifest["public_fetch_serving_activated"] is True
    assert manifest["non_loopback_sidecar_projection_activated"] is True
    assert manifest["openclaw_p2p_activated"] is False
    assert manifest["public_p2p_activated"] is False
    assert manifest["ecu_distribution_activated"] is False
    assert manifest["epoch_transition_triggered"] is False


def test_public_fetch_activation_requires_transport_principal_rate_key() -> None:
    context = _transport_context()
    decision = authorize_public_fetch_serving(
        bind_host="0.0.0.0",
        transport_principal_context=context,
        current_epoch=12,
    )

    assert decision["public_fetch_serving_enabled"] is True
    assert decision["non_loopback_sidecar_projection_enabled"] is False
    assert decision["rate_limit_identity_source"] == "authenticated_transport_principal"
    assert decision["rate_limit_key"] == context["rate_limit_key"]
    assert decision["requester_id_fallback_allowed"] is False
    assert validate_public_path_activation_decision(
        decision,
        current_epoch=12,
        surface="public_fetch",
    ) == decision


def test_sidecar_projection_activation_requires_non_loopback_bind() -> None:
    decision = authorize_non_loopback_sidecar_projection(
        bind_host="203.0.113.10",
        transport_principal_context=_transport_context(),
        current_epoch=12,
    )

    assert decision["non_loopback_sidecar_projection_enabled"] is True
    assert decision["public_fetch_serving_enabled"] is False
    assert decision["non_loopback_bind"] is True
    assert validate_public_path_activation_decision(
        decision,
        current_epoch=12,
        surface="sidecar_projection",
    ) == decision


def test_public_activation_rejects_loopback_bind() -> None:
    with pytest.raises(ValueError, match="public_path_non_loopback_bind_required_phase_1436"):
        authorize_public_fetch_serving(
            bind_host="127.0.0.1",
            transport_principal_context=_transport_context(),
            current_epoch=12,
        )


def test_public_activation_rejects_missing_principal_context() -> None:
    with pytest.raises(ValueError, match="transport_principal_context_version_invalid"):
        authorize_public_fetch_serving(
            bind_host="0.0.0.0",
            transport_principal_context={},
            current_epoch=12,
        )


def test_public_activation_rejects_rate_limit_over_ceiling() -> None:
    context = _transport_context()

    with pytest.raises(ValueError, match="public_path_rate_limit_exceeded_phase_1436"):
        authorize_public_fetch_serving(
            bind_host="0.0.0.0",
            transport_principal_context=context,
            current_epoch=12,
            rate_limit_counters={str(context["rate_limit_key"]): 1},
            rate_limit_ceiling=1,
        )


def test_activation_decision_exports_canonical_json() -> None:
    decision = authorize_public_fetch_serving(
        bind_host="0.0.0.0",
        transport_principal_context=_transport_context(),
        current_epoch=12,
    )

    payload = export_public_path_activation_decision_json(decision)
    decoded = json.loads(payload)

    assert decoded == decision
    assert payload == json.dumps(decoded, allow_nan=False, separators=(",", ":"), sort_keys=True)


def test_fetch_runtime_non_loopback_requires_public_flag() -> None:
    runtime = HttpFetchTransportRuntime(
        FetchTransportConfig(bind_host="0.0.0.0", rate_limit_window_id=12)
    )

    with pytest.raises(ValueError, match="public_fetch_serving_flag_required"):
        runtime._configure_public_fetch_activation()


def test_fetch_runtime_public_non_loopback_requires_principal_context() -> None:
    runtime = HttpFetchTransportRuntime(
        FetchTransportConfig(
            bind_host="0.0.0.0",
            public_fetch_serving_enabled=True,
            rate_limit_window_id=12,
        )
    )

    with pytest.raises(ValueError, match="public_fetch_transport_principal_context_required"):
        runtime._configure_public_fetch_activation()


def test_fetch_runtime_public_non_loopback_uses_transport_principal_key() -> None:
    context = _transport_context()
    runtime = HttpFetchTransportRuntime(
        FetchTransportConfig(
            bind_host="0.0.0.0",
            public_fetch_serving_enabled=True,
            rate_limit_window_id=12,
            transport_principal_context=context,
        )
    )

    runtime._configure_public_fetch_activation()

    assert runtime.state["public_fetch_serving_enabled"] is True
    assert runtime.state["non_loopback_bind"] is True
    assert runtime.state["rate_limit_identity_source"] == "authenticated_transport_principal"
    assert runtime.state["transport_principal_rate_limit_key"] == context["rate_limit_key"]


def test_fetch_runtime_loopback_default_remains_local_only() -> None:
    runtime = HttpFetchTransportRuntime(FetchTransportConfig(bind_host="127.0.0.1"))

    runtime._configure_public_fetch_activation()

    assert runtime.state["public_fetch_serving_enabled"] is False
    assert runtime.state["non_loopback_bind"] is False
    assert runtime._public_fetch_rate_limit_key is None


def test_projection_public_export_requires_sidecar_activation_decision() -> None:
    projection = project_graph(
        projection_type="authority_graph",
        nodes=({"id": "genesis:root"},),
        edges=(),
    )
    decision = authorize_non_loopback_sidecar_projection(
        bind_host="0.0.0.0",
        transport_principal_context=_transport_context(),
        current_epoch=12,
    )

    payload = export_projection_json_for_public_path(
        projection,
        activation_decision=decision,
        current_epoch=12,
    )

    assert json.loads(payload)["metadata"]["projection_type"] == "authority_graph"


def test_sidecar_public_export_requires_sidecar_activation_decision() -> None:
    decision = authorize_non_loopback_sidecar_projection(
        bind_host="0.0.0.0",
        transport_principal_context=_transport_context(),
        current_epoch=12,
    )

    payload = export_sidecar_query_json_for_public_path(
        {"query_type": "ego_graph", "nodes": ["genesis:root"]},
        activation_decision=decision,
        current_epoch=12,
    )

    assert json.loads(payload)["query_type"] == "ego_graph"


def test_public_fetch_decision_rejected_for_sidecar_export() -> None:
    decision = authorize_public_fetch_serving(
        bind_host="0.0.0.0",
        transport_principal_context=_transport_context(),
        current_epoch=12,
    )

    with pytest.raises(ValueError, match="public_path_activation_surface_mismatch"):
        export_sidecar_query_json_for_public_path(
            {"query_type": "ego_graph"},
            activation_decision=decision,
            current_epoch=12,
        )


def test_phase_1436_prompt_tokens_present_in_source() -> None:
    source_paths = (
        Path("ilc_core/sidecars/public_path_activation.py"),
        Path("ilc_core/network/d2d/http_fetch_transport_runtime.py"),
        Path("ilc_core/graph/sidecar_query_runtime.py"),
        Path("ilc_core/graph/agent_graph_projection_runtime.py"),
    )
    text = "\n".join(path.read_text() for path in source_paths)

    for token in (
        NON_LOOPBACK_SIDECAR_PROJECTION_ACTIVATED_TOKEN,
        PUBLIC_FETCH_SERVING_ACTIVATED_TOKEN,
        TRANSPORT_PRINCIPAL_CDL_RATIFIED_GATE_WIRED_TOKEN,
        GAP_14_COMPLETE_GATE_WIRED_TOKEN,
        OPENCLAW_P2P_NOT_ACTIVATED_TOKEN,
        ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
        EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
    ):
        assert token in text
