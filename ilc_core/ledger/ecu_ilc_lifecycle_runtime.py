# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 652 bounded ECU/ILC lifecycle runtime."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    parse_non_negative_decimal,
    to_decimal,
)
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


ECU_ILC_LIFECYCLE_RUNTIME_VERSION = "ecu_ilc_lifecycle_runtime_652.v0.1"


class EcuIlcLifecycleRuntimeError(ValueError):
    """Fail-closed lifecycle error with machine token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


class EcuIlcLifecycleRuntime:
    def __init__(
        self,
        *,
        wallet_store: LmdbWalletStore,
        ecu_runtime: EcuActiveLayerRuntime,
    ) -> None:
        self.wallet_store = wallet_store
        self.ecu_runtime = ecu_runtime

    def lifecycle_status(self, *, agent_id: str) -> dict[str, Any]:
        snapshot = self.lifecycle_snapshot(agent_id=agent_id)
        return {
            "ok": True,
            "token": "lifecycle_visibility_found",
            "data": snapshot["data"],
        }

    def lifecycle_snapshot(self, *, agent_id: str) -> dict[str, Any]:
        wallet_row = self.wallet_store.get_wallet(agent_id) or {}
        wallet_history = self.wallet_store.get_wallet_history(agent_id) or {}
        latest_balance_receipt = wallet_row.get("latest_balance_receipt")
        if not isinstance(latest_balance_receipt, dict):
            latest_balance_receipt = None
        return {
            "wallet_row": wallet_row,
            "wallet_history": wallet_history,
            "data": {
                "agent_id": agent_id,
                "balance_ecu": self.ecu_runtime.get_accrued_ecu(agent_id),
                "balance_ilc": _wallet_decimal_string(wallet_row.get("balance_ilc", "0")),
                "last_settled_epoch_id": wallet_row.get("last_settled_epoch_id"),
                "reward_status": wallet_row.get("reward_status", "not_rewarded"),
                "history_digest": wallet_history.get("history_digest"),
                "latest_balance_receipt": latest_balance_receipt,
                "claimability_state": "deferred",
            },
        }

    def commit_settled_epoch(
        self,
        *,
        agent_id: str,
        epoch_id: str,
        reward_delta_ilc: int | float | str | Decimal,
    ) -> dict[str, Any]:
        if not isinstance(epoch_id, str) or not epoch_id.strip():
            raise EcuIlcLifecycleRuntimeError("epoch_id_required", "epoch_id must be a non-empty string")

        try:
            reward_delta_decimal = parse_non_negative_decimal(
                reward_delta_ilc,
                token="lifecycle_reward_delta_invalid",
            )
        except ValueError as exc:
            raise EcuIlcLifecycleRuntimeError("lifecycle_reward_delta_invalid", str(exc)) from exc

        wallet_row = self.wallet_store.get_wallet(agent_id) or {}
        wallet_history = self.wallet_store.get_wallet_history(agent_id) or {}
        balance_history = wallet_history.get("balance_history")
        if not isinstance(balance_history, list):
            balance_history = []

        existing_entry = next(
            (
                item
                for item in balance_history
                if isinstance(item, dict) and item.get("epoch_id") == epoch_id
            ),
            None,
        )
        if existing_entry is not None:
            existing_delta = decimal_to_canonical_string(
                to_decimal(
                    existing_entry.get("reward_delta_ilc", "0"),
                    token="lifecycle_reward_delta_invalid",
                )
            )
            requested_delta = decimal_to_canonical_string(reward_delta_decimal)
            if existing_delta != requested_delta:
                raise EcuIlcLifecycleRuntimeError(
                    "lifecycle_epoch_replay_conflict",
                    "epoch_id replay conflicts with existing reward delta",
                )
            current_wallet_row = self.wallet_store.get_wallet(agent_id) or {
                "agent_id": agent_id,
                "balance_ilc": "0",
                "last_settled_epoch_id": epoch_id,
                "reward_status": "not_rewarded",
                "history_digest": wallet_history.get("history_digest"),
                "latest_balance_receipt": existing_entry,
                "claimability_state": "deferred",
            }
            return {
                "ok": True,
                "token": "lifecycle_epoch_commit_idempotent_replay",
                "data": current_wallet_row,
            }

        prior_balance = to_decimal(
            wallet_row.get("balance_ilc", "0"),
            token="lifecycle_wallet_balance_invalid",
        )
        balance_after = prior_balance + reward_delta_decimal
        latest_balance_receipt = {
            "epoch_id": epoch_id,
            "reward_delta_ilc": decimal_to_canonical_string(reward_delta_decimal),
            "balance_after_ilc": decimal_to_canonical_string(balance_after),
            "settlement_status": "applied",
        }
        merged_balance_history = [
            item
            for item in balance_history
            if isinstance(item, dict) and item.get("epoch_id") != epoch_id
        ]
        merged_balance_history.append(latest_balance_receipt)
        merged_balance_history.sort(key=lambda item: str(item.get("epoch_id", "")))
        history_digest = _stable_digest({"balance_history": merged_balance_history})

        next_wallet_row = {
            "agent_id": agent_id,
            "balance_ilc": decimal_to_canonical_string(balance_after),
            "last_settled_epoch_id": epoch_id,
            "reward_status": "rewarded" if balance_after > ZERO else "not_rewarded",
            "history_digest": history_digest,
            "latest_balance_receipt": latest_balance_receipt,
            "claimability_state": "deferred",
        }
        next_wallet_history = {
            "agent_id": agent_id,
            "balance_history": merged_balance_history,
            "history_digest": history_digest,
        }
        self.wallet_store.put_wallet(agent_id, next_wallet_row)
        self.wallet_store.put_wallet_history(agent_id, next_wallet_history)
        return {
            "ok": True,
            "token": "lifecycle_epoch_commit_applied",
            "data": next_wallet_row,
        }

    def coupling_invariants_diagnostic(self, *, graph_node_count: int) -> dict[str, Any]:
        return {
            "ok": True,
            "token": "coupling_invariants_diagnostic",
            "data": {
                "graph_truth_upstream": True,
                "graph_truth_node_count": int(graph_node_count),
                "ecu_accounting_source": "ecu_active_layer_runtime",
                "delayed_visible_ilc_source": "lmdb_wallet_store",
                "delayed_ilc_requires_epoch_commit": True,
                "ordering": [
                    "graph_truth",
                    "ecu_accounting",
                    "delayed_visible_ilc",
                ],
                "governance_lock_closed": False,
                "diagnostic_only": True,
            },
        }


def _stable_digest(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _wallet_decimal_string(value: object) -> str:
    return decimal_to_canonical_string(
        to_decimal(value if value is not None else "0", token="lifecycle_wallet_balance_invalid")
    )


__all__ = [
    "ECU_ILC_LIFECYCLE_RUNTIME_VERSION",
    "EcuIlcLifecycleRuntime",
    "EcuIlcLifecycleRuntimeError",
]
