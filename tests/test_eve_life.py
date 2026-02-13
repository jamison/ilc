import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.agent import EveAgent
from ilc_core.consensus.engine import ConsensusEngine

def test_eve_awakening():
    print("\n--- AGENT TEST: EVE AWAKENING ---")
    
    # 1. Boot the Universe (Graph)
    graph = EpistemicGraph()
    graph.load_genesis()
    consensus = ConsensusEngine(graph)
    
    # 2. Boot the Agent (EVE)
    eve = EveAgent("agent:eve:01", graph, consensus)
    eve.wallet_balance = 100.0
    print(f"Agent {eve.id} is online.")
    
    # 3. Run Hardware Benchmark (Proof of Potential)
    phi = eve.perform_pow_benchmark()
    assert 0.0 <= phi <= 1.0
    assert eve.trust_vector["potential"] == phi
    
    # 4. Perform Labor (Mine a Thought)
    # EVE derives "1 < 2" from the Math Axiom
    parent = "axiom:math:01"
    thought = eve.mine_thought("1 < 2", parent, stake=1.0)
    
    # 5. Verification
    assert thought is not None
    assert thought.id in graph.nodes
    assert graph.edge_count() > 0
    
    print(f"EVE successfully mined thought {thought.id} linked to {parent}")
    print("LIFE SYSTEMS: VERIFIED")

if __name__ == "__main__":
    test_eve_awakening()
