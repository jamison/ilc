from typing import Dict, Optional
from ..types import Node, Edge
from ..graph import EpistemicGraph
from .clustering import SponsorGraph

class ConsensusEngine:
    def __init__(self, graph: EpistemicGraph):
        self.graph = graph
        # Ledger: Node ID -> Staked Amount (Float)
        self.node_stakes: Dict[str, float] = {}
        self.sponsor_graph = SponsorGraph()
    
    def register_stake(self, node_id: str, amount: float):
        """Called when an agent Supports a node."""
        if amount < 0: raise ValueError("Cannot stake negative amount")
        
        current = self.node_stakes.get(node_id, 0.0)
        self.node_stakes[node_id] = current + amount
        print(f"[Consensus] Stake added to {node_id[:8]}. Net: {self.node_stakes[node_id]}")

    def register_sponsorship(self, sponsor_id: str, agent_id: str):
        """Records that Sponsor funds Agent."""
        self.sponsor_graph.union(sponsor_id, agent_id)

    def validate_independence(self, validators: list[str]) -> bool:
        """
        Sybil Check: Do these validators represent diverse capital?
        Returns True only if we have >= 3 distinct clusters.
        """
        unique_roots = self.sponsor_graph.get_cluster_count(validators)
        print(f"[Consensus] Independence Check: {len(validators)} agents -> {unique_roots} clusters.")
        return unique_roots >= 3

    def process_contradiction(self, target_id: str, stake_amount: float):
        """
        The 'Slash' Mechanism.
        Refutations are weighted 1.5x to incentivize error-finding.
        """
        current = self.node_stakes.get(target_id, 0.0)
        # The Slash: Remove the stake AND apply penalty logic (simplified here as subtraction)
        slash_impact = stake_amount * 1.5
        new_balance = current - slash_impact
        
        self.node_stakes[target_id] = new_balance
        print(f"[Consensus] ⚔️ CONTRADICTION! Node {target_id[:8]} slashed by {slash_impact}. Net: {new_balance}")

    def process_update(self, edge: Edge):
        """
        Handles 'supersedes' links.
        Unlike refutation, this does not slash. It deprecates.
        """
        if edge.type != "supersedes": return
        
        old_id = edge.target_id
        new_id = edge.source_id
        
        # In a full system, we would check if 'new_node' has enough stake/trust 
        # to actually replace 'old_node'. For MVP, we log the evolution.
        
        if old_id in self.node_stakes:
            print(f"[Consensus] 🔄 EVOLUTION: Node {new_id[:8]} supersedes {old_id[:8]}.")
            print(f"            (Old Node stake {self.node_stakes[old_id]} preserved, not slashed)")
        else:
            print(f"[Consensus] Warning: Superseded node {old_id[:8]} not found in ledger.")

    def is_canonical(self, node_id: str) -> bool:
        """
        The Truth Test.
        Genesis nodes are always true. Others need positive stake.
        """
        if node_id not in self.graph.nodes:
            return False
            
        node = self.graph.nodes[node_id]
        if node.type == "genesis":
            return True
            
        return self.node_stakes.get(node_id, 0.0) > 0
