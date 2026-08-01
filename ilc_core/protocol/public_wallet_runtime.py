# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 653 bounded public wallet runtime integration."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.ledger.exact_numeric import ZERO, decimal_to_canonical_string, to_decimal
from ilc_core.protocol.harness_interfaces import PublicWalletStore


PUBLIC_WALLET_RUNTIME_VERSION = "public_wallet_runtime_653.v0.1"
WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED = "proof_claimability_authorized"


class PublicWalletRuntimeError(ValueError):
    """Fail-closed public wallet runtime error with machine token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


class PublicWalletRuntime:
    def __init__(
        self,
        *,
        wallet_store: PublicWalletStore,
        lifecycle_runtime: EcuIlcLifecycleRuntime,
    ) -> None:
        self.wallet_store = wallet_store
        self.lifecycle_runtime = lifecycle_runtime

    def wallet_status(self, *, agent_id: str) -> dict[str, Any]:
        snapshot = self._wallet_snapshot(agent_id=agent_id)
        return {
            "ok": True,
            "token": "wallet_status_found",
            "data": snapshot["status"],
        }

    def wallet_history(self, *, agent_id: str) -> dict[str, Any]:
        snapshot = self._wallet_snapshot(agent_id=agent_id)
        status_data = snapshot["status"]
        balance_history = snapshot["records"]
        return {
            "ok": True,
            "token": "wallet_history_found",
            "data": {
                "agent_id": agent_id,
                "records": balance_history,
                "record_count": len(balance_history),
                "history_digest": status_data.get("history_digest"),
                "latest_balance_receipt_ref": status_data.get("latest_balance_receipt_ref"),
                "settled_runtime_root_ref": status_data["settled_runtime_root_ref"],
                "claimability_state": WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED,
            },
        }

    def wallet_export(self, *, agent_id: str) -> dict[str, Any]:
        snapshot = self._wallet_snapshot(agent_id=agent_id)
        status_data = snapshot["status"]
        history_data = {
            "history_digest": snapshot["history_digest"],
        }
        return {
            "ok": True,
            "token": "wallet_export_found",
            "data": {
                "agent_id": agent_id,
                "export_epoch": status_data.get("last_settled_epoch_id"),
                "settled_balance_ilc": status_data["balance_ilc"],
                "ecu_accrual": status_data["ecu_accrual"],
                "history_digest": history_data.get("history_digest"),
                "latest_balance_receipt_ref": status_data.get("latest_balance_receipt_ref"),
                "settled_runtime_root_ref": status_data["settled_runtime_root_ref"],
                "claimability_state": WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED,
                "wallet_store_kind": "lmdb_wallet_store",
            },
        }

    def ledger_summary(self, *, agent_id: str) -> dict[str, Any]:
        snapshot = self._wallet_snapshot(agent_id=agent_id)
        status_data = snapshot["status"]
        reward_total = sum(
            (
                to_decimal(record["settled_amount_ilc"], token="wallet_history_invalid")
                for record in snapshot["records"]
            ),
            ZERO,
        )
        return {
            "ok": True,
            "token": "ledger_summary_found",
            "data": {
                "agent_id": agent_id,
                "settled_balance_ilc": status_data["balance_ilc"],
                "reward_total_ilc": decimal_to_canonical_string(reward_total),
                "epoch_record_count": len(snapshot["records"]),
                "latest_epoch_id": status_data.get("last_settled_epoch_id"),
                "history_digest": snapshot["history_digest"],
                "latest_balance_receipt_ref": status_data.get("latest_balance_receipt_ref"),
                "settled_runtime_root_ref": status_data["settled_runtime_root_ref"],
                "claimability_state": WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED,
                "wallet_store_kind": "lmdb_wallet_store",
            },
        }

    def _wallet_snapshot(self, *, agent_id: str) -> dict[str, Any]:
        agent_id = _require_agent_id(agent_id)
        lifecycle_snapshot = self.lifecycle_runtime.lifecycle_snapshot(agent_id=agent_id)
        lifecycle_data = lifecycle_snapshot["data"]
        latest_balance_receipt = lifecycle_data.get("latest_balance_receipt")
        records = self._balance_history(payload=lifecycle_snapshot.get("wallet_history"))
        settled_runtime_root_ref = self._settled_runtime_root_ref(
            agent_id=agent_id,
            lifecycle_data=lifecycle_data,
            records=records,
        )
        latest_balance_receipt_ref = _payload_ref(
            prefix="balance_receipt_sha256",
            payload=latest_balance_receipt,
        )
        status = {
            "agent_id": agent_id,
            "balance_ilc": lifecycle_data["balance_ilc"],
            "ecu_accrual": lifecycle_data["balance_ecu"],
            "claimability_state": WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED,
            "last_settled_epoch_id": lifecycle_data.get("last_settled_epoch_id"),
            "history_digest": lifecycle_data.get("history_digest"),
            "latest_balance_receipt": latest_balance_receipt,
            "latest_balance_receipt_ref": latest_balance_receipt_ref,
            "settled_runtime_root_ref": settled_runtime_root_ref,
            "wallet_store_kind": "lmdb_wallet_store",
        }
        return {
            "status": status,
            "records": records,
            "history_digest": lifecycle_data.get("history_digest"),
        }

    def _balance_history(self, *, payload: dict[str, Any] | None) -> list[dict[str, Any]]:
        payload = payload or {}
        balance_history = payload.get("balance_history", [])
        if not isinstance(balance_history, list):
            raise PublicWalletRuntimeError("wallet_history_invalid", "balance_history must be a list")
        records: list[dict[str, Any]] = []
        for item in balance_history:
            if not isinstance(item, dict):
                raise PublicWalletRuntimeError("wallet_history_invalid", "balance_history entries must be objects")
            epoch_id = item.get("epoch_id")
            reward_delta_ilc = item.get("reward_delta_ilc")
            if not isinstance(epoch_id, str) or not epoch_id.strip():
                raise PublicWalletRuntimeError("wallet_history_invalid", "epoch_id missing from balance_history entry")
            settled_amount_ilc = decimal_to_canonical_string(
                to_decimal(reward_delta_ilc if reward_delta_ilc is not None else "0", token="wallet_history_invalid")
            )
            records.append(
                {
                    "epoch_id": epoch_id,
                    "settled_amount_ilc": settled_amount_ilc,
                    "attribution_snapshot_ref": _payload_ref(
                        prefix="attribution_snapshot_sha256",
                        payload=item,
                    ),
                    "balance_after_ilc": item.get("balance_after_ilc", "0"),
                    "receipt_ref": _payload_ref(prefix="balance_receipt_sha256", payload=item),
                }
            )
        return sorted(records, key=lambda record: str(record["epoch_id"]))

    def _settled_runtime_root_ref(
        self,
        *,
        agent_id: str,
        lifecycle_data: dict[str, Any],
        records: list[dict[str, Any]],
    ) -> str:
        payload = {
            "agent_id": agent_id,
            "balance_ilc": lifecycle_data["balance_ilc"],
            "balance_ecu": lifecycle_data["balance_ecu"],
            "last_settled_epoch_id": lifecycle_data.get("last_settled_epoch_id"),
            "history_digest": lifecycle_data.get("history_digest"),
            "records": records,
            "latest_balance_receipt": lifecycle_data.get("latest_balance_receipt"),
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest()
        return f"wallet_state_sha256:{digest}"


def _require_agent_id(agent_id: str) -> str:
    if not isinstance(agent_id, str) or not agent_id.strip():
        raise PublicWalletRuntimeError("wallet_agent_id_required", "agent_id must be a non-empty string")
    return agent_id


def _payload_ref(*, prefix: str, payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    return f"{prefix}:{digest}"


__all__ = [
    "PUBLIC_WALLET_RUNTIME_VERSION",
    "PublicWalletRuntime",
    "PublicWalletRuntimeError",
    "WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED",
]
