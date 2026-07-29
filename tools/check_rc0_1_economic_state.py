#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import hashlib
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
from tools import query_rc0_1_economic_state


def _exact_sum(values: Sequence[Any]) -> Any:
    return sum((to_decimal(value) for value in values), ZERO)


def _claim_total(claims: list[dict[str, Any]]) -> Any:
    amounts: list[Any] = []
    for claim in claims:
        amount = claim.get("amount")
        if isinstance(amount, bool):
            continue
        try:
            amounts.append(to_decimal(amount))
        except ValueError:
            continue
    return sum(amounts, ZERO)


def _claim_digest(claim: dict[str, Any]) -> str:
    return json.dumps(claim, sort_keys=True, separators=(",", ":"))


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _history_digest(*, claim_history: list[dict[str, Any]], epoch_history: list[dict[str, Any]], balance_history: list[dict[str, Any]]) -> str:
    return _sha256_json(
        {
            "claim_history": claim_history,
            "epoch_history": epoch_history,
            "balance_history": balance_history,
        }
    )


def check_economic_state(manifest_path: Path) -> tuple[str, list[str], dict[str, Any]]:
    manifest = query_rc0_1_economic_state.load_json(manifest_path)
    runtime_store = query_rc0_1_economic_state.load_runtime_store(manifest)
    preflight_failures: list[str] = []
    if runtime_store.get("store_kind") != "lmdb_public_runtime_v0.1":
        preflight_failures.append(f"economic_runtime_store_kind_invalid:{runtime_store.get('store_kind')}")
    for key in ("graph_store_root", "wallet_store_root", "ledger_store_root"):
        path_value = runtime_store.get(key)
        if not path_value:
            preflight_failures.append(f"economic_runtime_store_missing:{key}")
            continue
        if not Path(path_value).is_dir():
            preflight_failures.append(f"economic_runtime_store_path_missing:{key}:{path_value}")
    if preflight_failures:
        return "fail", preflight_failures, {"runtime_store": runtime_store}

    manifest, nodes, links, wallets, ledger, quorum_record = query_rc0_1_economic_state.load_state(manifest_path)
    summary = manifest.get("summary", {})
    settlement_manifest = manifest.get("settlement_manifest", {})
    wallet_manifest = manifest.get("wallet_manifest", {})
    runtime_identity = manifest.get("runtime_identity", {})

    failures: list[str] = []
    wallet_rows = wallets.get("wallets", {})
    if not isinstance(summary, dict):
        failures.append("economic_summary_invalid")
        summary = {}
    if not isinstance(wallet_rows, dict):
        failures.append("economic_wallet_rows_invalid")
        wallet_rows = {}
    balances = ledger.get("balances", {})
    epoch_records = ledger.get("epoch_records", {})
    if not isinstance(balances, dict):
        failures.append("economic_balances_invalid")
        balances = {}
    if not isinstance(epoch_records, dict):
        failures.append("economic_epoch_records_invalid")
        epoch_records = {}

    task_id = summary.get("task_id")
    if task_id and quorum_record.get("task_id") != task_id:
        failures.append("economic_quorum_task_id_mismatch")
    if not isinstance(quorum_record, dict) or not quorum_record:
        failures.append("economic_quorum_record_missing")
    if task_id and settlement_manifest.get("task_id") != task_id:
        failures.append("economic_settlement_task_id_mismatch")
    if not isinstance(runtime_identity, dict):
        failures.append("economic_runtime_identity_invalid")
        runtime_identity = {}
    if task_id and runtime_identity.get("task_id") != task_id:
        failures.append("economic_runtime_identity_task_id_mismatch")
    expected_epoch_index = settlement_manifest.get("epoch_index")
    if isinstance(expected_epoch_index, int) and runtime_identity.get("epoch_index") != expected_epoch_index:
        failures.append("economic_runtime_identity_epoch_index_mismatch")

    expected_node_count = summary.get("node_count")
    if isinstance(expected_node_count, int) and expected_node_count != len(nodes):
        failures.append("economic_node_count_mismatch")
    expected_link_count = summary.get("support_link_count")
    if isinstance(expected_link_count, int) and expected_link_count != len(links):
        failures.append("economic_link_count_mismatch")
    expected_wallet_count = summary.get("wallet_count")
    if isinstance(expected_wallet_count, int) and expected_wallet_count != len(wallet_rows):
        failures.append("economic_wallet_count_mismatch")

    reward_total = summary.get("reward_total")
    try:
        reward_total_decimal = to_decimal(reward_total)
    except ValueError:
        failures.append("economic_reward_total_invalid")
        reward_total_decimal = ZERO

    wallet_balance_total = _exact_sum(
        row.get("balance_ilc", "0")
        for row in wallet_rows.values()
        if isinstance(row, dict) and not isinstance(row.get("balance_ilc"), bool)
    )
    ledger_balance_total = _exact_sum(
        value
        for value in balances.values()
        if not isinstance(value, bool)
    )

    if wallet_balance_total != reward_total_decimal:
        failures.append("economic_reward_total_mismatch:wallets")
    if ledger_balance_total != reward_total_decimal:
        failures.append("economic_reward_total_mismatch:ledger")
    if wallet_balance_total != ledger_balance_total:
        failures.append("economic_balance_surface_mismatch")

    expected_rewarded_wallet_count = wallet_manifest.get("rewarded_wallet_count")
    rewarded_wallet_count = sum(
        1
        for row in wallet_rows.values()
        if isinstance(row, dict) and to_decimal(row.get("balance_ilc", "0")) > ZERO
    )
    if isinstance(expected_rewarded_wallet_count, int) and expected_rewarded_wallet_count != rewarded_wallet_count:
        failures.append("economic_rewarded_wallet_count_mismatch")

    expected_epoch_id = settlement_manifest.get("epoch_id")
    if isinstance(expected_epoch_id, str) and expected_epoch_id and expected_epoch_id not in epoch_records:
        failures.append("economic_epoch_record_missing")
    if isinstance(expected_epoch_id, str) and expected_epoch_id and runtime_identity.get("epoch_id") != expected_epoch_id:
        failures.append("economic_runtime_identity_epoch_id_mismatch")
    settlement_status = settlement_manifest.get("settlement_status")
    if settlement_status not in {"applied", "idempotent_replay"}:
        failures.append("economic_settlement_status_invalid")
    claim_batch_sha256 = settlement_manifest.get("claim_batch_sha256")
    if not isinstance(claim_batch_sha256, str) or not claim_batch_sha256:
        failures.append("economic_claim_batch_sha256_missing")
    elif runtime_identity.get("claims_sha256") != claim_batch_sha256:
        failures.append("economic_runtime_identity_claims_mismatch")
    latest_epoch_id = wallet_manifest.get("latest_epoch_id") if isinstance(wallet_manifest, dict) else None
    if isinstance(expected_epoch_id, str) and expected_epoch_id and latest_epoch_id != expected_epoch_id:
        failures.append("economic_wallet_manifest_latest_epoch_mismatch")
    wallet_claim_batch_sha256 = wallet_manifest.get("claim_batch_sha256") if isinstance(wallet_manifest, dict) else None
    if isinstance(claim_batch_sha256, str) and claim_batch_sha256 and wallet_claim_batch_sha256 != claim_batch_sha256:
        failures.append("economic_wallet_manifest_claim_batch_mismatch")

    for agent_id, row in sorted(wallet_rows.items()):
        if not isinstance(row, dict):
            failures.append(f"economic_wallet_row_invalid:{agent_id}")
            continue
        try:
            _, history = query_rc0_1_economic_state.load_wallet_history(manifest_path, agent_id)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        claim_history = history.get("claim_history", [])
        epoch_history = history.get("epoch_history", [])
        balance_history = history.get("balance_history", [])
        if not isinstance(claim_history, list) or not isinstance(epoch_history, list) or not isinstance(balance_history, list):
            failures.append(f"economic_wallet_history_invalid:{agent_id}")
            continue
        ecu_claim_total = row.get("ecu_claim_total")
        if ecu_claim_total is not None and not isinstance(ecu_claim_total, bool):
            if to_decimal(ecu_claim_total) != _claim_total([claim for claim in claim_history if isinstance(claim, dict)]):
                failures.append(f"economic_wallet_claim_total_mismatch:{agent_id}")
        settled_epoch_count = row.get("settled_epoch_count")
        if isinstance(settled_epoch_count, int) and settled_epoch_count != len(balance_history):
            failures.append(f"economic_wallet_settled_epoch_count_mismatch:{agent_id}")
        lifetime_claim_count = row.get("lifetime_claim_count")
        if isinstance(lifetime_claim_count, int) and lifetime_claim_count != len(claim_history):
            failures.append(f"economic_wallet_lifetime_claim_count_mismatch:{agent_id}")
        last_settled_epoch_id = row.get("last_settled_epoch_id")
        latest_epoch_id = history.get("latest_epoch_id")
        if last_settled_epoch_id and latest_epoch_id and str(last_settled_epoch_id) != str(latest_epoch_id):
            failures.append(f"economic_wallet_latest_epoch_mismatch:{agent_id}")
        digests = [_claim_digest(claim) for claim in claim_history if isinstance(claim, dict)]
        if len(set(digests)) != len(digests):
            failures.append(f"economic_wallet_claim_duplicate:{agent_id}")
        latest_claim_digest = history.get("latest_claim_digest")
        expected_claim_digest = _sha256_json([claim for claim in claim_history if isinstance(claim, dict)])
        if latest_claim_digest not in (None, expected_claim_digest):
            failures.append(f"economic_wallet_latest_claim_digest_mismatch:{agent_id}")
        balance_epoch_ids = []
        for balance_row in balance_history:
            if not isinstance(balance_row, dict):
                failures.append(f"economic_wallet_balance_history_invalid:{agent_id}")
                continue
            balance_epoch_id = balance_row.get("epoch_id")
            if isinstance(balance_epoch_id, str) and balance_epoch_id:
                balance_epoch_ids.append(balance_epoch_id)
            if balance_row.get("settlement_status") not in {"applied", "idempotent_replay"}:
                failures.append(f"economic_wallet_balance_history_status_invalid:{agent_id}")
        if len(set(balance_epoch_ids)) != len(balance_epoch_ids):
            failures.append(f"economic_wallet_balance_history_duplicate:{agent_id}")
        if isinstance(expected_epoch_id, str) and expected_epoch_id:
            epoch_ids = {
                str(record.get("epoch_id"))
                for record in epoch_history
                if isinstance(record, dict) and isinstance(record.get("epoch_id"), str)
            }
            if expected_epoch_id not in epoch_ids:
                failures.append(f"economic_wallet_epoch_history_missing:{agent_id}")
            if expected_epoch_id not in balance_epoch_ids:
                failures.append(f"economic_wallet_balance_history_missing:{agent_id}")
        history_digest = history.get("history_digest")
        expected_history_digest = _history_digest(
            claim_history=[claim for claim in claim_history if isinstance(claim, dict)],
            epoch_history=[epoch for epoch in epoch_history if isinstance(epoch, dict)],
            balance_history=[item for item in balance_history if isinstance(item, dict)],
        )
        if history_digest not in (None, expected_history_digest):
            failures.append(f"economic_wallet_history_digest_mismatch:{agent_id}")

    if summary.get("distribution_check_ok") is not True:
        failures.append("economic_distribution_check_not_pass")

    proof_summary = {
        "task_id": task_id,
        "runtime_store": runtime_store,
        "runtime_identity": runtime_identity,
        "reward_total": decimal_to_canonical_string(reward_total_decimal),
        "wallet_balance_total": decimal_to_canonical_string(wallet_balance_total),
        "ledger_balance_total": decimal_to_canonical_string(ledger_balance_total),
        "node_count": len(nodes),
        "link_count": len(links),
        "wallet_count": len(wallet_rows),
        "rewarded_wallet_count": rewarded_wallet_count,
        "epoch_record_count": len(epoch_records),
        "settlement_status": settlement_status,
    }
    if failures:
        return "fail", failures, proof_summary
    return "pass", [], proof_summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check RC0.1 economic runtime state invariants.")
    parser.add_argument("--manifest", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    verdict, failures, summary = check_economic_state(Path(args.manifest))
    if failures:
        for failure in failures:
            print(failure)
        print(json.dumps({"ok": False, "summary": summary}, sort_keys=True, separators=(",", ":")))
        print("economic_state_verdict=fail")
        return 1
    print(json.dumps({"ok": True, "summary": summary}, sort_keys=True, separators=(",", ":")))
    print("economic_state_verdict=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
