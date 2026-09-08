"""
ILC Adversarial Epistemics Research Harness — Agent Population Generator
=========================================================================

Generates a synthetic validator population with:
  - Operator cluster assignment (CDL-V3 diversity constraint)
  - Per-domain expertise (Beta-distributed)
  - Correlation group assignment (intra-group epistemic correlation rho)
  - Strategy type: honest | adversarial | rational-adversarial
  - Reputation and ECU state (Werner decay model)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from model import SimulationConfig


@dataclass
class Agent:
    agent_index: int
    operator_cluster: int           # 0..n_operator_clusters-1
    correlation_group: int          # agents in same group share epistemic noise
    domain_expertise: Dict[int, float]  # domain -> expertise score (0..1)
    strategy: str                   # "honest" | "adversarial" | "rational"
    reputation: float = 1.0         # current reputation weight
    ecu: float = 0.0                # accumulated ECU (Werner)
    base_accuracy: float = 0.75     # honest vote accuracy when fully expert

    def expertise_for(self, domain: int) -> float:
        return self.domain_expertise.get(domain, 0.0)

    def qualifies_for(self, domain: int, threshold: float) -> bool:
        return self.expertise_for(domain) >= threshold


def build_population(cfg: SimulationConfig, rng: np.random.Generator) -> List[Agent]:
    """
    Build a synthetic validator population respecting CDL-V3 constraints.

    Correlation groups are assigned so that within a group, validators share
    epistemic priors (same training corpus proxy). Operator clusters are
    independent from correlation groups — an operator can run validators
    from multiple correlation groups, and a correlation group can span operators.

    For the LLM-correlation scenario: set n_correlation_groups < n_validators
    to represent multiple validators derived from the same base model.
    """
    agents: List[Agent] = []

    # Distribute validators evenly across operator clusters
    cluster_sizes = _distribute_evenly(cfg.n_validators, cfg.n_operator_clusters)

    # Distribute correlation groups (independent of operator assignment)
    # Default: n_correlation_groups = n_operator_clusters (varied in SIM-LLM-CORR-01)
    n_corr_groups = cfg.n_operator_clusters
    corr_group_assignments = rng.integers(0, n_corr_groups, size=cfg.n_validators)

    # Build expertise matrix: Beta(2,5) => mean ~0.286, right-tail for specialists
    expertise_matrix = rng.beta(2, 5, size=(cfg.n_validators, cfg.n_domains))

    idx = 0
    for cluster_id, cluster_size in enumerate(cluster_sizes):
        for _ in range(cluster_size):
            domain_expertise = {
                d: float(expertise_matrix[idx, d])
                for d in range(cfg.n_domains)
            }
            agents.append(Agent(
                agent_index=idx,
                operator_cluster=cluster_id,
                correlation_group=int(corr_group_assignments[idx]),
                domain_expertise=domain_expertise,
                strategy="honest",   # override below for adversarial variants
                reputation=1.0,
                ecu=0.0,
                base_accuracy=rng.beta(7, 3),  # mean ~0.70, most validators honest-competent
            ))
            idx += 1

    return agents


def inject_adversarial_fraction(
    agents: List[Agent],
    eligible: List[int],     # indices in E(x) for this claim domain
    alpha_x: float,          # adversarial fraction of E(x)
    strategy: str,           # "adversarial" or "rational"
    rng: np.random.Generator,
) -> List[Agent]:
    """
    Convert a fraction alpha_x of eligible validators to adversarial strategy.
    Returns a NEW list (does not mutate the original population).
    """
    agents = [Agent(**a.__dict__) for a in agents]  # shallow copy
    n_adversarial = int(len(eligible) * alpha_x)
    if n_adversarial == 0:
        return agents
    chosen = rng.choice(eligible, size=n_adversarial, replace=False)
    for idx in chosen:
        agents[idx].strategy = strategy
    return agents


def _distribute_evenly(total: int, n_groups: int) -> List[int]:
    base = total // n_groups
    remainder = total % n_groups
    return [base + (1 if i < remainder else 0) for i in range(n_groups)]
