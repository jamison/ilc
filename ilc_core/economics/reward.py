"""
Reward helpers for the ILC economics sandbox.

This module defines simple_claim_reward(...), which turns ECU-like stake_spent,
hardware potential, and an entropy-weighted learning signal (optional success_rate)
into a single float reward. It is used in simulations to explore incentives and
does not yet define the final L1 protocol reward schedule.

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from __future__ import annotations

from typing import Optional
from .entropy import entropy_weight


def simple_claim_reward(
    stake_spent: float,
    potential: float = 0.0,
    success_rate: float | None = None,
) -> float:
    """
    Compute an entropy-weighted reward for a single claim in the economics sandbox.

    Args:
        stake_spent: ECU-like quantity associated with this task in the sim. In current
            simulations this is often approximated using the governance fee.
        potential: Proxy for the agent's hardware or capability in [0, 1].
        success_rate: Optional empirical or assumed success probability in [0, 1].
            When provided, an entropy-based weight is applied via the helpers in
            ilc_core.economics.entropy.

    Returns:
        A single float reward_paid in ILC units for this one task. The economics
        sandbox uses this as a scalar signal; it does not yet model full protocol
        distribution or multi-recipient payouts.
    """
    # 1. Base recovery of stake
    if stake_spent < 0.0:
        raise ValueError(f"stake_spent cannot be negative: {stake_spent}")
    if stake_spent == 0.0:
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
