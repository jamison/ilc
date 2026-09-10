# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import copy
import json

import pytest

from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH, _MLDSA_SIG_HEX_LENGTH
from ilc_core.network.connectivity_mode import ConnectivityMode
from ilc_core.network.d2d import gossip_peer_registry as registry_module
from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d import http_gossip_transport_runtime as http_runtime
from ilc_core.network.d2d.gossip_peer_registry import (
    MAX_CONNECTIVITY_AD_UPDATES_PER_EPOCH,
    MAX_CONNECTIVITY_RATE_LIMIT_ENTRIES,
    N_MAX,
    GossipPeerRegistry,
)
from ilc_core.network.d2d.peer_advertisement import TransportEndpoint
from ilc_core.sidecars import connectivity_advertisement as ca
from ilc_core.sidecars.connectivity_advertisement import (
    CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE,
    CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED,
    CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE,
    ConnectivityAdvertisement,
    ConnectivityAdvertisementTombstone,
    ConnectivityAdvertisementValidationError,
    ConnectivityAdvertisementValidator,
    VerifiedConnectivityAdvertisement,
    VerifiedConnectivityAdvertisementTombstone,
    build_connectivity_advertisement_gossip_message,
    build_connectivity_advertisement_tombstone_gossip_message,
    decode_connectivity_advertisement_gossip_payload,
    encode_connectivity_advertisement_gossip_payload,
    encode_connectivity_advertisement_tombstone_gossip_payload,
    connectivity_advertisement_sidecar_manifest,
)


AGENT_ID = "1" * 96
OTHER_AGENT_ID = "2" * 96
THIRD_AGENT_ID = "3" * 96
DIGEST = "4" * 96
PROBE_REF = "5" * 96
SIG_HEX = "a" * _MLDSA_SIG_HEX_LENGTH
BAD_SIG_HEX = "b" * _MLDSA_SIG_HEX_LENGTH
PUBKEY_HEX = "c" * _MLDSA_PK_HEX_LENGTH
OTHER_PUBKEY_HEX = "d" * _MLDSA_PK_HEX_LENGTH
KEY_REF = "mldsa:key:connectivity-ad"
PEER_ID = "peer-a"
KEY_ID = "key-a"
CURRENT_EPOCH = 10


def _endpoint(host: str = "node.example.com", port: int = 443) -> TransportEndpoint:
    return TransportEndpoint.from_mapping({"host": host, "port": port, "scheme": "https"})


def _endpoint_dict(host: str, port: int = 443) -> dict[str, object]:
    return {"host": host, "port": port, "scheme": "https"}


def _ad_dict(
    *,
    agent_id: str = AGENT_ID,
    host: str = "node.example.com",
    mode: str = "direct_public",
    timestamp: int = CURRENT_EPOCH,
    ttl: int = 4,
    signature: str = SIG_HEX,
    candidate_list: list[dict[str, object]] | None = None,
    relay_endpoint: dict[str, object] | None = None,
    relay_slot_ref: str | None = None,
) -> dict[str, object]:
    return {
        "body": {
            "agent_id": agent_id,
            "candidate_list": [] if candidate_list is None else candidate_list,
            "connectivity_mode": mode,
            "content_availability_count": 1,
            "installed_slices_digest": DIGEST,
            "peer_timestamp_epoch": timestamp,
            "probe_receipt_ref": PROBE_REF,
            "protocol_version": "ilc-d2d-gossip.v1",
            "relay_endpoint": relay_endpoint,
            "relay_slot_ref": relay_slot_ref,
            "schema_version": ca.CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION,
            "transport_endpoint": _endpoint(host).to_dict(),
            "ttl_epochs": ttl,
        },
        "key_binding_ref": KEY_REF,
        "ml_dsa_signature": signature,
        "schema_version": ca.CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION,
    }


def _ad(**kwargs: object) -> ConnectivityAdvertisement:
    return ConnectivityAdvertisement.from_dict(_ad_dict(**kwargs))


