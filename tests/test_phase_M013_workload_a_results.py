import os
import re

ARTIFACT_PATH = "docs/research/ilc_mysticeti_workload_a_results_M013_v0.1.md"

def test_m013_artifact_exists():
    assert os.path.exists(ARTIFACT_PATH), "M-013 artifact is missing"

def test_m013_verdict_passing():
    with open(ARTIFACT_PATH, "r") as f:
        content = f.read()
    assert "run_m013_workload_a_verdict=pass" in content, "M-013 outcome verdict missing or not pass"

def test_m013_contains_literal_evidence():
    with open(ARTIFACT_PATH, "r") as f:
        content = f.read()
    
    # Phase A Evidence Requirements (Baseline commits 1..10)
    assert "epoch_record_committed:epoch=1\n" in content, "Phase A: missing epoch 1 commit evidence"
    assert "epoch_record_committed:epoch=10\n" in content, "Phase A: missing epoch 10 commit evidence"
    
    # Phase B Evidence Requirements (Silent-Validator bounds on 11..12)
    assert "epoch_record_committed:epoch=11" in content, "Phase B: missing epoch 11 commit evidence"
    assert "epoch_record_committed:epoch=12" in content, "Phase B: missing epoch 12 commit evidence"
    
    # Assert missing Validator 1 evidence for epochs 11-12.
    assert "[m010_node] validator_id=1 received EpochSettlementTx epoch=11" not in content, "Phase B failure: Validator 1 should be silent for epoch 11"
    assert "[m010_node] validator_id=1 received EpochSettlementTx epoch=12" not in content, "Phase B failure: Validator 1 should be silent for epoch 12"

def test_m013_contains_no_filler():
    with open(ARTIFACT_PATH, "r") as f:
        content = f.read()
        
    bad_words = ["explicitly explicitly", "cleanly tracking", "dynamically natively", "seamlessly safely"]
    for w in bad_words:
        assert w not in content, f"Artifact failed filter for word salad: {w}"
