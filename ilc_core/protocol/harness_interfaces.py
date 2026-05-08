"""Pure harness adapter interfaces for package-boundary injection.

The interfaces in this module are structural contracts only. They do not open
network connections, own storage, parse CLI arguments, or select a concrete
harness implementation. Agentic harnesses such as OpenClaw/NemoClaw can satisfy
these Protocols with their own transport and persistence layers.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

HARNESS_INTERFACES_VERSION = "harness_interfaces_1244.v0.1"


@runtime_checkable
class TransportHarness(Protocol):
    """Structural contract for harness-owned payload transport."""

    def publish_payload(
        self,
        *,
        channel: str,
        payload: bytes,
        epoch: int,
        metadata: Mapping[str, str] | None = None,
    ) -> str:
        """Publish a payload through the harness and return its address."""

    def fetch_payload(
        self,
        *,
        address: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        """Fetch a bounded payload by harness address."""


@runtime_checkable
class StorageHarness(Protocol):
    """Structural contract for harness-owned byte persistence."""

    def put_payload(
        self,
        *,
        key: str,
        payload: bytes,
        epoch: int,
        metadata: Mapping[str, str] | None = None,
    ) -> str:
        """Store a payload through the harness and return its storage key."""

    def get_payload(
        self,
        *,
        key: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        """Load a bounded payload by storage key."""

    def has_payload(
        self,
        *,
        key: str,
        epoch: int,
    ) -> bool:
        """Return whether the harness-owned store contains a key."""


__all__ = [
    "HARNESS_INTERFACES_VERSION",
    "StorageHarness",
    "TransportHarness",
]