def _tombstone_dict(
    *,
    agent_id: str = AGENT_ID,
    revocation_epoch: int = CURRENT_EPOCH,
    signature: str = SIG_HEX,
) -> dict[str, object]:
    return {
        "body": {
            "agent_id": agent_id,
            "revocation_epoch": revocation_epoch,
            "revoke": True,
        },
        "key_binding_ref": KEY_REF,
        "ml_dsa_signature": signature,
        "schema_version": ca.CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION,
    }


def _tombstone(**kwargs: object) -> ConnectivityAdvertisementTombstone:
    return ConnectivityAdvertisementTombstone.from_dict(_tombstone_dict(**kwargs))


def _verify(message: bytes, signature_hex: str, pubkey_hex: str) -> bool:
    return bool(message) and signature_hex == SIG_HEX and pubkey_hex == PUBKEY_HEX


def _validator(*, current_epoch: int = CURRENT_EPOCH) -> ConnectivityAdvertisementValidator:
    return ConnectivityAdvertisementValidator(
        ml_dsa_verify_fn=_verify,
        pubkey_hex=PUBKEY_HEX,
        current_epoch=current_epoch,
    )


def _verified_ad(**kwargs: object) -> VerifiedConnectivityAdvertisement:
    return _validator(current_epoch=int(kwargs.get("current_epoch", CURRENT_EPOCH))).validate(
        _ad_dict(**{k: v for k, v in kwargs.items() if k != "current_epoch"})
    )


def _verified_tombstone(**kwargs: object) -> VerifiedConnectivityAdvertisementTombstone:
    return _validator(
        current_epoch=int(kwargs.get("current_epoch", CURRENT_EPOCH))
    ).validate_tombstone(
        _tombstone_dict(**{k: v for k, v in kwargs.items() if k != "current_epoch"})
    )


def _registry(*, actors: list[str] | None = None) -> GossipPeerRegistry:
    return GossipPeerRegistry(
        [
            {
                "authorized_actor_ids": [AGENT_ID] if actors is None else actors,
                "endpoint": "https://peer-a.example.org",
                "key_id": KEY_ID,
                "mldsa_pubkey_hex": PUBKEY_HEX,
                "peer_id": PEER_ID,
                "valid_from_epoch": 0,
                "valid_until_epoch": None,
            }
        ]
    )


def _headers(gossip_type: str) -> dict[str, str]:
    return gossip_transport.build_gossip_headers(
        gossip_type=gossip_type,
        channel="cid:feedfeedfeedfeed",
        epoch=CURRENT_EPOCH,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature=SIG_HEX,
        sender_peer_id=PEER_ID,
        key_id=KEY_ID,
        content_type="application/json",
    )


def _runtime(registry: GossipPeerRegistry) -> http_runtime.HttpGossipTransportRuntime:
    return http_runtime.HttpGossipTransportRuntime(
        http_runtime.TransportRuntimeConfig(
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


def test_guard_is_cleared_and_manifest_reports_public_gossip_enabled() -> None:
    assert CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED is False
    manifest = connectivity_advertisement_sidecar_manifest()
    assert manifest["connectivity_advertisement_activated"] is True
    assert manifest["public_gossip_propagation_enabled"] is True
    assert manifest["public_serving_enabled"] is False


def test_pre_flip_add_path_still_fails_closed_under_guard_patch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registry_module, "CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED", True)
    registry = GossipPeerRegistry([])

    with pytest.raises(RuntimeError, match="connectivity_advertisement_not_activated"):
        registry.add_connectivity_advertisement(_verified_ad(), current_epoch=CURRENT_EPOCH)


def test_pre_flip_get_path_returns_empty_under_guard_patch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registry_module, "CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED", True)
    registry = GossipPeerRegistry([])
    registry._connectivity_ad_table[AGENT_ID] = _ad()

    assert registry.get_connectivity_advertisements(current_epoch=CURRENT_EPOCH) == []


def test_post_flip_add_path_accepts_verified_advertisement() -> None:
    registry = GossipPeerRegistry([])

    assert registry.add_connectivity_advertisement(
        _verified_ad(),
        current_epoch=CURRENT_EPOCH,
    ) is True
    assert registry.get_connectivity_advertisements(current_epoch=CURRENT_EPOCH)[0].agent_id == AGENT_ID


