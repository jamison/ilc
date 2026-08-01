# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-382 D2d gossip runtime surface.

This module enforces CDL-039 transport invariants: no creator_agent_id in transport headers, opaque channel routing field, and cluster membership non-inferrability.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

from .interface import (
    D2dInterfaceValidationError,
    _canonical_header_alias,
    validate_d2d_channel,
    validate_d2d_peer_id,
)
from .peer import D2D_PEERING_DEPENDENCY


D2D_GOSSIP_RUNTIME_VERSION = "d2d_gossip_runtime_382.v0.1"
D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"
MAX_OBSERVER_METADATA_TRACE_PEERS = 1024

_EXPECTED_PEERING_DEPENDENCY = "d2d_peering_381.v0.1"
if D2D_PEERING_DEPENDENCY != _EXPECTED_PEERING_DEPENDENCY:
    import json as _json
    import sys as _sys
    _sys.stdout.write(
        _json.dumps(
            {
                "ok": False,
                "error": "d2d_version_mismatch",
                "expected": _EXPECTED_PEERING_DEPENDENCY,
                "got": D2D_PEERING_DEPENDENCY,
            },
            sort_keys=True,
        )
        + "\n"
    )
    _sys.stdout.flush()
    raise RuntimeError("d2d_gossip_peering_dependency_mismatch")


