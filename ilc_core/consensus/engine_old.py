from typing import Dict, Optional
import math
import time
from datetime import timezone
from ..types import Node, Edge
from ..graph import EpistemicGraph
from .clustering import SponsorGraph
from .governance import Governance # New Import

class ConsensusEngine:
    def __init__(self, graph: EpistemicGraph):
        self.graph = graph
        # Ledger: Node ID -> Staked Amount (Float)
        self.node_stakes: Dict[str, float] = {}
        self.sponsor_graph = SponsorGraph()
        self.governance = Governance() # The Fed
    
    def register_stake(self, node_id: str, amount: float):
        """Called when an agent Supports a node."""
        if amount < 0: raise ValueError("Cannot stake negative amount")
        
        # Enforce Minimum Fee based on Current Network Power
        required_fee = self.governance.get_dynamic_fee()
        
        if amount < required_fee:
            print(f"[Consensus] REJECTED: Stake {amount} < Min Fee {required_fee}")
            return False
            
        current = self.node_stakes.get(node_id, 0.0)
        self.node_stakes[node_id] = current + amount
        print(f"[Consensus] Stake accepted ({amount} ILC). Min Fee was {required_fee}")
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

    def get_node_age(self, node: Node) -> float:
        # In sim, we might use epochs. In real code, seconds.
        now = time.time()
        # Mock timestamp for simulation if needed, else real delta
        ts = node.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return max(1.0, now - ts.timestamp())

    def calculate_maintenance_tax(self, node: Node) -> float:
        """
        The Shield: Older, reused nodes pay less tax.
        """
        age = self.get_node_age(node)
        # Reuse count simulated by net_stake for now
        reuse_factor = max(1.0, node.net_stake) 
        
        base_tax = 0.01 # 1% per epoch
        # Decay tax as age and reuse increase
        tax_rate = base_tax / (1 + math.log(age * reuse_factor))
        return tax_rate

    def calculate_refutation_bounty(self, node: Node) -> float:
        """
        The Sword: Older nodes are worth more to destroy.
        Paradigm Shift Bonus = Age^1.4 (Tuned for Safety)
        """
        base_stake = self.node_stakes.get(node.id, 0.0)
        age = self.get_node_age(node)
        
        # Tuned to 1.4 to ensure EV < 0 for looting attacks at 1% error rate
        paradigm_bonus = 0.001 * math.pow(age, 1.4)
        
        total_bounty = base_stake + paradigm_bonus
        print(f"[Consensus] Node {node.id[:8]} Age: {age:.1f}s. Bounty: {total_bounty:.4f} (Bonus: {paradigm_bonus:.4f})")
        return total_bounty

    def process_contradiction(self, target_id: str, stake_amount: float):
        if target_id not in self.graph.nodes: return
        node = self.graph.nodes[target_id]
        
        bounty = self.calculate_refutation_bounty(node)
        
        # The Slash
        current = self.node_stakes.get(target_id, 0.0)
        new_balance = current - stake_amount # Simple slash for now
        self.node_stakes[target_id] = new_balance
        
        print(f"[Consensus] ⚔️ PARADIGM SHIFT! Refuter earns Jackpot: {bounty:.4f} ILC")
        # In real system: Transfer 'bounty' to refuter agent

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