def test_valid_advertisement_signature_is_accepted() -> None:
    verified = _validator().validate(_ad_dict())

    assert verified.advertisement.agent_id == AGENT_ID


def test_corrupted_advertisement_signature_is_rejected() -> None:
    with pytest.raises(ConnectivityAdvertisementValidationError, match="signature_invalid"):
        _validator().validate(_ad_dict(signature=BAD_SIG_HEX))


def test_wrong_advertisement_pubkey_is_rejected() -> None:
    validator = ConnectivityAdvertisementValidator(
        ml_dsa_verify_fn=_verify,
        pubkey_hex=OTHER_PUBKEY_HEX,
        current_epoch=CURRENT_EPOCH,
    )

    with pytest.raises(ConnectivityAdvertisementValidationError, match="signature_invalid"):
        validator.validate(_ad_dict())


def test_ttl_zero_is_invalid_not_revocation() -> None:
    with pytest.raises(ConnectivityAdvertisementValidationError, match="ttl_epochs_invalid"):
        _ad(ttl=0)


def test_missing_required_advertisement_field_is_rejected() -> None:
    payload = _ad_dict()
    del payload["body"]["installed_slices_digest"]  # type: ignore[index]

    with pytest.raises(ConnectivityAdvertisementValidationError, match="body_missing_fields"):
        ConnectivityAdvertisement.from_dict(payload)


def test_relay_mode_requires_relay_endpoint() -> None:
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="relay_mode_requires_relay_endpoint",
    ):
        _ad(mode="relay_reachable")


def test_local_only_mode_is_not_advertisable() -> None:
    with pytest.raises(ConnectivityAdvertisementValidationError, match="mode_not_advertisable"):
        _ad(mode="local_only")


def test_direct_public_mode_forbids_relay_endpoint() -> None:
    with pytest.raises(
        ConnectivityAdvertisementValidationError,
        match="non_relay_mode_relay_endpoint_forbidden",
    ):
        _ad(relay_endpoint=_endpoint("relay.example.com", 51151).to_dict())


@pytest.mark.parametrize(
    ("field", "host"),
    (
        ("transport_endpoint", "10.0.0.1"),
        ("transport_endpoint", "127.0.0.1"),
        ("relay_endpoint", "10.0.0.2"),
        ("candidate_list", "10.0.0.3"),
        ("transport_endpoint", "169.254.1.1"),
    ),
)
def test_private_address_literals_rejected_in_all_endpoint_fields(field: str, host: str) -> None:
    payload = _ad_dict()
    if field == "transport_endpoint":
        payload["body"]["transport_endpoint"] = _endpoint_dict(host)  # type: ignore[index]
    elif field == "relay_endpoint":
        payload["body"]["connectivity_mode"] = "relay_reachable"  # type: ignore[index]
        payload["body"]["relay_endpoint"] = _endpoint_dict(host, 51151)  # type: ignore[index]
    else:
        payload["body"]["candidate_list"] = [_endpoint_dict(host)]  # type: ignore[index]

    expected = "relay_endpoint_invalid" if field == "relay_endpoint" else "private_endpoint_forbidden"
    with pytest.raises(ValueError, match=expected):
        ConnectivityAdvertisement.from_dict(payload)


def test_registry_at_nmax_rejects_new_agent() -> None:
    registry = GossipPeerRegistry([])
    for index in range(N_MAX):
        agent_id = f"{index:096x}"
        registry._connectivity_ad_table[agent_id] = _ad(
            agent_id=agent_id,
            host=f"node-{index}.example.com",
        )

    assert registry.add_connectivity_advertisement(
        _verified_ad(agent_id=f"{N_MAX + 1:096x}", host="new.example.com"),
        current_epoch=CURRENT_EPOCH,
    ) is False


