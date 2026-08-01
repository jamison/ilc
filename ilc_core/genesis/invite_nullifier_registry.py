# SPDX-License-Identifier: AGPL-3.0-only
"""Local invite nullifier registry for Phase 1576p.

This module is in-process only. Cross-node D2D propagation is intentionally not
implemented here; Phase 1576p-b owns that sensitive network surface.
"""

from __future__ import annotations

import threading

INVITE_NULLIFIER_REGISTRY_VERSION = "invite_nullifier_registry_1576p.v0.1"
_MAX_REGISTRY_SIZE = 10_000
_SHA256_HEX_CHARS = 64


class InviteNullifierError(ValueError):
    """Stable exception type for local invite nullifier registry failures."""


class InviteNullifierRegistry:
    """Local registry of observed invite redemption nullifiers.

    LOCAL ONLY. Cross-node propagation via D2D gossip is Phase 1576p-b
    (SENSITIVE). This registry provides same-process replay detection only.
    """

    _MAX_REGISTRY_SIZE = _MAX_REGISTRY_SIZE

    def __init__(self) -> None:
        self._nullifiers: set[str] = set()
        self._lock = threading.Lock()

    def register_nullifier(self, nullifier_hex: str) -> None:
        """Record a nullifier. Raises InviteNullifierError if registry is full."""
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        with self._lock:
            if len(self._nullifiers) >= self._MAX_REGISTRY_SIZE and nullifier_hex not in self._nullifiers:
                raise InviteNullifierError("invite_nullifier_registry_full")
            self._nullifiers.add(nullifier_hex)

    def register_if_new(self, nullifier_hex: str) -> bool:
        """Atomically register a nullifier, returning False for duplicates."""
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        with self._lock:
            if nullifier_hex in self._nullifiers:
                return False
            if len(self._nullifiers) >= self._MAX_REGISTRY_SIZE:
                raise InviteNullifierError("invite_nullifier_registry_full")
            self._nullifiers.add(nullifier_hex)
            return True

    def discard_nullifier(self, nullifier_hex: str) -> None:
        """Remove a nullifier during same-process rollback."""
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        with self._lock:
            self._nullifiers.discard(nullifier_hex)

    def is_known(self, nullifier_hex: str) -> bool:
        """Return True if this nullifier has already been seen locally."""
        _require_sha256_hex(nullifier_hex, "invite_nullifier_invalid")
        with self._lock:
            return nullifier_hex in self._nullifiers

    def __len__(self) -> int:
        with self._lock:
            return len(self._nullifiers)


def _require_sha256_hex(value: object, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != _SHA256_HEX_CHARS
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise InviteNullifierError(token)


__all__ = [
    "INVITE_NULLIFIER_REGISTRY_VERSION",
    "InviteNullifierError",
    "InviteNullifierRegistry",
    "_MAX_REGISTRY_SIZE",
]
