# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from decimal import Decimal
from typing import TypedDict, cast

from ilc_core.ledger.backend import EpochRecord, LedgerBackend
from ilc_core.ledger.exact_numeric import (
    decimal_to_canonical_string,
    parse_non_negative_decimal,
)


class SettlementMetricsResult(TypedDict):
    num_epochs_total: int
    num_epochs_settled: int
    num_epochs_rolled_back: int
    num_epochs_superseded: int
    num_snapshots: int
    total_rewards_distributed: str
    total_rewards_stubbed: str


def _reward_total_from_record(record: EpochRecord) -> Decimal:
    summary = record.get("summary", {})
    if isinstance(summary, dict):
        reward = summary.get("reward_total", "0")
        try:
            return parse_non_negative_decimal(
                reward,
                token="invalid_reward_total",
            )
        except ValueError:
            return Decimal("0")
    return Decimal("0")


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

    total_rewards_distributed = Decimal("0")
    total_rewards_stubbed = Decimal("0")

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
        "total_rewards_distributed": decimal_to_canonical_string(total_rewards_distributed),
        "total_rewards_stubbed": decimal_to_canonical_string(total_rewards_stubbed),
    }
