from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict


@dataclass
class EpochStats:
    tasks: int = 0
    ecu_spent: Decimal = Decimal("0")
    rewards_paid: Decimal = Decimal("0")


class SimpleEpochLedger:
    """
    Minimal per-epoch ledger for sims.

    - Tracks how many tasks ran in an epoch.
    - Tracks total ECU spent (stake) and total rewards paid (ILC units).
    - Can compute a simple "clearing price" P_e = rewards / ECU.
    """

    def __init__(self) -> None:
        self.epochs: Dict[int, EpochStats] = {}

    def record_task(self, epoch: int, ecu_spent: Decimal, reward: Decimal) -> None:
        stats = self.epochs.setdefault(epoch, EpochStats())
        stats.tasks += 1
        stats.ecu_spent += _coerce_decimal(ecu_spent, "epoch_ledger_ecu_spent_invalid")
        stats.rewards_paid += _coerce_decimal(reward, "epoch_ledger_reward_invalid")

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

    def clearing_price(
        self,
        epoch: int | None = None,
        eps: Decimal = Decimal("0.000000001"),
    ) -> Decimal:
        """
        If epoch is None -> use aggregate across all epochs.
        Otherwise -> use that epoch's stats.

        Returns ILC per ECU (dimensionless ratio).
        """
        if epoch is None:
            stats = self.total_aggregate()
        else:
            stats = self.get_epoch_stats(epoch)

        if stats.ecu_spent <= Decimal("0"):
            return Decimal("0")
        return stats.rewards_paid / max(eps, stats.ecu_spent)


def _coerce_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, (bool, float)):
        raise ValueError(token)
    if not isinstance(value, (Decimal, int, str)):
        raise ValueError(token)
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(f"{token}_non_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{token}_negative")
    return amount
