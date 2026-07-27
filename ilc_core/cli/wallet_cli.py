# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only wallet query CLI handlers for Phase 1578g."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import lmdb

from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime, PublicWalletRuntimeError


WALLET_CLI_VERSION = "wallet_cli_1578g.v0.1"
DEFAULT_WALLET_STORE_PATH = Path("out/public_runtime/wallet")
IDENTITY_STATUS = "agent_id_account_anchor_queryable"
_WALLETS_DB = b"wallets"
_WALLET_HISTORY_DB = b"wallet_history"


class WalletCliError(ValueError):
    """Typed wallet CLI error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(f"{token}: {message}")
        self.token = token
        self.message = message


def run_wallet_command(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = str(getattr(args, "wallet_subcommand", "") or "")
    output_format = str(getattr(args, "format", "json") or "json")
    if output_format not in {"json", "text"}:
        raise WalletCliError("wallet_cli_format_invalid", "format must be json or text")

    agent_id = _agent_id_from_args(args)
    if subcommand == "identity":
        payload = _identity_payload(agent_id)
    elif subcommand in {"status", "history"}:
        payload = _runtime_payload(
            agent_id=agent_id,
            wallet_store_path=_wallet_store_path(args),
            subcommand=subcommand,
        )
    else:
        raise WalletCliError("wallet_cli_subcommand_missing", "wallet subcommand is required")

    return _render_payload(payload, output_format=output_format)


def _runtime_payload(*, agent_id: str, wallet_store_path: Path, subcommand: str) -> dict[str, Any]:
    if not wallet_store_path.exists():
        raise WalletCliError(
            "wallet_cli_store_missing",
            f"wallet store path does not exist: {wallet_store_path}",
        )

    wallet_store = _ReadOnlyWalletStore(wallet_store_path)
    try:
        lifecycle_runtime = EcuIlcLifecycleRuntime(
            wallet_store=wallet_store,
            ecu_runtime=EcuActiveLayerRuntime(),
        )
        runtime = PublicWalletRuntime(
            wallet_store=wallet_store,
            lifecycle_runtime=lifecycle_runtime,
        )
        if subcommand == "status":
            result = runtime.wallet_status(agent_id=agent_id)
        else:
            result = runtime.wallet_history(agent_id=agent_id)
    except PublicWalletRuntimeError as exc:
        raise WalletCliError(exc.token, exc.args[0] if exc.args else exc.token) from exc
    finally:
        wallet_store.close()

    data = result["data"]
    return {
        "ok": True,
        "subcommand": subcommand,
        "version": WALLET_CLI_VERSION,
        "read_only": True,
        "agent_id": agent_id,
        "data": data,
    }


def _identity_payload(agent_id: str) -> dict[str, Any]:
    return {
        "ok": True,
        "subcommand": "identity",
        "version": WALLET_CLI_VERSION,
        "read_only": True,
        "agent_id": agent_id,
        "data": {
            "agent_id": agent_id,
            "account_anchor": "agent_id",
            "enrollment_status": IDENTITY_STATUS,
            "identity_derivation_rule": "see_phase_1578a_agent_identity_enrollment_spec",
            "signer_binding_status": "deferred",
            "operator_delegation_status": "preflight_only",
        },
    }


def _agent_id_from_args(args: argparse.Namespace) -> str:
    agent_id = str(getattr(args, "agent_id", "") or os.environ.get("ILC_AGENT_ID", "") or "").strip()
    if not agent_id:
        raise WalletCliError("wallet_cli_agent_id_required", "agent_id is required")
    return agent_id


def _wallet_store_path(args: argparse.Namespace) -> Path:
    configured = str(
        getattr(args, "wallet_store", "")
        or os.environ.get("ILC_WALLET_STORE_PATH", "")
        or DEFAULT_WALLET_STORE_PATH
    )
    return Path(configured)


def _render_payload(payload: dict[str, Any], *, output_format: str) -> dict[str, Any]:
    if output_format == "json":
        return {
            "_raw": json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False),
        }
    return {
        "_raw": _format_text(payload),
    }


class _ReadOnlyWalletStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        try:
            self.env = lmdb.open(
                str(root.resolve()),
                create=False,
                lock=False,
                max_dbs=2,
                readonly=True,
                subdir=True,
            )
            self._dbs = {
                _WALLETS_DB: self.env.open_db(_WALLETS_DB, create=False),
                _WALLET_HISTORY_DB: self.env.open_db(_WALLET_HISTORY_DB, create=False),
            }
        except lmdb.Error as exc:
            raise WalletCliError("wallet_cli_store_unreadable", str(exc)) from exc

    def get_wallet(self, agent_id: str) -> dict[str, Any] | None:
        payload = self._get_json(_WALLETS_DB, agent_id)
        return payload if isinstance(payload, dict) else None

    def get_wallet_history(self, agent_id: str) -> dict[str, Any] | None:
        payload = self._get_json(_WALLET_HISTORY_DB, agent_id)
        return payload if isinstance(payload, dict) else None

    def close(self) -> None:
        self.env.close()

    def _get_json(self, db_name: bytes, key: str) -> Any:
        with self.env.begin(db=self._dbs[db_name]) as txn:
            row = txn.get(key.encode("utf-8"))
        if row is None:
            return None
        return json.loads(row.decode("utf-8"))


def _format_text(payload: dict[str, Any]) -> str:
    data = payload["data"]
    lines = [
        f"wallet {payload['subcommand']}",
        f"agent-id: {payload['agent_id']}",
        f"read-only: {str(payload['read_only']).lower()}",
    ]
    for key in sorted(data):
        value = data[key]
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines)


__all__ = [
    "DEFAULT_WALLET_STORE_PATH",
    "IDENTITY_STATUS",
    "WALLET_CLI_VERSION",
    "WalletCliError",
    "run_wallet_command",
]
