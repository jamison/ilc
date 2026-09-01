from __future__ import annotations

from collections.abc import Mapping
import asyncio
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    sign_invite_pop_digest,
    sign_relay_admission_digest,
    sign_relay_bootstrap_capsule_digest,
    sign_relay_bootstrap_record_digest,
    sign_relay_lifecycle_digest,
)
from ilc_core.identity.first_run_provisioning import invite_pop_payload_ref
import ilc_core.network.relay as relay_package
from ilc_core.network.relay.relay_client import (
    RELAY_CLIENT_SCHEMA_VERSION,
    RelayClient,
    RelayEndpoint,
    RelaySlotGrant,
    relay_admission_payload_ref,
    relay_lifecycle_payload_ref,
    relay_slot_claim_datagram,
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
    RelayDataPlaneRuntime,
    RelayRendezvousServer,
    RelayRevocationReceipt,
    RelayServerConfig,
    RelayServerError,
    RelayUdpDatagramProtocol,
    RelayUdpForwarder,
    RelayUdpPortForwarder,
    build_relay_bootstrap_record,
    make_relay_http_handler,
    parse_relay_bootstrap_capsule,
    relay_bootstrap_capsule_payload_ref,
    relay_bootstrap_record_payload_ref,
    run_relay_http_server,
    sign_relay_bootstrap_record,
    verify_relay_bootstrap_record,
)
from ilc_core.network.relay.relay_server import (
    _FailedAdmissionTracker,
    _RelayPortPool,
    _RelayTombstone,
    _PacketRateBucket,
    _MAX_FAILED_ADMISSION_ENTRIES,
    _MAX_PACKETS_PER_WINDOW,
    _PACKET_RATE_WINDOW_SECONDS,
    _error_token,
)
import ilc_core.network.relay.relay_server as relay_server_module


IKM_HEX = "44" * 32
SECOND_IKM_HEX = "45" * 32
INVITE_ID = "public-rc-relay-server-invite-00"
INVITE_NULLIFIER = "55" * 32
RELAY_AGENT_ID = "66" * 48
RELAY_HOST = "127.0.0.1"
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
        admission_signature = sign_relay_admission_digest(secret_key, admission_ref)
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
        signed = sign_relay_lifecycle_digest(secret_key, payload_ref)
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
    assert body["server_guard_active"] is False


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
    assert grant.relay_endpoint == RelayEndpoint(host=RELAY_HOST, port=52000)
    assert len(bytes.fromhex(grant.relay_slot_nonce)) == 32


def test_concurrent_admission_allocates_unique_ports() -> None:
    server = _server()
    payloads = [
        _admission_request(ikm_hex=f"{0x50 + index:02x}" * 32)[2]
        for index in range(8)
    ]
    results: list[int] = []
    errors: list[BaseException] = []
    lock = threading.Lock()

    def admit(index: int) -> None:
        try:
            status, body = server.handle_json_request(
                method="POST",
                path=RELAY_ADMISSION_REQUEST_PATH,
                payload=payloads[index],
                source_host=f"198.51.100.{index + 1}",
            )
            assert status == 200, body
            with lock:
                results.append(RelaySlotGrant.from_dict(body["grant"]).relay_endpoint.port)
        except BaseException as exc:
            with lock:
                errors.append(exc)

    threads = [threading.Thread(target=admit, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert all(not thread.is_alive() for thread in threads)

    assert errors == []
    assert len(results) == 8
    assert sorted(results) == list(range(52000, 52008))
    assert server.active_slot_count == 8


def test_invalid_bls_signature_rejected() -> None:
    _, _, payload = _admission_request(signature="f" * 192)

    status, body = _server().handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 400
    assert body["error"] == "relay_admission_signature_verification_failed"


def test_relay_admission_rejects_invite_pop_signature_domain() -> None:
    secret_key, _, payload = _admission_request()
    payload["relay_admission_signature"] = sign_invite_pop_digest(
        secret_key,
        payload["relay_admission_payload_ref"],
    )

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


def test_bls_invite_pop_failure_records_failure_without_slot_or_port() -> None:
    server = _server()
    _, agent_id, payload = _admission_request(invite_pop="e" * 192)
    before = server._port_pool.available_count

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.31",
    )

    assert status == 400
    assert body["error"] == "relay_invite_pop_verification_failed"
    assert server.active_slot_count == 0
    assert server._slots_by_id == {}
    assert server._port_pool.available_count == before
    assert server._failed_admissions.failure_count(agent_id) == 1
    assert server._failed_admissions.failure_count("ip:198.51.100.31") == 1


def test_bls_admission_signature_failure_records_failure_without_slot_or_port() -> None:
    server = _server()
    _, agent_id, payload = _admission_request(signature="f" * 192)
    before = server._port_pool.available_count

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.32",
    )

    assert status == 400
    assert body["error"] == "relay_admission_signature_verification_failed"
    assert server.active_slot_count == 0
    assert server._slots_by_id == {}
    assert server._port_pool.available_count == before
    assert server._failed_admissions.failure_count(agent_id) == 1
    assert server._failed_admissions.failure_count("ip:198.51.100.32") == 1


def test_admission_request_coercion_runs_before_state_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server = _server()
    _, _, payload = _admission_request()
    original = relay_server_module._coerce_admission_request
    lock_observed: list[bool] = []

    def wrapped(payload: Mapping[str, Any]) -> Any:
        is_owned = getattr(server._state_lock, "_is_owned", lambda: False)()
        lock_observed.append(bool(is_owned))
        return original(payload)

    monkeypatch.setattr(relay_server_module, "_coerce_admission_request", wrapped)

    status, _body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="198.51.100.33",
    )

    assert status == 200
    assert lock_observed == [False]


def test_two_concurrent_valid_admissions_succeed_without_deadlock() -> None:
    server = _server()
    _, _, first_payload = _admission_request(ikm_hex=IKM_HEX)
    _, _, second_payload = _admission_request(ikm_hex=SECOND_IKM_HEX)
    results: list[tuple[int, dict[str, Any]]] = []
    results_lock = threading.Lock()

    def request(payload: dict[str, Any], source_host: str) -> None:
        result = server.handle_json_request(
            method="POST",
            path=RELAY_ADMISSION_REQUEST_PATH,
            payload=payload,
            source_host=source_host,
        )
        with results_lock:
            results.append(result)

    first = threading.Thread(target=request, args=(first_payload, "198.51.100.34"))
    second = threading.Thread(target=request, args=(second_payload, "198.51.100.35"))
    first.start()
    second.start()
    first.join(timeout=10)
    second.join(timeout=10)

    assert not first.is_alive()
    assert not second.is_alive()
    assert sorted(status for status, _body in results) == [200, 200]
    assert server.active_slot_count == 2


