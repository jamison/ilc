import pytest
import json
from pathlib import Path
from ilc_core.exceptions import ReplayProofBaselineError
import ilc_core.protocol.ilc_cluster_a_replay_proof_ci_gate as ci_gate_module
from ilc_core.protocol.ilc_cluster_a_replay_proof_ci_gate import (
    run_cluster_a_replay_proof_ci_gate,
    load_ci_gate_baseline,
    compare_ci_gate_report_to_baseline,
)

FIXTURES_ROOT = Path("tests/fixtures").absolute()
BASELINE_PATH = FIXTURES_ROOT / "cluster_a_replay_proof_ci_gate_v0_1" / "release_v0_1_baseline.json"

# --- load_ci_gate_baseline ---

def test_load_baseline_success():
    baseline = load_ci_gate_baseline(BASELINE_PATH)
    assert isinstance(baseline, dict)
    assert baseline["gate_version"] == "v0.1"
    assert baseline["ok"] is True
    assert baseline["exit_code"] == 0

def test_load_baseline_not_found():
    with pytest.raises(FileNotFoundError):
        load_ci_gate_baseline(Path("/tmp/nonexistent_baseline_xyz.json"))

def test_load_baseline_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json {{{", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_ci_gate_baseline(bad)

def test_load_baseline_schema_invalid(tmp_path):
    bad = tmp_path / "invalid_schema.json"
    bad.write_text(json.dumps({"not_a_valid_report": True}), encoding="utf-8")
    with pytest.raises(ReplayProofBaselineError):
        load_ci_gate_baseline(bad)


def test_load_baseline_schema_unavailable_raises_value_error(monkeypatch):
    monkeypatch.setattr(ci_gate_module, "_GATE_REPORT_VALIDATOR", None)
    with pytest.raises(ReplayProofBaselineError, match="internal_error:schema_not_loaded"):
        load_ci_gate_baseline(BASELINE_PATH)

# --- compare_ci_gate_report_to_baseline ---

def test_compare_identical():
    report = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "release_v0_1")
    baseline = load_ci_gate_baseline(BASELINE_PATH)
    cmp = compare_ci_gate_report_to_baseline(report, baseline)
    assert cmp["compare_version"] == "v0.1"
    assert cmp["ok"] is True
    assert cmp["mismatch_count"] == 0
    assert cmp["mismatches"] == []

def test_compare_mismatch():
    report = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "release_v0_1")
    baseline = load_ci_gate_baseline(BASELINE_PATH)
    # Introduce a controlled mismatch
    baseline_modified = json.loads(json.dumps(baseline))
    baseline_modified["pass_count"] = 999
    cmp = compare_ci_gate_report_to_baseline(report, baseline_modified)
    assert cmp["ok"] is False
    assert cmp["mismatch_count"] >= 1
    paths = [m["path"] for m in cmp["mismatches"]]
    assert "/pass_count" in paths
    reasons = [m["reason"] for m in cmp["mismatches"]]
    assert "value_mismatch" in reasons

def test_compare_deterministic():
    report = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "release_v0_1")
    baseline = load_ci_gate_baseline(BASELINE_PATH)
    cmp1 = compare_ci_gate_report_to_baseline(report, baseline)
    cmp2 = compare_ci_gate_report_to_baseline(report, baseline)
    assert cmp1 == cmp2
    # Byte-level determinism
    assert json.dumps(cmp1, sort_keys=True) == json.dumps(cmp2, sort_keys=True)

def test_compare_schema_invalid_current():
    bad_current = {"invalid": True}
    baseline = load_ci_gate_baseline(BASELINE_PATH)
    cmp = compare_ci_gate_report_to_baseline(bad_current, baseline)
    assert cmp["ok"] is False
    assert cmp["mismatches"][0]["reason"] == "schema_invalid_current"

def test_compare_schema_invalid_baseline():
    report = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "release_v0_1")
    bad_baseline = {"invalid": True}
    cmp = compare_ci_gate_report_to_baseline(report, bad_baseline)
    assert cmp["ok"] is False
    assert cmp["mismatches"][0]["reason"] == "schema_invalid_baseline"


def test_compare_schema_unavailable_current_returns_fail_closed(monkeypatch):
    monkeypatch.setattr(ci_gate_module, "_GATE_REPORT_VALIDATOR", None)
    cmp = compare_ci_gate_report_to_baseline({"gate_version": "v0.1"}, {"gate_version": "v0.1"})
    assert cmp["ok"] is False
    assert cmp["mismatches"][0]["reason"] == "schema_invalid_current"
    assert cmp["mismatches"][0]["detail"] == "internal_error:schema_not_loaded"

def test_compare_mismatch_paths_sorted():
    """Mismatches must be deterministically sorted by (path, reason)."""
    report = run_cluster_a_replay_proof_ci_gate(FIXTURES_ROOT, "release_v0_1")
    baseline = load_ci_gate_baseline(BASELINE_PATH)
    baseline_modified = json.loads(json.dumps(baseline))
    baseline_modified["pass_count"] = 999
    baseline_modified["fail_count"] = 888
    cmp = compare_ci_gate_report_to_baseline(report, baseline_modified)
    paths = [(m["path"], m["reason"]) for m in cmp["mismatches"]]
    assert paths == sorted(paths)