def test_registry_at_nmax_accepts_existing_agent_supersession() -> None:
    registry = GossipPeerRegistry([])
    for index in range(N_MAX):
        agent_id = f"{index:096x}"
        registry._connectivity_ad_table[agent_id] = _ad(
            agent_id=agent_id,
            host=f"node-{index}.example.com",
        )
    agent_id = f"{7:096x}"

    assert registry.add_connectivity_advertisement(
        _verified_ad(agent_id=agent_id, host="replacement.example.com", timestamp=CURRENT_EPOCH),
        current_epoch=CURRENT_EPOCH,
    ) is True
    assert registry._connectivity_ad_table[agent_id].endpoint_url == "https://replacement.example.com:443"


def test_newer_epoch_supersedes_older_advertisement() -> None:
    registry = GossipPeerRegistry([])
    registry.add_connectivity_advertisement(
        _verified_ad(timestamp=CURRENT_EPOCH),
        current_epoch=CURRENT_EPOCH,
    )

    assert registry.add_connectivity_advertisement(
        _verified_ad(host="newer.example.com", timestamp=CURRENT_EPOCH + 1),
        current_epoch=CURRENT_EPOCH,
    ) is True
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH)[0].endpoint_url == "https://newer.example.com:443"


def test_older_epoch_does_not_replace_newer_advertisement() -> None:
    registry = GossipPeerRegistry([])
    registry.add_connectivity_advertisement(
        _verified_ad(timestamp=CURRENT_EPOCH + 1),
        current_epoch=CURRENT_EPOCH,
    )

    assert registry.add_connectivity_advertisement(
        _verified_ad(host="older.example.com", timestamp=CURRENT_EPOCH),
        current_epoch=CURRENT_EPOCH,
    ) is False
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH)[0].endpoint_url == "https://node.example.com:443"


def test_http_gossip_wiring_accepts_signed_connectivity_advertisement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    runtime = _runtime(registry)
    message = build_connectivity_advertisement_gossip_message(_ad())
    payload = encode_connectivity_advertisement_gossip_payload(message)
    headers = _headers(CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE)
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", _verify)

    status = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_BUFFERED
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH)[0].agent_id == AGENT_ID
    assert any(
        event.get("event") == "incoming_connectivity_advertisement_applied"
        for event in runtime.state["event_log"]
    )


def test_http_gossip_wiring_rejects_json_actor_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry(actors=[OTHER_AGENT_ID])
    runtime = _runtime(registry)
    message = build_connectivity_advertisement_gossip_message(_ad())
    message["claimed_actor"] = OTHER_AGENT_ID
    payload = encode_connectivity_advertisement_gossip_payload(message)
    headers = _headers(CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE)
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", _verify)

    status = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert runtime.state["event_log"][-1]["token"] == "connectivity_advertisement_actor_mismatch"
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH) == []


def test_expire_connectivity_ads_removes_only_expired_entries() -> None:
    registry = GossipPeerRegistry([])
    registry.add_connectivity_advertisement(
        _verified_ad(agent_id=AGENT_ID, host="a.example.com", timestamp=8, ttl=4),
        current_epoch=CURRENT_EPOCH,
    )
    registry.add_connectivity_advertisement(
        _verified_ad(agent_id=OTHER_AGENT_ID, host="b.example.com", timestamp=10, ttl=4),
        current_epoch=CURRENT_EPOCH,
    )

    assert registry.expire_connectivity_ads(current_epoch=12) == 1
    assert [ad.agent_id for ad in registry.get_connectivity_advertisements(12)] == [OTHER_AGENT_ID]


def test_per_agent_rate_limit_rejects_fourth_same_epoch_update() -> None:
    registry = GossipPeerRegistry([])
    for index in range(MAX_CONNECTIVITY_AD_UPDATES_PER_EPOCH):
        assert registry.add_connectivity_advertisement(
            _verified_ad(host=f"update-{index}.example.com"),
            current_epoch=CURRENT_EPOCH,
        ) is True

    assert registry.add_connectivity_advertisement(
        _verified_ad(host="update-4.example.com"),
        current_epoch=CURRENT_EPOCH,
    ) is False


