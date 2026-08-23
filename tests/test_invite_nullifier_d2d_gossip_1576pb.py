# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1576p-b invite nullifier D2D gossip tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invitation_provenance_record import (
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_agent_id_from_identity_seed,
)
from ilc_core.genesis.invite_nullifier_registry import (
    InviteNullifierError,
    InviteNullifierRegistry,
)
from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d import http_gossip_transport_runtime as http_runtime
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.invite_nullifier_gossip import (
    INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE,
    INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION,
    MAX_CLAIMED_ACTOR_CHARS,
    build_nullifier_gossip_message,
    decode_nullifier_gossip_payload,
    encode_nullifier_gossip_payload,
    handle_nullifier_gossip_message,
)
from ilc_core.sidecars.openclaw_invite_bootstrap import (
    CROSS_NODE_REPLAY_PREVENTION_GAP,
    InviteNullifierStore,
    MAX_NULLIFIER_STORE_BYTES,
    NULLIFIER_STORE_SCHEMA_VERSION,
    _invite_nonce_merkle_proof_length,
    build_synthetic_invite_bundle,
    derive_redemption_nullifier,
    verify_invite_bootstrap,
)


NULLIFIER = "1" * 64
PROFILE = "openclaw_public_rc_bootstrap"
IDENTITY_SEED_HEX = "22" * 32
REDEEMER_AGENT_ID = derive_agent_id_from_identity_seed(IDENTITY_SEED_HEX)
_SIG_VALID = "c" * 6618
_PUBKEY_VALID = "a" * 3328
_PEER_ID = "peer-a"
_KEY_ID = "key-a"
_CLAIMED_ACTOR = "agent-alpha"


def _headers(*, gossip_type: str = INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE) -> dict[str, str]:
    return gossip_transport.build_gossip_headers(
        gossip_type=gossip_type,
        channel="cid:1576feed1576feed",
        epoch=0,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature=_SIG_VALID,
        sender_peer_id="peer-unverifiable",
        key_id="key-unverifiable",
        content_type="application/json",
    )


def _path(headers: dict[str, str]) -> str:
    return gossip_transport.gossip_request_path(headers["ILC-Gossip-Type"])


def _transport() -> http_runtime.HttpGossipTransportRuntime:
    return http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        peer_registry=GossipPeerRegistry(["https://example.org"]),
    )


def _structured_registry() -> GossipPeerRegistry:
    return GossipPeerRegistry(
        [
            {
                "authorized_actor_ids": [_CLAIMED_ACTOR],
                "endpoint": "https://example.org",
                "key_id": _KEY_ID,
                "mldsa_pubkey_hex": _PUBKEY_VALID,
                "peer_id": _PEER_ID,
                "valid_from_epoch": 0,
                "valid_until_epoch": None,
            }
        ]
    )


def _signed_headers() -> dict[str, str]:
    return gossip_transport.build_gossip_headers(
        gossip_type=INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE,
        channel="cid:1576feed1576feed",
        epoch=0,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature=_SIG_VALID,
        sender_peer_id=_PEER_ID,
        key_id=_KEY_ID,
        content_type="application/json",
    )


def _valid_redemption(*, batch_id: str = "batch-1576pb"):
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id=batch_id,
        count=1,
        created_epoch=0,
        inviter_sig="genesis",
        nonces=(bytes.fromhex("11" * 32),),
    )
    return build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer",
        identity_seed=IDENTITY_SEED_HEX,
        redemption_epoch=0,
    )


def test_build_message_uses_canonical_type_and_schema() -> None:
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)

    assert message == {
        "claimed_actor": _CLAIMED_ACTOR,
        "message_type": INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE,
        "nullifier_hex": NULLIFIER,
        "schema_version": INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION,
    }


def test_uppercase_nullifier_rejected() -> None:
    with pytest.raises(InviteNullifierError, match="invite_nullifier_gossip_invalid_hex"):
        build_nullifier_gossip_message("A" * 64, claimed_actor=_CLAIMED_ACTOR)


@pytest.mark.parametrize(
    "claimed_actor",
    ["", " agent-alpha", "agent alpha", "a" * (MAX_CLAIMED_ACTOR_CHARS + 1)],
)
def test_claimed_actor_required_bounded_and_whitespace_free(claimed_actor: str) -> None:
    with pytest.raises(InviteNullifierError, match="invite_nullifier_gossip_claimed_actor_invalid"):
        build_nullifier_gossip_message(NULLIFIER, claimed_actor=claimed_actor)


def test_unknown_key_rejected() -> None:
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)
    message["extra"] = "unexpected"

    with pytest.raises(InviteNullifierError, match="invite_nullifier_gossip_message_unknown_key"):
        encode_nullifier_gossip_payload(message)


def test_payload_round_trip_is_deterministic_json() -> None:
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)
    payload = encode_nullifier_gossip_payload(message)

    assert payload == json.dumps(message, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    assert decode_nullifier_gossip_payload(payload) == message


def test_handle_registers_incoming_nullifier_once() -> None:
    registry = InviteNullifierRegistry()
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)

    first = handle_nullifier_gossip_message(message, registry)
    second = handle_nullifier_gossip_message(message, registry)

    assert first == "registered"
    assert second == "duplicate_discarded"
    assert registry.is_known(NULLIFIER) is True
    assert len(registry) == 1


