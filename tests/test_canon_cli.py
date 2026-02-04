
import pytest
import subprocess
import sys
import json
import shutil
from pathlib import Path

# Path to the fixture
FIXTURE_PATH = Path("tests/fixtures/canon_state_v0.1.json")

def run_cli(*args):
    """Refactored runner using sys.executable to ensure we use current venv."""
    cmd = [sys.executable, "-m", "ilc_core.cli.canon_cli"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_cli_valid_file():
    if not FIXTURE_PATH.exists():
        pytest.skip("Fixture not found")
        
    res = run_cli("--path", str(FIXTURE_PATH))
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["ok"] is True
    assert "canon_hash" not in data # default hidden

def test_cli_missing_file():
    res = run_cli("--path", "nonexistent.json")
    assert res.returncode == 1
    data = json.loads(res.stdout)
    assert data["ok"] is False
    assert "File not found" in data["error"]

def test_cli_print_hash():
    if not FIXTURE_PATH.exists():
        pytest.skip("Fixture not found")
        
    res = run_cli("--path", str(FIXTURE_PATH), "--print-hash")
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "canon_hash" in data
    assert "computed_hash" in data
    assert data["canon_hash"] == data["computed_hash"]

def test_cli_quiet():
    if not FIXTURE_PATH.exists():
        pytest.skip("Fixture not found")
        
    # Valid file -> 0
    res = run_cli("--path", str(FIXTURE_PATH), "--quiet")
    assert res.returncode == 0
    assert res.stdout == ""
    
    # Missing file -> 1
    res = run_cli("--path", "nonexistent.json", "--quiet")
    assert res.returncode == 1
    assert res.stdout == ""

def test_cli_tampered_file(tmp_path):
    if not FIXTURE_PATH.exists():
        pytest.skip("Fixture not found")
    
    # Create temp copy
    bad_file = tmp_path / "bad.json"
    shutil.copy(FIXTURE_PATH, bad_file)
    
    # modify
    with open(bad_file, "r") as f:
        data = json.load(f)
    data["balances"]["alice"] = -100.0
    with open(bad_file, "w") as f:
        json.dump(data, f)
        
    res = run_cli("--path", str(bad_file))
    assert res.returncode == 1
    data = json.loads(res.stdout)
    assert data["ok"] is False
    assert "Hash mismatch" in data["error"]

def test_cli_output_is_deterministic():
    if not FIXTURE_PATH.exists():
        pytest.skip("Fixture not found")

    res1 = run_cli("--path", str(FIXTURE_PATH), "--print-hash")
    res2 = run_cli("--path", str(FIXTURE_PATH), "--print-hash")

    assert res1.returncode == 0
    assert res2.returncode == 0
    assert res1.stdout == res2.stdout
