# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import pytest

import ilc_core.network.d2d.gossip_peer_registry as registry_module
import ilc_core.network.d2d.peer_discovery_manager as manager_module
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
from ilc_core.network.d2d.gossip_peer_registry import VerifiedPeerAdvertisement
from ilc_core.network.d2d.peer_advertisement import (
    MAX_CONTENT_AVAILABILITY_COUNT,
    MAX_PEER_ADVERTISEMENT_EPOCH,
    MAX_TTL_EPOCHS,
    PeerAdvertisement,
)
from ilc_core.network.d2d.peer_discovery_manager import PeerDiscoveryManager


ROOT = Path(__file__).resolve().parents[1]
RATIFICATION_DOC = (
    ROOT / "docs/specs/ilc_cdl_103_dynamic_peer_discovery_ratification_1583_v0.1.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SPEC = ROOT / "docs/specs/ilc_dynamic_peer_discovery_spec_v0.1.md"
PUBLIC_PREFLIGHT = ROOT / "ilc_core/graph/sidecar_public_path_preflight.py"
TRANSPORT_ADMISSION = ROOT / "ilc_core/sidecars/transport_principal_admission.py"
GOSSIP_POLICY = ROOT / "ilc_core/sidecars/confidential_coordination_gossip_policy.py"

PUBKEY_HEX = "a" * 3328
SIG_HEX = "b" * 6618
AGENT_A = "1" * 96
DIGEST_A = "3" * 96
AGENT_B = "2" * 96
DIGEST_B = "4" * 96


def _ad_dict(
    *,
    agent_id: str = AGENT_A,
    content_availability_count: int = 7,
    digest: str = DIGEST_A,
    host: str = "peer-a.example.com",
    key_binding_ref: str = "key-binding-a",
    timestamp: int = 10,
    ttl: int = 4,
) -> dict[str, object]:
    return {
        "body": {
            "agent_id": agent_id,
            "content_availability_count": content_availability_count,
            "installed_slices_digest": digest,
            "peer_timestamp_epoch": timestamp,
            "protocol_version": "ilc-d2d-gossip.v1",
            "transport_endpoint": {
                "host": host,
                "port": 443,
                "scheme": "https",
            },
            "ttl_epochs": ttl,
        },
        "key_binding_ref": key_binding_ref,
        "ml_dsa_signature": SIG_HEX,
        "schema_version": "peer_advertisement_cdl103.v0.1",
    }


def _ad(*, timestamp: int = 10, ttl: int = 4) -> PeerAdvertisement:
    return PeerAdvertisement.from_dict(_ad_dict(timestamp=timestamp, ttl=ttl))


def _ad_for(
    *,
    agent_id: str,
    host: str,
    key_binding_ref: str,
    timestamp: int = 10,
) -> PeerAdvertisement:
    return PeerAdvertisement.from_dict(
        _ad_dict(
            agent_id=agent_id,
            digest=DIGEST_B if agent_id == AGENT_B else DIGEST_A,
            host=host,
            key_binding_ref=key_binding_ref,
            timestamp=timestamp,
        )
    )


def _ad_b(*, timestamp: int = 10, ttl: int = 4) -> PeerAdvertisement:
    return PeerAdvertisement.from_dict(
        {
            "body": {
                "agent_id": AGENT_B,
                "content_availability_count": 3,
                "installed_slices_digest": DIGEST_B,
                "peer_timestamp_epoch": timestamp,
                "protocol_version": "ilc-d2d-gossip.v1",
                "transport_endpoint": {
                    "host": "peer-b.example.com",
                    "port": 443,
                    "scheme": "https",
                },
                "ttl_epochs": ttl,
            },
            "key_binding_ref": "key-binding-b",
            "ml_dsa_signature": SIG_HEX,
            "schema_version": "peer_advertisement_cdl103.v0.1",
        }
    )


def _verified(ad: PeerAdvertisement) -> VerifiedPeerAdvertisement:
    return VerifiedPeerAdvertisement(ad)


def test_cdl_103_ratification_doc_exists() -> None:
    text = RATIFICATION_DOC.read_text(encoding="utf-8")
    assert "**Status:** RATIFIED" in text
    assert "GO Phase 1583 GAP-DISCOV-03 CDL-103-RATIFY" in text


def test_peer_discovery_enabled_default_false_in_sidecars() -> None:
    assert "peer_discovery_enabled: bool = False" in PUBLIC_PREFLIGHT.read_text(encoding="utf-8")
    assert "peer_discovery_enabled: bool = False" in TRANSPORT_ADMISSION.read_text(encoding="utf-8")
    assert '"public_peer_discovery_enabled": False' in GOSSIP_POLICY.read_text(encoding="utf-8")


def test_peer_advertisement_runtime_exists_and_testnet_guard_cleared() -> None:
    status = STATUS.read_text(encoding="utf-8")
    doc = RATIFICATION_DOC.read_text(encoding="utf-8")
    assert "peer_advertisement_module_committed_gap_discov_02" in status
    assert "peer_discovery_manager_committed_gap_discov_02" in status
    assert "peer_advertisement_runtime_committed_phase_1579" not in status
    assert "stale input-token spelling" in doc
    assert registry_module.DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED is False
    assert manager_module.DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED is False
    assert registry_module.PEER_DISCOVERY_MODE == "static_plus_dynamic_testnet_v1"


def test_peer_discovery_spec_doc_exists() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert "PeerAdvertisement" in text
    assert "DHT" in text
    assert "not provide a formal eclipse-resistance guarantee" in text


def test_anti_eclipse_documented_not_solved() -> None:
    text = RATIFICATION_DOC.read_text(encoding="utf-8")
    assert "mitigation bounds only, not a solved" in text
    assert "cdl_103_signed_peer_table_roots_deferred_phase_1583" in text
    assert "cdl_103_multi_seed_comparison_deferred_phase_1583" in text


def test_cdl_103_ratified_token_in_status_and_register() -> None:
    status = STATUS.read_text(encoding="utf-8")
    register = REGISTER.read_text(encoding="utf-8")
    assert "cdl_103_ratified_phase_1583" in status
    assert "dynamic_peer_discovery_testnet_activated_phase_1583" in status
    assert "| CDL-103 |" in register
    assert "ratified_phase: GAP-DISCOV-03 / 1583" in register


def test_testnet_dynamic_discovery_accepts_valid_advertisement(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = GossipPeerRegistry([])
    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: True)
    manager = PeerDiscoveryManager(
        registry,
        "2" * 96,
        b"vrf-key",
        lambda payload: SIG_HEX if payload else "0",
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )

    assert manager.handle_incoming_advertisement(_ad(timestamp=10), 10) is True
    assert registry.get_dynamic_peers(10)[0].agent_id == AGENT_A


def test_ratified_ttl_and_future_skew_bounds_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="peer_advertisement_ttl_epochs_invalid"):
        _ad(ttl=MAX_TTL_EPOCHS + 1)

    registry = GossipPeerRegistry([])
    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: True)
    manager = PeerDiscoveryManager(
        registry,
        "2" * 96,
        b"vrf-key",
        lambda payload: SIG_HEX if payload else "0",
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )
    with pytest.raises(ValueError, match="peer_advertisement_timestamp_future_skew"):
        manager.handle_incoming_advertisement(_ad(timestamp=12), 10)


