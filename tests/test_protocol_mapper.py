import pytest
from ilc_core.types import Node
from ilc_core.economics.outcome import TaskOutcome
from ilc_core.protocol.mapper import (
    node_to_protocol_claim,
    node_to_protocol_refute,
    outcome_to_protocol_task_outcome,
    epoch_summary_to_protocol,
)

def test_node_to_protocol_claim_basic():
    node = Node(
        id="abc",
        type="claim",
        content="1 + 1 = 2",
        agent_id="agent:test",
        signature="sig",
        net_stake=10.0
    )
    proto = node_to_protocol_claim(node)
    assert proto["id"] == "abc"
    assert proto["type"] == "claim"
    assert proto["agent_id"] == "agent:test"
    assert proto["content"] == "1 + 1 = 2"
    assert proto["net_stake"] == 10.0
    assert "timestamp" in proto
    assert isinstance(proto["parent_ids"], list)

def test_node_to_protocol_refute_basic():
    # Note: Node type must be 'refutation' to pass validation in mapper
    # even if we map it to protocol type 'refute'
    node = Node(
        id="def",
        type="refutation",
        content="Counter-evidence",
        agent_id="agent:refuter",
        signature="sig2",
        net_stake=5.0
    )
    # Node is a Pydantic model and now has target_id field.
    node.target_id = "abc"
    
    proto = node_to_protocol_refute(node)
    assert proto["id"] == "def"
    assert proto["type"] == "refute" # Canonical protocol type
    assert proto["agent_id"] == "agent:refuter"
    assert proto["target_claim_id"] == "abc"
    assert proto["content"] == "Counter-evidence"

def test_node_to_protocol_refute_missing_target_defaults_none():
    node = Node(
        id="refute:no-target",
        type="refutation",
        content="Refute with no explicit target",
        agent_id="agent:refuter",
        signature="sig3",
        net_stake=1.0,
    )
    # target_id defaults to None
    proto = node_to_protocol_refute(node)
    assert proto["target_claim_id"] is None

def test_outcome_to_protocol_task_outcome_basic():
    outcome = TaskOutcome(
        task_type="claim.submit",
        domain="MEDIUM",
        stake_spent=0.1,
        reward_paid=0.2,
        success=True,
    )
    proto = outcome_to_protocol_task_outcome(outcome, epoch=3, agent_id="agent:test")
    assert proto["task_type"] == "claim.submit"
    assert proto["domain"] == "MEDIUM"
    assert proto["stake_spent"] == 0.1
    assert proto["reward_paid"] == 0.2
    assert proto["success"] is True
    assert proto["epoch"] == 3
    assert proto["agent_id"] == "agent:test"

def test_epoch_summary_to_protocol_basic():
    summary = {
        "total_tasks": 10,
        "total_ecu_spent": 1.5,
        "total_reward_paid": 2.0,
        "clearing_price_ilc_per_ecu": 1.3333,
    }
    proto = epoch_summary_to_protocol(epoch=7, summary=summary)
    assert proto["epoch"] == 7
    assert proto["total_tasks"] == 10
    assert proto["total_ecu_spent"] == 1.5
    assert proto["total_reward_paid"] == 2.0
    assert proto["clearing_price_ilc_per_ecu"] == 1.3333
