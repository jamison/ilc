from dataclasses import dataclass, field as dc_field
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, Set, Union
from datetime import datetime, timezone
import hashlib
import json

from pydantic import BaseModel, Field, field_serializer, field_validator

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, to_decimal

# THE KERNEL TAXONOMY
NodeType = Literal[
    "genesis",          # Axioms (Immutable)
    "claim",            # Assertions of truth
    "refutation",       # Counter-claims (Targeted attacks on validity)
    "task",             # Proof of Work (Method, Inputs, Artifacts)
    "star_map",         # Navigational Geometry (Vectors, Clusters)
    "proposal",         # Governance (Parameter changes)
    "genesis.schema",   # Meta: Defines new data structures
    "genesis.blob",     # Meta: Raw data adhering to a schema
    "hyperedge_entity", # Star-expanded hyperedge (ADR-0029 §2.3)
]

LinkType = Literal[
    "supports",
    "refutes",
    "equivalent",
    "depends_on",
]


def _parse_net_stake(value: object) -> Decimal:
    if value is None:
        return Decimal("0")
    return to_decimal(value, token="invalid_net_stake")

class Node(BaseModel):
    """
    The atomic unit of the Epistemological Graph.
    """
    id: str = Field(..., description="Unique Content ID (Hash)")
    type: NodeType
    # Content holds the payload. For 'claim' it might be text; for 'star_map' it's a Dict.
    content: Union[str, Dict[str, Any]] = Field(..., description="The payload")
    
    agent_id: str = Field(..., description="The Agent who minted this")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signature: str = Field(..., description="Cryptographic signature")
    
    # Epistemic State
    net_stake: Decimal = Field(default_factory=lambda: Decimal("0"))

    # Optional target for refutation-type nodes.
    # For now, used only when type == "refutation".
    target_id: Optional[str] = None
    # Optional parent lineage for claim/refutation nodes.
    parent_ids: List[str] = Field(default_factory=list)

    # ADR-0030: content-type tag enabling type-aware embedding selection.
    # Set at node creation time; retrofitting after the node store has volume is expensive.
    # Values: "text/plain", "text/markdown", "application/json", "image/*", etc.
    content_type: Optional[str] = None
    # ADR-0030: embedding vector, model name, and epoch stamp.
    # Populated asynchronously by the analytics embedding pipeline; None until then.
    embedding: Optional[List[float]] = None
    embedding_model: Optional[str] = None
    embedding_epoch: Optional[int] = None

    @field_validator("net_stake", mode="before")
    @classmethod
    def _validate_net_stake(cls, value: object) -> Decimal:
        return _parse_net_stake(value)

    @field_serializer("net_stake")
    def _serialize_net_stake(self, value: Decimal) -> str:
        return decimal_to_canonical_string(value)

    def _legacy_id_payload(self) -> bytes:
        """Build legacy SHA-256 payload bytes for offline migration tooling."""
        if isinstance(self.content, dict):
            payload_str = json.dumps(self.content, sort_keys=True)
        else:
            payload_str = str(self.content)

        # ID depends on Type, Content, and Author (Provenance)
        return f"{self.type}:{payload_str}:{self.agent_id}".encode()

    def compute_legacy_id(self) -> str:
        """Compute legacy SHA-256 hex node id contract (migration utility only)."""
        return hashlib.sha256(self._legacy_id_payload()).hexdigest()

    def _canonical_id_object(self) -> dict[str, Any]:
        """Build canonical object for CIDv1 node id generation."""
        return {
            "type": self.type,
            "content": self.content,
            "agent_id": self.agent_id,
        }

    def compute_canonical_id(self) -> str:
        """Compute canonical CIDv1 node id contract."""
        from ilc_core.encoding.cidv1 import node_id_from_obj

        return node_id_from_obj(self._canonical_id_object())

    def compute_id(self) -> str:
        """
        Default node id contract.

        Canonical-only CIDv1 over the canonical node-id object.
        Payloads that are not canonical DAG-CBOR encodable raise.
        """
        return self.compute_canonical_id()

