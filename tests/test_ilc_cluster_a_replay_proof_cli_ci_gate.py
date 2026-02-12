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
BASELINE_PATH = FIXTURES_ROOT / "cluster_a_replay_proof_ci_gate_v0_1" / "release_v0_1_baseline.json"
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

# --- Existing Phase 149 tests ---

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

# --- Phase 150: Baseline enforcement tests ---

def test_ci_gate_cli_baseline_success():
    """Baseline provided, no enforcement, gate passes, compare matches."""
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(BASELINE_PATH),
    ])
    assert code == 0
    rep = json.loads(out)
    assert rep["ok"] is True
    assert rep["baseline_compare"] is not None
    assert rep["baseline_compare"]["ok"] is True
    assert rep["baseline_compare"]["mismatch_count"] == 0
    # Schema validation
    schema = load_schema()
    jsonschema.validate(instance=rep, schema=schema)

def test_ci_gate_cli_enforce_baseline_pass():
    """Enforce baseline, no drift, should pass."""
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(BASELINE_PATH),
        "--enforce-baseline",
    ])
    assert code == 0
    rep = json.loads(out)
    assert rep["ok"] is True
    assert rep["baseline_compare"]["ok"] is True

def test_ci_gate_cli_enforce_baseline_drift(tmp_path):
    """Enforce baseline with a modified baseline to trigger drift -> exit 1."""
    # Create a modified baseline with a different pass_count
    modified_baseline = tmp_path / "modified_baseline.json"
    with open(BASELINE_PATH, "r") as f:
        baseline_data = json.load(f)
    baseline_data["pass_count"] = 999
    with open(modified_baseline, "w") as f:
        json.dump(baseline_data, f, sort_keys=True, separators=(",", ":"))
    
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(modified_baseline),
        "--enforce-baseline",
    ])
    assert code == 1
    rep = json.loads(out)
    assert rep["ok"] is False
    assert rep["error_token"] == "baseline_drift_detected"
    assert rep["baseline_compare"]["ok"] is False
    assert rep["baseline_compare"]["mismatch_count"] >= 1

def test_ci_gate_cli_baseline_not_found():
    """Baseline file does not exist -> exit 2."""
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", "/tmp/nonexistent_baseline_xyz.json",
    ])
    assert code == 2
    rep = json.loads(out)
    assert rep["error_token"] == "baseline_not_found"

def test_ci_gate_cli_baseline_invalid_json(tmp_path):
    """Baseline file is not valid JSON -> exit 2."""
    bad = tmp_path / "bad.json"
    bad.write_text("not json {{{", encoding="utf-8")
    
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(bad),
    ])
    assert code == 2
    rep = json.loads(out)
    assert rep["error_token"] == "baseline_invalid_json"

def test_ci_gate_cli_baseline_schema_invalid(tmp_path):
    """Baseline file fails schema validation -> exit 2."""
    bad = tmp_path / "invalid.json"
    bad.write_text(json.dumps({"not": "valid"}), encoding="utf-8")
    
    code, out = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(bad),
    ])
    assert code == 2
    rep = json.loads(out)
    assert rep["error_token"] == "baseline_schema_invalid"

def test_ci_gate_cli_baseline_determinism():
    """Baseline compare output must be byte-identical across runs."""
    code1, out1 = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(BASELINE_PATH),
    ])
    code2, out2 = run_cli_command([
        "ci-gate",
        "--fixtures-root", str(FIXTURES_ROOT),
        "--baseline", str(BASELINE_PATH),
    ])
    assert code1 == code2
    assert out1 == out2
