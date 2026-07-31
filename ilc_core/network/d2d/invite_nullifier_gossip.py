# SPDX-License-Identifier: AGPL-3.0-only
"""Invite nullifier D2D gossip payload helpers.

Phase 1576p-b closes the cross-node replay-prevention gap by adding the
message payload and ingress handler for invite redemption nullifiers. Transport
authentication is enforced by the HTTP gossip runtime treating this message
type as authority-bearing.
"""

from __future__ import annotations

import json
from typing import Mapping

from ilc_core.genesis.invite_nullifier_registry import (
    InviteNullifierError,
    InviteNullifierRegistry,
)

INVITE_NULLIFIER_GOSSIP_RUNTIME_VERSION = "invite_nullifier_gossip_1576pb.v0.1"
INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE: str = "invite_nullifier_v1"
INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION = "invite_nullifier_gossip_message.v1"
MAX_MESSAGE_KEYS = 5
MAX_CLAIMED_ACTOR_CHARS = 128
SHA256_HEX_CHARS = 64
_REQUIRED_KEYS = frozenset({
    "claimed_actor",
    "message_type",
    "nullifier_hex",
    "schema_version",
})
_OPTIONAL_KEYS = frozenset()


def build_nullifier_gossip_message(
    nullifier_hex: str,
    *,
    claimed_actor: str,
) -> dict[str, str]:
    """Build a canonical invite-nullifier gossip message."""

    _require_sha256_hex(nullifier_hex, "invite_nullifier_gossip_invalid_hex")
    return {
        "claimed_actor": _require_non_empty_string(
            claimed_actor,
            "invite_nullifier_gossip_claimed_actor_invalid",
        ),
        "message_type": INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE,
        "nullifier_hex": nullifier_hex,
        "schema_version": INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION,
    }


def encode_nullifier_gossip_payload(message: Mapping[str, object]) -> bytes:
    """Encode a nullifier gossip message as deterministic JSON bytes."""

    _validated_message(message)
    return json.dumps(
        dict(message),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def decode_nullifier_gossip_payload(payload: bytes | str) -> dict[str, str]:
    """Decode and validate a deterministic JSON nullifier gossip payload."""

    if isinstance(payload, bytes):
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InviteNullifierError("invite_nullifier_gossip_payload_invalid") from exc
    elif isinstance(payload, str):
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise InviteNullifierError("invite_nullifier_gossip_payload_invalid") from exc
    else:
        raise InviteNullifierError("invite_nullifier_gossip_payload_invalid")
    return _validated_message(decoded)


def handle_nullifier_gossip_message(
    message: Mapping[str, object],
    registry: InviteNullifierRegistry,
) -> str:
    """Register an incoming nullifier gossip message, discarding duplicates."""

    if not isinstance(registry, InviteNullifierRegistry):
        raise InviteNullifierError("invite_nullifier_gossip_registry_invalid")
    validated = _validated_message(message)
    nullifier_hex = validated["nullifier_hex"]
    if registry.is_known(nullifier_hex):
        return "duplicate_discarded"
    registry.register_nullifier(nullifier_hex)
    return "registered"


def _validated_message(message: object) -> dict[str, str]:
    if not isinstance(message, Mapping):
        raise InviteNullifierError("invite_nullifier_gossip_message_invalid")
    if len(message) > MAX_MESSAGE_KEYS:
        raise InviteNullifierError("invite_nullifier_gossip_message_too_wide")
    keys = set(message.keys())
    if not all(isinstance(key, str) for key in keys):
        raise InviteNullifierError("invite_nullifier_gossip_message_key_invalid")
    if not _REQUIRED_KEYS.issubset(keys):
        raise InviteNullifierError("invite_nullifier_gossip_message_missing_required")
    extra = keys.difference(_REQUIRED_KEYS.union(_OPTIONAL_KEYS))
    if extra:
        raise InviteNullifierError("invite_nullifier_gossip_message_unknown_key")
    if message["message_type"] != INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE:
        raise InviteNullifierError("invite_nullifier_gossip_message_type_invalid")
    if message["schema_version"] != INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION:
        raise InviteNullifierError("invite_nullifier_gossip_schema_version_invalid")
    nullifier_hex = message["nullifier_hex"]
    _require_sha256_hex(nullifier_hex, "invite_nullifier_gossip_invalid_hex")
    validated = {
        "message_type": INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE,
        "nullifier_hex": nullifier_hex,
        "schema_version": INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION,
    }
    if "claimed_actor" in message:
        validated["claimed_actor"] = _require_non_empty_string(
            message["claimed_actor"],
            "invite_nullifier_gossip_claimed_actor_invalid",
        )
    return validated


def _require_sha256_hex(value: object, token: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != SHA256_HEX_CHARS
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InviteNullifierError(token)
    return value


def _require_non_empty_string(value: object, token: str) -> str:
    if not isinstance(value, str):
        raise InviteNullifierError(token)
    normalized = value.strip()
    if (
        not normalized
        or normalized != value
        or len(normalized) > MAX_CLAIMED_ACTOR_CHARS
        or any(char.isspace() for char in normalized)
    ):
        raise InviteNullifierError(token)
    return normalized


__all__ = [
    "INVITE_NULLIFIER_GOSSIP_MESSAGE_TYPE",
    "INVITE_NULLIFIER_GOSSIP_RUNTIME_VERSION",
    "INVITE_NULLIFIER_GOSSIP_SCHEMA_VERSION",
    "MAX_CLAIMED_ACTOR_CHARS",
    "MAX_MESSAGE_KEYS",
    "build_nullifier_gossip_message",
    "decode_nullifier_gossip_payload",
    "encode_nullifier_gossip_payload",
    "handle_nullifier_gossip_message",
]
