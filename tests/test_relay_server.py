from __future__ import annotations

from collections.abc import Mapping
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_invite_pop_digest
from ilc_core.identity.first_run_provisioning import invite_pop_payload_ref
from ilc_core.network.relay.relay_client import (
    RELAY_CLIENT_SCHEMA_VERSION,
    RelayClient,
    RelayEndpoint,
    RelaySlotGrant,
    relay_admission_payload_ref,
    relay_lifecycle_payload_ref,
)
from ilc_core.network.relay.relay_server import (
    RELAY_ADMISSION_REQUEST_PATH,
    RELAY_HEALTH_PATH,
    RELAY_SERVER_NOT_ACTIVATED,
    RELAY_SERVER_SCHEMA_VERSION,
    RELAY_SERVER_TOKEN,
    RELAY_SLOT_KEEPALIVE_PATH,
    RELAY_SLOT_RELEASE_PATH,
    RelayForwardReceipt,
    RelayRendezvousServer,
    RelayRevocationReceipt,
    RelayServerConfig,
    RelayServerError,
    RelayUdpDatagramProtocol,
    RelayUdpForwarder,
    make_relay_http_handler,
    run_relay_http_server,
)
from ilc_core.network.relay.relay_server import (
    _FailedAdmissionTracker,
    _PacketRateBucket,
    _MAX_FAILED_ADMISSION_ENTRIES,
    _MAX_PACKETS_PER_WINDOW,
    _PACKET_RATE_WINDOW_SECONDS,
)
import ilc_core.network.relay.relay_server as relay_server_module


IKM_HEX = "44" * 32
SECOND_IKM_HEX = "45" * 32
INVITE_ID = "public-rc-relay-server-invite-00"
INVITE_NULLIFIER = "55" * 32
RELAY_AGENT_ID = "66" * 48
RELAY_HOST = "relay.example"
RELAY_PORT = 50151


def _pop_material(ikm_hex: str = IKM_HEX) -> tuple[str, str, str]:
    secret_key, agent_id = keypair_from_ikm_hex(ikm_hex)
    digest = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=INVITE_NULLIFIER,
        invite_id=INVITE_ID,
        epoch=0,
    )
    return secret_key, agent_id, sign_invite_pop_digest(secret_key, digest)


def _server_config() -> RelayServerConfig:
    return RelayServerConfig(
        relay_agent_id=RELAY_AGENT_ID,
        relay_host=RELAY_HOST,
        relay_port=RELAY_PORT,
    )


def _server() -> RelayRendezvousServer:
    return RelayRendezvousServer(_server_config())


def _admission_request(
    *,
    admission_epoch: int = 0,
    requested_internal_port: int = 50151,
    ikm_hex: str = IKM_HEX,
    invite_pop: str | None = None,
    signature: str | None = None,
    relay_base_url: str | None = None,
) -> tuple[str, str, dict[str, Any]]:
    secret_key, agent_id, valid_pop = _pop_material(ikm_hex)
    pop = invite_pop if invite_pop is not None else valid_pop
    invite_ref = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=INVITE_NULLIFIER,
        invite_id=INVITE_ID,
        epoch=0,
    )
    base_url = relay_base_url or _server_config().relay_base_url
    admission_ref = relay_admission_payload_ref(
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop_payload_ref_value=invite_ref,
        admission_epoch=admission_epoch,
        network_id="public-rc",
        relay_base_url=base_url,
        requested_internal_port=requested_internal_port,
        requested_protocol="quic",
        software_version="0.4.5",
    )
    admission_signature = signature
    if admission_signature is None:
        admission_signature = sign_invite_pop_digest(secret_key, admission_ref)
    return secret_key, agent_id, {
        "admission_epoch": admission_epoch,
        "agent_id": agent_id,
        "invite_id": INVITE_ID,
        "invite_nullifier": INVITE_NULLIFIER,
        "invite_pop": pop,
        "invite_pop_epoch": 0,
        "network_id": "public-rc",
        "relay_admission_payload_ref": admission_ref,
        "relay_admission_signature": admission_signature,
        "relay_base_url": base_url,
        "requested_internal_port": requested_internal_port,
        "requested_protocol": "quic",
        "software_version": "0.4.5",
    }