class ClaimRecord(BaseModel):
    """
    Internal representation of a claim or refutation in the epistemic graph.

    This mirrors the protocol-level schema used in node_to_protocol_claim/refute
    and claims.csv export.
    """
    id: str
    type: str  # "claim" or "refutation" (or other future variants)
    agent_id: str
    content: str
    signature: Optional[str] = None
    net_stake: Decimal = Field(default_factory=lambda: Decimal("0"))
    timestamp: Optional[str] = None
    parent_ids: List[str] = Field(default_factory=list)
    target_id: Optional[str] = None

    @field_validator("net_stake", mode="before")
    @classmethod
    def _validate_net_stake(cls, value: object) -> Decimal:
        return _parse_net_stake(value)

    @field_serializer("net_stake")
    def _serialize_net_stake(self, value: Decimal) -> str:
        return decimal_to_canonical_string(value)

def node_to_claim_record(node: Node) -> ClaimRecord:
    """
    Convert a graph Node into a ClaimRecord. Assumes node.type is claim-like.
    """
    content_str = str(node.content)
    if isinstance(node.content, dict):
        # If content is dict, maybe it has the text? For now just stringify or extract 'text' if present?
        # Let's stick to stringifying for safety or assuming content IS the text for claims.
        content_str = node.content.get("text", json.dumps(node.content))
    
    # Timestamp: Node has datetime, ClaimRecord wants str (ISO).
    ts_str = node.timestamp.isoformat() if node.timestamp else None

    return ClaimRecord(
        id=node.id,
        type=node.type,
        agent_id=node.agent_id,
        content=content_str,
        signature=node.signature,
        net_stake=node.net_stake,
        timestamp=ts_str,
        parent_ids=list(node.parent_ids),
        target_id=node.target_id,
    )

def claim_record_to_node(claim: ClaimRecord) -> Node:
    """
    Convert a ClaimRecord into a generic Node suitable for EpistemicGraph.
    """
    # We need to handle timestamp conversion str -> datetime
    ts = datetime.now(timezone.utc)
    if claim.timestamp:
        try:
            ts = datetime.fromisoformat(claim.timestamp)
        except ValueError:
            pass
    if not claim.signature:
        raise ValueError("ClaimRecord signature required to create Node")

    return Node(
        id=claim.id,
        type=claim.type, # type: ignore (ClaimRecord type is str, Node type is Literal)
        content=claim.content,
        agent_id=claim.agent_id,
        timestamp=ts,
        signature=claim.signature,
        net_stake=claim.net_stake,
        target_id=claim.target_id,
        parent_ids=list(claim.parent_ids),
    )

class LinkRecord(BaseModel):
    """
    Internal representation of a link between two claims.

    'source_id' -> 'target_id' with a given link_type.
    """
    id: str
    link_type: LinkType
    source_id: str
    target_id: str
    # Optional: timestamp, creator_agent_id, meta
    timestamp: Optional[str] = None
    agent_id: Optional[str] = None


# ADR-0029: Hypergraph substrate — n-ary relationships.
#
# HyperEdge connects any subset of graph nodes (|members| >= 2).
# Directed hyperedges use head_ids (source set) and tail_ids (target set).
# Undirected hyperedges populate member_ids only; head_ids and tail_ids are empty.
#
# weight is dynamic — callers must apply temporal decay (CDL-V1) before use.
# epoch stamps when this hyperedge was declared, enabling temporal analysis.
#
# star_expansion: to promote this hyperedge to a first-class epistemiological entity,
# create a Node(type="hyperedge_entity", id=self.id) and wire binary edges from each
# member_id to it. See ADR-0029 §2.3 and graph.py expand_hyperedge_to_star_node().
# Do not call star expansion before CDL: Hyperedge ECU Attribution is ratified.
#
# spectral_fingerprint: cached local top-k eigenvalue vector used for spectral beacon
# emission (SIM-BEACON-01 gate). None until analytics pipeline populates it.
@dataclass(frozen=True)
class HyperEdge:
    id: str                                       # content-addressed ID
    hyperedge_type: str                           # "panel" | "co_authorship" | "refutation_coalition" | "epoch_boundary"
    member_ids: List[str]                         # all members (undirected) or union of head+tail (directed)
    head_ids: List[str]                           # directed source set; empty list if undirected
    tail_ids: List[str]                           # directed target set; empty list if undirected
    weight: Decimal                               # W(e) — caller responsible for CDL-V1 decay
    epoch: int                                    # temporal stamp
    agent_id: str                                 # declaring agent
    signature: str                                # attribution
    spectral_fingerprint: Optional[List[float]] = dc_field(default=None)  # analytics-populated; gate: SIM-BEACON-01
