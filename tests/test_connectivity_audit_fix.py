from __future__ import annotations

import socket

import pytest
from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_invite_pop_digest
from ilc_core.identity.first_run_provisioning import invite_pop_payload_ref
from ilc_core.network.connectivity_mode import (
    ConnectivityMode,
    ConnectivityModeValidationError,
    ConnectivityReceipt,
)
from ilc_core.network.nat_probe import (
    CONNECTIVITY_AUDIT_FIX_TOKEN,
    NatProbeEngine,
    NatProbeError,
    NatTraversalAttemptReceipt,
    ProbeObserver,
    _udp_hole_punch_attempt,
)
from ilc_core.network.relay.relay_client import (
    RelayClient,
    RelayClientError,
    RelayEndpoint,
    RelaySlotGrant,
    relay_admission_payload_ref,
)
from ilc_core.sidecars.upnp_router_mapping import (
    UPNP_ROUTER_MAPPING_SIDECAR_VERSION,
    RouterMappingError,
    RouterMappingResult,
    _rollback_token_from_fields,
    build_upnp_rollback_instruction,
)


IKM_HEX = "11" * 32
INVITE_ID = "public-rc-relay-invite-00"
INVITE_NULLIFIER = "22" * 32
AGENT_ID = "a" * 96
ROLLBACK = {
    "action": "DeletePortMapping",
    "control_url": "http://192.168.1.1/control",
    "external_port": 50151,
    "internal_client": "192.168.1.20",
    "internal_port": 50151,
    "lease_seconds": 3600,
    "method_used": "upnp_igd",
    "protocol": "udp",
    "schema_version": UPNP_ROUTER_MAPPING_SIDECAR_VERSION,
    "service_type": "urn:schemas-upnp-org:service:WANIPConnection:1",
}


def _rollback_token(instruction: dict[str, object] = ROLLBACK) -> str:
    return _rollback_token_from_fields(
        method=str(instruction["method_used"]),
        internal_port=int(instruction["internal_port"]),
        external_port=int(instruction["external_port"]),
        lease_seconds=int(instruction["lease_seconds"]),
        protocol=str(instruction["protocol"]),
        rollback_instruction=instruction,
    )


def _pop_material() -> tuple[str, str, str]:
    secret_key, agent_id = keypair_from_ikm_hex(IKM_HEX)
    digest = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=INVITE_NULLIFIER,
        invite_id=INVITE_ID,
        epoch=0,
    )
    return secret_key, agent_id, sign_invite_pop_digest(secret_key, digest)


def _admission_signature(
    secret_key: str,
    agent_id: str,
    *,
    relay_base_url: str,
    admission_epoch: int = 0,
) -> str:
    invite_ref = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=INVITE_NULLIFIER,
        invite_id=INVITE_ID,
        epoch=0,
    )
    admission_ref = relay_admission_payload_ref(
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop_payload_ref_value=invite_ref,
        admission_epoch=admission_epoch,
        network_id="public-rc",
        relay_base_url=relay_base_url,
        requested_internal_port=50151,
        requested_protocol="quic",
        software_version="0.4.4",
    )
    return sign_invite_pop_digest(secret_key, admission_ref)


def _grant(*, agent_id: str, granted_epoch: int = 4) -> RelaySlotGrant:
    return RelaySlotGrant(
        slot_id="slot-0001",
        agent_id=agent_id,
        relay_endpoint=RelayEndpoint(host="relay.example", port=50151),
        granted_epoch=granted_epoch,
        ttl_epochs=4,
        target_internal_port=50151,
        max_bytes_per_epoch=64 * 1024 * 1024,
        max_concurrent_streams=8,
        admission_request_hash="0" * 64,
    )


def test_connectivity_audit_fix_token_present() -> None:
    assert (
        CONNECTIVITY_AUDIT_FIX_TOKEN
        == "connectivity_audit_fix_committed_GAP_CONNECTIVITY_AUDIT_FIX_00"
    )


def test_no_observer_no_relay_does_not_claim_outbound() -> None:
    report = NatProbeEngine().run_probe(probe_epoch=7)
    assert report.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert report.probe_result.has_outbound_connectivity is False


def test_observer_parse_failure_does_not_claim_outbound() -> None:
    engine = NatProbeEngine(
        observers=("http://127.0.0.1:9999/probe",),
        observer_fetcher=lambda *_: {"observed_ip": "bad", "observed_port": 50151},
    )
    report = engine.run_probe(probe_epoch=7)
    assert report.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert report.probe_result.has_outbound_connectivity is False


