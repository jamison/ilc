"""Phase 562 static gossip peer registry.

This module provides local static peer configuration only. Dynamic discovery is
intentionally deferred because CDL-039 topology privacy requires explicit
constitutional authorization for any discovery mechanism beyond static v1.
"""

from __future__ import annotations

import ipaddress
import socket
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
PRIVATE_PEER_ENDPOINT_TOKEN = "peer_endpoint_private_address_forbidden_phase_1332_fix4"
_LOCALHOST_NAMES = frozenset({"localhost", "localhost.localdomain"})
_NONSTANDARD_IPV4_LITERAL_CHARS = frozenset("0123456789abcdefABCDEFxX.")

if _GOSSIP_TRANSPORT_CHECK != GOSSIP_TRANSPORT_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "gossip_peer_registry_dep_chain_mismatch",
                "dependency": "gossip_transport_runtime",
                "expected": GOSSIP_TRANSPORT_DEPENDENCY,
                "got": _GOSSIP_TRANSPORT_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("gossip_peer_registry_gossip_transport_dependency_mismatch")

# PEER_DISCOVERY_MODE is a constitutional invariant: CDL-039 prohibits dynamic
# discovery without explicit authorization. Checked at runtime, not as an assert,
# so that python -O does not silently bypass the guard.
if PEER_DISCOVERY_MODE != "static_v1":
    raise RuntimeError(
        f"cdl_039_topology_privacy: dynamic peer discovery requires explicit CDL authorization, "
        f"got: {PEER_DISCOVERY_MODE}"
    )


def reject_private_address_literal(hostname: str) -> None:
    normalized = hostname.strip().lower().rstrip(".")
    if normalized in _LOCALHOST_NAMES or normalized.endswith(".localhost"):
        raise ValueError(PRIVATE_PEER_ENDPOINT_TOKEN)
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        address = _parse_nonstandard_ipv4_literal(normalized)
        if address is None:
            return
    if not address.is_global:
        raise ValueError(PRIVATE_PEER_ENDPOINT_TOKEN)


def _parse_nonstandard_ipv4_literal(hostname: str) -> ipaddress.IPv4Address | None:
    """Catch inet_aton-compatible IPv4 shorthands before outbound clients do."""

    if not hostname or not any(char.isdigit() for char in hostname):
        return None
    if any(char not in _NONSTANDARD_IPV4_LITERAL_CHARS for char in hostname):
        return None
    try:
        return ipaddress.IPv4Address(socket.inet_aton(hostname))
    except OSError:
        return None


def validate_peer_endpoint(
    endpoint: str,
    *,
    allow_private_address_literals: bool = False,
) -> str:
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
    hostname = parts.hostname.lower()
    if not allow_private_address_literals:
        reject_private_address_literal(hostname)
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError('peer_endpoint_invalid_format') from exc

    formatted_host = f"[{hostname}]" if ":" in hostname else hostname
    normalized_endpoint = f'https://{formatted_host}'
    if port is not None:
        normalized_endpoint += f':{port}'
    return normalized_endpoint


class GossipPeerRegistry:
    """Static v1 peer registry — no dynamic discovery."""

    def __init__(
        self,
        peers: list[str],
        *,
        allow_private_address_literals: bool = False,
    ) -> None:
        normalized_peers = list(
            dict.fromkeys(
                validate_peer_endpoint(
                    peer,
                    allow_private_address_literals=allow_private_address_literals,
                )
                for peer in peers
            )
        )
        if len(normalized_peers) > MAX_PEERS:
            raise ValueError('peer_registry_exceeds_max_peers')
        self._peers = normalized_peers
        self._allow_private_address_literals = allow_private_address_literals

    def peer_count(self) -> int:
        return len(self._peers)

    def get_peers(self) -> list[str]:
        return list(self._peers)

    def select_fanout_peers(self, fanout: int, exclude: list[str] | None = None) -> list[str]:
        if isinstance(fanout, bool) or not isinstance(fanout, int) or fanout < 1:
            raise ValueError('fanout_must_be_positive')
        excluded = set()
        if exclude is not None:
            excluded = {
                validate_peer_endpoint(
                    peer,
                    allow_private_address_literals=self._allow_private_address_literals,
                )
                for peer in exclude
            }
        available = sorted(peer for peer in self._peers if peer not in excluded)
        return available[:fanout]
