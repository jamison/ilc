from dataclasses import dataclass, field as dc_field
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Set, Union
from datetime import datetime, timezone
import hashlib
import json

from pydantic import BaseModel, Field, field_serializer, field_validator

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, to_decimal

# ---------------------------------------------------------------------------
# Hyperedge edge type system — pre-M-018 substrate additions
#
# EdgeType: typed classification for all HyperEdge relationships.
# Values are CDL-ratified edge type coefficients (α per type) pending SIM-REUSE-01.
# New types require a CDL amendment; unknown types from wire are rejected.
#
# WeightParams: replaces raw weight float — stores committed parameters so that
# w(e, t) can be deterministically recomputed from first principles at any epoch.
# Storing parameters (not the derived float) means historical Laplacians are
# auditable. Raw float weights cannot be validated post-hoc.
#
# PROVISIONAL: edge_type_coefficient values and reuse_count functional form
# are unratified placeholders. SIM-REUSE-01 validates; CDL locks them.
# ---------------------------------------------------------------------------

class EdgeType(str, Enum):
    """Typed classification for hyperedge relationships.

    Each type carries a provisional CDL weight coefficient (α).
    Constitutional values locked after SIM-REUSE-01 + CDL ratification.
    """
    ATTESTATION    = "attestation"      # Explicit vouching: agent A vouches for node B
    REUSE          = "reuse"            # Content consumption: agent traverses B's content
    REFUTATION     = "refutation"       # Counter-claim: agent disputes node B
    CO_AUTHORSHIP  = "co_authorship"    # Joint production: n-ary group output
    PROVENANCE     = "provenance"       # Derivation chain: B derives from A
    EPOCH_BOUNDARY = "epoch_boundary"   # Structural: cross-epoch continuity marker


@dataclass(frozen=True)
class WeightParams:
    """Committed parameters for deterministic edge weight computation.

    w(e, t) = α(edge_type) × f(reuse_count) × decay(stake, epoch_created, t)

    Where:
      α(edge_type)      = edge_type_coefficient  (CDL-ratified per type; provisional)
      f(reuse_count)    = log(reuse_count + 1)   (functional form: SIM-REUSE-01 pending)
      decay(stake, t)   = CDL-V1 temporal decay applied by caller

    Parameters are the committed record; the derived float is never stored.
    All fields included in JSON hash serialization (sort_keys=True).
    """
    stake: Decimal               # ECU stake at edge creation — basis for decay
    reuse_count: int             # Traversal counter; incremented on each access
    decay_rate: float            # CDL-V1 decay rate (0.0 = no decay; 1.0 = full decay per epoch)
    edge_type_coefficient: float # α — per-type weight multiplier; provisional until CDL


# ---------------------------------------------------------------------------
# Provisional attribution constants — named so that SIM-REUSE-01 and H-CON-01
# implementation have a single authoritative location to update. Do not
# hard-code these values elsewhere in the codebase.
#
# REUSE_ATTRIBUTION_RATE: per-traversal ECU rate — locked at Decimal("0.20")
#   by CDL-081 ratification (Phase 943). SIM-REUSE-01 evidence (Phase 941).
# EDGE_MINT_PHI_BOUND: Werner φ-bound — edge minting ≤ φ × node minting per
#   epoch. None until the Werner edge-minting CDL is opened and ratified.
# PROVENANCE_MAX_DEPTH: max hops for provenance chain attribution traversal.
#   N=3 is the provisional cap; CDL may adjust after SIM-REUSE-01.
# PROVENANCE_DECAY_ALPHA: geometric decay per provenance hop (α < 1 ensures
#   convergence). 0.5 is provisional; predictive-coding stability criterion
#   requires α < 1. CDL locks the final value.
# STAR_NODE_MIN_STAKE_ECU: minimum member stake floor for CO_AUTHORSHIP star
#   nodes (H-CON-01 Q2 = Option A, 1 ECU). CDL-ratified when H-CON-01 opens.
# ---------------------------------------------------------------------------
REUSE_ATTRIBUTION_RATE: Decimal = Decimal("0.20")       # CDL-081 ratified Phase 943
EDGE_MINT_PHI_BOUND: Optional[float] = None             # pending Werner edge-minting CDL
PROVENANCE_MAX_DEPTH: int = 3                            # provisional; CDL required to change
PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")         # Q9: CDL-084 locks mechanism; SIM-PROVENANCE-01 refines value
CDL_084_TYPES_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
STAR_NODE_MIN_STAKE_ECU: Decimal = Decimal("1")          # H-CON-01 Q2 Option A; CDL-ratified on open


