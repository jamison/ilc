from __future__ import annotations

import json

import pytest

import ilc_core.network.d2d.gossip_peer_registry as registry_module
import ilc_core.network.d2d.peer_discovery_manager as manager_module
from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.gossip_peer_registry import VerifiedPeerAdvertisement
from ilc_core.network.d2d.peer_advertisement import (
    PEER_ADVERTISEMENT_SCHEMA_VERSION,
    PeerAdvertisement,
    PeerAdvertisementValidationError,
)
from ilc_core.network.d2d.peer_discovery_manager import PeerDiscoveryManager


PUBKEY_HEX = "a" * _MLDSA_PK_HEX_LENGTH
SIG_HEX = "b" * 6618
AGENT_A = "1" * 96
AGENT_B = "2" * 96
DIGEST_A = "3" * 96
DIGEST_B = "4" * 96


def _ad_dict(
    *,
    agent_id: str = AGENT_A,
    host: str = "peer-a.example.com",
    port: int = 443,
    timestamp: int = 10,
    ttl: int = 4,
    signature: str = SIG_HEX,
    digest: str = DIGEST_A,
    key_binding_ref: str = "key-binding-a",
) -> dict[str, object]:
    return {
        "body": {
            "agent_id": agent_id,
            "content_availability_count": 7,
            "installed_slices_digest": digest,
            "peer_timestamp_epoch": timestamp,
            "protocol_version": "ilc-d2d-gossip.v1",
            "transport_endpoint": {
                "host": host,
                "port": port,
                "scheme": "https",
            },
            "ttl_epochs": ttl,
        },
        "key_binding_ref": key_binding_ref,
        "ml_dsa_signature": signature,
        "schema_version": PEER_ADVERTISEMENT_SCHEMA_VERSION,
    }


def _ad(**kwargs: object) -> PeerAdvertisement:
    return PeerAdvertisement.from_dict(_ad_dict(**kwargs))


def _verified(ad: PeerAdvertisement) -> VerifiedPeerAdvertisement:
    return VerifiedPeerAdvertisement(ad)


def _clear_dynamic_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry_module, "DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED", False)
    monkeypatch.setattr(manager_module, "DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED", False)


def test_peer_advertisement_from_dict_validates_canonical_schema() -> None:
    ad = _ad()

    assert ad.agent_id == AGENT_A
    assert ad.endpoint_url == "https://peer-a.example.com:443"
    assert ad.schema_version == PEER_ADVERTISEMENT_SCHEMA_VERSION


def test_peer_advertisement_from_dict_missing_field() -> None:
    payload = _ad_dict()
    del payload["body"]  # type: ignore[index]

    with pytest.raises(PeerAdvertisementValidationError, match="peer_advertisement_missing_fields"):
        PeerAdvertisement.from_dict(payload)


def test_peer_advertisement_rejects_float_body_value() -> None:
    payload = _ad_dict()
    body = dict(payload["body"])  # type: ignore[arg-type]
    body["content_availability_count"] = 1.5
    payload["body"] = body

    with pytest.raises(
        PeerAdvertisementValidationError,
        match="peer_advertisement_content_availability_count_invalid",
    ):
        PeerAdvertisement.from_dict(payload)


def test_peer_advertisement_rejects_uppercase_signature() -> None:
    with pytest.raises(PeerAdvertisementValidationError, match="peer_advertisement_signature_invalid"):
        _ad(signature="B" * 6618)


def test_peer_advertisement_canonical_json_is_body_only_sorted_compact_json() -> None:
    ad = _ad()

    canonical = ad.to_canonical_json()
    decoded = json.loads(canonical.decode("utf-8"))

    assert "ml_dsa_signature" not in decoded
    assert "key_binding_ref" not in decoded
    assert list(decoded) == sorted(decoded)
    assert b" " not in canonical


def test_peer_advertisement_verify_valid_signature_true() -> None:
    ad = _ad()

    def verifier(message: bytes, signature: str, pubkey: str) -> bool:
        return message == ad.to_canonical_json() and signature == SIG_HEX and pubkey == PUBKEY_HEX

    assert ad.verify(verifier, pubkey_hex=PUBKEY_HEX) is True


def test_invalid_sig_rejected() -> None:
    ad = _ad(signature="c" * 6618)

    def verifier(_message: bytes, signature: str, _pubkey: str) -> bool:
        return signature == SIG_HEX

    assert ad.verify(verifier, pubkey_hex=PUBKEY_HEX) is False


def test_expired_ad_rejected() -> None:
    assert _ad(timestamp=10, ttl=4).is_expired(14) is True
    assert _ad(timestamp=10, ttl=4).is_expired(13) is False


