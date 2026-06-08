from decimal import Decimal

from simulations.task_queue_reward_flow import run_task_queue_reward_flow


def test_task_queue_reward_flow_runs_and_returns_stats():
    stats = run_task_queue_reward_flow(steps=30)

    # Basic sanity: stats dict has expected keys and non-negative values.
    for key in [
        "EASY_tasks",
        "MEDIUM_tasks",
        "HARD_tasks",
        "EASY_ecu_spent",
        "MEDIUM_ecu_spent",
        "HARD_ecu_spent",
        "EASY_reward",
        "MEDIUM_reward",
        "HARD_reward",
    ]:
        assert key in stats
        assert stats[key] >= Decimal("0")

    # We should have processed exactly `steps` tasks in total.
    total_tasks = (
        stats["EASY_tasks"] +
        stats["MEDIUM_tasks"] +
        stats["HARD_tasks"]
    )
    assert int(total_tasks) == 30
