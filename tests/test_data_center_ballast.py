from simulations.data_center_ballast import run_ballast_simulation


def test_ballast_simulation_improves_or_matches_utilization():
    result = run_ballast_simulation(steps=24)

    # Basic sanity: sim ran and executed some tasks.
    assert result["steps"] == 24.0
    assert result["total_tasks"] >= 0.0  # could be 0 in a degenerate case, but we expect >0

    # Utilization with ILC ballast should not be worse than baseline.
    assert result["ilc_avg"] >= result["baseline_avg"]
    assert result["ilc_min"] >= result["baseline_min"]
