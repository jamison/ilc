from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Any

import pytest

from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_invite_pop_digest
from ilc_core.identity.first_run_provisioning import invite_pop_payload_ref
from ilc_core.network.connectivity_mode import ConnectivityMode
from ilc_core.network.nat_probe import NatProbeEngine
from ilc_core.network.relay import relay_client as relay_module
from ilc_core.network.relay.relay_client import (
    RELAY_CLIENT_NOT_ACTIVATED,
    RELAY_CLIENT_SCHEMA_VERSION,
    RelayAdmissionRequest,
    RelayClient,
    RelayClientError,
    RelayEndpoint,
    RelaySlotGrant,
    relay_admission_payload_ref,
    relay_lifecycle_payload_ref,
)


IKM_HEX = "11" * 32
INVITE_ID = "public-rc-relay-invite-00"
INVITE_NULLIFIER = "22" * 32


def _pop_material() -> tuple[str, str, str]:
    secret_key, agent_id = keypair_from_ikm_hex(IKM_HEX)
    digest = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=INVITE_NULLIFIER,
        invite_id=INVITE_ID,
        epoch=0,
    )
    return secret_key, agent_id, sign_invite_pop_digest(secret_key, digest)


def _relay_admission_signature(
    secret_key: str,
    agent_id: str,
    *,
    admission_epoch: int,
    network_id: str = "public-rc",
    relay_base_url: str = "http://127.0.0.1:9",
    requested_internal_port: int = 50151,
    software_version: str | None = None,
) -> tuple[str, str]:
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
        network_id=network_id,
        relay_base_url=relay_base_url,
        requested_internal_port=requested_internal_port,
        requested_protocol="quic",
        software_version=software_version or relay_module.ILC_CORE_VERSION,
    )
    return admission_ref, sign_invite_pop_digest(secret_key, admission_ref)


def _relay_lifecycle_signature(
    secret_key: str,
    agent_id: str,
    *,
    action: str,
    slot: RelaySlotGrant,
    lifecycle_epoch: int,
    network_id: str = "public-rc",
    relay_base_url: str = "http://127.0.0.1:9",
) -> tuple[str, str]:
    payload_ref = relay_lifecycle_payload_ref(
        action=action,
        agent_id=agent_id,
        slot_id=slot.slot_id,
        lifecycle_epoch=lifecycle_epoch,
        previous_grant_hash=slot.canonical_response_hash,
        network_id=network_id,
        relay_base_url=relay_base_url,
    )
    return payload_ref, sign_invite_pop_digest(secret_key, payload_ref)


def test_relay_client_guard_defaults_closed() -> None:
    assert RELAY_CLIENT_NOT_ACTIVATED is True
    secret_key, agent_id, invite_pop = _pop_material()
    _, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=0,
    )
    client = RelayClient(
        relay_base_url="http://127.0.0.1:9",
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        relay_admission_signature=admission_signature,
    )

    with pytest.raises(RelayClientError, match="relay_client_not_activated"):
        client.request_slot(admission_epoch=0)


def test_admission_request_verifies_invite_pop_and_serializes_canonically() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    admission_ref, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=0,
    )
    request = RelayAdmissionRequest(
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        invite_pop_epoch=0,
        admission_epoch=0,
        network_id="public-rc",
        relay_base_url="http://127.0.0.1:9",
        relay_admission_payload_ref=admission_ref,
        relay_admission_signature=admission_signature,
    )

    payload = request.to_dict()
    assert payload["canonical_request_hash"] == request.canonical_request_hash
    assert payload["invite_pop_payload_ref"] == invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=INVITE_NULLIFIER,
        invite_id=INVITE_ID,
        epoch=0,
    )
    assert request.to_canonical_json().startswith(b'{"admission_epoch":0')


def test_admission_request_rejects_wrong_invite_pop_binding() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    wrong_nullifier = "33" * 32
    invite_ref = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=wrong_nullifier,
        invite_id=INVITE_ID,
        epoch=0,
    )
    admission_ref = relay_admission_payload_ref(
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=wrong_nullifier,
        invite_pop_payload_ref_value=invite_ref,
        admission_epoch=0,
        network_id="public-rc",
        relay_base_url="http://127.0.0.1:9",
        requested_internal_port=50151,
        requested_protocol="quic",
        software_version=relay_module.ILC_CORE_VERSION,
    )
    admission_signature = sign_invite_pop_digest(secret_key, admission_ref)

    with pytest.raises(RelayClientError, match="relay_invite_pop_verification_failed"):
        RelayAdmissionRequest(
            agent_id=agent_id,
            invite_id=INVITE_ID,
            invite_nullifier=wrong_nullifier,
            invite_pop=invite_pop,
            invite_pop_epoch=0,
            admission_epoch=0,
            relay_base_url="http://127.0.0.1:9",
            relay_admission_payload_ref=admission_ref,
            relay_admission_signature=admission_signature,
        )


