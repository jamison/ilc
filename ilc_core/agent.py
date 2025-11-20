from typing import Optional
from .types import Node, Edge
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine # New Import
import time
import random

class EveAgent:
    def __init__(self, agent_id: str, graph: EpistemicGraph, consensus: ConsensusEngine):
        self.id = agent_id
        self.graph = graph
        self.consensus = consensus # The Judge
        self.wallet_balance = 100.0 # Starter funds
        
    def perform_pow_benchmark(self) -> float:
        """Simulates Hardware Efficiency (0.0 - 1.0)"""
        return round(random.uniform(0.1, 0.9), 2)

    def mine_thought(self, content: str, parent_id: str, stake: float) -> Optional[Node]:
        """Creates a node and STAKES on it."""
        if self.wallet_balance < stake:
            print(f"[{self.id}] Insufficient funds to stake.")
            return None
            
        # 1. Create Node
        node = Node(
            id="", type="claim", content=content,
            agent_id=self.id, signature="sig"
        )
        node.id = node.compute_id()
        
        # 2. Link
        edge = Edge(source_id=node.id, target_id=parent_id, type="derives_from")
        self.graph.add_node(node)
        self.graph.edges.append(edge)
        
        # 3. Stake (Skin in the Game)
        self.wallet_balance -= stake
        self.consensus.register_stake(node.id, stake)
        
        print(f"[{self.id}] Minted & Staked {stake} on {node.id[:8]}")
        return node

    def refute_node(self, target_id: str, stake: float):
        """The Attack Move."""
        if self.wallet_balance < stake: return
        
        self.wallet_balance -= stake
        # In full version, we'd create a Refutation Node. Here we call the engine directly.
        self.consensus.process_contradiction(target_id, stake)
