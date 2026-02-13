from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from typing import Mapping, TypedDict, TypeAlias

from ilc_core.ledger.backend import EpochRecord
from ilc_core.ledger.stake_snapshot import StakeSnapshot


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class SettlementVerificationResult(TypedDict):
    ok: bool
    total_delta: float
    expected_total: float
    max_agent_error: float
    top_errors: list[str]
    error_note: str
    input_hash: str


def hash_inputs(
    epoch_record: EpochRecord,
    snapshot: StakeSnapshot | None,
    balances_before: Mapping[str, float],
    balances_after: Mapping[str, float],
) -> str:
    """
    Create a deterministic hash of the verification inputs.
    """
    # Deterministic sorting
    input_data: JsonObject = {
        "epoch_record": epoch_record,
        "snapshot": asdict(snapshot) if snapshot else None,
        "balances_before": dict(sorted(balances_before.items())),
        "balances_after": dict(sorted(balances_after.items())),
    }
    dump = json.dumps(input_data, sort_keys=True, default=str)
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()[:16]


def verify_stake_distribution(
    epoch_record: EpochRecord,
    snapshot: StakeSnapshot | None,
    balances_before: Mapping[str, float],
    balances_after: Mapping[str, float],
) -> SettlementVerificationResult:
    """
    Verify that reward distribution matches the stake snapshot and expected total.
    """
    eps = 1e-6
    status = epoch_record.get("distribution_status")

    # Extract total reward (robust access)
    summary = epoch_record.get("summary", {})
    if isinstance(summary, dict):
        reward_total = float(summary.get("reward_total", 0.0))
    else:
        # Defensive fallback
        reward_total = 0.0

    # Compute actual deltas
    deltas: dict[str, float] = {}
    # We care about all agents in the snapshot, plus any that appeared in balances.
    all_agents = set(balances_before.keys()) | set(balances_after.keys())
    if snapshot:
        all_agents.update(snapshot.stakes.keys())

    for agent_id in all_agents:
        before = float(balances_before.get(agent_id, 0.0))
        after = float(balances_after.get(agent_id, 0.0))
        delta = after - before
        if abs(delta) > eps or agent_id in (snapshot.stakes if snapshot else []):
            deltas[agent_id] = delta

    total_delta = sum(deltas.values())
    expected_total = reward_total if status == "distributed" else 0.0

    max_err = 0.0

    missing_snapshot = status == "distributed" and (
        snapshot is None or snapshot.total_stake <= 0
    )

    if status == "distributed" and snapshot and snapshot.total_stake > 0:
        for agent_id, stake in snapshot.stakes.items():
            expected = (stake / snapshot.total_stake) * reward_total
            actual = deltas.get(agent_id, 0.0)
            err = abs(actual - expected)
            max_err = max(max_err, err)

        # Also check if non-stakers got rewards
        for agent_id, delta in deltas.items():
            if agent_id not in snapshot.stakes and abs(delta) > eps:
                max_err = max(max_err, abs(delta))

    elif status == "stub_no_snapshot":
        # Expect zero changes
        max_err = max((abs(v) for v in deltas.values()), default=0.0)

    # Check bounds
    ok_total = abs(total_delta - expected_total) <= eps
    ok_individual = max_err <= eps
    ok = ok_total and ok_individual and not missing_snapshot

    # Top errors
    error_map: dict[str, float] = {}
    if status == "distributed" and snapshot and snapshot.total_stake > 0:
        for agent_id in deltas.keys() | snapshot.stakes.keys():
            actual = deltas.get(agent_id, 0.0)
            stake = snapshot.stakes.get(agent_id, 0.0)
            expected = (stake / snapshot.total_stake) * reward_total
            error_map[agent_id] = abs(actual - expected)
    else:
        for agent_id, delta in deltas.items():
            error_map[agent_id] = abs(delta)

    top_errors = sorted(error_map.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top_errors_formatted = [f"{k}:{v:.6f}" for k, v in top_errors if v > eps]
    if missing_snapshot:
        top_errors_formatted.insert(0, "missing_snapshot_or_total_stake")

    return {
        "ok": ok,
        "total_delta": total_delta,
        "expected_total": expected_total,
        "max_agent_error": max_err,
        "top_errors": top_errors_formatted,
        "error_note": "distributed_without_snapshot" if missing_snapshot else "",
        "input_hash": hash_inputs(epoch_record, snapshot, balances_before, balances_after),
    }
