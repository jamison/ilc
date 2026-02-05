
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
        
        # Invalid input (missing required fields for export format, actually wait-
        # export_canon_format_v0_1 handles the transformation.
        # So we need input that passes export transformation but results in invalid schema?
        # Example: meta counts might be wrong if we manually tamper?
        # Or if export_canon_format logic is flawed.
        # Actually, let's create a scenario where export generation works but validation fails.
        # export_canon_format is strict on types.
        # Maybe we mock the validator to fail? Hard to do in subprocess.
        # Alternatively, we can patch `ilc_core.ledger.canon_export_validate.validate_canon_export_v0_1` 
        # inside the process? No.
        
        # Let's try to construct an input that validly exports but is invalid?
        # The exporter forces correct types and fields mostly.
        # Ah, warnings! Validation returns "ok": true on warnings.
        # If we want "ok": false, we need errors.
        # But exporter ensures schema compliance.
        # EXCEPT maybe if `canon_export_version` is missing in input, exporter raises ValueError.
        # That's an export failure, not a validation failure.
        
        # What if we pass `kpis` in input? Exporter copies them? No, exporter uses logic.
        # What if `canon_export_format` version is mismatched? It's hardcoded in exporter.
        
        # Wait, exporter is robust. Maybe I can't easily trigger validation failure 
        # unless exporter is broken or input allows bad data through that validation catches.
        # The validator checks `snapshots[*].balances` values.
        # Input balances: {"a": "bad"}.
        # Exporter: `balances = canon_state.get("balances", {})`. It just passes it through?
        # Let's check canon_export_format.py.
        # `balances: Dict[str, float] = canon_state.get("balances", {})`
        # `isinstance(balances, dict)` check is done.
        # But deep values check is NOT done in items.
        # So `{"balances": {"a": "bad_string"}}` will export successfully (JSON serializable).
        # Validator `snapshots[*].balances['agent']` check? 
        # Wait, exporter puts balances in 'snapshots' list AND input might have 'balances' dict?
        # The exporter maps input 'snapshots' (list) directly to output 'snapshots'.
        # So if input 'snapshots' contains bad data, exporter passes it through.
        
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
        assert 'must be a number' in result.stdout

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
        assert "Output file exists" in result.stderr
        
        # With --overwrite
        result2 = subprocess.run(
            COMMAND + ["--input", str(input_file), "--output", str(output_file), "--overwrite"],
            capture_output=True,
            text=True
        )
        assert result2.returncode == 0
        assert json.loads(output_file.read_text())["canon_hash"] == "h1"

    def test_missing_input(self, tmp_path):
        """Fail if input missing."""
        result = subprocess.run(
            COMMAND + ["--input", str(tmp_path / "missing.json"), "--output", "out.json"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "Input file not found" in result.stderr
