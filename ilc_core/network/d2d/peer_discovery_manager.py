# SPDX-License-Identifier: AGPL-3.0-only
"""Testnet-enabled dynamic peer discovery manager for GAP-DISCOV-03.

The manager coordinates local advertisement construction, incoming advertisement
validation, and deterministic introduction sampling. It performs no network I/O
and does not activate public sidecar serving or production listener surfaces.
"""

from __future__ import annotations

import hashlib
from typing import Any, Callable, Mapping, Sequence

from ilc_core.crypto.pq_signature_verify import verify_mldsa65_signature
from ilc_core.network.d2d.peer_advertisement import (
    MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS,
    PEER_ADVERTISEMENT_SCHEMA_VERSION,
    PeerAdvertisement,
    TransportEndpoint,
)


DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED = False
PEER_DISCOVERY_RUNTIME_VERSION = "dynamic_peer_discovery_gap_discov_03.v0.1"
DEFAULT_AD_BROADCAST_INTERVAL_EPOCHS = 1
DEFAULT_INTRODUCTION_SET_SIZE = 8

_SHA384_EMPTY_SLICE_DIGEST = hashlib.sha384(b"").hexdigest()


class PeerDiscoveryManager:
    def __init__(
        self,
        registry: Any,
        local_agent_id: str,
        vrf_key: bytes,
        ml_dsa_key_pair: Any,
        *,
        transport_endpoint: Mapping[str, Any] | TransportEndpoint | None = None,
        protocol_version: str = "ilc-d2d-gossip.v1",
        installed_slices_digest: str = _SHA384_EMPTY_SLICE_DIGEST,
        content_availability_count: int = 0,
        key_binding_ref: str = "cdl103_key_binding_ref_unratified",
        key_binding_resolver: Callable[[PeerAdvertisement], str | None] | Mapping[str, str] | None = None,
    ) -> None:
        self.registry = registry
        self.local_agent_id = local_agent_id
        self.vrf_key = _require_bytes(vrf_key, "peer_discovery_vrf_key_invalid")
        self.ml_dsa_key_pair = ml_dsa_key_pair
        self.transport_endpoint = _coerce_endpoint(transport_endpoint)
        self.protocol_version = protocol_version
        self.installed_slices_digest = installed_slices_digest
        self.content_availability_count = content_availability_count
        self.key_binding_ref = key_binding_ref
        self.key_binding_resolver = key_binding_resolver
        self.broadcast_log: list[PeerAdvertisement] = []

    def broadcast_advertisement(self, current_epoch: int) -> PeerAdvertisement:
        """Create and locally record a signed PeerAdvertisement."""

        _require_guard_cleared()
        unsigned = PeerAdvertisement.from_dict(
            {
                "body": {
                    "agent_id": self.local_agent_id,
                    "content_availability_count": self.content_availability_count,
                    "installed_slices_digest": self.installed_slices_digest,
                    "peer_timestamp_epoch": current_epoch,
                    "protocol_version": self.protocol_version,
                    "transport_endpoint": self.transport_endpoint.to_dict(),
                    "ttl_epochs": DEFAULT_AD_BROADCAST_INTERVAL_EPOCHS + 3,
                },
                "key_binding_ref": self.key_binding_ref,
                "ml_dsa_signature": "0" * 6618,
                "schema_version": PEER_ADVERTISEMENT_SCHEMA_VERSION,
            }
        )
        signature = _sign(self.ml_dsa_key_pair, unsigned.to_canonical_json())
        ad = PeerAdvertisement.from_dict(
            {
                "body": unsigned.body_dict(),
                "key_binding_ref": self.key_binding_ref,
                "ml_dsa_signature": signature,
                "schema_version": PEER_ADVERTISEMENT_SCHEMA_VERSION,
            }
        )
        self.broadcast_log.append(ad)
        return ad

    def handle_incoming_advertisement(
        self,
        ad: PeerAdvertisement,
        current_epoch: int,
    ) -> bool:
        """Validate and add an incoming advertisement to the guarded registry."""

        _require_guard_cleared()
        if not isinstance(ad, PeerAdvertisement):
            raise ValueError("peer_advertisement_invalid")
        _reject_future_skew(ad, current_epoch)
        if ad.is_expired(current_epoch):
            return False
        pubkey_hex = self._resolve_pubkey(ad)
        if pubkey_hex is None:
            return False
        if not ad.verify(verify_mldsa65_signature, pubkey_hex=pubkey_hex):
            return False
        return bool(self.registry.add_peer_advertisement(ad, current_epoch))

    def request_introduction(
        self,
        bootstrap_peer: Any,
        current_epoch: int,
    ) -> list[PeerAdvertisement]:
        """Request local/mock introduction ads from a bootstrap object."""

        _require_guard_cleared()
        if hasattr(bootstrap_peer, "provide_introduction_ads"):
            candidate_ads = list(bootstrap_peer.provide_introduction_ads(current_epoch))
        elif isinstance(bootstrap_peer, Sequence) and not isinstance(bootstrap_peer, (str, bytes)):
            candidate_ads = list(bootstrap_peer)
        else:
            raise ValueError("peer_introduction_bootstrap_invalid")
        sample = self.sample_introduction_set(candidate_ads, self.vrf_key)
        self.registry.add_introduction_entries(sample)
        return sample

    def sample_introduction_set(
        self,
        candidate_ads: Sequence[PeerAdvertisement],
        vrf_public_key: bytes,
        k: int = DEFAULT_INTRODUCTION_SET_SIZE,
    ) -> list[PeerAdvertisement]:
        """Select a deterministic hash-ranked introduction set.

        No PRNG is used. Each candidate is ranked by SHA-256 over the caller's
        VRF public key bytes and the advertisement canonical body. This is an
        anti-eclipse mitigation mechanism only, not a formal guarantee.
        """

        vrf_key = _require_bytes(vrf_public_key, "peer_discovery_vrf_public_key_invalid")
        if isinstance(k, bool) or not isinstance(k, int) or k < 0:
            raise ValueError("peer_introduction_k_invalid")
        normalized: dict[str, PeerAdvertisement] = {}
        for ad in candidate_ads:
            if not isinstance(ad, PeerAdvertisement):
                raise ValueError("peer_introduction_candidate_invalid")
            normalized[ad.agent_id] = ad
        if not normalized or k == 0:
            return []
        ranked = sorted(
            normalized.values(),
            key=lambda ad: (
                hashlib.sha256(vrf_key + ad.to_canonical_json()).hexdigest(),
                ad.agent_id,
            ),
        )
        return ranked[: min(k, len(ranked))]

    def _resolve_pubkey(self, ad: PeerAdvertisement) -> str | None:
        resolver = self.key_binding_resolver
        if resolver is None:
            return None
        if isinstance(resolver, Mapping):
            value = resolver.get(ad.key_binding_ref)
            return value if isinstance(value, str) else None
        value = resolver(ad)
        return value if isinstance(value, str) else None


