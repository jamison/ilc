import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.agent import EveAgent


def _make_agent():
    graph = EpistemicGraph()
    graph.load_genesis()
    consensus = ConsensusEngine(graph)
    agent = EveAgent("agent:test:auto", graph, consensus)
    return graph, consensus, agent


def test_auto_mine_respects_ecu_and_wallet():
    graph, consensus, agent = _make_agent()
    agent.wallet_balance = 5.0

    # Force a high potential so we lean aggressive.
    agent.trust_vector["potential"] = 1.0

    parent = "axiom:math:01"
    node = agent.auto_mine_claim("auto-claim", parent)

    assert node is not None
    assert node.id in graph.nodes
    assert consensus.node_stakes.get(node.id, 0.0) > 0.0
    assert agent.wallet_balance < 5.0  # some stake was spent


def test_high_potential_stakes_more_than_low():
    graph, consensus, agent_low = _make_agent()
    _, _, agent_high = _make_agent()

    agent_low.wallet_balance = 10.0
    agent_high.wallet_balance = 10.0

    # Low vs high potential.
    agent_low.trust_vector["potential"] = 0.0
    agent_high.trust_vector["potential"] = 1.0

    parent = "axiom:math:01"

    node_low = agent_low.auto_mine_claim("low", parent)
    node_high = agent_high.auto_mine_claim("high", parent)

    # Both should be able to mine at least once with the same config.
    assert node_low is not None
    assert node_high is not None

    spent_low = 10.0 - agent_low.wallet_balance
    spent_high = 10.0 - agent_high.wallet_balance

    # High-potential agent should be more aggressive.
    assert spent_high >= spent_low