def test_observer_programmer_type_error_is_not_swallowed() -> None:
    def broken_fetcher(_url: str, _timeout: float) -> dict[str, object]:
        raise TypeError("programming error")

    engine = NatProbeEngine(
        observers=("http://127.0.0.1:9999/probe",),
        observer_fetcher=broken_fetcher,
    )
    with pytest.raises(TypeError, match="programming error"):
        engine.run_probe(probe_epoch=0)


def test_relay_factory_programmer_type_error_is_not_swallowed(monkeypatch) -> None:
    from ilc_core.network.relay import relay_client as relay_module

    monkeypatch.setattr(relay_module, "RELAY_CLIENT_NOT_ACTIVATED", False)

    def broken_factory(**_kwargs: object) -> object:
        raise TypeError("bad relay factory")

    engine = NatProbeEngine(
        relay_server_url="https://relay.example",
        relay_admission_material={"agent_id": AGENT_ID},
        relay_client_factory=broken_factory,
    )
    with pytest.raises(TypeError, match="bad relay factory"):
        engine.run_probe(probe_epoch=0)


def test_ipv6_hole_punch_path_uses_ipv6_socket_family(monkeypatch) -> None:
    created: list[tuple[int, int]] = []
    sent_to: list[tuple[str, int, int, int]] = []

    class FakeSocket:
        def __init__(self, family: int, kind: int) -> None:
            created.append((family, kind))

        def __enter__(self) -> "FakeSocket":
            return self

        def __exit__(self, *_exc: object) -> None:
            return None

        def settimeout(self, _timeout: float) -> None:
            return None

        def sendto(self, _payload: bytes, address: tuple[str, int, int, int]) -> None:
            sent_to.append(address)

    monkeypatch.setattr("ilc_core.network.nat_probe.socket.socket", FakeSocket)

    assert _udp_hole_punch_attempt("2001:db8::1", 50151, 0.01) is False
    assert created == [(socket.AF_INET6, socket.SOCK_DGRAM)]
    assert sent_to == [("2001:db8::1", 50151, 0, 0)]


def test_connectivity_receipt_rejects_endpoint_host_with_slash() -> None:
    with pytest.raises(ConnectivityModeValidationError, match="relay_endpoint_host_invalid"):
        ConnectivityReceipt(
            mode=ConnectivityMode.RELAY_REACHABLE,
            observed_endpoint=None,
            relay_endpoint="relay.example/path:50151",
            probe_observer_agent_id=None,
            probe_epoch=0,
        )


def test_connectivity_receipt_rejects_endpoint_host_with_credentials_marker() -> None:
    with pytest.raises(ConnectivityModeValidationError, match="relay_endpoint_host_invalid"):
        ConnectivityReceipt(
            mode=ConnectivityMode.RELAY_REACHABLE,
            observed_endpoint=None,
            relay_endpoint="user@relay.example:50151",
            probe_observer_agent_id=None,
            probe_epoch=0,
        )


def test_router_success_requires_internal_port_and_protocol() -> None:
    with pytest.raises(RouterMappingError, match="router_mapping_success_internal_port_required"):
        RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=50151,
            lease_seconds=3600,
            rollback_token="b" * 64,
            protocol="udp",
            firewall_mutation_attempted=True,
            rollback_instruction=ROLLBACK,
        )
    with pytest.raises(RouterMappingError, match="router_mapping_success_protocol_required"):
        RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=50151,
            lease_seconds=3600,
            rollback_token="b" * 64,
            internal_port=50151,
            firewall_mutation_attempted=True,
            rollback_instruction=ROLLBACK,
        )


def test_router_rollback_external_port_must_match_result() -> None:
    with pytest.raises(RouterMappingError, match="router_mapping_rollback_instruction_mismatch"):
        RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=50152,
            lease_seconds=3600,
            rollback_token="b" * 64,
            internal_port=50151,
            protocol="udp",
            firewall_mutation_attempted=True,
            rollback_instruction=ROLLBACK,
        )


def test_router_rollback_lease_must_match_result() -> None:
    with pytest.raises(RouterMappingError, match="router_mapping_rollback_instruction_mismatch"):
        RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=50151,
            lease_seconds=1800,
            rollback_token="b" * 64,
            internal_port=50151,
            protocol="udp",
            firewall_mutation_attempted=True,
            rollback_instruction=ROLLBACK,
        )


