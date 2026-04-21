from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ilc_core.graph import EpistemicGraph
from ilc_core.ledger.backend import settle_commit_epoch
from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    normalize_json_scalars,
    parse_non_negative_decimal,
    to_decimal,
)
from ilc_core.ledger.ledger_export import (
    export_ledger_distribution_checks_csv,
    export_ledger_state_csv,
    export_ledger_state_json,
)
from ilc_core.ledger.lmdb_backend import LmdbLedgerBackend
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEventLog, make_commit_epoch_event, make_event
from ilc_core.storage.lmdb_public_runtime import LmdbGraphStore, LmdbWalletStore
from ilc_core.types import LinkRecord, Node

RUNTIME_VERSION = "rc0_1_economic_cycle_v0.1"


class EconomicCycleRuntimeError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(normalize_json_scalars(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_json(payload: Any) -> str:
    return _sha256_bytes(
        json.dumps(
            normalize_json_scalars(payload),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def _dag_cbor_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return format(value, ".15g")
    if isinstance(value, list):
        return [_dag_cbor_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _dag_cbor_safe(item) for key, item in value.items()}
    return str(value)


def _scenario_task_id(scenario_manifest: dict[str, Any]) -> str:
    task_id = scenario_manifest.get("task_id")
    if isinstance(task_id, str) and task_id:
        return task_id
    direct_author = scenario_manifest.get("direct_author_agent_id", "unknown-agent")
    return f"task::{direct_author}::{scenario_manifest.get('generated_at', 'epoch')}"


def _runtime_identity(*, scenario_manifest: dict[str, Any], claims_payload: dict[str, Any], panel_payload: dict[str, Any]) -> dict[str, Any]:
    task_id = _coerce_task_id(scenario_manifest.get("task_id")) or _scenario_task_id(scenario_manifest)
    epoch_index = scenario_manifest.get("epoch")
    if isinstance(epoch_index, bool) or not isinstance(epoch_index, int):
        epoch_index = 0
    return {
        "task_id": task_id,
        "epoch_index": epoch_index,
        "epoch_id": f"rc0_1::{task_id}::epoch::{epoch_index}",
        "claims_sha256": _sha256_json(claims_payload),
        "panel_sha256": _sha256_json(panel_payload),
        "scenario_sha256": _sha256_json(scenario_manifest),
    }


def _load_existing_manifest(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    payload = _load_json(path)
    return payload if isinstance(payload, dict) else None


def _assert_runtime_root_compatibility(*, output_root: Path, runtime_identity: dict[str, Any]) -> None:
    existing_manifest = _load_existing_manifest(output_root / "manifest.json")
    if existing_manifest is None:
        return
    existing_identity = existing_manifest.get("runtime_identity")
    if not isinstance(existing_identity, dict):
        raise EconomicCycleRuntimeError("economic_runtime_manifest_invalid")
    comparable_keys = ("task_id", "epoch_index", "epoch_id", "claims_sha256", "panel_sha256", "scenario_sha256")
    existing_projection = {key: existing_identity.get(key) for key in comparable_keys}
    current_projection = {key: runtime_identity.get(key) for key in comparable_keys}
    if existing_projection != current_projection:
        raise EconomicCycleRuntimeError("economic_runtime_root_conflict")


def _coerce_task_id(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _node_from_submission(submission: dict[str, Any]) -> Node:
    profile = submission.get("profile")
    if not isinstance(profile, dict):
        raise EconomicCycleRuntimeError("submission_profile_missing")
    output_payload = submission.get("output_payload")
    if not isinstance(output_payload, dict):
        raise EconomicCycleRuntimeError("submission_output_payload_missing")
    ep_task = submission.get("ep_task")
    if not isinstance(ep_task, dict):
        raise EconomicCycleRuntimeError("submission_ep_task_missing")
    agent_id = profile.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise EconomicCycleRuntimeError("submission_agent_id_missing")
    output_hash = submission.get("output_hash")
    if not isinstance(output_hash, str) or not output_hash:
        raise EconomicCycleRuntimeError("submission_output_hash_missing")
    ecu_estimate = ep_task.get("ecu_estimate", ep_task.get("ecu.estimate", 0.0))
    try:
        ecu_estimate_decimal = parse_non_negative_decimal(
            ecu_estimate,
            token="submission_ecu_estimate_invalid",
        )
    except ValueError as exc:
        raise EconomicCycleRuntimeError(str(exc)) from exc

    if isinstance(ecu_estimate, bool):
        raise EconomicCycleRuntimeError("submission_ecu_estimate_invalid")

    content = _dag_cbor_safe({
        "artifact_kind": "agent_submission",
        "task_id": submission.get("task_id"),
        "channel": submission.get("channel"),
        "epoch": submission.get("epoch"),
        "output_hash": output_hash,
        "output_payload": output_payload,
        "ep_task": ep_task,
    })
    node = Node(
        id="",
        type="claim",
        content=content,
        agent_id=agent_id,
        signature=f"agent-loop-submission:{output_hash[:24]}",
        net_stake=float(ecu_estimate_decimal),
    )
    node.id = node.compute_id()
    return node


def _link_id(source_id: str, target_id: str, link_type: str) -> str:
    return _sha256_bytes(f"{source_id}:{target_id}:{link_type}".encode("utf-8"))


def _node_export(node: Node) -> dict[str, Any]:
    return {
        "id": node.id,
        "type": node.type,
        "content": node.content,
        "agent_id": node.agent_id,
        "timestamp": node.timestamp.isoformat(),
        "signature": node.signature,
        "net_stake": node.net_stake,
        "target_id": node.target_id,
        "parent_ids": list(node.parent_ids),
    }


def _link_export(link: LinkRecord) -> dict[str, Any]:
    return {
        "id": link.id,
        "link_type": link.link_type,
        "source_id": link.source_id,
        "target_id": link.target_id,
        "timestamp": link.timestamp,
        "agent_id": link.agent_id,
    }


def _participant_profiles(scenario_root: Path) -> dict[str, dict[str, Any]]:
    participants: dict[str, dict[str, Any]] = {}
    for submission_path in sorted((scenario_root / "submissions").glob("submission_*.json")):
        wrapper = _load_json(submission_path)
        submission = wrapper.get("submission")
        if not isinstance(submission, dict):
            continue
        profile = submission.get("profile")
        if not isinstance(profile, dict):
            continue
        agent_id = profile.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            continue
        participants[agent_id] = {
            "cluster_id": profile.get("cluster_id"),
            "node_name": profile.get("node_name"),
            "slot": profile.get("slot"),
            "variant": profile.get("variant"),
        }

    panel_payload_path = scenario_root / "panel" / "panel_result.json"
    if panel_payload_path.is_file():
        panel_payload = _load_json(panel_payload_path)
        outsider_submission = panel_payload.get("outsider_submission")
        if isinstance(outsider_submission, dict):
            outsider_profile = outsider_submission.get("profile")
            if isinstance(outsider_profile, dict):
                agent_id = outsider_profile.get("agent_id")
                if isinstance(agent_id, str) and agent_id:
                    participants.setdefault(
                        agent_id,
                        {
                            "cluster_id": outsider_profile.get("cluster_id"),
                            "node_name": outsider_profile.get("node_name"),
                            "slot": outsider_profile.get("slot"),
                            "variant": outsider_profile.get("variant"),
                        },
                    )
    return participants


def materialize_graph_state(*, scenario_root: Path, output_root: Path) -> dict[str, Any]:
    scenario_manifest = _load_json(scenario_root / "scenario_manifest.json")
    panel_payload = _load_json(scenario_root / "panel" / "panel_result.json")
    claims_payload = _load_json(scenario_root / "panel" / "ecu_claims.json")
    graph = EpistemicGraph()
    graph_store_root = output_root / "store"
    graph_store = LmdbGraphStore(graph_store_root)
    event_log = ProtocolEventLog(output_root / "protocol_events.ndjson")

    submissions = []
    agent_node_map: dict[str, Node] = {}
    for submission_path in sorted((scenario_root / "submissions").glob("submission_*.json")):
        wrapper = _load_json(submission_path)
        submission = wrapper.get("submission")
        if not isinstance(submission, dict):
            raise EconomicCycleRuntimeError(f"submission_wrapper_invalid:{submission_path}")
        node = _node_from_submission(submission)
        graph.add_node(node)
        agent_node_map[node.agent_id] = node
        submissions.append(node)
        event_log.append(
            make_event(
                "claim",
                {
                    "node_id": node.id,
                    "agent_id": node.agent_id,
                    "task_id": submission.get("task_id"),
                    "epoch": submission.get("epoch"),
                    "output_hash": submission.get("output_hash"),
                },
                source="rc:economic_cycle",
            )
        )

    panel_result = panel_payload.get("panel_result")
    if not isinstance(panel_result, dict):
        raise EconomicCycleRuntimeError("panel_result_missing")
    direct_author = panel_result.get("direct_author_agent_id")
    if not isinstance(direct_author, str) or direct_author not in agent_node_map:
        raise EconomicCycleRuntimeError("direct_author_not_found_in_submissions")
    target_node = agent_node_map[direct_author]

    link_exports: list[dict[str, Any]] = []
    for vote in panel_result.get("votes", []):
        if not isinstance(vote, dict):
            continue
        if vote.get("passed") is not True:
            continue
        reviewer = vote.get("reviewer_agent_id")
        variant = vote.get("variant")
        if not isinstance(reviewer, str) or reviewer == direct_author or variant == "outsider":
            continue
        source_node = agent_node_map.get(reviewer)
        if source_node is None:
            continue
        link = LinkRecord(
            id=_link_id(source_node.id, target_node.id, "supports"),
            link_type="supports",
            source_id=source_node.id,
            target_id=target_node.id,
            timestamp=_utc_now(),
            agent_id=reviewer,
        )
        graph.add_link(link)
        link_exports.append(_link_export(link))

    task_id = _coerce_task_id(panel_result.get("task_id")) or _coerce_task_id(scenario_manifest.get("task_id")) or _scenario_task_id(scenario_manifest)

    quorum_record = {
        "version": RUNTIME_VERSION,
        "generated_at": _utc_now(),
        "task_id": task_id,
        "epoch": panel_result.get("epoch"),
        "panel_result": panel_result,
        "ecu_claim_batch": claims_payload,
    }

    event_log.append(
        make_event(
            "epoch_summary",
            {
                "task_id": quorum_record["task_id"],
                "epoch": quorum_record["epoch"],
                "submission_count": len(submissions),
                "support_link_count": len(link_exports),
                "panel_verdict_token": panel_result.get("verdict_token"),
                "ecu_claim_count": len(claims_payload.get("claims", [])),
            },
            source="rc:economic_cycle",
        )
    )

    node_exports = sorted((_node_export(node) for node in graph.nodes.values()), key=lambda row: str(row["id"]))
    link_exports = sorted(link_exports, key=lambda row: (str(row["source_id"]), str(row["target_id"]), str(row["id"])))
    for row in node_exports:
        graph_store.put_node(str(row["id"]), row)
    for row in link_exports:
        graph_store.put_link(str(row["id"]), row)
    graph_store.put_quorum_record(quorum_record)
    _write_json(output_root / "nodes.json", node_exports)
    _write_json(output_root / "links.json", link_exports)
    _write_json(output_root / "quorum_record.json", quorum_record)

    return {
        "version": RUNTIME_VERSION,
        "generated_at": _utc_now(),
        "node_count": len(node_exports),
        "link_count": len(link_exports),
        "direct_author_agent_id": direct_author,
        "panel_verdict_token": panel_result.get("verdict_token"),
        "nodes_sha256": _sha256_json(node_exports),
        "links_sha256": _sha256_json(link_exports),
        "store_kind": "lmdb",
        "store_root": str(graph_store_root),
        "nodes_path": str(output_root / "nodes.json"),
        "links_path": str(output_root / "links.json"),
        "quorum_record_path": str(output_root / "quorum_record.json"),
        "protocol_event_log_path": str(output_root / "protocol_events.ndjson"),
    }


def settle_economic_cycle(*, scenario_root: Path, output_root: Path) -> dict[str, Any]:
    scenario_manifest = _load_json(scenario_root / "scenario_manifest.json")
    claims_payload = _load_json(scenario_root / "panel" / "ecu_claims.json")
    claims = claims_payload.get("claims")
    if not isinstance(claims, list) or not claims:
        raise EconomicCycleRuntimeError("ecu_claims_missing")

    ledger_root = output_root / "ledger-store"
    ledger = LmdbLedgerBackend(ledger_root)

    claim_totals: dict[str, Any] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            raise EconomicCycleRuntimeError("ecu_claim_invalid")
        agent_id = claim.get("agent_id")
        amount = claim.get("amount")
        if not isinstance(agent_id, str) or not agent_id:
            raise EconomicCycleRuntimeError("ecu_claim_agent_id_invalid")
        try:
            amount_decimal = parse_non_negative_decimal(
                amount,
                token="ecu_claim_amount_invalid",
            )
        except ValueError as exc:
            raise EconomicCycleRuntimeError(str(exc)) from exc
        claim_totals[agent_id] = claim_totals.get(agent_id, ZERO) + amount_decimal

    ledger_payload = claims_payload.get("ledger")
    if not isinstance(ledger_payload, dict):
        raise EconomicCycleRuntimeError("ecu_claim_ledger_missing")
    rewards_paid = ledger_payload.get("rewards_paid")
    try:
        rewards_paid_decimal = parse_non_negative_decimal(
            rewards_paid,
            token="ecu_claim_rewards_paid_invalid",
        )
    except ValueError as exc:
        raise EconomicCycleRuntimeError(str(exc)) from exc

    epoch_index = scenario_manifest.get("epoch")
    if isinstance(epoch_index, bool) or not isinstance(epoch_index, int):
        epoch_index = int(claims[0].get("epoch", 0))
    task_id = _coerce_task_id(claims[0].get("task_id")) or _coerce_task_id(scenario_manifest.get("task_id")) or _scenario_task_id(scenario_manifest)
    epoch_id = f"rc0_1::{task_id}::epoch::{epoch_index}"
    reward_total = sum(claim_totals.values(), ZERO)
    if reward_total != rewards_paid_decimal:
        raise EconomicCycleRuntimeError("ecu_claim_reward_total_mismatch")
    total_stake = reward_total
    if total_stake <= ZERO:
        raise EconomicCycleRuntimeError("ecu_claim_reward_total_non_positive")

    claim_batch_sha256 = _sha256_json(claims_payload)
    existing_epoch_record = ledger.get_epoch_record(epoch_id)
    settlement_status = "applied"
    if existing_epoch_record is not None:
        existing_checksums = existing_epoch_record.get("checksums", {})
        existing_events_cid = existing_checksums.get("epoch_events_cid") if isinstance(existing_checksums, dict) else None
        expected_events_cid = f"sha256:{claim_batch_sha256}"
        if existing_events_cid != expected_events_cid:
            raise EconomicCycleRuntimeError("economic_epoch_replay_conflict")
        existing_summary = existing_epoch_record.get("summary", {})
        existing_reward_total = existing_summary.get("reward_total") if isinstance(existing_summary, dict) else None
        if existing_reward_total is not None:
            existing_reward_total_decimal = to_decimal(
                existing_reward_total,
                token="economic_epoch_reward_conflict",
            )
            if existing_reward_total_decimal != reward_total:
                raise EconomicCycleRuntimeError("economic_epoch_reward_conflict")
        settlement_status = "idempotent_replay"

    balances_before = dict(ledger.balances)
    snapshot = StakeSnapshot(
        epoch_id=epoch_id,
        epoch_index=epoch_index,
        namespace_id="rc0_1_three_node",
        stakes=claim_totals,
        total_stake=total_stake,
        created_at=_utc_now(),
    )
    ledger.put_stake_snapshot(snapshot)

    checksums = {
        "epoch_events_cid": f"sha256:{claim_batch_sha256}",
        "epoch_state_cid": f"sha256:{_sha256_json(scenario_manifest)}",
    }
    commit_event = make_commit_epoch_event(
        epoch_index=epoch_index,
        epoch_id=epoch_id,
        namespace_id="rc0_1_three_node",
        created_at=_utc_now(),
        finalization_state="committed",
        summary={
            "task_count": 1,
            "agent_count": len(claim_totals),
            "reward_total": reward_total,
            "stake_total": total_stake,
        },
        checksums=checksums,
        source="rc:economic_cycle",
    )
    settle_commit_epoch(ledger, commit_event)
    event_log = ProtocolEventLog(output_root / "protocol_events.ndjson")
    event_log.append(commit_event)

    ledger_json_path = output_root / "ledger_state.json"
    check = export_ledger_state_json(
        ledger,
        ledger_json_path,
        balances_before=balances_before,
        target_epoch_id=epoch_id,
    )
    export_ledger_state_csv(ledger, output_root / "ledger_state.csv")
    if check:
        export_ledger_distribution_checks_csv(
            [{**check, "epoch_id": epoch_id}],
            output_root / "ledger_distribution_checks.csv",
        )

    return {
        "version": RUNTIME_VERSION,
        "generated_at": _utc_now(),
        "task_id": task_id,
        "epoch_id": epoch_id,
        "epoch_index": epoch_index,
        "claim_count": len(claims),
        "claim_batch_sha256": claim_batch_sha256,
        "reward_total": decimal_to_canonical_string(reward_total),
        "agent_count": len(claim_totals),
        "settlement_status": settlement_status,
        "ledger_root": str(ledger_root),
        "store_kind": "lmdb",
        "ledger_state_path": str(ledger_json_path),
        "protocol_event_log_path": str(output_root / "protocol_events.ndjson"),
        "distribution_check_ok": bool(check.get("ok", False)) if isinstance(check, dict) else False,
        "balances": {
            agent_id: decimal_to_canonical_string(balance)
            for agent_id, balance in sorted(ledger.balances.items())
        },
    }


def _aggregate_claim_totals(claims: list[Any]) -> dict[str, dict[str, Any]]:
    claim_totals: dict[str, dict[str, Any]] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        agent_id = claim.get("agent_id")
        amount = claim.get("amount")
        if not isinstance(agent_id, str):
            continue
        try:
            amount_decimal = parse_non_negative_decimal(
                amount,
                token="wallet_claim_amount_invalid",
            )
        except ValueError:
            continue
        row = claim_totals.setdefault(agent_id, {"ecu_claim_total": ZERO, "claim_kinds": []})
        row["ecu_claim_total"] = row["ecu_claim_total"] + amount_decimal
        claim_kind = claim.get("claim_kind")
        if isinstance(claim_kind, str):
            row["claim_kinds"].append(claim_kind)
    return claim_totals


def _persist_agent_wallet_history(
    *,
    agent_id: str,
    row: dict,
    wallet_store: LmdbWalletStore,
    claims: list,
    epoch_history: list,
    epoch_id: Any,
    settlement_manifest: dict,
    generated_at: str,
) -> None:
    existing_history = wallet_store.get_wallet_history(agent_id) or {}
    existing_claims = existing_history.get("claim_history", [])
    existing_epochs = existing_history.get("epoch_history", [])
    existing_balance_history = existing_history.get("balance_history", [])
    if not isinstance(existing_claims, list):
        existing_claims = []
    if not isinstance(existing_epochs, list):
        existing_epochs = []
    if not isinstance(existing_balance_history, list):
        existing_balance_history = []
    claim_history = [
        claim
        for claim in claims
        if isinstance(claim, dict) and claim.get("agent_id") == agent_id
    ]
    claim_ids = sorted(
        str(claim.get("claim_id"))
        for claim in claim_history
        if isinstance(claim.get("claim_id"), str) and claim.get("claim_id")
    )
    claim_digest = _sha256_json(claim_history)
    balance_receipt = {
        "epoch_id": epoch_id,
        "epoch_index": settlement_manifest.get("epoch_index"),
        "claim_count": len(claim_history),
        "claim_ids": claim_ids,
        "claim_digest": claim_digest,
        "reward_delta_ilc": row["ecu_claim_total"],
        "balance_after_ilc": row["balance_ilc"],
        "reward_status": row["reward_status"],
        "distribution_check_ok": settlement_manifest.get("distribution_check_ok"),
        "settlement_status": settlement_manifest.get("settlement_status"),
        "claim_batch_sha256": settlement_manifest.get("claim_batch_sha256"),
    }
    merged_claim_map = {
        str(item.get("claim_id")): item
        for item in existing_claims
        if isinstance(item, dict) and isinstance(item.get("claim_id"), str) and item.get("claim_id")
    }
    for claim in claim_history:
        claim_id = claim.get("claim_id")
        if isinstance(claim_id, str) and claim_id:
            merged_claim_map[claim_id] = claim
    merged_epoch_map = {
        str(item.get("epoch_id")): item
        for item in existing_epochs
        if isinstance(item, dict) and isinstance(item.get("epoch_id"), str) and item.get("epoch_id")
    }
    for epoch_row in epoch_history:
        if isinstance(epoch_row, dict):
            epoch_row_id = epoch_row.get("epoch_id")
            if isinstance(epoch_row_id, str) and epoch_row_id:
                merged_epoch_map[epoch_row_id] = epoch_row
    merged_balance_map = {
        str(item.get("epoch_id")): item
        for item in existing_balance_history
        if isinstance(item, dict) and isinstance(item.get("epoch_id"), str) and item.get("epoch_id")
    }
    if isinstance(epoch_id, str) and epoch_id:
        merged_balance_map[epoch_id] = balance_receipt
    merged_claim_history = [merged_claim_map[key] for key in sorted(merged_claim_map)]
    merged_epoch_history = [merged_epoch_map[key] for key in sorted(merged_epoch_map)]
    merged_balance_history = [merged_balance_map[key] for key in sorted(merged_balance_map)]
    row["lifetime_claim_count"] = len(merged_claim_history)
    row["settled_epoch_count"] = len(merged_balance_history)
    wallet_store.put_wallet(agent_id, row)
    wallet_store.put_wallet_history(
        agent_id,
        {
            "version": RUNTIME_VERSION,
            "agent_id": agent_id,
            "generated_at": generated_at,
            "latest_epoch_id": epoch_id,
            "latest_claim_digest": claim_digest,
            "claim_history": merged_claim_history,
            "epoch_history": merged_epoch_history,
            "balance_history": merged_balance_history,
            "history_digest": _sha256_json(
                {
                    "claim_history": merged_claim_history,
                    "epoch_history": merged_epoch_history,
                    "balance_history": merged_balance_history,
                }
            ),
        },
    )


def export_wallet_state(
    *,
    scenario_root: Path,
    output_root: Path,
    balances: dict[str, object],
    settlement_manifest: dict[str, Any],
) -> dict[str, Any]:
    claims_payload = _load_json(scenario_root / "panel" / "ecu_claims.json")
    claims = claims_payload.get("claims")
    if not isinstance(claims, list):
        raise EconomicCycleRuntimeError("wallet_claims_missing")

    claim_totals = _aggregate_claim_totals(claims)
    participants = _participant_profiles(scenario_root)
    wallet_agent_ids = sorted(set(participants.keys()) | set(balances.keys()) | set(claim_totals.keys()))
    wallet_store_root = output_root / "wallet-store"
    wallet_store = LmdbWalletStore(wallet_store_root)
    epoch_id = settlement_manifest.get("epoch_id")
    claim_batch_sha256 = settlement_manifest.get("claim_batch_sha256")

    wallet_payload = {
        "version": RUNTIME_VERSION,
        "generated_at": _utc_now(),
        "wallets": {
            agent_id: {
                "balance_ilc": decimal_to_canonical_string(
                    to_decimal(balances.get(agent_id, "0"), token="wallet_balance_invalid")
                ),
                "ecu_claim_total": decimal_to_canonical_string(
                    to_decimal(
                        claim_totals.get(agent_id, {}).get("ecu_claim_total", ZERO),
                        token="wallet_claim_total_invalid",
                    )
                ),
                "claim_kinds": sorted(set(claim_totals.get(agent_id, {}).get("claim_kinds", []))),
                "cluster_id": participants.get(agent_id, {}).get("cluster_id"),
                "node_name": participants.get(agent_id, {}).get("node_name"),
                "slot": participants.get(agent_id, {}).get("slot"),
                "variant": participants.get(agent_id, {}).get("variant"),
                "reward_status": (
                    "rewarded"
                    if to_decimal(balances.get(agent_id, "0"), token="wallet_balance_invalid") > ZERO
                    else "not_rewarded"
                ),
                "last_settled_epoch_id": epoch_id,
            }
            for agent_id, balance in (
                (agent_id, balances.get(agent_id, "0")) for agent_id in wallet_agent_ids
            )
        },
    }
    epoch_history = []
    ledger_state_path = output_root / "ledger_state.json"
    if ledger_state_path.is_file():
        ledger_state = _load_json(ledger_state_path)
        epoch_records = ledger_state.get("epoch_records")
        if isinstance(epoch_records, dict):
            epoch_history = list(epoch_records.values())
    for agent_id, row in wallet_payload["wallets"].items():
        _persist_agent_wallet_history(
            agent_id=agent_id,
            row=row,
            wallet_store=wallet_store,
            claims=claims,
            epoch_history=epoch_history,
            epoch_id=epoch_id,
            settlement_manifest=settlement_manifest,
            generated_at=wallet_payload["generated_at"],
        )
    wallet_path = output_root / "wallets.json"
    _write_json(wallet_path, wallet_payload)
    return {
        "version": RUNTIME_VERSION,
        "generated_at": wallet_payload["generated_at"],
        "wallet_count": len(wallet_payload["wallets"]),
        "rewarded_wallet_count": sum(
            1
            for row in wallet_payload["wallets"].values()
            if to_decimal(row["balance_ilc"], token="wallet_balance_invalid") > ZERO
        ),
        "latest_epoch_id": epoch_id,
        "claim_batch_sha256": claim_batch_sha256,
        "wallet_store_root": str(wallet_store_root),
        "store_kind": "lmdb",
        "wallet_path": str(wallet_path),
    }


def materialize_economic_cycle(*, scenario_root: Path, output_root: Path) -> dict[str, Any]:
    if not scenario_root.is_dir():
        raise EconomicCycleRuntimeError(f"scenario_root_missing:{scenario_root}")
    graph_root = output_root / "graph"
    economy_root = output_root / "economy"
    scenario_manifest = _load_json(scenario_root / "scenario_manifest.json")
    claims_payload = _load_json(scenario_root / "panel" / "ecu_claims.json")
    panel_payload = _load_json(scenario_root / "panel" / "panel_result.json")
    runtime_identity = _runtime_identity(
        scenario_manifest=scenario_manifest,
        claims_payload=claims_payload,
        panel_payload=panel_payload,
    )
    _assert_runtime_root_compatibility(output_root=output_root, runtime_identity=runtime_identity)
    graph_manifest = materialize_graph_state(scenario_root=scenario_root, output_root=graph_root)
    settlement_manifest = settle_economic_cycle(scenario_root=scenario_root, output_root=economy_root)
    wallet_manifest = export_wallet_state(
        scenario_root=scenario_root,
        output_root=economy_root,
        balances=settlement_manifest["balances"],
        settlement_manifest=settlement_manifest,
    )
    manifest = {
        "version": RUNTIME_VERSION,
        "generated_at": _utc_now(),
        "scenario_root": str(scenario_root),
        "runtime_identity": runtime_identity,
        "graph_manifest": graph_manifest,
        "settlement_manifest": settlement_manifest,
        "wallet_manifest": wallet_manifest,
        "runtime_store": {
            "store_kind": "lmdb_public_runtime_v0.1",
            "graph_store_root": graph_manifest["store_root"],
            "ledger_store_root": settlement_manifest["ledger_root"],
            "wallet_store_root": wallet_manifest["wallet_store_root"],
        },
        "summary": {
            "task_id": settlement_manifest["task_id"],
            "node_count": graph_manifest["node_count"],
            "support_link_count": graph_manifest["link_count"],
            "wallet_count": wallet_manifest["wallet_count"],
            "reward_total": settlement_manifest["reward_total"],
            "distribution_check_ok": settlement_manifest["distribution_check_ok"],
        },
    }
    _write_json(output_root / "manifest.json", manifest)
    return manifest
