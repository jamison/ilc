import pytest
from pathlib import Path
from ilc_core.protocol.ilc_cluster_a_replay_proof_ci_gate import run_cluster_a_replay_proof_ci_gate

FIXTURES_ROOT = Path("tests/fixtures").absolute()

def test_ci_gate_release_profile_success():
    """Verify that existing fixtures pass the release_v0_1 profile."""
    # This relies on the fact that we have valid fixtures checked in.
    # If any check fails, the gate returns exit_code=1.
    result = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "release_v0_1")
    
    # We assert checks passed.
    # If this fails, it means our fixtures or logic are broken.
    if not result["ok"]:
        pytest.fail(f"CI Gate Check Failed: {result['error_token_counts']} Checks: {result['checks']}")
        
    assert result["gate_version"] == "v0.1"
    assert result["profile"] == "release_v0_1"
    assert result["ok"] is True
    assert result["exit_code"] == 0
    assert result["fail_count"] == 0
    assert result["pass_count"] == 5 # We defined 5 checks
    assert len(result["checks"]) == 5

def test_ci_gate_invalid_profile():
    result = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "invalid_profile")
    assert result["exit_code"] == 2
    assert result["error_token"] == "profile_invalid"
    assert result["ok"] is False

def test_ci_gate_missing_fixtures():
    # Point to empty dir
    empty_root = Path("/tmp/empty_fixtures_root_XYZ")
    result = run_cluster_a_replay_proof_ci_gate(empty_root, "release_v0_1")
    
    # Should fail checks because fixtures missing
    assert result["ok"] is False
    assert result["exit_code"] == 1
    assert result["fail_count"] == 5 # All 5 check fixtures missing
    assert "fixture_missing" in result["error_token_counts"]

def test_determinism():
    res1 = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT)
    res2 = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT)
    assert res1 == res2
