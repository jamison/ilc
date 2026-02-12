import pytest
import json
import jsonschema
from pathlib import Path
from unittest.mock import patch
import sys
from io import StringIO

from ilc_core.cli.canon_cluster_a_replay_proof import main

# Paths
FIXTURES_ROOT = Path("tests/fixtures").absolute()
SCHEMA_PATH = Path("docs/specs/ilc_cluster_a_replay_proof_ci_gate_report_v0.1.json")

def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

def run_cli_command(args_list):
    with patch.object(sys, "argv", ["prog"] + args_list):
        output = StringIO()
        with patch("sys.stdout", output):
            try:
                main()
            except SystemExit as e:
                return e.code, output.getvalue()
    return -1, ""

def test_ci_gate_cli_success(tmp_path):
    report_file = tmp_path / "report.json"
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--out", str(report_file)
    ])
    
    assert code == 0
    assert report_file.exists()
    
    # stdout should contain json
    console_report = json.loads(out)
    file_report = json.loads(report_file.read_text())
    
    assert console_report == file_report
    
    # Validate Schema
    schema = load_schema()
    jsonschema.validate(instance=console_report, schema=schema)
    
    assert console_report["ok"] is True
    assert console_report["exit_code"] == 0

def test_ci_gate_cli_quiet_guard():
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--quiet"
    ])
    
    assert code == 2
    # Check error token in output
    err = json.loads(out)
    assert err["error_token"] == "usage_error:no_output_sink"

def test_ci_gate_cli_determinism():
    code1, out1 = run_cli_command(["ci-gate", "--fixtures-root", str(FIXTURES_ROOT)])
    code2, out2 = run_cli_command(["ci-gate", "--fixtures-root", str(FIXTURES_ROOT)])
    
    assert code1 == code2
    assert out1 == out2

def test_ci_gate_cli_failure_exit_code(tmp_path):
    # Use empty fixtures to force check failures -> exit 1
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(empty_root)
    ])
    
    assert code == 1
    rep = json.loads(out)
    assert rep["ok"] is False
    assert rep["exit_code"] == 1
    assert rep["fail_count"] > 0
