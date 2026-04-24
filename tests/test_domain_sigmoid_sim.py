from simulations.domain_sigmoid_allocation import run_domain_allocation_sim


def test_domain_sigmoid_sim_runs():
    result = run_domain_allocation_sim(steps=100)

    # Basic structural integrity
    assert isinstance(result, dict), "sim must return a dict"
    assert result["total_steps"] == 100
    assert len(result["domains"]) == 3

    total_trials = sum(d["trials"] for d in result["domains"])
    assert total_trials == 100, f"total trials must equal steps, got {total_trials}"

    for d in result["domains"]:
        assert 0.0 <= d["p_hat"] <= 1.0, f"p_hat out of [0,1] for {d['name']}: {d['p_hat']}"
        assert d["trials"] >= 0
        assert d["total_rewards"] >= 0.0

    # With seed=42 and epsilon-greedy, the hard domain should not dominate trials
    domain_map = {d["name"]: d for d in result["domains"]}
    assert domain_map["C_hard"]["trials"] < domain_map["A_easy"]["trials"], (
        "epsilon-greedy should allocate fewer trials to the hard domain than the easy one"
    )
