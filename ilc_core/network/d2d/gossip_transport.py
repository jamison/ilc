"""Phase 558 HTTP gossip transport adapter.

This module implements the CDL-061 prelock envelope surface for D2d gossip.
It builds and validates HTTP header dictionaries only; it does not perform any
socket, QUIC, or HTTP client/server operations.
"""

from __future__ import annotations

from typing import Any, Mapping

from ilc_core.network.d2d.centrality_delta_gossip_runtime import (
    CDL_060_GOSSIP_RUNTIME_VERSION as _CDL_060_GOSSIP_RUNTIME_CHECK,
)
from ilc_core.network.d2d.gossip import validate_gossip_channel


GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_999.v0.1"
CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"
CDL_060_GOSSIP_RUNTIME_DEPENDENCY = "cdl_060_gossip_runtime_548.v0.1"
GOSSIP_URL_PREFIX = "/ilc/gossip/"
HOP_COUNT_SINGLE = 1
REQUIRED_HEADERS = frozenset({
    "ILC-Gossip-Type",
    "ILC-Channel",
    "ILC-Epoch",
    "ILC-Hop-Count",
    "ILC-Signature",
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
HTTP_STATUS_BUFFERED = 202
HTTP_STATUS_SUPPRESSED = 204
HTTP_STATUS_ENVELOPE_ERROR = 400
HTTP_STATUS_EPOCH_CONFLICT = 409
HTTP_STATUS_FANOUT_EXCEEDED = 429
HTTP_STATUS_CRASH_RECOVERY = 503

assert _CDL_060_GOSSIP_RUNTIME_CHECK == CDL_060_GOSSIP_RUNTIME_DEPENDENCY, (
    f"dep chain mismatch: {_CDL_060_GOSSIP_RUNTIME_CHECK}"
)


def _require_non_empty_string(value: Any, error_token: str) -> str:
    if not isinstance(value, str):
        raise ValueError(error_token)
    normalized = value.strip()
    if not normalized:
        raise ValueError(error_token)
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
    normalized = _require_non_empty_string(
        message_type,
        "gossip_message_type_must_be_non_empty_string",
    )
    return f"{GOSSIP_URL_PREFIX}{normalized}"


def build_gossip_headers(
    gossip_type: str,
    channel: str,
    epoch: int,
    hop_count: int,
    signature: str,
    content_type: str = "application/cbor",
) -> dict[str, str]:
    normalized_type = _require_non_empty_string(
        gossip_type,
        "gossip_message_type_must_be_non_empty_string",
    )
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
    normalized_content_type = _validated_content_type(content_type)
    return {
        "ILC-Gossip-Type": normalized_type,
        "ILC-Channel": normalized_channel,
        "ILC-Epoch": str(normalized_epoch),
        "ILC-Hop-Count": str(normalized_hop_count),
        "ILC-Signature": normalized_signature,
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
    _require_non_empty_string(
        headers["ILC-Gossip-Type"],
        "gossip_message_type_must_be_non_empty_string",
    )
    _require_non_empty_string(
        headers["ILC-Signature"],
        "gossip_signature_must_be_non_empty_string",
    )
    _validated_epoch_header(headers["ILC-Epoch"])

    return True
