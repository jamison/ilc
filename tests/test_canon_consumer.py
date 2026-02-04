import pytest
import json
import tempfile
import shutil
import sys
import subprocess
from pathlib import Path

from ilc_core.cli.canon_consumer import summarize_canon_state

FIXTURE_PATH = Path("tests/fixtures/canon_state_v0.1.json")

def run_cli(*args):
    cmd = [sys.executable, "-m", "ilc_core.cli.canon_consumer"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

class TestCanonConsumer:

    def test_summarize_valid_file(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")
            
        summary = summarize_canon_state(FIXTURE_PATH)
        assert summary["ok"] is True
        assert summary["canon_export_version"] == "v0.1"
        assert "canon_hash" in summary
        # Assuming fixture has some data, check types
        assert isinstance(summary["epoch_count"], int)
        assert isinstance(summary["snapshot_count"], int)
        assert isinstance(summary["balance_count"], int)

    def test_summarize_missing_file(self):
        summary = summarize_canon_state("nonexistent.json")
        assert summary["ok"] is False
        assert "File not found" in summary.get("error", "")

    def test_summarize_tampered_file(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")
            
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_path = Path(tmpdir) / "tampered.json"
            shutil.copy(FIXTURE_PATH, bad_path)
            
            # Tamper with content
            with open(bad_path, "r") as f:
                data = json.load(f)
            
            # Mutate a balance
            if "balances" in data:
                data["balances"]["alice"] = -999.99
            else:
                data["balances"] = {"alice": -999.99}
                
            with open(bad_path, "w") as f:
                json.dump(data, f)
                
            summary = summarize_canon_state(bad_path)
            assert summary["ok"] is False
            assert "Hash mismatch" in summary.get("error", "")

    def test_cli_valid(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        res = run_cli("--path", str(FIXTURE_PATH))
        assert res.returncode == 0
        
        data = json.loads(res.stdout)
        assert data["ok"] is True
        assert "epoch_count" in data

    def test_cli_error(self):
        res = run_cli("--path", "missing_file.json")
        assert res.returncode == 1
        
        data = json.loads(res.stdout)
        assert data["ok"] is False
