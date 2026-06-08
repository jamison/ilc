import sys
import os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.asgi import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_gossip_protocol():
    print("\n--- TEST: P2P GOSSIP ---")
    # Ensure server runtime state is initialized
    client.get("/")
    
    # 1. Populate Peer Table
    peers = [
        "phase-network-1.ilc.example",
        "phase-network-2.ilc.example",
        "phase-network-3.ilc.example",
        "phase-network-4.ilc.example",
        "phase-network-5.ilc.example",
    ]
    peer_manager = app.state.peer_manager
    peer_manager.peers.clear()
    for p in peers:
        client.post(f"/peers/add?host={p}&port=8000")
        
    assert len(peer_manager.peers) == 5
    print(f"Peer Table: {len(peer_manager.peers)} nodes.")
    
    # 2. Mine & Broadcast
    # We spy on the broadcast method to ensure it fires
    peer_manager.broadcast = MagicMock()
    
    payload = {
        "content": "Global Broadcast Test",
        "parent_id": "axiom:math:01",
        "stake": "1.0"
    }
    client.post("/mine", json=payload)
    
    # 3. Verify
    assert peer_manager.broadcast.called
    print("SUCCESS: Mining triggered network broadcast.")

if __name__ == "__main__":
    test_gossip_protocol()
