import pytest
from ilc_core.consensus.reputation import calculate_voting_power, apply_atrophy, MAX_POTENTIAL_BOOST, ATROPHY_HALF_LIFE_EPOCHS

def test_calculate_voting_power_perfect_score():
    stake = 100.0
    trust_vector = {
        'accuracy': 1.0,
        'precision': 1.0,
        'potential': 1.0
    }
    # Epistemic Score = (1.0 * 0.7) + (1.0 * 0.3) = 1.0
    # Efficiency Multiplier = 1.0 + (1.0 * 0.5) = 1.5
    # Expected Voting Power = 100 * 1.0 * 1.5 = 150.0
    expected_power = 150.0
    assert calculate_voting_power(stake, trust_vector) == expected_power

def test_calculate_voting_power_zero_score():
    stake = 100.0
    trust_vector = {
        'accuracy': 0.0,
        'precision': 0.0,
        'potential': 0.0
    }
    # Epistemic Score = 0.0
    # Efficiency Multiplier = 1.0
    # Expected Voting Power = 0.0
    assert calculate_voting_power(stake, trust_vector) == 0.0

def test_calculate_voting_power_mixed_score():
    stake = 100.0
    trust_vector = {
        'accuracy': 0.8,
        'precision': 0.6,
        'potential': 0.5
    }
    # Epistemic Score = (0.8 * 0.7) + (0.6 * 0.3) = 0.56 + 0.18 = 0.74
    # Efficiency Multiplier = 1.0 + (0.5 * 0.5) = 1.25
    # Expected Voting Power = 100 * 0.74 * 1.25 = 92.5
    expected_power = 92.5
    assert calculate_voting_power(stake, trust_vector) == expected_power

def test_apply_atrophy_no_decay():
    current_epoch = 2000
    agent_state = {
        'last_active_epoch': 1000,
        'trust_vector': {'accuracy': 1.0, 'precision': 1.0}
    }
    # Inactive = 1000 epochs < 1440 (grace period)
    # Should not decay
    new_state = apply_atrophy(agent_state, current_epoch)
    assert new_state['trust_vector']['accuracy'] == 1.0
    assert new_state['trust_vector']['precision'] == 1.0

def test_apply_atrophy_decay():
    current_epoch = 262800 + 2000 # One half-life + start
    agent_state = {
        'last_active_epoch': 2000,
        'trust_vector': {'accuracy': 1.0, 'precision': 1.0}
    }
    # Inactive = 262800 epochs = 1 half-life
    # Decay factor = 0.5 ^ 1 = 0.5
    new_state = apply_atrophy(agent_state, current_epoch)
    assert new_state['trust_vector']['accuracy'] == 0.5
    assert new_state['trust_vector']['precision'] == 0.5
