from typing import Dict, Optional
from ..types import Node, Edge
from ..graph import EpistemicGraph

class ConsensusEngine:
    def __init__(self, graph: EpistemicGraph):
        self.graph = graph
        # Ledger: Node ID -> Staked Amount (Float)
        self.node_stakes: Dict[str, float] = {}
    
    def register_stake(self, node_id: str, amount: float):
        """Called when an agent Supports a node."""
        if amount < 0: raise ValueError("Cannot stake negative amount")
        
        current = self.node_stakes.get(node_id, 0.0)
        self.node_stakes[node_id] = current + amount
        print(f"[Consensus] Stake added to {node_id[:8]}. Net: {self.node_stakes[node_id]}")

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
