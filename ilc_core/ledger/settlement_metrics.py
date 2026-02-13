from __future__ import annotations

from typing import TypedDict, cast

from ilc_core.ledger.backend import EpochRecord, LedgerBackend


class SettlementMetricsResult(TypedDict):
    num_epochs_total: int
    num_epochs_settled: int
    num_epochs_rolled_back: int
    num_epochs_superseded: int
    num_snapshots: int
    total_rewards_distributed: float
    total_rewards_stubbed: float


def _reward_total_from_record(record: EpochRecord) -> float:
    summary = record.get("summary", {})
    if isinstance(summary, dict):
        reward = summary.get("reward_total", 0.0)
        if isinstance(reward, (int, float)):
            return float(reward)
    return 0.0


def compute_settlement_metrics(ledger: LedgerBackend) -> SettlementMetricsResult:
    """
    Compute aggregate metrics from the ledger's state.

    Returns a dictionary suitable for inclusion in experiment summaries.

    Assumptions:
    - Reads from `ledger.epoch_records` and `ledger.stake_snapshots`.
    - Intended for InMemory/File backends that expose those attributes.
    """
    records_obj = getattr(ledger, "epoch_records", {})
    snapshots_obj = getattr(ledger, "stake_snapshots", {})

    records = records_obj if isinstance(records_obj, dict) else {}
    snapshots = snapshots_obj if isinstance(snapshots_obj, dict) else {}

    # Initialize counters
    num_epochs_total = len(records)
    num_epochs_settled = 0
    num_epochs_rolled_back = 0
    num_epochs_superseded = 0

    total_rewards_distributed = 0.0
    total_rewards_stubbed = 0.0

    for rec_obj in records.values():
        if not isinstance(rec_obj, dict):
            continue
        rec = cast(EpochRecord, rec_obj)
        status = rec.get("status", "unknown")
        dist_status = rec.get("distribution_status", "unknown")

        if status == "settled":
            num_epochs_settled += 1
        elif status == "rolled_back":
            num_epochs_rolled_back += 1
        elif status == "superseded":
            num_epochs_superseded += 1

        reward = _reward_total_from_record(rec)

        if status == "settled":
            if dist_status == "distributed":
                total_rewards_distributed += reward
            elif dist_status == "stub_no_snapshot":
                total_rewards_stubbed += reward

    # Snapshot count
    num_snapshots = len(snapshots)

    return {
        "num_epochs_total": num_epochs_total,
        "num_epochs_settled": num_epochs_settled,
        "num_epochs_rolled_back": num_epochs_rolled_back,
        "num_epochs_superseded": num_epochs_superseded,
        "num_snapshots": num_snapshots,
        "total_rewards_distributed": total_rewards_distributed,
        "total_rewards_stubbed": total_rewards_stubbed,
    }
