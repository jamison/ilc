from __future__ import annotations

from ilc_core.network.d2d import gossip_peer_registry


def test_registry_deduplicates_identical_and_case_normalized_endpoints() -> None:
    registry = gossip_peer_registry.GossipPeerRegistry([
        'https://a.example.com',
        'https://A.EXAMPLE.COM',
        'https://b.example.com',
        'https://a.example.com',
    ])
    assert registry.peer_count() == 2
    assert registry.get_peers() == ['https://a.example.com', 'https://b.example.com']


def test_select_fanout_peers_never_returns_duplicate_endpoints_after_dedup() -> None:
    registry = gossip_peer_registry.GossipPeerRegistry([
        'https://a.example.com',
        'https://a.example.com',  # intentional duplicate: tests dedup behavior
        'https://b.example.com',
        'https://c.example.com',
    ])
    assert registry.select_fanout_peers(3) == [
        'https://a.example.com',
        'https://b.example.com',
        'https://c.example.com',
    ]
