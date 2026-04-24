"""Phase-380 D2d abstract interface runtime surface."""

from __future__ import annotations

from dataclasses import dataclass, field
import copy
import re
from typing import Any, NewType, Protocol


D2D_INTERFACE_RUNTIME_VERSION = "d2d_interface_runtime_380.v0.1"
D2D_INTERFACE_DEPENDENCY = "d2d_interface_380.v0.1"
WIRE_TRANSPORT_DEPENDENCY = "wire_transport_runtime_323.v0.1"

D2dChannel = NewType("D2dChannel", str)

# ILC channel identifiers use a structured opaque prefix convention:
#   "cid:<hex>"  - deterministic channel bytes (NOT an IPFS CIDv1)
#   "rand:<hex>" - uniformly random channel bytes
# Payload CIDs (for example bafy... strings) are content-addresses carried in
# payload fields and are intentionally distinct from routing channel identifiers.
_ILC_CHANNEL_OPAQUE_PREFIXES = frozenset({"cid", "rand"})

_CANONICAL_D2D_INTERFACE_VECTORS: list[dict[str, Any]] = [
    {
        "message_id": "msg-001",
        "payload_cid": "bafybeigdyrzt6ncp4m2xg7r5z2xw7sbn3r7r2j7vph6a2m5wqk35m4w5ay",
        "channel_id": "cid:9f7a8c42bb11ddee99aa22cc33ff44aa",
        "sender_peer_id": "peer:alpha-01",
        "transport_headers": {
            "schema_ref": "d2d.message.v1",
            "topic": "node.header",
        },
    },
    {
        "message_id": "msg-002",
        "payload_cid": "bafybeibohv7i2fylx5vzo3h5smzqj2pvyew53kkr7bt7sn4l3vhh2n7zeu",
        "channel_id": "rand:11223344556677889900aabbccddeeff",
        "sender_peer_id": "peer:beta-02",
        "transport_headers": {
            "schema_ref": "d2d.message.v1",
            "topic": "node.fetch",
        },
    },
]


