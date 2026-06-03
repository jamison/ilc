# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1437 OpenClaw harness-assisted P2P relay.

This module wires the package-boundary TransportHarness protocol to the
CDL-078 routing-reputation serve-event path. It does not bind a socket, deploy
an OpenClaw gateway, establish native Rust QUIC P2P sessions, mint ECU, settle
ILC, write graph state, or trigger an epoch transition.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ilc_core.network.d2d.routing_reputation_runtime import (
    CDL_078_DEPENDENCY,
    _global_reputation_state,
    record_serve_event,
)
from ilc_core.protocol.harness_interfaces import TransportHarness


OPENCLAW_P2P_RELAY_VERSION = "openclaw_p2p_relay_phase_1437.v0.1"
CDL_078_RELAY_DEPENDENCY = CDL_078_DEPENDENCY

OPENCLAW_P2P_ACTIVATED_TOKEN = "openclaw_p2p_activated_phase_1437"
OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN = "openclaw_harness_p2p_activated_phase_1437"
OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN = (
    "openclaw_harness_assisted_p2p_active_phase_1437"
)
NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN = "native_rust_p2p_not_activated_phase_1437"
NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN = (
    "native_rust_p2p_deferred_window_1459_plus_phase_1437"
)
OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN = (
    "openclaw_gateway_not_publicly_activated_phase_1437"
)
CDL_078_RELAY_WIRED_OPENCLAW_HARNESS_TOKEN = (
    "cdl_078_relay_wired_openclaw_harness_phase_1437"
)
TRANSPORT_HARNESS_INTERFACE_WIRED_TOKEN = (
    "transport_harness_interface_wired_phase_1437"
)
REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN = (
    "rehearsal_openclaw_path_validated_gate_phase_1437"
)
ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN = "ecu_distribution_not_activated_phase_1437"
EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN = "epoch_transition_not_triggered_phase_1437"
PUBLIC_RC_NOT_ACTIVATED_TOKEN = "public_rc_not_activated_phase_1437"

NATIVE_RUST_P2P_NOT_ACTIVATED = True
OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED = True
ECU_DISTRIBUTION_ACTIVATED = False
EPOCH_TRANSITION_TRIGGERED = False
PUBLIC_RC_ACTIVATED = False

_MAX_PAYLOAD_BYTES = 65_536
_MAX_CHANNEL_LENGTH = 256
_MAX_ADDRESS_LENGTH = 1024
_MAX_METADATA_ENTRIES = 32
_MAX_METADATA_TEXT_LENGTH = 512

_DEFAULT_METADATA = {
    "phase": "1437",
    "relay_dependency": CDL_078_RELAY_DEPENDENCY,
}


def relay_payload_via_harness(
    *,
    harness: TransportHarness,
    channel: str,
    payload: bytes,
    epoch: int,
    peer_id: str,
    metadata: Mapping[str, str] | None = None,
    reputation_state: dict[str, Any] | None = None,
) -> str:
    """Publish a bounded payload through OpenClaw and credit CDL-078 on success."""

    transport = _require_harness(harness)
    clean_channel = _require_text(
        "channel",
        channel,
        max_length=_MAX_CHANNEL_LENGTH,
        error_token="openclaw_p2p_relay_invalid_channel",
    )
    clean_payload = _require_payload(payload)
    clean_epoch = _require_epoch(epoch)
    clean_peer_id = _require_text(
        "peer_id",
        peer_id,
        max_length=_MAX_ADDRESS_LENGTH,
        error_token="openclaw_p2p_relay_invalid_peer_id",
    )
    clean_metadata = _normalize_metadata(metadata)

    address = transport.publish_payload(
        channel=clean_channel,
        payload=clean_payload,
        epoch=clean_epoch,
        metadata=clean_metadata,
    )
    clean_address = _require_text(
        "address",
        address,
        max_length=_MAX_ADDRESS_LENGTH,
        error_token="openclaw_p2p_relay_invalid_address",
    )
    record_serve_event(
        clean_peer_id,
        clean_epoch,
        reputation_state if reputation_state is not None else _global_reputation_state,
    )
    return clean_address


def fetch_payload_via_harness(
    *,
    harness: TransportHarness,
    address: str,
    epoch: int,
) -> bytes:
    """Fetch a bounded payload through the OpenClaw TransportHarness."""

    transport = _require_harness(harness)
    clean_address = _require_text(
        "address",
        address,
        max_length=_MAX_ADDRESS_LENGTH,
        error_token="openclaw_p2p_relay_invalid_address",
    )
    clean_epoch = _require_epoch(epoch)
    fetched = transport.fetch_payload(
        address=clean_address,
        max_bytes=_MAX_PAYLOAD_BYTES,
        epoch=clean_epoch,
    )
    return _require_payload(fetched)


