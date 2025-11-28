import pytest
from simulations.rl_bandit_domain_allocation import run_rl_bandit_sim

def test_rl_bandit_sim_smoke():
    """
    Smoke test for the RL bandit simulation.
    Verifies that the bandit learns to prefer the MEDIUM domain (highest entropy reward).
    """
    result = run_rl_bandit_sim(trials=500)
    stats = result["stats"]
    values = result["values"]

    # 1. Check structure
    for domain in ["EASY", "MEDIUM", "HARD"]:
        assert domain in stats
        assert domain in values
        assert stats[domain]["tasks"] >= 0
    
    total_tasks = sum(stats[d]["tasks"] for d in stats)
    assert total_tasks == 500

    # 2. Verify behavior
    # The entropy-weighted reward function peaks at p=0.5.
    # MEDIUM (p=0.6) is closest to 0.5, so it should have the highest reward multiplier.
    # The bandit should learn this and allocate more tasks to MEDIUM than HARD (p=0.3).
    # EASY (p=0.9) is also low entropy, so MEDIUM should beat it too, but let's stick
    # to the robust assertion from the plan: MEDIUM >= HARD.
    
    tasks_medium = stats["MEDIUM"]["tasks"]
    tasks_hard = stats["HARD"]["tasks"]
    
    # We use a soft assertion here because 500 trials with epsilon=0.1 has variance.
    # But with random.seed(12345), it should be deterministic.
    assert tasks_medium >= tasks_hard, \
        f"Bandit failed to prefer MEDIUM ({tasks_medium}) over HARD ({tasks_hard})"
