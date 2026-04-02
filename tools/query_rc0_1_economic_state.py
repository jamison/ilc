#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_root(manifest_path: Path) -> Path:
    if manifest_path.name == "manifest.json":
        return manifest_path.parent
    raise ValueError("economic_manifest_path_invalid")


def _load_state(manifest_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = _load_json(manifest_path)
    root = _manifest_root(manifest_path)
    nodes = _load_json(root / "graph" / "nodes.json")
    links = _load_json(root / "graph" / "links.json")
    wallets = _load_json(root / "economy" / "wallets.json")
    ledger = _load_json(root / "economy" / "ledger_state.json")
    return manifest, nodes, links, wallets, ledger


def query_summary(manifest_path: Path) -> dict[str, Any]:
    manifest, _nodes, _links, wallets, ledger = _load_state(manifest_path)
    return {
        "ok": True,
        "data": {
            "summary": manifest.get("summary", {}),
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
        else:
            payload = query_graph(manifest_path, args.node_id)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