def _grant(server: RelayRendezvousServer) -> tuple[str, str, RelaySlotGrant]:
    secret_key, agent_id, payload = _admission_request()
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="203.0.113.10",
    )
    assert status == 200
    return secret_key, agent_id, RelaySlotGrant.from_dict(body["grant"])


def _lifecycle_payload(
    *,
    secret_key: str,
    agent_id: str,
    slot: RelaySlotGrant,
    action: str,
    epoch: int,
    signature: str | None = None,
) -> dict[str, Any]:
    payload_ref = relay_lifecycle_payload_ref(
        action=action,
        agent_id=agent_id,
        slot_id=slot.slot_id,
        lifecycle_epoch=epoch,
        previous_grant_hash=slot.canonical_response_hash,
        network_id="public-rc",
        relay_base_url=_server_config().relay_base_url,
    )
    signed = signature
    if signed is None:
        signed = sign_invite_pop_digest(secret_key, payload_ref)
    if action == "keepalive":
        return {
            "agent_id": agent_id,
            "keepalive_epoch": epoch,
            "previous_grant_hash": slot.canonical_response_hash,
            "relay_lifecycle_payload_ref": payload_ref,
            "relay_lifecycle_signature": signed,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "slot_id": slot.slot_id,
        }
    return {
        "agent_id": agent_id,
        "previous_grant_hash": slot.canonical_response_hash,
        "release_epoch": epoch,
        "relay_lifecycle_payload_ref": payload_ref,
        "relay_lifecycle_signature": signed,
        "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
        "slot_id": slot.slot_id,
    }


def test_health_endpoint_returns_correct_fields() -> None:
    status, body = _server().handle_json_request(
        method="GET",
        path=RELAY_HEALTH_PATH,
        payload=None,
    )

    assert status == 200
    assert body["relay_agent_id"] == RELAY_AGENT_ID
    assert body["schema_version"] == RELAY_SERVER_SCHEMA_VERSION
    assert body["active_slot_count"] == 0
    assert body["server_guard_active"] is True


def test_valid_admission_accepted() -> None:
    _, agent_id, payload = _admission_request()
    status, body = _server().handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="203.0.113.10",
    )

    assert status == 200
    grant = RelaySlotGrant.from_dict(body["grant"])
    assert grant.agent_id == agent_id
    assert grant.granted_epoch == 0
    assert grant.ttl_epochs == 4
    assert grant.max_bytes_per_epoch == 64 * 1024 * 1024
    assert grant.max_concurrent_streams == 8
    assert grant.relay_endpoint == RelayEndpoint(host=RELAY_HOST, port=RELAY_PORT)


def test_invalid_bls_signature_rejected() -> None:
    _, _, payload = _admission_request(signature="f" * 192)

    status, body = _server().handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 400
    assert body["error"] == "relay_admission_signature_verification_failed"


def test_invite_pop_verification_failure_rejected() -> None:
    _, _, payload = _admission_request(invite_pop="e" * 192)

    status, body = _server().handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 400
    assert body["error"] == "relay_invite_pop_verification_failed"


def test_agent_id_format_invalid_rejected() -> None:
    _, _, payload = _admission_request()
    payload["agent_id"] = "not-hex"

    status, body = _server().handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 400
    assert body["error"] == "relay_agent_id_invalid"


def test_duplicate_slot_for_same_agent_rejected() -> None:
    server = _server()
    _, _, payload = _admission_request()
    assert server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )[0] == 200

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 400
    assert body["error"] == "relay_slot_already_active"


def test_keepalive_within_ttl_window_accepted() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="keepalive",
            epoch=1,
        ),
    )

    assert status == 200
    assert body["renewal_result"] == "renewed"
    assert body["slot_id"] == slot.slot_id


def test_keepalive_epoch_before_grant_rejected() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
        )
    )
    secret_key, agent_id, payload = _admission_request(admission_epoch=2)
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )
    assert status == 200
    slot = RelaySlotGrant.from_dict(body["grant"])

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="keepalive",
            epoch=1,
        ),
    )

    assert status == 400
    assert body["error"] == "relay_lifecycle_epoch_before_grant"


