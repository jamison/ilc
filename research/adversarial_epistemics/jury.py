"""
ILC Adversarial Epistemics Research Harness — Jury Formation and Voting
========================================================================

Jury selection respects CDL-V3 operator diversity constraint:
  max 1/3 of panel from same operator cluster.

Voting model:
  - Honest experts: stochastic signal with correlation rho
  - Honest non-experts: near-random (accuracy ~0.52)
  - Adversarial: always vote True regardless of ground truth

Correlated noise model (per SIM-CORR-01 specification):
  rho = sigma_shared^2 / (sigma_shared^2 + sigma_independent^2)
  with total variance = 1:
    sigma_shared      = sqrt(rho)
    sigma_independent = sqrt(1 - rho)

  For a claim with ground truth T in {True, False}:
    signal = +1 if T else -1
    vote_i = 1 if (signal + b_g + epsilon_i) > 0 else 0
  where b_g ~ N(0, sigma_shared^2) is shared within correlation group g,
  and epsilon_i ~ N(0, sigma_independent^2) is agent-specific.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Tuple

from model import MAX_OPERATOR_FRACTION_PER_PANEL, MIN_PANEL_SIZE
from agents import Agent


def select_jury(
    agents: List[Agent],
    eligible: List[int],     # indices into agents list
    panel_size: int,
    rng: np.random.Generator,
) -> List[int]:
    """
    Select panel_size validators from eligible, respecting CDL-V3 diversity.

    CDL-V3: no single operator cluster may contribute more than 1/3 of the panel.
    If the eligible population is too small or too concentrated to form a valid
    panel, returns the best-effort panel (smaller than panel_size or None if
    impossible).

    Returns a list of agent indices.
    """
    if len(eligible) < MIN_PANEL_SIZE:
        return list(eligible)  # under-staffed panel — recorded as a finding

    max_per_cluster = max(1, int(panel_size * MAX_OPERATOR_FRACTION_PER_PANEL))

    # Shuffle eligible pool
    pool = list(eligible)
    rng.shuffle(pool)

    panel: List[int] = []
    cluster_counts: Dict[int, int] = {}

    for idx in pool:
        cluster = agents[idx].operator_cluster
        if cluster_counts.get(cluster, 0) >= max_per_cluster:
            continue
        panel.append(idx)
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
        if len(panel) >= panel_size:
            break

    return panel


def cast_votes(
    agents: List[Agent],
    panel: List[int],
    ground_truth: bool,
    rho: float,
    rng: np.random.Generator,
    signal_strength: float = 1.0,
) -> Tuple[List[int], bool]:
    """
    Each panelist casts a vote (True=1 or False=0).
    Returns (votes_list, jury_verdict) where verdict is majority vote.

    signal_strength: scales the truth signal relative to unit noise.
      1.0 = strong (SIM-CORR-01 default)
      0.5 = medium
      0.2 = weak
      0.1 = marginal (claim near-indistinguishable from noise)

    Correlated noise:
      Group-level shared bias b_g ~ N(0, rho) (one per correlation group)
      Agent-level independent noise epsilon_i ~ N(0, 1-rho)

    Non-expert baseline: accuracy effectively 0.52 (near-chance).
    Expert honest: signal + noise with base_accuracy factored in.
    Adversarial: always votes True (=1).
    """
    signal = signal_strength if ground_truth else -signal_strength

    # Precompute shared group biases
    group_bias: Dict[int, float] = {}
    sigma_shared = float(np.sqrt(rho)) if rho > 0 else 0.0
    sigma_indep = float(np.sqrt(max(0.0, 1.0 - rho)))

    votes: List[int] = []
    for idx in panel:
        agent = agents[idx]

        if agent.strategy == "adversarial":
            votes.append(1)  # always votes True
            continue

        if agent.strategy == "rational":
            # Rational adversary votes True when they expect it to pass jury,
            # False otherwise. For Phase 1 simplicity: behaves like adversarial.
            votes.append(1)
            continue

        # Honest agent vote
        g = agent.correlation_group
        if g not in group_bias:
            group_bias[g] = rng.normal(0.0, sigma_shared) if sigma_shared > 0 else 0.0

        epsilon = rng.normal(0.0, sigma_indep) if sigma_indep > 0 else 0.0
        raw_signal = signal + group_bias[g] + epsilon
        votes.append(1 if raw_signal > 0 else 0)

    verdict = sum(votes) > len(votes) / 2
    return votes, verdict


def evaluate_jury_accuracy(
    agents: List[Agent],
    eligible: List[int],
    panel_size: int,
    ground_truth: bool,
    rho: float,
    rng: np.random.Generator,
    signal_strength: float = 1.0,
) -> bool:
    """Convenience wrapper: select jury, cast votes, return correctness."""
    panel = select_jury(agents, eligible, panel_size, rng)
    if not panel:
        return False
    _, verdict = cast_votes(agents, panel, ground_truth, rho, rng, signal_strength=signal_strength)
    return verdict == ground_truth
