"""
RL-style agents for the ILC economics sandbox.

This module defines simple agents that implement the RLHook interface to
consume economic telemetry and adapt their behavior (e.g. domain selection).
"""
from __future__ import annotations
import random
from typing import Dict, List

from .telemetry import RLHook
from .outcome import TaskOutcome


class SimpleBanditHook(RLHook):
    """
    Simple epsilon-greedy bandit over discrete 'domains' using TaskOutcome.reward_paid
    as the reward signal.

    This is **sandbox-only** and not part of the L1 protocol. It exists to prove
    that our telemetry + outcome surfaces are usable by RL-style agents.
    """

    def __init__(self, domains: List[str], epsilon: float = 0.1):
        self.domains = domains
        self.epsilon = epsilon
        self.counts: Dict[str, int] = {d: 0 for d in domains}
        self.values: Dict[str, float] = {d: 0.0 for d in domains}

    def choose_domain(self) -> str:
        """
        Epsilon-greedy policy:
        - With probability epsilon: pick a random domain (explore).
        - Otherwise: pick the domain with highest estimated value (exploit).
        """
        if random.random() < self.epsilon:
            return random.choice(self.domains)
        
        # Exploit: find max value. Break ties arbitrarily (e.g. first found).
        # We can use max with key.
        best_domain = max(self.domains, key=lambda d: self.values[d])
        return best_domain

    def on_task_outcome(self, outcome: TaskOutcome) -> None:
        """
        Update bandit estimates based on outcome.domain and outcome.reward_paid.
        """
        arm = outcome.domain
        if arm not in self.domains:
            # Ignore outcomes for domains we don't know about
            return

        reward = outcome.reward_paid
        
        self.counts[arm] += 1
        n = self.counts[arm]
        old_value = self.values[arm]
        
        # Incremental mean update: Q_n+1 = Q_n + (R - Q_n) / n
        new_value = old_value + (reward - old_value) / float(n)
        self.values[arm] = new_value
