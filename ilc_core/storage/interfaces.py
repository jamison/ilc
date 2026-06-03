# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class GraphStore(Protocol):
    def put_node(self, node_id: str, payload: dict[str, Any]) -> None:
        ...

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        ...

    def iter_nodes(self) -> list[dict[str, Any]]:
        ...

    def put_link(self, link_id: str, payload: dict[str, Any]) -> None:
        ...

    def get_link(self, link_id: str) -> dict[str, Any] | None:
        ...

    def iter_links(self) -> list[dict[str, Any]]:
        ...

    def put_quorum_record(self, payload: dict[str, Any]) -> None:
        ...

    def get_quorum_record(self) -> dict[str, Any] | None:
        ...


@runtime_checkable
class WalletStore(Protocol):
    def put_wallet(self, agent_id: str, payload: dict[str, Any]) -> None:
        ...

    def get_wallet(self, agent_id: str) -> dict[str, Any] | None:
        ...

    def iter_wallets(self) -> dict[str, dict[str, Any]]:
        ...

    def put_wallet_history(self, agent_id: str, payload: dict[str, Any]) -> None:
        ...

    def get_wallet_history(self, agent_id: str) -> dict[str, Any] | None:
        ...
