# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Reward helpers for the ILC economics sandbox.

This module defines simple_claim_reward(...), which turns ECU-like stake_spent,
hardware potential, and an entropy-weighted learning signal (optional success_rate)
into a single Decimal reward. It is used in simulations to explore incentives and
does not yet define the final L1 protocol reward schedule.

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional
from .entropy import entropy_weight


def simple_claim_reward(
    stake_spent: Decimal,
    potential: Decimal = Decimal("0"),
    success_rate: object | None = None,
) -> Decimal:
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
            A single Decimal reward_paid in ILC units for this one task. The economics
        sandbox uses this as a scalar signal; it does not yet model full protocol
        distribution or multi-recipient payouts.
    """
    stake_spent_amount = _reward_decimal(stake_spent, "reward_stake_spent_invalid")
    potential_amount = _reward_decimal(potential, "reward_potential_invalid")

    # 1. Base recovery of stake
    if stake_spent_amount < Decimal("0"):
        raise ValueError(f"stake_spent cannot be negative: {stake_spent_amount}")
    if stake_spent_amount == Decimal("0"):
        return Decimal("0")

    base = stake_spent_amount
    
    # 2. Profit margin based on potential
    # e.g. if potential is 1.0, margin is 50%. If 0.0, margin is 0%.
    margin = Decimal("0.5") * potential_amount * stake_spent_amount
    
    total = base + margin

    # 3. Optional Entropy Weighting (Phase 10)
    if success_rate is not None:
        w = entropy_weight(success_rate)
        total *= w
        
    return total


def _reward_decimal(value: object, token: str) -> Decimal:
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
    return amount
