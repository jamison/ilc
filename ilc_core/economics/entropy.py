# ilc_core/economics/entropy.py
"""
Entropy-based helpers for shaping rewards in the ILC economics sandbox.

These functions provide a simple "learning signal" over empirical success rates,
and a corresponding entropy_weight(...) that upweights mid-entropy domains and
downweights tasks that are either trivial (almost always succeed) or hopeless
(almost always fail).

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from __future__ import annotations
from typing import Optional

def learning_signal(success_rate: float) -> float:
    """
    Map a success_rate in [0, 1] to a "learning signal" scalar.

    The shape is intentionally peaked around medium success probabilities, so that
    tasks which are neither trivial nor impossible produce the strongest signal.
    This is a toy model used only in the economics sandbox, not a fixed part of
    the ILC protocol.
    """
    p = max(0.0, min(1.0, float(success_rate)))
    return p * (1.0 - p)


def entropy_weight(
    success_rate: float,
    min_floor: float = 0.5,
    max_cap: float = 2.0,
) -> float:
    """
    Compute an entropy-like weight for a given success_rate in [0, 1].

    The weight is larger for mid-range success rates (where entropy is high) and
    smaller near 0.0 or 1.0. Reward helpers such as simple_claim_reward can use
    this to reward work on "interesting" domains more than on trivial or solved
    ones. This is purely exploratory and parameterized for future tuning.
    """
    base_signal = learning_signal(success_rate)  # in [0, 0.25]
    # Normalize to [0, 1]
    normalized = base_signal / 0.25 if base_signal > 0 else 0.0

    span = max_cap - min_floor
    return min_floor + span * normalized
