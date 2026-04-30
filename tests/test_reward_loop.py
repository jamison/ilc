import sys
import os
from decimal import Decimal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.agent import EveAgent
from ilc_core.config import load_governance_config
from ilc_core.economics.reward import simple_claim_reward


def _make_agent(starting_balance: Decimal = Decimal("5.0")):
    graph = EpistemicGraph()
    graph.load_genesis()
    cfg = load_governance_config()
    engine = ConsensusEngine(graph, governance_config=cfg)
    agent = EveAgent("agent:test:reward", graph, engine)
    agent.wallet_balance = starting_balance
    return graph, engine, agent


def test_simple_claim_reward_monotonic():
    # Higher stake and higher potential → higher reward
    r1 = simple_claim_reward(1.0, 0.0)
    r2 = simple_claim_reward(1.0, 1.0)
    r3 = simple_claim_reward(2.0, 0.5)

    assert r1 > 0
    assert r2 > r1
    assert r3 > r1


def test_agent_can_recover_balance_with_rewards():
    graph, engine, agent = _make_agent(starting_balance=Decimal("5.0"))
    parent = "axiom:math:01"

    # Mine a few claims with rewards
    for i in range(5):
        pre = agent.wallet_balance
        node = agent.auto_mine_claim(f"reward-test-{i}", parent)
        if node is None:
            break
        spent = max(Decimal("0"), pre - agent.wallet_balance)
        reward = simple_claim_reward(spent, agent.trust_vector.get("potential", 0.0))
        agent.receive_reward(reward)

    # Agent should not be completely bankrupt; balance should be > 0
    # In fact, with current toy reward logic (base + boost), they should profit.
    assert agent.wallet_balance > Decimal("0")
