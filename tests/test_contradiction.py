import sys
import os
from dataclasses import dataclass
from decimal import Decimal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.agent import EveAgent
from ilc_core.consensus.engine import ConsensusEngine


@dataclass(frozen=True)
class RelationEvent:
    source_id: str
    target_id: str
    type: str

def test_contradiction_economy():
    print("\n--- TEST: THE CONTRADICTION ECONOMY ---")
    
    # 1. Setup Universe
    graph = EpistemicGraph()
    graph.load_genesis() # Ensure axioms exist
    consensus = ConsensusEngine(graph)
    
    # 2. Bad Agent (The Spammer)
    bad_agent = EveAgent("agent:spam:01", graph, consensus)
    bad_agent.wallet_balance = Decimal("100.0")
    
    print("\n1. Bad Agent asserts '1+1=5' with 10.0 Stake...")
    # We link to the Math Axiom (id: axiom:math:01)
    lie_node = bad_agent.mine_thought("1 + 1 = 5", parent_id="axiom:math:01", stake=Decimal("10.0"))
    
    # Check Status: It should be true (canonical) initially because it has stake
    is_canon = consensus.is_canonical(lie_node.id)
    print(f"   -> Is Canonical? {is_canon}")
    assert is_canon == True
    
    # 3. Good Agent (The Auditor)
    good_agent = EveAgent("agent:audit:01", graph, consensus)
    good_agent.wallet_balance = Decimal("100.0")
    
    print("\n2. Good Agent refutes the lie with 10.0 Stake...")
    # In a full system, Refutation is a Node. Here we simulate a relation event directly.
    refutation_edge = RelationEvent(
        source_id="agent:audit:01",
        target_id=lie_node.id,
        type="refutes"
    )
    
    # The Refutation carries a 1.5x Multiplier (Bounty Logic)
    consensus.process_edge(refutation_edge, stake_amount=Decimal("10.0"))
    
    # 4. Verify The Slash
    final_stake = consensus.node_stakes[lie_node.id]
    is_canon_now = consensus.is_canonical(lie_node.id)
    
    print(f"   -> Lie Node Final Stake: {final_stake}")
    
    if not is_canon_now:
        print("SUCCESS: The Lie was pruned from reality.")
    else:
        print("FAILURE: The Lie survived!")
        raise AssertionError("Slash failed.")

if __name__ == "__main__":
    test_contradiction_economy()