def test_concurrent_capacity_race_leaves_one_winner_and_no_port_leak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(relay_server_module, "_MAX_ACTIVE_SLOTS", 1)
    server = _server()
    _, _, first_payload = _admission_request(ikm_hex=IKM_HEX)
    _, _, second_payload = _admission_request(ikm_hex=SECOND_IKM_HEX)
    before = server._port_pool.available_count
    results: list[tuple[int, dict[str, Any]]] = []
    results_lock = threading.Lock()

    def request(payload: dict[str, Any], source_host: str) -> None:
        result = server.handle_json_request(
            method="POST",
            path=RELAY_ADMISSION_REQUEST_PATH,
            payload=payload,
            source_host=source_host,
        )
        with results_lock:
            results.append(result)

    first = threading.Thread(target=request, args=(first_payload, "198.51.100.36"))
    second = threading.Thread(target=request, args=(second_payload, "198.51.100.37"))
    first.start()
    second.start()
    first.join(timeout=10)
    second.join(timeout=10)

    assert not first.is_alive()
    assert not second.is_alive()
    assert sorted(status for status, _body in results) == [200, 400]
    assert [body.get("error") for status, body in results if status == 400] == [
        "relay_server_active_slot_limit_exceeded"
    ]
    assert server.active_slot_count == 1
    assert server._port_pool.available_count == before - 1


def test_request_slot_checks_cooldown_before_and_after_bls_in_source() -> None:
    src = Path("ilc_core/network/relay/relay_server.py").read_text()
    start = src.index("def request_slot(")
    end = src.index("    def keepalive(", start)
    request_slot_src = src[start:end]
    first_lock = request_slot_src.index("with self._state_lock:")
    coerce = request_slot_src.index("_coerce_admission_request(body)")
    second_lock = request_slot_src.index("with self._state_lock:", coerce)

    assert first_lock < coerce < second_lock
    assert request_slot_src.index("self._require_admission_not_blocked", first_lock) < coerce
    assert request_slot_src.index("self._require_admission_not_blocked", second_lock) > coerce


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
    assert body["error"] == "relay_lifecycle_signature_verification_failed"


def test_relay_lifecycle_rejects_invite_pop_signature_domain() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)
    payload = _lifecycle_payload(
        secret_key=secret_key,
        agent_id=agent_id,
        slot=slot,
        action="keepalive",
        epoch=1,
    )
    payload["relay_lifecycle_signature"] = sign_invite_pop_digest(
        secret_key,
        payload["relay_lifecycle_payload_ref"],
    )

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_KEEPALIVE_PATH,
        payload=payload,
    )

    assert status == 400
    assert body["error"] == "relay_lifecycle_signature_verification_failed"


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


def test_relay_server_guard_is_activation_cleared() -> None:
    assert RELAY_SERVER_NOT_ACTIVATED is False


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


def test_data_plane_port_released_after_budget_revocation() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            max_bytes_per_epoch=1,
        )
    )
    _, _agent_id, payload = _admission_request()
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )
    assert status == 200
    slot = RelaySlotGrant.from_dict(body["grant"])
    before = server._port_pool.available_count

    _receipt, revocation = server.forward_datagram(slot_id=slot.slot_id, payload=b"ab", epoch=0)

    assert revocation is not None
    assert server._port_pool.available_count == before + 1


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
        relay_admission_signature=sign_relay_admission_digest(secret_key, admission_ref),
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
        relay_lifecycle_signature=sign_relay_lifecycle_digest(secret_key, keepalive_ref),
    ).renewal_result == "renewed"
    assert client.release_slot(
        slot=grant,
        release_epoch=1,
        relay_lifecycle_signature=sign_relay_lifecycle_digest(secret_key, release_ref),
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
    assert list(tracker._insertion_order) == [
        "ip:198.51.100.2",
        "ip:198.51.100.3",
        "ip:198.51.100.4",
    ]
    assert _MAX_FAILED_ADMISSION_ENTRIES == 65_536


def test_failed_admission_tracker_cooldown_expiry_unblocks(monkeypatch: pytest.MonkeyPatch) -> None:
    now = {"value": 1000.0}
    tracker = _FailedAdmissionTracker(now_provider=lambda: now["value"])
    key = "ip:198.51.100.200"

    for _ in range(5):
        tracker.record_failure(key)
    assert tracker.is_blocked(key) is True

    now["value"] += 60.001

    assert tracker.is_blocked(key) is False
    assert key not in tracker._entries
    assert key not in tracker._queued_keys
    assert key not in tracker._insertion_order


def test_cooldown_rejects_before_bls_coercion(monkeypatch: pytest.MonkeyPatch) -> None:
    server = _server()
    _, _, payload = _admission_request()
    source_host = "198.51.100.222"
    for _ in range(5):
        server._failed_admissions.record_failure(f"ip:{source_host}")

    def fail_if_called(_payload: Mapping[str, Any]) -> None:
        raise AssertionError("cooldown must block before BLS validation")

    monkeypatch.setattr(relay_server_module, "_coerce_admission_request", fail_if_called)

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host=source_host,
    )

    assert status == 400
    assert body["error"] == "relay_admission_cooldown_active"


def test_failed_admission_tracker_duplicate_key_reports_do_not_grow_fifo() -> None:
    tracker = _FailedAdmissionTracker(max_entries=3)

    for _ in range(20):
        tracker.record_failure("ip:198.51.100.201")

    assert tracker.failure_count("ip:198.51.100.201") == 20
    assert list(tracker._insertion_order) == ["ip:198.51.100.201"]
    assert tracker._queued_keys == {"ip:198.51.100.201"}


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