def test_keepalive_epoch_beyond_ttl_rejected() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="keepalive",
            epoch=5,
        ),
    )

    assert status == 400
    assert body["error"] == "relay_lifecycle_epoch_after_expiry"


def test_keepalive_wrong_lifecycle_signature_rejected() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="keepalive",
            epoch=1,
            signature="d" * 192,
        ),
    )

    assert status == 400
    assert body["error"] == "relay_lifecycle_signature_invalid"


def test_release_frees_slot_so_same_agent_can_request_again() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_RELEASE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="release",
            epoch=1,
        ),
    )
    assert status == 200
    assert body["release_result"] == "released"
    _, _, payload = _admission_request()

    status, _body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 200


def test_duplicate_release_replay_rejected() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)
    release_payload = _lifecycle_payload(
        secret_key=secret_key,
        agent_id=agent_id,
        slot=slot,
        action="release",
        epoch=1,
    )
    assert server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_RELEASE_PATH,
        payload=release_payload,
    )[0] == 200

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_RELEASE_PATH,
        payload=release_payload,
    )

    assert status == 400
    assert body["error"] == "relay_slot_released"


def test_relay_server_guard_blocks_start() -> None:
    assert RELAY_SERVER_NOT_ACTIVATED is True
    with pytest.raises(RelayServerError, match="relay_server_not_activated"):
        run_relay_http_server(
            config=_server_config(),
            bind_host="127.0.0.1",
            bind_port=0,
        )


def test_byte_budget_enforcement_revokes_slot() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            max_bytes_per_epoch=8,
        )
    )
    secret_key, agent_id, payload = _admission_request()
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )
    assert status == 200
    slot = RelaySlotGrant.from_dict(body["grant"])
    forwarder = RelayUdpForwarder(server)
    receipt, revocation = forwarder.forward(slot_id=slot.slot_id, payload=b"1234", epoch=0)
    assert receipt.to_dict()["status"] == "forwarded"
    assert revocation is None

    receipt, revocation = forwarder.forward(slot_id=slot.slot_id, payload=b"56789", epoch=0)
    assert receipt.status == "revoked"
    assert revocation is not None
    assert revocation.reason_token == "relay_slot_revoked_budget_exceeded"

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="keepalive",
            epoch=1,
        ),
    )
    assert status == 400
    assert body["error"] == "relay_slot_revoked_budget_exceeded"


def test_asyncio_udp_protocol_accounts_bytes_without_parsing_payload() -> None:
    server = _server()
    _, _, slot = _grant(server)
    peer = ("198.51.100.7", 54000)
    receipts = []
    protocol = RelayUdpDatagramProtocol(
        server,
        slot_id_by_peer={peer: slot.slot_id},
        epoch_provider=lambda: 0,
        receipt_sink=lambda receipt, addr: receipts.append((receipt, addr)),
    )
    opaque_quic_bytes = b"\xc3\x00\x00\x01encrypted-quic-payload"

    protocol.datagram_received(opaque_quic_bytes, peer)

    assert protocol.last_error is None
    assert len(receipts) == 1
    receipt, addr = receipts[0]
    assert addr == peer
    assert receipt.slot_id == slot.slot_id
    assert receipt.bytes_forwarded == len(opaque_quic_bytes)


def test_asyncio_udp_protocol_rejects_unadmitted_peer_without_payload_parse() -> None:
    protocol = RelayUdpDatagramProtocol(
        _server(),
        slot_id_by_peer={},
        epoch_provider=lambda: 0,
    )

    protocol.datagram_received(b"opaque-quic", ("198.51.100.8", 54001))

    assert protocol.last_error == "relay_udp_peer_not_admitted"


def test_slot_expires_and_agent_can_request_new_slot() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="keepalive",
            epoch=5,
        ),
    )
    assert status == 400
    assert body["error"] == "relay_lifecycle_epoch_after_expiry"
    _, _, payload = _admission_request(admission_epoch=5)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 200
    assert RelaySlotGrant.from_dict(body["grant"]).slot_id != slot.slot_id