def test_rate_limit_does_not_block_valid_tombstone_revocation() -> None:
    registry = GossipPeerRegistry([])
    for index in range(MAX_CONNECTIVITY_AD_UPDATES_PER_EPOCH):
        registry.add_connectivity_advertisement(
            _verified_ad(host=f"update-{index}.example.com"),
            current_epoch=CURRENT_EPOCH,
        )

    assert registry.revoke_connectivity_advertisement(
        _verified_tombstone(),
        authenticated_agent_id=AGENT_ID,
        current_epoch=CURRENT_EPOCH,
    ) is True
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH) == []


def test_tombstone_authenticated_actor_must_be_canonical_agent_id() -> None:
    registry = GossipPeerRegistry([])

    with pytest.raises(
        ValueError,
        match="connectivity_advertisement_authenticated_agent_id_invalid",
    ):
        registry.revoke_connectivity_advertisement(
            _verified_tombstone(),
            authenticated_agent_id="not-a-96-hex-agent-id",
            current_epoch=CURRENT_EPOCH,
        )


def test_connectivity_rate_limit_state_is_fifo_bounded() -> None:
    registry = GossipPeerRegistry([])
    for index in range(MAX_CONNECTIVITY_RATE_LIMIT_ENTRIES + 5):
        agent_id = f"{index:096x}"
        assert registry._consume_connectivity_ad_update(agent_id, index) is True

    assert len(registry._connectivity_ad_update_counts) == MAX_CONNECTIVITY_RATE_LIMIT_ENTRIES
    assert (f"{0:096x}", 0) not in registry._connectivity_ad_update_counts
    assert (f"{4:096x}", 4) not in registry._connectivity_ad_update_counts
    assert (f"{5:096x}", 5) in registry._connectivity_ad_update_counts


def test_connectivity_rate_limit_agent_key_must_be_canonical_agent_id() -> None:
    registry = GossipPeerRegistry([])

    with pytest.raises(ValueError, match="connectivity_advertisement_rate_limit_agent_id_invalid"):
        registry._consume_connectivity_ad_update("not-a-96-hex-agent-id", CURRENT_EPOCH)


def test_valid_signed_tombstone_removes_present_advertisement() -> None:
    registry = GossipPeerRegistry([])
    registry.add_connectivity_advertisement(_verified_ad(), current_epoch=CURRENT_EPOCH)

    assert registry.revoke_connectivity_advertisement(
        _verified_tombstone(),
        authenticated_agent_id=AGENT_ID,
        current_epoch=CURRENT_EPOCH,
    ) is True


def test_valid_signed_tombstone_for_absent_agent_returns_false() -> None:
    registry = GossipPeerRegistry([])

    assert registry.revoke_connectivity_advertisement(
        _verified_tombstone(),
        authenticated_agent_id=AGENT_ID,
        current_epoch=CURRENT_EPOCH,
    ) is False


def test_tombstone_with_invalid_signature_is_rejected_and_entry_remains() -> None:
    registry = GossipPeerRegistry([])
    registry.add_connectivity_advertisement(_verified_ad(), current_epoch=CURRENT_EPOCH)

    with pytest.raises(ConnectivityAdvertisementValidationError, match="signature_invalid"):
        _validator().validate_tombstone(_tombstone_dict(signature=BAD_SIG_HEX))
    assert len(registry.get_connectivity_advertisements(CURRENT_EPOCH)) == 1


def test_tombstone_actor_mismatch_rejected_and_entry_remains() -> None:
    registry = GossipPeerRegistry([])
    registry.add_connectivity_advertisement(_verified_ad(), current_epoch=CURRENT_EPOCH)

    with pytest.raises(ValueError, match="tombstone_actor_mismatch"):
        registry.revoke_connectivity_advertisement(
            _verified_tombstone(),
            authenticated_agent_id=OTHER_AGENT_ID,
            current_epoch=CURRENT_EPOCH,
        )
    assert len(registry.get_connectivity_advertisements(CURRENT_EPOCH)) == 1


def test_tombstone_future_epoch_is_rejected() -> None:
    with pytest.raises(ConnectivityAdvertisementValidationError, match="future_epoch"):
        _validator().validate_tombstone(_tombstone_dict(revocation_epoch=CURRENT_EPOCH + 1))


