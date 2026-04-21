from simulations.claim_lifecycle_playground import run_claim_lifecycle_playground


def test_claim_lifecycle_playground_runs_and_shapes():
    stats = run_claim_lifecycle_playground()

    # Basic structure checks
    assert "claim" in stats
    assert "refute" in stats
    assert "task_outcome" in stats
    assert "epoch_summary" in stats

    claim = stats["claim"]
    refute = stats["refute"]
    outcome = stats["task_outcome"]
    epoch = stats["epoch_summary"]

    assert claim["type"] == "claim"
    # Refutation type might map to 'refute' in protocol even if internal is 'refutation'
    assert refute["type"] == "refute" 
    # NEW: refute should point at the claim
    assert refute["target_claim_id"] == claim["id"]
    
    assert outcome["task_type"] == "claim.submit"
    assert isinstance(epoch["total_tasks"], int)
    assert isinstance(epoch["total_ecu_spent"], (str, float))  # protocol path returns canonical string
