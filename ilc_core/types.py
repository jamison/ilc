from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union, Dict, Any
from datetime import datetime
import hashlib
import json

# THE KERNEL TAXONOMY
NodeType = Literal[
    "genesis",          # Axioms (Immutable)
    "claim",            # Assertions of truth
    "refutation",       # Counter-claims (Targeted attacks on validity)
    "task",             # Proof of Work (Method, Inputs, Artifacts)
    "star_map",         # Navigational Geometry (Vectors, Clusters)
    "proposal",         # Governance (Parameter changes)
    "genesis.schema",   # Meta: Defines new data structures
    "genesis.blob"      # Meta: Raw data adhering to a schema
]

EdgeType = Literal[
    "supports",      # Validation (+Stake)
    "refutes",       # Contradiction (-Stake, Slash)
    "derives_from",  # Lineage (Task -> Claim)
    "equivalent",    # Dedup (A == B)
    "implements",    # Schema Compliance
    "relates_to",    # General link
    "supersedes"     # Versioning (New -> Old). No slashing.
]

class Node(BaseModel):
    """
    The atomic unit of the Epistemological Graph.
    """
    id: str = Field(..., description="Unique Content ID (Hash)")
    type: NodeType
    # Content holds the payload. For 'claim' it might be text; for 'star_map' it's a Dict.
    content: Union[str, Dict[str, Any]] = Field(..., description="The payload")
    
    agent_id: str = Field(..., description="The Agent who minted this")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    signature: str = Field(..., description="Cryptographic signature")
    
    # Epistemic State
    net_stake: float = 0.0

    # Optional target for refutation-type nodes.
    # For now, used only when type == "refutation".
    target_id: Optional[str] = None

    def compute_id(self) -> str:
        """Calculates SHA-256 ID. Dicts are canonicalized."""
        if isinstance(self.content, dict):
            payload_str = json.dumps(self.content, sort_keys=True)
        else:
            payload_str = str(self.content)
            
        # ID depends on Type, Content, and Author (Provenance)
        payload = f"{self.type}:{payload_str}:{self.agent_id}".encode()
        return hashlib.sha256(payload).hexdigest()

class Edge(BaseModel):
    """
    The 'citation' or 'semantic link' between two nodes.
    """
    source_id: str
    target_id: str
    type: EdgeType
    weight: float = 1.0

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
    net_stake: float = 0.0
    timestamp: Optional[str] = None
    parent_ids: List[str] = Field(default_factory=list)
    target_id: Optional[str] = None

def node_to_claim_record(node: Node) -> ClaimRecord:
    """
    Convert a graph Node into a ClaimRecord. Assumes node.type is claim-like.
    """
    # If node.content is a dict, we might find extra fields there, 
    # but for MVP claims are usually strings.
    # We'll check node.data if it existed, but Node model doesn't have 'data' field in types.py yet.
    # Wait, looking at Node definition:
    # content: Union[str, Dict[str, Any]]
    # It doesn't have a generic 'data' bag. 
    # However, in previous steps we saw usage like node.data in the plan.
    # But types.py shows Node only has: id, type, content, agent_id, timestamp, signature, net_stake, target_id.
    
    # So we map directly from Node fields.
    
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
        net_stake=node.net_stake,
        timestamp=ts_str,
        parent_ids=[], # Node doesn't explicitly store parents list yet, unless we query edges.
                       # For MVP, we'll leave empty or rely on graph lookups later.
                       # But wait, the plan said "data = node.data or {}".
                       # The Node model in types.py DOES NOT have a .data field.
                       # I should check if I need to add it or if I should just map what I have.
                       # The plan assumed node.data.
                       # I will map what is available in Node.
        target_id=node.target_id,
    )

def claim_record_to_node(claim: ClaimRecord) -> Node:
    """
    Convert a ClaimRecord into a generic Node suitable for EpistemicGraph.
    """
    # We need to handle timestamp conversion str -> datetime
    ts = datetime.utcnow()
    if claim.timestamp:
        try:
            ts = datetime.fromisoformat(claim.timestamp)
        except ValueError:
            pass

    return Node(
        id=claim.id,
        type=claim.type, # type: ignore (ClaimRecord type is str, Node type is Literal)
        content=claim.content,
        agent_id=claim.agent_id,
        timestamp=ts,
        signature="sig-placeholder", # ClaimRecord doesn't have sig yet?
                                     # Or maybe we should add sig to ClaimRecord?
                                     # The plan didn't have signature in ClaimRecord.
                                     # I'll use a placeholder or derived value.
        net_stake=claim.net_stake,
        target_id=claim.target_id,
    )