def test_http_gossip_wiring_accepts_signed_tombstone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    registry.add_connectivity_advertisement(_verified_ad(), current_epoch=CURRENT_EPOCH)
    runtime = _runtime(registry)
    message = build_connectivity_advertisement_tombstone_gossip_message(_tombstone())
    payload = encode_connectivity_advertisement_tombstone_gossip_payload(message)
    headers = _headers(CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE)
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", _verify)

    status = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_BUFFERED
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH) == []
    assert any(
        event.get("event") == "incoming_connectivity_advertisement_tombstone_applied"
        for event in runtime.state["event_log"]
    )


def test_http_tombstone_actor_mismatch_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry(actors=[OTHER_AGENT_ID])
    registry.add_connectivity_advertisement(_verified_ad(), current_epoch=CURRENT_EPOCH)
    runtime = _runtime(registry)
    message = build_connectivity_advertisement_tombstone_gossip_message(_tombstone())
    message["claimed_actor"] = OTHER_AGENT_ID
    payload = encode_connectivity_advertisement_tombstone_gossip_payload(message)
    headers = _headers(CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE)
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", _verify)

    status = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert registry.get_connectivity_advertisements(CURRENT_EPOCH)[0].agent_id == AGENT_ID


def test_connectivity_gossip_payload_rejects_unknown_fields() -> None:
    message = build_connectivity_advertisement_gossip_message(_ad())
    message["requester_id"] = "forbidden"

    with pytest.raises(ConnectivityAdvertisementValidationError, match="unknown_fields"):
        encode_connectivity_advertisement_gossip_payload(message)


def test_connectivity_gossip_payload_round_trip_is_canonical() -> None:
    message = build_connectivity_advertisement_gossip_message(_ad())
    payload = encode_connectivity_advertisement_gossip_payload(message)

    assert payload == json.dumps(
        message,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    assert decode_connectivity_advertisement_gossip_payload(payload) == message


def test_connectivity_advertisement_is_authority_bearing_gossip_type() -> None:
    assert CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE in http_runtime.AUTHORITY_BEARING_GOSSIP_TYPES
    assert (
        CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE
        in http_runtime.AUTHORITY_BEARING_GOSSIP_TYPES
    )


def test_unverifiable_connectivity_gossip_is_rejected() -> None:
    registry = GossipPeerRegistry(["https://fallback.example.org"])
    runtime = _runtime(registry)
    message = build_connectivity_advertisement_gossip_message(_ad())
    payload = encode_connectivity_advertisement_gossip_payload(message)
    headers = gossip_transport.build_gossip_headers(
        gossip_type=CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE,
        channel="cid:feedfeedfeedfeed",
        epoch=CURRENT_EPOCH,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature=SIG_HEX,
        sender_peer_id="missing-peer",
        key_id="missing-key",
        content_type="application/json",
    )

    status = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(payload),
        payload=payload,
    )

    assert status == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert runtime.state["event_log"][-1]["token"] == "gossip_signature_unverifiable_authority_rejected"


def test_connectivity_handler_failure_does_not_poison_replay_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    runtime = _runtime(registry)
    message = build_connectivity_advertisement_gossip_message(_ad())
    bad_message = copy.deepcopy(message)
    bad_message["advertisement"]["body"]["agent_id"] = THIRD_AGENT_ID  # type: ignore[index]
    bad_payload = encode_connectivity_advertisement_gossip_payload(bad_message)
    good_payload = encode_connectivity_advertisement_gossip_payload(message)
    headers = _headers(CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE)
    monkeypatch.setattr(http_runtime, "verify_mldsa65_signature", _verify)

    first = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(bad_payload),
        payload=bad_payload,
    )
    second = runtime.handle_gossip_request(
        _path(headers),
        headers,
        content_length=len(good_payload),
        payload=good_payload,
    )

    assert first == gossip_transport.HTTP_STATUS_ENVELOPE_ERROR
    assert second == gossip_transport.HTTP_STATUS_BUFFERED
