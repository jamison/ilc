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

if __name__ == "__main__":
    test_api_lifecycle()