def test_public_relay_package_exports_current_helpers_only() -> None:
    assert not hasattr(relay_package, "RelayUdpDatagramProtocol")
    assert relay_package.RelayUdpPortForwarder is RelayUdpPortForwarder
    assert relay_package.sign_relay_bootstrap_record is sign_relay_bootstrap_record
    assert relay_package.verify_relay_bootstrap_record is verify_relay_bootstrap_record
    assert relay_package.parse_relay_bootstrap_capsule is parse_relay_bootstrap_capsule
    assert relay_package.relay_slot_claim_datagram is relay_slot_claim_datagram


@pytest.mark.parametrize(
    "exc",
    [
        ValueError(""),
        ValueError("bad value with spaces"),
        ValueError("/tmp/private/path"),
        ValueError("line1\nline2"),
        ValueError("x" * 129),
    ],
)
def test_error_token_redacts_uncontrolled_exception_text(exc: Exception) -> None:
    assert _error_token(exc) == "relay_internal_error"


def test_error_token_preserves_controlled_tokens() -> None:
    assert _error_token(ValueError("relay_slot_revoked_budget_exceeded")) == (
        "relay_slot_revoked_budget_exceeded"
    )


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
    payload["relay_admission_signature"] = sign_relay_admission_digest(secret_key, admission_ref)

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


def test_release_removes_active_slot_and_retains_tombstone_with_port_returned() -> None:
    server = _server()
    secret_key, agent_id, slot = _grant(server)
    before_release = server._port_pool.available_count

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
    assert slot.slot_id not in server._slots_by_id
    assert server._tombstones[slot.slot_id].status == "released"
    assert server._tombstones[slot.slot_id].terminated_epoch == 1
    assert server._tombstones[slot.slot_id].data_port == slot.relay_endpoint.port
    assert server._port_pool.available_count == before_release + 1


def test_revocation_removes_active_slot_and_keeps_receipt_in_tombstone() -> None:
    server = _server()
    _, agent_id, slot = _grant(server)

    receipt = server._revoke_slot(
        slot.slot_id,
        "relay_slot_revoked_operator_emergency",
        terminated_epoch=2,
    )

    assert slot.slot_id not in server._slots_by_id
    tombstone = server._tombstones[slot.slot_id]
    assert tombstone.status == "revoked"
    assert tombstone.terminated_epoch == 2
    assert tombstone.revocation_receipt == receipt
    assert receipt.agent_id == agent_id
    assert server.get_revocation_receipt(slot.slot_id) == receipt


def test_expiry_removes_active_slot_and_preserves_terminal_error_token() -> None:
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

    assert slot.slot_id not in server._slots_by_id
    assert server._tombstones[slot.slot_id].status == "expired"

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
    assert body["error"] == "relay_slot_expired"


def test_tombstone_gc_evicts_entries_older_than_retention_window() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            tombstone_retention_epochs=1,
        )
    )
    secret_key, agent_id, slot = _grant(server)
    assert server.handle_json_request(
        method="POST",
        path=RELAY_SLOT_RELEASE_PATH,
        payload=_lifecycle_payload(
            secret_key=secret_key,
            agent_id=agent_id,
            slot=slot,
            action="release",
            epoch=0,
        ),
    )[0] == 200
    assert slot.slot_id in server._tombstones
    _, _, payload = _admission_request(admission_epoch=2)

    assert server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )[0] == 200

    assert slot.slot_id not in server._tombstones


def test_tombstone_gc_retains_entries_inside_retention_window() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            tombstone_retention_epochs=2,
        )
    )
    secret_key, agent_id, slot = _grant(server)
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
    _, _, payload = _admission_request(admission_epoch=3)

    assert server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )[0] == 200

    assert slot.slot_id in server._tombstones


def test_revocation_receipt_returns_none_after_tombstone_gc() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            tombstone_retention_epochs=1,
        )
    )
    _, _, slot = _grant(server)
    receipt = server._revoke_slot(
        slot.slot_id,
        "relay_slot_revoked_operator_emergency",
        terminated_epoch=0,
    )
    assert server.get_revocation_receipt(slot.slot_id) == receipt
    _, _, payload = _admission_request(admission_epoch=2)

    assert server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )[0] == 200

    assert server.get_revocation_receipt(slot.slot_id) is None


def test_tombstones_remain_bounded_after_many_release_cycles() -> None:
    server = RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            tombstone_retention_epochs=1,
        )
    )

    for epoch in range(200):
        server._tombstones[f"slot-{epoch}"] = _RelayTombstone(
            slot_id=f"slot-{epoch}",
            status="released",
            terminated_epoch=epoch,
        )
        server._gc_tombstones(epoch)

    assert len(server._slots_by_id) == 0
    assert len(server._tombstones) <= 2
    assert server.active_slot_count == 0


def test_tombstones_count_cap_bounds_same_epoch_churn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(relay_server_module, "_MAX_TOMBSTONES", 3)
    server = _server()

    for index in range(8):
        server._track_tombstone(
            _RelayTombstone(
                slot_id=f"slot-{index}",
                status="released",
                terminated_epoch=0,
            )
        )

    assert len(server._tombstones) == 3
    assert set(server._tombstones) == {"slot-5", "slot-6", "slot-7"}


def test_tombstone_retention_config_rejects_invalid_values() -> None:
    with pytest.raises(RelayServerError, match="relay_tombstone_retention_epochs_invalid"):
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host=RELAY_HOST,
            relay_port=RELAY_PORT,
            tombstone_retention_epochs=True,
        )


def test_port_pool_allocates_lowest_first() -> None:
    pool = _RelayPortPool(52010, 52012)

    assert [pool.allocate(), pool.allocate(), pool.allocate()] == [52010, 52011, 52012]


def test_port_pool_release_and_reallocate() -> None:
    pool = _RelayPortPool(52010, 52012)

    first = pool.allocate()
    second = pool.allocate()
    pool.release(first)

    assert second == 52011
    assert pool.allocate() == 52010


def test_port_pool_consecutive_double_release_is_idempotent() -> None:
    pool = _RelayPortPool(52010, 52010)
    first = pool.allocate()
    pool.release(first)
    pool.release(first)

    assert pool.available_count == 1
    assert pool.allocate() == first


def test_port_pool_released_port_is_not_duplicated_after_interleaving() -> None:
    pool = _RelayPortPool(52010, 52011)
    first = pool.allocate()
    second = pool.allocate()

    pool.release(first)
    pool.release(first)
    assert pool.available_count == 1
    assert pool.allocate() == first

    pool.release(second)
    assert pool.allocate() == second


