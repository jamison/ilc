import math

# CONSTANTS
MAX_POTENTIAL_BOOST = 0.5  # Max 1.5x multiplier
ATROPHY_HALF_LIFE_EPOCHS = 262800  # Approx 6 months

def calculate_voting_power(stake: float, trust_vector: dict) -> float:
    """
    Calculates L1 Voting Power.
    Formula: Stake * Epistemic_Score * (1 + Efficiency_Multiplier)
    Epistemic_Score = (Accuracy * 0.7) + (Precision * 0.3)
    Efficiency_Multiplier = potential * MAX_POTENTIAL_BOOST
    """
    accuracy = trust_vector.get('accuracy', 0.0)
    precision = trust_vector.get('precision', 0.0)
    potential = trust_vector.get('potential', 0.0)

    # Epistemic Score (Truth)
    epistemic_score = (accuracy * 0.7) + (precision * 0.3)
    
    # Efficiency Multiplier (Hardware) - Capped at 1.5x
    efficiency_mult = 1.0 + (potential * MAX_POTENTIAL_BOOST)

    return stake * epistemic_score * efficiency_mult

def apply_atrophy(agent_state: dict, current_epoch: int) -> dict:
    """
    Decays accuracy/precision if inactive > 1440 epochs.
    Formula: Score * (0.5 ^ (inactive_time / half_life))
    """
    last_active = agent_state.get('last_active_epoch', current_epoch)
    inactive = current_epoch - last_active

    # Grace period of 24 hours (1440 epochs)
    if inactive > 1440:
        decay = 0.5 ** (inactive / ATROPHY_HALF_LIFE_EPOCHS)
        tv = agent_state['trust_vector']
        tv['accuracy'] *= decay
        tv['precision'] *= decay
    
    return agent_state
