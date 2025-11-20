from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine
from .agent import EveAgent
from .types import Node
from .network.peer import PeerManager

# Singleton State (Simulated Persistence for MVP)
graph = EpistemicGraph()
graph.load_genesis()
consensus = ConsensusEngine(graph)
agent = EveAgent("agent:local_node", graph, consensus)
peer_manager = PeerManager(local_port=8000)

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