def test_port_pool_exhausted_raises() -> None:
    pool = _RelayPortPool(52010, 52010)
    assert pool.allocate() == 52010

    with pytest.raises(RelayServerError, match="relay_data_port_pool_exhausted"):
        pool.allocate()


def test_config_data_port_range_defaults() -> None:
    config = _server_config()

    assert config.data_port_range_start == 52000
    assert config.data_port_range_end == 52999
    assert config.control_port == 51151


def test_config_control_port_overlap_raises() -> None:
    with pytest.raises(RelayServerError, match="relay_control_port_overlaps_data_range"):
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host="127.0.0.1",
            control_port=52001,
        )


def test_config_non_loopback_no_tls_raises() -> None:
    with pytest.raises(RelayServerError, match="relay_non_loopback_requires_tls"):
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host="relay.example",
        )


def test_config_ssl_incomplete_raises() -> None:
    with pytest.raises(RelayServerError, match="relay_ssl_config_incomplete"):
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host="127.0.0.1",
            ssl_certfile="/tmp/relay-cert.pem",
        )


def test_build_relay_bootstrap_record_unsigned() -> None:
    record = build_relay_bootstrap_record(_server_config(), issued_epoch=0, expires_epoch=4)

    assert record["schema_version"] == "relay_bootstrap_record_v0.1"
    assert record["signature"] is None
    assert record["signing_key_id"] is None
    assert record["relay_agent_id"] == RELAY_AGENT_ID
    assert record["control_url"] == "http://127.0.0.1:51151"
    assert record["data_port_range"] == {"end": 52999, "start": 52000}


def test_build_relay_bootstrap_record_payload_sha384() -> None:
    record = build_relay_bootstrap_record(_server_config(), issued_epoch=0, expires_epoch=4)
    payload = {
        key: record[key]
        for key in (
            "control_url",
            "control_port",
            "data_port_range",
            "expires_epoch",
            "issued_epoch",
            "network_id",
            "relay_agent_id",
            "relay_host",
            "relay_mode",
            "schema_version",
            "tls_cert_der_sha256",
            "tls_mode",
        )
    }
    expected = hashlib.sha384(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    assert len(record["payload_sha384"]) == 96
    assert record["payload_sha384"] == expected


def test_build_relay_bootstrap_record_epoch_invalid() -> None:
    with pytest.raises(RelayServerError, match="relay_bootstrap_record_epoch_invalid"):
        build_relay_bootstrap_record(_server_config(), issued_epoch=4, expires_epoch=4)


def test_bootstrap_record_pinned_der_sha256_requires_cert_hash() -> None:
    with pytest.raises(RelayServerError, match="relay_bootstrap_tls_cert_der_sha256_required"):
        build_relay_bootstrap_record(
            _server_config(),
            issued_epoch=0,
            expires_epoch=4,
            tls_mode="pinned_der_sha256",
        )


def test_bootstrap_record_loopback_mode_forbids_cert_hash() -> None:
    with pytest.raises(RelayServerError, match="relay_bootstrap_loopback_tls_cert_pin_forbidden"):
        build_relay_bootstrap_record(
            _server_config(),
            issued_epoch=0,
            expires_epoch=4,
            tls_cert_der_sha256="12" * 32,
            tls_mode="loopback_only",
        )


def test_sign_and_verify_relay_bootstrap_record_recomputes_payload_hash() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    config = RelayServerConfig(
        relay_agent_id=relay_agent_id,
        relay_host="relay.example",
        ssl_certfile="/tmp/relay-cert.pem",
        ssl_keyfile="/tmp/relay-key.pem",
    )
    unsigned = build_relay_bootstrap_record(
        config,
        issued_epoch=0,
        expires_epoch=4,
        tls_cert_der_sha256="12" * 32,
    )
    signed = sign_relay_bootstrap_record(
        unsigned,
        relay_secret_key_hex=relay_secret_key,
        signing_key_id=relay_agent_id,
    )

    assert signed["signature"] is not None
    assert relay_bootstrap_record_payload_ref(signed) == signed["payload_sha384"]
    assert verify_relay_bootstrap_record(signed) is True

    tampered = {**signed, "relay_host": "evil.example"}
    assert verify_relay_bootstrap_record(tampered) is False

    with_extra_field = {**signed, "unsigned_extra": "must-not-ride-along"}
    assert verify_relay_bootstrap_record(with_extra_field) is False
    with pytest.raises(RelayServerError, match="relay_bootstrap_record_keys_invalid"):
        relay_bootstrap_record_payload_ref(with_extra_field)


def test_bootstrap_record_rejects_control_url_host_mismatch() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(
            relay_agent_id=relay_agent_id,
            relay_host="relay.example",
            ssl_certfile="/tmp/relay-cert.pem",
            ssl_keyfile="/tmp/relay-key.pem",
        ),
        issued_epoch=0,
        expires_epoch=4,
        tls_cert_der_sha256="12" * 32,
    )
    tampered = {**unsigned, "control_url": "https://evil.example:51151"}

    with pytest.raises(RelayServerError, match="relay_bootstrap_control_url_host_mismatch"):
        sign_relay_bootstrap_record(
            tampered,
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=relay_agent_id,
        )


def test_bootstrap_record_rejects_control_url_port_mismatch() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(
            relay_agent_id=relay_agent_id,
            relay_host="relay.example",
            ssl_certfile="/tmp/relay-cert.pem",
            ssl_keyfile="/tmp/relay-key.pem",
        ),
        issued_epoch=0,
        expires_epoch=4,
        tls_cert_der_sha256="12" * 32,
    )
    tampered = {**unsigned, "control_url": "https://relay.example:51152"}

    with pytest.raises(RelayServerError, match="relay_bootstrap_control_url_port_mismatch"):
        sign_relay_bootstrap_record(
            tampered,
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=relay_agent_id,
        )


