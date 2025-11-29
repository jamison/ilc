from simulations.epistemic_work_task_playground import (
    run_epistemic_work_task_playground,
)

def test_epistemic_work_task_playground_runs_and_returns_stats(tmp_path):
    log_file = tmp_path / "ep_task_events.ndjson"
    stats = run_epistemic_work_task_playground(
        num_tasks_per_class=3,
        log_path=str(log_file),
    )
    # Basic shape checks
    assert isinstance(stats, dict)
    assert "star.map.embedding" in stats
    assert "contradiction.sweep" in stats
    assert "custom" in stats

    for cls, s in stats.items():
        assert s["tasks"] >= 0
        assert s["stake_spent"] >= 0.0
        assert s["reward_paid"] >= 0.0

    # Ensure the log file was written and has at least one line
    assert log_file.exists()
    contents = log_file.read_text().strip()
    assert contents != ""

def test_epistemic_work_task_rewards_non_negative(tmp_path):
    log_file = tmp_path / "ep_task_events.ndjson"
    stats = run_epistemic_work_task_playground(
        num_tasks_per_class=2,
        log_path=str(log_file),
    )
    for cls, s in stats.items():
        assert s["reward_paid"] >= 0.0
