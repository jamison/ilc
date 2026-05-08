"""Pure harness adapter interfaces for package-boundary injection.

The interfaces in this module are structural contracts only. They do not open
network connections, own storage, parse CLI arguments, or select a concrete
harness implementation. Agentic harnesses such as OpenClaw/NemoClaw can satisfy
these Protocols with their own transport and persistence layers.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

HARNESS_INTERFACES_VERSION = "harness_interfaces_1244.v0.1"
PUBLIC_RUNTIME_STORE_INTERFACES_VERSION = "public_runtime_store_interfaces_1250.v0.1"
GAP14_ADAPTER_EXTRACTION_VERSION = "gap14_adapter_extraction_phase_1250.v0.1"


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


@runtime_checkable
class AdmissionReceiptStore(Protocol):
    """Structural contract for public admission receipt persistence."""

    def put_admission_receipt(self, receipt_id: str, payload: dict[str, Any]) -> None:
        """Persist an admission receipt."""

    def get_admission_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        """Load an admission receipt by id."""


@runtime_checkable
class PublicReceiptStore(Protocol):
    """Structural contract for public receipt persistence and indexes."""

    def put_receipt(self, receipt_id: str, payload: dict[str, Any]) -> None:
        """Persist a public receipt."""

    def get_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        """Load a public receipt by id."""

    def get_receipts_by_signer(self, signer_agent_id: str) -> list[dict[str, Any]]:
        """Load receipts for a signer."""

    def get_receipts_by_artifact_epoch(
        self,
        artifact_kind: str,
        epoch_id: str,
    ) -> list[dict[str, Any]]:
        """Load receipts for an artifact kind and epoch."""


@runtime_checkable
class PublicWalletStore(Protocol):
    """Structural contract for read-only public wallet/lifecycle storage."""

    def get_wallet(self, agent_id: str) -> dict[str, Any] | None:
        """Load a wallet row."""

    def get_wallet_history(self, agent_id: str) -> dict[str, Any] | None:
        """Load wallet history."""


@runtime_checkable
class TruthPrimitiveGraphPersistence(Protocol):
    """Structural contract for CDL-075 truth primitive graph persistence."""

    def put_node_if_absent(self, node_id: str, record: dict[str, Any]) -> bool:
        """Persist a node if not already present."""

    def put_edge_if_absent(self, edge_key: str, record: dict[str, Any]) -> bool:
        """Persist an edge if not already present."""

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Load a node record."""

    def get_edge(self, edge_key: str) -> dict[str, Any] | None:
        """Load an edge record."""

    def iter_nodes(self) -> list[dict[str, Any]]:
        """Return all node records."""

    def iter_edges(self) -> list[dict[str, Any]]:
        """Return all edge records."""


__all__ = [
    "AdmissionReceiptStore",
    "GAP14_ADAPTER_EXTRACTION_VERSION",
    "HARNESS_INTERFACES_VERSION",
    "PUBLIC_RUNTIME_STORE_INTERFACES_VERSION",
    "PublicReceiptStore",
    "PublicWalletStore",
    "StorageHarness",
    "TruthPrimitiveGraphPersistence",
    "TransportHarness",
]