@pytest.mark.parametrize(
    ("control_url", "error_token"),
    [
        ("https://relay.example:51151/path", "relay_bootstrap_control_url_not_root"),
        ("https://relay.example:51151?x=1", "relay_bootstrap_control_url_not_root"),
        ("https://relay.example:51151#frag", "relay_bootstrap_control_url_not_root"),
        (
            "https://user:pass@relay.example:51151",
            "relay_bootstrap_control_url_invalid_authority",
        ),
    ],
)
def test_bootstrap_record_rejects_non_root_control_url_authority(
    control_url: str,
    error_token: str,
) -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(
            relay_agent_id=relay_agent_id,
            relay_host="relay.example",
            ssl_certfile="/tmp/relay-cert.pem",
            ssl_keyfile="/tmp/relay-key.pem",
        ),
        issued_epoch=0,
        expires_epoch=4,
        tls_cert_der_sha256="12" * 32,
    )
    tampered = {**unsigned, "control_url": control_url}

    with pytest.raises(RelayServerError, match=error_token):
        sign_relay_bootstrap_record(
            tampered,
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=relay_agent_id,
        )


def test_sign_relay_bootstrap_record_rejects_wrong_signing_key_id() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    _other_secret_key, other_agent_id = keypair_from_ikm_hex("46" * 32)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )

    with pytest.raises(RelayServerError, match="relay_bootstrap_signing_key_mismatch"):
        sign_relay_bootstrap_record(
            unsigned,
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=other_agent_id,
        )


def test_sign_relay_bootstrap_record_rejects_mismatched_secret_key() -> None:
    _relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    other_secret_key, _other_agent_id = keypair_from_ikm_hex("46" * 32)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )

    with pytest.raises(RelayServerError, match="relay_bootstrap_signature_self_check_failed"):
        sign_relay_bootstrap_record(
            unsigned,
            relay_secret_key_hex=other_secret_key,
            signing_key_id=relay_agent_id,
        )


def test_parse_relay_bootstrap_capsule_verifies_genesis_and_relay_signatures() -> None:
    genesis_secret_key, genesis_agent_id = keypair_from_ikm_hex("47" * 32)
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    signed = sign_relay_bootstrap_record(
        unsigned,
        relay_secret_key_hex=relay_secret_key,
        signing_key_id=relay_agent_id,
    )
    capsule_payload = {
        "expires_epoch": 4,
        "issued_epoch": 0,
        "network_id": "public-rc",
        "relay_records": [signed],
        "schema_version": "relay_bootstrap_capsule_v0.1",
    }
    payload_ref = relay_bootstrap_capsule_payload_ref(capsule_payload)
    capsule = {
        **capsule_payload,
        "payload_sha384": payload_ref,
        "signature": sign_relay_bootstrap_capsule_digest(
            secret_key_hex=genesis_secret_key,
            digest_hex=payload_ref,
        ),
        "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
        "signing_key_id": genesis_agent_id,
    }

    assert parse_relay_bootstrap_capsule(
        capsule,
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=0,
    ) == (signed,)

    with_extra_field = {**capsule, "unsigned_extra": "must-not-ride-along"}
    assert parse_relay_bootstrap_capsule(
        with_extra_field,
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=0,
    ) == ()

    tampered_capsule = {**capsule, "network_id": "evil-rc"}
    assert parse_relay_bootstrap_capsule(
        tampered_capsule,
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=0,
    ) == ()


def test_parse_relay_bootstrap_capsule_filters_scope_and_epochs() -> None:
    genesis_secret_key, genesis_agent_id = keypair_from_ikm_hex("47" * 32)
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)

    def signed_record(
        *,
        network_id: str,
        issued_epoch: int,
        expires_epoch: int,
    ) -> dict[str, Any]:
        unsigned = build_relay_bootstrap_record(
            RelayServerConfig(
                relay_agent_id=relay_agent_id,
                relay_host="127.0.0.1",
                network_id=network_id,
            ),
            issued_epoch=issued_epoch,
            expires_epoch=expires_epoch,
        )
        return sign_relay_bootstrap_record(
            unsigned,
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=relay_agent_id,
        )

    valid = signed_record(network_id="public-rc", issued_epoch=0, expires_epoch=4)
    wrong_network = signed_record(network_id="other-rc", issued_epoch=0, expires_epoch=4)
    expired_record = signed_record(network_id="public-rc", issued_epoch=0, expires_epoch=1)

    def capsule_for(
        *,
        issued_epoch: int,
        expires_epoch: int,
        network_id: str = "public-rc",
        records: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "expires_epoch": expires_epoch,
            "issued_epoch": issued_epoch,
            "network_id": network_id,
            "relay_records": records or [valid],
            "schema_version": "relay_bootstrap_capsule_v0.1",
        }
        payload_ref = relay_bootstrap_capsule_payload_ref(payload)
        return {
            **payload,
            "payload_sha384": payload_ref,
            "signature": sign_relay_bootstrap_capsule_digest(
                secret_key_hex=genesis_secret_key,
                digest_hex=payload_ref,
            ),
            "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
            "signing_key_id": genesis_agent_id,
        }

    assert parse_relay_bootstrap_capsule(
        capsule_for(issued_epoch=0, expires_epoch=4),
        genesis_agent_id=genesis_agent_id,
        expected_network_id="other-rc",
        current_epoch=0,
    ) == ()
    assert parse_relay_bootstrap_capsule(
        capsule_for(issued_epoch=0, expires_epoch=4),
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=5,
    ) == ()
    assert parse_relay_bootstrap_capsule(
        capsule_for(issued_epoch=2, expires_epoch=4),
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=1,
    ) == ()
    assert parse_relay_bootstrap_capsule(
        capsule_for(records=[valid, wrong_network, expired_record], issued_epoch=0, expires_epoch=4),
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=2,
    ) == (valid,)


def test_sign_relay_bootstrap_record_rejects_payload_ref_mismatch() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    stale = {**unsigned, "payload_sha384": "12" * 48}

    with pytest.raises(RelayServerError, match="relay_bootstrap_payload_ref_mismatch"):
        sign_relay_bootstrap_record(
            stale,
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=relay_agent_id,
        )


def test_sign_relay_bootstrap_record_rejects_already_signed_record() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )

    with pytest.raises(RelayServerError, match="relay_bootstrap_record_already_signed"):
        sign_relay_bootstrap_record(
            {**unsigned, "signature": "12" * 96},
            relay_secret_key_hex=relay_secret_key,
            signing_key_id=relay_agent_id,
        )


