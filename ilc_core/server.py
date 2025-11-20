from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine
from .agent import EveAgent
from .types import Node

# Singleton State (Simulated Persistence for MVP)
graph = EpistemicGraph()
graph.load_genesis()
consensus = ConsensusEngine(graph)
agent = EveAgent("agent:local_node", graph, consensus)

app = FastAPI(title="ILC Node Daemon", version="0.1.0")

# Request Models
class ClaimRequest(BaseModel):
    content: str
    parent_id: str
    stake: float

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
