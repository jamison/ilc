# SPDX-License-Identifier: AGPL-3.0-only
"""Guarded relay/rendezvous client and Option A admission handshake.

This module implements the client-side relay slot protocol only. It does not
deploy a relay server, clear activation guards, grant validator authority, or
activate CDL-078 rewards. Relay admission presents an existing AgentID,
Genesis-traced invite metadata, and the invite proof-of-possession from the
onboarding path; future relay servers must verify the same material again.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
import hashlib
import ipaddress
import json
import math
import re
import ssl
from typing import Any, Protocol
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

from ilc_core import __version__ as ILC_CORE_VERSION
from ilc_core.identity.bls_backend import verify_invite_pop_digest
from ilc_core.identity.first_run_provisioning import (
    POP_DOMAIN,
    invite_pop_payload_ref,
    verify_invite_pop,
)


RELAY_CLIENT_NOT_ACTIVATED = True
RELAY_CLIENT_SCHEMA_VERSION = "relay_client_GAP_RELAY_RENDEZVOUS_IMPL_00.v0.1"
RELAY_CLIENT_TOKEN = "relay_client_committed_GAP_RELAY_RENDEZVOUS_IMPL_00"
RELAY_ADMISSION_DOMAIN = "ilc-relay-rendezvous-admission-v1"
RELAY_LIFECYCLE_DOMAIN = "ilc-relay-rendezvous-lifecycle-v1"
RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC = "pass_through_consensus_quic"

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA384_RE = re.compile(r"^[0-9a-f]{96}$")
_BLS_SIGNATURE_RE = re.compile(r"^[0-9a-f]{192}$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_NETWORK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,62}$")

_DEFAULT_TIMEOUT_SECONDS = 3.0
_DEFAULT_INTERNAL_PORT = 50151
_MAX_EPOCH = (1 << 64) - 1
_MAX_TEXT_CHARS = 512
_MAX_REQUEST_BYTES = 32_768
_MAX_RESPONSE_BYTES = 65_536
_MAX_TTL_EPOCHS = 4
_MAX_BYTES_PER_EPOCH = 64 * 1024 * 1024
_MAX_CONCURRENT_STREAMS = 8


class RelayClientError(ValueError):
    """Raised when relay client input, transport, or server response is invalid."""


class RelayClientTransport(Protocol):
    """Minimal JSON POST transport used by RelayClient."""

    def post_json(
        self,
        path: str,
        payload: Mapping[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        """POST canonical JSON and return a decoded JSON object."""


def relay_admission_payload_ref(
    *,
    agent_id: str,
    invite_id: str,
    invite_nullifier: str,
    invite_pop_payload_ref_value: str,
    admission_epoch: int,
    network_id: str,
    relay_base_url: str,
    requested_internal_port: int,
    requested_protocol: str,
    software_version: str,
) -> str:
    """Return the SHA-384 relay admission transcript digest signed by the agent."""

    _require_agent_id(agent_id, "relay_agent_id_invalid")
    _require_non_empty_string(invite_id, "relay_invite_id_invalid")
    _require_sha256_hex(invite_nullifier, "relay_invite_nullifier_invalid")
    _require_sha384_hex(
        invite_pop_payload_ref_value,
        "relay_invite_pop_payload_ref_invalid",
    )
    _require_epoch(admission_epoch, "relay_admission_epoch_invalid")
    _require_network_id(network_id)
    relay_base_url = _require_relay_base_url(relay_base_url)
    _require_port(requested_internal_port, "relay_requested_internal_port")
    _require_token(software_version, "relay_software_version_invalid")
    if requested_protocol != "quic":
        raise RelayClientError("relay_requested_protocol_must_be_quic")
    return hashlib.sha384(
        _canonical_json_bytes(
            {
                "admission_epoch": admission_epoch,
                "agent_id": agent_id,
                "domain": RELAY_ADMISSION_DOMAIN,
                "invite_id": invite_id,
                "invite_nullifier": invite_nullifier,
                "invite_pop_payload_ref": invite_pop_payload_ref_value,
                "network_id": network_id,
                "relay_base_url": relay_base_url,
                "requested_internal_port": requested_internal_port,
                "requested_protocol": requested_protocol,
                "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
                "software_version": software_version,
            }
        )
    ).hexdigest()


def relay_lifecycle_payload_ref(
    *,
    action: str,
    agent_id: str,
    slot_id: str,
    lifecycle_epoch: int,
    previous_grant_hash: str,
    network_id: str,
    relay_base_url: str,
) -> str:
    """Return the SHA-384 digest signed for relay keepalive/release messages."""

    if action not in {"keepalive", "release"}:
        raise RelayClientError("relay_lifecycle_action_invalid")
    _require_agent_id(agent_id, "relay_lifecycle_agent_id_invalid")
    _require_token(slot_id, "relay_slot_id_invalid")
    _require_epoch(lifecycle_epoch, f"relay_{action}_epoch_invalid")
    _require_sha256_hex(previous_grant_hash, "relay_previous_grant_hash_invalid")
    _require_network_id(network_id)
    relay_base_url = _require_relay_base_url(relay_base_url)
    return hashlib.sha384(
        _canonical_json_bytes(
            {
                "action": action,
                "agent_id": agent_id,
                "domain": RELAY_LIFECYCLE_DOMAIN,
                "lifecycle_epoch": lifecycle_epoch,
                "network_id": network_id,
                "previous_grant_hash": previous_grant_hash,
                "relay_base_url": relay_base_url,
                "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
                "slot_id": slot_id,
            }
        )
    ).hexdigest()


@dataclass(frozen=True)
class RelayEndpoint:
    """Endpoint assigned by a relay slot grant."""

    host: str
    port: int
    transport: str = "quic"
    relay_mode: str = RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC

    def __post_init__(self) -> None:
        _require_host(self.host, "relay_endpoint_host")
        _require_port(self.port, "relay_endpoint_port")
        _require_token(self.transport, "relay_endpoint_transport")
        if self.transport != "quic":
            raise RelayClientError("relay_endpoint_transport_must_be_quic")
        if self.relay_mode != RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC:
            raise RelayClientError("relay_endpoint_mode_invalid")

    def as_host_port(self) -> str:
        try:
            parsed = ipaddress.ip_address(self.host)
        except ValueError:
            return f"{self.host}:{self.port}"
        if isinstance(parsed, ipaddress.IPv6Address):
            return f"[{self.host}]:{self.port}"
        return f"{self.host}:{self.port}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RelayAdmissionRequest:
    """Canonical request payload for Option A relay admission."""

    agent_id: str
    invite_id: str
    invite_nullifier: str
    invite_pop: str
    invite_pop_epoch: int
    admission_epoch: int
    network_id: str = "public-rc"
    relay_base_url: str | None = None
    requested_internal_port: int = _DEFAULT_INTERNAL_PORT
    requested_protocol: str = "quic"
    software_version: str = ILC_CORE_VERSION
    relay_admission_payload_ref: str | None = None
    relay_admission_signature: str | None = None

    def __post_init__(self) -> None:
        _require_agent_id(self.agent_id, "relay_agent_id_invalid")
        _require_non_empty_string(self.invite_id, "relay_invite_id_invalid")
        _require_sha256_hex(self.invite_nullifier, "relay_invite_nullifier_invalid")
        _require_bls_signature_hex(self.invite_pop, "relay_invite_pop_invalid")
        _require_epoch(self.invite_pop_epoch, "relay_invite_pop_epoch_invalid")
        _require_epoch(self.admission_epoch, "relay_admission_epoch_invalid")
        _require_network_id(self.network_id)
        if self.relay_base_url is None:
            raise RelayClientError("relay_base_url_required")
        object.__setattr__(
            self,
            "relay_base_url",
            _require_relay_base_url(self.relay_base_url),
        )
        _require_port(self.requested_internal_port, "relay_requested_internal_port")
        _require_token(self.software_version, "relay_software_version_invalid")
        if self.requested_protocol != "quic":
            raise RelayClientError("relay_requested_protocol_must_be_quic")
        expected_admission_ref = self.expected_relay_admission_payload_ref
        if self.relay_admission_payload_ref is None:
            raise RelayClientError("relay_admission_payload_ref_required")
        _require_sha384_hex(
            self.relay_admission_payload_ref,
            "relay_admission_payload_ref_invalid",
        )
        if self.relay_admission_payload_ref != expected_admission_ref:
            raise RelayClientError("relay_admission_payload_ref_mismatch")
        if self.relay_admission_signature is None:
            raise RelayClientError("relay_admission_signature_required")
        _require_bls_signature_hex(
            self.relay_admission_signature,
            "relay_admission_signature_invalid",
        )
        if not verify_invite_pop(
            agent_id_hex=self.agent_id,
            invite_nullifier=self.invite_nullifier,
            invite_id=self.invite_id,
            epoch=self.invite_pop_epoch,
            invite_pop=self.invite_pop,
        ):
            raise RelayClientError("relay_invite_pop_verification_failed")
        try:
            signature_ok = verify_invite_pop_digest(
                public_key_hex=self.agent_id,
                digest_hex=self.relay_admission_payload_ref,
                signature_hex=self.relay_admission_signature,
            )
        except ValueError as exc:
            raise RelayClientError("relay_admission_signature_invalid") from exc
        if not signature_ok:
            raise RelayClientError("relay_admission_signature_verification_failed")

    @property
    def invite_pop_payload_ref(self) -> str:
        return invite_pop_payload_ref(
            agent_id_hex=self.agent_id,
            invite_nullifier=self.invite_nullifier,
            invite_id=self.invite_id,
            epoch=self.invite_pop_epoch,
        )

    @property
    def expected_relay_admission_payload_ref(self) -> str:
        return relay_admission_payload_ref(
            agent_id=self.agent_id,
            invite_id=self.invite_id,
            invite_nullifier=self.invite_nullifier,
            invite_pop_payload_ref_value=self.invite_pop_payload_ref,
            admission_epoch=self.admission_epoch,
            network_id=self.network_id,
            relay_base_url=self.relay_base_url,
            requested_internal_port=self.requested_internal_port,
            requested_protocol=self.requested_protocol,
            software_version=self.software_version,
        )

    @property
    def canonical_request_hash(self) -> str:
        return hashlib.sha256(_canonical_json_bytes(self._core_payload())).hexdigest()

    def _core_payload(self) -> dict[str, Any]:
        return {
            "admission_epoch": self.admission_epoch,
            "agent_id": self.agent_id,
            "domain": RELAY_ADMISSION_DOMAIN,
            "invite_id": self.invite_id,
            "invite_nullifier": self.invite_nullifier,
            "invite_pop": self.invite_pop,
            "invite_pop_domain": POP_DOMAIN,
            "invite_pop_epoch": self.invite_pop_epoch,
            "invite_pop_payload_ref": self.invite_pop_payload_ref,
            "network_id": self.network_id,
            "relay_base_url": self.relay_base_url,
            "requested_internal_port": self.requested_internal_port,
            "requested_protocol": self.requested_protocol,
            "relay_admission_payload_ref": self.relay_admission_payload_ref,
            "relay_admission_signature": self.relay_admission_signature,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "software_version": self.software_version,
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._core_payload()
        payload["canonical_request_hash"] = self.canonical_request_hash
        return payload

    def to_canonical_json(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


@dataclass(frozen=True)
class RelaySlotGrant:
    """Bound relay slot grant returned by a relay server."""

    slot_id: str
    agent_id: str
    relay_endpoint: RelayEndpoint
    granted_epoch: int
    ttl_epochs: int
    target_internal_port: int
    max_bytes_per_epoch: int
    max_concurrent_streams: int
    admission_request_hash: str
    relay_slot_nonce: str
    relay_mode: str = RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC
    revocation_ref: str | None = None
    canonical_response_hash: str | None = None

    def __post_init__(self) -> None:
        _require_token(self.slot_id, "relay_slot_id_invalid")
        _require_agent_id(self.agent_id, "relay_grant_agent_id_invalid")
        endpoint = _coerce_endpoint(self.relay_endpoint)
        object.__setattr__(self, "relay_endpoint", endpoint)
        _require_epoch(self.granted_epoch, "relay_granted_epoch_invalid")
        _require_ttl_epochs(self.ttl_epochs)
        _require_port(self.target_internal_port, "relay_target_internal_port")
        _require_uint_range(
            self.max_bytes_per_epoch,
            "relay_max_bytes_per_epoch_invalid",
            1,
            _MAX_BYTES_PER_EPOCH,
        )
        _require_uint_range(
            self.max_concurrent_streams,
            "relay_max_concurrent_streams_invalid",
            1,
            _MAX_CONCURRENT_STREAMS,
        )
        _require_sha256_hex(self.admission_request_hash, "relay_admission_request_hash_invalid")
        _require_relay_slot_nonce(self.relay_slot_nonce)
        if self.relay_mode != RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC:
            raise RelayClientError("relay_grant_mode_invalid")
        if self.revocation_ref is not None:
            _require_token(self.revocation_ref, "relay_revocation_ref_invalid")
        expected_hash = self._response_hash()
        if self.canonical_response_hash is None:
            object.__setattr__(self, "canonical_response_hash", expected_hash)
        elif self.canonical_response_hash != expected_hash:
            raise RelayClientError("relay_response_hash_mismatch")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RelaySlotGrant":
        _require_mapping(payload, "relay_grant_response_must_be_object")
        return cls(
            slot_id=payload.get("slot_id"),
            agent_id=payload.get("agent_id"),
            relay_endpoint=_coerce_endpoint(payload.get("relay_endpoint")),
            granted_epoch=payload.get("granted_epoch"),
            ttl_epochs=payload.get("ttl_epochs"),
            target_internal_port=payload.get("target_internal_port"),
            max_bytes_per_epoch=payload.get("max_bytes_per_epoch"),
            max_concurrent_streams=payload.get("max_concurrent_streams"),
            admission_request_hash=payload.get("admission_request_hash"),
            relay_slot_nonce=payload.get("relay_slot_nonce"),
            relay_mode=payload.get("relay_mode", RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC),
            revocation_ref=payload.get("revocation_ref"),
            canonical_response_hash=payload.get("canonical_response_hash"),
        )

    def _core_payload(self) -> dict[str, Any]:
        return {
            "admission_request_hash": self.admission_request_hash,
            "agent_id": self.agent_id,
            "granted_epoch": self.granted_epoch,
            "max_bytes_per_epoch": self.max_bytes_per_epoch,
            "max_concurrent_streams": self.max_concurrent_streams,
            "relay_endpoint": self.relay_endpoint.to_dict(),
            "relay_mode": self.relay_mode,
            "relay_slot_nonce": self.relay_slot_nonce,
            "revocation_ref": self.revocation_ref,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "slot_id": self.slot_id,
            "target_internal_port": self.target_internal_port,
            "ttl_epochs": self.ttl_epochs,
        }

    def _response_hash(self) -> str:
        return hashlib.sha256(_canonical_json_bytes(self._core_payload())).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        payload = self._core_payload()
        payload["canonical_response_hash"] = self.canonical_response_hash
        return payload

    def to_canonical_json(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


def relay_slot_claim_datagram(grant: RelaySlotGrant) -> bytes:
    """Return the explicit first UDP datagram that claims a relay slot."""

    if not isinstance(grant, RelaySlotGrant):
        raise RelayClientError("relay_slot_grant_required")
    return bytes.fromhex(_require_relay_slot_nonce(grant.relay_slot_nonce))


@dataclass(frozen=True)
class RelayKeepaliveReceipt:
    """Client-side receipt for a relay keepalive response."""

    slot_id: str
    agent_id: str
    keepalive_epoch: int
    previous_grant_hash: str
    relay_lifecycle_payload_ref: str
    relay_lifecycle_signature: str
    renewal_result: str

    def __post_init__(self) -> None:
        _require_token(self.slot_id, "relay_slot_id_invalid")
        _require_agent_id(self.agent_id, "relay_keepalive_agent_id_invalid")
        _require_epoch(self.keepalive_epoch, "relay_keepalive_epoch_invalid")
        _require_sha256_hex(self.previous_grant_hash, "relay_previous_grant_hash_invalid")
        _require_sha384_hex(
            self.relay_lifecycle_payload_ref,
            "relay_lifecycle_payload_ref_invalid",
        )
        _require_bls_signature_hex(
            self.relay_lifecycle_signature,
            "relay_lifecycle_signature_invalid",
        )
        _require_token(self.renewal_result, "relay_keepalive_result_invalid")

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "keepalive_epoch": self.keepalive_epoch,
            "previous_grant_hash": self.previous_grant_hash,
            "relay_lifecycle_payload_ref": self.relay_lifecycle_payload_ref,
            "relay_lifecycle_signature": self.relay_lifecycle_signature,
            "renewal_result": self.renewal_result,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "slot_id": self.slot_id,
        }

    def to_canonical_json(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


@dataclass(frozen=True)
class RelayReleaseReceipt:
    """Client-side receipt for a relay slot release response."""

    slot_id: str
    agent_id: str
    release_epoch: int
    previous_grant_hash: str
    relay_lifecycle_payload_ref: str
    relay_lifecycle_signature: str
    release_result: str

    def __post_init__(self) -> None:
        _require_token(self.slot_id, "relay_slot_id_invalid")
        _require_agent_id(self.agent_id, "relay_release_agent_id_invalid")
        _require_epoch(self.release_epoch, "relay_release_epoch_invalid")
        _require_sha256_hex(self.previous_grant_hash, "relay_previous_grant_hash_invalid")
        _require_sha384_hex(
            self.relay_lifecycle_payload_ref,
            "relay_lifecycle_payload_ref_invalid",
        )
        _require_bls_signature_hex(
            self.relay_lifecycle_signature,
            "relay_lifecycle_signature_invalid",
        )
        _require_token(self.release_result, "relay_release_result_invalid")

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "previous_grant_hash": self.previous_grant_hash,
            "release_epoch": self.release_epoch,
            "relay_lifecycle_payload_ref": self.relay_lifecycle_payload_ref,
            "relay_lifecycle_signature": self.relay_lifecycle_signature,
            "release_result": self.release_result,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "slot_id": self.slot_id,
        }

    def to_canonical_json(self) -> bytes:
        return _canonical_json_bytes(self.to_dict())


class HttpsRelayClientTransport:
    """Bounded HTTPS JSON transport for relay admission and slot lifecycle."""

    def __init__(self, relay_base_url: str, tls_cert_der_sha256: str | None = None) -> None:
        self._base_url = _require_relay_base_url(relay_base_url)
        self._tls_cert_der_sha256 = _require_optional_sha256_hex(
            tls_cert_der_sha256,
            "relay_tls_cert_der_sha256_invalid",
        )

    def post_json(
        self,
        path: str,
        payload: Mapping[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        _require_timeout(timeout_seconds)
        if not isinstance(path, str) or not path.startswith("/"):
            raise RelayClientError("relay_request_path_invalid")
        try:
            encoded = json.dumps(
                dict(payload),
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise RelayClientError("relay_request_payload_invalid") from exc
        if len(encoded) > _MAX_REQUEST_BYTES:
            raise RelayClientError("relay_request_too_large")
        request = Request(
            f"{self._base_url}{path}",
            data=encoded,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"ilc-core/{ILC_CORE_VERSION} relay-client",
            },
            method="POST",
        )
        try:
            response = _urlopen_no_redirect(
                request,
                timeout_seconds,
                tls_cert_der_sha256=self._tls_cert_der_sha256,
            )
            try:
                if getattr(response, "status", 200) >= 400:
                    raise RelayClientError("relay_transport_http_status_failed")
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
            finally:
                response.close()
        except URLError as exc:
            raise RelayClientError("relay_transport_failed") from exc
        if len(raw) > _MAX_RESPONSE_BYTES:
            raise RelayClientError("relay_response_too_large")
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RelayClientError("relay_response_json_invalid") from exc
        if not isinstance(decoded, dict):
            raise RelayClientError("relay_response_must_be_object")
        return decoded


class RelayClient:
    """Client-side relay slot admission, keepalive, and release."""

    def __init__(
        self,
        *,
        relay_base_url: str,
        agent_id: str,
        invite_id: str,
        invite_nullifier: str,
        invite_pop: str,
        invite_pop_epoch: int = 0,
        network_id: str = "public-rc",
        requested_internal_port: int = _DEFAULT_INTERNAL_PORT,
        software_version: str = ILC_CORE_VERSION,
        relay_admission_signature: str | None = None,
        tls_cert_der_sha256: str | None = None,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
        transport: RelayClientTransport | None = None,
        allow_guarded_request: bool = False,
    ) -> None:
        self.relay_base_url = _require_relay_base_url(relay_base_url)
        self.agent_id = _require_agent_id(agent_id, "relay_agent_id_invalid")
        self.invite_id = _require_non_empty_string(invite_id, "relay_invite_id_invalid")
        self.invite_nullifier = _require_sha256_hex(
            invite_nullifier,
            "relay_invite_nullifier_invalid",
        )
        self.invite_pop = _require_bls_signature_hex(invite_pop, "relay_invite_pop_invalid")
        _require_epoch(invite_pop_epoch, "relay_invite_pop_epoch_invalid")
        self.invite_pop_epoch = invite_pop_epoch
        _require_network_id(network_id)
        self.network_id = network_id
        _require_port(requested_internal_port, "relay_requested_internal_port")
        self.requested_internal_port = requested_internal_port
        self.software_version = _require_token(
            software_version,
            "relay_software_version_invalid",
        )
        if relay_admission_signature is not None:
            _require_bls_signature_hex(
                relay_admission_signature,
                "relay_admission_signature_invalid",
            )
        self.relay_admission_signature = relay_admission_signature
        self.tls_cert_der_sha256 = _require_optional_sha256_hex(
            tls_cert_der_sha256,
            "relay_tls_cert_der_sha256_invalid",
        )
        self.timeout_seconds = _require_timeout(timeout_seconds)
        self._transport = transport or HttpsRelayClientTransport(
            self.relay_base_url,
            tls_cert_der_sha256=self.tls_cert_der_sha256,
        )
        self._allow_guarded_request = _require_bool(
            allow_guarded_request,
            "relay_allow_guarded_request_must_be_bool",
        )

    def request_slot(
        self,
        *,
        admission_epoch: int,
        relay_admission_signature: str | None = None,
    ) -> RelaySlotGrant:
        """Request a bounded relay slot for the current protocol epoch."""

        self._require_active()
        invite_ref = invite_pop_payload_ref(
            agent_id_hex=self.agent_id,
            invite_nullifier=self.invite_nullifier,
            invite_id=self.invite_id,
            epoch=self.invite_pop_epoch,
        )
        admission_ref = relay_admission_payload_ref(
            agent_id=self.agent_id,
            invite_id=self.invite_id,
            invite_nullifier=self.invite_nullifier,
            invite_pop_payload_ref_value=invite_ref,
            admission_epoch=admission_epoch,
            network_id=self.network_id,
            relay_base_url=self.relay_base_url,
            requested_internal_port=self.requested_internal_port,
            requested_protocol="quic",
            software_version=self.software_version,
        )
        request = RelayAdmissionRequest(
            agent_id=self.agent_id,
            invite_id=self.invite_id,
            invite_nullifier=self.invite_nullifier,
            invite_pop=self.invite_pop,
            invite_pop_epoch=self.invite_pop_epoch,
            admission_epoch=admission_epoch,
            network_id=self.network_id,
            relay_base_url=self.relay_base_url,
            requested_internal_port=self.requested_internal_port,
            software_version=self.software_version,
            relay_admission_payload_ref=admission_ref,
            relay_admission_signature=(
                relay_admission_signature or self.relay_admission_signature
            ),
        )
        response = self._transport.post_json(
            "/relay/admission/request",
            request.to_dict(),
            self.timeout_seconds,
        )
        grant_payload = _extract_object(response, "grant", "relay_grant_missing")
        grant = RelaySlotGrant.from_dict(grant_payload)
        if grant.agent_id != self.agent_id:
            raise RelayClientError("relay_grant_agent_id_mismatch")
        if grant.target_internal_port != self.requested_internal_port:
            raise RelayClientError("relay_grant_target_port_mismatch")
        if grant.granted_epoch != admission_epoch:
            raise RelayClientError("relay_grant_epoch_mismatch")
        if grant.admission_request_hash != request.canonical_request_hash:
            raise RelayClientError("relay_grant_admission_request_hash_mismatch")
        return grant

    def keepalive(
        self,
        *,
        slot: RelaySlotGrant,
        keepalive_epoch: int,
        relay_lifecycle_signature: str,
    ) -> RelayKeepaliveReceipt:
        """Send a per-epoch relay slot keepalive."""

        self._require_active()
        slot = self._require_slot_for_agent(slot)
        _require_lifecycle_epoch(
            keepalive_epoch,
            "relay_keepalive_epoch_invalid",
            slot=slot,
        )
        payload_ref = relay_lifecycle_payload_ref(
            action="keepalive",
            agent_id=self.agent_id,
            slot_id=slot.slot_id,
            lifecycle_epoch=keepalive_epoch,
            previous_grant_hash=slot.canonical_response_hash,
            network_id=self.network_id,
            relay_base_url=self.relay_base_url,
        )
        _verify_lifecycle_signature(
            agent_id=self.agent_id,
            payload_ref=payload_ref,
            signature=relay_lifecycle_signature,
        )
        payload = {
            "agent_id": self.agent_id,
            "keepalive_epoch": keepalive_epoch,
            "previous_grant_hash": slot.canonical_response_hash,
            "relay_lifecycle_payload_ref": payload_ref,
            "relay_lifecycle_signature": relay_lifecycle_signature,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "slot_id": slot.slot_id,
        }
        response = self._transport.post_json(
            "/relay/slot/keepalive",
            payload,
            self.timeout_seconds,
        )
        renewal_result = _require_bound_lifecycle_response(
            response,
            action="keepalive",
            agent_id=self.agent_id,
            epoch=keepalive_epoch,
            previous_grant_hash=slot.canonical_response_hash,
            payload_ref=payload_ref,
            slot_id=slot.slot_id,
        )
        return RelayKeepaliveReceipt(
            slot_id=slot.slot_id,
            agent_id=self.agent_id,
            keepalive_epoch=keepalive_epoch,
            previous_grant_hash=slot.canonical_response_hash,
            relay_lifecycle_payload_ref=payload_ref,
            relay_lifecycle_signature=relay_lifecycle_signature,
            renewal_result=renewal_result,
        )

    def release_slot(
        self,
        *,
        slot: RelaySlotGrant,
        release_epoch: int,
        relay_lifecycle_signature: str,
    ) -> RelayReleaseReceipt:
        """Gracefully release a relay slot before shutdown."""

        self._require_active()
        slot = self._require_slot_for_agent(slot)
        _require_lifecycle_epoch(
            release_epoch,
            "relay_release_epoch_invalid",
            slot=slot,
        )
        payload_ref = relay_lifecycle_payload_ref(
            action="release",
            agent_id=self.agent_id,
            slot_id=slot.slot_id,
            lifecycle_epoch=release_epoch,
            previous_grant_hash=slot.canonical_response_hash,
            network_id=self.network_id,
            relay_base_url=self.relay_base_url,
        )
        _verify_lifecycle_signature(
            agent_id=self.agent_id,
            payload_ref=payload_ref,
            signature=relay_lifecycle_signature,
        )
        payload = {
            "agent_id": self.agent_id,
            "previous_grant_hash": slot.canonical_response_hash,
            "release_epoch": release_epoch,
            "relay_lifecycle_payload_ref": payload_ref,
            "relay_lifecycle_signature": relay_lifecycle_signature,
            "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
            "slot_id": slot.slot_id,
        }
        response = self._transport.post_json(
            "/relay/slot/release",
            payload,
            self.timeout_seconds,
        )
        release_result = _require_bound_lifecycle_response(
            response,
            action="release",
            agent_id=self.agent_id,
            epoch=release_epoch,
            previous_grant_hash=slot.canonical_response_hash,
            payload_ref=payload_ref,
            slot_id=slot.slot_id,
        )
        return RelayReleaseReceipt(
            slot_id=slot.slot_id,
            agent_id=self.agent_id,
            release_epoch=release_epoch,
            previous_grant_hash=slot.canonical_response_hash,
            relay_lifecycle_payload_ref=payload_ref,
            relay_lifecycle_signature=relay_lifecycle_signature,
            release_result=release_result,
        )

    def _require_active(self) -> None:
        if RELAY_CLIENT_NOT_ACTIVATED and not self._allow_guarded_request:
            raise RelayClientError("relay_client_not_activated")

    def _require_slot_for_agent(self, slot: object) -> RelaySlotGrant:
        if not isinstance(slot, RelaySlotGrant):
            raise RelayClientError("relay_slot_grant_required")
        if slot.agent_id != self.agent_id:
            raise RelayClientError("relay_slot_agent_id_mismatch")
        if slot.target_internal_port != self.requested_internal_port:
            raise RelayClientError("relay_slot_target_port_mismatch")
        return slot


def _extract_object(
    payload: Mapping[str, Any],
    key: str,
    missing_token: str,
) -> Mapping[str, Any]:
    _require_mapping(payload, missing_token)
    if key not in payload:
        raise RelayClientError(missing_token)
    value = payload[key]
    _require_mapping(value, missing_token)
    return value


def _require_bound_lifecycle_response(
    response: Mapping[str, Any],
    *,
    action: str,
    agent_id: str,
    epoch: int,
    previous_grant_hash: str,
    payload_ref: str,
    slot_id: str,
) -> str:
    if action == "keepalive":
        epoch_field = "keepalive_epoch"
        result_field = "renewal_result"
        result_token = "relay_keepalive_result_invalid"
        mismatch_token = "relay_keepalive_response_binding_mismatch"
    elif action == "release":
        epoch_field = "release_epoch"
        result_field = "release_result"
        result_token = "relay_release_result_invalid"
        mismatch_token = "relay_release_response_binding_mismatch"
    else:
        raise RelayClientError("relay_lifecycle_action_invalid")

    _require_mapping(response, mismatch_token)
    result = _require_token(response.get(result_field), result_token)
    expected = {
        "agent_id": agent_id,
        epoch_field: epoch,
        "previous_grant_hash": previous_grant_hash,
        "relay_lifecycle_payload_ref": payload_ref,
        "schema_version": RELAY_CLIENT_SCHEMA_VERSION,
        "slot_id": slot_id,
    }
    for field_name, expected_value in expected.items():
        if response.get(field_name) != expected_value:
            raise RelayClientError(mismatch_token)
    return result


def _coerce_endpoint(value: object) -> RelayEndpoint:
    if isinstance(value, RelayEndpoint):
        return value
    if not isinstance(value, Mapping):
        raise RelayClientError("relay_endpoint_must_be_object")
    return RelayEndpoint(
        host=value.get("host"),
        port=value.get("port"),
        transport=value.get("transport", "quic"),
        relay_mode=value.get("relay_mode", RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC),
    )


def _require_mapping(value: object, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RelayClientError(token)
    return value


def _require_relay_base_url(value: object) -> str:
    if not isinstance(value, str) or len(value) > _MAX_TEXT_CHARS:
        raise RelayClientError("relay_base_url_invalid")
    parsed = urlparse(value)
    if parsed.username is not None or parsed.password is not None:
        raise RelayClientError("relay_base_url_credentials_forbidden")
    if parsed.query or parsed.fragment:
        raise RelayClientError("relay_base_url_query_fragment_forbidden")
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise RelayClientError("relay_base_url_port_invalid") from exc
    if parsed_port is not None and (parsed_port < 1 or parsed_port > 65535):
        raise RelayClientError("relay_base_url_port_invalid")
    normalized = value.rstrip("/")
    if parsed.scheme == "https" and parsed.netloc and parsed.hostname:
        return normalized
    if parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "::1", "localhost"}:
        return normalized
    raise RelayClientError("relay_base_url_must_be_https_or_loopback_test_url")


def _require_lifecycle_epoch(
    value: object,
    token: str,
    *,
    slot: RelaySlotGrant,
) -> int:
    epoch = _require_epoch(value, token)
    if epoch < slot.granted_epoch:
        raise RelayClientError("relay_lifecycle_epoch_before_grant")
    if epoch > slot.granted_epoch + slot.ttl_epochs:
        raise RelayClientError("relay_lifecycle_epoch_after_ttl")
    return epoch


def _verify_lifecycle_signature(
    *,
    agent_id: str,
    payload_ref: str,
    signature: str,
) -> None:
    _require_bls_signature_hex(signature, "relay_lifecycle_signature_invalid")
    try:
        signature_ok = verify_invite_pop_digest(
            public_key_hex=agent_id,
            digest_hex=payload_ref,
            signature_hex=signature,
        )
    except ValueError as exc:
        raise RelayClientError("relay_lifecycle_signature_invalid") from exc
    if not signature_ok:
        raise RelayClientError("relay_lifecycle_signature_verification_failed")


def _require_host(value: object, token: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise RelayClientError(token)
    if (
        len(value) > _MAX_TEXT_CHARS
        or any(char in value for char in "/?#@")
        or any(char.isspace() for char in value)
    ):
        raise RelayClientError(token)
    return value


def _require_agent_id(value: object, token: str) -> str:
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise RelayClientError(token)
    return value


def _require_sha256_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise RelayClientError(token)
    return value


def _require_sha384_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or _SHA384_RE.fullmatch(value) is None:
        raise RelayClientError(token)
    return value


def _require_optional_sha256_hex(value: object, token: str) -> str | None:
    if value is None:
        return None
    return _require_sha256_hex(value, token)


def _require_bls_signature_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or _BLS_SIGNATURE_RE.fullmatch(value) is None:
        raise RelayClientError(token)
    return value


def _require_relay_slot_nonce(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise RelayClientError("relay_slot_nonce_invalid")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise RelayClientError("relay_slot_nonce_invalid") from exc
    if value.lower() != value:
        raise RelayClientError("relay_slot_nonce_invalid")
    return value


def _require_non_empty_string(value: object, token: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise RelayClientError(token)
    if len(value) > _MAX_TEXT_CHARS:
        raise RelayClientError(token)
    return value


def _require_token(value: object, token: str) -> str:
    if not isinstance(value, str) or _TOKEN_RE.fullmatch(value) is None:
        raise RelayClientError(token)
    return value


def _require_network_id(value: object) -> str:
    if not isinstance(value, str) or _NETWORK_ID_RE.fullmatch(value) is None:
        raise RelayClientError("relay_network_id_invalid")
    return value


def _require_port(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelayClientError(f"{token}_must_be_port_int")
    if value < 1 or value > 65535:
        raise RelayClientError(f"{token}_out_of_range")
    return value


def _require_epoch(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelayClientError(token)
    if value < 0 or value > _MAX_EPOCH:
        raise RelayClientError(token)
    return value


def _require_ttl_epochs(value: object) -> int:
    return _require_uint_range(
        value,
        "relay_ttl_epochs_invalid",
        1,
        _MAX_TTL_EPOCHS,
    )


def _require_uint_range(value: object, token: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelayClientError(token)
    if value < minimum or value > maximum:
        raise RelayClientError(token)
    return value


def _require_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RelayClientError("relay_timeout_invalid")
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0 or timeout > 10:
        raise RelayClientError("relay_timeout_out_of_range")
    return timeout


def _require_bool(value: object, token: str) -> bool:
    if not isinstance(value, bool):
        raise RelayClientError(token)
    return value


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args: object, **_kwargs: object) -> None:
        raise RelayClientError("relay_redirect_forbidden")


def _urlopen_no_redirect(
    request: Request,
    timeout_seconds: float,
    *,
    tls_cert_der_sha256: str | None = None,
) -> Any:
    if tls_cert_der_sha256 is None:
        return build_opener(_NoRedirect).open(request, timeout=timeout_seconds)
    # ILC-native relay trust is the signed DER fingerprint in the bootstrap
    # record. CA and hostname verification are intentionally replaced here by
    # post-handshake pin verification against that signed fingerprint.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    response = build_opener(HTTPSHandler(context=context), _NoRedirect).open(
        request,
        timeout=timeout_seconds,
    )
    try:
        _verify_response_tls_pin(response, tls_cert_der_sha256)
    except BaseException:
        response.close()
        raise
    return response


def _verify_response_tls_pin(response: Any, tls_cert_der_sha256: str) -> None:
    expected = _require_sha256_hex(
        tls_cert_der_sha256,
        "relay_tls_cert_der_sha256_invalid",
    )
    cert_der = _extract_response_cert_der(response)
    actual = hashlib.sha256(cert_der).hexdigest()
    if actual != expected:
        raise RelayClientError("relay_tls_cert_der_sha256_mismatch")


def _extract_response_cert_der(response: Any) -> bytes:
    try:
        sock = response.fp.raw._sock
        cert_der = sock.getpeercert(binary_form=True)
    except AttributeError as exc:
        raise RelayClientError("relay_tls_cert_unavailable") from exc
    if not isinstance(cert_der, bytes) or not cert_der:
        raise RelayClientError("relay_tls_cert_unavailable")
    return cert_der


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    encoded = json.dumps(
        dict(payload),
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(encoded) > _MAX_REQUEST_BYTES:
        raise RelayClientError("relay_canonical_payload_too_large")
    return encoded


__all__ = [
    "RELAY_ADMISSION_DOMAIN",
    "RELAY_CLIENT_NOT_ACTIVATED",
    "RELAY_CLIENT_SCHEMA_VERSION",
    "RELAY_CLIENT_TOKEN",
    "RELAY_LIFECYCLE_DOMAIN",
    "RELAY_MODE_PASS_THROUGH_CONSENSUS_QUIC",
    "HttpsRelayClientTransport",
    "RelayAdmissionRequest",
    "RelayClient",
    "RelayClientError",
    "RelayEndpoint",
    "RelayKeepaliveReceipt",
    "RelayReleaseReceipt",
    "RelaySlotGrant",
    "relay_admission_payload_ref",
    "relay_lifecycle_payload_ref",
    "relay_slot_claim_datagram",
]
