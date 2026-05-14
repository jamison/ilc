from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal, ROUND_DOWN
import hashlib
import json
from typing import Mapping, TypedDict, TypeAlias

from ilc_core.ledger.backend import EpochRecord
from ilc_core.ledger.exact_numeric import (
    ZERO,
    decimal_to_canonical_string,
    normalize_json_scalars,
    to_decimal,
)
from ilc_core.ledger.stake_snapshot import StakeSnapshot


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
_SETTLEMENT_QUANTUM = Decimal("0.000000001")


class SettlementVerificationResult(TypedDict):
    ok: bool
    total_delta: str
    expected_total: str
    max_agent_error: str
    top_errors: list[str]
    error_note: str
    input_hash: str


def _quantize_distribution_amount(amount: Decimal) -> Decimal:
    return amount.quantize(_SETTLEMENT_QUANTUM, rounding=ROUND_DOWN)


def _expected_distribution(
    snapshot: StakeSnapshot,
    reward_total: Decimal,
) -> dict[str, Decimal]:
    if snapshot.total_stake <= ZERO:
        return {}
    expected: dict[str, Decimal] = {}
    running_total = ZERO
    stake_items = sorted(snapshot.stakes.items(), key=lambda item: item[0])
    for index, (agent_id, stake) in enumerate(stake_items):
        if index == len(stake_items) - 1:
            share = reward_total - running_total
        else:
            share = _quantize_distribution_amount(
                (stake / snapshot.total_stake) * reward_total
            )
            running_total += share
        expected[agent_id] = share
    return expected


def hash_inputs(
    epoch_record: EpochRecord,
    snapshot: StakeSnapshot | None,
    balances_before: Mapping[str, object],
    balances_after: Mapping[str, object],
) -> str:
    """
    Create a deterministic hash of the verification inputs.
    """
    # Deterministic sorting
    input_data: JsonObject = {
        "epoch_record": normalize_json_scalars(epoch_record),
        "snapshot": normalize_json_scalars(asdict(snapshot)) if snapshot else None,
        "balances_before": normalize_json_scalars(dict(sorted(balances_before.items()))),
        "balances_after": normalize_json_scalars(dict(sorted(balances_after.items()))),
    }
    dump = json.dumps(
        input_data,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()


def verify_stake_distribution(
    epoch_record: EpochRecord,
    snapshot: StakeSnapshot | None,
    balances_before: Mapping[str, object],
    balances_after: Mapping[str, object],
) -> SettlementVerificationResult:
    """
    Verify that reward distribution matches the stake snapshot and expected total.
    """
    status = epoch_record.get("distribution_status")

    # Extract total reward (robust access)
    summary = epoch_record.get("summary", {})
    if isinstance(summary, dict):
        reward_total = to_decimal(
            summary.get("reward_total", "0"),
            token="settlement_reward_total_invalid",
        )
    else:
        reward_total = ZERO

    deltas: dict[str, Decimal] = {}
    # We care about all agents in the snapshot, plus any that appeared in balances.
    all_agents = set(balances_before.keys()) | set(balances_after.keys())
    if snapshot:
        all_agents.update(snapshot.stakes.keys())

    for agent_id in all_agents:
        before = to_decimal(
            balances_before.get(agent_id, "0"),
            token="settlement_balance_before_invalid",
        )
        after = to_decimal(
            balances_after.get(agent_id, "0"),
            token="settlement_balance_after_invalid",
        )
        delta = after - before
        if delta != ZERO or agent_id in (snapshot.stakes if snapshot else []):
            deltas[agent_id] = delta

    total_delta = sum(deltas.values(), ZERO)
    expected_total = reward_total if status == "distributed" else ZERO

    max_err = ZERO

    missing_snapshot = status == "distributed" and (
        snapshot is None or snapshot.total_stake <= ZERO
    )

    if status == "distributed" and snapshot and snapshot.total_stake > ZERO:
        expected_distribution = _expected_distribution(snapshot, reward_total)
        for agent_id, expected in expected_distribution.items():
            actual = deltas.get(agent_id, ZERO)
            err = abs(actual - expected)
            max_err = max(max_err, err)

        # Also check if non-stakers got rewards
        for agent_id, delta in deltas.items():
            if agent_id not in snapshot.stakes and delta != ZERO:
                max_err = max(max_err, abs(delta))

    elif status == "stub_no_snapshot":
        # Expect zero changes
        max_err = max((abs(v) for v in deltas.values()), default=ZERO)

    # Check bounds
    ok_total = abs(total_delta - expected_total) <= _SETTLEMENT_QUANTUM
    ok_individual = max_err <= _SETTLEMENT_QUANTUM
    ok = ok_total and ok_individual and not missing_snapshot

    # Top errors
    error_map: dict[str, Decimal] = {}
    if status == "distributed" and snapshot and snapshot.total_stake > ZERO:
        expected_distribution = _expected_distribution(snapshot, reward_total)
        for agent_id in deltas.keys() | snapshot.stakes.keys():
            actual = deltas.get(agent_id, ZERO)
            expected = expected_distribution.get(agent_id, ZERO)
            error_map[agent_id] = abs(actual - expected)
    else:
        for agent_id, delta in deltas.items():
            error_map[agent_id] = abs(delta)

    top_errors = sorted(error_map.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top_errors_formatted = [
        f"{k}:{decimal_to_canonical_string(v)}"
        for k, v in top_errors
        if v != ZERO
    ]
    if missing_snapshot:
        top_errors_formatted.insert(0, "missing_snapshot_or_total_stake")

    return {
        "ok": ok,
        "total_delta": decimal_to_canonical_string(total_delta),
        "expected_total": decimal_to_canonical_string(expected_total),
        "max_agent_error": decimal_to_canonical_string(max_err),
        "top_errors": top_errors_formatted,
        "error_note": "distributed_without_snapshot" if missing_snapshot else "",
        "input_hash": hash_inputs(epoch_record, snapshot, balances_before, balances_after),
    }
