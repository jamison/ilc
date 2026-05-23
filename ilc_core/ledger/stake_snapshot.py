# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Stake snapshot model for calculating reward distribution shares.
"""

from decimal import Decimal
from dataclasses import dataclass
from typing import Dict

from ilc_core.ledger.exact_numeric import ZERO, to_decimal

@dataclass(frozen=True)
class StakeSnapshot:
    """
    Represents the stake distribution at the start of a specific epoch.
    Required for deterministic reward calculation.
    """
    epoch_id: str
    epoch_index: int
    namespace_id: str
    stakes: Dict[str, Decimal]  # agent_id -> stake amount
    total_stake: Decimal
    created_at: str  # ISO8601

    def __post_init__(self):
        """Validate stake integrity."""
        normalized_stakes = {
            agent_id: to_decimal(amount, token="stake_snapshot_stake_invalid")
            for agent_id, amount in self.stakes.items()
        }
        normalized_total = to_decimal(
            self.total_stake,
            token="stake_snapshot_total_stake_invalid",
        )
        object.__setattr__(self, "stakes", normalized_stakes)
        object.__setattr__(self, "total_stake", normalized_total)

        calculated_total = sum(self.stakes.values())
        if calculated_total != self.total_stake:
            raise ValueError(
                f"total_stake ({self.total_stake}) does not match sum of stakes ({calculated_total})"
            )
        if self.total_stake < ZERO:
            raise ValueError("total_stake_must_be_non_negative")
        if any(s < ZERO for s in self.stakes.values()):
            raise ValueError("All stake values must be non-negative")


def compute_total_stake(stakes: Dict[str, Decimal]) -> Decimal:
    """Compute total stake from a mapping of agent stakes."""
    return sum(stakes.values(), ZERO)
