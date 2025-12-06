import pytest
from ilc_core.network.topology import build_line_topology, DevnetTopology
from ilc_core.network.gossip import (
    Message,
    MessageType,
    initialize_inboxes,
    gossip_broadcast,
    gossip_step
)

@pytest.fixture
def topology():
    # n1 <-> n2 <-> n3
    return build_line_topology(["n1", "n2", "n3"])

@pytest.fixture
def inboxes(topology):
    return initialize_inboxes(topology)

def test_initialization(inboxes):
    assert len(inboxes) == 3
    assert inboxes["n1"] == []
    assert inboxes["n2"] == []
    assert inboxes["n3"] == []

def test_broadcast(topology, inboxes):
    msg = Message("m1", MessageType.GENERIC, "n1", {}, ttl=3)
    gossip_broadcast(topology, inboxes, "n1", msg)
    
    assert len(inboxes["n1"]) == 1
    assert inboxes["n1"][0].msg_id == "m1"
    assert len(inboxes["n2"]) == 0

def test_propagation(topology, inboxes):
    # Seed at n1
    msg = Message("m1", MessageType.GENERIC, "n1", {}, ttl=3)
    gossip_broadcast(topology, inboxes, "n1", msg)
    
    # Step 1: n1 -> n2
    gossip_step(topology, inboxes)
    assert len(inboxes["n2"]) == 1
    assert inboxes["n2"][0].msg_id == "m1"
    assert inboxes["n2"][0].ttl == 2
    
    # Step 2: n2 -> n3 (and n2 -> n1 echo, n1 -> n2 echo allowed for MVP)
    gossip_step(topology, inboxes)
    
    # n3 should have it
    assert len(inboxes["n3"]) >= 1
    found_n3 = [m for m in inboxes["n3"] if m.msg_id == "m1"]
    assert found_n3
    assert found_n3[0].ttl == 1

def test_ttl_stopping(topology, inboxes):
    # Seed at n1 with TTL=1. Should reach n2 (ttl=0), but not n3
    msg = Message("m2", MessageType.GENERIC, "n1", {}, ttl=1)
    gossip_broadcast(topology, inboxes, "n1", msg)
    
    # Step 1: n1 -> n2 (ttl becomes 0)
    gossip_step(topology, inboxes)
    assert len(inboxes["n2"]) == 1
    assert inboxes["n2"][0].ttl == 0
    
    # Step 2: n2 tries to send, but ttl=0, so no propagation
    gossip_step(topology, inboxes)
    assert len(inboxes["n3"]) == 0

def test_isolation():
    # n1, n2 connected. n3 isolated
    nodes = {"n1", "n2", "n3"}
    # Manually build disconnected top
    from ilc_core.network.topology import NodeConfig, NodeRole
    topo = DevnetTopology(
        nodes={n: NodeConfig(n, NodeRole.WORKER) for n in nodes},
        adjacency={"n1": ["n2"], "n2": ["n1"], "n3": []}
    )
    inboxes = initialize_inboxes(topo)
    
    msg = Message("m3", MessageType.GENERIC, "n1", {}, ttl=5)
    gossip_broadcast(topo, inboxes, "n1", msg)
    
    # Run many steps
    for _ in range(5):
        gossip_step(topo, inboxes)
        
    assert len(inboxes["n2"]) > 0
    assert len(inboxes["n3"]) == 0

def test_gossip_ttl_eventually_inert(topology):
    # Tests that messages stop spawning copies once their TTL is consumed locally
    inboxes = initialize_inboxes(topology)

    msg = Message(
        msg_id="m1",
        msg_type=MessageType.GENERIC,
        origin_node="n1",
        payload={},
        ttl=2,
    )

    gossip_broadcast(topology, inboxes, "n1", msg)

    # Run more steps than the TTL
    for _ in range(5):
        gossip_step(topology, inboxes)

    # After enough steps, no message should have ttl > 0 in ANY inbox
    for node_msgs in inboxes.values():
        for m in node_msgs:
            assert m.ttl == 0, f"Found active message {m} which should be inert"
