# ilc_core/economics/entropy.py

from __future__ import annotations
from typing import Optional

def learning_signal(success_rate: float) -> float:
    """
    Symmetric bell-shaped learning signal in [0, 0.25].

    For a given empirical success rate p ∈ [0, 1], the signal is:
        L(p) = p * (1 - p)

    Intuition:
    - p ~ 0.0  → task is too hard, no gradient.
    - p ~ 1.0  → task is solved, no gradient.
    - p ~ 0.5  → maximal "learning juice".
    """
    p = max(0.0, min(1.0, float(success_rate)))
    return p * (1.0 - p)


def entropy_weight(
    success_rate: float,
    min_floor: float = 0.5,
    max_cap: float = 2.0,
) -> float:
    """
    Map learning_signal(p) into a multiplicative weight ∈ [min_floor, max_cap].

    We normalize L(p) ∈ [0, 0.25] by scaling and shifting into the target band.

    This is intentionally soft and purely experimental. It does NOT affect
    Governance or ECU-based minimum fees; it only modulates reward in sims.
    """
    base_signal = learning_signal(success_rate)  # in [0, 0.25]
    # Normalize to [0, 1]
    normalized = base_signal / 0.25 if base_signal > 0 else 0.0

    span = max_cap - min_floor
    return min_floor + span * normalized