def test_server_implements_existing_client_paths() -> None:
    server = _server()
    secret_key, agent_id, invite_pop = _pop_material()
    captured_paths: list[str] = []

    class Transport:
        def post_json(
            self,
            path: str,
            payload: Mapping[str, Any],
            timeout_seconds: float,
        ) -> dict[str, Any]:
            assert timeout_seconds == 3.0
            captured_paths.append(path)
            status, body = server.handle_json_request(
                method="POST",
                path=path,
                payload=payload,
            )
            assert status == 200, body
            return body

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
        admission_epoch=0,
        network_id="public-rc",
        relay_base_url=_server_config().relay_base_url,
        requested_internal_port=50151,
        requested_protocol="quic",
        software_version="0.4.5",
    )
    client = RelayClient(
        relay_base_url=_server_config().relay_base_url,
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop=invite_pop,
        relay_admission_signature=sign_invite_pop_digest(secret_key, admission_ref),
        software_version="0.4.5",
        transport=Transport(),
        allow_guarded_request=True,
    )
    grant = client.request_slot(admission_epoch=0)
    keepalive_ref = relay_lifecycle_payload_ref(
        action="keepalive",
        agent_id=agent_id,
        slot_id=grant.slot_id,
        lifecycle_epoch=1,
        previous_grant_hash=grant.canonical_response_hash,
        network_id="public-rc",
        relay_base_url=_server_config().relay_base_url,
    )
    release_ref = relay_lifecycle_payload_ref(
        action="release",
        agent_id=agent_id,
        slot_id=grant.slot_id,
        lifecycle_epoch=1,
        previous_grant_hash=grant.canonical_response_hash,
        network_id="public-rc",
        relay_base_url=_server_config().relay_base_url,
    )

    assert client.keepalive(
        slot=grant,
        keepalive_epoch=1,
        relay_lifecycle_signature=sign_invite_pop_digest(secret_key, keepalive_ref),
    ).renewal_result == "renewed"
    assert client.release_slot(
        slot=grant,
        release_epoch=1,
        relay_lifecycle_signature=sign_invite_pop_digest(secret_key, release_ref),
    ).release_result == "released"
    assert captured_paths == [
        RELAY_ADMISSION_REQUEST_PATH,
        RELAY_SLOT_KEEPALIVE_PATH,
        RELAY_SLOT_RELEASE_PATH,
    ]


