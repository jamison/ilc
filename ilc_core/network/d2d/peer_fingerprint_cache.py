# SPDX-License-Identifier: AGPL-3.0-or-later
"""H-013 peer fingerprint cache — Phase 931.

Rolling cache of received peer spectral fingerprints, keyed by peer_endpoint.
Feeds query_route_index_spectral() with live peer fingerprint data, closing
the gap between the CDL-080 L3 spectral routing primitive and real beacon data.

Eviction policy: overwrite-only (H-013 Q3 = Option D). Entries are replaced
when a newer beacon arrives from the same peer; they are never evicted by epoch
alone. Use is_dead_peer() to detect silent peers separately from staleness.

ADR basis: ADR-0034 (sealed sender — agent_id is None when relayed, present
when this node was the terminal recipient).
CDL basis: CDL-080 (L3 spectral routing; query_route_index_spectral() consumer).
Gate: H-013 sequence lock 930; emission wiring in Phase 936.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


PEER_FINGERPRINT_CACHE_VERSION = "peer_fingerprint_cache_931.v0.1"
H013_SEQUENCE_LOCK_DEPENDENCY = "h013_gossip_beacon_activation_sequence_lock_930.v0.1"
CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"
PEER_FINGERPRINT_CACHE_HARDENING = "peer_fingerprint_cache_max_size_1218b"

# Provisional silence threshold for dead-peer detection.
# A peer is considered dead if it has not sent a beacon for this many epochs.
# SIM-BEACON-01 will calibrate the real figure; 10 epochs is a conservative default.
DEFAULT_DEAD_PEER_SILENCE_EPOCHS: int = 10

# Hard cap on cache size. Prevents OOM DoS from attackers flooding unique peer_endpoint
# strings. Eviction is dead-peer-first (oldest last_seen_epoch), then live-peer LRU.
# Preserves H-013 Q3 = Option D overwrite-only semantics within the bounded set.
DEFAULT_MAX_CACHE_SIZE: int = 5_000


@dataclass(frozen=True)
class PeerFingerprint:
    """Cached spectral fingerprint for a single peer.

    Immutable record — replaced wholesale on update (overwrite-only policy).

    Attributes:
        peer_endpoint: "host:port" or peer ID string identifying the peer.
        lambda_local: noise-perturbed top-k eigenvalues received in the beacon.
            These are the peer's spectral fingerprint of its epistemic neighbourhood.
            Noise was added by the emitting peer at sigma >= MIN_NOISE_SIGMA.
        noise_sigma: noise level the emitting peer declared. Informational only —
            this node cannot verify the actual noise applied.
        last_seen_epoch: epoch at which this fingerprint was last received and
            recorded. Used by is_dead_peer() to detect silent peers.
        agent_id: the peer's agent ID. Present only when this node received the
            beacon as the terminal recipient (ADR-0034 sealed sender: relay nodes
            never see the origin). None when the beacon arrived via relay.
    """

    peer_endpoint: str
    lambda_local: List[float]
    noise_sigma: float
    last_seen_epoch: int
    agent_id: Optional[str] = None


@dataclass
class PeerFingerprintCache:
    """Rolling cache of received peer spectral fingerprints.

    Keyed by peer_endpoint. Overwrite-only (H-013 Q3 = Option D): when a newer
    beacon arrives from the same peer, its entry is unconditionally replaced.
    No epoch-based eviction — a silent peer keeps its last-known fingerprint
    as a routing hint. Use is_dead_peer() to detect silence separately.

    Bounded by max_size (default DEFAULT_MAX_CACHE_SIZE). When at capacity, a
    single entry is evicted before inserting a new peer: dead peers (by
    last_seen_epoch) are evicted first; if all peers are live, the peer with the
    oldest last_seen_epoch is evicted. This preserves Option D semantics while
    preventing OOM DoS from attackers flooding unique peer_endpoint strings.

    Primary consumer: query_route_index_spectral() in star_map_route_index_runtime.py.
    Call as_fingerprint_dict() to produce the {endpoint: lambda_local} mapping
    that query_route_index_spectral() expects. Without live fingerprints from
    this cache, L3 spectral routing falls back to manually-configured test data.

    Population path (Phase 934): node_startup_runtime.py receives beacons via
    gossip transport, peels the sealed envelope, and calls update() on this cache.
    Emission path (Phase 936): this node emits its own beacon at epoch boundaries
    when its fingerprint has changed by more than the change threshold (Q4).

    Thread safety: not thread-safe. Callers must serialise access if the cache
    is shared across threads.
    """

    _entries: Dict[str, PeerFingerprint] = field(default_factory=dict)
    max_size: int = field(default=DEFAULT_MAX_CACHE_SIZE)

    def update(
        self,
        peer_endpoint: str,
        lambda_local: List[float],
        noise_sigma: float,
        epoch: int,
        agent_id: Optional[str] = None,
    ) -> None:
        """Update or insert a peer fingerprint (overwrite-only).

        The existing entry for peer_endpoint, if any, is unconditionally replaced.
        There is no epoch ordering guard — relay forwarding may deliver beacons
        slightly out of order; the most-recently-processed beacon wins. Callers
        that require strict epoch ordering must guard externally.

        Args:
            peer_endpoint: identifying string for the peer.
            lambda_local: the peer's noise-perturbed spectral fingerprint.
            noise_sigma: noise level declared by the emitting peer.
            epoch: epoch at which this beacon was received (from the beacon record,
                not the local node clock — use the beacon's epoch field).
            agent_id: peer's agent ID if this node was the terminal recipient;
                None if received via relay (ADR-0034 sealed sender).
        """
        if peer_endpoint not in self._entries and len(self._entries) >= self.max_size:
            self._evict_one(epoch)
        self._entries[peer_endpoint] = PeerFingerprint(
            peer_endpoint=peer_endpoint,
            lambda_local=list(lambda_local),  # defensive copy
            noise_sigma=noise_sigma,
            last_seen_epoch=epoch,
            agent_id=agent_id,
        )

    def _evict_one(self, current_epoch: int) -> None:
        """Evict one entry to make room. Dead peers evicted first (oldest epoch),
        then live peers by oldest last_seen_epoch. No-op if cache is empty."""
        if not self._entries:
            return
        # Partition into dead and live by default silence threshold.
        dead = [
            fp for fp in self._entries.values()
            if self.is_dead_peer(fp.peer_endpoint, current_epoch)
        ]
        if dead:
            victim = min(dead, key=lambda fp: fp.last_seen_epoch)
        else:
            victim = min(self._entries.values(), key=lambda fp: fp.last_seen_epoch)
        del self._entries[victim.peer_endpoint]

    def get(self, peer_endpoint: str) -> Optional[PeerFingerprint]:
        """Retrieve the cached fingerprint for a peer. None if not cached."""
        return self._entries.get(peer_endpoint)

    def all_fingerprints(self) -> List[PeerFingerprint]:
        """Return all cached PeerFingerprint records, in insertion/update order."""
        return list(self._entries.values())

    def as_fingerprint_dict(self) -> Dict[str, List[float]]:
        """Return {peer_endpoint: lambda_local} for query_route_index_spectral().

        This is the interface contract between the H-013 peer fingerprint cache
        and the CDL-080 L3 spectral routing function. The route index function
        accepts a plain dict; this method produces it from the cache state.

        Returns a snapshot — mutations to the cache after this call do not
        affect the returned dict.
        """
        return {ep: list(fp.lambda_local) for ep, fp in self._entries.items()}

    def is_dead_peer(
        self,
        peer_endpoint: str,
        current_epoch: int,
        silence_threshold: int = DEFAULT_DEAD_PEER_SILENCE_EPOCHS,
    ) -> bool:
        """True if the peer has not sent a beacon in silence_threshold epochs.

        A dead peer's fingerprint remains in the cache (overwrite-only policy),
        but callers may choose to exclude or deprioritise dead peers from
        query_route_index_spectral() results. The fingerprint is not evicted —
        a stale hint is better than no hint for routing purposes.

        Args:
            peer_endpoint: the peer to check.
            current_epoch: the current epoch (from the local node's epoch counter).
            silence_threshold: epochs of silence before declaring dead.
                Default is DEFAULT_DEAD_PEER_SILENCE_EPOCHS (10, provisional).

        Returns:
            False if the peer is not in the cache (unknown ≠ dead).
            True if (current_epoch - last_seen_epoch) > silence_threshold.
        """
        fp = self._entries.get(peer_endpoint)
        if fp is None:
            return False  # not in cache — unknown, not dead
        return (current_epoch - fp.last_seen_epoch) > silence_threshold

    def live_fingerprint_dict(
        self,
        current_epoch: int,
        silence_threshold: int = DEFAULT_DEAD_PEER_SILENCE_EPOCHS,
    ) -> Dict[str, List[float]]:
        """Return fingerprint dict excluding dead peers.

        Convenience method combining as_fingerprint_dict() with dead-peer
        filtering. Suitable for routing queries where stale hints would
        degrade result quality.
        """
        return {
            ep: list(fp.lambda_local)
            for ep, fp in self._entries.items()
            if not self.is_dead_peer(ep, current_epoch, silence_threshold)
        }

    def peer_count(self) -> int:
        """Number of distinct peers in the cache (live and dead combined)."""
        return len(self._entries)

    def live_peer_count(
        self,
        current_epoch: int,
        silence_threshold: int = DEFAULT_DEAD_PEER_SILENCE_EPOCHS,
    ) -> int:
        """Number of peers that have sent a beacon within silence_threshold epochs."""
        return sum(
            1 for ep in self._entries
            if not self.is_dead_peer(ep, current_epoch, silence_threshold)
        )

    def remove(self, peer_endpoint: str) -> None:
        """Explicitly remove a peer from the cache.

        Not used during normal operation — the cache is overwrite-only. Available
        for operator-level cache management (e.g. on confirmed peer departure or
        operator-directed peer banning). No-op if peer_endpoint is not cached.
        """
        self._entries.pop(peer_endpoint, None)
