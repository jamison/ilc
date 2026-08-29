# SPDX-License-Identifier: AGPL-3.0-only
"""Guarded relay/rendezvous server implementation.

The server side mirrors :mod:`ilc_core.network.relay.relay_client`: Option A
admission verifies invite proof-of-possession and a second relay-admission BLS
signature before issuing a bounded slot grant. The forwarding primitive is
pass-through only: it accounts opaque QUIC/UDP bytes by slot and never
terminates, decrypts, re-signs, rewrites, or re-originates consensus messages.
The current relay data plane proves per-slot client address binding and opaque
UDP forwarding only. General third-party NAT traversal, arbitrary peer relay
reachability, and validator-grade relay readiness require DEPLOY-00 topology
smoke evidence across distinct hosts or network namespaces.

This module is source-only until GAP-RELAY-RENDEZVOUS-DEPLOY-00 clears
``RELAY_SERVER_NOT_ACTIVATED`` and starts it on live validator hosts.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import TimeoutError as FutureTimeoutError
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
import heapq
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import math
import re
import secrets
import ssl
import threading
import time
from typing import Any, Callable
from urllib.parse import urlparse

from ilc_core import __version__ as ILC_CORE_VERSION
from ilc_core.identity.bls_backend import (
    sign_relay_bootstrap_record_digest,
    verify_relay_bootstrap_capsule_digest,
    verify_relay_bootstrap_record_digest,
    verify_relay_lifecycle_digest,
)
from ilc_core.network.relay.relay_client import (
    RELAY_CLIENT_SCHEMA_VERSION,
    RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC,
    RelayAdmissionRequest,
    RelayClientError,
    RelayEndpoint,
    RelaySlotGrant,
    relay_lifecycle_payload_ref,
)


RELAY_SERVER_NOT_ACTIVATED = True
RELAY_SERVER_SCHEMA_VERSION = "relay_server_GAP_RELAY_SERVER_IMPL_00.v0.1"
RELAY_SERVER_TOKEN = "relay_server_impl_committed_GAP_RELAY_SERVER_IMPL_00"
RELAY_ABUSE_LIMITS_SCHEMA_VERSION = "relay_abuse_limits_GAP_RELAY_ABUSE_LIMITS_FIX1_00.v0.1"

RELAY_ADMISSION_REQUEST_PATH = "/relay/admission/request"
RELAY_SLOT_KEEPALIVE_PATH = "/relay/slot/keepalive"
RELAY_SLOT_RELEASE_PATH = "/relay/slot/release"
RELAY_HEALTH_PATH = "/relay/health"

_DEFAULT_NETWORK_ID = "public-rc"
_DEFAULT_RELAY_PORT = 50151
_DEFAULT_CONTROL_PORT = 51151
_DEFAULT_DATA_PORT_RANGE_START = 52000
_DEFAULT_DATA_PORT_RANGE_END = 52999
_RELAY_BOOTSTRAP_RECORD_SCHEMA_VERSION = "relay_bootstrap_record_v0.1"
_RELAY_BOOTSTRAP_CAPSULE_SCHEMA_VERSION = "relay_bootstrap_capsule_v0.1"
_RELAY_BOOTSTRAP_SIGNATURE_ALG = "BLS12-381-G2-SHA-256-SSWU-RO"
_TLS_MODE_PINNED_DER_SHA256 = "pinned_der_sha256"
_TLS_MODE_LOOPBACK_ONLY = "loopback_only"
_MAX_REQUEST_BYTES = 32_768
_MAX_RESPONSE_BYTES = 65_536
_MAX_DATAGRAM_BYTES = 65_535
_DATA_PLANE_OPERATION_TIMEOUT_SECONDS = 5.0
_MAX_EPOCH = (1 << 64) - 1
_MAX_TTL_EPOCHS = 4
_MAX_BYTES_PER_EPOCH = 64 * 1024 * 1024
_MAX_CONCURRENT_STREAMS = 8
_MAX_TEXT_CHARS = 512
_MAX_ACTIVE_SLOTS = 1024
_MAX_PACKETS_PER_WINDOW = 1000
_PACKET_RATE_WINDOW_SECONDS = 1.0
_MAX_FAILED_ATTEMPTS = 5
_FAILED_ADMISSION_COOLDOWN_SECONDS = 60.0
_MAX_FAILED_ADMISSION_ENTRIES = 65_536
_MAX_RELAY_RECORDS_PER_CAPSULE = 8
_TOMBSTONE_RETENTION_EPOCHS = 8
_MAX_TOMBSTONES = _MAX_ACTIVE_SLOTS * (_TOMBSTONE_RETENTION_EPOCHS + 1)
_CONTROLLED_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_RELAY_BOOTSTRAP_RECORD_PAYLOAD_KEYS = frozenset(
    {
        "control_port",
        "control_url",
        "data_port_range",
        "expires_epoch",
        "issued_epoch",
        "network_id",
        "relay_agent_id",
        "relay_host",
        "relay_mode",
        "schema_version",
        "tls_cert_der_sha256",
        "tls_mode",
    }
)
_RELAY_BOOTSTRAP_RECORD_KEYS = _RELAY_BOOTSTRAP_RECORD_PAYLOAD_KEYS | frozenset(
    {"payload_sha384", "signature", "signature_alg", "signing_key_id"}
)
_RELAY_BOOTSTRAP_CAPSULE_PAYLOAD_KEYS = frozenset(
    {"expires_epoch", "issued_epoch", "network_id", "relay_records", "schema_version"}
)
_RELAY_BOOTSTRAP_CAPSULE_KEYS = _RELAY_BOOTSTRAP_CAPSULE_PAYLOAD_KEYS | frozenset(
    {"payload_sha384", "signature", "signature_alg", "signing_key_id"}
)
_ADMISSION_FAILURE_TOKENS = frozenset(
    {
        "relay_admission_payload_ref_invalid",
        "relay_admission_payload_ref_mismatch",
        "relay_admission_payload_ref_required",
        "relay_admission_signature_invalid",
        "relay_admission_signature_required",
        "relay_admission_signature_verification_failed",
        "relay_agent_id_invalid",
        "relay_base_url_invalid",
        "relay_base_url_required",
        "relay_invite_id_invalid",
        "relay_invite_nullifier_invalid",
        "relay_invite_pop_epoch_invalid",
        "relay_invite_pop_invalid",
        "relay_invite_pop_payload_ref_invalid",
        "relay_invite_pop_verification_failed",
        "relay_requested_internal_port_must_be_port_int",
        "relay_requested_internal_port_out_of_range",
        "relay_requested_protocol_must_be_quic",
        "relay_software_version_invalid",
    }
)


class RelayServerError(ValueError):
    """Raised when relay server input or lifecycle state is invalid."""


@dataclass(frozen=True)
class RelayServerConfig:
    """Configuration for one relay-serving ILC node.

    ``relay_port`` is retained for compatibility with pre-transport-fix callers.
    Admission grants now use per-slot UDP ports from
    ``data_port_range_start``..``data_port_range_end``.
    """

    relay_agent_id: str
    relay_host: str
    relay_port: int = _DEFAULT_RELAY_PORT
    network_id: str = _DEFAULT_NETWORK_ID
    ttl_epochs: int = _MAX_TTL_EPOCHS
    max_bytes_per_epoch: int = _MAX_BYTES_PER_EPOCH
    max_concurrent_streams: int = _MAX_CONCURRENT_STREAMS
    data_port_range_start: int = _DEFAULT_DATA_PORT_RANGE_START
    data_port_range_end: int = _DEFAULT_DATA_PORT_RANGE_END
    control_port: int = _DEFAULT_CONTROL_PORT
    tombstone_retention_epochs: int = _TOMBSTONE_RETENTION_EPOCHS
    ssl_certfile: str | None = None
    ssl_keyfile: str | None = None

    def __post_init__(self) -> None:
        _require_agent_id(self.relay_agent_id, "relay_server_agent_id_invalid")
        _require_host(self.relay_host, "relay_server_host_invalid")
        _require_port(self.relay_port, "relay_server_port_invalid")
        _require_network_id(self.network_id)
        _require_uint_range(
            self.ttl_epochs,
            "relay_server_ttl_epochs_invalid",
            1,
            _MAX_TTL_EPOCHS,
        )
        _require_uint_range(
            self.max_bytes_per_epoch,
            "relay_server_max_bytes_per_epoch_invalid",
            1,
            _MAX_BYTES_PER_EPOCH,
        )
        _require_uint_range(
            self.max_concurrent_streams,
            "relay_server_max_concurrent_streams_invalid",
            1,
            _MAX_CONCURRENT_STREAMS,
        )
        data_start = _require_port(
            self.data_port_range_start,
            "relay_data_port_range_start_invalid",
        )
        data_end = _require_port(
            self.data_port_range_end,
            "relay_data_port_range_end_invalid",
        )
        if data_start > data_end:
            raise RelayServerError("relay_data_port_range_invalid")
        control_port = _require_port(self.control_port, "relay_control_port_invalid")
        if data_start <= control_port <= data_end:
            raise RelayServerError("relay_control_port_overlaps_data_range")
        _require_uint_range(
            self.tombstone_retention_epochs,
            "relay_tombstone_retention_epochs_invalid",
            0,
            _MAX_TTL_EPOCHS * 16,
        )
        certfile = _require_optional_path(
            self.ssl_certfile,
            "relay_ssl_certfile_invalid",
        )
        keyfile = _require_optional_path(
            self.ssl_keyfile,
            "relay_ssl_keyfile_invalid",
        )
        if (certfile is None) != (keyfile is None):
            raise RelayServerError("relay_ssl_config_incomplete")
        if not _host_is_loopback(self.relay_host) and certfile is None:
            raise RelayServerError("relay_non_loopback_requires_tls")

    @property
    def relay_base_url(self) -> str:
        host = self.relay_host
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        scheme = "https"
        if self.ssl_certfile is None and self.ssl_keyfile is None and _host_is_loopback(
            self.relay_host
        ):
            scheme = "http"
        return f"{scheme}://{host}:{self.control_port}"


@dataclass(frozen=True)
class RelaySlotState:
    """In-memory state for a granted relay slot."""

    grant: RelaySlotGrant
    target_host: str
    allocated_data_port: int | None = None
    bytes_forwarded_this_epoch: int = 0
    current_epoch: int | None = None
    status: str = "active"
    revocation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "allocated_data_port": self.allocated_data_port,
            "bytes_forwarded_this_epoch": self.bytes_forwarded_this_epoch,
            "current_epoch": self.current_epoch,
            "grant": self.grant.to_dict(),
            "revocation_reason": self.revocation_reason,
            "schema_version": RELAY_SERVER_SCHEMA_VERSION,
            "status": self.status,
            "target_host": self.target_host,
        }


@dataclass(frozen=True)
class RelayForwardReceipt:
    """Receipt for an opaque pass-through forwarding decision."""

    slot_id: str
    agent_id: str
    bytes_forwarded: int
    epoch: int
    relay_mode: str = RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC
    status: str = "forwarded"

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "bytes_forwarded": self.bytes_forwarded,
            "epoch": self.epoch,
            "relay_mode": self.relay_mode,
            "schema_version": RELAY_SERVER_SCHEMA_VERSION,
            "slot_id": self.slot_id,
            "status": self.status,
        }

    def to_canonical_json(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


@dataclass(frozen=True)
class RelayRevocationReceipt:
    """Self-certifying local receipt for relay slot revocation."""

    slot_id: str
    agent_id: str
    epoch: int
    reason_token: str
    bytes_forwarded: int
    revocation_ref: str

    def __post_init__(self) -> None:
        _require_token(self.slot_id, "relay_revocation_slot_id_invalid")
        _require_agent_id(self.agent_id, "relay_revocation_agent_id_invalid")
        _require_epoch(self.epoch, "relay_revocation_epoch_invalid")
        _require_token(self.reason_token, "relay_revocation_reason_invalid")
        _require_uint_range(
            self.bytes_forwarded,
            "relay_revocation_bytes_forwarded_invalid",
            0,
            _MAX_BYTES_PER_EPOCH,
        )
        _require_sha256_hex(self.revocation_ref, "relay_revocation_ref_invalid")

    @classmethod
    def build(
        cls,
        *,
        slot_id: str,
        agent_id: str,
        epoch: int,
        reason_token: str,
        bytes_forwarded: int,
    ) -> "RelayRevocationReceipt":
        payload = {
            "agent_id": _require_agent_id(agent_id, "relay_revocation_agent_id_invalid"),
            "bytes_forwarded": _require_uint_range(
                bytes_forwarded,
                "relay_revocation_bytes_forwarded_invalid",
                0,
                _MAX_BYTES_PER_EPOCH,
            ),
            "epoch": _require_epoch(epoch, "relay_revocation_epoch_invalid"),
            "reason_token": _require_token(
                reason_token,
                "relay_revocation_reason_invalid",
            ),
            "slot_id": _require_token(slot_id, "relay_revocation_slot_id_invalid"),
        }
        # Self-certifying receipt: hash exactly the other five canonical fields.
        revocation_ref = hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()
        return cls(**payload, revocation_ref=revocation_ref)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "bytes_forwarded": self.bytes_forwarded,
            "epoch": self.epoch,
            "reason_token": self.reason_token,
            "revocation_ref": self.revocation_ref,
            "schema_version": RELAY_ABUSE_LIMITS_SCHEMA_VERSION,
            "slot_id": self.slot_id,
        }

    def to_canonical_json(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


@dataclass(frozen=True)
class _RelayTombstone:
    """Bounded terminal-state record for released, expired, or revoked slots."""

    slot_id: str
    status: str
    terminated_epoch: int
    revocation_receipt: RelayRevocationReceipt | None = None
    data_port: int | None = None

    def __post_init__(self) -> None:
        _require_token(self.slot_id, "relay_tombstone_slot_id_invalid")
        if self.status not in {"released", "expired", "revoked"}:
            raise RelayServerError("relay_tombstone_status_invalid")
        _require_epoch(self.terminated_epoch, "relay_tombstone_epoch_invalid")
        if self.data_port is not None:
            _require_port(self.data_port, "relay_tombstone_data_port_invalid")
        if self.status == "revoked" and self.revocation_receipt is None:
            raise RelayServerError("relay_tombstone_revocation_receipt_required")
        if self.status != "revoked" and self.revocation_receipt is not None:
            raise RelayServerError("relay_tombstone_revocation_receipt_forbidden")


@dataclass
class _PacketRateBucket:
    window_start: float
    packet_count: int = 0

    def allow(self) -> bool:
        # time.monotonic() is local infrastructure rate limiting only, not a
        # protocol epoch, settlement, keepalive, or consensus-validity clock.
        now = time.monotonic()
        if not math.isfinite(now):
            raise RelayServerError("relay_packet_rate_clock_invalid")
        if now - self.window_start >= _PACKET_RATE_WINDOW_SECONDS:
            self.window_start = now
            self.packet_count = 0
        if self.packet_count >= _MAX_PACKETS_PER_WINDOW:
            return False
        self.packet_count += 1
        return True


@dataclass
class _FailedAdmissionEntry:
    attempt_count: int
    first_attempt: float
    last_attempt: float


class _FailedAdmissionTracker:
    """Bounded local failed-admission cooldown tracker."""

    def __init__(
        self,
        *,
        max_entries: int = _MAX_FAILED_ADMISSION_ENTRIES,
        now_provider: Callable[[], float] = time.monotonic,
    ) -> None:
        self._entries: dict[str, _FailedAdmissionEntry] = {}
        self._insertion_order: deque[str] = deque()
        self._queued_keys: set[str] = set()
        self._max_entries = _require_uint_range(
            max_entries,
            "relay_failed_admission_max_entries_invalid",
            1,
            _MAX_FAILED_ADMISSION_ENTRIES,
        )
        self._now_provider = now_provider

    def record_failure(self, key: str) -> None:
        clean_key = _require_admission_tracker_key(key)
        now = self._now()
        entry = self._entries.get(clean_key)
        if entry is None:
            self._evict_if_needed()
            self._entries[clean_key] = _FailedAdmissionEntry(
                attempt_count=1,
                first_attempt=now,
                last_attempt=now,
            )
            if clean_key not in self._queued_keys:
                self._insertion_order.append(clean_key)
                self._queued_keys.add(clean_key)
            return
        if self._cooldown_elapsed(entry, now):
            self._entries[clean_key] = _FailedAdmissionEntry(
                attempt_count=1,
                first_attempt=now,
                last_attempt=now,
            )
            return
        self._entries[clean_key] = _FailedAdmissionEntry(
            attempt_count=entry.attempt_count + 1,
            first_attempt=entry.first_attempt,
            last_attempt=now,
        )

    def is_blocked(self, key: str) -> bool:
        clean_key = _require_admission_tracker_key(key)
        now = self._now()
        entry = self._entries.get(clean_key)
        if entry is None or entry.attempt_count < _MAX_FAILED_ATTEMPTS:
            return False
        if self._cooldown_elapsed(entry, now):
            self._drop_key(clean_key)
            return False
        return True

    def failure_count(self, key: str) -> int:
        entry = self._entries.get(_require_admission_tracker_key(key))
        return 0 if entry is None else entry.attempt_count

    def _evict_if_needed(self) -> None:
        while len(self._entries) >= self._max_entries:
            if not self._insertion_order:
                self._entries.clear()
                self._queued_keys.clear()
                return
            oldest = self._insertion_order.popleft()
            if oldest not in self._queued_keys or oldest not in self._entries:
                continue
            self._drop_key(oldest, remove_from_order=False)

    def _drop_key(self, clean_key: str, *, remove_from_order: bool = True) -> None:
        self._entries.pop(clean_key, None)
        self._queued_keys.discard(clean_key)
        if remove_from_order:
            try:
                self._insertion_order.remove(clean_key)
            except ValueError:
                pass

    def _cooldown_elapsed(self, entry: _FailedAdmissionEntry, now: float) -> bool:
        return now - entry.last_attempt >= _FAILED_ADMISSION_COOLDOWN_SECONDS

    def _now(self) -> float:
        now = self._now_provider()
        if not math.isfinite(now):
            raise RelayServerError("relay_failed_admission_clock_invalid")
        return now


class _RelayPortPool:
    """Thread-safe lowest-free allocator for per-slot UDP data ports."""

    def __init__(self, start: int, end: int) -> None:
        self._start = _require_port(start, "relay_data_port_range_start_invalid")
        self._end = _require_port(end, "relay_data_port_range_end_invalid")
        if self._start > self._end:
            raise RelayServerError("relay_data_port_range_invalid")
        self._available: list[int] = list(range(self._start, self._end + 1))
        heapq.heapify(self._available)
        self._allocated: set[int] = set()
        self._lock = threading.Lock()

    def allocate(self) -> int:
        with self._lock:
            if not self._available:
                raise RelayServerError("relay_data_port_pool_exhausted")
            port = heapq.heappop(self._available)
            self._allocated.add(port)
            return port

    def release(self, port: int) -> None:
        try:
            clean_port = _require_port(port, "relay_data_port_release_invalid")
        except RelayServerError:
            return
        if clean_port < self._start or clean_port > self._end:
            return
        with self._lock:
            if clean_port not in self._allocated:
                return
            self._allocated.remove(clean_port)
            heapq.heappush(self._available, clean_port)

    @property
    def available_count(self) -> int:
        with self._lock:
            return len(self._available)


class RelayRendezvousServer:
    """Option A relay admission and lifecycle state machine."""

    def __init__(
        self,
        config: RelayServerConfig,
        *,
        enable_data_plane: bool = False,
        epoch_provider: Callable[[], int] | None = None,
        receipt_sink: Callable[[RelayForwardReceipt, tuple[str, int]], None] | None = None,
        data_plane_bind_host: str = "0.0.0.0",
    ) -> None:
        self.config = config
        self._slots_by_id: dict[str, RelaySlotState] = {}
        self._active_slot_by_agent: dict[str, str] = {}
        self._packet_rate_buckets: dict[str, _PacketRateBucket] = {}
        self._failed_admissions = _FailedAdmissionTracker()
        self._tombstones: dict[str, _RelayTombstone] = {}
        self._tombstone_order: deque[str] = deque()
        self._state_lock = threading.RLock()
        self._active_slot_count = 0
        self._port_pool = _RelayPortPool(
            self.config.data_port_range_start,
            self.config.data_port_range_end,
        )
        self._data_plane: RelayDataPlaneRuntime | None = None
        if enable_data_plane:
            self._data_plane = RelayDataPlaneRuntime(
                self,
                self._port_pool,
                epoch_provider=epoch_provider or (lambda: 0),
                receipt_sink=receipt_sink,
                bind_host=data_plane_bind_host,
            )
            self._data_plane.start()

    @property
    def active_slot_count(self) -> int:
        with self._state_lock:
            return self._active_slot_count

    def health(self) -> dict[str, Any]:
        with self._state_lock:
            return {
                "active_slot_count": self._active_slot_count,
                "data_port_range_end": self.config.data_port_range_end,
                "data_port_range_start": self.config.data_port_range_start,
                "ilc_core_version": ILC_CORE_VERSION,
                "relay_agent_id": self.config.relay_agent_id,
                "schema_version": RELAY_SERVER_SCHEMA_VERSION,
                "server_guard_active": RELAY_SERVER_NOT_ACTIVATED,
            }

    def request_slot(
        self,
        payload: Mapping[str, Any],
        *,
        source_host: str = "127.0.0.1",
    ) -> dict[str, Any]:
        # Admission classification:
        # Pre-lock safe: request shape/field validation, payload-ref checks,
        # invite PoP BLS verification, and relay admission BLS verification are
        # performed by RelayAdmissionRequest construction below.
        # Lock-required: failed-admission cooldown checks, tracker mutation,
        # active-slot checks, tombstone GC, port allocation, slot insertion, and
        # active-agent/rate-bucket state mutation.
        body = _require_mapping(payload, "relay_request_body_must_be_object")
        source_host = _require_host(source_host, "relay_source_host_invalid")
        ip_key = _admission_ip_key(source_host)
        agent_key = _admission_agent_key(body.get("agent_id"))
        with self._state_lock:
            self._require_admission_not_blocked(ip_key, agent_key)
        try:
            request = _coerce_admission_request(body)
        except (RelayClientError, RelayServerError, ValueError) as exc:
            token = _error_token(exc)
            if token in _ADMISSION_FAILURE_TOKENS:
                if self._record_admission_failure(ip_key, agent_key):
                    raise RelayServerError("relay_admission_cooldown_active") from exc
            raise
        with self._state_lock:
            self._require_admission_not_blocked(ip_key, agent_key)
            if self._active_slot_count >= _MAX_ACTIVE_SLOTS:
                raise RelayServerError("relay_server_active_slot_limit_exceeded")
            self._gc_tombstones(request.admission_epoch)
            if request.network_id != self.config.network_id:
                raise RelayServerError("relay_admission_network_id_mismatch")
            if request.relay_base_url != self.config.relay_base_url:
                raise RelayServerError("relay_admission_base_url_mismatch")
            if request.agent_id in self._active_slot_by_agent:
                raise RelayServerError("relay_slot_already_active")
            slot_id = f"slot-{secrets.token_hex(16)}"
            allocated_port = self._port_pool.allocate()
            active_count_incremented = False
            try:
                grant = RelaySlotGrant(
                    slot_id=slot_id,
                    agent_id=request.agent_id,
                    relay_endpoint=RelayEndpoint(
                        host=self.config.relay_host,
                        port=allocated_port,
                    ),
                    granted_epoch=request.admission_epoch,
                    ttl_epochs=self.config.ttl_epochs,
                    target_internal_port=request.requested_internal_port,
                    max_bytes_per_epoch=self.config.max_bytes_per_epoch,
                    max_concurrent_streams=self.config.max_concurrent_streams,
                    admission_request_hash=request.canonical_request_hash,
                    relay_slot_nonce=secrets.token_hex(32),
                )
                self._slots_by_id[slot_id] = RelaySlotState(
                    grant=grant,
                    target_host=source_host,
                    allocated_data_port=allocated_port,
                    current_epoch=request.admission_epoch,
                )
                self._active_slot_by_agent[request.agent_id] = slot_id
                self._active_slot_count += 1
                active_count_incremented = True
                self._packet_rate_buckets[slot_id] = _PacketRateBucket(
                    window_start=time.monotonic(),
                )
                if self._data_plane is not None:
                    self._data_plane.open_slot(
                        slot_id,
                        target_host=source_host,
                        target_port=request.requested_internal_port,
                        allocated_port=allocated_port,
                        relay_slot_nonce=grant.relay_slot_nonce,
                    )
            except Exception:
                self._slots_by_id.pop(slot_id, None)
                self._active_slot_by_agent.pop(request.agent_id, None)
                if active_count_incremented:
                    self._decrement_active_slot_count()
                self._packet_rate_buckets.pop(slot_id, None)
                self._port_pool.release(allocated_port)
                raise
            return {"grant": grant.to_dict(), "schema_version": RELAY_SERVER_SCHEMA_VERSION}

    def keepalive(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        with self._state_lock:
            slot = self._require_active_slot(payload.get("slot_id"))
            agent_id = _require_agent_id(
                payload.get("agent_id"),
                "relay_keepalive_agent_id_invalid",
            )
            if agent_id != slot.grant.agent_id:
                raise RelayServerError("relay_keepalive_agent_id_mismatch")
            epoch = _require_epoch(payload.get("keepalive_epoch"), "relay_keepalive_epoch_invalid")
            self._validate_lifecycle_epoch_snapshot(slot, epoch)
            previous_hash = _require_sha256_hex(
                payload.get("previous_grant_hash"),
                "relay_previous_grant_hash_invalid",
            )
            if previous_hash != slot.grant.canonical_response_hash:
                raise RelayServerError("relay_previous_grant_hash_mismatch")
            payload_ref = _require_sha384_hex(
                payload.get("relay_lifecycle_payload_ref"),
                "relay_lifecycle_payload_ref_invalid",
            )
            self._verify_lifecycle_payload_ref(
                action="keepalive",
                agent_id=agent_id,
                epoch=epoch,
                payload_ref=payload_ref,
                previous_grant_hash=previous_hash,
                slot_id=slot.grant.slot_id,
            )
            slot_id = slot.grant.slot_id
            grant_hash = slot.grant.canonical_response_hash
            signature = payload.get("relay_lifecycle_signature")
        _verify_lifecycle_signature(
            agent_id=agent_id,
            payload_ref=payload_ref,
            signature=signature,
        )
        with self._state_lock:
            slot = self._require_active_slot(slot_id)
            if slot.grant.agent_id != agent_id:
                raise RelayServerError("relay_keepalive_agent_id_mismatch")
            if slot.grant.canonical_response_hash != grant_hash:
                raise RelayServerError("relay_previous_grant_hash_mismatch")
            self._require_lifecycle_epoch(slot, epoch)
            if slot.status != "active":
                raise RelayServerError(f"relay_slot_{slot.status}")
            self._slots_by_id[slot.grant.slot_id] = RelaySlotState(
                grant=slot.grant,
                target_host=slot.target_host,
                allocated_data_port=slot.allocated_data_port,
                bytes_forwarded_this_epoch=slot.bytes_forwarded_this_epoch,
                current_epoch=epoch,
            )
            return {
                "agent_id": agent_id,
                "keepalive_epoch": epoch,
                "previous_grant_hash": previous_hash,
                "relay_lifecycle_payload_ref": payload_ref,
                "renewal_result": "renewed",
                "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
                "slot_id": slot.grant.slot_id,
            }

    def release(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        with self._state_lock:
            slot = self._require_active_slot(payload.get("slot_id"))
            agent_id = _require_agent_id(payload.get("agent_id"), "relay_release_agent_id_invalid")
            if agent_id != slot.grant.agent_id:
                raise RelayServerError("relay_release_agent_id_mismatch")
            epoch = _require_epoch(payload.get("release_epoch"), "relay_release_epoch_invalid")
            self._validate_lifecycle_epoch_snapshot(slot, epoch)
            previous_hash = _require_sha256_hex(
                payload.get("previous_grant_hash"),
                "relay_previous_grant_hash_invalid",
            )
            if previous_hash != slot.grant.canonical_response_hash:
                raise RelayServerError("relay_previous_grant_hash_mismatch")
            payload_ref = _require_sha384_hex(
                payload.get("relay_lifecycle_payload_ref"),
                "relay_lifecycle_payload_ref_invalid",
            )
            self._verify_lifecycle_payload_ref(
                action="release",
                agent_id=agent_id,
                epoch=epoch,
                payload_ref=payload_ref,
                previous_grant_hash=previous_hash,
                slot_id=slot.grant.slot_id,
            )
            slot_id = slot.grant.slot_id
            grant_hash = slot.grant.canonical_response_hash
            signature = payload.get("relay_lifecycle_signature")
        _verify_lifecycle_signature(
            agent_id=agent_id,
            payload_ref=payload_ref,
            signature=signature,
        )
        with self._state_lock:
            slot = self._require_active_slot(slot_id)
            if slot.grant.agent_id != agent_id:
                raise RelayServerError("relay_release_agent_id_mismatch")
            if slot.grant.canonical_response_hash != grant_hash:
                raise RelayServerError("relay_previous_grant_hash_mismatch")
            self._require_lifecycle_epoch(slot, epoch)
            self._release_slot(slot.grant.slot_id, terminated_epoch=epoch)
            return {
                "agent_id": agent_id,
                "previous_grant_hash": previous_hash,
                "release_epoch": epoch,
                "relay_lifecycle_payload_ref": payload_ref,
                "release_result": "released",
                "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
                "slot_id": slot.grant.slot_id,
            }

    def forward_datagram(
        self,
        *,
        slot_id: str,
        payload: bytes,
        epoch: int,
    ) -> tuple[RelayForwardReceipt, RelayRevocationReceipt | None]:
        with self._state_lock:
            slot = self._require_active_slot(slot_id)
            epoch = _require_epoch(epoch, "relay_forward_epoch_invalid")
            self._require_lifecycle_epoch(slot, epoch)
            clean_payload = _require_datagram(payload)
            bucket = self._packet_rate_buckets.setdefault(
                slot.grant.slot_id,
                _PacketRateBucket(window_start=time.monotonic()),
            )
            if not bucket.allow():
                revocation = self._revoke_slot(
                    slot.grant.slot_id,
                    "relay_slot_revoked_packet_rate_exceeded",
                    terminated_epoch=epoch,
                )
                return (
                    RelayForwardReceipt(
                        slot_id=slot.grant.slot_id,
                        agent_id=slot.grant.agent_id,
                        bytes_forwarded=0,
                        epoch=epoch,
                        status="revoked",
                    ),
                    revocation,
                )
            prior_bytes = slot.bytes_forwarded_this_epoch
            if slot.current_epoch != epoch:
                prior_bytes = 0
            next_total = prior_bytes + len(clean_payload)
            if next_total > slot.grant.max_bytes_per_epoch:
                revocation = self._revoke_slot(
                    slot.grant.slot_id,
                    "relay_slot_revoked_budget_exceeded",
                    terminated_epoch=epoch,
                )
                return (
                    RelayForwardReceipt(
                        slot_id=slot.grant.slot_id,
                        agent_id=slot.grant.agent_id,
                        bytes_forwarded=0,
                        epoch=epoch,
                        status="revoked",
                    ),
                    revocation,
                )
            self._slots_by_id[slot.grant.slot_id] = RelaySlotState(
                grant=slot.grant,
                target_host=slot.target_host,
                allocated_data_port=slot.allocated_data_port,
                bytes_forwarded_this_epoch=next_total,
                current_epoch=epoch,
            )
            return (
                RelayForwardReceipt(
                    slot_id=slot.grant.slot_id,
                    agent_id=slot.grant.agent_id,
                    bytes_forwarded=len(clean_payload),
                    epoch=epoch,
                ),
                None,
            )

    def handle_json_request(
        self,
        *,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None,
        source_host: str = "127.0.0.1",
    ) -> tuple[int, dict[str, Any]]:
        try:
            if method == "GET" and path == RELAY_HEALTH_PATH:
                return 200, self.health()
            if method != "POST":
                return 405, {"error": "relay_method_not_allowed"}
            body = _require_mapping(payload, "relay_request_body_must_be_object")
            if path == RELAY_ADMISSION_REQUEST_PATH:
                return 200, self.request_slot(body, source_host=source_host)
            if path == RELAY_SLOT_KEEPALIVE_PATH:
                return 200, self.keepalive(body)
            if path == RELAY_SLOT_RELEASE_PATH:
                return 200, self.release(body)
            return 404, {"error": "relay_path_not_found"}
        except (RelayClientError, RelayServerError, ValueError) as exc:
            return 400, {"error": _error_token(exc)}

    def _verify_lifecycle_payload_ref(
        self,
        *,
        action: str,
        agent_id: str,
        epoch: int,
        payload_ref: str,
        previous_grant_hash: str,
        slot_id: str,
    ) -> None:
        expected = relay_lifecycle_payload_ref(
            action=action,
            agent_id=agent_id,
            slot_id=slot_id,
            lifecycle_epoch=epoch,
            previous_grant_hash=previous_grant_hash,
            network_id=self.config.network_id,
            relay_base_url=self.config.relay_base_url,
        )
        if payload_ref != expected:
            raise RelayServerError("relay_lifecycle_payload_ref_mismatch")

    def _require_admission_not_blocked(self, ip_key: str, agent_key: str | None) -> None:
        if self._failed_admissions.is_blocked(ip_key):
            raise RelayServerError("relay_admission_cooldown_active")
        if agent_key is not None and self._failed_admissions.is_blocked(agent_key):
            raise RelayServerError("relay_admission_cooldown_active")

    def _record_admission_failure(self, ip_key: str, agent_key: str | None) -> bool:
        with self._state_lock:
            was_blocked = self._failed_admissions.is_blocked(ip_key)
            if agent_key is not None:
                was_blocked = was_blocked or self._failed_admissions.is_blocked(agent_key)
            if was_blocked:
                return True
            self._failed_admissions.record_failure(ip_key)
            if agent_key is not None:
                self._failed_admissions.record_failure(agent_key)
            return was_blocked

    def _require_lifecycle_epoch(self, slot: RelaySlotState, epoch: int) -> None:
        if epoch < slot.grant.granted_epoch:
            raise RelayServerError("relay_lifecycle_epoch_before_grant")
        if epoch > slot.grant.granted_epoch + slot.grant.ttl_epochs:
            self._expire_slot(slot.grant.slot_id, terminated_epoch=epoch)
            raise RelayServerError("relay_lifecycle_epoch_after_expiry")

    def _validate_lifecycle_epoch_snapshot(self, slot: RelaySlotState, epoch: int) -> None:
        if epoch < slot.grant.granted_epoch:
            raise RelayServerError("relay_lifecycle_epoch_before_grant")

    def _require_known_slot(self, slot_id: object) -> RelaySlotState:
        clean_slot_id = _require_token(slot_id, "relay_slot_id_invalid")
        slot = self._slots_by_id.get(clean_slot_id)
        if slot is None:
            tombstone = self._tombstones.get(clean_slot_id)
            if tombstone is None:
                raise RelayServerError("relay_slot_not_found")
            if tombstone.status == "revoked" and tombstone.revocation_receipt is not None:
                raise RelayServerError(tombstone.revocation_receipt.reason_token)
            raise RelayServerError(f"relay_slot_{tombstone.status}")
        return slot

    def _require_active_slot(self, slot_id: object) -> RelaySlotState:
        slot = self._require_known_slot(slot_id)
        if slot.status == "active":
            return slot
        if slot.status == "revoked" and slot.revocation_reason:
            raise RelayServerError(slot.revocation_reason)
        raise RelayServerError(f"relay_slot_{slot.status}")

    def _release_slot(self, slot_id: str, *, terminated_epoch: int | None = None) -> None:
        slot = self._slots_by_id[slot_id]
        self._release_data_port(slot_id, slot)
        if slot.status == "active":
            self._decrement_active_slot_count()
        self._slots_by_id.pop(slot_id, None)
        self._track_tombstone(_RelayTombstone(
            slot_id=slot_id,
            status="released",
            terminated_epoch=self._terminal_epoch(slot, terminated_epoch),
            data_port=slot.allocated_data_port,
        ))
        self._active_slot_by_agent.pop(slot.grant.agent_id, None)
        self._packet_rate_buckets.pop(slot_id, None)

    def _expire_slot(self, slot_id: str, *, terminated_epoch: int | None = None) -> None:
        slot = self._slots_by_id[slot_id]
        self._release_data_port(slot_id, slot)
        if slot.status == "active":
            self._decrement_active_slot_count()
        self._slots_by_id.pop(slot_id, None)
        self._track_tombstone(_RelayTombstone(
            slot_id=slot_id,
            status="expired",
            terminated_epoch=self._terminal_epoch(slot, terminated_epoch),
            data_port=slot.allocated_data_port,
        ))
        self._active_slot_by_agent.pop(slot.grant.agent_id, None)
        self._packet_rate_buckets.pop(slot_id, None)

    def _revoke_slot(
        self,
        slot_id: str,
        reason_token: str,
        *,
        terminated_epoch: int | None = None,
    ) -> RelayRevocationReceipt:
        slot = self._slots_by_id[slot_id]
        self._release_data_port(slot_id, slot)
        if slot.status == "active":
            self._decrement_active_slot_count()
        epoch = self._terminal_epoch(slot, terminated_epoch)
        receipt = RelayRevocationReceipt.build(
            slot_id=slot.grant.slot_id,
            agent_id=slot.grant.agent_id,
            epoch=epoch,
            reason_token=reason_token,
            bytes_forwarded=slot.bytes_forwarded_this_epoch,
        )
        self._slots_by_id.pop(slot_id, None)
        self._track_tombstone(_RelayTombstone(
            slot_id=slot_id,
            status="revoked",
            terminated_epoch=epoch,
            revocation_receipt=receipt,
            data_port=slot.allocated_data_port,
        ))
        self._active_slot_by_agent.pop(slot.grant.agent_id, None)
        self._packet_rate_buckets.pop(slot_id, None)
        return receipt

    def _release_data_port(self, slot_id: str, slot: RelaySlotState) -> None:
        if self._data_plane is not None:
            try:
                self._data_plane.close_slot(slot_id)
            except RelayServerError as exc:
                if _error_token(exc) != "relay_data_plane_slot_not_open":
                    raise
        if slot.allocated_data_port is not None:
            self._port_pool.release(slot.allocated_data_port)

    def _terminal_epoch(self, slot: RelaySlotState, epoch: int | None) -> int:
        if epoch is not None:
            return _require_epoch(epoch, "relay_tombstone_epoch_invalid")
        if slot.current_epoch is not None:
            return _require_epoch(slot.current_epoch, "relay_tombstone_epoch_invalid")
        return _require_epoch(slot.grant.granted_epoch, "relay_tombstone_epoch_invalid")

    def _gc_tombstones(self, current_epoch: int) -> None:
        clean_epoch = _require_epoch(current_epoch, "relay_tombstone_gc_epoch_invalid")
        cutoff = clean_epoch - self.config.tombstone_retention_epochs
        if cutoff > 0:
            expired = [
                slot_id
                for slot_id, tombstone in self._tombstones.items()
                if tombstone.terminated_epoch < cutoff
            ]
            for slot_id in expired:
                self._drop_tombstone(slot_id)
        self._trim_tombstones_to_cap()

    def _track_tombstone(self, tombstone: _RelayTombstone) -> None:
        if tombstone.slot_id not in self._tombstones:
            self._tombstone_order.append(tombstone.slot_id)
        self._tombstones[tombstone.slot_id] = tombstone
        self._gc_tombstones(tombstone.terminated_epoch)

    def _drop_tombstone(self, slot_id: str) -> None:
        self._tombstones.pop(slot_id, None)
        try:
            self._tombstone_order.remove(slot_id)
        except ValueError:
            pass

    def _trim_tombstones_to_cap(self) -> None:
        while len(self._tombstones) > _MAX_TOMBSTONES:
            if not self._tombstone_order:
                oldest_slot_id = min(
                    self._tombstones,
                    key=lambda key: self._tombstones[key].terminated_epoch,
                )
                self._tombstones.pop(oldest_slot_id, None)
                continue
            slot_id = self._tombstone_order.popleft()
            if slot_id in self._tombstones:
                self._tombstones.pop(slot_id, None)

    def get_revocation_receipt(self, slot_id: object) -> RelayRevocationReceipt | None:
        clean_slot_id = _require_token(slot_id, "relay_slot_id_invalid")
        tombstone = self._tombstones.get(clean_slot_id)
        if tombstone is None:
            return None
        return tombstone.revocation_receipt

    def _decrement_active_slot_count(self) -> None:
        if self._active_slot_count <= 0:
            raise RelayServerError("relay_active_slot_count_underflow")
        self._active_slot_count -= 1


class RelayUdpForwarder:
    """Bounded opaque QUIC/UDP pass-through helper.

    The class intentionally accepts an explicit ``slot_id`` supplied by the
    caller rather than parsing or modifying QUIC payloads. That preserves the
    non-termination invariant and makes forwarding authorization auditable.
    """

    def __init__(self, server: RelayRendezvousServer) -> None:
        self._server = server

    def forward(
        self,
        *,
        slot_id: str,
        payload: bytes,
        epoch: int,
    ) -> tuple[RelayForwardReceipt, RelayRevocationReceipt | None]:
        return self._server.forward_datagram(slot_id=slot_id, payload=payload, epoch=epoch)


class RelayUdpPortForwarder(asyncio.DatagramProtocol):
    """Asyncio UDP protocol that forwards opaque bytes for one relay slot.

    The first sender on the dedicated slot port becomes the relay requester
    only after sending the per-slot nonce as the prefix of its first datagram.
    The learned client-side address is the source address of that nonce claim
    as seen by the relay socket. For NATed clients, this is the post-NAT
    address:port. The first non-requester sender is then bound as that slot's
    peer. Subsequent datagrams are forwarded only between those two addresses.
    Unknown sources are dropped without parsing or rewriting QUIC bytes.
    """

    def __init__(
        self,
        server: RelayRendezvousServer,
        *,
        slot_id: str,
        target_host: str,
        target_port: int,
        relay_slot_nonce: str,
        epoch_provider: Callable[[], int],
        receipt_sink: Callable[[RelayForwardReceipt, tuple[str, int]], None] | None = None,
    ) -> None:
        self._server = server
        self._slot_id = _require_token(slot_id, "relay_udp_slot_id_invalid")
        _require_host(target_host, "relay_udp_target_host_invalid")
        _require_port(target_port, "relay_udp_target_port_invalid")
        self._nonce = _require_relay_slot_nonce_bytes(relay_slot_nonce)
        self._nonce_verified = False
        self._epoch_provider = epoch_provider
        self._receipt_sink = receipt_sink
        self._client_addr: tuple[str, int] | None = None
        self._peer_addr: tuple[str, int] | None = None
        self._client_addr_lock = threading.Lock()
        self._last_error_lock = threading.Lock()
        self._transport: asyncio.DatagramTransport | None = None
        self._closed = False
        self._last_error: str | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        if not isinstance(transport, asyncio.DatagramTransport):
            self._set_last_error("relay_udp_transport_invalid")
            return
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        if self._closed:
            self._set_last_error("relay_udp_forwarder_closed")
            return
        if self._transport is None:
            self._set_last_error("relay_udp_transport_not_ready")
            return
        try:
            sender = _require_socket_addr(addr, "relay_udp_sender_addr_invalid")
            payload = data
            if not self._is_nonce_verified():
                payload = self._claim_client_addr(sender, payload)
                if payload is None:
                    return
            destination = self._destination_for_sender(sender)
            if destination is None:
                self._set_last_error("relay_udp_peer_not_bound")
                return
            receipt, revocation = self._server.forward_datagram(
                slot_id=self._slot_id,
                payload=payload,
                epoch=self._epoch_provider(),
            )
            if revocation is not None:
                self._set_last_error(revocation.reason_token)
                self._closed = True
                self._transport.close()
                return
            self._transport.sendto(payload, destination)
        except RelayServerError as exc:
            self._set_last_error(_error_token(exc))
            return
        self._set_last_error(None)
        if self._receipt_sink is not None:
            self._receipt_sink(receipt, sender)

    def error_received(self, exc: Exception) -> None:
        self._set_last_error(_error_token(exc))

    def connection_lost(self, exc: Exception | None) -> None:
        self._closed = True
        self._set_last_error(None if exc is None else _error_token(exc))

    @property
    def client_addr(self) -> tuple[str, int] | None:
        with self._client_addr_lock:
            return self._client_addr

    @property
    def last_error(self) -> str | None:
        with self._last_error_lock:
            return self._last_error

    def _destination_for_sender(self, sender: tuple[str, int]) -> tuple[str, int] | None:
        with self._client_addr_lock:
            if self._client_addr is None:
                return None
            if sender == self._client_addr:
                return self._peer_addr
            if self._peer_addr is None:
                self._peer_addr = sender
                return self._client_addr
            if sender == self._peer_addr:
                return self._client_addr
        return None

    def _claim_client_addr(self, sender: tuple[str, int], data: bytes) -> bytes | None:
        if not data.startswith(self._nonce):
            self._set_last_error("relay_udp_nonce_mismatch")
            return None
        with self._client_addr_lock:
            if self._client_addr is None:
                self._client_addr = sender
                self._nonce_verified = True
        payload = data[len(self._nonce):]
        if not payload:
            self._set_last_error(None)
            return None
        return payload

    def _is_nonce_verified(self) -> bool:
        with self._client_addr_lock:
            return self._nonce_verified

    def _set_last_error(self, value: str | None) -> None:
        with self._last_error_lock:
            self._last_error = value


class RelayDataPlaneRuntime:
    """Owns the relay UDP asyncio loop and one forwarder per active slot."""

    def __init__(
        self,
        server: RelayRendezvousServer,
        port_pool: _RelayPortPool,
        *,
        epoch_provider: Callable[[], int],
        receipt_sink: Callable[[RelayForwardReceipt, tuple[str, int]], None] | None = None,
        bind_host: str = "0.0.0.0",
    ) -> None:
        self._server = server
        self._port_pool = port_pool
        self._epoch_provider = epoch_provider
        self._receipt_sink = receipt_sink
        self._bind_host = _require_host(bind_host, "relay_data_plane_bind_host_invalid")
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._running = False
        self._slots: dict[str, tuple[int, asyncio.DatagramTransport, RelayUdpPortForwarder]] = {}
        self._cancelled_slots: set[str] = set()

    def start(self) -> None:
        with self._lock:
            if self._running:
                raise RelayServerError("relay_data_plane_already_running")
            self._ready.clear()
            self._thread = threading.Thread(
                target=self._run_loop,
                name="ilc-relay-data-plane",
                daemon=True,
            )
            self._thread.start()
            if not self._ready.wait(_DATA_PLANE_OPERATION_TIMEOUT_SECONDS):
                raise RelayServerError("relay_data_plane_start_timeout")
            self._running = True

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            slot_ids = list(self._slots)
        for slot_id in slot_ids:
            port = self.close_slot(slot_id)
            self._port_pool.release(port)
        self._loop.call_soon_threadsafe(self._loop.stop)
        thread = self._thread
        if thread is not None:
            thread.join(_DATA_PLANE_OPERATION_TIMEOUT_SECONDS)
        with self._lock:
            self._running = False
            self._thread = None

    def open_slot(
        self,
        slot_id: str,
        *,
        target_host: str,
        target_port: int,
        allocated_port: int,
        relay_slot_nonce: str,
    ) -> None:
        clean_slot_id = _require_token(slot_id, "relay_data_plane_slot_id_invalid")
        clean_target_host = _require_host(target_host, "relay_data_plane_target_host_invalid")
        clean_target_port = _require_port(target_port, "relay_data_plane_target_port_invalid")
        clean_allocated_port = _require_port(allocated_port, "relay_data_plane_port_invalid")
        clean_relay_slot_nonce = _require_relay_slot_nonce(relay_slot_nonce)
        with self._lock:
            if not self._running:
                raise RelayServerError("relay_data_plane_not_running")
            if clean_slot_id in self._slots:
                raise RelayServerError("relay_data_plane_slot_already_open")
            self._cancelled_slots.discard(clean_slot_id)
        future = asyncio.run_coroutine_threadsafe(
            self._open_slot(
                clean_slot_id,
                target_host=clean_target_host,
                target_port=clean_target_port,
                allocated_port=clean_allocated_port,
                relay_slot_nonce=clean_relay_slot_nonce,
            ),
            self._loop,
        )
        try:
            future.result(timeout=_DATA_PLANE_OPERATION_TIMEOUT_SECONDS)
        except FutureTimeoutError as exc:
            future.cancel()
            with self._lock:
                self._cancelled_slots.add(clean_slot_id)
            try:
                self.close_slot(clean_slot_id)
            except RelayServerError:
                pass
            raise RelayServerError("relay_data_plane_open_timeout") from exc

    def close_slot(self, slot_id: str) -> int:
        clean_slot_id = _require_token(slot_id, "relay_data_plane_slot_id_invalid")
        with self._lock:
            if clean_slot_id not in self._slots:
                raise RelayServerError("relay_data_plane_slot_not_open")
        future = asyncio.run_coroutine_threadsafe(
            self._close_slot(clean_slot_id),
            self._loop,
        )
        return future.result(timeout=_DATA_PLANE_OPERATION_TIMEOUT_SECONDS)

    @property
    def active_slot_ports(self) -> dict[str, int]:
        with self._lock:
            return {slot_id: port for slot_id, (port, _transport, _protocol) in self._slots.items()}

    async def _open_slot(
        self,
        slot_id: str,
        *,
        target_host: str,
        target_port: int,
        allocated_port: int,
        relay_slot_nonce: str,
    ) -> None:
        transport, protocol = await self._loop.create_datagram_endpoint(
            lambda: RelayUdpPortForwarder(
                self._server,
                slot_id=slot_id,
                target_host=target_host,
                target_port=target_port,
                relay_slot_nonce=relay_slot_nonce,
                epoch_provider=self._epoch_provider,
                receipt_sink=self._receipt_sink,
            ),
            local_addr=(self._bind_host, allocated_port),
        )
        if not isinstance(protocol, RelayUdpPortForwarder):
            transport.close()
            raise RelayServerError("relay_data_plane_protocol_invalid")
        with self._lock:
            if slot_id in self._cancelled_slots:
                self._cancelled_slots.discard(slot_id)
                transport.close()
                raise RelayServerError("relay_data_plane_open_cancelled")
            if slot_id in self._slots:
                transport.close()
                raise RelayServerError("relay_data_plane_slot_already_open")
            self._slots[slot_id] = (allocated_port, transport, protocol)

    async def _close_slot(self, slot_id: str) -> int:
        with self._lock:
            port, transport, _protocol = self._slots.pop(slot_id)
        transport.close()
        await asyncio.sleep(0)
        return port

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()


# Superseded by RelayUdpPortForwarder. Not exported. Will be removed post-RC.
class RelayUdpDatagramProtocol(asyncio.DatagramProtocol):
    """Asyncio UDP adapter for opaque relay byte accounting.

    Slot selection is supplied out-of-band by the deployment layer using the
    sender address. The relay never parses QUIC frames to discover stream counts
    or identities; stream caps are advertised in the slot grant and must be
    enforced by a future non-terminating transport mechanism before any stronger
    stream-enforcement claim is made.
    """

    def __init__(
        self,
        server: RelayRendezvousServer,
        *,
        slot_id_by_peer: Mapping[tuple[str, int], str],
        epoch_provider: Callable[[], int],
        receipt_sink: Callable[[RelayForwardReceipt, tuple[str, int]], None] | None = None,
    ) -> None:
        self._server = server
        self._slot_id_by_peer = dict(slot_id_by_peer)
        self._epoch_provider = epoch_provider
        self._receipt_sink = receipt_sink
        self.last_error: str | None = None

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        slot_id = self._slot_id_by_peer.get(addr)
        if slot_id is None:
            self.last_error = "relay_udp_peer_not_admitted"
            return
        try:
            receipt, revocation = self._server.forward_datagram(
                slot_id=slot_id,
                payload=data,
                epoch=self._epoch_provider(),
            )
        except RelayServerError as exc:
            self.last_error = _error_token(exc)
            return
        if revocation is not None:
            self.last_error = revocation.reason_token
            return
        self.last_error = None
        if self._receipt_sink is not None:
            self._receipt_sink(receipt, addr)


def make_relay_http_handler(
    relay_server: RelayRendezvousServer,
    *,
    request_timeout_seconds: float = 3.0,
) -> type[BaseHTTPRequestHandler]:
    """Return a bounded stdlib HTTP handler for relay admission/lifecycle."""

    request_timeout = _require_timeout(request_timeout_seconds)

    class RelayHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:  # noqa: N802
            self._dispatch(None)

        def do_POST(self) -> None:  # noqa: N802
            try:
                raw = self._read_request_body()
                payload = json.loads(raw.decode("utf-8"))
            except RelayServerError as exc:
                self._send_json(400, {"error": _error_token(exc)})
                return
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"error": "relay_request_json_invalid"})
                return
            if not isinstance(payload, Mapping):
                self._send_json(400, {"error": "relay_request_body_must_be_object"})
                return
            self._dispatch(payload)

        def log_message(self, *_args: object) -> None:
            return

        def _read_request_body(self) -> bytes:
            self.connection.settimeout(request_timeout)
            length_header = self.headers.get("Content-Length")
            try:
                length = int(length_header or "0")
            except ValueError as exc:
                raise RelayServerError("relay_content_length_invalid") from exc
            if length < 0 or length > _MAX_REQUEST_BYTES:
                raise RelayServerError("relay_request_too_large")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise RelayServerError("relay_request_body_incomplete")
            return raw

        def _dispatch(self, payload: Mapping[str, Any] | None) -> None:
            source_host = str(self.client_address[0])
            status, body = relay_server.handle_json_request(
                method=self.command,
                path=self.path,
                payload=payload,
                source_host=source_host,
            )
            self._send_json(status, body)

        def _send_json(self, status: int, body: Mapping[str, Any]) -> None:
            encoded = _canonical_json_bytes(body)
            if len(encoded) > _MAX_RESPONSE_BYTES:
                encoded = _canonical_json_bytes({"error": "relay_response_too_large"})
                status = 500
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(encoded)

    return RelayHandler


def run_relay_http_server(
    *,
    config: RelayServerConfig,
    bind_host: str,
    bind_port: int | None = None,
    timeout_seconds: float = 3.0,
    allow_guarded_start: bool = False,
) -> None:
    """Start the relay HTTP server after deployment clears the guard."""

    if RELAY_SERVER_NOT_ACTIVATED and not allow_guarded_start:
        raise RelayServerError("relay_server_not_activated")
    bind_host = _require_host(bind_host, "relay_bind_host_invalid")
    bind_port = config.control_port if bind_port is None else _require_port(
        bind_port,
        "relay_bind_port_invalid",
    )
    timeout = _require_timeout(timeout_seconds)
    relay_server = RelayRendezvousServer(
        config,
        enable_data_plane=True,
        data_plane_bind_host=bind_host,
    )

    class _TimedThreadingHTTPServer(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    server = _TimedThreadingHTTPServer(
        (bind_host, bind_port),
        make_relay_http_handler(relay_server, request_timeout_seconds=timeout),
    )
    if config.ssl_certfile is not None and config.ssl_keyfile is not None:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(config.ssl_certfile, config.ssl_keyfile)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
    server.socket.settimeout(timeout)
    try:
        server.serve_forever()
    finally:
        if relay_server._data_plane is not None:
            relay_server._data_plane.stop()
        server.server_close()


def build_relay_bootstrap_record(
    config: RelayServerConfig,
    *,
    issued_epoch: int,
    expires_epoch: int,
    tls_cert_der_sha256: str | None = None,
    tls_mode: str | None = None,
) -> dict[str, Any]:
    """Build an unsigned canonical relay bootstrap record for later signing."""

    issued = _require_epoch(issued_epoch, "relay_bootstrap_record_epoch_invalid")
    expires = _require_epoch(expires_epoch, "relay_bootstrap_record_epoch_invalid")
    if expires <= issued:
        raise RelayServerError("relay_bootstrap_record_epoch_invalid")
    resolved_tls_mode = _require_tls_mode_for_record(
        config.relay_host,
        tls_mode=tls_mode,
        tls_cert_der_sha256=tls_cert_der_sha256,
    )
    cert_sha256 = (
        None
        if tls_cert_der_sha256 is None
        else _require_sha256_hex(
            tls_cert_der_sha256,
            "relay_bootstrap_tls_cert_der_sha256_invalid",
        )
    )
    payload = {
        "control_port": config.control_port,
        "control_url": config.relay_base_url,
        "data_port_range": {
            "end": config.data_port_range_end,
            "start": config.data_port_range_start,
        },
        "expires_epoch": expires,
        "issued_epoch": issued,
        "network_id": config.network_id,
        "relay_agent_id": config.relay_agent_id,
        "relay_host": config.relay_host,
        "relay_mode": RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC,
        "schema_version": _RELAY_BOOTSTRAP_RECORD_SCHEMA_VERSION,
        "tls_cert_der_sha256": cert_sha256,
        "tls_mode": resolved_tls_mode,
    }
    return {
        **payload,
        "payload_sha384": hashlib.sha384(_canonical_json_bytes(payload)).hexdigest(),
        "signature": None,
        "signature_alg": _RELAY_BOOTSTRAP_SIGNATURE_ALG,
        "signing_key_id": None,
    }


def sign_relay_bootstrap_record(
    record: Mapping[str, Any],
    *,
    relay_secret_key_hex: str,
    signing_key_id: str,
) -> dict[str, Any]:
    """Return a relay self-signed bootstrap record.

    The relay AgentID is the BLS public key that verifies the signature. Genesis
    signs capsules containing these records in DEPLOY-00; this function does not
    use or require Genesis signing material.
    """

    unsigned = _require_mapping(record, "relay_bootstrap_record_must_be_object")
    if unsigned.get("signature") is not None:
        raise RelayServerError("relay_bootstrap_record_already_signed")
    payload_ref = relay_bootstrap_record_payload_ref(unsigned)
    if unsigned.get("payload_sha384") != payload_ref:
        raise RelayServerError("relay_bootstrap_payload_ref_mismatch")
    clean_signing_key_id = _require_agent_id(
        signing_key_id,
        "relay_bootstrap_signing_key_invalid",
    )
    if clean_signing_key_id != _require_agent_id(
        unsigned.get("relay_agent_id"),
        "relay_bootstrap_agent_id_invalid",
    ):
        raise RelayServerError("relay_bootstrap_signing_key_mismatch")
    signed = {
        **dict(unsigned),
        "payload_sha384": payload_ref,
        "signature": sign_relay_bootstrap_record_digest(
            secret_key_hex=relay_secret_key_hex,
            digest_hex=payload_ref,
        ),
        "signature_alg": _RELAY_BOOTSTRAP_SIGNATURE_ALG,
        "signing_key_id": clean_signing_key_id,
    }
    if not verify_relay_bootstrap_record(signed):
        raise RelayServerError("relay_bootstrap_signature_self_check_failed")
    return signed


def verify_relay_bootstrap_record(record: Mapping[str, Any]) -> bool:
    """Return True only for a well-formed, self-signed relay bootstrap record."""

    try:
        signed = _require_mapping(record, "relay_bootstrap_record_must_be_object")
        payload_ref = relay_bootstrap_record_payload_ref(signed)
        if signed.get("payload_sha384") != payload_ref:
            return False
        if signed.get("signature_alg") != _RELAY_BOOTSTRAP_SIGNATURE_ALG:
            return False
        relay_agent_id = _require_agent_id(
            signed.get("relay_agent_id"),
            "relay_bootstrap_agent_id_invalid",
        )
        signing_key_id = _require_agent_id(
            signed.get("signing_key_id"),
            "relay_bootstrap_signing_key_invalid",
        )
        if signing_key_id != relay_agent_id:
            return False
        signature = _require_bls_signature_hex(
            signed.get("signature"),
            "relay_bootstrap_signature_invalid",
        )
        return verify_relay_bootstrap_record_digest(
            public_key_hex=signing_key_id,
            digest_hex=payload_ref,
            signature_hex=signature,
        )
    except (RelayClientError, RelayServerError, ValueError):
        return False


def relay_bootstrap_record_payload_ref(record: Mapping[str, Any]) -> str:
    """Return the canonical SHA-384 payload hash for a bootstrap record."""

    payload = _relay_bootstrap_record_payload(record)
    return hashlib.sha384(_canonical_json_bytes(payload)).hexdigest()


def relay_bootstrap_capsule_payload_ref(capsule: Mapping[str, Any]) -> str:
    """Return the canonical SHA-384 payload hash for a Genesis relay capsule."""

    payload = _relay_bootstrap_capsule_payload(capsule)
    return hashlib.sha384(_canonical_json_bytes(payload)).hexdigest()


def parse_relay_bootstrap_capsule(
    capsule: Mapping[str, Any],
    *,
    genesis_agent_id: str,
    expected_network_id: str,
    current_epoch: int,
) -> tuple[dict[str, Any], ...]:
    """Verify a Genesis relay capsule and return verified relay records.

    The capsule signature authenticates the set of relay self-signed records.
    Each returned record has also passed its own relay-AgentID signature check.
    Invalid capsules return an empty tuple rather than partially trusted data.
    """

    clean_expected_network_id = _require_network_id(expected_network_id)
    clean_current_epoch = _require_epoch(
        current_epoch,
        "relay_bootstrap_capsule_current_epoch_invalid",
    )
    try:
        clean_capsule = _require_mapping(
            capsule,
            "relay_bootstrap_capsule_must_be_object",
        )
        clean_genesis_agent_id = _require_agent_id(
            genesis_agent_id,
            "relay_bootstrap_capsule_genesis_agent_id_invalid",
        )
        payload_ref = relay_bootstrap_capsule_payload_ref(clean_capsule)
        capsule_payload = _relay_bootstrap_capsule_payload(clean_capsule)
        if capsule_payload["network_id"] != clean_expected_network_id:
            return ()
        if not (
            capsule_payload["issued_epoch"]
            <= clean_current_epoch
            <= capsule_payload["expires_epoch"]
        ):
            return ()
        if clean_capsule.get("payload_sha384") != payload_ref:
            return ()
        if clean_capsule.get("signature_alg") != _RELAY_BOOTSTRAP_SIGNATURE_ALG:
            return ()
        if clean_capsule.get("signing_key_id") != clean_genesis_agent_id:
            return ()
        signature = _require_bls_signature_hex(
            clean_capsule.get("signature"),
            "relay_bootstrap_capsule_signature_invalid",
        )
        if not verify_relay_bootstrap_capsule_digest(
            public_key_hex=clean_genesis_agent_id,
            digest_hex=payload_ref,
            signature_hex=signature,
        ):
            return ()
        records = _require_relay_records(clean_capsule.get("relay_records"))
        return tuple(
            dict(record)
            for record in records
            if verify_relay_bootstrap_record(record)
            and _relay_record_matches_scope(
                record,
                expected_network_id=clean_expected_network_id,
                current_epoch=clean_current_epoch,
            )
        )
    except (RelayClientError, RelayServerError, ValueError):
        return ()


def _relay_bootstrap_record_payload(record: Mapping[str, Any]) -> dict[str, Any]:
    clean_record = _require_mapping(record, "relay_bootstrap_record_must_be_object")
    _require_exact_keys(
        clean_record,
        allowed_key_sets=(
            _RELAY_BOOTSTRAP_RECORD_PAYLOAD_KEYS,
            _RELAY_BOOTSTRAP_RECORD_KEYS,
        ),
        token="relay_bootstrap_record_keys_invalid",
    )
    schema_version = clean_record.get("schema_version")
    if schema_version != _RELAY_BOOTSTRAP_RECORD_SCHEMA_VERSION:
        raise RelayServerError("relay_bootstrap_schema_version_invalid")
    data_range = _require_mapping(
        clean_record.get("data_port_range"),
        "relay_bootstrap_data_port_range_invalid",
    )
    data_start = _require_port(
        data_range.get("start"),
        "relay_bootstrap_data_port_range_start_invalid",
    )
    data_end = _require_port(
        data_range.get("end"),
        "relay_bootstrap_data_port_range_end_invalid",
    )
    if data_start > data_end:
        raise RelayServerError("relay_bootstrap_data_port_range_invalid")
    control_port = _require_port(
        clean_record.get("control_port"),
        "relay_bootstrap_control_port_invalid",
    )
    issued = _require_epoch(
        clean_record.get("issued_epoch"),
        "relay_bootstrap_record_epoch_invalid",
    )
    expires = _require_epoch(
        clean_record.get("expires_epoch"),
        "relay_bootstrap_record_epoch_invalid",
    )
    if expires <= issued:
        raise RelayServerError("relay_bootstrap_record_epoch_invalid")
    relay_host = _require_host(clean_record.get("relay_host"), "relay_bootstrap_host_invalid")
    tls_cert_der_sha256 = clean_record.get("tls_cert_der_sha256")
    if tls_cert_der_sha256 is not None:
        tls_cert_der_sha256 = _require_sha256_hex(
            tls_cert_der_sha256,
            "relay_bootstrap_tls_cert_der_sha256_invalid",
        )
    tls_mode = _require_tls_mode_for_record(
        relay_host,
        tls_mode=clean_record.get("tls_mode"),
        tls_cert_der_sha256=tls_cert_der_sha256,
    )
    control_url = _require_relay_base_url_for_record(
        clean_record.get("control_url"),
        "relay_bootstrap_control_url_invalid",
        relay_host=relay_host,
        control_port=control_port,
        tls_mode=tls_mode,
    )
    payload = {
        "control_port": control_port,
        "control_url": control_url,
        "data_port_range": {"end": data_end, "start": data_start},
        "expires_epoch": expires,
        "issued_epoch": issued,
        "network_id": _require_network_id(clean_record.get("network_id")),
        "relay_agent_id": _require_agent_id(
            clean_record.get("relay_agent_id"),
            "relay_bootstrap_agent_id_invalid",
        ),
        "relay_host": relay_host,
        "relay_mode": _require_relay_mode(clean_record.get("relay_mode")),
        "schema_version": schema_version,
        "tls_cert_der_sha256": tls_cert_der_sha256,
        "tls_mode": tls_mode,
    }
    return payload


def _relay_bootstrap_capsule_payload(capsule: Mapping[str, Any]) -> dict[str, Any]:
    clean_capsule = _require_mapping(
        capsule,
        "relay_bootstrap_capsule_must_be_object",
    )
    _require_exact_keys(
        clean_capsule,
        allowed_key_sets=(
            _RELAY_BOOTSTRAP_CAPSULE_PAYLOAD_KEYS,
            _RELAY_BOOTSTRAP_CAPSULE_KEYS,
        ),
        token="relay_bootstrap_capsule_keys_invalid",
    )
    if clean_capsule.get("schema_version") != _RELAY_BOOTSTRAP_CAPSULE_SCHEMA_VERSION:
        raise RelayServerError("relay_bootstrap_capsule_schema_version_invalid")
    records = _require_relay_records(clean_capsule.get("relay_records"))
    issued = _require_epoch(
        clean_capsule.get("issued_epoch"),
        "relay_bootstrap_capsule_epoch_invalid",
    )
    expires = _require_epoch(
        clean_capsule.get("expires_epoch"),
        "relay_bootstrap_capsule_epoch_invalid",
    )
    if expires <= issued:
        raise RelayServerError("relay_bootstrap_capsule_epoch_invalid")
    return {
        "expires_epoch": expires,
        "issued_epoch": issued,
        "network_id": _require_network_id(clean_capsule.get("network_id")),
        "relay_records": tuple(dict(record) for record in records),
        "schema_version": _RELAY_BOOTSTRAP_CAPSULE_SCHEMA_VERSION,
    }


def _require_relay_records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        raise RelayServerError("relay_bootstrap_capsule_records_invalid")
    if len(value) < 1 or len(value) > _MAX_RELAY_RECORDS_PER_CAPSULE:
        raise RelayServerError("relay_bootstrap_capsule_records_invalid")
    records: list[Mapping[str, Any]] = []
    for item in value:
        records.append(
            _require_mapping(
                item,
                "relay_bootstrap_capsule_record_invalid",
            )
        )
    return tuple(records)


def _require_relay_mode(value: object) -> str:
    if value != RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC:
        raise RelayServerError("relay_bootstrap_relay_mode_invalid")
    return value


def _require_exact_keys(
    value: Mapping[str, Any],
    *,
    allowed_key_sets: tuple[frozenset[str], ...],
    token: str,
) -> None:
    keys = frozenset(value.keys())
    if keys not in allowed_key_sets:
        raise RelayServerError(token)


def _relay_record_matches_scope(
    record: Mapping[str, Any],
    *,
    expected_network_id: str,
    current_epoch: int,
) -> bool:
    try:
        payload = _relay_bootstrap_record_payload(record)
    except (RelayClientError, RelayServerError, ValueError):
        return False
    if payload["network_id"] != expected_network_id:
        return False
    return payload["issued_epoch"] <= current_epoch <= payload["expires_epoch"]


def _require_tls_mode_for_record(
    relay_host: str,
    *,
    tls_mode: object,
    tls_cert_der_sha256: str | None,
) -> str:
    if tls_mode is None:
        tls_mode = _TLS_MODE_LOOPBACK_ONLY if _host_is_loopback(relay_host) else _TLS_MODE_PINNED_DER_SHA256
    if tls_mode not in {_TLS_MODE_LOOPBACK_ONLY, _TLS_MODE_PINNED_DER_SHA256}:
        raise RelayServerError("relay_bootstrap_tls_mode_invalid")
    if tls_mode == _TLS_MODE_PINNED_DER_SHA256 and tls_cert_der_sha256 is None:
        raise RelayServerError("relay_bootstrap_tls_cert_der_sha256_required")
    if tls_mode == _TLS_MODE_LOOPBACK_ONLY and not _host_is_loopback(relay_host):
        raise RelayServerError("relay_bootstrap_loopback_tls_mode_host_invalid")
    if tls_mode == _TLS_MODE_LOOPBACK_ONLY and tls_cert_der_sha256 is not None:
        raise RelayServerError("relay_bootstrap_loopback_tls_cert_pin_forbidden")
    return tls_mode


def _require_relay_base_url_for_record(
    value: object,
    token: str,
    *,
    relay_host: str,
    control_port: int,
    tls_mode: str,
) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise RelayServerError(token)
    text = value
    if len(text) > _MAX_TEXT_CHARS:
        raise RelayServerError(token)
    if any(char.isspace() for char in text):
        raise RelayServerError(token)
    parsed = urlparse(text)
    if parsed.username is not None or parsed.password is not None:
        raise RelayServerError("relay_bootstrap_control_url_invalid_authority")
    if parsed.query or parsed.fragment:
        raise RelayServerError("relay_bootstrap_control_url_not_root")
    if parsed.path not in {"", "/"}:
        raise RelayServerError("relay_bootstrap_control_url_not_root")
    if parsed.hostname is None:
        raise RelayServerError(token)
    if parsed.hostname.lower() != relay_host.lower():
        raise RelayServerError("relay_bootstrap_control_url_host_mismatch")
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise RelayServerError("relay_bootstrap_control_url_port_mismatch") from exc
    default_port = 443 if parsed.scheme == "https" else 80 if parsed.scheme == "http" else None
    effective_port = parsed_port if parsed_port is not None else default_port
    if effective_port != control_port:
        raise RelayServerError("relay_bootstrap_control_url_port_mismatch")
    if tls_mode == _TLS_MODE_PINNED_DER_SHA256 and parsed.scheme != "https":
        raise RelayServerError("relay_bootstrap_control_url_tls_mode_mismatch")
    if tls_mode == _TLS_MODE_LOOPBACK_ONLY and parsed.scheme not in {"http", "https"}:
        raise RelayServerError("relay_bootstrap_control_url_tls_mode_mismatch")
    return text.rstrip("/")


def _coerce_admission_request(payload: Mapping[str, Any]) -> RelayAdmissionRequest:
    return RelayAdmissionRequest(
        agent_id=payload.get("agent_id"),
        invite_id=payload.get("invite_id"),
        invite_nullifier=payload.get("invite_nullifier"),
        invite_pop=payload.get("invite_pop"),
        invite_pop_epoch=payload.get("invite_pop_epoch"),
        admission_epoch=payload.get("admission_epoch"),
        network_id=payload.get("network_id", _DEFAULT_NETWORK_ID),
        relay_base_url=payload.get("relay_base_url"),
        requested_internal_port=payload.get("requested_internal_port", _DEFAULT_RELAY_PORT),
        requested_protocol=payload.get("requested_protocol", "quic"),
        software_version=payload.get("software_version", ILC_CORE_VERSION),
        relay_admission_payload_ref=payload.get("relay_admission_payload_ref"),
        relay_admission_signature=payload.get("relay_admission_signature"),
    )


def _verify_lifecycle_signature(
    *,
    agent_id: str,
    payload_ref: str,
    signature: object,
) -> None:
    clean_signature = _require_bls_signature_hex(
        signature,
        "relay_lifecycle_signature_invalid",
    )
    try:
        signature_ok = verify_relay_lifecycle_digest(
            public_key_hex=agent_id,
            digest_hex=payload_ref,
            signature_hex=clean_signature,
        )
    except ValueError as exc:
        raise RelayServerError("relay_lifecycle_signature_invalid") from exc
    if not signature_ok:
        raise RelayServerError("relay_lifecycle_signature_verification_failed")


def _admission_ip_key(source_host: str) -> str:
    return _require_admission_tracker_key(f"ip:{source_host}")


def _admission_agent_key(value: object) -> str | None:
    try:
        return _require_agent_id(value, "relay_agent_id_invalid")
    except RelayServerError:
        return None


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    encoded = json.dumps(
        dict(payload),
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(encoded) > _MAX_RESPONSE_BYTES:
        raise RelayServerError("relay_canonical_payload_too_large")
    return encoded


def _require_mapping(value: object, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RelayServerError(token)
    return value


def _require_agent_id(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 96:
        raise RelayServerError(token)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise RelayServerError(token) from exc
    if value.lower() != value:
        raise RelayServerError(token)
    return value


def _require_sha256_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise RelayServerError(token)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise RelayServerError(token) from exc
    if value.lower() != value:
        raise RelayServerError(token)
    return value


def _require_sha384_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 96:
        raise RelayServerError(token)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise RelayServerError(token) from exc
    if value.lower() != value:
        raise RelayServerError(token)
    return value


def _require_bls_signature_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 192:
        raise RelayServerError(token)
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise RelayServerError(token) from exc
    if value.lower() != value:
        raise RelayServerError(token)
    return value


def _require_relay_slot_nonce(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise RelayServerError("relay_slot_nonce_invalid")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise RelayServerError("relay_slot_nonce_invalid") from exc
    if value.lower() != value:
        raise RelayServerError("relay_slot_nonce_invalid")
    return value


def _require_relay_slot_nonce_bytes(value: object) -> bytes:
    return bytes.fromhex(_require_relay_slot_nonce(value))


def _require_token(value: object, token: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise RelayServerError(token)
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-")
    if any(char not in allowed for char in value):
        raise RelayServerError(token)
    return value


def _require_admission_tracker_key(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > _MAX_TEXT_CHARS:
        raise RelayServerError("relay_admission_tracker_key_invalid")
    if any(char.isspace() for char in value):
        raise RelayServerError("relay_admission_tracker_key_invalid")
    if value.startswith("ip:"):
        _require_host(value[3:], "relay_admission_tracker_ip_invalid")
        return value
    return _require_agent_id(value, "relay_admission_tracker_agent_id_invalid")


def _require_host(value: object, token: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise RelayServerError(token)
    if (
        len(value) > _MAX_TEXT_CHARS
        or any(char in value for char in "/?#@")
        or any(char.isspace() for char in value)
    ):
        raise RelayServerError(token)
    return value


def _require_socket_addr(value: object, token: str) -> tuple[str, int]:
    if not isinstance(value, tuple) or len(value) < 2:
        raise RelayServerError(token)
    host = _require_host(value[0], token)
    port = _require_port(value[1], token)
    return host, port


def _require_optional_path(value: object, token: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise RelayServerError(token)
    if (
        len(value) > _MAX_TEXT_CHARS
        or "\x00" in value
        or any(char in value for char in "\r\n")
    ):
        raise RelayServerError(token)
    return value


def _host_is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _require_network_id(value: object) -> str:
    if not isinstance(value, str) or len(value) < 2 or len(value) > 63:
        raise RelayServerError("relay_network_id_invalid")
    first = value[0]
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789._-")
    if first not in set("abcdefghijklmnopqrstuvwxyz0123456789"):
        raise RelayServerError("relay_network_id_invalid")
    if any(char not in allowed for char in value):
        raise RelayServerError("relay_network_id_invalid")
    return value


def _require_port(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelayServerError(f"{token}_must_be_port_int")
    if value < 1 or value > 65535:
        raise RelayServerError(f"{token}_out_of_range")
    return value


def _require_epoch(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelayServerError(token)
    if value < 0 or value > _MAX_EPOCH:
        raise RelayServerError(token)
    return value


def _require_uint_range(value: object, token: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelayServerError(token)
    if value < minimum or value > maximum:
        raise RelayServerError(token)
    return value


def _require_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RelayServerError("relay_timeout_invalid")
    timeout = float(value)
    if not math.isfinite(timeout):
        raise RelayServerError("relay_timeout_invalid")
    if not (0 < timeout <= 10):
        raise RelayServerError("relay_timeout_out_of_range")
    return timeout


def _require_datagram(value: object) -> bytes:
    if not isinstance(value, bytes):
        raise RelayServerError("relay_forward_payload_invalid")
    if len(value) == 0 or len(value) > _MAX_DATAGRAM_BYTES:
        raise RelayServerError("relay_forward_payload_size_invalid")
    return value


def _error_token(exc: BaseException) -> str:
    token = str(exc).strip()
    if _CONTROLLED_TOKEN_RE.fullmatch(token) is None:
        return "relay_internal_error"
    return token


__all__ = [
    "RELAY_ADMISSION_REQUEST_PATH",
    "RELAY_HEALTH_PATH",
    "RELAY_SERVER_NOT_ACTIVATED",
    "RELAY_SERVER_SCHEMA_VERSION",
    "RELAY_SERVER_TOKEN",
    "RELAY_ABUSE_LIMITS_SCHEMA_VERSION",
    "RELAY_SLOT_KEEPALIVE_PATH",
    "RELAY_SLOT_RELEASE_PATH",
    "RelayForwardReceipt",
    "RelayDataPlaneRuntime",
    "RelayRendezvousServer",
    "RelayRevocationReceipt",
    "RelayServerConfig",
    "RelayServerError",
    "RelaySlotState",
    "RelayUdpForwarder",
    "RelayUdpPortForwarder",
    "build_relay_bootstrap_record",
    "make_relay_http_handler",
    "parse_relay_bootstrap_capsule",
    "relay_bootstrap_capsule_payload_ref",
    "relay_bootstrap_record_payload_ref",
    "run_relay_http_server",
    "sign_relay_bootstrap_record",
    "verify_relay_bootstrap_record",
]