def test_http_handler_rejects_oversized_request_without_socket_leak() -> None:
    server = _server()
    httpd = None
    thread = None

    class _TestHTTPServer(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    httpd = _TestHTTPServer(("127.0.0.1", 0), make_relay_http_handler(server))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        request = Request(
            f"http://127.0.0.1:{httpd.server_port}{RELAY_ADMISSION_REQUEST_PATH}",
            data=b"{" + (b'"x":' + b'"a"' * 40_000) + b"}",
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(HTTPError) as exc_info:
            urlopen(request, timeout=3)
        assert exc_info.value.code == 400
        body = json.loads(exc_info.value.read().decode("utf-8"))
    finally:
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()
        if thread is not None:
            thread.join(timeout=2)

    assert body["error"] == "relay_request_too_large"


def test_unknown_endpoint_rejected() -> None:
    status, body = _server().handle_json_request(
        method="POST",
        path="/relay/request-slot",
        payload={},
    )

    assert status == 404
    assert body["error"] == "relay_path_not_found"


def test_schema_token_and_canonical_receipt_are_stable() -> None:
    server = _server()
    _, _, slot = _grant(server)
    receipt, revocation = server.forward_datagram(slot_id=slot.slot_id, payload=b"abc", epoch=0)

    assert RELAY_SERVER_TOKEN == "relay_server_impl_committed_GAP_RELAY_SERVER_IMPL_00"
    assert revocation is None
    assert receipt.to_canonical_json().startswith(b'{"agent_id":')
    assert b'"schema_version":"relay_server_GAP_RELAY_SERVER_IMPL_00.v0.1"' in (
        receipt.to_canonical_json()
    )


def test_packet_rate_bucket_drops_on_exhaustion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(relay_server_module.time, "monotonic", lambda: 100.0)
    bucket = _PacketRateBucket(window_start=100.0)

    assert all(bucket.allow() for _ in range(_MAX_PACKETS_PER_WINDOW))
    assert bucket.allow() is False


def test_packet_rate_bucket_resets_after_window(monkeypatch: pytest.MonkeyPatch) -> None:
    now = {"value": 100.0}
    monkeypatch.setattr(relay_server_module.time, "monotonic", lambda: now["value"])
    bucket = _PacketRateBucket(window_start=100.0)
    for _ in range(_MAX_PACKETS_PER_WINDOW):
        assert bucket.allow() is True
    assert bucket.allow() is False

    now["value"] = 100.0 + _PACKET_RATE_WINDOW_SECONDS + 0.001

    assert bucket.allow() is True
    assert bucket.packet_count == 1


def test_packet_rate_exceeded_revokes_slot_with_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(relay_server_module.time, "monotonic", lambda: 200.0)
    server = _server()
    _, agent_id, slot = _grant(server)

    for _ in range(_MAX_PACKETS_PER_WINDOW):
        receipt, revocation = server.forward_datagram(slot_id=slot.slot_id, payload=b"x", epoch=0)
        assert receipt.status == "forwarded"
        assert revocation is None

    receipt, revocation = server.forward_datagram(slot_id=slot.slot_id, payload=b"x", epoch=0)

    assert receipt.status == "revoked"
    assert revocation is not None
    assert revocation.agent_id == agent_id
    assert revocation.reason_token == "relay_slot_revoked_packet_rate_exceeded"
    assert slot.slot_id not in server._packet_rate_buckets


def test_failed_admission_tracker_blocks_after_n_failures() -> None:
    server = _server()
    _, _agent_id, payload = _admission_request(signature="f" * 192)

    for _ in range(5):
        status, body = server.handle_json_request(
            method="POST",
            path=RELAY_ADMISSION_REQUEST_PATH,
            payload=payload,
            source_host="198.51.100.44",
        )
        assert status == 400
        assert body["error"] == "relay_admission_signature_verification_failed"

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.44",
    )

    assert status == 400
    assert body["error"] == "relay_admission_cooldown_active"


def test_failed_admission_tracker_blocks_by_agent_id() -> None:
    server = _server()
    _, agent_id, payload = _admission_request(invite_pop="e" * 192)

    for index in range(5):
        status, body = server.handle_json_request(
            method="POST",
            path=RELAY_ADMISSION_REQUEST_PATH,
            payload=payload,
            source_host=f"198.51.100.{50 + index}",
        )
        assert status == 400
        assert body["error"] == "relay_invite_pop_verification_failed"

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.99",
    )

    assert status == 400
    assert body["error"] == "relay_admission_cooldown_active"
    assert server._failed_admissions.failure_count(agent_id) == 5


def test_failed_admission_tracker_fifo_eviction_at_cap() -> None:
    tracker = _FailedAdmissionTracker(max_entries=3)

    tracker.record_failure("ip:198.51.100.1")
    tracker.record_failure("ip:198.51.100.2")
    tracker.record_failure("ip:198.51.100.3")
    tracker.record_failure("ip:198.51.100.4")

    assert len(tracker._entries) == 3
    assert "ip:198.51.100.1" not in tracker._entries
    assert tracker._insertion_order == [
        "ip:198.51.100.2",
        "ip:198.51.100.3",
        "ip:198.51.100.4",
    ]
    assert _MAX_FAILED_ADMISSION_ENTRIES == 65_536


def test_failed_admission_valid_client_not_penalized() -> None:
    server = _server()
    _, agent_id, payload = _admission_request()
    assert server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.77",
    )[0] == 200

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.77",
    )

    assert status == 400
    assert body["error"] == "relay_slot_already_active"
    assert server._failed_admissions.failure_count(agent_id) == 0
    assert server._failed_admissions.failure_count("ip:198.51.100.77") == 0


