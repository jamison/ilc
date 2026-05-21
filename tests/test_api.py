import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from ilc_core.asgi import app
from ilc_core.types import Node

client = TestClient(app)


def _build_gossip_node_payload(content: str, node_id: str) -> dict:
    node = Node(
        id=node_id,
        type="claim",
        content=content,
        agent_id="agent:gossip:test",
        signature="sig:gossip:test",
        net_stake="1.0",
    )
    node.id = node.compute_id()
    return node.model_dump(mode="json")

def test_api_lifecycle():
    """Smoke-test the legacy HTTP API: pulse, mine, and read-back a node."""
    # 1. Check Pulse
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["system"] == "Intelligent Labor Coin"
    print("API Pulse: OK")
    
    # 2. Mine a Claim via HTTP
    payload = {
        "content": "Hello World via API",
        "parent_id": "axiom:math:01",
        "stake": "1.0"
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


def test_gossip_receive_accepts_valid_new_node():
    payload = _build_gossip_node_payload("gossip_accept_payload", "placeholder")
    response = client.post("/gossip/receive", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}
    assert payload["id"] in app.state.graph.nodes


def test_gossip_receive_rejects_id_mismatch():
    payload = _build_gossip_node_payload("gossip_bad_id_payload", "placeholder")
    payload["id"] = "not_the_expected_hash"
    response = client.post("/gossip/receive", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"


def test_gossip_receive_ignores_existing_node():
    payload = _build_gossip_node_payload("gossip_duplicate_payload", "placeholder")
    first = client.post("/gossip/receive", json=payload)
    second = client.post("/gossip/receive", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == {"status": "ignored", "reason": "already_have"}

def test_get_protocol_schema():
    """Ensure /v1/protocol/schema returns the MVP protocol schema with core objects."""
    response = client.get("/v1/protocol/schema")
    assert response.status_code == 200
    data = response.json()
    # Check for core objects in schema
    assert "objects" in data
    assert "claim" in data["objects"]

def test_submit_protocol_claim():
    """POST /v1/protocol/claim returns a protocol-shaped claim echoing core fields."""
    payload = {
        "agent_id": "agent:test",
        "content": "1 + 1 = 2",
        "net_stake": "1.0"
    }
    response = client.post("/v1/protocol/claim", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "claim" in data
    claim = data["claim"]
    assert claim["type"] == "claim"
    assert claim["agent_id"] == "agent:test"
    assert claim["content"] == "1 + 1 = 2"
    assert claim["net_stake"] == "1"
    assert claim["id"] is not None

def test_submit_protocol_refute():
    """POST /v1/protocol/refute returns a refute object correctly linked to target_claim_id."""
    payload = {
        "agent_id": "agent:refuter",
        "content": "Counter-evidence",
        "target_claim_id": "claim:demo:1",
        "net_stake": "0.5"
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
    """POST /v1/protocol/task_outcome accepts a task outcome and returns a protocol-shaped echo."""
    payload = {
        "task_type": "claim.submit",
        "domain": "MEDIUM",
        "agent_id": "agent:test",
        "epoch": 3,
        "stake_spent": "0.1",
        "reward_paid": "0.2",
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


def test_protocol_decimal_boundaries_reject_non_finite_values():
    claim_response = client.post(
        "/v1/protocol/claim",
        json={
            "agent_id": "agent:test",
            "content": "non-finite stake",
            "net_stake": "NaN",
        },
    )
    assert claim_response.status_code == 400
    assert claim_response.json()["detail"] == "protocol_claim_net_stake_invalid_non_finite"

    outcome_response = client.post(
        "/v1/protocol/task_outcome",
        json={
            "task_type": "claim.submit",
            "domain": "MEDIUM",
            "agent_id": "agent:test",
            "stake_spent": "0.1",
            "reward_paid": "Infinity",
            "success": True,
        },
    )
    assert outcome_response.status_code == 400
    assert outcome_response.json()["detail"] == "protocol_task_outcome_reward_paid_invalid_non_finite"

def test_get_ep_task_schema():
    """
    The ep_task schema endpoint should return a JSON object describing
    the EpistemicWorkTask structure.
    """
    response = client.get("/v1/protocol/ep_task_schema")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Very light sanity checks; the exact schema is locked in the JSON file.
    assert data.get("title") is not None or "Epistemic" in json.dumps(data)
    assert "properties" in data

def test_submit_epistemic_work_task_mvp():
    """
    Submitting an EpistemicWorkTask over HTTP should:
    - Validate the payload
    - Echo back a canonical ep_task JSON
    - Return a mapped TaskDescriptor dict
    """
    payload = {
        "task_id": "task:demo:1",
        "task_class": "star.map.embedding",
        "agent_id": "agent:test",
        "region_scope": ["global"],
        "difficulty_factor": 1.0,
        "input_data": {"dummy": True},
        "verification_method": "hash-match",
        "task_state": "proposed",
        "timestamp_created": 1700000000,
        # If your EpistemicWorkTask uses an alias like "ecu.estimate",
        # include it here as in the schema:
        "ecu.estimate": 0.5,
    }

    response = client.post("/v1/protocol/ep_task", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "ep_task" in data
    assert "task_descriptor" in data

    ep = data["ep_task"]
    td = data["task_descriptor"]

    # Basic checks on the EpTask echo
    assert ep["task_id"] == "task:demo:1"
    assert ep["agent_id"] == "agent:test"
    assert ep["task_class"] == "star.map.embedding"

    # Basic checks on the TaskDescriptor mapping
    assert td["task_id"] == "task:demo:1"
    assert td["agent_id"] == "agent:test"
    # Depending on how from_epistemic_work_task is implemented:
    # task_type might be something like "epistemic.work"
    assert "task_type" in td
    assert "payload" in td

if __name__ == "__main__":
    test_api_lifecycle()
    test_get_protocol_schema()
    test_submit_protocol_claim()
    test_submit_protocol_refute()
    test_submit_protocol_task_outcome()
    test_get_ep_task_schema()
    test_submit_epistemic_work_task_mvp()
