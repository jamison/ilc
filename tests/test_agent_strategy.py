import sys
import os
from decimal import Decimal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.agent import DRAFT_SIGNATURE, EveAgent


def test_decide_stake_respects_ecu_fee_and_wallet():
    graph = EpistemicGraph()
    graph.load_genesis()
    consensus = ConsensusEngine(graph)

    agent = EveAgent("agent:test:strategy", graph, consensus)
    agent.wallet_balance = Decimal("1.0")  # small but non-zero

    fee = consensus.governance.get_task_fee_ecu("claim.submit")
    assert fee > Decimal("0")

    # Case 1: requested stake below fee -> should be bumped up to >= fee (if wallet allows)
    chosen = agent.decide_stake_for_claim(requested_stake=fee / Decimal("10"))
    assert chosen >= fee
    assert chosen <= agent.wallet_balance

    # Case 2: requested stake equal to fee -> should be kept
    chosen2 = agent.decide_stake_for_claim(requested_stake=fee)
    assert chosen2 == fee

    # Case 3: requested stake above wallet -> should be capped at wallet
    chosen3 = agent.decide_stake_for_claim(requested_stake=agent.wallet_balance * Decimal("10"))
    assert chosen3 == agent.wallet_balance


def test_mine_thought_uses_strategy_and_succeeds_with_funds():
    graph = EpistemicGraph()
    graph.load_genesis()
    consensus = ConsensusEngine(graph)

    agent = EveAgent("agent:test:mine", graph, consensus)
    agent.wallet_balance = Decimal("10.0")

    parent = "axiom:math:01"
    thought = agent.mine_thought("2 < 3", parent, stake=Decimal("1.0"))

    # With a funded wallet and reasonable stake, mining should succeed.
    assert thought is not None
    assert thought.signature == DRAFT_SIGNATURE
    assert thought.id in graph.nodes
    assert graph.edge_count() > 0
    assert consensus.node_stakes.get(thought.id, Decimal("0")) > Decimal("0")
    assert agent.wallet_balance < Decimal("10.0")  # stake was deducted
