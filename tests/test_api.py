import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from ilc_core.server import app

client = TestClient(app)

def test_api_lifecycle():
    # 1. Check Pulse
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["system"] == "Intelligent Labor Coin"
    print("API Pulse: OK")
    
    # 2. Mine a Claim via HTTP
    payload = {
        "content": "Hello World via API",
        "parent_id": "axiom:math:01",
        "stake": 1.0
    }
    res = client.post("/mine", json=payload)
    assert res.status_code == 200
    data = res.json()
    print(f"Mined Node: {data['node_id']}")
    
    # 3. Read it back
    res_read = client.get(f"/node/{data['node_id']}")
    assert res_read.status_code == 200
    assert res_read.json()["content"] == "Hello World via API"
    print("Read Back: OK")

def test_get_protocol_schema():
    response = client.get("/v1/protocol/schema")
    assert response.status_code == 200
    data = response.json()
    # Check for core objects in schema
    assert "objects" in data
    assert "claim" in data["objects"]

def test_submit_protocol_claim():
    payload = {
        "agent_id": "agent:test",
        "content": "1 + 1 = 2",
        "net_stake": 1.0
    }
    response = client.post("/v1/protocol/claim", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "claim" in data
    claim = data["claim"]
    assert claim["type"] == "claim"
    assert claim["agent_id"] == "agent:test"
    assert claim["content"] == "1 + 1 = 2"
    assert claim["net_stake"] == 1.0
    assert claim["id"] is not None

def test_submit_protocol_refute():
    payload = {
        "agent_id": "agent:refuter",
        "content": "Counter-evidence",
        "target_claim_id": "claim:demo:1",
        "net_stake": 0.5
    }
    response = client.post("/v1/protocol/refute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "refute" in data
    refute = data["refute"]
    assert refute["type"] == "refute"
    assert refute["agent_id"] == "agent:refuter"
    assert refute["target_claim_id"] == "claim:demo:1"

def test_submit_protocol_task_outcome():
    payload = {
        "task_type": "claim.submit",
        "domain": "MEDIUM",
        "agent_id": "agent:test",
        "epoch": 3,
        "stake_spent": 0.1,
        "reward_paid": 0.2,
        "success": True,
    }
    response = client.post("/v1/protocol/task_outcome", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_outcome" in data
    outcome = data["task_outcome"]
    assert outcome["task_type"] == "claim.submit"
    assert outcome["domain"] == "MEDIUM"
    assert outcome["epoch"] == 3

if __name__ == "__main__":
    test_api_lifecycle()
    test_get_protocol_schema()
    test_submit_protocol_claim()
    test_submit_protocol_refute()
    test_submit_protocol_task_outcome()
