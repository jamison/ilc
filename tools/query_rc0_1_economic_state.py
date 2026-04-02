#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.ledger.lmdb_backend import LmdbLedgerBackend
from ilc_core.storage.lmdb_public_runtime import LmdbGraphStore, LmdbWalletStore


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_root(manifest_path: Path) -> Path:
    if manifest_path.name == "manifest.json":
        return manifest_path.parent
    raise ValueError("economic_manifest_path_invalid")


def _load_state(manifest_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = _load_json(manifest_path)
    runtime_store = manifest.get("runtime_store")
    if isinstance(runtime_store, dict):
        graph_store_root = runtime_store.get("graph_store_root")
        wallet_store_root = runtime_store.get("wallet_store_root")
        ledger_store_root = runtime_store.get("ledger_store_root")
        if all(isinstance(value, str) and value for value in (graph_store_root, wallet_store_root, ledger_store_root)):
            graph_store = LmdbGraphStore(Path(graph_store_root))
            wallet_store = LmdbWalletStore(Path(wallet_store_root))
            ledger_backend = LmdbLedgerBackend(Path(ledger_store_root))
            nodes = graph_store.iter_nodes()
            links = graph_store.iter_links()
            wallets = {"wallets": wallet_store.iter_wallets()}
            ledger = {
                "balances": dict(sorted(ledger_backend.balances.items())),
                "epoch_records": ledger_backend.epoch_records,
            }
            return manifest, nodes, links, wallets, ledger
    root = _manifest_root(manifest_path)
    nodes = _load_json(root / "graph" / "nodes.json")
    links = _load_json(root / "graph" / "links.json")
    wallets = _load_json(root / "economy" / "wallets.json")
    ledger = _load_json(root / "economy" / "ledger_state.json")
    return manifest, nodes, links, wallets, ledger


def _load_claims(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    scenario_root = manifest.get("scenario_root")
    if not isinstance(scenario_root, str) or not scenario_root:
        return []
    claims_path = Path(scenario_root) / "panel" / "ecu_claims.json"
    if not claims_path.is_file():
        return []
    claims_payload = _load_json(claims_path)
    claims = claims_payload.get("claims")
    if not isinstance(claims, list):
        return []
    return [row for row in claims if isinstance(row, dict)]


def query_summary(manifest_path: Path) -> dict[str, Any]:
    manifest, _nodes, _links, wallets, ledger = _load_state(manifest_path)
    summary = manifest.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "ok": True,
        "data": {
            "summary": summary,
            "task_id": summary.get("task_id"),
            "distribution_check_ok": summary.get("distribution_check_ok"),
            "reward_total": summary.get("reward_total"),
            "node_count": summary.get("node_count"),
            "support_link_count": summary.get("support_link_count"),
            "wallet_count": len(wallets.get("wallets", {})),
            "balance_count": len(ledger.get("balances", {})),
        },
    }


def query_wallets(manifest_path: Path, agent_id: str | None) -> dict[str, Any]:
    manifest, _nodes, _links, wallets, _ledger = _load_state(manifest_path)
    wallet_rows = wallets.get("wallets", {})
    if not isinstance(wallet_rows, dict):
        raise ValueError("wallet_rows_invalid")
    if agent_id is not None:
        row = wallet_rows.get(agent_id)
        if row is None:
            raise ValueError(f"wallet_agent_missing:{agent_id}")
        return {"ok": True, "data": {"agent_id": agent_id, "wallet": row, "summary": manifest.get("summary", {})}}
    return {"ok": True, "data": {"wallets": wallet_rows, "summary": manifest.get("summary", {})}}


def query_wallet_history(manifest_path: Path, agent_id: str) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    runtime_store = manifest.get("runtime_store")
    if isinstance(runtime_store, dict):
        wallet_store_root = runtime_store.get("wallet_store_root")
        ledger_store_root = runtime_store.get("ledger_store_root")
        if isinstance(wallet_store_root, str) and wallet_store_root and isinstance(ledger_store_root, str) and ledger_store_root:
            wallet_store = LmdbWalletStore(Path(wallet_store_root))
            ledger_backend = LmdbLedgerBackend(Path(ledger_store_root))
            row = wallet_store.get_wallet(agent_id)
            if row is None:
                raise ValueError(f"wallet_agent_missing:{agent_id}")
            history = wallet_store.get_wallet_history(agent_id) or {}
            return {
                "ok": True,
                "data": {
                    "agent_id": agent_id,
                    "wallet": row,
                    "claim_history": history.get("claim_history", []),
                    "epoch_history": history.get("epoch_history", list(ledger_backend.epoch_records.values())),
                    "summary": manifest.get("summary", {}),
                },
            }
    manifest, _nodes, _links, wallets, ledger = _load_state(manifest_path)
    wallet_rows = wallets.get("wallets", {})
    if not isinstance(wallet_rows, dict):
        raise ValueError("wallet_rows_invalid")
    row = wallet_rows.get(agent_id)
    if row is None:
        raise ValueError(f"wallet_agent_missing:{agent_id}")
    claims = [claim for claim in _load_claims(manifest) if claim.get("agent_id") == agent_id]
    epoch_records = ledger.get("epoch_records", {})
    if not isinstance(epoch_records, dict):
        epoch_records = {}
    return {
        "ok": True,
        "data": {
            "agent_id": agent_id,
            "wallet": row,
            "claim_history": claims,
            "epoch_history": list(epoch_records.values()),
            "summary": manifest.get("summary", {}),
        },
    }


def query_graph(manifest_path: Path, node_id: str | None) -> dict[str, Any]:
    manifest, nodes, links, _wallets, _ledger = _load_state(manifest_path)
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise ValueError("graph_state_invalid")
    if node_id is None:
        return {
            "ok": True,
            "data": {
                "summary": manifest.get("summary", {}),
                "node_count": len(nodes),
                "link_count": len(links),
                "nodes": nodes,
                "links": links,
            },
        }
    matched = next((row for row in nodes if row.get("id") == node_id), None)
    if matched is None:
        raise ValueError(f"graph_node_missing:{node_id}")
    linked = [row for row in links if row.get("source_id") == node_id or row.get("target_id") == node_id]
    return {"ok": True, "data": {"summary": manifest.get("summary", {}), "node": matched, "links": linked}}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query persisted RC0.1 economic-cycle state.")
    parser.add_argument("--manifest", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("summary")

    wallet_parser = subparsers.add_parser("wallets")
    wallet_parser.add_argument("--agent-id")

    wallet_history_parser = subparsers.add_parser("wallet-history")
    wallet_history_parser.add_argument("--agent-id", required=True)

    graph_parser = subparsers.add_parser("graph")
    graph_parser.add_argument("--node-id")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    manifest_path = Path(args.manifest)
    try:
        if args.command == "summary":
            payload = query_summary(manifest_path)
        elif args.command == "wallets":
            payload = query_wallets(manifest_path, args.agent_id)
        elif args.command == "wallet-history":
            payload = query_wallet_history(manifest_path, args.agent_id)
        else:
            payload = query_graph(manifest_path, args.node_id)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