def test_cross_node_gossip_blocks_redeemed_invite_when_enforcement_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(invite_enforcement, "INVITE_ENFORCEMENT_ENABLED", True)
    registry_node_b = InviteNullifierRegistry()
    redemption = _valid_redemption()
    message = build_nullifier_gossip_message(
        redemption.redemption_nullifier,
        claimed_actor=_CLAIMED_ACTOR,
    )

    handle_nullifier_gossip_message(message, registry_node_b)

    with pytest.raises(ValueError, match="invite_nullifier_already_used_for_enrollment"):
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            nullifier_registry=registry_node_b,
            require_redeemer_key_binding=False,
        )


def test_openclaw_broadcasts_after_local_registration(tmp_path: Path) -> None:
    registry = InviteNullifierRegistry()
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    nullifier = derive_redemption_nullifier(
        "openclaw-fix2d-batch",
        str(bundle["private_invite_nonce"]),
    )
    messages: list[dict[str, str]] = []

    def broadcaster(message: dict[str, str]) -> None:
        assert registry.is_known(nullifier) is True
        messages.append(message)

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        nullifier_store=InviteNullifierStore(tmp_path / "invite_nullifiers.json"),
        nullifier_gossip_broadcaster=broadcaster,
        nullifier_gossip_claimed_actor=_CLAIMED_ACTOR,
        persist_nullifier=False,
    )

    assert decision.bootstrap_allowed is True
    assert decision.nullifier_gossip_status == "broadcast_requested"
    assert decision.nullifier_status == "local_recorded_not_persisted"
    assert messages == [
        build_nullifier_gossip_message(nullifier, claimed_actor=_CLAIMED_ACTOR)
    ]
    assert decision.to_dict()["nullifier_gossip_status"] == "broadcast_requested"


def test_openclaw_broadcast_failure_does_not_deny_local_acceptance(tmp_path: Path) -> None:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)

    def broadcaster(_message: dict[str, str]) -> None:
        raise OSError("transport unavailable")

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(tmp_path / "invite_nullifiers.json"),
        nullifier_gossip_broadcaster=broadcaster,
        nullifier_gossip_claimed_actor=_CLAIMED_ACTOR,
        persist_nullifier=False,
    )

    assert decision.bootstrap_allowed is True
    assert decision.nullifier_gossip_status == "broadcast_failed:OSError"


def test_openclaw_broadcaster_without_claimed_actor_does_not_emit_unbound_gossip(tmp_path: Path) -> None:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    messages: list[dict[str, str]] = []

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(tmp_path / "invite_nullifiers.json"),
        nullifier_gossip_broadcaster=messages.append,
        persist_nullifier=False,
    )

    assert decision.bootstrap_allowed is True
    assert decision.nullifier_gossip_status == "broadcast_not_configured_claimed_actor_required"
    assert messages == []


def test_invite_nullifier_type_is_authority_bearing() -> None:
    assert INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE in http_runtime.AUTHORITY_BEARING_GOSSIP_TYPES


def test_unverifiable_invite_nullifier_gossip_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)
    payload = encode_nullifier_gossip_payload(message)
    headers = _headers()
    transport = _transport()
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", lambda *_: False)

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == (
        "gossip_signature_unverifiable_authority_rejected"
    )


def test_signed_http_invite_nullifier_gossip_updates_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = InviteNullifierRegistry()
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)
    payload = encode_nullifier_gossip_payload(message)
    headers = _signed_headers()
    expected_context = http_runtime._build_gossip_signed_context(headers, payload)

    def fake_verify(message_bytes: bytes, sig_hex: str, pubkey_hex: str) -> bool:
        return message_bytes == expected_context and sig_hex == _SIG_VALID and pubkey_hex == _PUBKEY_VALID

    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", fake_verify)
    transport = http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        invite_nullifier_registry=registry,
        peer_registry=_structured_registry(),
    )

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_BUFFERED
    assert registry.is_known(NULLIFIER) is True
    assert transport.state["event_log"][-2]["event"] == "incoming_invite_nullifier_gossip_applied"
    assert transport.state["event_log"][-2]["nullifier_status"] == "registered"


def test_signed_http_invite_nullifier_requires_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)
    payload = encode_nullifier_gossip_payload(message)
    headers = _signed_headers()
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", lambda *_: True)
    transport = http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        peer_registry=_structured_registry(),
    )

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "invite_nullifier_gossip_registry_not_configured"


def test_invite_nullifier_registry_config_error_does_not_poison_replay_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    message = build_nullifier_gossip_message(NULLIFIER, claimed_actor=_CLAIMED_ACTOR)
    payload = encode_nullifier_gossip_payload(message)
    headers = _signed_headers()
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", lambda *_: True)
    transport = http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        peer_registry=_structured_registry(),
    )

    first = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )
    registry = InviteNullifierRegistry()
    transport._invite_nullifier_registry = registry
    second = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert first == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert second == gossip_transport.HTTP_STATUS_BUFFERED
    assert registry.is_known(NULLIFIER) is True


