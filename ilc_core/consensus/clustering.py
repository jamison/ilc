# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import Dict, List, Set

class SponsorGraph:
    def __init__(self):
        self.parents: Dict[str, str] = {}
        self.weights: Dict[str, float] = {}

    def find(self, agent_id: str) -> str:
        """Finds the 'Capital Root' of an agent."""
        if agent_id not in self.parents:
            self.parents[agent_id] = agent_id
            return agent_id
        
        # Path compression
        if self.parents[agent_id] != agent_id:
            self.parents[agent_id] = self.find(self.parents[agent_id])
        return self.parents[agent_id]

    def union(self, agent_a: str, agent_b: str):
        """Links two agents (e.g., Sponsor funds Agent)."""
        root_a = self.find(agent_a)
        root_b = self.find(agent_b)
        
        if root_a != root_b:
            # Simple union: attach B to A
            self.parents[root_b] = root_a

    def get_cluster_count(self, agents: List[str]) -> int:
        """Counts unique Capital Roots in a list of agents."""
        roots = {self.find(a) for a in agents}
        return len(roots)
