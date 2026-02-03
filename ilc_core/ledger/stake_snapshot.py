"""
Stake snapshot model for calculating reward distribution shares.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StakeSnapshot:
    """
    Represents the stake distribution at the start of a specific epoch.
    Required for deterministic reward calculation.
    """
    epoch_id: str
    epoch_index: int
    namespace_id: str
    stakes: Dict[str, float]  # agent_id -> stake amount
    total_stake: float
    created_at: str  # ISO8601

    def __post_init__(self):
        """Validate stake integrity."""
        calculated_total = sum(self.stakes.values())
        # Use small epsilon for float comparison if needed, but strict equality is better for deterministic ledger
        if abs(calculated_total - self.total_stake) > 1e-9:
            raise ValueError(
                f"total_stake ({self.total_stake}) matches sum of stakes ({calculated_total})"
            )
        if any(s < 0 for s in self.stakes.values()):
            raise ValueError("All stake values must be non-negative")


def compute_total_stake(stakes: Dict[str, float]) -> float:
    """Compute total stake from a mapping of agent stakes."""
    return sum(stakes.values())
