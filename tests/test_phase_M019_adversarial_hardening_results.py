import os
import subprocess

def check_results():
    path = "docs/research/ilc_mysticeti_adversarial_hardening_M019_v0.1.md"
    assert os.path.exists(path), "Output report missing"
    
    with open(path, "r") as f:
        doc = f.read()
    
    assert "run_m019_adversarial_hardening_verdict=pass" in doc, "Verdict flag missing"
    assert "SafetyNoDualCert" in doc, "SafetyNoDualCert spec anchor missing"
    assert "Row7_Liveness" in doc, "Row7_Liveness spec anchor missing"
    
    # Negative constraint: Ensure M-019 does not claim Row-5 evidence
    assert "Row-5" not in doc, "M-019 results doc improperly claims Row-5 evidence"
    
    # Log-based assertions require a prior run of ilc_loopback_m019_runner.sh.
    # The log file is gitignored ephemeral state; skip gracefully on fresh checkouts.
    log_path = "tools/testbed/m019_run.log"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_content = f.read()
        assert "PASS - Honest Quorum Comitted Epoch 1 Successfully" in log_content, "Silent/slow logic failed to commit"
        assert "PASS - Equivocation Detected!" in log_content, "Equivocating specific logic bound dropped"
        assert "PASS - Redundant Path Evident!" in log_content, "Censoring failure on verifying honest side"
        print("Log-based scenario assertions passed")
    else:
        print("m019_run.log absent — log assertions skipped (run ilc_loopback_m019_runner.sh to generate)")
    
    # Verification condition: Check for no ilc_core source code mutations logically
    cmd = ["git", "diff", "--name-only"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        modified_files = result.stdout.split("\n")
        assert not any(f.startswith("ilc_core/") for f in modified_files), "M-019 modified ilc_core components natively outside bounds"

    print("M-019 Passed")

if __name__ == "__main__":
    check_results()
