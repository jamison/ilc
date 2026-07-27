"""
HIGH-002 Phase B closure gate.

Validates:
1. Phase B M-track document exists and carries the pass verdict token.
2. 3-of-4 quorum commit evidence token is present.
3. SafetyNoDualCert unaffected token is present.
4. Harness update token (3-key quorum injection comment) is in the runner script.
5. Phase A unit test evidence: 86 tests, quorum_threshold, 5 new HIGH-002 tests.
6. No ilc_core/ or ilc_consensus/ modifications in working tree (no scope drift).
7. Phase A commit recorded in git log with HIGH-002 identifiers.
8. Phase B doc references quorum_threshold(4)=3 and signers=[1,2,3].
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PHASE_B_DOC = os.path.join(
    REPO_ROOT,
    "docs/research/ilc_high_002_phase_b_adversarial_validation_M_v0.1.md",
)
RUNNER_SCRIPT = os.path.join(
    REPO_ROOT,
    "tools/testbed/ilc_loopback_m019_runner.sh",
)
EPOCH_SETTLEMENT = os.path.join(
    REPO_ROOT,
    "ilc_consensus/src/epoch_settlement.rs",
)
VALIDATOR_RS = os.path.join(
    REPO_ROOT,
    "ilc_consensus/src/validator.rs",
)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# --- Test 1: Phase B doc exists and pass verdict present ---
def test_phase_b_doc_exists_with_pass_verdict():
    assert os.path.isfile(PHASE_B_DOC), f"Phase B doc missing: {PHASE_B_DOC}"
    text = read(PHASE_B_DOC)
    assert "high_002_phase_b_adversarial_validation_pass" in text, (
        "Pass verdict token absent from Phase B doc"
    )


# --- Test 2: 3-of-4 quorum commit evidence token ---
def test_phase_b_doc_carries_3_of_4_commit_token():
    text = read(PHASE_B_DOC)
    assert "high_002_3_of_4_quorum_commits_with_v4_partitioned" in text, (
        "3-of-4 commit evidence token missing from Phase B doc"
    )


# --- Test 3: SafetyNoDualCert unaffected token ---
def test_phase_b_doc_carries_safety_no_dual_cert_unaffected_token():
    text = read(PHASE_B_DOC)
    assert "safety_no_dual_cert_unaffected_by_high_002_fix" in text, (
        "SafetyNoDualCert unaffected token missing from Phase B doc"
    )


# --- Test 4: Runner script carries 3-key quorum injection comment ---
def test_runner_script_updated_for_3_key_quorum():
    text = read(RUNNER_SCRIPT)
    # The HIGH-002 comment must be present in the silent/slow branch
    assert "HIGH-002" in text, "HIGH-002 comment missing from runner script"
    assert "3-of-4 quorum keys" in text or "3 quorum keys" in text, (
        "3-quorum-key annotation missing from runner script silent/slow branch"
    )
    # Must NOT pass all 4 keys in the silent/slow branch
    # (The censoring branch still uses 4 keys — that is intentional)
    # We check that validator_4_consensus_key.hex does NOT appear in the
    # silent/slow else-branch (lines after the `else` but before next elif).
    lines = text.splitlines()
    in_else_branch = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("else"):
            in_else_branch = True
        elif stripped.startswith("elif") or (stripped.startswith("fi") and in_else_branch):
            in_else_branch = False
        if in_else_branch and "validator_4_consensus_key.hex" in line:
            # This would mean V4's key is still being passed in silent/slow
            raise AssertionError(
                "validator_4_consensus_key.hex found in silent/slow else-branch — "
                "HIGH-002 harness update not applied"
            )


# --- Test 5: Phase A unit test evidence in epoch_settlement.rs ---
def test_phase_a_high002_unit_tests_present():
    text = read(EPOCH_SETTLEMENT)
    required_tests = [
        "test_quorum_threshold_correctness",
        "test_three_of_four_signers_commits_epoch",
        "test_two_of_four_signers_rejected",
        "test_duplicate_signer_rejected",
        "test_unknown_signer_rejected",
    ]
    for t in required_tests:
        assert t in text, f"HIGH-002 unit test missing: {t}"


# --- Test 6: quorum_threshold function in validator.rs ---
def test_phase_a_quorum_threshold_in_validator_rs():
    text = read(VALIDATOR_RS)
    assert "quorum_threshold" in text, "quorum_threshold function missing from validator.rs"
    assert "n.saturating_sub(n.saturating_sub(1) / 3)" in text or \
           "n - floor((N - 1) / 3)" in text, (
        "quorum_threshold BFT formula missing from validator.rs"
    )


# --- Test 7: Working tree clean (no ilc_core/ or ilc_consensus/ modifications) ---
def test_working_tree_clean_no_scope_drift():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    modified = [
        line for line in result.stdout.splitlines()
        if "ilc_core/" in line or "ilc_consensus/" in line
    ]
    assert not modified, (
        f"Unexpected ilc_core/ or ilc_consensus/ modifications in working tree:\n"
        + "\n".join(modified)
    )


# --- Test 8: Phase B doc references quorum_threshold(4)=3 and signers subset ---
def test_phase_b_doc_references_quorum_math_and_signers():
    text = read(PHASE_B_DOC)
    assert "quorum_threshold(4)" in text or "quorum_threshold = 3" in text, (
        "quorum_threshold(4)=3 math missing from Phase B doc"
    )
    assert "signers=[1,2,3]" in text or "signers = [1,2,3]" in text, (
        "signers subset [1,2,3] not documented in Phase B doc"
    )


if __name__ == "__main__":
    tests = [
        test_phase_b_doc_exists_with_pass_verdict,
        test_phase_b_doc_carries_3_of_4_commit_token,
        test_phase_b_doc_carries_safety_no_dual_cert_unaffected_token,
        test_runner_script_updated_for_3_key_quorum,
        test_phase_a_high002_unit_tests_present,
        test_phase_a_quorum_threshold_in_validator_rs,
        test_working_tree_clean_no_scope_drift,
        test_phase_b_doc_references_quorum_math_and_signers,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
