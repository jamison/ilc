import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.graph import EpistemicGraph

def test_sybil_attack():
    print("\n--- TEST: SYBIL DEFENSE (SPONSOR CLUSTERING) ---")
    
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)
    
    # 1. The Attack Setup
    whale_id = "wallet:attacker_main"
    sockpuppets = [f"agent:bot_{i}" for i in range(10)]
    
    print(f"1. Attacker spins up {len(sockpuppets)} bots...")
    
    # 2. The Funding (The Trap)
    # The attacker must fund the bots to make them active.
    # This reveals the link.
    for bot in sockpuppets:
        engine.register_sponsorship(whale_id, bot)
        
    # 3. The Attack Attempt
    # The bots try to form a quorum to validate a lie.
    print("2. Bots attempt to form a Consensus Quorum...")
    is_valid = engine.validate_independence(sockpuppets)
    
    # 4. The Defense
    print(f"   -> Quorum Valid? {is_valid}")
    
    if not is_valid:
        print("SUCCESS: Sybil attack blocked. 10 bots = 1 Cluster.")
    else:
        raise AssertionError("FAILURE: System was fooled by sockpuppets!")

    # 5. The Honest Scenario
    print("\n3. Testing Honest Scenario...")
    honest_agents = ["agent:alice", "agent:bob", "agent:charlie"]
    # No common sponsor links registered implies they are self-funded/independent
    is_valid_honest = engine.validate_independence(honest_agents)
    print(f"   -> Alice, Bob, Charlie Valid? {is_valid_honest}")
    assert is_valid_honest == True

if __name__ == "__main__":
    test_sybil_attack()
