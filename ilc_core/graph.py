import json
import os
from typing import Dict, List, Optional
from .types import Node, Edge, ClaimRecord, claim_record_to_node, node_to_claim_record

class EpistemicGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.genesis_hash: str = ""

    def load_genesis(self, config_path="config/genesis.json"):
        """Hydrates the graph with the Axiomatic Core."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Genesis config missing: {config_path}")

        with open(config_path, "r") as f:
            data = json.load(f)
        
        # Create the 'Root' Genesis Node (Abstract container)
        # We use a placeholder sig/agent for the bootstrapping
        for axiom in data.get("axiomatic_core", []):
            node = Node(
                id=axiom["id"],  # Use the static ID from config
                type="genesis",
                content=axiom["claim"],
                agent_id="agent:genesis:00",
                signature="GENESIS_BOOTSTRAP_SIG",
                net_stake=axiom["weight"]
            )
            self.nodes[node.id] = node
            print(f"loaded_axiom: {node.content} ({node.id})")

    def add_node(self, node: Node):
        if node.id in self.nodes:
            raise ValueError("Node already exists")
        self.nodes[node.id] = node
        self.nodes[node.id] = node
        return True

    def add_claim(self, claim: ClaimRecord) -> None:
        node = claim_record_to_node(claim)
        self.add_node(node)

    def get_claim(self, claim_id: str) -> Optional[ClaimRecord]:
        node = self.nodes.get(claim_id)
        if node is None:
            return None
        # Only return if it's actually a claim/refutation
        if node.type not in ("claim", "refutation", "refute"):
            return None
        return node_to_claim_record(node)
