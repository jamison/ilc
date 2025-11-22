import sys
import os
import time
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.types import Node

def test_paradigm_dynamics():
    print("\n--- TEST: THE PARADIGM SHIFT CURVE ---")
    
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)
    
    # 1. Create Nodes
    # "Ancient Dogma" - Created 10,000 ticks ago
    old_time = datetime.utcnow() - timedelta(seconds=10000)
    old_node = Node(
        id="", type="claim", content="Earth is Flat", 
        agent_id="agent:ancient", signature="sig", timestamp=old_time,
        net_stake=100.0 # High reuse
    )
    old_node.id = "node_ancient"
    graph.nodes[old_node.id] = old_node
    engine.node_stakes[old_node.id] = 10.0
    
    # "New Rumor" - Created now
    new_node = Node(
        id="", type="claim", content="Stock X is up", 
        agent_id="agent:new", signature="sig",
        net_stake=1.0 # Low reuse
    )
    new_node.id = "node_new"
    graph.nodes[new_node.id] = new_node
    engine.node_stakes[new_node.id] = 10.0
    
    # 2. Compare Tax (Maintenance)
    tax_old = engine.calculate_maintenance_tax(old_node)
    tax_new = engine.calculate_maintenance_tax(new_node)
    
    print(f"Ancient Tax Rate: {tax_old:.6f}")
    print(f"New Rumor Tax Rate: {tax_new:.6f}")
    
    assert tax_old < tax_new
    print("SUCCESS: Ancient dogma is cheaper to maintain (Superconductor effect).")
    
    # 3. Compare Bounty (Risk)
    bounty_old = engine.calculate_refutation_bounty(old_node)
    bounty_new = engine.calculate_refutation_bounty(new_node)
    
    print(f"Ancient Bounty: {bounty_old:.2f}")
    print(f"New Bounty: {bounty_new:.2f}")
    
    assert bounty_old > bounty_new * 10 # Should be significantly higher
    print("SUCCESS: Ancient dogma offers a massive bounty (Paradigm Shift effect).")

if __name__ == "__main__":
    test_paradigm_dynamics()
