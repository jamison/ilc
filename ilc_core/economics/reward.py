from __future__ import annotations

from typing import Optional


def simple_claim_reward(
    stake_amount: float,
    potential: float,
    reuse_count: int = 0,
) -> float:
    """
    MVP / Simulation-only reward function for mined claims.

    This is NOT the final ILC monetary policy. It is a toy function to enable
    simulations with a live reward loop.

    Intuition
    ---------
    - Higher stake should generally yield higher rewards.
    - Higher hardware/intelligence potential may slightly boost reward.
    - Reuse_count (how often a node is reused) could matter later; for now,
      we keep it optional and small.

    Parameters
    ----------
    stake_amount : float
        Amount staked on the claim.
    potential : float
        Agent's hardware/intelligence potential in [0, 1].
    reuse_count : int, optional
        Number of times this claim has been reused in the sim (for future use).

    Returns
    -------
    float
        Reward amount (generic units). For now, we keep this on the same
        numeric scale as stakes.
    """
    if stake_amount <= 0.0:
        return 0.0

    # Base reward proportional to stake.
    base = stake_amount

    # Small boost from potential (e.g. up to +50% for potential=1.0).
    potential_boost = 0.5 * potential * stake_amount

    # For now, ignore reuse_count or treat it as a tiny additive factor.
    reuse_boost = 0.0

    return base + potential_boost + reuse_boost
