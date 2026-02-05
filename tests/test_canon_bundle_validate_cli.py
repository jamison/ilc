
import pytest
import json
import subprocess
import sys
from pathlib import Path

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_validate"]

class TestCanonBundleValidateCLI:
    
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        bundle_dir = tmp_path / "valid_bundle"
        write_canon_export_bundle(
            {"canon_hash": "h1"}, {"ok": True}, bundle_dir
        )
        return bundle_dir

    def test_valid_bundle(self, valid_bundle):
        result = subprocess.run(
            COMMAND + ["--bundle", str(valid_bundle)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert "\n" not in result.stdout.strip() # Single line check
        assert result.stderr.strip() == ""

    def test_missing_bundle(self, tmp_path):
        missing_path = (tmp_path / "missing").resolve()
        result = subprocess.run(
            COMMAND + ["--bundle", str(missing_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert any("not found" in e for e in data["errors"])
        assert any(str(missing_path) in e for e in data["errors"])
        assert result.stderr.strip() == ""

    def test_invalid_bundle(self, valid_bundle):
        # Tamper with file
        (valid_bundle / "export.json").write_text("tampered\n")
        
        result = subprocess.run(
            COMMAND + ["--bundle", str(valid_bundle)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert any("hash mismatch" in e for e in data["errors"])
        assert result.stderr.strip() == ""
