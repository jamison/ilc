import json
import os
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable, Protocol, Set, runtime_checkable
from ilc_core.types import (
    ClaimRecord,
    HyperEdge,
    LinkRecord,
    Node,
    claim_record_to_node,
    node_to_claim_record,
)
from ilc_core.exceptions import DuplicateNodeError, GraphIntegrityError, NodeNotFoundError
from ilc_core.links import is_symmetric, validate_link_type

logger = logging.getLogger(__name__)

# Track-1007 boundary: edge path is compatibility-only lineage relation.
EDGE_COMPATIBILITY_TYPES = frozenset({"derives_from"})


@dataclass(frozen=True)
class GraphEdge:
    """Compatibility lineage edge record (non-semantic relation surface)."""
    source_id: str
    target_id: str
    type: str
    weight: float = 1.0


@runtime_checkable
class EdgeEventLike(Protocol):
    source_id: str
    target_id: str
    type: str


class EpistemicGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.outgoing_edges: Dict[str, List[GraphEdge]] = {}
        self.incoming_edges: Dict[str, List[GraphEdge]] = {}
        self._edge_count: int = 0
        self.links: Dict[str, LinkRecord] = {}
        self.outgoing_links: Dict[str, List[str]] = {}
        self.incoming_links: Dict[str, List[str]] = {}
        self.genesis_hash: str = ""

        # ADR-0029: sparse hypergraph incidence index.
        # The explicit incidence matrix H (|V| x |E|) is NEVER stored; it is computed
        # on demand by analytics layers from these two dicts.
        # vertex_membership: node_id  -> set of hyperedge_ids (sparse H^T row)
        # hyperedge_members: hyperedge_id -> set of node_ids  (sparse H column)
        self.hyperedges: Dict[str, HyperEdge] = {}
        self.vertex_membership: Dict[str, Set[str]] = {}
        self.hyperedge_members: Dict[str, Set[str]] = {}

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
            logger.info("loaded_axiom: %s (%s)", node.content, node.id)

    def add_node(self, node: Node):
        if node.id in self.nodes:
            raise DuplicateNodeError(node.id, message="Node already exists")
        self.nodes[node.id] = node
        return True

    def _coerce_edge_event(self, edge_event: EdgeEventLike) -> GraphEdge:
        edge_type = str(edge_event.type)
        if edge_type not in EDGE_COMPATIBILITY_TYPES:
            raise GraphIntegrityError(
                f"edge_compatibility_type_unsupported:{edge_type}"
            )
        return GraphEdge(
            source_id=edge_event.source_id,
            target_id=edge_event.target_id,
            type=edge_type,
            weight=float(getattr(edge_event, "weight", 1.0)),
        )

    def add_edge(self, edge_event: EdgeEventLike) -> None:
        """Add compatibility lineage edge and update indexes."""
        edge = self._coerce_edge_event(edge_event)
        if edge.source_id not in self.nodes:
            raise NodeNotFoundError(
                edge.source_id, message=f"Unknown source_id: {edge.source_id}"
            )
        if edge.target_id not in self.nodes:
            raise NodeNotFoundError(
                edge.target_id, message=f"Unknown target_id: {edge.target_id}"
            )

        self.outgoing_edges.setdefault(edge.source_id, []).append(edge)
        self.incoming_edges.setdefault(edge.target_id, []).append(edge)
        self._edge_count += 1

    def add_edge_by_ids(self, source_id: str, target_id: str, edge_type: str) -> None:
        """Construct and add an edge using primitive ids for adapter-first callers."""
        self.add_edge(GraphEdge(source_id=source_id, target_id=target_id, type=edge_type))

    def edge_count(self) -> int:
        """Return current graph edge relation count."""
        return self._edge_count

    def iter_edges_from(self, source_id: str) -> Iterable[GraphEdge]:
        for edge in self.outgoing_edges.get(source_id, []):
            yield edge

    def iter_edges_to(self, target_id: str) -> Iterable[GraphEdge]:
        for edge in self.incoming_edges.get(target_id, []):
            yield edge

    def iter_edges_between(self, source_id: str, target_id: str) -> Iterable[GraphEdge]:
        for edge in self.iter_edges_from(source_id):
            if edge.target_id == target_id:
                yield edge

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
        """Add semantic relation link (`supports/refutes/equivalent/depends_on`)."""
        # Validate link_type
        link_type = validate_link_type(link.link_type)

        if link.id in self.links:
            raise GraphIntegrityError(f"Link with id={link.id} already exists")

        # Optional: ensure both endpoints exist as nodes
        if link.source_id not in self.nodes:
            raise NodeNotFoundError(
                link.source_id, message=f"Unknown source_id: {link.source_id}"
            )
        if link.target_id not in self.nodes:
            raise NodeNotFoundError(
                link.target_id, message=f"Unknown target_id: {link.target_id}"
            )

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

    # ADR-0029: hyperedge operations.

    def add_hyperedge(self, hyperedge: HyperEdge) -> None:
        """Add a hyperedge and update the sparse incidence index."""
        if hyperedge.id in self.hyperedges:
            raise GraphIntegrityError(f"HyperEdge with id={hyperedge.id} already exists")
        self.hyperedges[hyperedge.id] = hyperedge
        self.hyperedge_members[hyperedge.id] = set(hyperedge.member_ids)
        for node_id in hyperedge.member_ids:
            self.vertex_membership.setdefault(node_id, set()).add(hyperedge.id)

    def hyperedge_degree(self, node_id: str) -> int:
        """Number of hyperedges containing this node — O(1)."""
        return len(self.vertex_membership.get(node_id, set()))

    def hyperedges_containing(self, node_id: str) -> Iterable[HyperEdge]:
        """All hyperedges that include node_id."""
        for hid in self.vertex_membership.get(node_id, set()):
            yield self.hyperedges[hid]
