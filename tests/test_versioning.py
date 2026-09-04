import sys
import os
from dataclasses import dataclass
from decimal import Decimal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.agent import EveAgent


@dataclass(frozen=True)
class RelationEvent:
    source_id: str
    target_id: str
    type: str

def test_version_update():
    print("\n--- TEST: EVOLUTION (NO SLASHING) ---")
    
    graph = EpistemicGraph()
    graph.load_genesis()
    consensus = ConsensusEngine(graph)
    
    # We patch the agent to have the new engine
    agent_a = EveAgent("agent:founder", graph, consensus)
    agent_a.wallet_balance = Decimal("100")
    agent_b = EveAgent("agent:updater", graph, consensus)
    agent_b.wallet_balance = Decimal("100")
    
    # 1. Old Valid Data
    print("1. Agent A posts IP List v1...")
    node_v1 = agent_a.mine_thought("IP List: [1.1.1.1]", "axiom:logic:01", stake=Decimal("5"))
    
    # 2. The Update
    print("2. Agent B posts IP List v2 (Updated)...")
    node_v2 = agent_b.mine_thought("IP List: [1.1.1.2]", "axiom:logic:01", stake=Decimal("5"))
    
    # 3. The Link (Supersedes)
    update_edge = RelationEvent(
        source_id=node_v2.id,
        target_id=node_v1.id,
        type="supersedes"
    )
    
    # Process the update
    consensus.process_update(update_edge)
    
    # 4. Verify No Slash
    # Agent A's stake should still be 5. If it were a refutation, it would be -2.5.
    stake_v1 = consensus.node_stakes[node_v1.id]
    print(f"   -> Node v1 Stake: {stake_v1} (Should be 5)")
    
    if stake_v1 == Decimal("5"):
        print("SUCCESS: Evolution occurred without violence.")
    else:
        print(f"FAILURE: Stake was modified to {stake_v1}")
        raise AssertionError("Update treated as refutation!")

if __name__ == "__main__":
    test_version_update()
