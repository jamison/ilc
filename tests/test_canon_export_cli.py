
import pytest
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# We can test by invoking the module directly using subprocess, 
# or by mocking arguments and calling main().
# Subprocess is safer for CLI tests to ensure entrypoint mechanics work,
# but main() is faster. Let's do main mock for speed and one subprocess for integration if needed.
# Actually, given "No heavy dependencies", pure python invocation via -m is good.

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_export"]

class TestCanonExportCLI:
    
    def test_export_happy_path(self, tmp_path):
        """Test basic export flow."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        
        # Valid input
        input_data = {
            "canon_hash": "h1",
            "canon_export_version": "v1",
            "epochs": [],
            "snapshots": []
        }
        input_file.write_text(json.dumps(input_data))
        
        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert output_file.exists()
        
        data = json.loads(output_file.read_text())
        assert data["canon_export_format"] == "v0.1"
        assert data["canon_hash"] == "h1"

    def test_export_pretty(self, tmp_path):
        """Test pretty print output."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        
        input_file.write_text(json.dumps({
            "canon_hash": "h1",
            "canon_export_version": "v1"
        }))
        
        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file), "--pretty"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        content = output_file.read_text()
        assert "\n" in content
        assert '  "canon_export_format":' in content # Indentation

    def test_export_validate_success(self, tmp_path):
        """Test export with validation (success)."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        
        input_file.write_text(json.dumps({
            "canon_hash": "h1",
            "canon_export_version": "v1",
            "epochs": [],
            "snapshots": []
        }))
        
        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file), "--validate"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        # Check stdout for validation report
        assert '"ok":true' in result.stdout.replace(" ", "") 

    def test_export_validate_failure(self, tmp_path):
        """Test export with validation (failure)."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        
        # Craft input that exports successfully but fails validation on deep balances.
        input_data = {
            "canon_hash": "h1",
            "canon_export_version": "v1",
            "snapshots": [
                 {"epoch_id": "e1", "balances": {"agent": "NOT_A_NUMBER"}} 
            ],
            "epochs": []
        }
        input_file.write_text(json.dumps(input_data))
        
        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file), "--validate"],
            capture_output=True,
            text=True
        )
        
        # Should export fine (file created)
        assert output_file.exists()
        # But validation fail
        assert result.returncode == 1
        assert '"ok":false' in result.stdout.replace(" ", "")
        assert 'must be a non-negative exact numeric value' in result.stdout

    def test_overwrite_protection(self, tmp_path):
        """Test overwrite file protection."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        output_file.write_text("pre-existing")
        
        input_file.write_text(json.dumps({
            "canon_hash": "h1", "canon_export_version": "v1"
        }))
        
        # Without --overwrite
        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        error_payload = json.loads(result.stdout)
        assert error_payload["ok"] is False
        assert error_payload["error"] == "output_exists"
        assert "Output file exists" in error_payload["detail"]
        assert result.stderr == ""
        
        # With --overwrite
        result2 = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file), "--overwrite"],
            capture_output=True,
            text=True
        )
        assert result2.returncode == 0
        assert json.loads(output_file.read_text())["canon_hash"] == "h1"

    def test_output_dir_creation(self, tmp_path):
        """Ensure parent directories are created for output."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "nested" / "dir" / "export.json"

        input_file.write_text(json.dumps({
            "canon_hash": "h1",
            "canon_export_version": "v1"
        }))

        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_missing_input(self, tmp_path):
        """Fail if input missing."""
        result = subprocess.run(
            COMMAND + ["--input", str(tmp_path / "missing.json"), "--output", "out.json"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        error_payload = json.loads(result.stdout)
        assert error_payload["ok"] is False
        assert error_payload["error"] == "input_file_not_found"
        assert "Input file not found" in error_payload["detail"]
        assert result.stderr == ""

    def test_exported_at_is_utc(self, tmp_path):
        """Exported timestamp should be UTC."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"

        input_file.write_text(json.dumps({
            "canon_hash": "h1",
            "canon_export_version": "v1"
        }))

        result = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        data = json.loads(output_file.read_text())
        assert data["exported_at"].endswith("+00:00") or data["exported_at"].endswith("Z")