class D2dGossipValidationError(ValueError):
    """Typed validation exception with deterministic token semantics."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _validate_non_empty_string(value: Any, token: str, message: str) -> str:
    if not isinstance(value, str):
        raise D2dGossipValidationError(token, message)
    normalized = value.strip()
    if not normalized:
        raise D2dGossipValidationError(token, message)
    return normalized

def sanitize_transport_headers(headers: Mapping[str, Any]) -> dict[str, str]:
    """Normalize transport headers and enforce creator-agent exclusion."""

    if not isinstance(headers, Mapping):
        raise D2dGossipValidationError(
            "d2d_transport_headers_not_mapping",
            "transport_headers_not_mapping",
        )

    normalized: dict[str, str] = {}
    for raw_key, raw_value in headers.items():
        key = _validate_non_empty_string(
            raw_key,
            "d2d_transport_header_key_invalid",
            "transport_header_key_invalid",
        )
        key_lower = key.lower()
        key_alias = _canonical_header_alias(key_lower)
        if key_alias == "creator_agent_id":
            raise D2dGossipValidationError(
                "d2d_creator_agent_id_forbidden",
                "creator_agent_id_forbidden_in_transport_headers",
            )
        if key_lower in normalized:
            raise D2dGossipValidationError(
                "d2d_transport_header_key_collision",
                f"transport_header_key_collision:{key_lower}",
            )
        value = _validate_non_empty_string(
            raw_value,
            "d2d_transport_header_value_invalid",
            f"transport_header_value_invalid:{key_lower}",
        )
        normalized[key_lower] = value

    return {k: normalized[k] for k in sorted(normalized)}


def validate_gossip_channel(channel_id: Any) -> str:
    """Validate gossip routing channel as an opaque identifier."""

    try:
        return str(validate_d2d_channel(channel_id))
    except D2dInterfaceValidationError as exc:
        raise D2dGossipValidationError(exc.token, exc.message) from exc


def build_transport_envelope(
    *,
    message_id: Any,
    payload_cid: Any,
    channel_id: Any,
    sender_peer_id: Any,
    transport_headers: Mapping[str, Any],
) -> dict[str, Any]:
    """Build deterministic transport envelope with CDL-039 invariants enforced."""

    normalized_message_id = _validate_non_empty_string(
        message_id,
        "d2d_message_id_invalid",
        "message_id_invalid",
    )
    normalized_payload_cid = _validate_non_empty_string(
        payload_cid,
        "d2d_payload_cid_invalid",
        f"payload_cid_invalid:{normalized_message_id}",
    )
    normalized_sender = validate_d2d_peer_id(sender_peer_id)
    normalized_channel = validate_gossip_channel(channel_id)
    normalized_headers = sanitize_transport_headers(transport_headers)

    return {
        "message_id": normalized_message_id,
        "payload_cid": normalized_payload_cid,
        "channel_id": normalized_channel,
        "sender_peer_id": normalized_sender,
        "transport_headers": normalized_headers,
    }


def deterministic_gossip_candidates(
    candidate_peers: Sequence[str],
    *,
    seed: int,
    limit: int = 4,
) -> list[str]:
    """Return deterministic candidate ordering for gossip relay selection."""

    if limit <= 0:
        raise D2dGossipValidationError(
            "d2d_gossip_limit_invalid",
            f"gossip_limit_invalid:{limit}",
        )

    normalized = sorted({validate_d2d_peer_id(peer_id) for peer_id in candidate_peers})
    if not normalized:
        return []

    def _ranking_key(peer_id: str) -> str:
        payload = f"{seed}:{peer_id}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    ranked = sorted(normalized, key=_ranking_key)
    return ranked[:limit]


def build_observer_metadata_trace(
    selected_peers: Sequence[str],
    *,
    channel_id: str,
    epoch_slot: int,
) -> list[dict[str, Any]]:
    """Build passive-observer metadata trace without cluster-membership disclosure."""

    normalized_channel = validate_gossip_channel(channel_id)
    if epoch_slot < 0:
        raise D2dGossipValidationError(
            "d2d_epoch_slot_invalid",
            f"epoch_slot_invalid:{epoch_slot}",
        )
    if len(selected_peers) > MAX_OBSERVER_METADATA_TRACE_PEERS:
        raise D2dGossipValidationError(
            "d2d_observer_trace_peer_limit_exceeded",
            f"observer_trace_peer_limit_exceeded:{len(selected_peers)}",
        )

    channel_tag = hashlib.sha256(normalized_channel.encode("utf-8")).hexdigest()[:16]
    trace: list[dict[str, Any]] = []
    for peer_id in selected_peers:
        normalized_peer = validate_d2d_peer_id(peer_id)
        trace.append(
            {
                "relay_peer_id": normalized_peer,
                "channel_tag": channel_tag,
                "epoch_slot": epoch_slot,
            }
        )
    return trace


def analyze_passive_observer_membership_leakage(
    metadata_trace: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Analyze trace records for passive-observer cluster-membership leakage."""

    forbidden_membership_keys = {
        "cluster_id",
        "cluster_members",
        "membership_set",
        "cohort",
        "group_membership",
    }

    for index, event in enumerate(metadata_trace):
        if not isinstance(event, Mapping):
            raise D2dGossipValidationError(
                "d2d_observer_event_invalid",
                f"observer_event_invalid:{index}",
            )

        present_forbidden = sorted(forbidden_membership_keys.intersection(event.keys()))
        if present_forbidden:
            raise D2dGossipValidationError(
                "d2d_cluster_membership_leak_detected",
                f"membership_leak_detected:{index}:{','.join(present_forbidden)}",
            )

        required = {"relay_peer_id", "channel_tag", "epoch_slot"}
        missing = sorted(required.difference(event.keys()))
        if missing:
            raise D2dGossipValidationError(
                "d2d_observer_event_missing_required_keys",
                f"observer_event_missing_required_keys:{index}:{','.join(missing)}",
            )

    return {
        "event_count": len(metadata_trace),
        "membership_leak_detected": False,
    }


async def execute_gossip_round(
    candidate_peers: Sequence[str],
    *,
    seed: int,
    channel_id: str,
    epoch_slot: int,
    limit: int = 4,
) -> dict[str, Any]:
    """Async-compatible deterministic gossip round helper."""

    selected = deterministic_gossip_candidates(candidate_peers, seed=seed, limit=limit)
    trace = build_observer_metadata_trace(selected, channel_id=channel_id, epoch_slot=epoch_slot)
    analysis = analyze_passive_observer_membership_leakage(trace)
    return {
        "selected_peers": selected,
        "metadata_trace": trace,
        "analysis": analysis,
    }
