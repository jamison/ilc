from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from ilc_core.network.connectivity_mode import ConnectivityMode
from ilc_core.network.nat_probe import NatProbeEngine, NatProbeError, ProbeObserver
from ilc_core.sidecars.upnp_router_mapping import (
    RouterMappingResult,
    _rollback_token_from_fields,
)


AGENT_ID = "a" * 96
ROLLBACK_INSTRUCTION = {
    "action": "DeletePortMapping",
    "control_url": "http://192.168.1.1/control",
    "external_port": 50151,
    "internal_client": "192.168.1.20",
    "internal_port": 50151,
    "lease_seconds": 3600,
    "method_used": "upnp_igd",
    "protocol": "udp",
    "schema_version": "upnp_router_mapping_sidecar_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1",
    "service_type": "urn:schemas-upnp-org:service:WANIPConnection:1",
}


def _rollback_token() -> str:
    return _rollback_token_from_fields(
        method=ROLLBACK_INSTRUCTION["method_used"],
        internal_port=ROLLBACK_INSTRUCTION["internal_port"],
        external_port=ROLLBACK_INSTRUCTION["external_port"],
        lease_seconds=ROLLBACK_INSTRUCTION["lease_seconds"],
        protocol=ROLLBACK_INSTRUCTION["protocol"],
        rollback_instruction=ROLLBACK_INSTRUCTION,
    )


def test_live_probe_without_observers_is_non_mutating_local_only() -> None:
    report = NatProbeEngine().run_probe(probe_epoch=0)

    assert report.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert report.probe_result.has_outbound_connectivity is False
    assert report.firewall_mutation_attempted is False
    assert report.router_mapping is None
    assert report.attempt_receipts[0].result == "skipped_no_opt_in"
    assert "no_ilc_probe_observer_configured" in report.warnings


def test_loopback_observer_detects_direct_public_without_external_network() -> None:
    def fetcher(url: str, timeout_seconds: float) -> dict[str, object]:
        assert url == "http://127.0.0.1:9999/probe"
        assert timeout_seconds == 3.0
        return {
            "observed_ip": "203.0.113.10",
            "observed_port": 50151,
            "observer_agent_id": AGENT_ID,
        }

    punched: list[tuple[str, int, float]] = []
    engine = NatProbeEngine(
        observers=(ProbeObserver("http://127.0.0.1:9999/probe"),),
        observer_fetcher=fetcher,
        hole_puncher=lambda host, port, timeout: punched.append((host, port, timeout))
        is None,
    )
    report = engine.run_probe(probe_epoch=12)

    assert report.connectivity_receipt.mode is ConnectivityMode.DIRECT_PUBLIC
    assert report.connectivity_receipt.observed_endpoint == "203.0.113.10:50151"
    assert report.connectivity_receipt.probe_observer_agent_id == AGENT_ID
    assert report.connectivity_receipt.probe_epoch == 12
    assert report.firewall_mutation_attempted is False
    assert report.attempt_receipts[0].external_endpoint == "203.0.113.10:50151"
    assert punched == [("203.0.113.10", 50151, 3.0)]


def test_probe_report_serializes_canonically() -> None:
    report = NatProbeEngine().run_probe(probe_epoch=0)
    encoded = report.to_canonical_json()
    assert encoded.startswith(b'{"attempt_receipts":')
    assert json.loads(encoded)["schema_version"] == (
        "nat_probe_engine_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1"
    )


def test_observer_response_size_and_shape_are_guarded() -> None:
    with pytest.raises(NatProbeError, match="probe_observer_must_be_ilc_https"):
        NatProbeEngine(observers=("http://example.com/probe",))

    engine = NatProbeEngine(
        observers=("http://127.0.0.1:9999/probe",),
        observer_fetcher=lambda *_: {"observed_ip": "not-ip", "observed_port": 50151},
    )
    report = engine.run_probe(probe_epoch=0)
    assert report.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert any("probe_observer_failed" in warning for warning in report.warnings)


