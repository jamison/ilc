from decimal import Decimal

import pytest

# tests/test_entropy_reward.py
from ilc_core.economics.entropy import learning_signal, entropy_weight
from ilc_core.economics.reward import simple_claim_reward

def test_learning_signal_shape():
    low = learning_signal(Decimal("0.1"))
    mid = learning_signal(Decimal("0.5"))
    high = learning_signal(Decimal("0.9"))

    # Symmetric, peak in the middle
    assert mid > low
    assert mid > high
    assert abs(low - high) < Decimal("0.000001")


def test_entropy_weight_bounds():
    for p in ["0", "0.1", "0.5", "0.9", "1"]:
        w = entropy_weight(p)
        assert Decimal("0.5") <= w <= Decimal("2.0")


def test_entropy_weight_rejects_unbounded_max_cap_configuration():
    with pytest.raises(ValueError, match="entropy_cap_exceeds_maximum"):
        entropy_weight("0.5", max_cap=Decimal("10.000000001"))


def test_simple_claim_reward_entropy_weighting():
    stake = Decimal("10")
    potential = Decimal("0.8")

    r_low = simple_claim_reward(stake, potential, success_rate=Decimal("0.1"))
    r_mid = simple_claim_reward(stake, potential, success_rate=Decimal("0.5"))
    r_high = simple_claim_reward(stake, potential, success_rate=Decimal("0.9"))

    # Middle difficulty should be most rewarded
    assert r_mid > r_low
    assert r_mid > r_high


@pytest.mark.parametrize("value", [0.5, float("nan"), float("inf")])
def test_entropy_rejects_float_inputs(value: float) -> None:
    with pytest.raises(ValueError):
        learning_signal(value)
