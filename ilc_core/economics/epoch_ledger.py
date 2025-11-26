from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class EpochStats:
    tasks: int = 0
    ecu_spent: float = 0.0
    rewards_paid: float = 0.0


class SimpleEpochLedger:
    """
    Minimal per-epoch ledger for sims.

    - Tracks how many tasks ran in an epoch.
    - Tracks total ECU spent (stake) and total rewards paid (ILC units).
    - Can compute a simple "clearing price" P_e = rewards / ECU.
    """

    def __init__(self) -> None:
        self.epochs: Dict[int, EpochStats] = {}

    def record_task(self, epoch: int, ecu_spent: float, reward: float) -> None:
        stats = self.epochs.setdefault(epoch, EpochStats())
        stats.tasks += 1
        stats.ecu_spent += float(ecu_spent)
        stats.rewards_paid += float(reward)

    def get_epoch_stats(self, epoch: int) -> EpochStats:
        return self.epochs.get(epoch, EpochStats())

    def total_aggregate(self) -> EpochStats:
        """
        Aggregate across all epochs to a single EpochStats-like view.
        """
        agg = EpochStats()
        for stats in self.epochs.values():
            agg.tasks += stats.tasks
            agg.ecu_spent += stats.ecu_spent
            agg.rewards_paid += stats.rewards_paid
        return agg

    def clearing_price(self, epoch: int | None = None, eps: float = 1e-9) -> float:
        """
        If epoch is None -> use aggregate across all epochs.
        Otherwise -> use that epoch's stats.

        Returns ILC per ECU (dimensionless ratio).
        """
        if epoch is None:
            stats = self.total_aggregate()
        else:
            stats = self.get_epoch_stats(epoch)

        if stats.ecu_spent <= 0.0:
            return 0.0
        return stats.rewards_paid / max(eps, stats.ecu_spent)
