# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 562 static gossip peer registry with GAP-DISCOV-03 testnet discovery.

This module keeps the static peer list as authoritative fallback while allowing
the CDL-103 PeerAdvertisement dynamic table in testnet scope. It does not create
a listener, enable public sidecar serving, or authorize DHT discovery.
"""

from __future__ import annotations

import ipaddress
import json
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlsplit

from ilc_core.crypto.pq_signature_verify import (
    CDL_101_SIGNED_ENVELOPE_DEPENDENCY,
    _MLDSA_PK_HEX_LENGTH,
    verify_mldsa65_signature,
)
from ilc_core.network.d2d.gossip_transport import (
    GOSSIP_TRANSPORT_RUNTIME_VERSION as _GOSSIP_TRANSPORT_CHECK,
)
from ilc_core.network.d2d.peer_advertisement import (
    MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS,
    MAX_PEER_ADVERTISEMENT_EPOCH,
    PeerAdvertisement,
)
from ilc_core.sidecars.connectivity_advertisement import (
    CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED,
    CONNECTIVITY_ADVERTISEMENT_VERIFICATION_CONTEXT,
    ConnectivityAdvertisement,
    VerifiedConnectivityAdvertisement,
)


GOSSIP_PEER_REGISTRY_VERSION = "gossip_peer_registry_1571.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"
GOSSIP_TRANSPORT_DEPENDENCY = "gossip_transport_runtime_1572.v0.1"
PEER_DISCOVERY_MODE = "static_plus_dynamic_testnet_v1"
DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED = False
LEXICOGRAPHIC_FANOUT_ROTATION_DEFERRED_TOKEN = (
    "lexicographic_gossip_fanout_rotation_deferred_pending_cdl_103_phase_1575h_fix2"
)
MAX_PEERS = 16
N_MAX = 1000
MAX_INTRODUCTION_CANDIDATES = N_MAX
MAX_BOOTSTRAP_HINTS = 8
MAX_BOOTSTRAP_HINTS_FILE_BYTES = 1_048_576
BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION = "bootstrap_peer_hints.v0.1"
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

# PEER_DISCOVERY_MODE is a constitutional invariant. CDL-103 Phase 1583 permits
# advertisement-based dynamic discovery only in the bounded testnet runtime.
# CDL-039 topology privacy remains in force: cdl_039_topology_privacy.
if PEER_DISCOVERY_MODE != "static_plus_dynamic_testnet_v1":
    raise RuntimeError(
        f"cdl_103_dynamic_peer_discovery: unsupported peer discovery mode, "
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


@dataclass(frozen=True)
class VerifiedPeerAdvertisement:
    """Manager-verified advertisement envelope required for registry insertion."""

    advertisement: PeerAdvertisement
    verification_context: str = "mldsa65_signature_verified_cdl103"


def _require_peer_string(value: Any, token: str, max_chars: int) -> str:
    if not isinstance(value, str):
        raise ValueError(token)
    normalized = value.strip()
    if not normalized or len(normalized) > max_chars or any(char.isspace() for char in normalized):
        raise ValueError(token)
    return normalized


def _require_epoch(value: Any, token: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > MAX_PEER_ADVERTISEMENT_EPOCH
    ):
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
    """Static v1 peer registry with default-off dynamic advertisement support."""

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
        self._dynamic_ad_table: dict[str, PeerAdvertisement] = {}
        self._connectivity_ad_table: dict[str, ConnectivityAdvertisement] = {}
        self._vrf_introduction_table: dict[str, PeerAdvertisement] = {}

    def peer_count(self) -> int:
        return len(self.get_peers())

    def get_peers(self) -> list[str]:
        if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED or not self._dynamic_ad_table:
            return list(self._peers)
        dynamic_endpoints = [
            ad.endpoint_url
            for ad in sorted(self._dynamic_ad_table.values(), key=lambda item: item.agent_id)
            if ad.endpoint_url not in self._peers
        ]
        return list(self._peers) + dynamic_endpoints

    def add_peer_advertisement(
        self,
        verified_ad: VerifiedPeerAdvertisement,
        current_epoch: int,
    ) -> bool:
        """Add or replace a manager-verified dynamic advertisement."""

        if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED:
            raise RuntimeError("dynamic_peer_discovery_not_activated")
        current = _require_epoch(current_epoch, "peer_advertisement_current_epoch_invalid")
        if not isinstance(verified_ad, VerifiedPeerAdvertisement):
            raise ValueError("peer_advertisement_requires_verified_envelope")
        ad = verified_ad.advertisement
        if not isinstance(ad, PeerAdvertisement):
            raise ValueError("peer_advertisement_invalid")
        if verified_ad.verification_context != "mldsa65_signature_verified_cdl103":
            raise ValueError("peer_advertisement_verification_context_invalid")
        if ad.peer_timestamp_epoch > current + MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS:
            raise ValueError("peer_advertisement_timestamp_future_skew")
        if ad.is_expired(current):
            return False
        if ad.endpoint_url in self._peers:
            return False
        existing = self._dynamic_ad_table.get(ad.agent_id)
        if existing is None and len(self._dynamic_ad_table) >= N_MAX:
            return False
        if any(
            agent_id != ad.agent_id and existing_ad.endpoint_url == ad.endpoint_url
            for agent_id, existing_ad in self._dynamic_ad_table.items()
        ):
            return False
        if existing is not None and ad.peer_timestamp_epoch < existing.peer_timestamp_epoch:
            return False
        self._dynamic_ad_table[ad.agent_id] = ad
        return True

    def expire_ads(self, current_epoch: int) -> int:
        current = _require_epoch(current_epoch, "peer_advertisement_current_epoch_invalid")
        expired_agent_ids = [
            agent_id
            for agent_id, ad in self._dynamic_ad_table.items()
            if ad.is_expired(current)
        ]
        for agent_id in expired_agent_ids:
            del self._dynamic_ad_table[agent_id]
            self._vrf_introduction_table.pop(agent_id, None)
        return len(expired_agent_ids)

    def get_dynamic_peers(self, current_epoch: int | None = None) -> list[PeerAdvertisement]:
        if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED:
            return []
        if current_epoch is not None:
            self.expire_ads(current_epoch)
        return sorted(self._dynamic_ad_table.values(), key=lambda item: item.agent_id)

    def add_connectivity_advertisement(
        self,
        verified_ad: VerifiedConnectivityAdvertisement,
        current_epoch: int,
    ) -> bool:
        """Add or replace a verified CDL-112 connectivity advertisement.

        This table is separate from CDL-103 peer fanout and remains inaccessible
        while CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED is True.
        """

        if CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED:
            raise RuntimeError("connectivity_advertisement_not_activated")
        current = _require_epoch(
            current_epoch,
            "connectivity_advertisement_current_epoch_invalid",
        )
        if not isinstance(verified_ad, VerifiedConnectivityAdvertisement):
            raise ValueError("connectivity_advertisement_requires_verified_envelope")
        ad = verified_ad.advertisement
        if not isinstance(ad, ConnectivityAdvertisement):
            raise ValueError("connectivity_advertisement_invalid")
        if verified_ad.verification_context != CONNECTIVITY_ADVERTISEMENT_VERIFICATION_CONTEXT:
            raise ValueError("connectivity_advertisement_verification_context_invalid")
        if ad.peer_timestamp_epoch > current + MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS:
            raise ValueError("connectivity_advertisement_timestamp_future_skew")
        if ad.is_expired(current):
            return False
        existing = self._connectivity_ad_table.get(ad.agent_id)
        if existing is None and len(self._connectivity_ad_table) >= N_MAX:
            return False
        advertised_urls = {ad.endpoint_url}
        advertised_urls.update(endpoint.to_url() for endpoint in ad.candidate_list)
        if ad.relay_endpoint is not None:
            advertised_urls.add(ad.relay_endpoint.to_url())
        for agent_id, existing_ad in self._connectivity_ad_table.items():
            if agent_id == ad.agent_id:
                continue
            existing_urls = {existing_ad.endpoint_url}
            existing_urls.update(endpoint.to_url() for endpoint in existing_ad.candidate_list)
            if existing_ad.relay_endpoint is not None:
                existing_urls.add(existing_ad.relay_endpoint.to_url())
            if advertised_urls & existing_urls:
                return False
        if existing is not None and ad.peer_timestamp_epoch < existing.peer_timestamp_epoch:
            return False
        self._connectivity_ad_table[ad.agent_id] = ad
        return True

    def expire_connectivity_ads(self, current_epoch: int) -> int:
        current = _require_epoch(
            current_epoch,
            "connectivity_advertisement_current_epoch_invalid",
        )
        expired_agent_ids = [
            agent_id
            for agent_id, ad in self._connectivity_ad_table.items()
            if ad.is_expired(current)
        ]
        for agent_id in expired_agent_ids:
            del self._connectivity_ad_table[agent_id]
        return len(expired_agent_ids)

    def get_connectivity_advertisements(
        self,
        current_epoch: int | None = None,
    ) -> list[ConnectivityAdvertisement]:
        if CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED:
            return []
        if current_epoch is not None:
            self.expire_connectivity_ads(current_epoch)
        return sorted(self._connectivity_ad_table.values(), key=lambda item: item.agent_id)

    def load_bootstrap_hints(self, path: Path | str, *, current_epoch: int) -> int:
        """Load locally persisted, self-verifiable invite bootstrap peer hints."""

        current = _require_epoch(current_epoch, "bootstrap_peer_hints_current_epoch_invalid")
        if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED:
            raise RuntimeError("dynamic_peer_discovery_not_activated")
        hints_path = Path(path).expanduser()
        try:
            with hints_path.open("rb") as handle:
                raw = handle.read(MAX_BOOTSTRAP_HINTS_FILE_BYTES + 1)
            if len(raw) > MAX_BOOTSTRAP_HINTS_FILE_BYTES:
                raise ValueError("bootstrap_peer_hints_file_too_large")
            payload = json.loads(raw.decode("utf-8"))
        except ValueError:
            raise
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("bootstrap_peer_hints_file_invalid") from exc
        if not isinstance(payload, Mapping):
            raise ValueError("bootstrap_peer_hints_file_invalid")
        if payload.get("schema_version") != BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION:
            raise ValueError("bootstrap_peer_hints_schema_version_invalid")

        raw_hints = payload.get("known_peer_hints")
        if not isinstance(raw_hints, list) or len(raw_hints) > MAX_BOOTSTRAP_HINTS:
            raise ValueError("bootstrap_peer_hints_invalid")
        key_bindings = payload.get("known_peer_hint_key_bindings")
        if not isinstance(key_bindings, Mapping):
            raise ValueError("bootstrap_peer_hint_key_bindings_invalid")
        normalized_bindings = {
            _require_peer_string(key, "bootstrap_peer_hint_key_binding_ref_invalid", 256):
            _require_mldsa_pubkey_hex(value)
            for key, value in key_bindings.items()
        }

        loaded = 0
        for raw_hint in raw_hints:
            try:
                ad = PeerAdvertisement.from_dict(
                    raw_hint,
                    allow_private_address_literals=self._allow_private_address_literals,
                )
            except Exception as exc:
                raise ValueError("bootstrap_peer_hint_invalid") from exc
            if ad.peer_timestamp_epoch > current + MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS:
                continue
            if ad.is_expired(current):
                continue
            pubkey_hex = normalized_bindings.get(ad.key_binding_ref)
            if pubkey_hex is None or not ad.verify(
                verify_mldsa65_signature,
                pubkey_hex=pubkey_hex,
            ):
                raise ValueError("bootstrap_peer_hint_signature_invalid")
            if self.add_peer_advertisement(
                VerifiedPeerAdvertisement(advertisement=ad),
                current,
            ):
                loaded += 1
        return loaded

    def add_introduction_entries(self, ads: Iterable[PeerAdvertisement]) -> None:
        if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED:
            raise RuntimeError("dynamic_peer_discovery_not_activated")
        if isinstance(ads, (str, bytes)) or not isinstance(ads, Iterable):
            raise ValueError("peer_introduction_entries_invalid")
        bounded_ads: list[PeerAdvertisement] = []
        for index, ad in enumerate(ads):
            if index >= MAX_INTRODUCTION_CANDIDATES:
                raise ValueError("peer_introduction_entries_exceed_n_max")
            if not isinstance(ad, PeerAdvertisement):
                raise ValueError("peer_introduction_entry_invalid")
            bounded_ads.append(ad)
        self._vrf_introduction_table = {
            ad.agent_id: ad
            for ad in sorted(bounded_ads, key=lambda item: item.agent_id)
        }

    def get_introduction_entries(self) -> list[PeerAdvertisement]:
        if DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED:
            return []
        return sorted(self._vrf_introduction_table.values(), key=lambda item: item.agent_id)

    def get_static_peers(self) -> list[str]:
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
        """Return deterministic lexicographic fanout over static and dynamic peers.

        CDL-103 (ratified Phase 1583) activates dynamic discovery; fanout now
        includes dynamic advertisement endpoints via get_peers(). The lexicographic
        selection order is retained. Hash-derived rotation remains deferred per
        LEXICOGRAPHIC_FANOUT_ROTATION_DEFERRED_TOKEN pending explicit eclipse-resistance review.
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
        available = sorted(peer for peer in self.get_peers() if peer not in excluded)
        return available[:fanout]
