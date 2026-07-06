from __future__ import annotations

import json

from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d import http_gossip_transport_runtime as runtime


_PUBKEY_A = "a" * 3328
_PUBKEY_B = "b" * 3328
_SIG_VALID = "c" * 6618
_SIG_INVALID = "d" * 6618


def _registry(*, expired: bool = False) -> GossipPeerRegistry:
    return GossipPeerRegistry(
        [
            {
                "endpoint": "https://example.com",
                "peer_id": "peer-a",
                "mldsa_pubkey_hex": _PUBKEY_A,
                "key_id": "key-a",
                "valid_from_epoch": 0,
                "valid_until_epoch": 4 if expired else None,
                "authorized_actor_ids": ["actor-a"],
            },
            {
                "endpoint": "https://example.net",
                "peer_id": "peer-b",
                "mldsa_pubkey_hex": _PUBKEY_B,
                "key_id": "key-b",
                "valid_from_epoch": 0,
                "valid_until_epoch": None,
                "authorized_actor_ids": ["actor-b"],
            },
        ]
    )


def _headers(
    *,
    peer_id: str = "peer-a",
    key_id: str = "key-a",
    gossip_type: str = "centrality_delta",
    channel: str = "cid:1234567890abcdef",
    epoch: int = 5,
    signature: str = _SIG_VALID,
) -> dict[str, str]:
    return gossip_transport.build_gossip_headers(
        gossip_type=gossip_type,
        channel=channel,
        epoch=epoch,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature=signature,
        sender_peer_id=peer_id,
        key_id=key_id,
        content_type="application/json",
    )


def _transport(
    *,
    registry: GossipPeerRegistry | None = None,
) -> runtime.HttpGossipTransportRuntime:
    return runtime.HttpGossipTransportRuntime(
        runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        peer_registry=registry,
    )


def _path(headers: dict[str, str]) -> str:
    return gossip_transport.gossip_request_path(headers["ILC-Gossip-Type"])


def _json_payload(*, actor: str = "actor-a") -> bytes:
    return json.dumps({"claimed_actor": actor, "body": "ok"}, sort_keys=True).encode("utf-8")


def test_valid_envelope_accepted(monkeypatch) -> None:
    payload = _json_payload()
    headers = _headers()
    expected_context = runtime._build_gossip_signed_context(headers, payload)

    def fake_verify(message_bytes: bytes, sig_hex: str, pubkey_hex: str) -> bool:
        return message_bytes == expected_context and sig_hex == _SIG_VALID and pubkey_hex == _PUBKEY_A

    monkeypatch.setattr(runtime, "verify_mldsa65_signature", fake_verify)
    transport = _transport(registry=_registry())

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_BUFFERED
    assert transport.state["event_log"][-1]["event"] == "incoming_envelope_buffered"


def test_forged_sender_peer_id(monkeypatch) -> None:
    payload = _json_payload()
    original_headers = _headers(peer_id="peer-a", key_id="key-a")
    signed_context_for_peer_a = runtime._build_gossip_signed_context(original_headers, payload)
    forged_headers = _headers(peer_id="peer-b", key_id="key-b")

    def fake_verify(message_bytes: bytes, sig_hex: str, pubkey_hex: str) -> bool:
        return message_bytes == signed_context_for_peer_a and pubkey_hex == _PUBKEY_A

    monkeypatch.setattr(runtime, "verify_mldsa65_signature", fake_verify)
    transport = _transport(registry=_registry())

    status = transport.handle_gossip_request(
        _path(forged_headers),
        forged_headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "gossip_mldsa_signature_invalid"


def test_body_tamper(monkeypatch) -> None:
    original_payload = _json_payload()
    tampered_payload = _json_payload(actor="actor-a") + b" "
    headers = _headers()
    signed_context_for_original = runtime._build_gossip_signed_context(headers, original_payload)

    def fake_verify(message_bytes: bytes, sig_hex: str, pubkey_hex: str) -> bool:
        return message_bytes == signed_context_for_original

    monkeypatch.setattr(runtime, "verify_mldsa65_signature", fake_verify)
    transport = _transport(registry=_registry())

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(tampered_payload),
        payload=tampered_payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "gossip_mldsa_signature_invalid"


def test_routing_field_tamper(monkeypatch) -> None:
    payload = _json_payload()
    original_headers = _headers(channel="cid:1234567890abcdef")
    signed_context_for_original = runtime._build_gossip_signed_context(original_headers, payload)
    tampered_headers = _headers(channel="cid:ffffffffffffffff")

    def fake_verify(message_bytes: bytes, sig_hex: str, pubkey_hex: str) -> bool:
        return message_bytes == signed_context_for_original

    monkeypatch.setattr(runtime, "verify_mldsa65_signature", fake_verify)
    transport = _transport(registry=_registry())

    status = transport.handle_gossip_request(
        _path(tampered_headers),
        tampered_headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "gossip_mldsa_signature_invalid"


def test_replay_detected(monkeypatch) -> None:
    payload = _json_payload()
    headers = _headers()
    monkeypatch.setattr(runtime, "verify_mldsa65_signature", lambda *_: True)
    transport = _transport(registry=_registry())

    first = transport.handle_gossip_request(_path(headers), headers, content_length=len(payload), payload=payload)
    second = transport.handle_gossip_request(_path(headers), headers, content_length=len(payload), payload=payload)

    assert first == gossip_transport.HTTP_STATUS_BUFFERED
    assert second == gossip_transport.HTTP_STATUS_EPOCH_CONFLICT
    assert transport.state["event_log"][-1]["token"] == "gossip_replay_detected"


def test_actor_binding_mismatch(monkeypatch) -> None:
    payload = _json_payload(actor="actor-b")
    headers = _headers(gossip_type="agent_submission")
    monkeypatch.setattr(runtime, "verify_mldsa65_signature", lambda *_: True)
    transport = _transport(registry=_registry())

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "d2d_actor_binding_mismatch"


def test_invalid_packet_does_not_poison_replay_cache(monkeypatch) -> None:
    payload = _json_payload()
    bad_headers = _headers(signature=_SIG_INVALID)
    good_headers = _headers(signature=_SIG_VALID)

    def fake_verify(message_bytes: bytes, sig_hex: str, pubkey_hex: str) -> bool:
        return sig_hex == _SIG_VALID

    monkeypatch.setattr(runtime, "verify_mldsa65_signature", fake_verify)
    transport = _transport(registry=_registry())

    invalid = transport.handle_gossip_request(
        _path(bad_headers),
        bad_headers,
        content_length=len(payload),
        payload=payload,
    )
    valid = transport.handle_gossip_request(
        _path(good_headers),
        good_headers,
        content_length=len(payload),
        payload=payload,
    )

    assert invalid == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert valid == gossip_transport.HTTP_STATUS_BUFFERED


def test_unverifiable_peer_buffered(monkeypatch) -> None:
    payload = _json_payload()
    headers = _headers(peer_id="peer-unverifiable", key_id="key-unverifiable")
    transport = _transport(
        registry=GossipPeerRegistry(["https://example.org"])
    )
    monkeypatch.setattr(runtime, "verify_mldsa65_signature", lambda *_: False)

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_BUFFERED
    assert any(
        event.get("token") == "gossip_signature_unverifiable_no_pubkey"
        for event in transport.state["event_log"]
    )


def test_expired_key_rejected(monkeypatch) -> None:
    payload = _json_payload()
    headers = _headers(epoch=5)
    monkeypatch.setattr(runtime, "verify_mldsa65_signature", lambda *_: True)
    transport = _transport(registry=_registry(expired=True))

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "gossip_sender_key_expired"
