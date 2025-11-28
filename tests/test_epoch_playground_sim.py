from simulations.end_to_end_epoch_playground import run_epoch_playground


def test_epoch_playground_runs_and_returns_stats():
    stats = run_epoch_playground(num_epochs=3, tasks_per_epoch=12)

    # Expect three domains with non-negative stats
    assert set(stats.keys()) == {"EASY", "MEDIUM", "HARD"}

    for domain, s in stats.items():
        assert s["tasks"] >= 0
        assert s["ecu_spent"] >= 0.0
        assert s["reward"] >= 0.0
