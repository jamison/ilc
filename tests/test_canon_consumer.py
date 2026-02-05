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
        assert any("File not found" in e for e in summary.get("errors", []))

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
            assert any("Hash mismatch" in e for e in summary.get("errors", []))

    def test_cli_valid(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        res = run_cli("--path", str(FIXTURE_PATH))
        assert res.returncode == 0
        
        # Output should be: status=ok canon_path=... canon_hash=... errors=[]
        output = res.stdout.strip()
        assert output.startswith("status=ok")
        assert f"canon_path={str(FIXTURE_PATH)}" in output
        assert "canon_hash=" in output
        assert "errors=[]" in output
        
        # Ensure hash is shortened (usually 64 chars -> 12 chars)
        import re
        hash_match = re.search(r"canon_hash=([a-f0-9]+|unknown)", output)
        if hash_match:
            hash_val = hash_match.group(1)
            if hash_val != "unknown":
                assert len(hash_val) <= 12

    def test_cli_error(self):
        res = run_cli("--path", "missing_file.json")
        assert res.returncode == 1
        
        output = res.stdout.strip()
        assert output.startswith("status=fail")
        assert "errors=[" in output
        assert "File not found" in output

    def test_cli_quiet(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        res = run_cli("--path", str(FIXTURE_PATH), "--quiet")
        assert res.returncode == 0
        assert res.stdout == ""

    def test_cli_version_mismatch(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_path = Path(tmpdir) / "bad_version.json"
            shutil.copy(FIXTURE_PATH, bad_path)

            with open(bad_path, "r") as f:
                data = json.load(f)

            data["canon_export_version"] = "v0.99"
            with open(bad_path, "w") as f:
                json.dump(data, f)

            res = run_cli("--path", str(bad_path))
            assert res.returncode == 1
            
            output = res.stdout.strip()
            assert output.startswith("status=fail")
            assert "Unsupported version" in output

    def test_cli_report_valid(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        res = run_cli("--path", str(FIXTURE_PATH), "--report")
        assert res.returncode == 0
        
        # Must be parseable JSON
        output = res.stdout
        assert "\n" not in output.strip()
        report = json.loads(output)
        assert list(report.keys()) == ["ok", "canon_hash", "computed_hash", "errors", "meta"]
        assert report["ok"] is True
        assert isinstance(report["errors"], list)
        assert "meta" in report
        assert report["meta"]["epoch_count"] is not None
        assert report["meta"]["canon_export_version"] == "v0.1"

    def test_cli_report_error(self):
        res = run_cli("--path", "missing_file.json", "--report")
        assert res.returncode == 1
        
        output = res.stdout
        assert "\n" not in output.strip()
        report = json.loads(output)
        assert list(report.keys()) == ["ok", "canon_hash", "computed_hash", "errors", "meta"]
        assert report["ok"] is False
        assert isinstance(report["errors"], list)
        assert "meta" in report
        assert report["meta"]["epoch_count"] is None
        assert any("File not found" in e for e in report["errors"])

    def test_cli_report_ignores_quiet(self):
        res = run_cli("--path", "missing_file.json", "--report", "--quiet")
        assert res.returncode == 1
        assert res.stdout.strip() != ""

    def test_cli_module_invocation(self):
        """Verify that the module can be invoked via python -m ilc_core.cli.canon_consumer"""
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")
            
        cmd = [sys.executable, "-m", "ilc_core.cli.canon_consumer", "--path", str(FIXTURE_PATH)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        assert res.returncode == 0
        assert res.stdout.strip().startswith("status=ok")

    def test_cli_kpis_valid(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        res = run_cli("--path", str(FIXTURE_PATH), "--kpis")
        assert res.returncode == 0
        output = res.stdout.strip()
        expected = "kpis=epochs:1 snapshots:1 balances:2"
        assert output == expected

    def test_cli_kpis_precedence(self):
        if not FIXTURE_PATH.exists():
            pytest.skip("Fixture not found")

        # --report overrides --kpis
        res = run_cli("--path", str(FIXTURE_PATH), "--kpis", "--report")
        assert res.returncode == 0
        output = res.stdout.strip()
        assert output.startswith("{")  # JSON
        assert "kpis=" not in output

        # --quiet suppresses --kpis
        res = run_cli("--path", str(FIXTURE_PATH), "--kpis", "--quiet")
        assert res.returncode == 0
        assert res.stdout.strip() == ""

    def test_cli_kpis_error(self):
        res = run_cli("--path", "missing_file.json", "--kpis")
        assert res.returncode == 1
        output = res.stdout.strip()
        # Expect: kpis=epochs:None snapshots:None balances:None
        assert "epochs:None" in output
        assert "snapshots:None" in output
        assert "balances:None" in output
