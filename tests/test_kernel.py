import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.types import Node

def test_graph_boot():
    print("--- KERNEL TEST: GENESIS LINKING ---")
    
    # 1. Initialize Graph
    graph = EpistemicGraph()
    graph.load_genesis()
    
    # 2. Verify Genesis Axioms exist
    assert "axiom:math:01" in graph.nodes
    print("SUCCESS: Genesis axioms loaded.")
    
    # 3. Create a new 'Derivative Claim' (Simulation of EVE working)
    eve_node = Node(
        id="", # Will compute
        type="claim",
        content="2 + 2 = 4",
        agent_id="agent:eve:01",
        signature="simulated_sig"
    )
    eve_node.id = eve_node.compute_id()
    
    # 4. Add to Graph
    graph.add_node(eve_node)
    print(f"SUCCESS: Minted new node {eve_node.id}")
    
    # 5. Link EVE's node to Genesis (The 'Why')
    # "2+2=4" derives from "1+1=2" (axiom:math:01)
    graph.add_edge_by_ids(eve_node.id, "axiom:math:01", "derives_from")
    print(f"SUCCESS: Linked '{eve_node.content}' -> '{graph.nodes['axiom:math:01'].content}'")
    print("KERNEL INTEGRITY: VERIFIED")

if __name__ == "__main__":
    test_graph_boot()
