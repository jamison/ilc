from typing import Optional
from .types import Node, Edge
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine
from .mining.benchmark import PoWBenchmark
from .economics.onboarding import OnboardingVault
import time

class EveAgent:
    def __init__(self, agent_id: str, graph: EpistemicGraph, consensus: ConsensusEngine, vault: Optional[OnboardingVault] = None):
        self.id = agent_id
        self.graph = graph
        self.consensus = consensus
        self.vault = vault
        
        self.wallet_balance = 0.0
        self.credit_balance = 0.0
        
        # Onboarding: Request Credit if Vault exists
        if self.vault:
            credit = self.vault.request_starter_credit(self.id)
            self.credit_balance += credit
            self.wallet_balance += credit # Credit is liquid for staking

        self.benchmark_engine = PoWBenchmark(matrix_size=1000)
        self.trust_vector = {
            "accuracy": 0.5,
            "precision": 0.5,
            "potential": 0.0,
            "tier": "unknown"
        }

    def perform_pow_benchmark(self) -> float:
        # Preserving Phase H Logic
        result = self.benchmark_engine.run(self.id)
        self.trust_vector["potential"] = result["score"]
        self.trust_vector["tier"] = result["tier"]
        print(f"[{self.id}] Hardware Verified: {result['device']} ({result['tier']})")
        return result["score"]

    def mine_thought(self, content: str, parent_id: str, stake: float) -> Optional[Node]:
        if self.wallet_balance < stake:
            print(f"[{self.id}] Insufficient funds to stake.")
            return None
            
        node = Node(id="", type="claim", content=content, agent_id=self.id, signature="sig")
        node.id = node.compute_id()
        edge = Edge(source_id=node.id, target_id=parent_id, type="derives_from")
        self.graph.add_node(node)
        self.graph.edges.append(edge)
        
        self.wallet_balance -= stake
        self.consensus.register_stake(node.id, stake)
        print(f"[{self.id}] Minted {node.id[:8]}")
        return node

    def receive_reward(self, amount: float):
        """Handle earnings and auto-repayment."""
        if self.vault:
            repayment, net = self.vault.process_repayment(self.id, amount)
            self.wallet_balance += net
            # Credit balance is technically liability, but simplistic tracking here:
            if repayment > 0:
                print(f"[{self.id}] Repaid {repayment:.4f}. Net Earnings: {net:.4f}")
        else:
            self.wallet_balance += amount

    def refute_node(self, target_id: str, stake: float):
        if self.wallet_balance < stake: return
        self.wallet_balance -= stake
        self.consensus.process_contradiction(target_id, stake)
