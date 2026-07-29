#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.rc.economic_cycle_runtime import EconomicCycleRuntimeError, materialize_economic_cycle
from tools import check_rc0_1_economic_state
from tools import query_rc0_1_economic_state

DEFAULT_OUTPUT_ROOT = REPO_ROOT / "out/rc0_1_economic_proof"


class EconomicProofError(RuntimeError):
    pass


def _digest(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _normalize_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for row in nodes:
        normalized.append(
            {
                "type": row.get("type"),
                "content": row.get("content"),
                "agent_id": row.get("agent_id"),
                "signature": row.get("signature"),
                "net_stake": row.get("net_stake"),
                "target_id": row.get("target_id"),
                "parent_ids": row.get("parent_ids", []),
            }
        )
    return sorted(normalized, key=lambda row: (str(row["agent_id"]), str(row["type"]), _digest(row["content"])))


def _normalize_links(links: list[dict[str, Any]], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    node_map = {str(row.get("id")): str(row.get("agent_id")) for row in nodes}
    normalized = []
    for row in links:
        normalized.append(
            {
                "link_type": row.get("link_type"),
                "source_agent_id": node_map.get(str(row.get("source_id"))),
                "target_agent_id": node_map.get(str(row.get("target_id"))),
                "agent_id": row.get("agent_id"),
            }
        )
    return sorted(normalized, key=lambda row: (str(row["link_type"]), str(row["source_agent_id"]), str(row["target_agent_id"])))


def _normalize_epoch_records(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    epoch_records = ledger.get("epoch_records", {})
    if not isinstance(epoch_records, dict):
        return []
    normalized = []
    for row in epoch_records.values():
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "epoch_id": row.get("epoch_id"),
                "status": row.get("status"),
                "rewards": row.get("rewards"),
                "reward_total": row.get("reward_total"),
            }
        )
    return sorted(normalized, key=lambda row: str(row.get("epoch_id")))


def _normalize_quorum(quorum_record: dict[str, Any]) -> dict[str, Any]:
    panel_result = quorum_record.get("panel_result", {})
    ecu_claim_batch = quorum_record.get("ecu_claim_batch", {})
    return {
        "task_id": quorum_record.get("task_id"),
        "epoch": quorum_record.get("epoch"),
        "panel_result": {
            "task_id": panel_result.get("task_id"),
            "epoch": panel_result.get("epoch"),
            "yes_votes": panel_result.get("yes_votes"),
            "no_votes": panel_result.get("no_votes"),
            "agreement_score": panel_result.get("agreement_score"),
            "verdict_token": panel_result.get("verdict_token"),
            "passed": panel_result.get("passed"),
            "direct_author_agent_id": panel_result.get("direct_author_agent_id"),
            "votes": panel_result.get("votes"),
        },
        "ecu_claim_batch": {
            "claims": ecu_claim_batch.get("claims"),
            "ledger": ecu_claim_batch.get("ledger"),
        },
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def prove_economic_state(*, manifest_path: Path, output_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    verdict, failures, invariant_summary = check_rc0_1_economic_state.check_economic_state(manifest_path)
    if verdict != "pass":
        raise EconomicProofError(f"economic_state_check_failed:{','.join(failures)}")

    manifest = _load_manifest(manifest_path)
    scenario_root = manifest.get("scenario_root")
    if not isinstance(scenario_root, str) or not scenario_root:
        raise EconomicProofError("economic_scenario_root_missing")

    replay_root = output_root / "replay"
    try:
        replay_manifest = materialize_economic_cycle(
            scenario_root=Path(scenario_root),
            output_root=replay_root,
        )
    except EconomicCycleRuntimeError as exc:
        raise EconomicProofError(str(exc)) from exc

    original_state = query_rc0_1_economic_state.load_state(manifest_path)
    replay_state = query_rc0_1_economic_state.load_state(replay_root / "manifest.json")
    _, orig_nodes, orig_links, orig_wallets, orig_ledger, orig_quorum = original_state
    _, replay_nodes, replay_links, replay_wallets, replay_ledger, replay_quorum = replay_state

    comparison = {
        "nodes_match": _digest(_normalize_nodes(orig_nodes)) == _digest(_normalize_nodes(replay_nodes)),
        "links_match": _digest(_normalize_links(orig_links, orig_nodes)) == _digest(_normalize_links(replay_links, replay_nodes)),
        "wallets_match": _digest(orig_wallets) == _digest(replay_wallets),
        "ledger_match": _digest(
            {
                "balances": orig_ledger.get("balances", {}),
                "epoch_records": _normalize_epoch_records(orig_ledger),
            }
        ) == _digest(
            {
                "balances": replay_ledger.get("balances", {}),
                "epoch_records": _normalize_epoch_records(replay_ledger),
            }
        ),
        "quorum_match": _digest(_normalize_quorum(orig_quorum)) == _digest(_normalize_quorum(replay_quorum)),
    }
    if not all(comparison.values()):
        raise EconomicProofError(
            "economic_replay_mismatch:" + ",".join(sorted(key for key, value in comparison.items() if not value))
        )

    wallet_rows = orig_wallets.get("wallets", {}) if isinstance(orig_wallets, dict) else {}
    first_agent_id = next(iter(sorted(wallet_rows)), None)
    query_payloads: dict[str, Any] = {}
    query_timings_ms: dict[str, float] = {}

    def _record_query(name: str, callback: Any) -> None:
        started = time.perf_counter()
        query_payloads[name] = callback()
        query_timings_ms[name] = round((time.perf_counter() - started) * 1000.0, 6)

    _record_query("summary", lambda: query_rc0_1_economic_state.query_summary(manifest_path))
    _record_query("store_summary", lambda: query_rc0_1_economic_state.query_store_summary(manifest_path))
    _record_query("quorum_record", lambda: query_rc0_1_economic_state.query_quorum_record(manifest_path))
    _record_query("wallet_export", lambda: query_rc0_1_economic_state.query_wallet_export(manifest_path))
    _record_query("graph_summary", lambda: query_rc0_1_economic_state.query_graph_summary(manifest_path))
    _record_query("graph_links", lambda: query_rc0_1_economic_state.query_graph_links(manifest_path))
    _record_query("ledger_summary", lambda: query_rc0_1_economic_state.query_ledger_summary(manifest_path))
    if isinstance(first_agent_id, str):
        _record_query(
            "wallet_status",
            lambda: query_rc0_1_economic_state.query_wallet_status(manifest_path, first_agent_id),
        )
        _record_query(
            "wallet_history",
            lambda: query_rc0_1_economic_state.query_wallet_history(manifest_path, first_agent_id),
        )
        if orig_nodes:
            _record_query(
                "graph_node",
                lambda: query_rc0_1_economic_state.query_graph_node(manifest_path, str(orig_nodes[0].get("id"))),
            )

    output_path = output_root / "manifest.json"
    proof_manifest = {
        "version": "rc0_1_economic_proof_v0.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "proof_manifest_path": str(output_path),
        "scenario_root": scenario_root,
        "replay_manifest_path": str(replay_root / "manifest.json"),
        "invariant_summary": invariant_summary,
        "comparison": comparison,
        "query_payloads": query_payloads,
        "query_timings_ms": query_timings_ms,
        "runtime_store": query_rc0_1_economic_state.load_runtime_store(manifest),
        "replay_runtime_store": replay_manifest.get("runtime_store", {}),
    }
    output_path.write_text(json.dumps(proof_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return proof_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prove RC0.1 economic runtime state invariants and replay stability.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-root")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        payload = prove_economic_state(manifest_path=Path(args.manifest), output_root=output_root)
    except EconomicProofError as exc:
        print(json.dumps({"marker": "rc0_1_economic_proof_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps({"marker": "rc0_1_economic_proof_ok", "manifest": payload}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
