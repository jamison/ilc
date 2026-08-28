from __future__ import annotations

import json

import pytest

from ilc_core.network.connectivity_mode import ProbeResult
from ilc_core.sidecars.upnp_router_mapping import (
    RouterMappingError,
    RouterMappingRequest,
    RouterMappingResult,
    _reject_xml_entities,
    _require_local_http_url,
    attempt_router_mapping_via_sidecar,
    upnp_router_mapping_sidecar_manifest,
)


PROBE = ProbeResult(
    has_public_ip=False,
    observed_ip=None,
    observed_port=None,
    relay_available=False,
    validator_participation_enabled=False,
    has_outbound_connectivity=True,
)


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def attempt_pcp(self, request: RouterMappingRequest) -> RouterMappingResult:
        self.calls.append("pcp")
        return RouterMappingResult(
            success=False,
            method_used="pcp",
            external_port=None,
            lease_seconds=request.lease_seconds,
            rollback_token=None,
            firewall_mutation_attempted=False,
            error="pcp_unavailable",
        )

    def attempt_nat_pmp(self, request: RouterMappingRequest) -> RouterMappingResult:
        self.calls.append("nat_pmp")
        return RouterMappingResult(
            success=True,
            method_used="nat_pmp",
            external_port=request.requested_external_port,
            lease_seconds=request.lease_seconds,
            rollback_token="c" * 64,
            firewall_mutation_attempted=True,
        )

    def attempt_upnp_igd(self, request: RouterMappingRequest) -> RouterMappingResult:
        self.calls.append("upnp_igd")
        raise AssertionError("UPnP should not be called after NAT-PMP success")


def test_sidecar_requires_explicit_opt_in() -> None:
    result = attempt_router_mapping_via_sidecar(PROBE)
    assert result.success is False
    assert result.firewall_mutation_attempted is False
    assert result.error == "explicit_router_mapping_opt_in_required"


def test_sidecar_attempts_methods_in_order_until_success() -> None:
    transport = FakeTransport()
    request = RouterMappingRequest(
        internal_port=50151,
        requested_external_port=50151,
        explicit_opt_in=True,
    )
    result = attempt_router_mapping_via_sidecar(
        PROBE,
        request=request,
        transport=transport,
    )

    assert result.success is True
    assert result.method_used == "nat_pmp"
    assert result.external_port == 50151
    assert result.firewall_mutation_attempted is True
    assert transport.calls == ["pcp", "nat_pmp"]


def test_request_validates_port_lease_method_and_timeout() -> None:
    with pytest.raises(RouterMappingError, match="internal_port_out_of_range"):
        RouterMappingRequest(internal_port=80, explicit_opt_in=True)
    with pytest.raises(RouterMappingError, match="router_mapping_lease_out_of_range"):
        RouterMappingRequest(internal_port=50151, lease_seconds=3601, explicit_opt_in=True)
    with pytest.raises(RouterMappingError, match="router_mapping_method_invalid"):
        RouterMappingRequest(
            internal_port=50151,
            methods=("third_party_stun",),
            explicit_opt_in=True,
        )
    with pytest.raises(RouterMappingError, match="router_mapping_timeout_out_of_range"):
        RouterMappingRequest(internal_port=50151, timeout_seconds=11, explicit_opt_in=True)


def test_result_serializes_canonically() -> None:
    result = RouterMappingResult(
        success=True,
        method_used="upnp_igd",
        external_port=50151,
        lease_seconds=3600,
        rollback_token="d" * 64,
        firewall_mutation_attempted=True,
    )
    encoded = result.to_canonical_json()
    assert encoded.startswith(b'{"error":')
    decoded = json.loads(encoded)
    assert decoded["schema_version"] == (
        "upnp_router_mapping_sidecar_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1"
    )


def test_manifest_is_deterministic_and_non_authorizing() -> None:
    manifest = upnp_router_mapping_sidecar_manifest()
    assert manifest["sidecar_id"] == "upnp-router-mapping"
    assert manifest["authority_gate"] == "explicit opt-in only via attempt_router_mapping=True"
    assert manifest["no_import_time_router_mutation"] is True
    assert json.dumps(manifest, sort_keys=True, separators=(",", ":"))


def test_upnp_location_rejects_global_hosts_and_xml_entities() -> None:
    with pytest.raises(RouterMappingError, match="upnp_location_global_host_forbidden"):
        _require_local_http_url("http://8.8.8.8/rootDesc.xml")
    with pytest.raises(RouterMappingError, match="upnp_description_xml_entity_forbidden"):
        _reject_xml_entities(b'<!DOCTYPE foo [<!ENTITY x "y">]><root />')
