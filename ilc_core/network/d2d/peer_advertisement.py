# SPDX-License-Identifier: AGPL-3.0-only
"""PeerAdvertisement runtime schema for CDL-103 dynamic discovery.

The module implements the GAP-DISCOV-01 candidate schema only. It does not
activate dynamic discovery, authorize unknown peers, or grant network roles.
"""

from __future__ import annotations

import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit

from ilc_core.crypto.pq_signature_verify import (
    _MLDSA_PK_HEX_LENGTH,
    _MLDSA_SIG_HEX_LENGTH,
)


PEER_ADVERTISEMENT_SCHEMA_VERSION = "peer_advertisement_cdl103.v0.1"
PEER_ADVERTISEMENT_RUNTIME_VERSION = "peer_advertisement_gap_discov_03.v0.1"
MAX_TTL_EPOCHS = 4

_SHA384_HEX_RE = re.compile(r"^[0-9a-f]{96}$")
_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")
_MAX_HOST_CHARS = 253
_MAX_PROTOCOL_VERSION_CHARS = 64
_MAX_KEY_BINDING_REF_CHARS = 256
_LOCALHOST_NAMES = frozenset({"localhost", "localhost.localdomain"})
_NONSTANDARD_IPV4_LITERAL_CHARS = frozenset("0123456789abcdefABCDEFxX.")


class PeerAdvertisementValidationError(ValueError):
    """Stable validation error for malformed peer advertisements."""


@dataclass(frozen=True)
class TransportEndpoint:
    scheme: str
    host: str
    port: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "scheme": self.scheme,
        }

    def to_url(self) -> str:
        formatted_host = f"[{self.host}]" if ":" in self.host else self.host
        return f"{self.scheme}://{formatted_host}:{self.port}"

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
        *,
        allow_private_address_literals: bool = False,
    ) -> "TransportEndpoint":
        if not isinstance(value, Mapping):
            raise PeerAdvertisementValidationError("peer_advertisement_endpoint_invalid")
        allowed = {"host", "port", "scheme"}
        extra = sorted(set(value).difference(allowed))
        if extra:
            raise PeerAdvertisementValidationError(
                f"peer_advertisement_endpoint_unknown_fields:{extra}"
            )
        scheme = _require_string(
            value.get("scheme"),
            "peer_advertisement_endpoint_scheme_invalid",
            max_chars=16,
        ).lower()
        if scheme != "https":
            raise PeerAdvertisementValidationError(
                "peer_advertisement_endpoint_scheme_must_be_https"
            )
        host = _require_string(
            value.get("host"),
            "peer_advertisement_endpoint_host_invalid",
            max_chars=_MAX_HOST_CHARS,
        ).lower().rstrip(".")
        port = _require_int(
            value.get("port"),
            "peer_advertisement_endpoint_port_invalid",
            min_value=1,
            max_value=65535,
        )
        endpoint = f"https://[{host}]:{port}" if ":" in host else f"https://{host}:{port}"
        normalized = _validate_peer_endpoint(
            endpoint,
            allow_private_address_literals=allow_private_address_literals,
        )
        if not normalized.endswith(f":{port}"):
            raise PeerAdvertisementValidationError("peer_advertisement_endpoint_port_invalid")
        return cls(scheme="https", host=host, port=port)