def test_revocation_receipt_is_self_certifying() -> None:
    receipt = RelayRevocationReceipt.build(
        slot_id="slot-test",
        agent_id="77" * 48,
        epoch=0,
        reason_token="relay_slot_revoked_packet_rate_exceeded",
        bytes_forwarded=123,
    )
    expected_payload = {
        "agent_id": "77" * 48,
        "bytes_forwarded": 123,
        "epoch": 0,
        "reason_token": "relay_slot_revoked_packet_rate_exceeded",
        "slot_id": "slot-test",
    }

    expected = hashlib.sha256(
        json.dumps(
            expected_payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    assert receipt.revocation_ref == expected
    assert b'"schema_version":"relay_abuse_limits_GAP_RELAY_ABUSE_LIMITS_FIX1_00.v0.1"' in (
        receipt.to_canonical_json()
    )


def test_no_quic_stream_parsing_in_relay_server() -> None:
    source = Path("ilc_core/network/relay/relay_server.py").read_text()

    forbidden = [
        "stream_id",
        "STREAM_LIMIT",
        "parse_quic",
        "quic_frame",
        "quic_stream_count",
    ]

    for token in forbidden:
        assert token not in source


def test_no_global_reputation_penalty_on_revocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "ilc_core.network.d2d.routing_reputation_runtime.record_serve_event",
        lambda *_args, **_kwargs: calls.append("record_serve_event"),
    )
    monkeypatch.setattr(
        "ilc_core.network.d2d.centrality_delta_gossip_runtime.accumulate_centrality_delta",
        lambda *_args, **_kwargs: calls.append("accumulate_centrality_delta"),
    )
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            max_bytes_per_epoch=1,
        )
    )
    _, _, slot = _grant(server)

    _receipt, revocation = server.forward_datagram(slot_id=slot.slot_id, payload=b"ab", epoch=0)

    assert revocation is not None
    assert calls == []


def test_malformed_agent_id_records_ip_only() -> None:
    server = _server()
    _, _, payload = _admission_request()
    payload["agent_id"] = "not-hex"

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.88",
    )

    assert status == 400
    assert body["error"] == "relay_agent_id_invalid"
    assert server._failed_admissions.failure_count("ip:198.51.100.88") == 1


def test_network_id_mismatch_does_not_increment_failed_admission_tracker() -> None:
    server = _server()
    secret_key, agent_id, payload = _admission_request()
    payload["network_id"] = "other-rc"
    admission_ref = relay_admission_payload_ref(
        agent_id=agent_id,
        invite_id=INVITE_ID,
        invite_nullifier=INVITE_NULLIFIER,
        invite_pop_payload_ref_value=invite_pop_payload_ref(
            agent_id_hex=agent_id,
            invite_nullifier=INVITE_NULLIFIER,
            invite_id=INVITE_ID,
            epoch=0,
        ),
        admission_epoch=0,
        network_id="other-rc",
        relay_base_url=_server_config().relay_base_url,
        requested_internal_port=50151,
        requested_protocol="quic",
        software_version="0.4.5",
    )
    payload["relay_admission_payload_ref"] = admission_ref
    payload["relay_admission_signature"] = sign_invite_pop_digest(secret_key, admission_ref)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.89",
    )

    assert status == 400
    assert body["error"] == "relay_admission_network_id_mismatch"
    assert server._failed_admissions.failure_count(agent_id) == 0
    assert server._failed_admissions.failure_count("ip:198.51.100.89") == 0


def test_bucket_removed_on_release_expiry_and_revocation() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)
    assert slot.slot_id in server._packet_rate_buckets
    assert server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_RELEASE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="release",
            epoch=1,
        ),
    )[0] == 200
    assert slot.slot_id not in server._packet_rate_buckets

    _secret_key, _agent_id, slot = _grant(server)
    assert slot.slot_id in server._packet_rate_buckets
    server._expire_slot(slot.slot_id)
    assert slot.slot_id not in server._packet_rate_buckets

    _secret_key, _agent_id, slot = _grant(server)
    assert slot.slot_id in server._packet_rate_buckets
    server._revoke_slot(slot.slot_id, "relay_slot_revoked_operator_emergency")
    assert slot.slot_id not in server._packet_rate_buckets