def test_registry_rejects_future_skew_advertisement_directly() -> None:
    """MEDIUM: registry.add_peer_advertisement() must enforce future-skew bound
    independently of the manager path so direct callers cannot inject ads with
    timestamps beyond current_epoch + MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS."""
    registry = GossipPeerRegistry([])
    # timestamp=12, current=10: skew=2 > MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS(1)
    with pytest.raises(ValueError, match="peer_advertisement_timestamp_future_skew"):
        registry.add_peer_advertisement(_verified(_ad(timestamp=12)), 10)
    # timestamp=11, current=10: skew=1 == limit, must be accepted
    ad_at_limit = _ad(timestamp=11, ttl=4)
    result = registry.add_peer_advertisement(_verified(ad_at_limit), 10)
    assert result is True


def test_registry_rejects_raw_unverified_advertisement_directly() -> None:
    registry = GossipPeerRegistry([])

    with pytest.raises(ValueError, match="peer_advertisement_requires_verified_envelope"):
        registry.add_peer_advertisement(_ad(timestamp=10), 10)  # type: ignore[arg-type]


def test_select_fanout_peers_includes_dynamic_peers_after_cdl103_ratification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LOW: After CDL-103 ratification (Phase 1583), select_fanout_peers() must
    include dynamic advertisement endpoints alongside static peers."""
    registry = GossipPeerRegistry([])
    monkeypatch.setattr(manager_module, "verify_mldsa65_signature", lambda *_args: True)
    manager = PeerDiscoveryManager(
        registry,
        "2" * 96,
        b"vrf-key",
        lambda payload: SIG_HEX if payload else "0",
        key_binding_resolver={"key-binding-a": PUBKEY_HEX},
    )
    manager.handle_incoming_advertisement(_ad(timestamp=10), 10)
    fanout = registry.select_fanout_peers(10)
    assert "https://peer-a.example.com:443" in fanout


def test_select_fanout_peers_static_only_when_no_dynamic_ads() -> None:
    """Baseline: when dynamic table is empty, fanout returns static peers only."""
    from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry
    registry = GossipPeerRegistry([])
    # No dynamic ads added — fanout should be empty for empty registry
    assert registry.select_fanout_peers(5) == []


def test_get_peers_deduplicates_dynamic_ad_matching_static_endpoint() -> None:
    """add_peer_advertisement() returns False and static endpoint is not duplicated
    when a dynamic ad's endpoint matches a static peer's endpoint."""
    static_peer = {
        "endpoint": "https://peer-a.example.com:443",
        "peer_id": "a" * 64,
        "mldsa_pubkey_hex": PUBKEY_HEX,
        "key_id": "key-a",
        "valid_from_epoch": 0,
        "authorized_actor_ids": ["actor-a"],
    }
    registry = GossipPeerRegistry([static_peer])
    ad = _ad(timestamp=10)
    result = registry.add_peer_advertisement(_verified(ad), 10)
    assert result is False
    peers = registry.get_peers()
    assert peers.count("https://peer-a.example.com:443") == 1


def test_dynamic_endpoint_duplicate_rejected_across_agent_ids() -> None:
    registry = GossipPeerRegistry([])
    first = _ad_for(
        agent_id=AGENT_A,
        host="same-dynamic.example.com",
        key_binding_ref="key-binding-a",
    )
    second = _ad_for(
        agent_id=AGENT_B,
        host="same-dynamic.example.com",
        key_binding_ref="key-binding-b",
    )

    assert registry.add_peer_advertisement(_verified(first), 10) is True
    assert registry.add_peer_advertisement(_verified(second), 10) is False
    assert registry.get_peers().count("https://same-dynamic.example.com:443") == 1


def test_add_introduction_entries_replaces_previous_table() -> None:
    """add_introduction_entries() replaces the full introduction table atomically;
    entries from a prior call must not persist."""
    registry = GossipPeerRegistry([])
    registry.add_introduction_entries([_ad(timestamp=10)])
    assert len(registry.get_introduction_entries()) == 1
    assert registry.get_introduction_entries()[0].agent_id == AGENT_A

    # Replace with a different ad — Agent A entry must be gone
    registry.add_introduction_entries([_ad_b(timestamp=10)])
    entries = registry.get_introduction_entries()
    assert len(entries) == 1
    assert entries[0].agent_id == AGENT_B


def test_introduction_entries_reject_over_n_max_storage() -> None:
    registry = GossipPeerRegistry([])
    ads = (
        _ad_for(
            agent_id=f"{index:096x}",
            host=f"intro-{index}.example.com",
            key_binding_ref=f"key-{index}",
        )
        for index in range(registry_module.MAX_INTRODUCTION_CANDIDATES + 1)
    )

    with pytest.raises(ValueError, match="peer_introduction_entries_exceed_n_max"):
        registry.add_introduction_entries(ads)


def test_introduction_sampling_rejects_over_n_max_candidates() -> None:
    manager = PeerDiscoveryManager(GossipPeerRegistry([]), AGENT_A, b"vrf-key", lambda _payload: SIG_HEX)
    ads = (
        _ad_for(
            agent_id=f"{index:096x}",
            host=f"candidate-{index}.example.com",
            key_binding_ref=f"key-{index}",
        )
        for index in range(registry_module.MAX_INTRODUCTION_CANDIDATES + 1)
    )

    with pytest.raises(ValueError, match="peer_introduction_candidates_exceed_n_max"):
        manager.sample_introduction_set(ads, b"vrf-key")


def test_peer_advertisement_rejects_unbounded_u64_fields() -> None:
    oversized_count = _ad_dict(content_availability_count=MAX_CONTENT_AVAILABILITY_COUNT + 1)
    with pytest.raises(ValueError, match="peer_advertisement_content_availability_count_invalid"):
        PeerAdvertisement.from_dict(oversized_count)

    oversized_epoch = _ad_dict(timestamp=MAX_PEER_ADVERTISEMENT_EPOCH + 1)
    with pytest.raises(ValueError, match="peer_advertisement_timestamp_epoch_invalid"):
        PeerAdvertisement.from_dict(oversized_epoch)


def test_broadcast_requires_explicit_transport_endpoint() -> None:
    manager = PeerDiscoveryManager(GossipPeerRegistry([]), AGENT_A, b"vrf-key", lambda _payload: SIG_HEX)

    with pytest.raises(ValueError, match="peer_discovery_transport_endpoint_required"):
        manager.broadcast_advertisement(10)
