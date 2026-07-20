# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 562 static gossip peer registry.

This module provides local static peer configuration only. Dynamic discovery is
intentionally deferred because CDL-039 topology privacy requires explicit
constitutional authorization for any discovery mechanism beyond static v1.
"""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from ilc_core.crypto.pq_signature_verify import (
    CDL_101_SIGNED_ENVELOPE_DEPENDENCY,
    _MLDSA_PK_HEX_LENGTH,
)
from ilc_core.network.d2d.gossip_transport import (
    GOSSIP_TRANSPORT_RUNTIME_VERSION as _GOSSIP_TRANSPORT_CHECK,
)


GOSSIP_PEER_REGISTRY_VERSION = "gossip_peer_registry_1571.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"
GOSSIP_TRANSPORT_DEPENDENCY = "gossip_transport_runtime_1572.v0.1"
PEER_DISCOVERY_MODE = "static_v1"
LEXICOGRAPHIC_FANOUT_ROTATION_DEFERRED_TOKEN = (
    "lexicographic_gossip_fanout_rotation_deferred_pending_cdl_103_phase_1575h_fix2"
)
MAX_PEERS = 16
PRIVATE_PEER_ENDPOINT_TOKEN = "peer_endpoint_private_address_forbidden_phase_1332_fix4"
_LOCALHOST_NAMES = frozenset({"localhost", "localhost.localdomain"})
_NONSTANDARD_IPV4_LITERAL_CHARS = frozenset("0123456789abcdefABCDEFxX.")
_HEX_CHARS = frozenset("0123456789abcdefABCDEF")

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


@dataclass(frozen=True)
class _PeerEntry:
    endpoint: str
    peer_id: str | None = None
    mldsa_pubkey_hex: str | None = None
    key_id: str | None = None
    authorized_actor_ids: tuple[str, ...] = ()
    valid_from_epoch: int = 0
    valid_until_epoch: int | None = None


def _require_peer_string(value: Any, token: str, max_chars: int) -> str:
    if not isinstance(value, str):
        raise ValueError(token)
    normalized = value.strip()
    if not normalized or len(normalized) > max_chars or any(char.isspace() for char in normalized):
        raise ValueError(token)
    return normalized


def _require_epoch(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_mldsa_pubkey_hex(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _MLDSA_PK_HEX_LENGTH
        or any(char not in _HEX_CHARS for char in value)
    ):
        raise ValueError("peer_mldsa_pubkey_hex_invalid")
    return value


def _require_authorized_actor_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("peer_authorized_actor_ids_required")
    actors = tuple(
        _require_peer_string(actor, "peer_authorized_actor_id_invalid", 128)
        for actor in value
    )
    if len(set(actors)) != len(actors):
        raise ValueError("peer_authorized_actor_ids_duplicate")
    return actors


def _normalize_peer_entry(
    peer: str | Mapping[str, Any],
    *,
    allow_private_address_literals: bool,
) -> _PeerEntry:
    if isinstance(peer, str):
        return _PeerEntry(
            endpoint=validate_peer_endpoint(
                peer,
                allow_private_address_literals=allow_private_address_literals,
            )
        )
    if not isinstance(peer, Mapping):
        raise ValueError("peer_entry_invalid")

    endpoint = validate_peer_endpoint(
        peer.get("endpoint"),
        allow_private_address_literals=allow_private_address_literals,
    )
    peer_id = _require_peer_string(peer.get("peer_id"), "peer_id_invalid", 128)
    pubkey = _require_mldsa_pubkey_hex(peer.get("mldsa_pubkey_hex"))
    key_id = _require_peer_string(peer.get("key_id"), "peer_key_id_invalid", 64)
    valid_from = _require_epoch(peer.get("valid_from_epoch", 0), "peer_valid_from_epoch_invalid")
    valid_until_raw = peer.get("valid_until_epoch")
    if valid_until_raw is None:
        valid_until = None
    else:
        valid_until = _require_epoch(valid_until_raw, "peer_valid_until_epoch_invalid")
        if valid_until < valid_from:
            raise ValueError("peer_valid_until_before_valid_from")
    if "authorized_actor_ids" not in peer:
        raise ValueError("peer_authorized_actor_ids_required")
    return _PeerEntry(
        endpoint=endpoint,
        peer_id=peer_id,
        mldsa_pubkey_hex=pubkey,
        key_id=key_id,
        authorized_actor_ids=_require_authorized_actor_ids(peer.get("authorized_actor_ids")),
        valid_from_epoch=valid_from,
        valid_until_epoch=valid_until,
    )


class GossipPeerRegistry:
    """Static v1 peer registry — no dynamic discovery."""

    def __init__(
        self,
        peers: Sequence[str | Mapping[str, Any]],
        *,
        allow_private_address_literals: bool = False,
    ) -> None:
        normalized_entries_by_endpoint: dict[str, _PeerEntry] = {}
        entries_by_peer_id: dict[str, _PeerEntry] = {}
        for peer in peers:
            entry = _normalize_peer_entry(
                peer,
                allow_private_address_literals=allow_private_address_literals,
            )
            if entry.endpoint in normalized_entries_by_endpoint:
                continue
            normalized_entries_by_endpoint[entry.endpoint] = entry
            if entry.peer_id is not None:
                if entry.peer_id in entries_by_peer_id:
                    raise ValueError("peer_id_duplicate")
                entries_by_peer_id[entry.peer_id] = entry
        if len(normalized_entries_by_endpoint) > MAX_PEERS:
            raise ValueError('peer_registry_exceeds_max_peers')
        self._entries = tuple(normalized_entries_by_endpoint.values())
        self._peers = [entry.endpoint for entry in self._entries]
        self._entries_by_peer_id = entries_by_peer_id
        self._allow_private_address_literals = allow_private_address_literals

    def peer_count(self) -> int:
        return len(self._peers)

    def get_peers(self) -> list[str]:
        return list(self._peers)

    def get_peer_pubkey(self, peer_id: str) -> str | None:
        entry = self._entries_by_peer_id.get(peer_id)
        if entry is None:
            return None
        return entry.mldsa_pubkey_hex

    def get_peer_key_id(self, peer_id: str) -> str | None:
        entry = self._entries_by_peer_id.get(peer_id)
        if entry is None:
            return None
        return entry.key_id

    def get_authorized_actor_ids(self, peer_id: str) -> tuple[str, ...]:
        entry = self._entries_by_peer_id.get(peer_id)
        if entry is None:
            return ()
        return entry.authorized_actor_ids

    def is_actor_authorized_for_peer(self, peer_id: str, claimed_actor: str) -> bool:
        if not isinstance(claimed_actor, str):
            return False
        return claimed_actor in self.get_authorized_actor_ids(peer_id)

    def is_peer_key_valid(self, peer_id: str, epoch: int) -> bool:
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            return False
        entry = self._entries_by_peer_id.get(peer_id)
        if entry is None or entry.mldsa_pubkey_hex is None:
            return False
        if epoch < entry.valid_from_epoch:
            return False
        return entry.valid_until_epoch is None or epoch <= entry.valid_until_epoch

    def select_fanout_peers(self, fanout: int, exclude: list[str] | None = None) -> list[str]:
        """Return static-v1 deterministic fanout.

        The current lexicographic prefix selection is retained to avoid a
        silent network-behavior change in a security cleanup phase. Rotating or
        hash-derived fanout should be introduced under CDL-103/dynamic
        discovery, where anti-eclipse tradeoffs are reviewed explicitly.
        """
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
