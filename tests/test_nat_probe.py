from __future__ import annotations

import json

import pytest

from ilc_core.network.connectivity_mode import ConnectivityMode
from ilc_core.network.nat_probe import NatProbeEngine, NatProbeError, ProbeObserver
from ilc_core.sidecars.upnp_router_mapping import RouterMappingResult


AGENT_ID = "a" * 96
ROLLBACK_INSTRUCTION = {
    "action": "DeletePortMapping",
    "control_url": "http://192.168.1.1/control",
    "external_port": 50151,
    "protocol": "udp",
    "schema_version": "upnp_router_mapping_sidecar_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1",
    "service_type": "urn:schemas-upnp-org:service:WANIPConnection:1",
}


def test_live_probe_without_observers_is_non_mutating_outbound_only() -> None:
    report = NatProbeEngine().run_probe(probe_epoch=0)

    assert report.connectivity_receipt.mode is ConnectivityMode.OUTBOUND_ONLY
    assert report.firewall_mutation_attempted is False
    assert report.router_mapping is None
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
    assert punched == [("203.0.113.10", 50151, 3.0)]


def test_probe_report_serializes_canonically() -> None:
    report = NatProbeEngine().run_probe(probe_epoch=0)
    encoded = report.to_canonical_json()
    assert encoded.startswith(b'{"connectivity_receipt":')
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
    assert report.connectivity_receipt.mode is ConnectivityMode.OUTBOUND_ONLY
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
            rollback_token="b" * 64,
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
    assert with_mapping.connectivity_receipt.mode is ConnectivityMode.OUTBOUND_ONLY
    assert with_mapping.connectivity_receipt.observed_endpoint is None
    assert "router_mapping_created_external_verification_pending" in with_mapping.warnings
