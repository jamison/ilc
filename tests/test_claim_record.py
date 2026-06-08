import pytest
from decimal import Decimal
from ilc_core.types import ClaimRecord, node_to_claim_record, claim_record_to_node
from ilc_core.graph import EpistemicGraph

def test_claim_record_round_trip():
    claim = ClaimRecord(
        signature="sig",
        id="c1",
        type="claim",
        agent_id="agent:a",
        content="foo",
        net_stake=Decimal("3.0"),
        timestamp="2025-01-01T00:00:00",
        parent_ids=["p1", "p2"],
        target_id=None,
    )
    node = claim_record_to_node(claim)
    recovered = node_to_claim_record(node)
    
    # Verify round-trip fields.
    assert recovered.id == claim.id
    assert recovered.type == claim.type
    assert recovered.agent_id == claim.agent_id
    assert recovered.content == claim.content
    assert recovered.signature == claim.signature
    assert recovered.net_stake == claim.net_stake
    # Timestamp might have minor formatting diffs, but let's check basic equality
    assert recovered.timestamp == claim.timestamp
    assert recovered.parent_ids == claim.parent_ids
    assert recovered.target_id == claim.target_id

def test_epistemic_graph_add_and_get_claim():
    graph = EpistemicGraph()
    claim = ClaimRecord(
        signature="sig",
        id="c1",
        type="claim",
        agent_id="agent:a",
        content="foo",
        net_stake=Decimal("3.0"),
        timestamp="2025-01-01T00:00:00",
        parent_ids=[],
        target_id=None,
    )
    graph.add_claim(claim)
    fetched = graph.get_claim("c1")
    assert fetched is not None
    assert fetched.id == "c1"
    assert fetched.agent_id == "agent:a"
    assert fetched.content == "foo"

def test_get_claim_returns_none_for_missing():
    graph = EpistemicGraph()
    assert graph.get_claim("missing") is None

def test_get_claim_returns_none_for_non_claim_node():
    # If we add a node that isn't a claim (e.g. genesis or task if supported)
    # get_claim should return None.
    # Let's manually add a node with type 'task' (if allowed by Literal)
    from ilc_core.types import Node
    node = Node(
        id="t1",
        type="task",
        content="some task",
        agent_id="agent:x",
        signature="sig",
    )
    graph = EpistemicGraph()
    graph.add_node(node)
    assert graph.get_claim("t1") is None
