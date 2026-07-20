# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 558 HTTP gossip transport adapter.

This module implements the CDL-061 prelock envelope surface for D2d gossip.
It builds and validates HTTP header dictionaries only; it does not perform any
socket, QUIC, or HTTP client/server operations.
"""

from __future__ import annotations

from typing import Any, Mapping

from ilc_core.crypto.pq_signature_verify import CDL_101_SIGNED_ENVELOPE_DEPENDENCY
from ilc_core.network.d2d.centrality_delta_gossip_runtime import (
    CDL_060_GOSSIP_RUNTIME_VERSION as _CDL_060_GOSSIP_RUNTIME_CHECK,
)
from ilc_core.network.d2d.gossip import validate_gossip_channel


GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_1572.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"
CDL_060_GOSSIP_RUNTIME_DEPENDENCY = "cdl_060_gossip_runtime_548.v0.1"
GOSSIP_URL_PREFIX = "/ilc/gossip/"
HOP_COUNT_SINGLE = 1
MAX_GOSSIP_TYPE_BYTES = 128
MAX_GOSSIP_BODY_BYTES = 10 * 1024 * 1024
REQUIRED_HEADERS = frozenset({
    "ILC-Gossip-Type",
    "ILC-Channel",
    "ILC-Epoch",
    "ILC-Hop-Count",
    "ILC-Signature",
    "ILC-Sender-Peer-Id",
    "ILC-Key-Id",
    "Content-Type",
})
FORBIDDEN_HEADER_KEYS = frozenset({
    "creator_agent_id",
    "node_id",
    "ILC-Creator-Agent-Id",
    "ILC-Node-Id",
})
_FORBIDDEN_HEADER_KEYS_LOWER = frozenset(key.lower() for key in FORBIDDEN_HEADER_KEYS)
ALLOWED_CONTENT_TYPES = frozenset({"application/cbor", "application/json"})
MAX_SENDER_PEER_ID_CHARS = 128
MAX_KEY_ID_CHARS = 64
LEGACY_UNVERIFIABLE_SENDER_PEER_ID = "legacy-unverifiable-peer"
LEGACY_UNVERIFIABLE_KEY_ID = "legacy-unverifiable-key"
HTTP_STATUS_BUFFERED = 202
HTTP_STATUS_SUPPRESSED = 204
HTTP_STATUS_ENVELOPE_ERROR = 400
HTTP_STATUS_EPOCH_CONFLICT = 409
HTTP_STATUS_FANOUT_EXCEEDED = 429
HTTP_STATUS_CRASH_RECOVERY = 503

if _CDL_060_GOSSIP_RUNTIME_CHECK != CDL_060_GOSSIP_RUNTIME_DEPENDENCY:
    import json as _json, sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "gossip_transport_dep_chain_mismatch",
                "dependency": "cdl_060_gossip_runtime",
                "expected": CDL_060_GOSSIP_RUNTIME_DEPENDENCY,
                "got": _CDL_060_GOSSIP_RUNTIME_CHECK,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("gossip_transport_cdl_060_gossip_runtime_dependency_mismatch")


def _require_non_empty_string(value: Any, error_token: str) -> str:
    if not isinstance(value, str):
        raise ValueError(error_token)
    normalized = value.strip()
    if not normalized:
        raise ValueError(error_token)
    return normalized


def _require_no_whitespace(value: str, error_token: str) -> str:
    if any(char.isspace() for char in value):
        raise ValueError(error_token)
    return value


def _require_gossip_type(value: Any) -> str:
    normalized = _require_non_empty_string(
        value,
        "gossip_message_type_must_be_non_empty_string",
    )
    if len(normalized.encode("utf-8")) > MAX_GOSSIP_TYPE_BYTES:
        raise ValueError("gossip_message_type_too_long")
    return normalized


def _require_non_negative_int(value: Any, error_token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(error_token)
    return value


def _validated_channel(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("cdl_039_channel_must_be_opaque")
    try:
        return str(validate_gossip_channel(value))
    except ValueError as exc:  # pragma: no cover - normalized to the ratified token
        raise ValueError("cdl_039_channel_must_be_opaque") from exc


def _validated_content_type(value: Any) -> str:
    normalized = _require_non_empty_string(value, "unsupported_content_type")
    if normalized not in ALLOWED_CONTENT_TYPES:
        raise ValueError("unsupported_content_type")
    return normalized


def _validated_sender_peer_id(value: Any) -> str:
    # CDL-039 compatibility: this is a static transport peer-registry slot
    # introduced by CDL-101. It is not a creator agent ID, graph node ID, or
    # authorship claim, so it does not join FORBIDDEN_HEADER_KEYS.
    normalized = _require_non_empty_string(value, "sender_peer_id_must_be_non_empty_string")
    if len(normalized) > MAX_SENDER_PEER_ID_CHARS:
        raise ValueError("sender_peer_id_too_long")
    return _require_no_whitespace(normalized, "sender_peer_id_must_not_contain_whitespace")


def _validated_key_id(value: Any) -> str:
    normalized = _require_non_empty_string(value, "key_id_must_be_non_empty_string")
    if len(normalized) > MAX_KEY_ID_CHARS:
        raise ValueError("key_id_too_long")
    return _require_no_whitespace(normalized, "key_id_must_not_contain_whitespace")


def _canonical_forbidden_match(key: str) -> bool:
    return key.lower() in _FORBIDDEN_HEADER_KEYS_LOWER


def _validated_epoch_header(value: Any) -> int:
    try:
        normalized = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("epoch_must_be_integer") from exc
    if normalized < 0:
        raise ValueError("epoch_must_be_non_negative")
    return normalized


def gossip_request_path(message_type: str) -> str:
    normalized = _require_gossip_type(message_type)
    return f"{GOSSIP_URL_PREFIX}{normalized}"


def build_gossip_headers(
    gossip_type: str,
    channel: str,
    epoch: int,
    hop_count: int,
    signature: str,
    sender_peer_id: str = LEGACY_UNVERIFIABLE_SENDER_PEER_ID,
    key_id: str = LEGACY_UNVERIFIABLE_KEY_ID,
    content_type: str = "application/cbor",
) -> dict[str, str]:
    normalized_type = _require_gossip_type(gossip_type)
    normalized_channel = _validated_channel(channel)
    normalized_epoch = _require_non_negative_int(epoch, "epoch_must_be_non_negative")
    normalized_hop_count = _require_non_negative_int(
        hop_count,
        "cdl_060_hop_count_must_be_single: single_hop_only",
    )
    if normalized_hop_count != HOP_COUNT_SINGLE:
        raise ValueError("cdl_060_hop_count_must_be_single: single_hop_only")
    normalized_signature = _require_non_empty_string(
        signature,
        "gossip_signature_must_be_non_empty_string",
    )
    normalized_sender_peer_id = _validated_sender_peer_id(sender_peer_id)
    normalized_key_id = _validated_key_id(key_id)
    normalized_content_type = _validated_content_type(content_type)
    return {
        "ILC-Gossip-Type": normalized_type,
        "ILC-Channel": normalized_channel,
        "ILC-Epoch": str(normalized_epoch),
        "ILC-Hop-Count": str(normalized_hop_count),
        "ILC-Signature": normalized_signature,
        "ILC-Sender-Peer-Id": normalized_sender_peer_id,
        "ILC-Key-Id": normalized_key_id,
        "Content-Type": normalized_content_type,
    }


def validate_gossip_headers(headers: dict[str, str]) -> bool:
    if not isinstance(headers, Mapping):
        raise ValueError("gossip_headers_must_be_mapping")

    for header_name in REQUIRED_HEADERS:
        if header_name not in headers:
            raise ValueError(f"missing_required_header:{header_name}")

    for raw_key in headers:
        if not isinstance(raw_key, str):
            raise ValueError("gossip_header_key_must_be_string")
        if _canonical_forbidden_match(raw_key):
            raise ValueError(f"cdl_039_violation: forbidden_header_{raw_key}")

    if str(headers["ILC-Hop-Count"]).strip() != str(HOP_COUNT_SINGLE):
        raise ValueError("cdl_060_hop_count_violation: single_hop_only")

    _validated_channel(headers["ILC-Channel"])
    _validated_content_type(headers["Content-Type"])
    _require_gossip_type(headers["ILC-Gossip-Type"])
    _require_non_empty_string(
        headers["ILC-Signature"],
        "gossip_signature_must_be_non_empty_string",
    )
    _validated_sender_peer_id(headers["ILC-Sender-Peer-Id"])
    _validated_key_id(headers["ILC-Key-Id"])
    _validated_epoch_header(headers["ILC-Epoch"])

    return True


def validate_gossip_body_size(body: bytes | bytearray | memoryview) -> int:
    """Validate an already-buffered gossip body against the transport cap."""

    if not isinstance(body, (bytes, bytearray, memoryview)):
        raise ValueError("gossip_body_must_be_bytes")
    size = len(body)
    if size > MAX_GOSSIP_BODY_BYTES:
        raise ValueError("gossip_body_too_large")
    return size
