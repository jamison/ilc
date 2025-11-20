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

EdgeType = Literal["supports", "refutes", "derives_from", "equivalent", "implements", "relates_to"]

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