class D2dInterfaceValidationError(ValueError):
    """Typed validation exception with deterministic tokenized semantics."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


@dataclass(frozen=True)
class D2dMessage:
    """Abstract message shape used by higher-layer D2d loops."""

    message_id: str
    payload_cid: str
    channel_id: D2dChannel
    sender_peer_id: str
    transport_headers: dict[str, str] = field(default_factory=dict)


class D2dPeer(Protocol):
    """Abstract peer contract for later peering-loop runtime implementation."""

    peer_id: str

    def advertise(self) -> dict[str, str]:
        """Return deterministic peer metadata for topology selection."""

    def can_relay(self, channel_id: D2dChannel) -> bool:
        """Return whether this peer is eligible to relay a channel."""


class D2dTopology(Protocol):
    """Abstract topology contract for deterministic peer selection."""

    def candidate_peers(self, channel_id: D2dChannel) -> list[str]:
        """Return candidate peer IDs for a channel."""

    def peer_metadata(self, peer_id: str) -> dict[str, str]:
        """Return deterministic metadata for a peer."""


def _validate_non_empty_string(value: Any, token: str, message: str) -> str:
    if not isinstance(value, str):
        raise D2dInterfaceValidationError(token, message)
    normalized = value.strip()
    if not normalized:
        raise D2dInterfaceValidationError(token, message)
    return normalized


_CANONICAL_ALIAS_RE = re.compile(r"[-.]")


def _canonical_header_alias(value: str) -> str:
    """Canonicalize header aliases for invariant checks only."""

    return _CANONICAL_ALIAS_RE.sub("_", value.lower())


def validate_d2d_channel(value: Any) -> D2dChannel:
    """Validate a channel identifier as opaque transport metadata."""

    raw = _validate_non_empty_string(
        value,
        "d2d_channel_invalid",
        "channel_id_invalid",
    )
    if ":" not in raw:
        raise D2dInterfaceValidationError(
            "d2d_channel_not_opaque",
            f"channel_id_not_opaque:{raw}",
        )

    prefix, suffix = raw.split(":", 1)
    prefix = prefix.lower().strip()
    suffix = suffix.lower().strip()
    if prefix not in _ILC_CHANNEL_OPAQUE_PREFIXES:
        raise D2dInterfaceValidationError(
            "d2d_channel_not_opaque",
            f"channel_id_prefix_not_opaque:{raw}",
        )
    if len(suffix) < 16 or not re.fullmatch(r"[0-9a-f]+", suffix):
        raise D2dInterfaceValidationError(
            "d2d_channel_not_opaque",
            f"channel_id_suffix_not_opaque:{raw}",
        )
    return D2dChannel(f"{prefix}:{suffix}")


def validate_d2d_peer_id(value: Any) -> str:
    """Validate deterministic peer identity shape for abstract interfaces."""

    peer_id = _validate_non_empty_string(
        value,
        "d2d_peer_id_invalid",
        "peer_id_invalid",
    )
    if not re.fullmatch(r"peer:[a-z0-9][a-z0-9._-]{2,63}", peer_id):
        raise D2dInterfaceValidationError(
            "d2d_peer_id_invalid",
            f"peer_id_shape_invalid:{peer_id}",
        )
    return peer_id


def validate_d2d_message_envelope(raw: Any) -> dict[str, Any]:
    """Validate and normalize envelope shape without any transport behavior."""

    if not isinstance(raw, dict):
        raise D2dInterfaceValidationError(
            "d2d_message_envelope_not_object",
            "message_envelope_not_object",
        )

    message_id = _validate_non_empty_string(
        raw.get("message_id"),
        "d2d_message_id_invalid",
        "message_id_invalid",
    )
    payload_cid = _validate_non_empty_string(
        raw.get("payload_cid"),
        "d2d_payload_cid_invalid",
        f"payload_cid_invalid:{message_id}",
    )
    channel_id = validate_d2d_channel(raw.get("channel_id"))
    sender_peer_id = validate_d2d_peer_id(raw.get("sender_peer_id"))

    headers = raw.get("transport_headers", {})
    if not isinstance(headers, dict):
        raise D2dInterfaceValidationError(
            "d2d_transport_headers_not_object",
            f"transport_headers_not_object:{message_id}",
        )

    normalized_headers: dict[str, str] = {}
    for key, value in headers.items():
        normalized_key = _validate_non_empty_string(
            key,
            "d2d_transport_header_key_invalid",
            f"transport_header_key_invalid:{message_id}",
        )
        key_lower = normalized_key.lower()
        key_alias = _canonical_header_alias(key_lower)
        if key_alias == "creator_agent_id":
            raise D2dInterfaceValidationError(
                "d2d_creator_agent_id_forbidden",
                f"creator_agent_id_forbidden_in_transport_headers:{message_id}",
            )
        if key_lower in normalized_headers:
            raise D2dInterfaceValidationError(
                "d2d_transport_header_key_collision",
                f"transport_header_key_collision:{message_id}:{key_lower}",
            )
        normalized_value = _validate_non_empty_string(
            value,
            "d2d_transport_header_value_invalid",
            f"transport_header_value_invalid:{message_id}:{key_lower}",
        )
        normalized_headers[key_lower] = normalized_value

    return {
        "message_id": message_id,
        "payload_cid": payload_cid,
        "channel_id": channel_id,
        "sender_peer_id": sender_peer_id,
        "transport_headers": {k: normalized_headers[k] for k in sorted(normalized_headers)},
    }


def canonical_d2d_interface_vectors() -> list[dict[str, Any]]:
    """Return deep-copied deterministic vectors for runtime tests."""

    return copy.deepcopy(_CANONICAL_D2D_INTERFACE_VECTORS)