def test_verify_relay_bootstrap_record_rejects_invite_pop_dst_signature() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    wrong_dst_signature = sign_invite_pop_digest(relay_secret_key, unsigned["payload_sha384"])
    signed_wrong_dst = {
        **unsigned,
        "signature": wrong_dst_signature,
        "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
        "signing_key_id": relay_agent_id,
    }

    assert verify_relay_bootstrap_record(signed_wrong_dst) is False


def test_verify_relay_bootstrap_record_rejects_non_matching_signing_key() -> None:
    _relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    other_secret_key, other_agent_id = keypair_from_ikm_hex("46" * 32)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    wrong_signature = sign_relay_bootstrap_record_digest(
        secret_key_hex=other_secret_key,
        digest_hex=unsigned["payload_sha384"],
    )
    assert other_agent_id != relay_agent_id
    forged = {
        **unsigned,
        "signature": wrong_signature,
        "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
        "signing_key_id": relay_agent_id,
    }

    assert verify_relay_bootstrap_record(forged) is False


def test_parse_relay_bootstrap_capsule_rejects_too_many_records() -> None:
    genesis_secret_key, genesis_agent_id = keypair_from_ikm_hex("47" * 32)
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    signed = sign_relay_bootstrap_record(
        unsigned,
        relay_secret_key_hex=relay_secret_key,
        signing_key_id=relay_agent_id,
    )
    payload = {
        "expires_epoch": 4,
        "issued_epoch": 0,
        "network_id": "public-rc",
        "relay_records": [signed] * 9,
        "schema_version": "relay_bootstrap_capsule_v0.1",
    }
    payload_ref = hashlib.sha384(
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    capsule = {
        **payload,
        "payload_sha384": payload_ref,
        "signature": sign_relay_bootstrap_capsule_digest(
            secret_key_hex=genesis_secret_key,
            digest_hex=payload_ref,
        ),
        "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
        "signing_key_id": genesis_agent_id,
    }

    assert parse_relay_bootstrap_capsule(
        capsule,
        genesis_agent_id=genesis_agent_id,
        expected_network_id="public-rc",
        current_epoch=0,
    ) == ()


def test_bootstrap_record_rejects_bad_relay_mode() -> None:
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    unsigned = build_relay_bootstrap_record(
        RelayServerConfig(relay_agent_id=relay_agent_id, relay_host="127.0.0.1"),
        issued_epoch=0,
        expires_epoch=4,
    )
    signed = sign_relay_bootstrap_record(
        unsigned,
        relay_secret_key_hex=relay_secret_key,
        signing_key_id=relay_agent_id,
    )

    assert verify_relay_bootstrap_record({**signed, "relay_mode": "terminating_proxy"}) is False


def test_non_loopback_bootstrap_record_defaults_to_pinned_der_sha256() -> None:
    _relay_secret_key, relay_agent_id = keypair_from_ikm_hex(SECOND_IKM_HEX)
    config = RelayServerConfig(
        relay_agent_id=relay_agent_id,
        relay_host="relay.example",
        ssl_certfile="/tmp/relay-cert.pem",
        ssl_keyfile="/tmp/relay-key.pem",
    )

    record = build_relay_bootstrap_record(
        config,
        issued_epoch=0,
        expires_epoch=4,
        tls_cert_der_sha256="12" * 32,
    )

    assert record["tls_mode"] == "pinned_der_sha256"
    assert record["tls_cert_der_sha256"] == "12" * 32


def test_relay_cli_help_exposes_serve_entrypoint() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "relay", "serve", "--help"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "--relay-host" in result.stdout
    assert "--bind-host" in result.stdout
    assert "--ssl-certfile" in result.stdout


def test_relay_service_template_uses_committed_cli_entrypoint() -> None:
    template = Path("tools/relay_service_template.service").read_text(encoding="utf-8")

    assert "ilc relay serve" in template
    assert "User=ilcops" in template
    assert "Group=ilcops" in template
    assert "--relay-host ${ILC_RELAY_HOST}" in template
    assert "--bind-host ${ILC_RELAY_BIND_HOST}" in template
    assert "NoNewPrivileges=true" in template
    assert "MemoryMax=512M" in template


def test_run_relay_http_server_passes_bind_host_to_data_plane(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeRelayRendezvousServer:
        def __init__(self, config: RelayServerConfig, **kwargs: object) -> None:
            captured["config"] = config
            captured.update(kwargs)
            self._data_plane = None

    class FakeHttpServer:
        def __init__(self, address: tuple[str, int], _handler: object) -> None:
            captured["address"] = address
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def serve_forever(self) -> None:
            return

        def server_close(self) -> None:
            self.socket.close()

    monkeypatch.setattr(relay_server_module, "RelayRendezvousServer", FakeRelayRendezvousServer)
    monkeypatch.setattr(relay_server_module, "ThreadingHTTPServer", FakeHttpServer)
    monkeypatch.setattr(relay_server_module, "RELAY_SERVER_NOT_ACTIVATED", False)

    run_relay_http_server(
        config=_server_config(),
        bind_host="127.0.0.1",
    )

    assert captured["address"] == ("127.0.0.1", 51151)
    assert captured["enable_data_plane"] is True
    assert captured["data_plane_bind_host"] == "127.0.0.1"


def test_request_slot_returns_allocated_port() -> None:
    _, _agent_id, payload = _admission_request()
    status, body = _server().handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )

    assert status == 200
    grant = RelaySlotGrant.from_dict(body["grant"])
    assert 52000 <= grant.relay_endpoint.port <= 52999
    assert grant.relay_endpoint.port != RELAY_PORT


def test_request_slot_port_released_on_data_plane_open_error() -> None:
    class FailingDataPlane:
        def open_slot(self, *_args: object, **_kwargs: object) -> None:
            raise RelayServerError("relay_data_plane_open_failed")

        def close_slot(self, _slot_id: str) -> int:
            raise RelayServerError("relay_data_plane_slot_not_open")

    server = _server()
    server._data_plane = FailingDataPlane()  # type: ignore[assignment]
    _, _agent_id, payload = _admission_request()

    with pytest.raises(RelayServerError, match="relay_data_plane_open_failed"):
        server.request_slot(payload)

    assert server._port_pool.available_count == 1000


def _udp_socket() -> socket.socket:
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("127.0.0.1", 0))
    udp.settimeout(2.0)
    return udp


