from typing import Optional
from .types import Node, Edge
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine
from .mining.benchmark import PoWBenchmark
import time

class EveAgent:
    def __init__(self, agent_id: str, graph: EpistemicGraph, consensus: ConsensusEngine):
        self.id = agent_id
        self.graph = graph
        self.consensus = consensus
        self.wallet_balance = 100.0
        self.benchmark_engine = PoWBenchmark(matrix_size=1000)
        
        self.trust_vector = {
            "accuracy": 0.5,
            "precision": 0.5,
            "potential": 0.0,
            "tier": "unknown"
        }

    def perform_pow_benchmark(self) -> float:
        """
        Runs the 'Check-In'. 
        Decides TASK based on Agent ID and Graph State.
        """
        # Pass Agent ID to enable Genesis Bypass and Task Sharding
        result = self.benchmark_engine.run(self.id)
        
        self.trust_vector["potential"] = result["score"]
        self.trust_vector["tier"] = result["tier"]
        
        print(f"[{self.id}] Hardware Verified: {result['device']} ({result['tier']})")
        print(f"[{self.id}] Performed Task: {result['task']} -> Score: {result['score']}")
        return result["score"]

    # ... (Keep mine_thought and refute_node as they were) ...
    def mine_thought(self, content: str, parent_id: str, stake: float) -> Optional[Node]:
        if self.wallet_balance < stake: return None
        node = Node(id="", type="claim", content=content, agent_id=self.id, signature="sig")
        node.id = node.compute_id()
        edge = Edge(source_id=node.id, target_id=parent_id, type="derives_from")
        self.graph.add_node(node)
        self.graph.edges.append(edge)
        self.wallet_balance -= stake
        self.consensus.register_stake(node.id, stake)
        print(f"[{self.id}] Minted {node.id[:8]}")
        return node

    def refute_node(self, target_id: str, stake: float):
        if self.wallet_balance < stake: return
        self.wallet_balance -= stake
        self.consensus.process_contradiction(target_id, stake)