def test_ttl_expiry_removes_ad(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry(["https://static.example.com"])
    assert registry.add_peer_advertisement(_verified(_ad(timestamp=1, ttl=2)), 1) is True

    assert registry.expire_ads(3) == 1
    assert registry.get_dynamic_peers(3) == []


def test_n_max_cap_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    monkeypatch.setattr(registry_module, "N_MAX", 1)
    registry = GossipPeerRegistry([])

    assert registry.add_peer_advertisement(_verified(_ad(agent_id=AGENT_A)), 10) is True
    assert registry.add_peer_advertisement(_verified(_ad(agent_id=AGENT_B, host="peer-b.example.com")), 10) is False


def test_n_max_cap_replacement_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    monkeypatch.setattr(registry_module, "N_MAX", 1)
    registry = GossipPeerRegistry([])

    assert registry.add_peer_advertisement(_verified(_ad(timestamp=10)), 10) is True
    assert registry.add_peer_advertisement(_verified(_ad(host="peer-a-new.example.com", timestamp=11)), 11) is True
    assert registry.get_dynamic_peers()[0].endpoint_url == "https://peer-a-new.example.com:443"


def test_deduplication_second_ad_replaces_first(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry([])

    registry.add_peer_advertisement(_verified(_ad(host="peer-a.example.com", timestamp=10)), 10)
    registry.add_peer_advertisement(_verified(_ad(host="peer-a-new.example.com", timestamp=12)), 12)

    assert len(registry.get_dynamic_peers()) == 1
    assert registry.get_dynamic_peers()[0].endpoint_url == "https://peer-a-new.example.com:443"


def test_older_duplicate_ad_does_not_replace_newer(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry([])

    registry.add_peer_advertisement(_verified(_ad(host="new.example.com", timestamp=12)), 12)
    assert registry.add_peer_advertisement(_verified(_ad(host="old.example.com", timestamp=10)), 12) is False
    assert registry.get_dynamic_peers()[0].endpoint_url == "https://new.example.com:443"


def test_static_fallback_when_dynamic_empty() -> None:
    registry = GossipPeerRegistry(["https://static.example.com"])

    assert registry.get_peers() == ["https://static.example.com"]


def test_static_fallback_when_guard_active(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry(["https://static.example.com"])
    registry.add_peer_advertisement(_verified(_ad()), 10)
    monkeypatch.setattr(registry_module, "DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED", True)

    assert registry.get_peers() == ["https://static.example.com"]
    with pytest.raises(RuntimeError, match="dynamic_peer_discovery_not_activated"):
        registry.add_peer_advertisement(_verified(_ad(host="peer-new.example.com")), 10)


def test_valid_ad_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry([])
    ad = _ad()

    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: True)
    manager = PeerDiscoveryManager(
        registry,
        AGENT_B,
        b"vrf-key",
        lambda _payload: SIG_HEX,
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )

    assert manager.handle_incoming_advertisement(ad, 10) is True
    assert registry.get_dynamic_peers() == [ad]


def test_manager_invalid_sig_not_added(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry([])
    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: False)
    manager = PeerDiscoveryManager(
        registry,
        AGENT_B,
        b"vrf-key",
        lambda _payload: SIG_HEX,
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )

    assert manager.handle_incoming_advertisement(_ad(), 10) is False
    assert registry.get_dynamic_peers() == []


def test_broadcast_produces_signed_ad(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    manager = PeerDiscoveryManager(
        GossipPeerRegistry([]),
        AGENT_A,
        b"vrf-key",
        lambda payload: SIG_HEX if payload else "0",
        transport_endpoint={"scheme": "https", "host": "local-peer.example.com", "port": 8443},
        installed_slices_digest=DIGEST_A,
        key_binding_ref="key-binding-a",
    )

    ad = manager.broadcast_advertisement(21)

    assert ad.ml_dsa_signature == SIG_HEX
    assert ad.peer_timestamp_epoch == 21
    assert ad.endpoint_url == "https://local-peer.example.com:8443"


def test_vrf_introduction_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    manager = PeerDiscoveryManager(GossipPeerRegistry([]), AGENT_A, b"vrf-key", lambda _payload: SIG_HEX)
    candidates = [
        _ad(agent_id=f"{index:096x}", host=f"peer-{index}.example.com")
        for index in range(12)
    ]

    first = manager.sample_introduction_set(candidates, b"same-key", k=8)
    second = manager.sample_introduction_set(list(reversed(candidates)), b"same-key", k=8)

    assert [ad.agent_id for ad in first] == [ad.agent_id for ad in second]
    assert len(first) == 8


def test_vrf_introduction_different_key_different_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    manager = PeerDiscoveryManager(GossipPeerRegistry([]), AGENT_A, b"vrf-key", lambda _payload: SIG_HEX)
    candidates = [
        _ad(agent_id=f"{index:096x}", host=f"peer-{index}.example.com")
        for index in range(12)
    ]

    first = manager.sample_introduction_set(candidates, b"key-one", k=4)
    second = manager.sample_introduction_set(candidates, b"key-two", k=4)

    assert [ad.agent_id for ad in first] != [ad.agent_id for ad in second]


def test_introduction_k_capped_at_candidate_count(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    manager = PeerDiscoveryManager(GossipPeerRegistry([]), AGENT_A, b"vrf-key", lambda _payload: SIG_HEX)
    candidates = [_ad(agent_id=AGENT_A), _ad(agent_id=AGENT_B, host="peer-b.example.com")]

    assert len(manager.sample_introduction_set(candidates, b"key", k=8)) == 2


def test_request_introduction_stores_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry([])
    manager = PeerDiscoveryManager(registry, AGENT_A, b"vrf-key", lambda _payload: SIG_HEX)
    candidates = [
        _ad(agent_id=f"{index:096x}", host=f"peer-{index}.example.com")
        for index in range(3)
    ]

    sample = manager.request_introduction(candidates, 10)

    assert len(sample) == 3
    assert registry.get_introduction_entries() == sample


def test_static_seed_endpoint_conflict_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_dynamic_guard(monkeypatch)
    registry = GossipPeerRegistry(["https://peer-a.example.com:443"])

    assert registry.add_peer_advertisement(_verified(_ad()), 10) is False