def _data_plane_server_for_target(target_port: int) -> tuple[RelayRendezvousServer, RelaySlotGrant]:
    server = RelayRendezvousServer(
        _server_config(),
        enable_data_plane=True,
        epoch_provider=lambda: 0,
        data_plane_bind_host="127.0.0.1",
    )
    _, _agent_id, payload = _admission_request(requested_internal_port=target_port)
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
        source_host="127.0.0.1",
    )
    assert status == 200
    return server, RelaySlotGrant.from_dict(body["grant"])


def test_udp_forwarder_client_to_peer_real_socket() -> None:
    peer = _udp_socket()
    client = _udp_socket()
    server, grant = _data_plane_server_for_target(peer.getsockname()[1])
    try:
        relay_addr = ("127.0.0.1", grant.relay_endpoint.port)
        client.sendto(relay_slot_claim_datagram(grant), relay_addr)
        peer.sendto(b"peer-binds-slot", relay_addr)
        assert client.recvfrom(1024)[0] == b"peer-binds-slot"
        client.sendto(b"client-to-peer", relay_addr)
        data, _addr = peer.recvfrom(1024)
    finally:
        server._data_plane.stop() if server._data_plane is not None else None
        peer.close()
        client.close()

    assert data == b"client-to-peer"


def test_udp_forwarder_peer_to_client_real_socket() -> None:
    peer = _udp_socket()
    client = _udp_socket()
    server, grant = _data_plane_server_for_target(peer.getsockname()[1])
    try:
        relay_addr = ("127.0.0.1", grant.relay_endpoint.port)
        client.sendto(relay_slot_claim_datagram(grant), relay_addr)
        peer.sendto(b"peer-to-client", relay_addr)
        data, _addr = client.recvfrom(1024)
    finally:
        server._data_plane.stop() if server._data_plane is not None else None
        peer.close()
        client.close()

    assert data == b"peer-to-client"


def test_udp_forwarder_unknown_source_dropped_real_socket() -> None:
    peer = _udp_socket()
    client = _udp_socket()
    stranger = _udp_socket()
    server, grant = _data_plane_server_for_target(peer.getsockname()[1])
    try:
        relay_addr = ("127.0.0.1", grant.relay_endpoint.port)
        client.sendto(relay_slot_claim_datagram(grant), relay_addr)
        peer.sendto(b"learn-peer", relay_addr)
        assert client.recvfrom(1024)[0] == b"learn-peer"
        stranger.sendto(b"stranger", relay_addr)
        with pytest.raises(TimeoutError):
            peer.recvfrom(1024)
    finally:
        server._data_plane.stop() if server._data_plane is not None else None
        peer.close()
        client.close()
        stranger.close()


def test_udp_forwarder_client_addr_learned_on_first_packet() -> None:
    receipts: list[RelayForwardReceipt] = []
    server = _server()
    _, _agent_id, payload = _admission_request()
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_ADMISSION_REQUEST_PATH,
        payload=payload,
    )
    assert status == 200
    slot = RelaySlotGrant.from_dict(body["grant"])
    client = ("198.51.100.10", 50000)
    peer = ("198.51.100.11", 50001)
    protocol = RelayUdpPortForwarder(
        server,
        slot_id=slot.slot_id,
        target_host=peer[0],
        target_port=peer[1],
        relay_slot_nonce=slot.relay_slot_nonce,
        epoch_provider=lambda: 0,
        receipt_sink=lambda receipt, _addr: receipts.append(receipt),
    )

    class FakeTransport(asyncio.DatagramTransport):
        def __init__(self) -> None:
            self.sends: list[tuple[bytes, tuple[str, int]]] = []

        def sendto(self, data: bytes, addr: tuple[str, int] | None = None) -> None:
            assert addr is not None
            self.sends.append((data, addr))

    transport = FakeTransport()
    protocol.connection_made(transport)
    protocol.datagram_received(bytes.fromhex(slot.relay_slot_nonce), client)
    protocol.datagram_received(b"peer-first", peer)
    protocol.datagram_received(b"client-second", client)

    assert protocol.client_addr == client
    assert transport.sends == [
        (b"peer-first", client),
        (b"client-second", peer),
    ]
    assert [receipt.bytes_forwarded for receipt in receipts] == [10, 13]


def test_udp_forwarder_claim_only_nonce_does_not_forward() -> None:
    receipts: list[RelayForwardReceipt] = []
    server = _server()
    _secret_key, _agent_id, slot = _grant(server)
    peer = ("198.51.100.11", 50001)
    protocol = RelayUdpPortForwarder(
        server,
        slot_id=slot.slot_id,
        target_host=peer[0],
        target_port=peer[1],
        relay_slot_nonce=slot.relay_slot_nonce,
        epoch_provider=lambda: 0,
        receipt_sink=lambda receipt, _addr: receipts.append(receipt),
    )

    class FakeTransport(asyncio.DatagramTransport):
        def __init__(self) -> None:
            self.sends: list[tuple[bytes, tuple[str, int]]] = []

        def sendto(self, data: bytes, addr: tuple[str, int] | None = None) -> None:
            assert addr is not None
            self.sends.append((data, addr))

    transport = FakeTransport()
    protocol.connection_made(transport)
    protocol.datagram_received(relay_slot_claim_datagram(slot), ("198.51.100.10", 50000))

    assert protocol.last_error is None
    assert protocol.client_addr == ("198.51.100.10", 50000)
    assert transport.sends == []
    assert receipts == []


def test_udp_forwarder_wrong_nonce_does_not_register_client() -> None:
    server = _server()
    _secret_key, _agent_id, slot = _grant(server)
    protocol = RelayUdpPortForwarder(
        server,
        slot_id=slot.slot_id,
        target_host="127.0.0.1",
        target_port=50151,
        relay_slot_nonce=slot.relay_slot_nonce,
        epoch_provider=lambda: 0,
    )

    class FakeTransport(asyncio.DatagramTransport):
        def sendto(self, _data: bytes, _addr: tuple[str, int] | None = None) -> None:
            raise AssertionError("wrong nonce must not forward")

    protocol.connection_made(FakeTransport())
    protocol.datagram_received(b"wrong-nonce", ("198.51.100.20", 50001))

    assert protocol.last_error == "relay_udp_nonce_mismatch"
    assert protocol.client_addr is None