def test_signed_http_invite_nullifier_requires_claimed_actor(monkeypatch: pytest.MonkeyPatch) -> None:
    message = {
        "message_type": INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE,
        "nullifier_hex": NULLIFIER,
        "schema_version": INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION,
    }
    payload = json.dumps(
        message,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    headers = _signed_headers()
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", lambda *_: True)
    transport = http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        invite_nullifier_registry=InviteNullifierRegistry(),
        peer_registry=_structured_registry(),
    )

    status = transport.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert transport.state["event_log"][-1]["token"] == "invite_nullifier_gossip_claimed_actor_required"


def test_invite_nullifier_transport_fanout_uses_signed_send_path(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = GossipPeerRegistry(
        [
            {
                "authorized_actor_ids": [_CLAIMED_ACTOR],
                "endpoint": "https://a.example.org",
                "key_id": _KEY_ID,
                "mldsa_pubkey_hex": _PUBKEY_VALID,
                "peer_id": _PEER_ID,
                "valid_from_epoch": 0,
            },
            {
                "authorized_actor_ids": [_CLAIMED_ACTOR],
                "endpoint": "https://b.example.org",
                "key_id": "key-b",
                "mldsa_pubkey_hex": "b" * 3328,
                "peer_id": "peer-b",
                "valid_from_epoch": 0,
            },
        ]
    )
    transport = http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
            transport_kind="http",
            bind_host="127.0.0.1",
            bind_port=0,
            tls_cert_path="not-used",
            tls_key_path="not-used",
        ),
        peer_registry=registry,
    )
    sent: list[dict[str, object]] = []

    def fake_send_gossip(
        endpoint: str,
        gossip_type: str,
        channel: str,
        epoch: int,
        signature: str,
        payload: bytes | str = b"",
        **kwargs: object,
    ) -> int:
        sent.append(
            {
                "channel": channel,
                "endpoint": endpoint,
                "epoch": epoch,
                "gossip_type": gossip_type,
                "kwargs": kwargs,
                "payload": payload,
                "signature": signature,
            }
        )
        return gossip_transport.HTTP_STATUS_BUFFERED

    monkeypatch.setattr(transport, "send_gossip", fake_send_gossip)

    statuses = transport.broadcast_invite_nullifier(
        NULLIFIER,
        channel="cid:1576feed1576feed",
        epoch=0,
        signature=_SIG_VALID,
        sender_peer_id=_PEER_ID,
        key_id=_KEY_ID,
        claimed_actor=_CLAIMED_ACTOR,
        fanout=1,
    )

    assert statuses == [
        {
            "endpoint": "https://a.example.org",
            "status_code": gossip_transport.HTTP_STATUS_BUFFERED,
        }
    ]
    assert len(sent) == 1
    assert sent[0]["gossip_type"] == INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE
    assert sent[0]["kwargs"] == {
        "content_type": "application/json",
        "key_id": _KEY_ID,
        "sender_peer_id": _PEER_ID,
    }
    assert decode_nullifier_gossip_payload(sent[0]["payload"]) == build_nullifier_gossip_message(
        NULLIFIER,
        claimed_actor=_CLAIMED_ACTOR,
    )


def test_nullifier_store_rejects_oversize_file_before_json_parse(tmp_path: Path) -> None:
    path = tmp_path / "invite_nullifiers.json"
    path.write_bytes(b"{" + (b" " * MAX_NULLIFIER_STORE_BYTES) + b"}")

    with pytest.raises(ValueError, match="openclaw_nullifier_store_too_large"):
        InviteNullifierStore(path)


def test_nullifier_store_rejects_corrupt_json_with_stable_token(tmp_path: Path) -> None:
    path = tmp_path / "invite_nullifiers.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="openclaw_nullifier_store_invalid"):
        InviteNullifierStore(path)


def test_nullifier_store_rejects_schema_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "invite_nullifiers.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "wrong",
                "used_nullifiers": {},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="openclaw_nullifier_store_schema_invalid"):
        InviteNullifierStore(path)


def test_invite_nonce_merkle_proof_length_handles_non_power_of_two_counts() -> None:
    assert _invite_nonce_merkle_proof_length(3) == 2
    assert _invite_nonce_merkle_proof_length(5) == 3
    assert _invite_nonce_merkle_proof_length(6) == 3


def test_cross_node_gap_annotation_closed() -> None:
    source = Path("ilc_core/sidecars/openclaw_invite_bootstrap.py").read_text(encoding="utf-8")

    assert "cross_node_replay_prevention_phase_1576pb" in source
    assert "cross_node_replay_prevention_phase_1576pb" in CROSS_NODE_REPLAY_PREVENTION_GAP
    assert "cross_node_d2d_propagation_remains_open_phase_1576p_b" not in CROSS_NODE_REPLAY_PREVENTION_GAP
