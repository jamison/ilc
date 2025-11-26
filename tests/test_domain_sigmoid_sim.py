from simulations.domain_sigmoid_allocation import run_domain_allocation_sim

def test_domain_sigmoid_sim_runs():
    # We just ensure it runs without errors for a small number of steps.
    run_domain_allocation_sim(steps=100)
