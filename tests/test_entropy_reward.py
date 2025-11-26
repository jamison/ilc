# tests/test_entropy_reward.py

from ilc_core.economics.entropy import learning_signal, entropy_weight
from ilc_core.economics.reward import simple_claim_reward

def test_learning_signal_shape():
    low = learning_signal(0.1)
    mid = learning_signal(0.5)
    high = learning_signal(0.9)

    # Symmetric, peak in the middle
    assert mid > low
    assert mid > high
    assert abs(low - high) < 1e-6


def test_entropy_weight_bounds():
    for p in [0.0, 0.1, 0.5, 0.9, 1.0]:
        w = entropy_weight(p)
        assert 0.5 <= w <= 2.0


def test_simple_claim_reward_entropy_weighting():
    stake = 10.0
    potential = 0.8

    r_low = simple_claim_reward(stake, potential, success_rate=0.1)
    r_mid = simple_claim_reward(stake, potential, success_rate=0.5)
    r_high = simple_claim_reward(stake, potential, success_rate=0.9)

    # Middle difficulty should be most rewarded
    assert r_mid > r_low
    assert r_mid > r_high
