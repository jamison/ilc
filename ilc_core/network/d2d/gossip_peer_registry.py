"""Phase 562 static gossip peer registry.

This module provides local static peer configuration only. Dynamic discovery is
intentionally deferred because CDL-039 topology privacy requires explicit
constitutional authorization for any discovery mechanism beyond static v1.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from ilc_core.network.d2d.gossip_transport import (
    GOSSIP_TRANSPORT_RUNTIME_VERSION as _GOSSIP_TRANSPORT_CHECK,
)


GOSSIP_PEER_REGISTRY_VERSION = "gossip_peer_registry_562.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"
GOSSIP_TRANSPORT_DEPENDENCY = "gossip_transport_runtime_558.v0.1"
PEER_DISCOVERY_MODE = "static_v1"
MAX_PEERS = 16

assert _GOSSIP_TRANSPORT_CHECK == GOSSIP_TRANSPORT_DEPENDENCY, (
    f"dep chain mismatch: {_GOSSIP_TRANSPORT_CHECK}"
)
assert PEER_DISCOVERY_MODE == "static_v1", (
    "cdl_039_topology_privacy: dynamic peer discovery requires explicit CDL authorization"
)


def validate_peer_endpoint(endpoint: str) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError('peer_endpoint_invalid_format')
    normalized = endpoint.strip()
    if normalized.startswith('http://'):
        raise ValueError('peer_endpoint_must_use_https')

    parts = urlsplit(normalized)
    if parts.scheme != 'https':
        raise ValueError('peer_endpoint_invalid_format')
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError('peer_endpoint_invalid_format')
    if parts.path not in ('', '/'):
        raise ValueError('peer_endpoint_invalid_format')
    if not parts.hostname:
        raise ValueError('peer_endpoint_invalid_format')
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError('peer_endpoint_invalid_format') from exc

    normalized_endpoint = f'https://{parts.hostname.lower()}'
    if port is not None:
        normalized_endpoint += f':{port}'
    return normalized_endpoint


class GossipPeerRegistry:
    """Static v1 peer registry — no dynamic discovery."""

    def __init__(self, peers: list[str]) -> None:
        normalized_peers = list(dict.fromkeys(validate_peer_endpoint(peer) for peer in peers))
        if len(normalized_peers) > MAX_PEERS:
            raise ValueError('peer_registry_exceeds_max_peers')
        self._peers = normalized_peers

    def peer_count(self) -> int:
        return len(self._peers)

    def get_peers(self) -> list[str]:
        return list(self._peers)

    def select_fanout_peers(self, fanout: int, exclude: list[str] | None = None) -> list[str]:
        if isinstance(fanout, bool) or not isinstance(fanout, int) or fanout < 1:
            raise ValueError('fanout_must_be_positive')
        excluded = set()
        if exclude is not None:
            excluded = {validate_peer_endpoint(peer) for peer in exclude}
        available = sorted(peer for peer in self._peers if peer not in excluded)
        return available[:fanout]
