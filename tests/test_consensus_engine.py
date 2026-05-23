import sys
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.types import Node


def _make_node(
    node_id: str,
    age_seconds: int,
    net_stake: Decimal = Decimal("1.0"),
) -> Node:
    timestamp = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    node = Node(
        id="",
        type="claim",
        content="test",
        agent_id="agent:test",
        signature="sig",
        timestamp=timestamp,
        net_stake=net_stake,
    )
    node.id = node_id
    return node


def test_end_epoch_update_advances_epoch():
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)

    assert engine.epoch_index == 0
    assert engine.last_epoch_finalized == 0

    engine.end_epoch_update(backlog_len=5, finalized_last_epoch=3, agent_potentials=[1.0, 2.0])

    assert engine.epoch_index == 1
    assert engine.last_epoch_finalized == 3


def test_calculate_maintenance_tax_decreases_with_age():
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)

    old_node = _make_node("node_old", age_seconds=10000, net_stake=Decimal("10.0"))
    new_node = _make_node("node_new", age_seconds=10, net_stake=Decimal("10.0"))
    graph.nodes[old_node.id] = old_node
    graph.nodes[new_node.id] = new_node

    tax_old = engine.calculate_maintenance_tax(old_node)
    tax_new = engine.calculate_maintenance_tax(new_node)

    assert tax_old < tax_new


def test_get_node_age_uses_injected_reference_clock_deterministically():
    graph = EpistemicGraph()
    reference_seconds = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
    engine = ConsensusEngine(graph, age_reference_clock=lambda: reference_seconds)
    node = Node(
        id="node-1",
        type="claim",
        content="test",
        agent_id="agent:test",
        signature="sig",
        timestamp=datetime.fromtimestamp(reference_seconds - 25, tz=timezone.utc),
        net_stake=Decimal("1.0"),
    )

    assert engine.get_node_age(node) == 25.0


def test_get_node_age_rejects_naive_timestamp():
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)

    node = _make_node("node_naive", age_seconds=100, net_stake=Decimal("1.0"))
    node.timestamp = node.timestamp.replace(tzinfo=None)

    with pytest.raises(ValueError, match="node_timestamp_naive_not_allowed"):
        engine.get_node_age(node)


def test_process_contradiction_reduces_stake():
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)

    node = _make_node("node_target", age_seconds=100, net_stake=Decimal("1.0"))
    graph.nodes[node.id] = node
    engine.node_stakes[node.id] = Decimal("10.0")

    engine.process_contradiction(node.id, stake_amount=Decimal("2.5"))

    assert engine.node_stakes[node.id] == Decimal("7.5")
