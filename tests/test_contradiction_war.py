import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.agent import EveAgent

def test_contradiction():
    print("\n--- TEST: THE CONTRADICTION WAR ---")
    
    # Setup
    graph = EpistemicGraph()
    graph.load_genesis()
    engine = ConsensusEngine(graph)
    
    bad_agent = EveAgent("agent:liar", graph, engine)
    good_agent = EveAgent("agent:cop", graph, engine)
    
    # 1. The Lie
    print("\n1. Bad Agent lies...")
    lie_node = bad_agent.mine_thought("1 + 1 = 5", "axiom:math:01", stake=10.0)
    
    assert engine.is_canonical(lie_node.id) == True
    print(f"   State: Canonical (Stake: {engine.node_stakes[lie_node.id]})")
    
    # 2. The Refutation
    print("\n2. Good Agent attacks...")
    good_agent.refute_node(lie_node.id, stake=10.0)
    
    # 3. The Aftermath
    final_stake = engine.node_stakes[lie_node.id]
    is_canon = engine.is_canonical(lie_node.id)
    
    print(f"   State: {is_canon} (Net Stake: {final_stake})")
    
    # Assertion: 10 (Support) - 15 (Refutation Impact) = -5
    assert final_stake == -5.0
    assert is_canon == False
    print("\nSUCCESS: Lie was destroyed by intelligent labor.")

if __name__ == "__main__":
    test_contradiction()
