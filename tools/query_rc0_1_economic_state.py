#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    to_decimal,
)
from ilc_core.ledger.lmdb_backend import LmdbLedgerBackend
from ilc_core.storage.lmdb_public_runtime import LmdbGraphStore, LmdbWalletStore


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_root(manifest_path: Path) -> Path:
    if manifest_path.name == "manifest.json":
        return manifest_path.parent
    raise ValueError("economic_manifest_path_invalid")


def load_runtime_store(manifest: dict[str, Any]) -> dict[str, str]:
    runtime_store = manifest.get("runtime_store")
    if not isinstance(runtime_store, dict):
        return {}
    payload: dict[str, str] = {}
    for key in ("store_kind", "graph_store_root", "wallet_store_root", "ledger_store_root"):
        value = runtime_store.get(key)
        if isinstance(value, str) and value:
            payload[key] = value
    return payload


def load_state(
    manifest_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = load_json(manifest_path)
    runtime_store = load_runtime_store(manifest)
    graph_store_root = runtime_store.get("graph_store_root")
    wallet_store_root = runtime_store.get("wallet_store_root")
    ledger_store_root = runtime_store.get("ledger_store_root")
    if graph_store_root and wallet_store_root and ledger_store_root:
        graph_store = LmdbGraphStore(Path(graph_store_root))
        wallet_store = LmdbWalletStore(Path(wallet_store_root))
        ledger_backend = LmdbLedgerBackend(Path(ledger_store_root))
        return (
            manifest,
            graph_store.iter_nodes(),
            graph_store.iter_links(),
            {"wallets": wallet_store.iter_wallets()},
            {
                "balances": {
                    agent_id: decimal_to_canonical_string(balance)
                    for agent_id, balance in sorted(ledger_backend.balances.items())
                },
                "epoch_records": ledger_backend.epoch_records,
            },
            graph_store.get_quorum_record() or {},
        )

    root = manifest_root(manifest_path)
    nodes = load_json(root / "graph" / "nodes.json")
    links = load_json(root / "graph" / "links.json")
    wallets = load_json(root / "economy" / "wallets.json")
    ledger = load_json(root / "economy" / "ledger_state.json")
    quorum_record = load_json(root / "graph" / "quorum_record.json")
    if not isinstance(nodes, list) or not isinstance(links, list):
        raise ValueError("graph_state_invalid")
    if not isinstance(wallets, dict) or not isinstance(ledger, dict) or not isinstance(quorum_record, dict):
        raise ValueError("economic_state_invalid")
    return manifest, nodes, links, wallets, ledger, quorum_record


def load_wallet_history(manifest_path: Path, agent_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(manifest_path)
    runtime_store = load_runtime_store(manifest)
    wallet_store_root = runtime_store.get("wallet_store_root")
    ledger_store_root = runtime_store.get("ledger_store_root")
    if wallet_store_root and ledger_store_root:
        wallet_store = LmdbWalletStore(Path(wallet_store_root))
        ledger_backend = LmdbLedgerBackend(Path(ledger_store_root))
        row = wallet_store.get_wallet(agent_id)
        if row is None:
            raise ValueError(f"wallet_agent_missing:{agent_id}")
        history = wallet_store.get_wallet_history(agent_id) or {}
        return row, {
            "version": history.get("version"),
            "agent_id": history.get("agent_id", agent_id),
            "generated_at": history.get("generated_at"),
            "latest_epoch_id": history.get("latest_epoch_id"),
            "latest_claim_digest": history.get("latest_claim_digest"),
            "claim_history": history.get("claim_history", []),
            "epoch_history": history.get("epoch_history", list(ledger_backend.epoch_records.values())),
            "balance_history": history.get("balance_history", []),
            "history_digest": history.get("history_digest"),
        }

    manifest, _nodes, _links, wallets, ledger, _quorum = load_state(manifest_path)
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
    return row, {
        "version": manifest.get("version"),
        "agent_id": agent_id,
        "generated_at": manifest.get("generated_at"),
        "latest_epoch_id": next(iter(epoch_records.keys()), None) if epoch_records else None,
        "latest_claim_digest": None,
        "claim_history": claims,
        "epoch_history": list(epoch_records.values()),
        "balance_history": [],
        "history_digest": None,
    }


def _load_claims(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    scenario_root = manifest.get("scenario_root")
    if not isinstance(scenario_root, str) or not scenario_root:
        return []
    claims_path = Path(scenario_root) / "panel" / "ecu_claims.json"
    if not claims_path.is_file():
        return []
    claims_payload = load_json(claims_path)
    claims = claims_payload.get("claims")
    if not isinstance(claims, list):
        return []
    return [row for row in claims if isinstance(row, dict)]


def query_summary(manifest_path: Path) -> dict[str, Any]:
    manifest, nodes, links, wallets, ledger, quorum_record = load_state(manifest_path)
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
            "graph_node_count": len(nodes),
            "graph_link_count": len(links),
            "quorum_task_id": quorum_record.get("task_id"),
            "runtime_store": load_runtime_store(manifest),
        },
    }


def query_wallets(manifest_path: Path, agent_id: str | None) -> dict[str, Any]:
    manifest, _nodes, _links, wallets, _ledger, _quorum = load_state(manifest_path)
    wallet_rows = wallets.get("wallets", {})
    if not isinstance(wallet_rows, dict):
        raise ValueError("wallet_rows_invalid")
    if agent_id is not None:
        row = wallet_rows.get(agent_id)
        if row is None:
            raise ValueError(f"wallet_agent_missing:{agent_id}")
        return {"ok": True, "data": {"agent_id": agent_id, "wallet": row, "summary": manifest.get("summary", {})}}
    return {"ok": True, "data": {"wallets": wallet_rows, "summary": manifest.get("summary", {})}}


def query_wallet_status(manifest_path: Path, agent_id: str) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    row, history = load_wallet_history(manifest_path, agent_id)
    claim_history = history.get("claim_history", [])
    epoch_history = history.get("epoch_history", [])
    balance_history = history.get("balance_history", [])
    latest_balance_receipt = balance_history[-1] if isinstance(balance_history, list) and balance_history else None
    return {
        "ok": True,
        "data": {
            "agent_id": agent_id,
            "wallet": row,
            "claim_count": len(claim_history) if isinstance(claim_history, list) else 0,
            "epoch_count": len(epoch_history) if isinstance(epoch_history, list) else 0,
            "settled_epoch_count": len(balance_history) if isinstance(balance_history, list) else 0,
            "latest_epoch_id": history.get("latest_epoch_id"),
            "latest_claim_digest": history.get("latest_claim_digest"),
            "history_digest": history.get("history_digest"),
            "latest_balance_receipt": latest_balance_receipt,
            "summary": manifest.get("summary", {}),
        },
    }


def query_wallet_export(manifest_path: Path) -> dict[str, Any]:
    manifest, _nodes, _links, wallets, ledger, _quorum = load_state(manifest_path)
    wallet_rows = wallets.get("wallets", {})
    if not isinstance(wallet_rows, dict):
        raise ValueError("wallet_rows_invalid")
    return {
        "ok": True,
        "data": {
            "wallets": wallet_rows,
            "balances": ledger.get("balances", {}),
            "summary": manifest.get("summary", {}),
        },
    }


def query_wallet_history(manifest_path: Path, agent_id: str) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    row, history = load_wallet_history(manifest_path, agent_id)
    return {
        "ok": True,
        "data": {
            "agent_id": agent_id,
            "wallet": row,
            "version": history.get("version"),
            "generated_at": history.get("generated_at"),
            "latest_epoch_id": history.get("latest_epoch_id"),
            "latest_claim_digest": history.get("latest_claim_digest"),
            "claim_history": history.get("claim_history", []),
            "epoch_history": history.get("epoch_history", []),
            "balance_history": history.get("balance_history", []),
            "history_digest": history.get("history_digest"),
            "summary": manifest.get("summary", {}),
        },
    }


def query_graph(manifest_path: Path, node_id: str | None) -> dict[str, Any]:
    manifest, nodes, links, _wallets, _ledger, _quorum = load_state(manifest_path)
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


def query_graph_summary(manifest_path: Path) -> dict[str, Any]:
    return query_graph(manifest_path, None)


def query_graph_node(manifest_path: Path, node_id: str) -> dict[str, Any]:
    return query_graph(manifest_path, node_id)


def query_graph_links(
    manifest_path: Path,
    *,
    node_id: str | None = None,
    agent_id: str | None = None,
    link_type: str | None = None,
) -> dict[str, Any]:
    manifest, _nodes, links, _wallets, _ledger, _quorum = load_state(manifest_path)
    filtered = links
    if node_id is not None:
        filtered = [
            row
            for row in filtered
            if row.get("source_id") == node_id or row.get("target_id") == node_id
        ]
    if agent_id is not None:
        filtered = [row for row in filtered if row.get("agent_id") == agent_id]
    if link_type is not None:
        filtered = [row for row in filtered if row.get("link_type") == link_type]
    return {
        "ok": True,
        "data": {
            "summary": manifest.get("summary", {}),
            "filter": {
                "node_id": node_id,
                "agent_id": agent_id,
                "link_type": link_type,
            },
            "link_count": len(filtered),
            "links": filtered,
        },
    }


def query_quorum_record(manifest_path: Path) -> dict[str, Any]:
    manifest, _nodes, _links, _wallets, _ledger, quorum_record = load_state(manifest_path)
    if not quorum_record:
        raise ValueError("quorum_record_missing")
    return {"ok": True, "data": {"summary": manifest.get("summary", {}), "quorum_record": quorum_record}}


def query_ledger_summary(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    _manifest, _nodes, _links, _wallets, ledger, _quorum = load_state(manifest_path)
    balances = ledger.get("balances", {})
    epoch_records = ledger.get("epoch_records", {})
    if not isinstance(balances, dict):
        raise ValueError("ledger_balances_invalid")
    if not isinstance(epoch_records, dict):
        raise ValueError("ledger_epoch_records_invalid")
    reward_total = decimal_to_canonical_string(
        sum(
            (
                to_decimal(value, token="ledger_summary_balance_invalid")
                for value in balances.values()
                if not isinstance(value, bool)
            ),
            ZERO,
        )
    )
    latest_epoch_id = next(iter(sorted(epoch_records.keys(), reverse=True)), None)
    settlement_manifest = manifest.get("settlement_manifest", {})
    return {
        "ok": True,
        "data": {
            "summary": manifest.get("summary", {}),
            "reward_total": reward_total,
            "balance_count": len(balances),
            "epoch_record_count": len(epoch_records),
            "latest_epoch_id": latest_epoch_id,
            "settlement_status": settlement_manifest.get("settlement_status")
            if isinstance(settlement_manifest, dict)
            else None,
            "balances": balances,
            "epoch_records": epoch_records,
        },
    }


def query_store_summary(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    runtime_store = load_runtime_store(manifest)
    roots = {
        key: {"path": value, "exists": Path(value).exists()}
        for key, value in runtime_store.items()
        if key.endswith("_root")
    }
    return {
        "ok": True,
        "data": {
            "runtime_store": runtime_store,
            "roots": roots,
            "summary": manifest.get("summary", {}),
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query persisted RC0.1 economic-cycle state.")
    parser.add_argument("--manifest", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("summary")

    wallet_parser = subparsers.add_parser("wallets")
    wallet_parser.add_argument("--agent-id")

    wallet_history_parser = subparsers.add_parser("wallet-history")
    wallet_history_parser.add_argument("--agent-id", required=True)

    wallet_status_parser = subparsers.add_parser("wallet-status")
    wallet_status_parser.add_argument("--agent-id", required=True)

    subparsers.add_parser("wallet-export")

    graph_parser = subparsers.add_parser("graph")
    graph_parser.add_argument("--node-id")
    subparsers.add_parser("graph-summary")

    graph_node_parser = subparsers.add_parser("graph-node")
    graph_node_parser.add_argument("--node-id", required=True)

    graph_links_parser = subparsers.add_parser("graph-links")
    graph_links_parser.add_argument("--node-id")
    graph_links_parser.add_argument("--agent-id")
    graph_links_parser.add_argument("--link-type")

    subparsers.add_parser("quorum-record")
    subparsers.add_parser("ledger-summary")
    subparsers.add_parser("store-summary")
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
        elif args.command == "wallet-status":
            payload = query_wallet_status(manifest_path, args.agent_id)
        elif args.command == "wallet-export":
            payload = query_wallet_export(manifest_path)
        elif args.command == "graph-summary":
            payload = query_graph_summary(manifest_path)
        elif args.command == "graph-node":
            payload = query_graph_node(manifest_path, args.node_id)
        elif args.command == "graph-links":
            payload = query_graph_links(
                manifest_path,
                node_id=args.node_id,
                agent_id=args.agent_id,
                link_type=args.link_type,
            )
        elif args.command == "quorum-record":
            payload = query_quorum_record(manifest_path)
        elif args.command == "ledger-summary":
            payload = query_ledger_summary(manifest_path)
        elif args.command == "store-summary":
            payload = query_store_summary(manifest_path)
        else:
            payload = query_graph(manifest_path, args.node_id)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
