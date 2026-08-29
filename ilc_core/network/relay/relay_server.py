# SPDX-License-Identifier: AGPL-3.0-only
"""Guarded relay/rendezvous server implementation.

The server side mirrors :mod:`ilc_core.network.relay.relay_client`: Option A
admission verifies invite proof-of-possession and a second relay-admission BLS
signature before issuing a bounded slot grant. The forwarding primitive is
pass-through only: it accounts opaque QUIC/UDP bytes by slot and never
terminates, decrypts, re-signs, rewrites, or re-originates consensus messages.

This module is source-only until GAP-RELAY-RENDEZVOUS-DEPLOY-00 clears
``RELAY_SERVER_NOT_ACTIVATED`` and starts it on live validator hosts.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import secrets
import time
from typing import Any, Callable

from ilc_core import __version__ as ILC_CORE_VERSION
from ilc_core.identity.bls_backend import verify_invite_pop_digest
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
_MAX_REQUEST_BYTES = 32_768
_MAX_RESPONSE_BYTES = 65_536
_MAX_DATAGRAM_BYTES = 65_535
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
    """Configuration for one relay-serving ILC node."""

    relay_agent_id: str
    relay_host: str
    relay_port: int = _DEFAULT_RELAY_PORT
    network_id: str = _DEFAULT_NETWORK_ID
    ttl_epochs: int = _MAX_TTL_EPOCHS
    max_bytes_per_epoch: int = _MAX_BYTES_PER_EPOCH
    max_concurrent_streams: int = _MAX_CONCURRENT_STREAMS

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

    @property
    def relay_base_url(self) -> str:
        host = self.relay_host
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        return f"https://{host}:{self.relay_port}"


@dataclass(frozen=True)
class RelaySlotState:
    """In-memory state for a granted relay slot."""

    grant: RelaySlotGrant
    target_host: str
    bytes_forwarded_this_epoch: int = 0
    current_epoch: int | None = None
    status: str = "active"
    revocation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
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
        self._insertion_order: list[str] = []
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
            self._insertion_order.append(clean_key)
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
            self._entries.pop(clean_key, None)
            self._insertion_order = [
                existing for existing in self._insertion_order if existing != clean_key
            ]
            return False
        return True

    def failure_count(self, key: str) -> int:
        entry = self._entries.get(_require_admission_tracker_key(key))
        return 0 if entry is None else entry.attempt_count

    def _evict_if_needed(self) -> None:
        while len(self._entries) >= self._max_entries:
            oldest = self._insertion_order.pop(0)
            self._entries.pop(oldest, None)

    def _cooldown_elapsed(self, entry: _FailedAdmissionEntry, now: float) -> bool:
        return now - entry.last_attempt >= _FAILED_ADMISSION_COOLDOWN_SECONDS

    def _now(self) -> float:
        now = self._now_provider()
        if not math.isfinite(now):
            raise RelayServerError("relay_failed_admission_clock_invalid")
        return now


class RelayRendezvousServer:
    """Option A relay admission and lifecycle state machine."""

    def __init__(self, config: RelayServerConfig) -> None:
        self.config = config
        self._slots_by_id: dict[str, RelaySlotState] = {}
        self._active_slot_by_agent: dict[str, str] = {}
        self._packet_rate_buckets: dict[str, _PacketRateBucket] = {}
        self._failed_admissions = _FailedAdmissionTracker()
        self._revocation_receipts_by_slot: dict[str, RelayRevocationReceipt] = {}

    @property
    def active_slot_count(self) -> int:
        return sum(1 for slot in self._slots_by_id.values() if slot.status == "active")

    def health(self) -> dict[str, Any]:
        return {
            "active_slot_count": self.active_slot_count,
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
        source_host = _require_host(source_host, "relay_source_host_invalid")
        ip_key = _admission_ip_key(source_host)
        agent_key = _admission_agent_key(payload.get("agent_id"))
        self._require_admission_not_blocked(ip_key, agent_key)
        if self.active_slot_count >= _MAX_ACTIVE_SLOTS:
            raise RelayServerError("relay_server_active_slot_limit_exceeded")
        try:
            request = _coerce_admission_request(payload)
        except (RelayClientError, RelayServerError, ValueError) as exc:
            token = _error_token(exc)
            if token in _ADMISSION_FAILURE_TOKENS:
                self._failed_admissions.record_failure(ip_key)
                if agent_key is not None:
                    self._failed_admissions.record_failure(agent_key)
            raise
        if request.network_id != self.config.network_id:
            raise RelayServerError("relay_admission_network_id_mismatch")
        if request.relay_base_url != self.config.relay_base_url:
            raise RelayServerError("relay_admission_base_url_mismatch")
        if request.agent_id in self._active_slot_by_agent:
            raise RelayServerError("relay_slot_already_active")
        slot_id = f"slot-{secrets.token_hex(16)}"
        grant = RelaySlotGrant(
            slot_id=slot_id,
            agent_id=request.agent_id,
            relay_endpoint=RelayEndpoint(
                host=self.config.relay_host,
                port=self.config.relay_port,
            ),
            granted_epoch=request.admission_epoch,
            ttl_epochs=self.config.ttl_epochs,
            target_internal_port=request.requested_internal_port,
            max_bytes_per_epoch=self.config.max_bytes_per_epoch,
            max_concurrent_streams=self.config.max_concurrent_streams,
            admission_request_hash=request.canonical_request_hash,
        )
        self._slots_by_id[slot_id] = RelaySlotState(
            grant=grant,
            target_host=source_host,
            current_epoch=request.admission_epoch,
        )
        self._active_slot_by_agent[request.agent_id] = slot_id
        self._packet_rate_buckets[slot_id] = _PacketRateBucket(
            window_start=time.monotonic(),
        )
        return {"grant": grant.to_dict(), "schema_version": RELAY_SERVER_SCHEMA_VERSION}

    def keepalive(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        slot = self._require_active_slot(payload.get("slot_id"))
        agent_id = _require_agent_id(payload.get("agent_id"), "relay_keepalive_agent_id_invalid")
        if agent_id != slot.grant.agent_id:
            raise RelayServerError("relay_keepalive_agent_id_mismatch")
        epoch = _require_epoch(payload.get("keepalive_epoch"), "relay_keepalive_epoch_invalid")
        self._require_lifecycle_epoch(slot, epoch)
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
        _verify_lifecycle_signature(
            agent_id=agent_id,
            payload_ref=payload_ref,
            signature=payload.get("relay_lifecycle_signature"),
        )
        if slot.status != "active":
            raise RelayServerError(f"relay_slot_{slot.status}")
        self._slots_by_id[slot.grant.slot_id] = RelaySlotState(
            grant=slot.grant,
            target_host=slot.target_host,
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
        slot = self._require_active_slot(payload.get("slot_id"))
        agent_id = _require_agent_id(payload.get("agent_id"), "relay_release_agent_id_invalid")
        if agent_id != slot.grant.agent_id:
            raise RelayServerError("relay_release_agent_id_mismatch")
        epoch = _require_epoch(payload.get("release_epoch"), "relay_release_epoch_invalid")
        self._require_lifecycle_epoch(slot, epoch)
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
        _verify_lifecycle_signature(
            agent_id=agent_id,
            payload_ref=payload_ref,
            signature=payload.get("relay_lifecycle_signature"),
        )
        self._release_slot(slot.grant.slot_id)
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
            revocation = self._revoke_slot(slot.grant.slot_id, "relay_slot_revoked_budget_exceeded")
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

    def _require_lifecycle_epoch(self, slot: RelaySlotState, epoch: int) -> None:
        if epoch < slot.grant.granted_epoch:
            raise RelayServerError("relay_lifecycle_epoch_before_grant")
        if epoch > slot.grant.granted_epoch + slot.grant.ttl_epochs:
            self._expire_slot(slot.grant.slot_id)
            raise RelayServerError("relay_lifecycle_epoch_after_expiry")

    def _require_known_slot(self, slot_id: object) -> RelaySlotState:
        clean_slot_id = _require_token(slot_id, "relay_slot_id_invalid")
        slot = self._slots_by_id.get(clean_slot_id)
        if slot is None:
            raise RelayServerError("relay_slot_not_found")
        return slot

    def _require_active_slot(self, slot_id: object) -> RelaySlotState:
        slot = self._require_known_slot(slot_id)
        if slot.status == "active":
            return slot
        if slot.status == "revoked" and slot.revocation_reason:
            raise RelayServerError(slot.revocation_reason)
        raise RelayServerError(f"relay_slot_{slot.status}")

    def _release_slot(self, slot_id: str) -> None:
        slot = self._slots_by_id[slot_id]
        self._slots_by_id[slot_id] = RelaySlotState(
            grant=slot.grant,
            target_host=slot.target_host,
            bytes_forwarded_this_epoch=slot.bytes_forwarded_this_epoch,
            current_epoch=slot.current_epoch,
            status="released",
        )
        self._active_slot_by_agent.pop(slot.grant.agent_id, None)
        self._packet_rate_buckets.pop(slot_id, None)

    def _expire_slot(self, slot_id: str) -> None:
        slot = self._slots_by_id[slot_id]
        self._slots_by_id[slot_id] = RelaySlotState(
            grant=slot.grant,
            target_host=slot.target_host,
            bytes_forwarded_this_epoch=slot.bytes_forwarded_this_epoch,
            current_epoch=slot.current_epoch,
            status="expired",
        )
        self._active_slot_by_agent.pop(slot.grant.agent_id, None)
        self._packet_rate_buckets.pop(slot_id, None)

    def _revoke_slot(self, slot_id: str, reason_token: str) -> RelayRevocationReceipt:
        slot = self._slots_by_id[slot_id]
        epoch = slot.current_epoch
        if epoch is None:
            epoch = slot.grant.granted_epoch
        receipt = RelayRevocationReceipt.build(
            slot_id=slot.grant.slot_id,
            agent_id=slot.grant.agent_id,
            epoch=epoch,
            reason_token=reason_token,
            bytes_forwarded=slot.bytes_forwarded_this_epoch,
        )
        self._slots_by_id[slot_id] = RelaySlotState(
            grant=slot.grant,
            target_host=slot.target_host,
            bytes_forwarded_this_epoch=slot.bytes_forwarded_this_epoch,
            current_epoch=slot.current_epoch,
            status="revoked",
            revocation_reason=reason_token,
        )
        self._active_slot_by_agent.pop(slot.grant.agent_id, None)
        self._packet_rate_buckets.pop(slot_id, None)
        self._revocation_receipts_by_slot[slot_id] = receipt
        return receipt


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
) -> type[BaseHTTPRequestHandler]:
    """Return a bounded stdlib HTTP handler for relay admission/lifecycle."""

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
    bind_port: int,
    timeout_seconds: float = 3.0,
    allow_guarded_start: bool = False,
) -> None:
    """Start the relay HTTP server after deployment clears the guard."""

    if RELAY_SERVER_NOT_ACTIVATED and not allow_guarded_start:
        raise RelayServerError("relay_server_not_activated")
    bind_host = _require_host(bind_host, "relay_bind_host_invalid")
    bind_port = _require_port(bind_port, "relay_bind_port_invalid")
    timeout = _require_timeout(timeout_seconds)
    relay_server = RelayRendezvousServer(config)

    class _TimedThreadingHTTPServer(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    server = _TimedThreadingHTTPServer(
        (bind_host, bind_port),
        make_relay_http_handler(relay_server),
    )
    server.socket.settimeout(timeout)
    try:
        server.serve_forever()
    finally:
        server.server_close()


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
        signature_ok = verify_invite_pop_digest(
            public_key_hex=agent_id,
            digest_hex=payload_ref,
            signature_hex=clean_signature,
        )
    except ValueError as exc:
        raise RelayServerError("relay_lifecycle_signature_invalid") from exc
    if not signature_ok:
        raise RelayServerError("relay_lifecycle_signature_invalid")


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
    token = str(exc)
    if not token or any(char.isspace() for char in token) or len(token) > 128:
        return "relay_server_error"
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
    "RelayRendezvousServer",
    "RelayRevocationReceipt",
    "RelayServerConfig",
    "RelayServerError",
    "RelaySlotState",
    "RelayUdpDatagramProtocol",
    "RelayUdpForwarder",
    "make_relay_http_handler",
    "run_relay_http_server",
]