@dataclass(frozen=True)
class PeerAdvertisement:
    agent_id: str
    transport_endpoint: TransportEndpoint
    protocol_version: str
    installed_slices_digest: str
    content_availability_count: int
    peer_timestamp_epoch: int
    ttl_epochs: int
    ml_dsa_signature: str
    key_binding_ref: str
    schema_version: str = PEER_ADVERTISEMENT_SCHEMA_VERSION

    def body_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "content_availability_count": self.content_availability_count,
            "installed_slices_digest": self.installed_slices_digest,
            "peer_timestamp_epoch": self.peer_timestamp_epoch,
            "protocol_version": self.protocol_version,
            "transport_endpoint": self.transport_endpoint.to_dict(),
            "ttl_epochs": self.ttl_epochs,
        }

    def to_canonical_json(self) -> bytes:
        """Return the canonical signature preimage: JSON bytes for body only."""

        return json.dumps(
            self.body_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")

    def to_dict(self) -> dict[str, Any]:
        return {
            "body": self.body_dict(),
            "key_binding_ref": self.key_binding_ref,
            "ml_dsa_signature": self.ml_dsa_signature,
            "schema_version": self.schema_version,
        }

    def verify(
        self,
        ml_dsa_verify_fn: Callable[[bytes, str, str], bool],
        *,
        pubkey_hex: str,
    ) -> bool:
        """Verify the ML-DSA-65 signature against an explicit bound public key."""

        try:
            _require_lower_hex_exact(
                pubkey_hex,
                _MLDSA_PK_HEX_LENGTH,
                "peer_advertisement_pubkey_invalid",
            )
            return bool(
                ml_dsa_verify_fn(
                    self.to_canonical_json(),
                    self.ml_dsa_signature,
                    pubkey_hex,
                )
            )
        except Exception:  # noqa: BLE001 - verification must fail closed.
            return False

    def is_expired(self, current_epoch: int) -> bool:
        current = _require_int(
            current_epoch,
            "peer_advertisement_current_epoch_invalid",
            min_value=0,
        )
        return self.peer_timestamp_epoch + self.ttl_epochs <= current

    @property
    def endpoint_url(self) -> str:
        return self.transport_endpoint.to_url()

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        allow_private_address_literals: bool = False,
    ) -> "PeerAdvertisement":
        if not isinstance(value, Mapping):
            raise PeerAdvertisementValidationError("peer_advertisement_not_mapping")
        allowed = {"body", "key_binding_ref", "ml_dsa_signature", "schema_version"}
        missing = sorted(allowed.difference(value))
        if missing:
            raise PeerAdvertisementValidationError(
                f"peer_advertisement_missing_fields:{missing}"
            )
        extra = sorted(set(value).difference(allowed))
        if extra:
            raise PeerAdvertisementValidationError(
                f"peer_advertisement_unknown_fields:{extra}"
            )
        schema_version = _require_string(
            value.get("schema_version"),
            "peer_advertisement_schema_version_invalid",
            max_chars=80,
        )
        if schema_version != PEER_ADVERTISEMENT_SCHEMA_VERSION:
            raise PeerAdvertisementValidationError(
                "peer_advertisement_schema_version_unsupported"
            )
        body = value.get("body")
        if not isinstance(body, Mapping):
            raise PeerAdvertisementValidationError("peer_advertisement_body_invalid")
        allowed_body = {
            "agent_id",
            "content_availability_count",
            "installed_slices_digest",
            "peer_timestamp_epoch",
            "protocol_version",
            "transport_endpoint",
            "ttl_epochs",
        }
        missing_body = sorted(allowed_body.difference(body))
        if missing_body:
            raise PeerAdvertisementValidationError(
                f"peer_advertisement_body_missing_fields:{missing_body}"
            )
        extra_body = sorted(set(body).difference(allowed_body))
        if extra_body:
            raise PeerAdvertisementValidationError(
                f"peer_advertisement_body_unknown_fields:{extra_body}"
            )
        return cls(
            agent_id=_require_sha384_hex(
                body.get("agent_id"),
                "peer_advertisement_agent_id_invalid",
            ),
            transport_endpoint=TransportEndpoint.from_mapping(
                body.get("transport_endpoint"),
                allow_private_address_literals=allow_private_address_literals,
            ),
            protocol_version=_require_string(
                body.get("protocol_version"),
                "peer_advertisement_protocol_version_invalid",
                max_chars=_MAX_PROTOCOL_VERSION_CHARS,
            ),
            installed_slices_digest=_require_sha384_hex(
                body.get("installed_slices_digest"),
                "peer_advertisement_installed_slices_digest_invalid",
            ),
            content_availability_count=_require_int(
                body.get("content_availability_count"),
                "peer_advertisement_content_availability_count_invalid",
                min_value=0,
            ),
            peer_timestamp_epoch=_require_int(
                body.get("peer_timestamp_epoch"),
                "peer_advertisement_timestamp_epoch_invalid",
                min_value=0,
            ),
            ttl_epochs=_require_int(
                body.get("ttl_epochs"),
                "peer_advertisement_ttl_epochs_invalid",
                min_value=1,
                max_value=MAX_TTL_EPOCHS,
            ),
            ml_dsa_signature=_require_lower_hex_exact(
                value.get("ml_dsa_signature"),
                _MLDSA_SIG_HEX_LENGTH,
                "peer_advertisement_signature_invalid",
            ),
            key_binding_ref=_require_string(
                value.get("key_binding_ref"),
                "peer_advertisement_key_binding_ref_invalid",
                max_chars=_MAX_KEY_BINDING_REF_CHARS,
            ),
            schema_version=schema_version,
        )


