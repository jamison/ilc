"""Phase-381 D2d peering runtime surface."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Sequence

from .interface import D2D_INTERFACE_DEPENDENCY, validate_d2d_peer_id


D2D_PEERING_RUNTIME_VERSION = "d2d_peering_runtime_381.v0.1"
D2D_PEERING_DEPENDENCY = "d2d_peering_381.v0.1"

_EXPECTED_INTERFACE_DEPENDENCY = "d2d_interface_380.v0.1"
if D2D_INTERFACE_DEPENDENCY != _EXPECTED_INTERFACE_DEPENDENCY:
    raise RuntimeError("d2d_peering_interface_dependency_mismatch")


class D2dPeeringValidationError(ValueError):
    """Typed validation exception with deterministic token semantics."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


PEER_STATE_DISCONNECTED = "disconnected"
PEER_STATE_HANDSHAKING = "handshaking"
PEER_STATE_CONNECTED = "connected"
PEER_STATE_BACKOFF = "backoff"


@dataclass(frozen=True)
class PeeringState:
    """Deterministic peering session state."""

    peer_id: str
    state: str
    attempt: int = 0
    last_error: str = ""


def _validate_state(value: str) -> str:
    allowed = {
        PEER_STATE_DISCONNECTED,
        PEER_STATE_HANDSHAKING,
        PEER_STATE_CONNECTED,
        PEER_STATE_BACKOFF,
    }
    if value not in allowed:
        raise D2dPeeringValidationError(
            "d2d_peering_state_invalid",
            f"peer_state_invalid:{value}",
        )
    return value


def create_disconnected_state(peer_id: str) -> PeeringState:
    """Create deterministic initial state for a peer."""

    normalized_peer_id = validate_d2d_peer_id(peer_id)
    return PeeringState(
        peer_id=normalized_peer_id,
        state=PEER_STATE_DISCONNECTED,
        attempt=0,
        last_error="",
    )


def transition_to_handshaking(state: PeeringState) -> PeeringState:
    """Transition from disconnected/backoff into handshaking."""

    _validate_state(state.state)
    if state.state not in {PEER_STATE_DISCONNECTED, PEER_STATE_BACKOFF}:
        raise D2dPeeringValidationError(
            "d2d_peering_transition_forbidden",
            f"transition_forbidden:{state.state}->handshaking",
        )
    return PeeringState(
        peer_id=state.peer_id,
        state=PEER_STATE_HANDSHAKING,
        attempt=state.attempt,
        last_error=state.last_error,
    )


def transition_from_handshake(
    state: PeeringState,
    *,
    handshake_ok: bool,
    failure_reason: str = "",
) -> PeeringState:
    """Transition from handshaking into connected or backoff state."""

    _validate_state(state.state)
    if state.state != PEER_STATE_HANDSHAKING:
        raise D2dPeeringValidationError(
            "d2d_peering_transition_forbidden",
            f"transition_forbidden:{state.state}->handshake_result",
        )

    if handshake_ok:
        return PeeringState(
            peer_id=state.peer_id,
            state=PEER_STATE_CONNECTED,
            attempt=state.attempt,
            last_error="",
        )

    reason = failure_reason.strip()
    if not reason:
        raise D2dPeeringValidationError(
            "d2d_peering_handshake_reason_missing",
            f"handshake_reason_missing:{state.peer_id}",
        )
    return PeeringState(
        peer_id=state.peer_id,
        state=PEER_STATE_BACKOFF,
        attempt=state.attempt + 1,
        last_error=reason,
    )


async def execute_peering_cycle(
    state: PeeringState,
    *,
    handshake_ok: bool,
    failure_reason: str = "",
) -> PeeringState:
    """Async-compatible deterministic peering cycle helper."""

    handshaking_state = transition_to_handshaking(state)
    return transition_from_handshake(
        handshaking_state,
        handshake_ok=handshake_ok,
        failure_reason=failure_reason,
    )


def deterministic_reconnect_candidates(
    candidates: Sequence[str],
    *,
    seed: int,
    limit: int = 3,
) -> list[str]:
    """Return deterministic reconnect candidate ordering for a seed."""

    if limit <= 0:
        raise D2dPeeringValidationError(
            "d2d_peering_limit_invalid",
            f"reconnect_limit_invalid:{limit}",
        )
    if not candidates:
        return []

    normalized: list[str] = []
    for candidate in candidates:
        normalized.append(validate_d2d_peer_id(candidate))

    unique = sorted(set(normalized))

    def _ranking_key(peer_id: str) -> str:
        payload = f"{seed}:{peer_id}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    ordered = sorted(unique, key=_ranking_key)
    return ordered[:limit]