def test_router_rollback_token_must_match_instruction() -> None:
    with pytest.raises(RouterMappingError, match="router_mapping_rollback_token_mismatch"):
        RouterMappingResult(
            success=True,
            method_used="upnp_igd",
            external_port=50151,
            lease_seconds=3600,
            rollback_token="b" * 64,
            internal_port=50151,
            protocol="udp",
            firewall_mutation_attempted=True,
            rollback_instruction=ROLLBACK,
        )


def test_router_rollback_token_bound_to_instruction_accepts() -> None:
    result = RouterMappingResult(
        success=True,
        method_used="upnp_igd",
        external_port=50151,
        lease_seconds=3600,
        rollback_token=_rollback_token(),
        internal_port=50151,
        protocol="udp",
        firewall_mutation_attempted=True,
        rollback_instruction=ROLLBACK,
    )
    assert result.rollback_token == _rollback_token()


def test_rollback_instruction_records_bound_mapping_fields() -> None:
    assert build_upnp_rollback_instruction(
        control_url="http://192.168.1.1/control",
        internal_client="192.168.1.20",
        internal_port=50151,
        lease_seconds=3600,
        method_used="upnp_igd",
        service_type="urn:schemas-upnp-org:service:WANIPConnection:1",
        external_port=50151,
        protocol="udp",
    ) == ROLLBACK


def test_relay_grant_requires_admission_request_hash() -> None:
    with pytest.raises(RelayClientError, match="relay_admission_request_hash_invalid"):
        RelaySlotGrant(
            slot_id="slot-0001",
            agent_id=AGENT_ID,
            relay_endpoint=RelayEndpoint(host="relay.example", port=50151),
            granted_epoch=0,
            ttl_epochs=4,
            target_internal_port=50151,
            max_bytes_per_epoch=64 * 1024 * 1024,
            max_concurrent_streams=8,
            admission_request_hash=None,
        )


def test_relay_client_rejects_grant_not_bound_to_request_hash() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    relay_base_url = "http://127.0.0.1:9/"
    admission_signature = _admission_signature(
        secret_key,
        agent_id,
        relay_base_url=relay_base_url,
    )

    class BadGrantTransport:
        def post_json(self, _path: str, payload: object, _timeout: float) -> dict[str, object]:
            assert isinstance(payload, dict)
            return {
                "grant": RelaySlotGrant(
                    slot_id="slot-0001",
                    agent_id=agent_id,
                    relay_endpoint=RelayEndpoint(host="relay.example", port=50151),
                    granted_epoch=payload["admission_epoch"],
                    ttl_epochs=4,
                    target_internal_port=payload["requested_internal_port"],
                    max_bytes_per_epoch=64 * 1024 * 1024,
                    max_concurrent_streams=8,
                    admission_request_hash="f" * 64,
                ).to_dict()
            }

    client = RelayClient(
        relay_base_url=relay_base_url,
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        relay_admission_signature=admission_signature,
        software_version="0.4.4",
        transport=BadGrantTransport(),
        allow_guarded_request=True,
    )
    with pytest.raises(RelayClientError, match="relay_grant_admission_request_hash_mismatch"):
        client.request_slot(admission_epoch=0)


def test_relay_lifecycle_rejects_epoch_before_grant() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    admission_signature = _admission_signature(
        secret_key,
        agent_id,
        relay_base_url="http://127.0.0.1:9",
    )
    client = RelayClient(
        relay_base_url="http://127.0.0.1:9",
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        relay_admission_signature=admission_signature,
        software_version="0.4.4",
        allow_guarded_request=True,
    )
    with pytest.raises(RelayClientError, match="relay_lifecycle_epoch_before_grant"):
        client.keepalive(
            slot=_grant(agent_id=agent_id, granted_epoch=4),
            keepalive_epoch=3,
            relay_lifecycle_signature="a" * 192,
        )


def test_nat_attempt_receipt_requires_rollback_for_firewall_mutation() -> None:
    with pytest.raises(NatProbeError, match="firewall_mutation_requires_rollback_instruction"):
        NatTraversalAttemptReceipt(
            agent_id=AGENT_ID,
            attempt_timestamp_epoch=0,
            method="upnp_igd",
            result="success",
            external_endpoint=None,
            internal_port=50151,
            lease_seconds=3600,
            rollback_instruction=None,
            observer_ref=None,
            firewall_mutation_attempted=True,
        )
