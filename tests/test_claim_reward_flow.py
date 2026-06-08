import pytest
from decimal import Decimal
from simulations.claim_reward_flow import run_claim_reward_flow

def test_claim_reward_flow_smoke():
    """
    Smoke test to ensure the claim reward flow sim runs and returns expected stats.
    """
    stats = run_claim_reward_flow()

    # 1. Check structure
    expected_keys = ["CLAIM_upheld", "CLAIM_refuted", "REFUTE_success", "REFUTE_failed"]
    for key in expected_keys:
        assert key in stats, f"Missing key {key} in stats"
        assert stats[key]["tasks"] >= 0
        assert stats[key]["total_reward"] >= Decimal("0")

    # 2. Check that at least one success bucket has rewards
    # (This confirms the reward function is actually producing output)
    has_rewards = (stats["CLAIM_upheld"]["total_reward"] > Decimal("0")) or \
                  (stats["REFUTE_success"]["total_reward"] > Decimal("0"))
    assert has_rewards, "Expected some rewards to be generated for successful tasks"