def test_router_mapping_called_only_when_requested(monkeypatch) -> None:
    calls: list[bool] = []

    def fake_mapping(_probe_result, *, request):
        calls.append(request.explicit_opt_in)
        return RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=50151,
            lease_seconds=3600,
            rollback_token=_rollback_token(),
            internal_port=50151,
            protocol="udp",
            firewall_mutation_attempted=True,
            rollback_instruction=ROLLBACK_INSTRUCTION,
        )

    monkeypatch.setattr(
        "ilc_core.sidecars.upnp_router_mapping.attempt_router_mapping_via_sidecar",
        fake_mapping,
    )

    no_mapping = NatProbeEngine().run_probe(probe_epoch=0)
    assert no_mapping.router_mapping is None
    assert calls == []

    with_mapping = NatProbeEngine().run_probe(
        attempt_router_mapping=True,
        probe_epoch=0,
    )
    assert calls == [True]
    assert with_mapping.firewall_mutation_attempted is True
    assert with_mapping.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert with_mapping.connectivity_receipt.observed_endpoint is None
    assert with_mapping.attempt_receipts[0].method == "upnp_igd"
    assert with_mapping.attempt_receipts[0].firewall_mutation_attempted is True
    assert "router_mapping_created_external_verification_pending" in with_mapping.warnings


def test_relay_admission_material_cli_shape_does_not_duplicate_client_kwargs(
    monkeypatch,
) -> None:
    from ilc_core.network.relay import relay_client as relay_module

    monkeypatch.setattr(relay_module, "RELAY_CLIENT_NOT_ACTIVATED", False)
    captured: dict[str, object] = {}

    class FakeRelayClient:
        def __init__(self, **kwargs: object) -> None:
            captured["kwargs"] = kwargs

        def request_slot(
            self,
            *,
            admission_epoch: int,
            relay_admission_signature: str | None,
        ) -> object:
            captured["admission_epoch"] = admission_epoch
            captured["relay_admission_signature"] = relay_admission_signature
            return SimpleNamespace(
                relay_endpoint=SimpleNamespace(
                    as_host_port=lambda: "relay.example:52000",
                ),
            )

    engine = NatProbeEngine(
        relay_server_url="https://relay.example:51151",
        relay_admission_material={
            "admission_epoch": 0,
            "agent_id": AGENT_ID,
            "invite_id": "invite-1",
            "invite_nullifier": "b" * 64,
            "invite_pop": "c" * 192,
            "invite_pop_epoch": 0,
            "network_id": "public-rc",
            "relay_admission_payload_ref": "d" * 96,
            "relay_admission_signature": "e" * 192,
            "relay_base_url": "https://relay.example:51151",
            "requested_internal_port": 50151,
            "requested_protocol": "quic",
            "software_version": "0.4.10",
            "tls_cert_der_sha256": "f" * 64,
        },
        relay_client_factory=FakeRelayClient,
    )

    report = engine.run_probe(probe_epoch=0)

    assert report.connectivity_receipt.mode is ConnectivityMode.RELAY_REACHABLE
    assert report.connectivity_receipt.relay_endpoint == "relay.example:52000"
    assert captured["admission_epoch"] == 0
    assert captured["relay_admission_signature"] == "e" * 192
    assert captured["kwargs"] == {
        "agent_id": AGENT_ID,
        "invite_id": "invite-1",
        "invite_nullifier": "b" * 64,
        "invite_pop": "c" * 192,
        "invite_pop_epoch": 0,
        "network_id": "public-rc",
        "relay_base_url": "https://relay.example:51151",
        "requested_internal_port": 50151,
        "software_version": "0.4.10",
        "timeout_seconds": 3.0,
        "tls_cert_der_sha256": "f" * 64,
    }


def test_relay_admission_material_base_url_mismatch_fails_closed(monkeypatch) -> None:
    from ilc_core.network.relay import relay_client as relay_module

    monkeypatch.setattr(relay_module, "RELAY_CLIENT_NOT_ACTIVATED", False)

    engine = NatProbeEngine(
        relay_server_url="https://relay.example:51151",
        relay_admission_material={
            "agent_id": AGENT_ID,
            "invite_id": "invite-1",
            "invite_nullifier": "b" * 64,
            "invite_pop": "c" * 192,
            "invite_pop_epoch": 0,
            "relay_base_url": "https://other-relay.example:51151",
        },
    )

    report = engine.run_probe(probe_epoch=0)

    assert report.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert "relay_slot_request_failed:RelayClientError" in report.warnings
