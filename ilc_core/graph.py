import json
import os
from typing import Dict, List, Optional, Iterable
from .types import Node, Edge, ClaimRecord, claim_record_to_node, node_to_claim_record, LinkRecord
from .links import validate_link_type, is_symmetric

class EpistemicGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.links: Dict[str, LinkRecord] = {}
        self.outgoing_links: Dict[str, List[str]] = {}
        self.incoming_links: Dict[str, List[str]] = {}
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

    def add_link(self, link: LinkRecord) -> None:
        # Validate link_type
        link_type = validate_link_type(link.link_type)

        if link.id in self.links:
            raise ValueError(f"Link with id={link.id} already exists")

        # Optional: ensure both endpoints exist as nodes
        if link.source_id not in self.nodes:
            raise KeyError(f"Unknown source_id: {link.source_id}")
        if link.target_id not in self.nodes:
            raise KeyError(f"Unknown target_id: {link.target_id}")

        self.links[link.id] = link

        self.outgoing_links.setdefault(link.source_id, []).append(link.id)
        self.incoming_links.setdefault(link.target_id, []).append(link.id)

        if is_symmetric(link_type) and link.source_id != link.target_id:
            # For symmetric links, we can add a mirrored representation if desired,
            # or leave symmetry semantics to higher layers. For MVP, we just
            # record the single directed link and rely on queries to treat it as symmetric.
            pass

    def iter_links_from(self, claim_id: str) -> Iterable[LinkRecord]:
        for link_id in self.outgoing_links.get(claim_id, []):
            yield self.links[link_id]

    def iter_links_to(self, claim_id: str) -> Iterable[LinkRecord]:
        for link_id in self.incoming_links.get(claim_id, []):
            yield self.links[link_id]

    def iter_links_between(self, source_id: str, target_id: str) -> Iterable[LinkRecord]:
        for link in self.iter_links_from(source_id):
            if link.target_id == target_id:
                yield link
