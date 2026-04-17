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
    
    assert "epoch_record_committed:epoch=12" in content, "M-013 missing epoch 12 commit evidence"
    assert "duplicate EpochSettlementTx epoch=" in content, "M-013 missing duplicate injection log"

def test_m013_contains_no_filler():
    with open(ARTIFACT_PATH, "r") as f:
        content = f.read()
        
    bad_words = ["explicitly explicitly", "cleanly tracking", "dynamically natively", "seamlessly safely"]
    for w in bad_words:
        assert w not in content, f"Artifact failed filter for word salad: {w}"