# ---------------------------------------------------------------------------
# EpochAttributionBatch — design stub for temporal batching of REUSE and
# CO_AUTHORSHIP attribution events.
#
# CDL-078 precedent: serve-event buffer collected during epoch, processed at
# epoch close. Same pattern applied here to attribution events.
#
# Invariants (enforced by implementation):
#   - Each event in the batch is processed with a fresh visited_set.
#     No cross-event state contamination: provenance traversal must not bleed
#     between events in the same epoch.
#   - Batch is sealed at epoch close; no events may be added after settle()
#     is called. Late-arriving clearance records become epoch+1 obligations.
#   - settle() is a pure payout quote: calling it twice returns the same payout
#     list, but callers must apply returned transfers at most once.
#
# CDL-081 ratified (Phase 943). H-012 attribution runtime implemented in
# ilc_core/economics/epoch_attribution_settle_runtime.py (Phase 946).
# H-CON-02 forward obligation: ejected stake treasury sub-path remains stubbed.
# ---------------------------------------------------------------------------
EPOCH_ATTRIBUTION_BATCH_VERSION = "epoch_attribution_batch.v0.2"


@dataclass
class EpochAttributionBatch:
    """Temporal batch for REUSE and CO_AUTHORSHIP attribution events.

    Collect traversal clearance records during an epoch; process at epoch
    close with a fresh visited_set per event. CDL-078 precedent pattern.

    Not yet wired: settle() raises NotImplementedError until H-CON-01 CDL
    is ratified and the H-012 attribution runtime is implemented.
    """
    epoch: int
    events: List[Any] = dc_field(default_factory=list)
    sealed: bool = dc_field(default=False, init=False)

    def add_event(self, event: Any) -> None:
        """Record a traversal clearance event for this epoch."""
        if self.sealed:
            raise ValueError("epoch_attribution_batch_sealed_no_new_events")
        self.events.append(event)

    def seal(self) -> None:
        """Seal the batch at epoch close. No further events may be added."""
        self.sealed = True

    def settle(
        self,
        stake_map: dict[str, dict[str, "Decimal"]],
        emitted_tokens: Optional[list[str]] = None,
    ) -> list[tuple[str, "Decimal"]]:
        """Process all events and return ECU attribution payout quotes.

        CDL-081 §§4.1–4.6. Delegates to epoch_attribution_settle_runtime.
        Partial: ejected stake treasury path raises NotImplementedError(CDL_HCON_02_DEPENDENCY).

        Args:
            stake_map: {star_node_id: {member_agent_id: stake_amount}}
                For REUSE events, stake_map is not accessed.
            emitted_tokens: Optional mutable list for protocol event tokens.
        Returns:
            List of (agent_id, ecu_amount) Decimal payouts. This method does not
            mutate balances; callers are responsible for applying the returned
            payouts at most once.
        """
        from ilc_core.economics.epoch_attribution_settle_runtime import settle_attribution_batch
        return settle_attribution_batch(self, stake_map, emitted_tokens)


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
    hyperedge_type: str                           # "panel" | "co_authorship" | "refutation_coalition" | "epoch_boundary" | "content_package"
    member_ids: List[str]                         # all members (undirected) or union of head+tail (directed)
    head_ids: List[str]                           # directed source set; empty list if undirected
    tail_ids: List[str]                           # directed target set; empty list if undirected
    weight_params: WeightParams                   # committed weight parameters — derive w(e,t) via compute_weight()
    epoch: int                                    # temporal stamp
    agent_id: str                                 # declaring agent
    signature: str                                # attribution
    # --- Optional fields: always included in hash (as null if absent) ---
    edge_type: Optional[EdgeType] = dc_field(default=None)          # structured type; None = legacy/unknown
    edge_payload: Optional[bytes] = dc_field(default=None)          # reserved future logic slot; null interpretation is default/no-op
    spectral_fingerprint: Optional[List[float]] = dc_field(default=None)  # analytics-populated; gate: SIM-BEACON-01