def openclaw_p2p_relay_tokens() -> tuple[str, ...]:
    """Return Phase 1437 activation and non-activation tokens."""

    return (
        OPENCLAW_P2P_RELAY_VERSION,
        CDL_078_RELAY_DEPENDENCY,
        OPENCLAW_P2P_ACTIVATED_TOKEN,
        OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN,
        OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN,
        NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN,
        NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN,
        OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN,
        CDL_078_RELAY_WIRED_OPENCLAW_HARNESS_TOKEN,
        TRANSPORT_HARNESS_INTERFACE_WIRED_TOKEN,
        REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN,
        ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
        EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN,
        PUBLIC_RC_NOT_ACTIVATED_TOKEN,
    )


def openclaw_p2p_relay_manifest() -> dict[str, Any]:
    """Return side-effect-free Phase 1437 relay activation metadata."""

    return {
        "cdl_078_relay_dependency": CDL_078_RELAY_DEPENDENCY,
        "ecu_distribution_activated": ECU_DISTRIBUTION_ACTIVATED,
        "epoch_transition_triggered": EPOCH_TRANSITION_TRIGGERED,
        "max_address_bytes": _MAX_ADDRESS_LENGTH,
        "max_payload_bytes": _MAX_PAYLOAD_BYTES,
        "native_rust_p2p_activated": not NATIVE_RUST_P2P_NOT_ACTIVATED,
        "native_rust_p2p_deferred_window": "1459+",
        "openclaw_gateway_publicly_activated": (
            not OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED
        ),
        "openclaw_harness_p2p_activated": True,
        "public_rc_activated": PUBLIC_RC_ACTIVATED,
        "tokens": openclaw_p2p_relay_tokens(),
        "transport_interface": "TransportHarness",
        "version": OPENCLAW_P2P_RELAY_VERSION,
    }


def _require_harness(harness: TransportHarness) -> TransportHarness:
    if not isinstance(harness, TransportHarness):
        raise ValueError("openclaw_p2p_relay_invalid_harness")
    return harness


def _require_epoch(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("openclaw_p2p_relay_invalid_epoch")
    return value


def _require_text(
    name: str,
    value: Any,
    *,
    max_length: int,
    error_token: str,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(error_token)
    clean = value.strip()
    if len(clean) > max_length:
        raise ValueError(error_token)
    if "\x00" in clean:
        raise ValueError(error_token)
    return clean


def _require_payload(value: Any) -> bytes:
    if not isinstance(value, bytes):
        raise ValueError("openclaw_p2p_relay_invalid_payload")
    if len(value) > _MAX_PAYLOAD_BYTES:
        raise ValueError("openclaw_p2p_relay_payload_too_large")
    return value


def _normalize_metadata(metadata: Mapping[str, str] | None) -> dict[str, str]:
    merged: dict[str, str] = dict(_DEFAULT_METADATA)
    if metadata is None:
        return merged
    if not isinstance(metadata, Mapping):
        raise ValueError("openclaw_p2p_relay_invalid_metadata")
    if len(metadata) > _MAX_METADATA_ENTRIES:
        raise ValueError("openclaw_p2p_relay_metadata_too_large")
    for key, value in metadata.items():
        clean_key = _require_text(
            "metadata_key",
            key,
            max_length=_MAX_METADATA_TEXT_LENGTH,
            error_token="openclaw_p2p_relay_invalid_metadata",
        )
        clean_value = _require_text(
            "metadata_value",
            value,
            max_length=_MAX_METADATA_TEXT_LENGTH,
            error_token="openclaw_p2p_relay_invalid_metadata",
        )
        merged[clean_key] = clean_value
    if len(merged) > _MAX_METADATA_ENTRIES:
        raise ValueError("openclaw_p2p_relay_metadata_too_large")
    return merged


__all__ = [
    "CDL_078_RELAY_DEPENDENCY",
    "CDL_078_RELAY_WIRED_OPENCLAW_HARNESS_TOKEN",
    "ECU_DISTRIBUTION_ACTIVATED",
    "ECU_DISTRIBUTION_NOT_ACTIVATED_TOKEN",
    "EPOCH_TRANSITION_NOT_TRIGGERED_TOKEN",
    "EPOCH_TRANSITION_TRIGGERED",
    "NATIVE_RUST_P2P_DEFERRED_WINDOW_1459_PLUS_TOKEN",
    "NATIVE_RUST_P2P_NOT_ACTIVATED",
    "NATIVE_RUST_P2P_NOT_ACTIVATED_TOKEN",
    "OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED",
    "OPENCLAW_GATEWAY_NOT_PUBLICLY_ACTIVATED_TOKEN",
    "OPENCLAW_HARNESS_ASSISTED_P2P_ACTIVE_TOKEN",
    "OPENCLAW_HARNESS_P2P_ACTIVATED_TOKEN",
    "OPENCLAW_P2P_ACTIVATED_TOKEN",
    "OPENCLAW_P2P_RELAY_VERSION",
    "PUBLIC_RC_ACTIVATED",
    "PUBLIC_RC_NOT_ACTIVATED_TOKEN",
    "REHEARSAL_OPENCLAW_PATH_VALIDATED_GATE_TOKEN",
    "TRANSPORT_HARNESS_INTERFACE_WIRED_TOKEN",
    "fetch_payload_via_harness",
    "openclaw_p2p_relay_manifest",
    "openclaw_p2p_relay_tokens",
    "relay_payload_via_harness",
]
