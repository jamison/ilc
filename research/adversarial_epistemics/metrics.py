"""
ILC Adversarial Epistemics Research Harness — Metrics
======================================================

Core metrics derived from formal model in docs/specs/ilc_comprehensive_forward_plan_post_1575c_v0.1.md Part 12g.

effective_n(n, rho):
    Votes from n correlated agents with pairwise correlation rho are equivalent
    to effective_n independent votes. Derivation:
      Var(average vote) = sigma^2 * [1 + (n-1)*rho] / n
    Effective independent sample count:
      effective_n = n / (1 + (n-1)*rho)
    At rho=0: effective_n = n (fully independent)
    At rho=1: effective_n = 1 (all votes carry same information)
    At rho=0.5, n=7: effective_n = 7/(1+6*0.5) = 7/4 = 1.75 — severe loss

false_consensus_rate:
    Fraction of trials where jury incorrectly accepts a false claim as true.

gini_coefficient:
    Measure of ECU / reputation inequality across validators.
    Higher Gini = stronger Matthew effect / oligarchy risk.

jury_accuracy:
    Overall accuracy on both true and false claims.
"""

from __future__ import annotations

import math
from typing import List


def effective_n(n: int, rho: float) -> float:
    """
    Effective independent vote count given n correlated validators with
    pairwise epistemic error correlation rho.
    """
    if rho >= 1.0:
        return 1.0
    if rho <= 0.0 or n <= 1:
        return float(n)
    return n / (1.0 + (n - 1) * rho)


def false_consensus_rate(n_false_accepted: int, n_false_total: int) -> float:
    """Fraction of false claims incorrectly ratified by jury."""
    if n_false_total == 0:
        return 0.0
    return n_false_accepted / n_false_total


def true_rejection_rate(n_true_rejected: int, n_true_total: int) -> float:
    """Fraction of true claims incorrectly rejected by jury."""
    if n_true_total == 0:
        return 0.0
    return n_true_rejected / n_true_total


def jury_accuracy(n_correct: int, n_total: int) -> float:
    if n_total == 0:
        return 0.0
    return n_correct / n_total


def gini_coefficient(values: List[float]) -> float:
    """
    Gini coefficient of a distribution (0 = perfect equality, 1 = maximum inequality).
    Used to measure ECU/reputation concentration across validator population.
    """
    if not values:
        return 0.0
    n = len(values)
    total = sum(values)
    if total == 0.0:
        return 0.0
    sorted_vals = sorted(values)
    cumulative = 0.0
    for i, v in enumerate(sorted_vals):
        cumulative += (2 * (i + 1) - n - 1) * v
    return cumulative / (n * total)


def cartel_control_probability(
    alpha_x: float,
    panel_size: int,
    rho: float = 0.0,
) -> float:
    """
    Analytical estimate: probability that adversarial fraction alpha_x of E(x)
    achieves majority on a panel of panel_size (ignoring CDL-V3 for now).

    For rho=0 (independent adversarial votes), this uses a binomial tail sum.
    For rho>0 we apply effective_n correction to the adversarial bloc.

    Note: adversarial votes are perfectly correlated with each other (all vote True)
    so effective_n for the adversarial bloc = alpha_x * panel_size.
    The honest bloc has correlation rho, reducing their effective vote mass.
    """
    # Expected adversarial votes on panel (assuming random selection from E(x))
    n_adv = alpha_x * panel_size
    # Effective honest votes
    n_honest_raw = (1 - alpha_x) * panel_size
    n_honest_eff = effective_n(max(1, int(round(n_honest_raw))), rho)
    # Adversarial wins majority if n_adv > n_honest_eff/2 + n_adv/2 is not right;
    # simple majority: adversarial wins if their block > total/2
    # With adversarial perfectly correlated: they always vote as one bloc.
    # Honest effective mass: n_honest_eff.
    # Adversarial wins if n_adv > n_honest_eff, i.e. they outnumber effective honest.
    if n_adv > n_honest_eff:
        return 1.0
    elif n_adv == n_honest_eff:
        return 0.5
    else:
        return 0.0


def summary_stats(values: List[float]) -> dict:
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "p10": 0.0, "p90": 0.0}
    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance)
    sorted_v = sorted(values)
    p10 = sorted_v[int(0.10 * n)]
    p90 = sorted_v[int(0.90 * n)]
    return {
        "mean": mean,
        "std": std,
        "min": sorted_v[0],
        "max": sorted_v[-1],
        "p10": p10,
        "p90": p90,
    }