def _require_string(value: Any, token: str, *, max_chars: int) -> str:
    if not isinstance(value, str):
        raise PeerAdvertisementValidationError(token)
    normalized = value.strip()
    if not normalized or len(normalized) > max_chars or any(char.isspace() for char in normalized):
        raise PeerAdvertisementValidationError(token)
    return normalized


def _require_int(
    value: Any,
    token: str,
    *,
    min_value: int,
    max_value: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < min_value:
        raise PeerAdvertisementValidationError(token)
    if max_value is not None and value > max_value:
        raise PeerAdvertisementValidationError(token)
    return value


def _require_sha384_hex(value: Any, token: str) -> str:
    if not isinstance(value, str) or _SHA384_HEX_RE.fullmatch(value) is None:
        raise PeerAdvertisementValidationError(token)
    return value


def _require_lower_hex_exact(value: Any, expected_length: int, token: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != expected_length
        or _LOWER_HEX_RE.fullmatch(value) is None
    ):
        raise PeerAdvertisementValidationError(token)
    return value


def _validate_peer_endpoint(
    endpoint: str,
    *,
    allow_private_address_literals: bool = False,
) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise PeerAdvertisementValidationError("peer_advertisement_endpoint_invalid")
    normalized = endpoint.strip()
    parts = urlsplit(normalized)
    if (
        parts.scheme != "https"
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
        or parts.path not in ("", "/")
        or not parts.hostname
    ):
        raise PeerAdvertisementValidationError("peer_advertisement_endpoint_invalid")
    hostname = parts.hostname.lower()
    if not allow_private_address_literals:
        _reject_private_address_literal(hostname)
    try:
        port = parts.port
    except ValueError as exc:
        raise PeerAdvertisementValidationError(
            "peer_advertisement_endpoint_port_invalid"
        ) from exc
    if port is None:
        raise PeerAdvertisementValidationError("peer_advertisement_endpoint_port_invalid")
    formatted_host = f"[{hostname}]" if ":" in hostname else hostname
    return f"https://{formatted_host}:{port}"


def _reject_private_address_literal(hostname: str) -> None:
    normalized = hostname.strip().lower().rstrip(".")
    if normalized in _LOCALHOST_NAMES or normalized.endswith(".localhost"):
        raise PeerAdvertisementValidationError(
            "peer_advertisement_private_endpoint_forbidden"
        )
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        address = _parse_nonstandard_ipv4_literal(normalized)
        if address is None:
            return
    if not address.is_global:
        raise PeerAdvertisementValidationError(
            "peer_advertisement_private_endpoint_forbidden"
        )


def _parse_nonstandard_ipv4_literal(hostname: str) -> ipaddress.IPv4Address | None:
    if not hostname or not any(char.isdigit() for char in hostname):
        return None
    if any(char not in _NONSTANDARD_IPV4_LITERAL_CHARS for char in hostname):
        return None
    try:
        return ipaddress.IPv4Address(socket.inet_aton(hostname))
    except OSError:
        return None
