# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 652 bounded ECU/ILC lifecycle runtime."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

from ilc_core.consensus.attribution_batch_bridge import read_rust_balance_store_ecu
from ilc_core.economic_constants import C_MAX_ILC, ILC_QUANTUM
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    parse_non_negative_decimal,
    to_decimal,
)
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


ECU_ILC_LIFECYCLE_RUNTIME_VERSION = "ecu_ilc_lifecycle_runtime_652.v0.1"
LIFECYCLE_C_MAX_ILC = C_MAX_ILC
LIFECYCLE_BALANCE_EXCEEDS_C_MAX_TOKEN = "lifecycle_balance_exceeds_c_max"
LIFECYCLE_MAX_AGENT_ID_BYTES = 256
LIFECYCLE_MAX_EPOCH_ID_BYTES = 64
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")


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
        consensus_lmdb: str | Path | None = None,
        rust_balance_binary: str | Path | None = None,
    ) -> None:
        self.wallet_store = wallet_store
        self.ecu_runtime = ecu_runtime
        self.consensus_lmdb = Path(consensus_lmdb) if consensus_lmdb is not None else None
        self.rust_balance_binary = (
            Path(rust_balance_binary) if rust_balance_binary is not None else None
        )

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
        pending_balance_ecu = self.ecu_runtime.get_accrued_ecu(agent_id)
        balance_ecu = pending_balance_ecu
        balance_ecu_source = "python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597"
        snapshot_extra: dict[str, Any] = {}
        if self.consensus_lmdb is not None:
            balance_ecu = decimal_to_canonical_string(
                read_rust_balance_store_ecu(
                    self.consensus_lmdb,
                    agent_id,
                    rust_binary=self.rust_balance_binary,
                )
            )
            balance_ecu_source = "rust_balance_store_committed_aggregate"
            snapshot_extra["balance_ecu_pending"] = pending_balance_ecu
        return {
            "wallet_row": wallet_row,
            "wallet_history": wallet_history,
            "data": {
                "agent_id": agent_id,
                "balance_ecu": balance_ecu,
                "balance_ecu_source": balance_ecu_source,
                "balance_ilc": _wallet_decimal_string(wallet_row.get("balance_ilc", "0")),
                "last_settled_epoch_id": wallet_row.get("last_settled_epoch_id"),
                "reward_status": wallet_row.get("reward_status", "not_rewarded"),
                "history_digest": wallet_history.get("history_digest"),
                "latest_balance_receipt": latest_balance_receipt,
                "claimability_state": _claimability_state(wallet_row),
                **snapshot_extra,
            },
        }

    def commit_settled_epoch(
        self,
        *,
        agent_id: str,
        epoch_id: str,
        reward_delta_ilc: int | str | Decimal,
    ) -> dict[str, Any]:
        _require_lifecycle_agent_id(
            agent_id,
            token="agent_id_required",
            max_bytes=LIFECYCLE_MAX_AGENT_ID_BYTES,
        )
        _require_lifecycle_id(
            epoch_id,
            token="epoch_id_required",
            max_bytes=LIFECYCLE_MAX_EPOCH_ID_BYTES,
            label="epoch_id",
        )

        try:
            reward_delta_decimal = parse_non_negative_decimal(
                reward_delta_ilc,
                token="lifecycle_reward_delta_invalid",
            )
        except ValueError as exc:
            raise EcuIlcLifecycleRuntimeError("lifecycle_reward_delta_invalid", str(exc)) from exc
        if reward_delta_decimal % ILC_QUANTUM != ZERO:
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_reward_delta_invalid",
                "reward delta must align to ILC quantum",
            )
        if reward_delta_decimal == ZERO:
            raise EcuIlcLifecycleRuntimeError(
                "lifecycle_reward_delta_must_be_positive",
                "reward delta must be positive for direct lifecycle commits",
            )

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
        if balance_after > LIFECYCLE_C_MAX_ILC:
            raise EcuIlcLifecycleRuntimeError(
                LIFECYCLE_BALANCE_EXCEEDS_C_MAX_TOKEN,
                "wallet balance cannot exceed the constitutional C_MAX_ILC ceiling",
            )
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
        merged_balance_history.sort(key=_epoch_history_sort_key)
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
        self.wallet_store.put_wallet_and_history(agent_id, next_wallet_row, next_wallet_history)
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
    _reject_decimal_tree(payload)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _epoch_history_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    epoch_id = str(item.get("epoch_id", ""))
    if epoch_id.isdecimal():
        return (0, int(epoch_id), epoch_id)
    return (1, 0, epoch_id)


def _reject_decimal_tree(value: Any) -> None:
    if isinstance(value, Decimal):
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_stable_digest_decimal_unencoded",
            "stable digest payloads must encode Decimal values as canonical strings",
        )
    if isinstance(value, float):
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_stable_digest_float_unencoded",
            "stable digest payloads must encode exact numeric values as canonical strings",
        )
    if isinstance(value, dict):
        for item in value.values():
            _reject_decimal_tree(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_decimal_tree(item)


def _wallet_decimal_string(value: object) -> str:
    return decimal_to_canonical_string(
        to_decimal(value if value is not None else "0", token="lifecycle_wallet_balance_invalid")
    )


def _claimability_state(wallet_row: dict[str, Any]) -> str:
    value = wallet_row.get("claimability_state", "deferred")
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise EcuIlcLifecycleRuntimeError(
            "lifecycle_claimability_state_invalid",
            "claimability_state must be a non-empty string",
        )
    return value


def _require_lifecycle_id(value: object, *, token: str, max_bytes: int, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise EcuIlcLifecycleRuntimeError(token, f"{label} must be a non-empty string")
    if len(value.encode("utf-8")) > max_bytes:
        raise EcuIlcLifecycleRuntimeError(token, f"{label} exceeds maximum byte length")
    return value


def _require_lifecycle_agent_id(value: object, *, token: str, max_bytes: int) -> str:
    agent_id = _require_lifecycle_id(
        value,
        token=token,
        max_bytes=max_bytes,
        label="agent_id",
    )
    if _AGENT_ID_RE.fullmatch(agent_id) is None:
        raise EcuIlcLifecycleRuntimeError(token, "agent_id must be 96 lowercase hex")
    return agent_id


__all__ = [
    "ECU_ILC_LIFECYCLE_RUNTIME_VERSION",
    "LIFECYCLE_BALANCE_EXCEEDS_C_MAX_TOKEN",
    "LIFECYCLE_C_MAX_ILC",
    "LIFECYCLE_MAX_AGENT_ID_BYTES",
    "LIFECYCLE_MAX_EPOCH_ID_BYTES",
    "EcuIlcLifecycleRuntime",
    "EcuIlcLifecycleRuntimeError",
]