def test_admission_epoch_can_differ_from_invite_pop_epoch() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    admission_ref, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=7,
    )
    request = RelayAdmissionRequest(
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        invite_pop_epoch=0,
        admission_epoch=7,
        relay_base_url="http://127.0.0.1:9",
        relay_admission_payload_ref=admission_ref,
        relay_admission_signature=admission_signature,
    )

    payload = request.to_dict()
    assert payload["admission_epoch"] == 7
    assert payload["invite_pop_epoch"] == 0


def test_admission_request_rejects_stale_relay_signature() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    admission_ref, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=0,
    )

    with pytest.raises(RelayClientError, match="relay_admission_payload_ref_mismatch"):
        RelayAdmissionRequest(
            agent_id=agent_id,
            invite_id=INVITE_ID,
            invite_nullifier=INVITE_NULLIFIER,
            invite_pop=invite_pop,
            invite_pop_epoch=0,
            admission_epoch=1,
            relay_base_url="http://127.0.0.1:9",
            relay_admission_payload_ref=admission_ref,
            relay_admission_signature=admission_signature,
        )


def test_loopback_relay_slot_keepalive_and_release() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    captured: list[dict[str, Any]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers["Content-Length"])
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            captured.append({"path": self.path, "payload": payload})
            if self.path == "/relay/admission/request":
                body = {
                    "grant": RelaySlotGrant(
                        slot_id="slot-0001",
                        agent_id=payload["agent_id"],
                        relay_endpoint=RelayEndpoint(host="relay.local", port=50151),
                        granted_epoch=payload["admission_epoch"],
                        ttl_epochs=4,
                        target_internal_port=payload["requested_internal_port"],
                        max_bytes_per_epoch=64 * 1024 * 1024,
                        max_concurrent_streams=8,
                        admission_request_hash=payload["canonical_request_hash"],
                    ).to_dict()
                }
            elif self.path == "/relay/slot/keepalive":
                body = {"renewal_result": "renewed"}
            elif self.path == "/relay/slot/release":
                body = {"release_result": "released"}
            else:
                self.send_response(404)
                self.end_headers()
                return
            encoded = json.dumps(
                body,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        relay_base_url = f"http://127.0.0.1:{server.server_port}"
        _, admission_signature = _relay_admission_signature(
            secret_key,
            agent_id,
            admission_epoch=0,
            relay_base_url=relay_base_url,
        )
        client = RelayClient(
            relay_base_url=relay_base_url,
            agent_id=agent_id,
            invite_id=INVITE_ID,
            invite_nullifier=INVITE_NULLIFIER,
            invite_pop=invite_pop,
            relay_admission_signature=admission_signature,
            allow_guarded_request=True,
        )
        grant = client.request_slot(admission_epoch=0)
        _, keepalive_signature = _relay_lifecycle_signature(
            secret_key,
            agent_id,
            action="keepalive",
            slot=grant,
            lifecycle_epoch=1,
            relay_base_url=relay_base_url,
        )
        _, release_signature = _relay_lifecycle_signature(
            secret_key,
            agent_id,
            action="release",
            slot=grant,
            lifecycle_epoch=1,
            relay_base_url=relay_base_url,
        )
        keepalive = client.keepalive(
            slot=grant,
            keepalive_epoch=1,
            relay_lifecycle_signature=keepalive_signature,
        )
        release = client.release_slot(
            slot=grant,
            release_epoch=1,
            relay_lifecycle_signature=release_signature,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert grant.relay_endpoint.as_host_port() == "relay.local:50151"
    assert grant.ttl_epochs == 4
    assert keepalive.to_dict()["renewal_result"] == "renewed"
    assert release.to_dict()["release_result"] == "released"
    assert [entry["path"] for entry in captured] == [
        "/relay/admission/request",
        "/relay/slot/keepalive",
        "/relay/slot/release",
    ]
    assert captured[0]["payload"]["schema_version"] == RELAY_CLIENT_SCHEMA_VERSION


def test_grant_rejects_agent_mismatch() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    _, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=0,
    )

    class BadTransport:
        def post_json(self, *_args: object) -> dict[str, object]:
            return RelaySlotGrant(
                slot_id="slot-0001",
                agent_id="a" * 96,
                relay_endpoint=RelayEndpoint(host="relay.local", port=50151),
                granted_epoch=0,
                ttl_epochs=4,
                target_internal_port=50151,
                max_bytes_per_epoch=64 * 1024 * 1024,
                max_concurrent_streams=8,
                admission_request_hash="0" * 64,
            ).to_dict()

    client = RelayClient(
        relay_base_url="http://127.0.0.1:9",
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        relay_admission_signature=admission_signature,
        transport=BadTransport(),
        allow_guarded_request=True,
    )

    with pytest.raises(RelayClientError, match="relay_grant_agent_id_mismatch"):
        client.request_slot(admission_epoch=0)


def test_keepalive_and_release_reject_foreign_slot() -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    _, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=0,
    )
    client = RelayClient(
        relay_base_url="http://127.0.0.1:9",
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        relay_admission_signature=admission_signature,
        allow_guarded_request=True,
    )
    foreign_slot = RelaySlotGrant(
        slot_id="slot-0001",
        agent_id="a" * 96,
        relay_endpoint=RelayEndpoint(host="relay.local", port=50151),
        granted_epoch=0,
        ttl_epochs=4,
        target_internal_port=50151,
        max_bytes_per_epoch=64 * 1024 * 1024,
        max_concurrent_streams=8,
        admission_request_hash="0" * 64,
    )

    with pytest.raises(RelayClientError, match="relay_slot_agent_id_mismatch"):
        client.keepalive(
            slot=foreign_slot,
            keepalive_epoch=1,
            relay_lifecycle_signature="a" * 192,
        )
    with pytest.raises(RelayClientError, match="relay_slot_agent_id_mismatch"):
        client.release_slot(
            slot=foreign_slot,
            release_epoch=1,
            relay_lifecycle_signature="a" * 192,
        )