def test_udp_forwarder_preclaim_attacker_does_not_poison_nonce_state() -> None:
    receipts: list[RelayForwardReceipt] = []
    server = _server()
    _secret_key, _agent_id, slot = _grant(server)
    target = ("198.51.100.33", 50005)
    protocol = RelayUdpPortForwarder(
        server,
        slot_id=slot.slot_id,
        target_host=target[0],
        target_port=target[1],
        relay_slot_nonce=slot.relay_slot_nonce,
        epoch_provider=lambda: 0,
        receipt_sink=lambda receipt, _addr: receipts.append(receipt),
    )

    class FakeTransport(asyncio.DatagramTransport):
        def __init__(self) -> None:
            self.sends: list[tuple[bytes, tuple[str, int]]] = []

        def sendto(self, data: bytes, addr: tuple[str, int] | None = None) -> None:
            assert addr is not None
            self.sends.append((data, addr))

    transport = FakeTransport()
    protocol.connection_made(transport)
    protocol.datagram_received(b"attacker-data", ("198.51.100.30", 50002))
    assert protocol.last_error == "relay_udp_nonce_mismatch"
    assert protocol.client_addr is None

    client = ("198.51.100.31", 50003)
    protocol.datagram_received(relay_slot_claim_datagram(slot), client)
    protocol.datagram_received(b"peer-payload", target)
    protocol.datagram_received(b"client-payload", client)

    assert protocol.client_addr == client
    assert transport.sends == [(b"peer-payload", client), (b"client-payload", target)]
    assert [receipt.bytes_forwarded for receipt in receipts] == [12, 14]


def test_udp_forwarder_nonce_prefixed_payload_forwards_to_request_bound_target() -> None:
    server = _server()
    _secret_key, _agent_id, slot = _grant(server)
    target = ("198.51.100.40", 50151)
    protocol = RelayUdpPortForwarder(
        server,
        slot_id=slot.slot_id,
        target_host=target[0],
        target_port=target[1],
        relay_slot_nonce=slot.relay_slot_nonce,
        epoch_provider=lambda: 0,
    )

    class FakeTransport(asyncio.DatagramTransport):
        def __init__(self) -> None:
            self.sends: list[tuple[bytes, tuple[str, int]]] = []

        def sendto(self, data: bytes, addr: tuple[str, int] | None = None) -> None:
            assert addr is not None
            self.sends.append((data, addr))

    transport = FakeTransport()
    protocol.connection_made(transport)
    protocol.datagram_received(
        relay_slot_claim_datagram(slot) + b"first-payload",
        ("198.51.100.32", 50004),
    )

    assert protocol.last_error is None
    assert protocol.client_addr == ("198.51.100.32", 50004)
    assert transport.sends == [(b"first-payload", target)]


def test_udp_forwarder_rejects_unbound_target_source() -> None:
    receipts: list[RelayForwardReceipt] = []
    server = _server()
    _secret_key, _agent_id, slot = _grant(server)
    client = ("198.51.100.50", 53032)
    target = ("198.51.100.51", 53031)
    stranger = ("198.51.100.52", 53031)
    protocol = RelayUdpPortForwarder(
        server,
        slot_id=slot.slot_id,
        target_host=target[0],
        target_port=target[1],
        relay_slot_nonce=slot.relay_slot_nonce,
        epoch_provider=lambda: 0,
        receipt_sink=lambda receipt, _addr: receipts.append(receipt),
    )

    class FakeTransport(asyncio.DatagramTransport):
        def __init__(self) -> None:
            self.sends: list[tuple[bytes, tuple[str, int]]] = []

        def sendto(self, data: bytes, addr: tuple[str, int] | None = None) -> None:
            assert addr is not None
            self.sends.append((data, addr))

    transport = FakeTransport()
    protocol.connection_made(transport)
    protocol.datagram_received(relay_slot_claim_datagram(slot), client)
    protocol.datagram_received(b"stranger-tries-to-bind", stranger)
    protocol.datagram_received(b"target-to-client", target)

    assert protocol.last_error is None
    assert transport.sends == [(b"target-to-client", client)]
    assert [receipt.bytes_forwarded for receipt in receipts] == [16]


def test_data_plane_start_stop_releases_port() -> None:
    server = _server()
    pool = _RelayPortPool(52020, 52020)
    runtime = RelayDataPlaneRuntime(
        server,
        pool,
        epoch_provider=lambda: 0,
        bind_host="127.0.0.1",
    )
    runtime.start()
    allocated_port = pool.allocate()
    runtime.open_slot(
        "slot-data-plane",
        target_host="127.0.0.1",
        target_port=50151,
        allocated_port=allocated_port,
        relay_slot_nonce="ab" * 32,
    )
    assert runtime.close_slot("slot-data-plane") == allocated_port
    pool.release(allocated_port)
    runtime.stop()

    assert pool.available_count == 1


def test_data_plane_duplicate_start_raises() -> None:
    runtime = RelayDataPlaneRuntime(
        _server(),
        _RelayPortPool(52020, 52020),
        epoch_provider=lambda: 0,
        bind_host="127.0.0.1",
    )
    runtime.start()
    try:
        with pytest.raises(RelayServerError, match="relay_data_plane_already_running"):
            runtime.start()
    finally:
        runtime.stop()


def test_deploy_prompt_requires_audit_fix_and_topology_smoke_gate() -> None:
    prompt = Path(
        "docs/antigravity_tasks/"
        "antigravity_prompt__phase_gap_relay_rendezvous_deploy_00_g10_relay_server_deployment.md"
    ).read_text(encoding="utf-8")

    assert "relay_audit_fix_committed_GAP_RELAY_AUDIT_FIX_00" in prompt
    assert "3-socket topology smoke" in prompt
    assert "completion forbidden if this cannot be run" in prompt
    assert "sufficient for relay-assisted peer connectivity" not in prompt


def test_fix2_prompt_uses_current_data_port_range_flag_names() -> None:
    prompt = Path(
        "docs/antigravity_tasks/"
        "antigravity_prompt__phase_gap_relay_deploy_surface_fix2_00_g10_relay_deploy_surface.md"
    ).read_text(encoding="utf-8")

    assert "--data-port-range-start" in prompt
    assert "--data-port-range-end" in prompt
    assert "--data-port-start" not in prompt
    assert "--data-port-end" not in prompt
