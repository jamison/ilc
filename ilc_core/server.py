from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine
from .agent import EveAgent
from .types import Node
from .network.peer import PeerManager
from .config import load_governance_config
from fastapi.responses import JSONResponse
from typing import List, Optional
from ilc_core.economics.outcome import TaskOutcome
from ilc_core.protocol.schema import load_protocol_schema
from ilc_core.protocol.mapper import (
    node_to_protocol_claim,
    node_to_protocol_refute,
    outcome_to_protocol_task_outcome,
)
from ilc_core.genesis.work_task import EpistemicWorkTask, ep_task_to_json
from ilc_core.genesis.schema import load_epistemic_work_task_schema
from ilc_core.work.task_queue import TaskDescriptor

# Singleton State (Simulated Persistence for MVP)
graph = EpistemicGraph()
graph.load_genesis()
cfg = load_governance_config()
consensus = ConsensusEngine(graph, governance_config=cfg)
agent = EveAgent("agent:local_node", graph, consensus)
agent.wallet_balance = 1000.0
peer_manager = PeerManager(local_port=8000)

app = FastAPI(title="ILC Node Daemon", version="0.1.0")

# Request Models
class ClaimRequest(BaseModel):
    content: str
    parent_id: str
    stake: float

class ProtocolClaimRequest(BaseModel):
    agent_id: str
    content: str
    parent_ids: Optional[List[str]] = None
    net_stake: Optional[float] = None

class ProtocolRefuteRequest(BaseModel):
    agent_id: str
    content: str
    target_claim_id: str
    net_stake: Optional[float] = None

class ProtocolTaskOutcomeRequest(BaseModel):
    task_type: str
    domain: str
    agent_id: str
    epoch: Optional[int] = None
    stake_spent: float
    reward_paid: float
    success: bool

@app.get("/")
def read_root():
    return {
        "system": "Intelligent Labor Coin",
        "status": "online",
        "agent_id": agent.id,
        "graph_size": len(graph.nodes),
        "genesis_hash": graph.nodes["axiom:math:01"].id if "axiom:math:01" in graph.nodes else "unknown"
    }

@app.post("/mine")
def mine_claim(req: ClaimRequest):
    """
    Public Endpoint: Ask the internal agent to perform labor.
    """
    node = agent.mine_thought(req.content, req.parent_id, req.stake)
    if not node:
        raise HTTPException(status_code=400, detail="Mining failed (insufficient funds?)")
    
    # NEW: Gossip the success!
    peer_manager.broadcast("/gossip/receive", node.model_dump())
    
    return {
        "status": "success",
        "node_id": node.id,
        "content": node.content,
        "net_stake": consensus.node_stakes.get(node.id, 0.0)
    }

@app.get("/node/{node_id}")
def get_node(node_id: str):
    if node_id not in graph.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    return graph.nodes[node_id]

@app.post("/gossip/receive")
def receive_gossip(node_data: dict):
    """
    Endpoint for other nodes to push data to us.
    """
    # 1. Parse Node
    try:
        # Simple validation logic (would be deeper in production)
        node_id = node_data.get("id")
        print(f"[Gossip] Received Node {node_id} from peer.")
        
        # 2. Add to Graph (if new)
        # In a real system, we'd verify signature here first!
        if node_id not in graph.nodes:
            # Reconstruct node object (simplified for MVP)
            # graph.add_node(Node(**node_data))
            print(f"[Gossip] Accepted new knowledge: {node_id}")
            return {"status": "accepted"}
        else:
            return {"status": "ignored", "reason": "already_have"}
            
    except Exception as e:
        print(f"[Gossip] Error processing: {e}")
        raise HTTPException(status_code=400, detail="Invalid Gossip")

@app.post("/peers/add")
def add_peer_endpoint(host: str, port: int):
    peer_manager.add_peer(host, port)
    return {"status": "added", "total_peers": len(peer_manager.peers)}

# --- Protocol Surface (MVP) ---
# NOTE: These /v1/protocol/* endpoints expose the MVP protocol schema over HTTP.
# They do not persist to a real chain or run consensus; they just:
#   - accept simple request models
#   - construct internal Node/TaskOutcome objects
#   - map them to protocol-shaped dicts via ilc_core.protocol.mapper
# This keeps the API in lockstep with protocol/ilc_protocol_mvp.json without
# hard-coding JSON structures here.

@app.get("/v1/protocol/schema")
def get_protocol_schema():
    schema = load_protocol_schema()
    return JSONResponse(schema)

@app.post("/v1/protocol/claim")
def submit_protocol_claim(req: ProtocolClaimRequest):
    # Build a Node; keep it simple and deterministic
    node = Node(
        id="", # Will be computed
        type="claim",
        content=req.content,
        agent_id=req.agent_id,
        signature="api_signed",
        net_stake=req.net_stake or 0.0,
    )
    node.id = node.compute_id()

    # Inject parent_ids if provided (mapper looks for attribute)
    if req.parent_ids:
        node.parent_ids = req.parent_ids

    proto = node_to_protocol_claim(node)
    return {"claim": proto}

@app.post("/v1/protocol/refute")
def submit_protocol_refute(req: ProtocolRefuteRequest):
    node = Node(
        id="",
        type="refutation",
        content=req.content,
        agent_id=req.agent_id,
        signature="api_signed",
        net_stake=req.net_stake or 0.0,
        target_id=req.target_claim_id
    )
    node.id = node.compute_id()
    
    proto = node_to_protocol_refute(node)
    return {"refute": proto}

@app.post("/v1/protocol/task_outcome")
def submit_protocol_task_outcome(req: ProtocolTaskOutcomeRequest):
    outcome = TaskOutcome(
        task_type=req.task_type,
        domain=req.domain,
        stake_spent=req.stake_spent,
        reward_paid=req.reward_paid,
        success=req.success,
    )
    proto = outcome_to_protocol_task_outcome(
        outcome,
        epoch=req.epoch,
        agent_id=req.agent_id,
    )
    return {"task_outcome": proto}

@app.get("/v1/protocol/ep_task_schema")
def get_ep_task_schema():
    """
    Return the canonical JSON schema for EpistemicWorkTask.

    This is the same schema used by the EpistemicWorkTask Pydantic model
    and is suitable for external validation / code generation.
    """
    schema = load_epistemic_work_task_schema()
    return JSONResponse(schema)

@app.post("/v1/protocol/ep_task")
def submit_ep_task(ep_task: EpistemicWorkTask):
    """
    Intake endpoint for a single EpistemicWorkTask.

    MVP behavior:
    - Validate the incoming JSON against EpistemicWorkTask.
    - Wrap it into a TaskDescriptor via TaskDescriptor.from_epistemic_work_task(...).
    - Return both the canonical ep_task JSON and the TaskDescriptor
      to show how the scheduler would view it.

    This endpoint does *not* enqueue the task into any global worker
    or trigger a reward loop. It is a shaping + validation surface only.
    """
    # Canonical JSON view of the EpistemicWorkTask
    ep_json = ep_task_to_json(ep_task)

    # Bridge into TaskDescriptor
    td = TaskDescriptor.from_epistemic_work_task(ep_task)

    # If TaskDescriptor is a dataclass, convert to dict appropriately
    try:
        from dataclasses import asdict
        td_dict = asdict(td)
    except TypeError:
        # If it's a pydantic model or has .dict(), use that
        if hasattr(td, "dict"):
            td_dict = td.dict()
        else:
            td_dict = td.__dict__

    return {
        "ep_task": ep_json,
        "task_descriptor": td_dict,
    }