def test_https_required_except_loopback_test_url() -> None:
    _secret_key, agent_id, invite_pop = _pop_material()

    with pytest.raises(
        RelayClientError,
        match="relay_base_url_must_be_https_or_loopback_test_url",
    ):
        RelayClient(
            relay_base_url="http://relay.example",
            agent_id=agent_id,
            invite_id=INVITE_ID,
            invite_nullifier=INVITE_NULLIFIER,
            invite_pop=invite_pop,
        )

    with pytest.raises(RelayClientError, match="relay_base_url_credentials_forbidden"):
        RelayClient(
            relay_base_url="https://user:pass@relay.example",
            agent_id=agent_id,
            invite_id=INVITE_ID,
            invite_nullifier=INVITE_NULLIFIER,
            invite_pop=invite_pop,
        )

    with pytest.raises(RelayClientError, match="relay_base_url_query_fragment_forbidden"):
        RelayClient(
            relay_base_url="https://relay.example?token=leak",
            agent_id=agent_id,
            invite_id=INVITE_ID,
            invite_nullifier=INVITE_NULLIFIER,
            invite_pop=invite_pop,
        )


def test_nat_probe_requests_relay_only_after_guard_cleared(monkeypatch) -> None:
    secret_key, agent_id, invite_pop = _pop_material()
    _, admission_signature = _relay_admission_signature(
        secret_key,
        agent_id,
        admission_epoch=2,
        relay_base_url="https://relay.example",
    )
    calls: list[int] = []

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            assert kwargs["relay_base_url"] == "https://relay.example"

        def request_slot(
            self,
            *,
            admission_epoch: int,
            relay_admission_signature: str | None = None,
        ) -> RelaySlotGrant:
            calls.append(admission_epoch)
            assert relay_admission_signature == admission_signature
            return RelaySlotGrant(
                slot_id="slot-0001",
                agent_id=agent_id,
                relay_endpoint=RelayEndpoint(host="relay.example", port=50151),
                granted_epoch=admission_epoch,
                ttl_epochs=4,
                target_internal_port=50151,
                max_bytes_per_epoch=64 * 1024 * 1024,
                max_concurrent_streams=8,
                admission_request_hash="0" * 64,
            )

    engine = NatProbeEngine(
        relay_server_url="https://relay.example",
        relay_admission_material={
            "agent_id": agent_id,
            "invite_id": INVITE_ID,
            "invite_nullifier": INVITE_NULLIFIER,
            "invite_pop": invite_pop,
            "invite_pop_epoch": 0,
            "relay_admission_signature": admission_signature,
        },
        relay_client_factory=FakeClient,
    )
    guarded = engine.run_probe(probe_epoch=2)
    assert guarded.connectivity_receipt.mode is ConnectivityMode.LOCAL_ONLY
    assert calls == []

    monkeypatch.setattr(relay_module, "RELAY_CLIENT_NOT_ACTIVATED", False)
    unguarded = engine.run_probe(probe_epoch=2)
    assert unguarded.connectivity_receipt.mode is ConnectivityMode.RELAY_REACHABLE
    assert unguarded.connectivity_receipt.relay_endpoint == "relay.example:50151"
    assert calls == [2]
