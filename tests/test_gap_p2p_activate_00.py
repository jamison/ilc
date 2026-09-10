from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from ilc_core.network.d2d import http_fetch_transport_runtime
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.http_fetch_transport_runtime import (
    FetchTransportConfig,
    HttpFetchTransportRuntime,
)
from ilc_core.network.d2d.transport_principal_cdl_094_status import (
    NON_LOOPBACK_SIDECAR_PROJECTION_ENABLED,
    PUBLIC_FETCH_SERVING_ENABLED,
    PUBLIC_P2P_ENABLED,
    transport_principal_cdl_094_opening_status,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.network.rust_p2p_bridge import (
    CDL_094_ADMISSION_WIRE_NOT_ACTIVATED,
    RUST_P2P_BRIDGE_NOT_ACTIVATED,
    RustP2PBridge,
)
from ilc_core.sidecars.connectivity_advertisement import (
    CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED,
)
from ilc_core.sidecars.public_path_activation import (
    NATIVE_RUST_P2P_ACTIVATED_TOKEN,
    PUBLIC_P2P_ACTIVATED,
    public_path_activation_manifest,
)
from ilc_core.validator.validator_admission_ejection_production_path import (
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
)


def _transport_context(
    *,
    material: str = "gap-p2p-activate-credential",
    nonce: str = "gap-p2p-activate-nonce",
    epoch: int = 9,
) -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="mtls_certificate_fingerprint",
        credential_material=material,
        handshake_nonce=nonce,
        issued_epoch=epoch,
        expires_epoch=epoch + 10,
        current_epoch=epoch,
    )


def test_gap_p2p_activate_guard_states_are_exact() -> None:
    assert PUBLIC_P2P_ENABLED is True
    assert PUBLIC_FETCH_SERVING_ENABLED is True
    assert NON_LOOPBACK_SIDECAR_PROJECTION_ENABLED is True
    assert RUST_P2P_BRIDGE_NOT_ACTIVATED is False
    assert CDL_094_ADMISSION_WIRE_NOT_ACTIVATED is False
    assert CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED is True
    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True


def test_transport_principal_status_snapshot_reports_public_p2p_enabled() -> None:
    status = transport_principal_cdl_094_opening_status()

    assert status["public_p2p_enabled"] is True
    assert status["public_fetch_serving_enabled"] is True
    assert status["non_loopback_sidecar_projection_enabled"] is True
    assert status["requester_id_fallback_allowed"] is False
    assert status["raw_agent_id_default_rate_limit_key_allowed"] is False
    assert status["client_ip_primary_rate_limit_key_allowed"] is False


def test_public_path_activation_snapshot_reports_native_rust_p2p_enabled() -> None:
    manifest = public_path_activation_manifest()

    assert PUBLIC_P2P_ACTIVATED is True
    assert manifest["public_p2p_activated"] is True
    assert NATIVE_RUST_P2P_ACTIVATED_TOKEN in set(manifest["tokens"])


def test_rust_bridge_active_path_requires_transport_principal_before_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("subprocess must not run without authenticated principal")

    monkeypatch.setattr("ilc_core.network.rust_p2p_bridge.subprocess.run", fake_run)

    with pytest.raises(ValueError, match="cdl_094_principal_not_provided_by_bridge"):
        RustP2PBridge().send_via_rust_p2p("validator-1", b"payload")
    assert calls == []


def test_rust_bridge_active_path_uses_installed_helper_after_admission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = tmp_path / "ilc_p2p_bridge"
    helper.write_text(
        "#!/bin/sh\n"
        "case \"$*\" in *'--request-json'*) exit 0 ;; *) exit 2 ;; esac\n",
        encoding="utf-8",
    )
    helper.chmod(0o700)
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))

    assert RustP2PBridge().send_via_rust_p2p(
        "validator-1",
        b"payload",
        transport_principal_context=_transport_context(),
        current_epoch=9,
    ) is True


def test_rust_bridge_rejects_requester_id_fallback_before_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []
    context = _transport_context()
    context["requester_id_fallback_allowed"] = True

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("subprocess must not run for requester-id fallback")

    monkeypatch.setattr("ilc_core.network.rust_p2p_bridge.subprocess.run", fake_run)

    with pytest.raises(ValueError, match="requester_id_rate_limit_fallback_still_forbidden"):
        RustP2PBridge().send_via_rust_p2p(
            "validator-1",
            b"payload",
            transport_principal_context=context,
            current_epoch=9,
        )
    assert calls == []


def test_real_loopback_fetch_serving_responds_and_bounds_oversize_request() -> None:
    runtime = HttpFetchTransportRuntime(
        FetchTransportConfig(
            bind_host="127.0.0.1",
            bind_port=0,
            store_path="",
            request_timeout_seconds=2.0,
        )
    )
    runtime.start()
    try:
        port = int(runtime.state["bound_port"])
        body = json.dumps(
            {"node_id": "bafy-gap-p2p-activate", "requester_id": "agent-1"},
            sort_keys=True,
        ).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/fetch/want-have",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            parsed = json.loads(response.read())
        assert parsed == {"have": False, "node_id": "bafy-gap-p2p-activate"}

        oversized = b"x" * (http_fetch_transport_runtime._MAX_INBOUND_BYTES + 1)
        oversized_request = urllib.request.Request(
            f"http://127.0.0.1:{port}/fetch/want-have",
            data=oversized,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(oversized)),
            },
        )
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(oversized_request, timeout=3)
        assert exc_info.value.code == 413
    finally:
        runtime.stop()


def test_connectivity_advertisement_ingestion_remains_guarded() -> None:
    registry = GossipPeerRegistry(())

    with pytest.raises(RuntimeError, match="connectivity_advertisement_not_activated"):
        registry.add_connectivity_advertisement(object(), current_epoch=0)  # type: ignore[arg-type]