def _require_guard_cleared() -> None:
    if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED:
        raise RuntimeError("dynamic_peer_discovery_not_activated")


def _reject_future_skew(ad: PeerAdvertisement, current_epoch: int) -> None:
    if isinstance(current_epoch, bool) or not isinstance(current_epoch, int) or current_epoch < 0:
        raise ValueError("peer_discovery_current_epoch_invalid")
    if ad.peer_timestamp_epoch > current_epoch + MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS:
        raise ValueError("peer_advertisement_timestamp_future_skew")


def _coerce_endpoint(
    value: Mapping[str, Any] | TransportEndpoint | None,
) -> TransportEndpoint:
    if value is None:
        value = {"scheme": "https", "host": "peer.example.com", "port": 443}
    if isinstance(value, TransportEndpoint):
        return value
    return TransportEndpoint.from_mapping(value)


def _require_bytes(value: Any, token: str) -> bytes:
    if type(value) is not bytes or not value:
        raise ValueError(token)
    return value


def _sign(ml_dsa_key_pair: Any, payload: bytes) -> str:
    if callable(ml_dsa_key_pair):
        signature = ml_dsa_key_pair(payload)
    elif hasattr(ml_dsa_key_pair, "sign"):
        signature = ml_dsa_key_pair.sign(payload)
    else:
        raise ValueError("peer_discovery_mldsa_signer_invalid")
    if isinstance(signature, bytes):
        signature = signature.hex()
    if not isinstance(signature, str):
        raise ValueError("peer_discovery_mldsa_signature_invalid")
    return signature
