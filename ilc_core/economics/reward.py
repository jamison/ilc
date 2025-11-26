from __future__ import annotations

from typing import Optional
from .entropy import entropy_weight


def simple_claim_reward(
    stake_spent: float,
    potential: float,
    reuse_count: int = 0,
    success_rate: Optional[float] = None,
) -> float:
    """
    MVP / Simulation-only reward function.
    
    Returns:
        reward_amount (float): The amount of ILC to mint as reward.
        
    Formula (Sim-Only):
        Base Reward = stake_spent + (0.5 * potential * stake_spent)
        
        If success_rate is provided (Phase 10), we apply an entropy multiplier:
            Multiplier = entropy_weight(success_rate)  (in [0.5, 2.0])
            Final Reward = Base Reward * Multiplier
            
    NOTE: This is NOT the final ILC monetary policy. It is a placeholder
    to allow agents to earn back what they spend plus a margin, so they
    don't go bankrupt in long-running simulations.
    """
    # 1. Base recovery of stake
    if stake_spent <= 0.0:
        return 0.0

    base = stake_spent
    
    # 2. Profit margin based on potential
    # e.g. if potential is 1.0, margin is 50%. If 0.0, margin is 0%.
    margin = 0.5 * potential * stake_spent
    
    total = base + margin

    # 3. Optional Entropy Weighting (Phase 10)
    if success_rate is not None:
        w = entropy_weight(success_rate)
        total *= w
        
    return total
